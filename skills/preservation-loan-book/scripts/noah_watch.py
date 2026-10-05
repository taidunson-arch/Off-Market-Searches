#!/usr/bin/env python3
"""OPTIONAL NOAH watch adapter (off by default; references/noah-watch.md). Enable only with `--noah-watch` on build_universe.py.

Reads a manual `noah_candidates.csv` of unregulated 5+ unit properties absent from OHCS / HUD / NHPD with columns
  property_name, address, city, zip, county_fips, units, year_built, hold_years, tax_delinquent_years, est_rent, fmr, lender_type, maturity, owner_name
and emits leads with asset_class noah_unregulated plus RECORDED/REPORTED events: HOLD_YEARS, TAX_DELINQUENT_YEARS, LOAN_MATURITY (REPORTED, only
when a maturity is stated), and the rent_to_fmr_ratio column. Scoring uses references/scoring/noah_watch.json; the only route is nofa_offer
(acquisition_grant product) with owner_outreach false. No valuation beyond the rent / FMR gap, no outreach.

Usage: python scripts/noah_watch.py --input noah_candidates.csv --pack <dir> --out-dir <dir> [--as-of YYYY-MM-DD] [--horizon-years 10]
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import Any, Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plb import adapters as A  # noqa: E402
from plb import dates as D  # noqa: E402
from plb import geo as G  # noqa: E402
from plb.entities import infer_owner_type  # noqa: E402
from plb.schema import clean_numeric  # noqa: E402

ALIASES: Dict[str, List[str]] = {
    "name": ["property_name", "Property Name"], "address": ["address", "Address"], "city": ["city", "City"], "zip": ["zip", "Zip"],
    "county_fips": ["county_fips"], "units": ["units", "Units"], "year_built": ["year_built"], "hold_years": ["hold_years"],
    "tax_delinquent_years": ["tax_delinquent_years"], "est_rent": ["est_rent", "rent"], "fmr": ["fmr", "safmr"], "lender_type": ["lender_type"],
    "maturity": ["maturity", "maturity_date"], "owner": ["owner_name", "Owner Name"],
}
REQUIRED = ["name", "address", "zip", "units"]


def run(a) -> Dict[str, Any]:
    as_of = D.parse_as_of(a.as_of)
    df = A.read_table(a.input)
    try:
        col = A.resolve_columns(df, ALIASES, REQUIRED)
    except A.SchemaMismatch as exc:
        print(f"ERROR noah_candidates: {exc}", file=sys.stderr)
        sys.exit(2)
    vintage = A.file_vintage(a.input)
    source = f"noah_candidates (manual) {vintage}"
    leads, events = [], []
    for r in df.to_dict(orient="records"):
        units = clean_numeric(r.get(col["units"]), True)
        if units is None or units < 5:
            continue
        fips = str(r.get(col.get("county_fips", ""), "") if "county_fips" in col else "").strip()
        pid = G.property_id("OR", fips or None, None, r[col["address"]], r[col["zip"]])
        evs = []
        hy = clean_numeric(r.get(col.get("hold_years", ""), ""), False) if "hold_years" in col else None
        if hy is not None:
            evs.append(A.make_event(pid, "HOLD_YEARS", as_of, "RECORDED", source, as_of, vintage, value=hy, derivation="assessor deed date (manual)"))
        ty = clean_numeric(r.get(col.get("tax_delinquent_years", ""), ""), True) if "tax_delinquent_years" in col else None
        if ty:
            evs.append(A.make_event(pid, "TAX_DELINQUENT_YEARS", as_of, "RECORDED", source, as_of, vintage, value=ty, derivation="assessor payment history (manual)"))
        if "maturity" in col:
            m = D.parse_value(r.get(col["maturity"], ""), "iso").value
            if m:
                evs.append(A.make_event(pid, "LOAN_MATURITY", m, "REPORTED", source, as_of, vintage, derivation="stated maturity (manual)", detail=f"lender_type={r.get(col.get('lender_type', ''), '') if 'lender_type' in col else 'unknown'}"))
        rent = clean_numeric(r.get(col.get("est_rent", ""), ""), False) if "est_rent" in col else None
        fmr = clean_numeric(r.get(col.get("fmr", ""), ""), False) if "fmr" in col else None
        owner = str(r.get(col.get("owner", ""), "") if "owner" in col else "").strip()
        lead = A.blank_lead(property_id=pid, property_name=str(r[col["name"]]).strip(), address=str(r[col["address"]]).strip(), city=str(r.get(col.get("city", ""), "")).title() if "city" in col else "",
                            zip=G.zip5(r[col["zip"]]), county_fips=fips, county_name=G.COUNTY_NAME_BY_FIPS.get(fips, ""), geo_modes="|".join(G.modes_for_fips(fips, r.get(col.get("city", ""), ""))) if fips else "",
                            geo_grade="county_field" if fips else "", asset_class="noah_unregulated", status="Active", units=units, year_built=clean_numeric(r.get(col.get("year_built", ""), ""), True) if "year_built" in col else "",
                            owner_name=owner, owner_type=infer_owner_type(owner, None, None, "noah_unregulated") if owner else "unknown", universe="universe_not_held", in_inventory=False,
                            restricted_units=0, units_at_risk=units, units_basis="proxy", signals="noah_candidate;owner_outreach:false", source_vintages=f"noah_candidates={vintage}",
                            as_of_date=as_of.isoformat(), pii_scope="organization")
        lead["rent_to_fmr_ratio"] = round(rent / fmr, 3) if rent and fmr else ""
        lead["hold_years"] = hy if hy is not None else ""
        fd, fr, inh = A.first_events([e for e in evs if e], a.horizon_years * 12, a.horizon_years * 12)
        A.apply_first(lead, fd, fr, inh)
        leads.append(lead)
        events.extend(e for e in evs if e)
    summary = {"adapter": "noah_candidates", "as_of_date": as_of.isoformat(), "input_sha256": A.sha256(a.input), "vintage": vintage, "leads": len(leads), "events": len(events),
               "by_basis": A.basis_breakdown(events), "note": "optional NOAH watch; route nofa_offer only; owner_outreach false"}
    A.write_outputs(a.out_dir, leads, events, summary)
    print(f"[noah] leads {len(leads)} events {len(events)}")
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", required=True)
    ap.add_argument("--pack", default=None)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--horizon-years", type=float, default=10)
    ap.add_argument("--as-of", default=None)
    run(ap.parse_args(argv))


if __name__ == "__main__":
    main()
