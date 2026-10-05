#!/usr/bin/env python3
"""File-drop adapter: OHCS "Affordable Housing 10-Year Expiration Forecast" (PuSH dashboard source) -> leads/events.

TEMPLATE STATUS: the dataset page on data.oregon.gov was not fetched in this build (verified_live=false). Column names
in dataset-schemas.yaml `ohcs_push_forecast` and the alias table below are guesses from the dataset description; the
adapter names every missing field instead of guessing. Run date_profile.py on the real export, confirm the
preservation-status vocabulary, and extend `status_map` before relying on it.

What it emits:
  signal on_state_expiring_list = true          on every forecast row (scored +6 when inside 5 years with no notice)
  PRESERVATION_NOTICE_RECEIVED (RECORDED)       when the preservation-status value is in status_map.notice_received
                                                (detail push_first / push_second / hap_optout per status_map), dated by
                                                `Notice Date` when present else the file vintage (verify_flag Needs Anchor Date)
  REGULATORY_LATEST_END (REPORTED)              from the forecast's expiration date (cross-checks the OAHI LATEST date)
  STABILIZATION_AWARD (RECORDED)                when status is in status_map.preserved (suppresses conversion motivation)
Matching: `--ohcs-leads <leads.csv>` from ohcs_inventory_targets.py lets the forecast row reuse the OAHI property_id by
normalized Property Name + Address (exact) or by fuzzy name + zip5 >= 0.92; otherwise the address-hash id is used and
merge_leads.py performs the union. `--prior <previous forecast.csv>` writes status_flips.csv (quarterly diff): any row
whose status moved into notice_received is the status flip that PRESERVATION_NOTICE_RECEIVED is built on.

Usage:
  python scripts/normalize_ohcs_forecast.py --input <forecast.csv> --pack references/sources/oregon-portland \
      [--ohcs-leads runs/x/adapter_ohcs/leads.csv] [--prior <older forecast.csv>] [--counties 41051,41067,41005] \
      --out-dir runs/x/forecast [--as-of YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import difflib
import os
import sys
from typing import Any, Dict, List, Optional

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from omdf import adapters as A  # noqa: E402
from omdf import dates as D  # noqa: E402
from omdf import geo as G  # noqa: E402
from omdf.entities import archetype, infer_owner_type  # noqa: E402
from omdf.schema import FLAG_ANCHOR, clean_numeric, load_dataset_schemas  # noqa: E402

ALIASES: Dict[str, List[str]] = {
    "name": ["Property Name", "PROPERTY_NAME", "Project Name", "property_name"],
    "address": ["Address", "ADDRESS", "Property Address", "address"],
    "city": ["City", "CITY", "city"],
    "zip": ["Zip", "Zip Code", "ZIP", "zip"],
    "county": ["County", "COUNTY", "county"],
    "units": ["Affordable Units", "Total Units", "Units", "AFFORDABLE_UNITS"],
    "assistance": ["Assistance Type", "Program", "Funding Source", "ASSISTANCE_TYPE"],
    "ami": ["AMI", "Target AMI", "AMI Level"],
    "expiration": ["Expiration Date", "Expiration/Termination Date", "Termination Date", "EXPIRATION_DATE", "LATEST_Expiration_Date"],
    "status": ["Preservation Status", "PRESERVATION_STATUS", "Status", "Preservation_Status"],
    "notice_date": ["Notice Date", "NOTICE_DATE", "Notice Received Date"],
    "owner": ["Owner Name", "Owner", "OWNER_NAME"],
}
REQUIRED = ["name", "status"]


def _norm_key(name: str, addr: str) -> str:
    return f"{str(name or '').upper().strip()}|{G.normalize_address(addr)}"


def match_to_ohcs(name: str, addr: str, zipc: str, ohcs: Optional[pd.DataFrame]) -> Optional[str]:
    if ohcs is None or len(ohcs) == 0:
        return None
    key = _norm_key(name, addr)
    exact = ohcs[ohcs["_key"] == key]
    if len(exact):
        return str(exact.iloc[0]["property_id"])
    z = G.zip5(zipc)
    if not z:
        return None
    cands = ohcs[ohcs["zip"].astype(str) == z]
    best, best_pid = 0.0, None
    for _, r in cands.iterrows():
        ratio = difflib.SequenceMatcher(None, str(r["property_name"]).upper(), str(name).upper()).ratio()
        if ratio > best:
            best, best_pid = ratio, str(r["property_id"])
    return best_pid if best >= 0.92 else None


def run(a) -> Dict[str, Any]:
    as_of = D.parse_as_of(a.as_of)
    schemas = load_dataset_schemas(a.pack)
    spec = schemas.get("ohcs_push_forecast") or {}
    smap = spec.get("status_map") or {}
    df = A.read_table(a.input)
    try:
        col = A.resolve_columns(df, ALIASES, REQUIRED)
    except A.SchemaMismatch as exc:
        print(f"ERROR ohcs_push_forecast: {exc}", file=sys.stderr)
        sys.exit(2)
    fmt_exp = (spec.get("dates") or {}).get("Expiration Date", {}).get("format", "%m/%d/%Y")
    fmt_not = (spec.get("dates") or {}).get("Notice Date", {}).get("format", "%m/%d/%Y")
    counties = set(c.strip() for c in a.counties.split(",")) if a.counties else None
    county_map = (schemas.get("ohcs_affordable_housing_inventory") or {}).get("county_fips") or {}
    vintage = A.file_vintage(a.input)
    source = f"OHCS 10-Year Expiration Forecast {vintage}"
    ohcs = None
    if a.ohcs_leads and os.path.exists(a.ohcs_leads):
        ohcs = pd.read_csv(a.ohcs_leads, dtype=str, keep_default_na=False)
        ohcs["_key"] = [_norm_key(n, ad) for n, ad in zip(ohcs["property_name"], ohcs["address"])]
    prior_status: Dict[str, str] = {}
    if a.prior and os.path.exists(a.prior):
        pdf = A.read_table(a.prior)
        try:
            pcol = A.resolve_columns(pdf, ALIASES, REQUIRED)
            for _, r in pdf.iterrows():
                prior_status[_norm_key(r[pcol["name"]], r.get(pcol.get("address", ""), "") if "address" in pcol else "")] = str(r[pcol["status"]]).strip()
        except A.SchemaMismatch as exc:
            print(f"WARNING prior forecast ignored: {exc}", file=sys.stderr)

    def in_set(status: str, key: str) -> bool:
        return str(status).strip().lower() in {s.lower() for s in (smap.get(key) or [])}

    leads, events, flips = [], [], []
    n_total = n_geo = n_matched = 0
    for r in df.to_dict(orient="records"):
        n_total += 1
        name = str(r[col["name"]]).strip()
        addr = str(r.get(col.get("address", ""), "") if "address" in col else "").strip()
        zipc = str(r.get(col.get("zip", ""), "") if "zip" in col else "")
        county = str(r.get(col.get("county", ""), "") if "county" in col else "")
        fips = G.county_fips_from_name(county, county_map) or ""
        if counties and fips and fips not in counties:
            continue
        if counties and not fips:
            continue  # cannot place the row; a geography that cannot be established is not assumed
        n_geo += 1
        pid = match_to_ohcs(name, addr, zipc, ohcs)
        if pid:
            n_matched += 1
        else:
            pid = G.property_id("OR", fips or None, None, addr, zipc)
        status = str(r[col["status"]]).strip()
        key = _norm_key(name, addr)
        if prior_status and prior_status.get(key) != status:
            flips.append({"property_id": pid, "property_name": name, "status_prior": prior_status.get(key, "(not listed)"), "status_now": status,
                          "flip_into_notice": in_set(status, "notice_received") and not in_set(prior_status.get(key, ""), "notice_received")})
        evs: List[Dict[str, Any]] = []
        exp = D.parse_value(r.get(col.get("expiration", ""), ""), fmt_exp).value if "expiration" in col else None
        if exp:
            evs.append(A.make_event(pid, "REGULATORY_LATEST_END", exp, "REPORTED", source, as_of, vintage, derivation="forecast expiration/termination date (cross-check OAHI LATEST)"))
        if in_set(status, "notice_received"):
            nd = D.parse_value(r.get(col.get("notice_date", ""), ""), fmt_not).value if "notice_date" in col else None
            detail = "push_second" if in_set(status, "second_notice") else ("hap_optout" if "opt" in status.lower() else "push_first")
            ev = A.make_event(pid, "PRESERVATION_NOTICE_RECEIVED", nd or as_of, "RECORDED", source, as_of, vintage, detail=detail,
                              derivation=f"forecast preservation status '{status}'" + ("" if nd else " (no notice date in file; dated as of run)"),
                              verify_flag="" if nd else FLAG_ANCHOR)
            evs.append(ev)
        if in_set(status, "preserved"):
            evs.append(A.make_event(pid, "STABILIZATION_AWARD", as_of, "RECORDED", source, as_of, vintage, detail=status, derivation="forecast status indicates preservation / stabilization"))
        evs = [e for e in evs if e]
        owner = str(r.get(col.get("owner", ""), "") if "owner" in col else "").strip()
        owner_type = infer_owner_type(owner, None, None, "affordable_regulated") if owner else "unknown"
        arch = archetype(owner_type)
        lead = A.blank_lead(property_id=pid, property_name=name, address=addr, city=str(r.get(col.get("city", ""), "") if "city" in col else "").title(), zip=G.zip5(zipc),
                            county_fips=fips, county_name=county.title(), jurisdiction=str(r.get(col.get("city", ""), "") if "city" in col else "").title(),
                            geo_modes="|".join(G.modes_for_fips(fips, r.get(col.get("city", ""), "") if "city" in col else "")), geo_grade="county_field" if fips else "",
                            asset_class="affordable_regulated", status="Active", units=clean_numeric(r.get(col.get("units", ""), ""), True) if "units" in col else "",
                            owner_name=owner, owner_type=owner_type, owner_archetype=arch["archetype"], decision_maker_name="not in public record",
                            decision_maker_role=arch["decision_maker_role"], dm_source="", contact_grade="C",
                            signals=";".join(["ohcs_forecast", f"preservation_status:{status}"]), route=arch["route"], outreach_template=arch["template"],
                            outreach_angle=arch["angle"], source_vintages=f"ohcs_push_forecast={vintage}", as_of_date=as_of.isoformat())
        lead.update({"on_state_expiring_list": True, "preservation_status": status,
                     "assistance_type": str(r.get(col.get("assistance", ""), "") if "assistance" in col else "")})
        fd, fr, inh = A.first_events(evs, a.horizon_years * 12, a.horizon_years * 12)
        A.apply_first(lead, fd, fr, inh)
        leads.append(lead)
        events.extend(evs)
    summary = {"adapter": "ohcs_push_forecast", "as_of_date": as_of.isoformat(), "input_sha256": A.sha256(a.input), "vintage": vintage, "rows_total": n_total,
               "rows_in_geography": n_geo, "matched_to_ohcs_leads": n_matched, "leads": len(leads), "events": len(events), "by_basis": A.basis_breakdown(events),
               "notices": sum(1 for e in events if e["event_type"] == "PRESERVATION_NOTICE_RECEIVED"), "status_flips": len(flips), "verified_live": False,
               "note": "field names and status vocabulary are guesses from the dataset description; confirm from the live export before relying on notice detection"}
    A.write_outputs(a.out_dir, leads, events, summary)
    pd.DataFrame(flips, columns=["property_id", "property_name", "status_prior", "status_now", "flip_into_notice"]).to_csv(os.path.join(a.out_dir, "status_flips.csv"), index=False)
    print(f"[forecast] rows {n_total} in_geography {n_geo} matched_to_ohcs {n_matched} leads {len(leads)} events {len(events)} notices {summary['notices']} status_flips {len(flips)}")
    print("[forecast] basis breakdown: " + " / ".join(f"{k} {v}" for k, v in summary["by_basis"].items()))
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", required=True)
    ap.add_argument("--pack", default=None)
    ap.add_argument("--ohcs-leads", default=None, help="leads.csv from ohcs_inventory_targets.py to reuse property_ids")
    ap.add_argument("--prior", default=None, help="previous forecast export for the quarterly status-flip diff")
    ap.add_argument("--counties", default=None)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--horizon-years", type=float, default=5)
    ap.add_argument("--as-of", default=None)
    run(ap.parse_args(argv))


if __name__ == "__main__":
    main()
