#!/usr/bin/env python3
"""File-drop adapter: HUD Insured Multifamily Mortgages (FHA Subsidiary Ledger) Active [+ Terminated] -> leads/events.

TEMPLATE STATUS: the HUD file could not be fetched live by our researchers (verified_live=false), so the field
names below come from the published layout snippets and are matched through an alias table. The adapter
validates the header and names every missing field instead of guessing. Tested only against the synthetic
fixture scripts/tests/fixtures/hud_fhasl_sample.csv. Confirm field names against the live Excel header on
first run and extend ALIASES if needed.

Emits per property:
  LOAN_MATURITY (RECORDED)              from `Maturity Date`                 -- HUD_DIRECT_LOAN_MATURITY instead when the
                                                                                Section of the Act is in soa_affordable_codes (236, 221(d)(3), 202, 811, 542)
  PREPAY_WINDOW_OPEN (DERIVED, +/-6 mo) from `Final Endorsement Date` + 10y
  REFINANCE_CLOSED + SUPPRESS_UNTIL     from the Terminated file matched on digits-only HUD Project Number
Geography: county from a HUD USPS ZIP-County crosswalk (--zip-crosswalk; highest RES_RATIO wins, straddling
ZIPs flagged) or a county column; never by ZIP prefix.

Usage:
  python scripts/normalize_hud_insured.py --input <FHASL_Active.xlsx|csv> [--terminated <FHASL_Terminated.xlsx|csv>] \
      --pack references/sources/oregon-portland --counties 41051,41067,41005 --zip-crosswalk <crosswalk.csv> \
      --out-dir runs/hud_fhasl [--horizon-years 5] [--as-of YYYY-MM-DD]
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
from omdf.capital_stack import refi_test  # noqa: E402
from omdf.entities import archetype  # noqa: E402
from omdf.schema import load_dataset_schemas, load_market_params  # noqa: E402

ALIASES: Dict[str, List[str]] = {
    "project_number": ["HUD Project Number", "FHA Number", "Project Number", "HUD_PROJECT_NUMBER", "FHA#"],
    "name": ["Property Name", "Project Name", "PROPERTY_NAME_TEXT"],
    "street": ["Property Street", "Property Address", "Street", "ADDRESS_LINE1_TEXT"],
    "city": ["Property City", "Project City", "City", "CITY_NAME_TEXT"],
    "state": ["Property State", "Project State", "State", "STATE_CODE"],
    "zip": ["Property Zip", "Project Zip", "Zip", "ZIP_CODE"],
    "county": ["County", "County Name", "COUNTY_NAME"],
    "units": ["Units", "Number of Units", "TOTAL_UNIT_COUNT", "UNITS"],
    "initial_endorsement": ["Initial Endorsement Date", "INITIAL_ENDORSEMENT_DATE"],
    "final_endorsement": ["Final Endorsement Date", "FINAL_ENDORSEMENT_DATE"],
    "original_amount": ["Original Mortgage Amount", "ORIGINAL_MORTGAGE_AMOUNT", "Mortgage Amount"],
    "first_payment": ["First Payment Date", "FIRST_PAYMENT_DATE"],
    "maturity": ["Maturity Date", "MATURITY_DATE"],
    "term_months": ["Term in Months", "Term (Months)", "TERM_MONTHS"],
    "rate": ["Interest Rate", "INTEREST_RATE", "Note Rate"],
    "upb": ["Amortized Unpaid Principal Balance", "Unpaid Principal Balance", "UPB", "Amortized UPB"],
    "holder": ["Holding Lender Name", "Holder Name", "HOLDER_NAME"],
    "servicer": ["Servicing Lender Name", "Servicer Name", "SERVICER_NAME"],
    "soa_code": ["Section of the Act Code", "SOA Code", "SOA_CODE", "Section of the Act"],
    "soa_desc": ["Section of the Act", "SOA Description", "SOA_DESC"],
}
REQUIRED = ["project_number", "name", "city", "state", "zip", "maturity"]
TERM_ALIASES = {"project_number": ALIASES["project_number"], "termination_date": ["Termination Date", "TERMINATION_DATE"],
                "termination_type": ["Termination Type", "Termination Reason", "TERMINATION_TYPE"]}


def _num(v):
    try:
        s = str(v).replace(",", "").replace("$", "").strip()
        return float(s) if s and s.lower() != "nan" else None
    except ValueError:
        return None


def soa_is_affordable(code: str, affordable_codes: List[str]) -> bool:
    c = str(code or "")
    return any(a in c for a in affordable_codes)


def program_for_soa(code: str) -> List[str]:
    c = str(code or "")
    progs = ["HUD_INSURED"]
    if "236" in c:
        progs.append("HUD_236")
    if "202" in c or "811" in c:
        progs.append("HUD_202_811")
    return progs


def run(a) -> Dict[str, Any]:
    as_of = D.parse_as_of(a.as_of)
    schemas = load_dataset_schemas(a.pack)
    spec = schemas.get("hud_fhasl_active", {})
    affordable_codes = spec.get("soa_affordable_codes", ["236", "221(d)(3)", "202", "811", "542"])
    params = load_market_params(a.pack)
    df = A.read_table(a.input, a.sheet)
    try:
        col = A.resolve_columns(df, ALIASES, REQUIRED)
    except A.SchemaMismatch as exc:
        print(f"ERROR hud_fhasl_active: {exc}", file=sys.stderr)
        sys.exit(2)
    counties = set(c.strip() for c in a.counties.split(",")) if a.counties else None
    resolve = A.county_resolver(a.zip_crosswalk)
    vintage = A.file_vintage(a.input)
    source = f"HUD FHASL Active {vintage}"
    hz = a.horizon_years * 12

    terminated: Dict[str, Dict[str, Any]] = {}
    if a.terminated and os.path.exists(a.terminated):
        tdf = A.read_table(a.terminated)
        try:
            tcol = A.resolve_columns(tdf, TERM_ALIASES, ["project_number", "termination_date"])
            for _, r in tdf.iterrows():
                terminated[A.digits_only(r[tcol["project_number"]])] = {"date": D.parse_value(r[tcol["termination_date"]], "excel_date").value,
                                                                        "type": r.get(tcol.get("termination_type", ""), "") if tcol.get("termination_type") else ""}
        except A.SchemaMismatch as exc:
            print(f"WARNING terminated file ignored: {exc}", file=sys.stderr)

    leads, events = [], []
    n_geo = n_total = 0
    straddle_zips = set()
    for _, r in df.iterrows():
        n_total += 1
        state = str(r[col["state"]]).strip().upper()
        fips, grade, straddles = resolve(r[col["zip"]], r[col["county"]] if "county" in col else None, state)
        if straddles:
            straddle_zips.add(G.zip5(r[col["zip"]]))
        if counties and fips not in counties:
            continue
        if not counties and state not in ("OR", "WA"):
            continue
        n_geo += 1
        pn = str(r[col["project_number"]]).strip()
        pid = G.property_id(state, fips, None, r.get(col.get("street", ""), "") if "street" in col else "", r[col["zip"]])
        soa = str(r.get(col.get("soa_code", ""), "") if "soa_code" in col else "")
        affordable = soa_is_affordable(soa, affordable_codes)
        maturity = D.parse_value(r[col["maturity"]], "excel_date")
        final_end = D.parse_value(r[col["final_endorsement"]], "excel_date").value if "final_endorsement" in col else None
        initial_end = D.parse_value(r[col["initial_endorsement"]], "excel_date").value if "initial_endorsement" in col else None
        first_pay = D.parse_value(r[col["first_payment"]], "excel_date").value if "first_payment" in col else None
        # the loan term runs from amortization start; initial endorsement can precede it by 1-3 construction years
        orig = first_pay or final_end or initial_end
        evs: List[Dict[str, Any]] = []
        flag = ""
        if maturity.value and orig and not (orig < maturity.value < D.add_years(orig, 45)):
            flag = "Rejected — Out of Range"
        et = "HUD_DIRECT_LOAN_MATURITY" if affordable else "LOAN_MATURITY"
        ev = A.make_event(pid, et, maturity.value, "RECORDED", source, as_of, vintage, derivation="HUD FHASL Maturity Date", program="HUD_INSURED",
                          detail=("236_irp" if "236" in soa else ""), verify_flag=flag or maturity.flag or "", lender_type="hud_fha")
        if ev:
            if flag:
                ev["status"] = "REJECTED"
            evs.append(ev)
        if final_end:
            d = D.add_years(final_end, 10)
            evs.append(A.make_event(pid, "PREPAY_WINDOW_OPEN", d, "DERIVED", source, as_of, vintage, derivation="Final Endorsement Date + 10y (penalty step-down end; verify note)",
                                    window_start=D.add_months(d, -6).isoformat(), window_end=D.add_months(d, 6).isoformat()))
        t = terminated.get(A.digits_only(pn))
        if t and t["date"]:
            evs.append(A.make_event(pid, "REFINANCE_CLOSED", t["date"], "RECORDED", f"HUD FHASL Terminated ({t['type'] or 'terminated'})", as_of, vintage,
                                    derivation="Terminated file row matched on digits-only HUD Project Number", detail=str(t["type"] or "")))
            evs.append(A.make_event(pid, "SUPPRESS_UNTIL", D.add_years(t["date"], 5), "DERIVED", source, as_of, vintage,
                                    derivation="termination date + 5y (min bank term; successor lender unknown)"))
        upb = _num(r[col["upb"]]) if "upb" in col else None
        rate = _num(r[col["rate"]]) if "rate" in col else None
        rate = rate / 100.0 if rate and rate > 1 else rate
        rt = refi_test(None, upb, None, params, note_rate=rate, affordable=affordable)
        lead = A.blank_lead(
            property_id=pid, property_name=str(r[col["name"]]).strip(), address=str(r.get(col.get("street", ""), "")).strip() if "street" in col else "",
            city=str(r[col["city"]]).strip().title(), zip=G.zip5(r[col["zip"]]), county_fips=fips or "", county_name=G.COUNTY_NAME_BY_FIPS.get(fips or "", ""),
            jurisdiction=str(r[col["city"]]).strip().title(), geo_modes="|".join(G.modes_for_fips(fips, r[col["city"]])), geo_grade=grade,
            asset_class="affordable_regulated" if affordable else "market_rate_mf", status="Active", units=_num(r[col["units"]]) if "units" in col else "",
            programs=";".join(program_for_soa(soa)), owner_name="", owner_type="unknown", owner_archetype="Unresolved entity (HUD insured file has no owner; join HUD Sec 8 / assessor)",
            decision_maker_name="not in public record", decision_maker_role="not in public record", dm_source="", contact_grade="C",
            est_loan_balance=upb if upb is not None else "", balance_basis="REPORTED" if upb is not None else "", assumable_debt=True,
            signals="hud_insured;soa:" + soa.replace(";", ","), source_vintages=f"hud_fhasl_active={vintage}", as_of_date=as_of.isoformat(),
            route=archetype("unknown")["route"], outreach_template="hud_usda_assisted_owner" if affordable else "single_asset_llc",
        )
        lead.update({"hud_project_number": pn, "lender_type": "hud_fha", "note_rate": rate if rate is not None else "", "holder": str(r.get(col.get("holder", ""), "")) if "holder" in col else "",
                     "servicer": str(r.get(col.get("servicer", ""), "")) if "servicer" in col else "", "soa": soa,
                     "rate_spread_bp": rt["rate_spread_bp"] if rt["rate_spread_bp"] is not None else "", "zip_straddles_counties": straddles})
        fd, fr, inh = A.first_events(evs, hz, hz)
        A.apply_first(lead, fd, fr, inh)
        if straddles:
            lead["verify_flags"] = "Verify — Ambiguous: ZIP straddles counties; confirm parcel county"
        leads.append(lead)
        events.extend(e for e in evs if e)
    summary = {"adapter": "hud_fhasl_active", "as_of_date": as_of.isoformat(), "input_sha256": A.sha256(a.input), "vintage": vintage, "rows_total": n_total,
               "rows_in_geography": n_geo, "leads": len(leads), "events": len(events), "by_basis": A.basis_breakdown(events),
               "straddling_zips": sorted(straddle_zips), "terminated_matched": sum(1 for e in events if e["event_type"] == "REFINANCE_CLOSED"),
               "verified_live": False, "note": "field names matched via alias table; confirm against the live HUD header"}
    A.write_outputs(a.out_dir, leads, events, summary)
    bb = summary["by_basis"]
    print(f"[hud_fhasl] rows {n_total} in_geography {n_geo} leads {len(leads)} events {len(events)} terminated_matched {summary['terminated_matched']}")
    print("[hud_fhasl] basis breakdown: " + " / ".join(f"{k} {v}" for k, v in bb.items()))
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", required=True)
    ap.add_argument("--terminated", default=None)
    ap.add_argument("--sheet", default=None)
    ap.add_argument("--pack", default=None)
    ap.add_argument("--counties", default=None, help="comma list of county FIPS; default: all OR/WA rows")
    ap.add_argument("--zip-crosswalk", default=None, help="HUD USPS ZIP-County crosswalk CSV (ZIP, COUNTY, RES_RATIO)")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--horizon-years", type=float, default=5)
    ap.add_argument("--as-of", default=None)
    run(ap.parse_args(argv))


if __name__ == "__main__":
    main()
