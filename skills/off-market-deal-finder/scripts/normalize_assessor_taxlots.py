#!/usr/bin/env python3
"""File-drop adapter: assessor taxlot extract (Multnomah SAIL / Metro RLIS field names) -> leads/events for classes 1 and 2.

TEMPLATE STATUS: the SAIL FeatureServer and RLIS layers were not fetched in this build (verified_live=false); field
names come from a third-party query tool and are declared in dataset-schemas.yaml `assessor_taxlots`. Rename other
counties' exports (Washington Co. A&T, Clackamas AscendWeb, Clark GIS) to these names before dropping.

Emits per taxlot (all RECORDED, basis of the roll itself):
  HOLD_YEARS                (value = years since DEED_DATE)          DEPRECIATION_EXHAUSTED when >= 27.5
  RECENT_1031_ACQUISITION   when hold < 3 y (suppression; exchange language is not visible in the roll)
  ABSENTEE_TIER             (value in occupant | local | in_state | out_of_state | far) from mailing vs situs
  TAX_DELINQUENT_YEARS      when a DELQ_YEARS column is present (value = years)
Lead fields: mailing_address (the Step 6 hop-1 address), av_rmv_ratio = ROLLM50 / (ROLLLAND + ROLLIMP),
est_value = RMV x pack `rmv_sales_ratio` (default 1.0) with value_source rmv_calibrated, owner_type from the NAME
string (individual vs LLC/trust), asset_class from UNITS (<= 4 sfr_small_res, else market_rate_mf) unless overridden.
Assessed Value is never used as value (Measure 50); AV/RMV is a tenure signal only.

Usage:
  python scripts/normalize_assessor_taxlots.py --input <taxlots.csv> --pack references/sources/oregon-portland \
      [--county-fips 41051] [--asset-class auto|sfr_small_res|market_rate_mf] --out-dir runs/x/assessor [--as-of YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import Any, Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from omdf import adapters as A  # noqa: E402
from omdf import dates as D  # noqa: E402
from omdf import geo as G  # noqa: E402
from omdf.entities import archetype, infer_owner_type  # noqa: E402
from omdf.schema import apply_numeric_block, clean_numeric, detect_schema, load_dataset_schemas, load_market_params, param  # noqa: E402

PORTLAND_CBSA_STATES = {"OR", "WA"}
METRO_CITIES = {c.upper() for c in G.METRO_JURISDICTIONS}


def absentee_tier(mail_addr: str, mail_city: str, mail_state: str, mail_zip: str, situs_addr: str, situs_city: str, situs_zip: str) -> str:
    if G.normalize_address(mail_addr) and G.normalize_address(mail_addr) == G.normalize_address(situs_addr) and (not situs_zip or not mail_zip or G.zip5(mail_zip) == G.zip5(situs_zip)):
        return "occupant"
    st = (mail_state or "").strip().upper()
    if st in ("OR", "WA") and (mail_city or "").strip().upper() in METRO_CITIES:
        return "local"
    if st == "OR":
        return "in_state"
    if st in ("", None):
        return "in_state"
    if st in ("WA", "CA", "ID", "NV"):
        return "out_of_state"
    return "far"


def run(a) -> Dict[str, Any]:
    as_of = D.parse_as_of(a.as_of)
    schemas = load_dataset_schemas(a.pack)
    spec = schemas.get("assessor_taxlots") or {}
    params = load_market_params(a.pack)
    df = A.read_table(a.input)
    sid = detect_schema(list(df.columns), schemas)
    if sid != "assessor_taxlots":
        print(f"ERROR: input does not match assessor_taxlots (detected {sid}); required columns: {spec.get('match_columns')}; file columns: {list(df.columns)}", file=sys.stderr)
        sys.exit(2)
    apply_numeric_block(df, spec)
    fips_default = a.county_fips or spec.get("default_county_fips") or "41051"
    vintage = A.file_vintage(a.input)
    source = f"assessor taxlot roll {vintage}"
    fmt = (spec.get("dates") or {}).get("DEED_DATE", {}).get("format", "%Y-%m-%d")
    sales_ratio = float(param(params, "rmv_sales_ratio", 1.0) or 1.0)
    hz = a.horizon_years * 12
    leads, events = [], []
    n_total = 0
    for r in df.to_dict(orient="records"):
        n_total += 1
        fips = str(r.get("COUNTY_FIPS") or (G.county_fips_from_name(r.get("COUNTY")) if r.get("COUNTY") else "") or fips_default)
        state = G.STATE_BY_FIPS_PREFIX.get(fips[:2], "OR")
        situs = str(r.get("SITUSADDR") or "")
        situs_city = str(r.get("SITUSCITY") or "")
        situs_zip = str(r.get("SITUSZIP") or r.get("ZIP") or "")
        parcel = str(r.get("PROPID") or r.get("MAPTAXLOT") or "").strip()
        pid = G.property_id(state, fips, parcel or None, situs, situs_zip)
        name = str(r.get("NAME") or "").strip()
        mail = f"{r.get('ADDR1') or ''}, {r.get('CITY') or ''} {r.get('STATE') or ''} {r.get('ZIP') or ''}".strip(", ")
        tier = absentee_tier(str(r.get("ADDR1") or ""), str(r.get("CITY") or ""), str(r.get("STATE") or ""), str(r.get("ZIP") or ""), situs, situs_city, situs_zip)
        units = clean_numeric(r.get("UNITS"), True)
        cls = a.asset_class if a.asset_class != "auto" else ("sfr_small_res" if (units or 1) <= 4 else "market_rate_mf")
        evs: List[Dict[str, Any]] = []
        deed = D.parse_value(r.get("DEED_DATE"), fmt).value if str(r.get("DEED_DATE") or "").strip() else None
        hold = None
        if deed:
            hold = round((as_of - deed).days / 365.25, 1)
            evs.append(A.make_event(pid, "HOLD_YEARS", deed, "RECORDED", source, as_of, vintage, value=hold, derivation="(as_of - DEED_DATE) / 365.25"))
            if hold >= 27.5:
                evs.append(A.make_event(pid, "DEPRECIATION_EXHAUSTED", deed, "RECORDED", source, as_of, vintage, value=hold, derivation="HOLD_YEARS >= 27.5 (IRS Pub 527 residential recovery)"))
            if hold < 3:
                evs.append(A.make_event(pid, "RECENT_1031_ACQUISITION", deed, "RECORDED", source, as_of, vintage, value=hold, derivation="hold < 3y (exchange language not visible in the roll)"))
        evs.append(A.make_event(pid, "ABSENTEE_TIER", as_of, "RECORDED", source, as_of, vintage, value=tier, derivation="mailing address vs situs after USPS normalization"))
        dq = clean_numeric(r.get("DELQ_YEARS"), True)
        if dq:
            evs.append(A.make_event(pid, "TAX_DELINQUENT_YEARS", as_of, "RECORDED", source, as_of, vintage, value=dq, derivation="assessor payment history (DELQ_YEARS)"))
        land, imp, av = clean_numeric(r.get("ROLLLAND"), False), clean_numeric(r.get("ROLLIMP"), False), clean_numeric(r.get("ROLLM50"), False)
        rmv = (land or 0) + (imp or 0) if (land is not None or imp is not None) else None
        ratio = round(av / rmv, 3) if (av and rmv) else ""
        est_value = round(rmv * sales_ratio, 0) if rmv else ""
        owner_type = infer_owner_type(name, None, None, cls)
        if owner_type == "individual_absentee" and tier == "occupant":
            owner_type = "individual_occupant"
        arch = archetype(owner_type)
        lead = A.blank_lead(property_id=pid, property_name=name or situs, address=situs, city=situs_city.title(), zip=G.zip5(situs_zip), county_fips=fips,
                            county_name=G.COUNTY_NAME_BY_FIPS.get(fips, ""), jurisdiction=situs_city.title(), geo_modes="|".join(G.modes_for_fips(fips, situs_city)),
                            geo_grade="county_field", asset_class=cls, status="Active", units=units if units is not None else "",
                            year_built=clean_numeric(r.get("ACTYEARBUILT"), True) or "", owner_name=name, owner_type=owner_type, owner_archetype=arch["archetype"],
                            decision_maker_name=name if owner_type.startswith("individual") else "not in public record",
                            decision_maker_role="owner of record" if owner_type.startswith("individual") else arch["decision_maker_role"],
                            dm_source="assessor roll NAME + mailing address (hop 1)", contact_grade="C",
                            est_value=est_value, value_source=f"rmv_calibrated (RMV x sales_ratio {sales_ratio}; AV never used, Measure 50)" if est_value else "not computed (no RMV)",
                            signals=";".join(["assessor_roll", f"absentee:{tier}"] + (["depreciation_exhausted"] if hold is not None and hold >= 27.5 else [])),
                            route=arch["route"], outreach_template=arch["template"], outreach_angle=arch["angle"],
                            source_vintages=f"assessor_taxlots={vintage}", as_of_date=as_of.isoformat())
        lead.update({"mailing_address": mail, "av_rmv_ratio": ratio, "hold_years": hold if hold is not None else "", "rmv": rmv if rmv else "",
                     "parcel_id": parcel, "sale_price": clean_numeric(r.get("SALE_PRICE"), False) or "", "exemption_code": str(r.get("EXEMPTION") or "")})
        evs = [e for e in evs if e]
        fd, fr, inh = A.first_events(evs, hz, hz)
        A.apply_first(lead, fd, fr, inh)
        leads.append(lead)
        events.extend(evs)
    summary = {"adapter": "assessor_taxlots", "as_of_date": as_of.isoformat(), "input_sha256": A.sha256(a.input), "vintage": vintage, "rows_total": n_total,
               "rows_in_geography": n_total, "leads": len(leads), "events": len(events), "by_basis": A.basis_breakdown(events), "verified_live": False,
               "note": "SAIL/RLIS field names from a third-party query tool; confirm on first pull. Assessor facts count once in stacking."}
    A.write_outputs(a.out_dir, leads, events, summary)
    print(f"[assessor] rows {n_total} leads {len(leads)} events {len(events)}")
    print("[assessor] basis breakdown: " + " / ".join(f"{k} {v}" for k, v in summary["by_basis"].items()))
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", required=True)
    ap.add_argument("--pack", default=None)
    ap.add_argument("--county-fips", default=None, help="county FIPS when the file has no COUNTY / COUNTY_FIPS column (default 41051)")
    ap.add_argument("--asset-class", default="auto", choices=["auto", "sfr_small_res", "market_rate_mf"])
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--horizon-years", type=float, default=5)
    ap.add_argument("--as-of", default=None)
    run(ap.parse_args(argv))


if __name__ == "__main__":
    main()
