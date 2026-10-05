#!/usr/bin/env python3
"""File-drop adapter: HUD REAC / NSPIRE inspection export -> REAC_SCORE events (REPORTED).

TEMPLATE STATUS: hud.gov was not fetched in this build (verified_live=false); field names are matched through an alias table and
every missing field is named. Emits one REAC_SCORE per property (latest inspection) with `value` = score and `detail` =
protocol (nspire | uphcs) plus `decline_ge_15` when the prior score is >= 15 points higher. Scores below 60 read as troubled-asset
asset management (NSPIRE fail; blocks MU2M renewal), never as a bid discount.

Usage: python scripts/normalize_reac_scores.py --input <reac.csv|xlsx> --pack <dir> [--counties 41051,41067,41005] [--zip-crosswalk <csv>]
           --out-dir <dir> [--as-of YYYY-MM-DD]
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

ALIASES: Dict[str, List[str]] = {
    "property_id": ["property_id", "PROPERTY_ID", "REMS Property Id", "rems_property_id"],
    "name": ["property_name", "PROPERTY_NAME", "Property Name", "property_name_text"],
    "street": ["address", "ADDRESS", "address_line1_text", "Address"],
    "city": ["city", "CITY", "city_name_text"],
    "state": ["state", "STATE", "state_code"],
    "zip": ["zip", "ZIP", "zip_code", "Zip"],
    "county": ["county", "COUNTY", "county_name_text"],
    "score": ["inspection_score", "INSPECTION_SCORE", "Score", "score"],
    "date": ["inspection_date", "INSPECTION_DATE", "Inspection Date"],
    "prior_score": ["prior_score", "PRIOR_SCORE", "previous_score"],
    "protocol": ["protocol", "inspection_protocol", "PROTOCOL"],
}
REQUIRED = ["property_id", "name", "score"]


def _num(v):
    try:
        s = str(v).replace(",", "").strip()
        return float(s) if s and s.lower() != "nan" else None
    except ValueError:
        return None


def run(a) -> Dict[str, Any]:
    as_of = D.parse_as_of(a.as_of)
    df = A.read_table(a.input, a.sheet)
    try:
        col = A.resolve_columns(df, ALIASES, REQUIRED)
    except A.SchemaMismatch as exc:
        print(f"ERROR hud_reac_scores: {exc}", file=sys.stderr)
        sys.exit(2)
    counties = set(c.strip() for c in a.counties.split(",")) if a.counties else None
    resolve = A.county_resolver(a.zip_crosswalk)
    vintage = A.file_vintage(a.input)
    source = f"HUD REAC/NSPIRE export {vintage}"
    leads, events = [], []
    n_total = n_geo = 0
    for r in df.to_dict(orient="records"):
        n_total += 1
        zipc = r.get(col["zip"], "") if "zip" in col else ""
        fips, grade, _ = resolve(zipc, r.get(col["county"]) if "county" in col else None, r.get(col["state"], "OR") if "state" in col else "OR")
        if counties and fips not in counties:
            continue
        n_geo += 1
        addr = str(r.get(col["street"], "")) if "street" in col else ""
        pid = G.property_id("OR", fips, None, addr, zipc)
        score = _num(r[col["score"]])
        if score is None:
            continue
        d = D.parse_value(r.get(col["date"], ""), "iso").value if "date" in col else None
        if d is None and "date" in col:
            d = D.parse_value(r.get(col["date"], ""), "%m/%d/%Y").value
        prior = _num(r.get(col["prior_score"], "")) if "prior_score" in col else None
        detail = str(r.get(col["protocol"], "") if "protocol" in col else "nspire").strip().lower() or "nspire"
        if prior is not None and prior - score >= 15:
            detail += "; decline_ge_15"
        ev = A.make_event(pid, "REAC_SCORE", d or as_of, "REPORTED", source, as_of, vintage, value=int(score), detail=detail, derivation="HUD inspection export (latest score)")
        city = str(r.get(col["city"], "")) if "city" in col else ""
        lead = A.blank_lead(property_id=pid, property_name=str(r[col["name"]]).strip(), address=addr, city=city.title(), zip=G.zip5(zipc), county_fips=fips or "",
                            county_name=G.COUNTY_NAME_BY_FIPS.get(fips or "", ""), jurisdiction=city.title(), geo_modes="|".join(G.modes_for_fips(fips, city)), geo_grade=grade,
                            asset_class="affordable_regulated", status="Active", signals=";".join(["hud_reac", f"reac_score:{int(score)}"] + (["reac_below_60"] if score < 60 else [])),
                            source_vintages=f"hud_reac={vintage}", as_of_date=as_of.isoformat())
        lead["hud_property_id"] = str(r[col["property_id"]]).strip()
        lead["last_reac_score"] = int(score)
        fd, fr, inh = A.first_events([ev], a.horizon_years * 12, a.horizon_years * 12)
        A.apply_first(lead, fd, fr, inh)
        leads.append(lead)
        events.append(ev)
    summary = {"adapter": "hud_reac_scores", "as_of_date": as_of.isoformat(), "input_sha256": A.sha256(a.input), "vintage": vintage, "rows_total": n_total,
               "rows_in_geography": n_geo, "leads": len(leads), "events": len(events), "by_basis": A.basis_breakdown(events), "below_60": sum(1 for e in events if e["value"] < 60),
               "verified_live": False, "note": "field names matched via alias table; confirm against the live HUD export"}
    A.write_outputs(a.out_dir, leads, events, summary)
    print(f"[reac] rows {n_total} in_geography {n_geo} leads {len(leads)} below_60 {summary['below_60']}")
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", required=True)
    ap.add_argument("--sheet", default=None)
    ap.add_argument("--pack", default=None)
    ap.add_argument("--counties", default=None)
    ap.add_argument("--zip-crosswalk", default=None)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--horizon-years", type=float, default=10)
    ap.add_argument("--as-of", default=None)
    run(ap.parse_args(argv))


if __name__ == "__main__":
    main()
