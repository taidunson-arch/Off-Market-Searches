#!/usr/bin/env python3
"""File-drop adapter: HUD Multifamily Assistance & Section 8 Contracts database -> leads/events.

TEMPLATE STATUS: hud.gov could not be fetched live by our researchers (verified_live=false). Field names come
from the TRACS extract data dictionary snippets and are matched through an alias table; the adapter names every
missing field rather than guessing. Tested only on scripts/tests/fixtures/hud_sec8_sample.csv.

Input: the contracts table (one row per HAP/PRAC/PAC contract). `--properties` optionally joins the property
table on property_id for owner / management-agent names when the contracts table lacks them.

Emits per contract:
  HAP_EXPIRATION (REPORTED, confidence 0.70)  from tracs_overall_expiration_date; detail = short_renewal_pattern
                                              (overall - effective <= 5y) or mahra_20yr_recent (>= 20y and effective <= 3y ago)
  HAP_OPTOUT_NOTICE_DEADLINE (DERIVED)        expiration - 12 months (federal one-year opt-out notice)
Signals: below_fmr_optout_risk (rent_to_FMR < 0.85), above_fmr_renewal_incentive (> 1.0), fha:<number> join hint.

Usage:
  python scripts/normalize_hud_sec8.py --input <MF_Assistance_&_Sec8_Contracts.xlsx|csv> [--properties <MF_Properties.xlsx>] \
      --pack references/sources/oregon-portland --counties 41051,41067,41005 --zip-crosswalk <crosswalk.csv> \
      --out-dir runs/hud_sec8 [--horizon-years 5] [--as-of YYYY-MM-DD]
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

ALIASES: Dict[str, List[str]] = {
    "property_id": ["property_id", "PROPERTY_ID", "REMS Property Id"],
    "name": ["property_name_text", "PROPERTY_NAME_TEXT", "Property Name"],
    "street": ["address_line1_text", "ADDRESS_LINE1_TEXT", "Address"],
    "city": ["city_name_text", "CITY_NAME_TEXT", "City"],
    "state": ["state_code", "STATE_CODE", "State"],
    "zip": ["zip_code", "ZIP_CODE", "Zip"],
    "county": ["county_name_text", "county", "COUNTY_NAME_TEXT", "County"],
    "contract": ["contract_number", "CONTRACT_NUMBER"],
    "program": ["program_type_name", "PROGRAM_TYPE_NAME", "Program Type"],
    "effective": ["tracs_effective_date", "TRACS_EFFECTIVE_DATE"],
    "expiration": ["tracs_overall_expiration_date", "TRACS_OVERALL_EXPIRATION_DATE"],
    "current_expiration": ["tracs_current_expiration_date", "TRACS_CURRENT_EXPIRATION_DATE"],
    "assisted_units": ["assisted_units_count", "ASSISTED_UNITS_COUNT"],
    "total_units": ["property_total_unit_count", "PROPERTY_TOTAL_UNIT_COUNT", "Total Units"],
    "rent_to_fmr": ["rent_to_FMR_ratio", "rent_to_fmr_ratio", "RENT_TO_FMR_RATIO"],
    "owner": ["owner_organization_name", "OWNER_ORGANIZATION_NAME"],
    "owner_phone": ["owner_main_phone_number_text", "OWNER_MAIN_PHONE_NUMBER_TEXT"],
    "mgmt": ["mgmt_agent_org_name", "MGMT_AGENT_ORG_NAME"],
    "fha": ["primary_fha_number", "PRIMARY_FHA_NUMBER"],
}
REQUIRED = ["property_id", "name", "city", "state", "zip", "expiration"]


def _num(v):
    try:
        s = str(v).replace(",", "").strip()
        return float(s) if s and s.lower() != "nan" else None
    except ValueError:
        return None


def program_enum(program_name: str) -> str:
    p = str(program_name or "").upper()
    if "PRAC" in p:
        return "PRAC"
    if "PAC" in p:
        return "PAC"
    if "RAP" in p or "RENT SUPP" in p:
        return "RAC"
    return "HAP"


def run(a) -> Dict[str, Any]:
    as_of = D.parse_as_of(a.as_of)
    df = A.read_table(a.input, a.sheet)
    try:
        col = A.resolve_columns(df, ALIASES, REQUIRED)
    except A.SchemaMismatch as exc:
        print(f"ERROR hud_mf_assistance_sec8: {exc}", file=sys.stderr)
        sys.exit(2)
    props = {}
    if a.properties and os.path.exists(a.properties):
        pdf = A.read_table(a.properties)
        try:
            pcol = A.resolve_columns(pdf, ALIASES, ["property_id"])
            for _, r in pdf.iterrows():
                props[str(r[pcol["property_id"]]).strip()] = {k: r[pcol[k]] for k in ("owner", "mgmt", "owner_phone", "total_units") if k in pcol}
        except A.SchemaMismatch as exc:
            print(f"WARNING properties file ignored: {exc}", file=sys.stderr)
    counties = set(c.strip() for c in a.counties.split(",")) if a.counties else None
    resolve = A.county_resolver(a.zip_crosswalk)
    vintage = A.file_vintage(a.input)
    source = f"HUD MF Assistance & Sec 8 {vintage}"
    hz = a.horizon_years * 12

    by_pid: Dict[str, Dict[str, Any]] = {}
    events_by_pid: Dict[str, List[Dict[str, Any]]] = {}
    n_total = n_geo = 0
    for _, r in df.iterrows():
        n_total += 1
        state = str(r[col["state"]]).strip().upper()
        fips, grade, straddles = resolve(r[col["zip"]], r[col["county"]] if "county" in col else None, state)
        if counties and fips not in counties:
            continue
        if not counties and state not in ("OR", "WA"):
            continue
        n_geo += 1
        hud_pid = str(r[col["property_id"]]).strip()
        pid = G.property_id(state, fips, None, r.get(col.get("street", ""), "") if "street" in col else "", r[col["zip"]])
        prop = props.get(hud_pid, {})
        owner = str(r.get(col.get("owner", ""), "") if "owner" in col else prop.get("owner", "")).strip()
        mgmt = str(r.get(col.get("mgmt", ""), "") if "mgmt" in col else prop.get("mgmt", "")).strip()
        prog = program_enum(r[col["program"]] if "program" in col else "")
        exp = D.parse_value(r[col["expiration"]], "excel_date").value
        eff = D.parse_value(r[col["effective"]], "excel_date").value if "effective" in col else None
        detail = ""
        if exp and eff:
            term_y = (exp - eff).days / 365.25
            if term_y <= 5:
                detail = "short_renewal_pattern"
            elif term_y >= 20 and (as_of - eff).days <= 3 * 365:
                detail = "mahra_20yr_recent"
        rtf = _num(r[col["rent_to_fmr"]]) if "rent_to_fmr" in col else None
        signals = ["hud_sec8", f"program:{prog}"]
        if rtf is not None:
            signals.append("below_fmr_optout_risk" if rtf < 0.85 else ("above_fmr_renewal_incentive" if rtf > 1.0 else "near_fmr"))
        fha = str(r.get(col.get("fha", ""), "") if "fha" in col else "").strip()
        if fha and fha.lower() != "nan":
            signals.append("fha:" + A.digits_only(fha))
        evs = []
        ev = A.make_event(pid, "HAP_EXPIRATION", exp, "REPORTED", source, as_of, vintage, confidence=0.70, program=prog, detail=detail,
                          derivation="tracs_overall_expiration_date (annual renewals roll forward; 0.70 confidence)", value=rtf if rtf is not None else "")
        if ev:
            evs.append(ev)
            evs.append(A.make_event(pid, "HAP_OPTOUT_NOTICE_DEADLINE", D.add_months(exp, -12), "DERIVED", source, as_of, vintage,
                                    derivation="HAP_EXPIRATION - 12 months (federal one-year opt-out notice)", program=prog))
        units = _num(r[col["total_units"]]) if "total_units" in col else _num(prop.get("total_units"))
        owner_type = infer_owner_type(owner, None, None, "affordable_regulated")
        arch = archetype(owner_type)
        lead = by_pid.get(pid) or A.blank_lead(
            property_id=pid, property_name=str(r[col["name"]]).strip(), address=str(r.get(col.get("street", ""), "")).strip() if "street" in col else "",
            city=str(r[col["city"]]).strip().title(), zip=G.zip5(r[col["zip"]]), county_fips=fips or "", county_name=G.COUNTY_NAME_BY_FIPS.get(fips or "", ""),
            jurisdiction=str(r[col["city"]]).strip().title(), geo_modes="|".join(G.modes_for_fips(fips, r[col["city"]])), geo_grade=grade,
            asset_class="affordable_regulated", status="Active", units=units if units is not None else "", programs="", hud_contract={"HAP": "Housing Assistance Payment", "PRAC": "Project Rental Assistance Contract", "PAC": "Project Assistance Contract", "RAC": "Rental Assistance Contract"}[prog],
            rental_assistance_units=_num(r[col["assisted_units"]]) if "assisted_units" in col else "", owner_name=owner, owner_type=owner_type, owner_archetype=arch["archetype"],
            manager_name=mgmt, decision_maker_name="not in public record", decision_maker_role=arch["decision_maker_role"],
            dm_source="HUD owner_organization_name / mgmt_agent_org_name (entity only)", contact_grade="C", route=arch["route"],
            outreach_template="hud_usda_assisted_owner" if owner_type in ("lihtc_partnership_forprofit_gp", "single_asset_llc", "regional_operator", "institutional", "unknown") else arch["template"],
            outreach_angle=arch["angle"], source_vintages=f"hud_mf_sec8={vintage}", as_of_date=as_of.isoformat(),
        )
        lead["programs"] = ";".join(dict.fromkeys([p for p in (lead["programs"].split(";") if lead["programs"] else []) + [prog]]))
        lead["signals"] = ";".join(dict.fromkeys([s for s in (lead["signals"].split(";") if lead["signals"] else []) + signals]))
        lead["hud_property_id"] = hud_pid
        lead["owner_phone"] = str(r.get(col.get("owner_phone", ""), "") if "owner_phone" in col else prop.get("owner_phone", ""))
        lead["rent_to_fmr_ratio"] = rtf if rtf is not None else ""
        lead["primary_fha_number"] = A.digits_only(fha)
        if straddles:
            lead["verify_flags"] = "Verify — Ambiguous: ZIP straddles counties; confirm parcel county"
        by_pid[pid] = lead
        events_by_pid.setdefault(pid, []).extend(e for e in evs if e)
    leads, events = [], []
    for pid, lead in by_pid.items():
        evs = events_by_pid.get(pid, [])
        fd, fr, inh = A.first_events(evs, hz, hz)
        A.apply_first(lead, fd, fr, inh)
        leads.append(lead)
        events.extend(evs)
    summary = {"adapter": "hud_mf_assistance_sec8", "as_of_date": as_of.isoformat(), "input_sha256": A.sha256(a.input), "vintage": vintage,
               "rows_total": n_total, "rows_in_geography": n_geo, "leads": len(leads), "events": len(events), "by_basis": A.basis_breakdown(events),
               "verified_live": False, "note": "field names matched via alias table; HAP expirations under annual renewal roll forward (confidence 0.70)"}
    A.write_outputs(a.out_dir, leads, events, summary)
    print(f"[hud_sec8] rows {n_total} in_geography {n_geo} leads {len(leads)} events {len(events)}")
    print("[hud_sec8] basis breakdown: " + " / ".join(f"{k} {v}" for k, v in summary["by_basis"].items()))
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", required=True, help="contracts table")
    ap.add_argument("--properties", default=None, help="property table (joined on property_id)")
    ap.add_argument("--sheet", default=None)
    ap.add_argument("--pack", default=None)
    ap.add_argument("--counties", default=None)
    ap.add_argument("--zip-crosswalk", default=None)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--horizon-years", type=float, default=5)
    ap.add_argument("--as-of", default=None)
    run(ap.parse_args(argv))


if __name__ == "__main__":
    main()
