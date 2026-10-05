#!/usr/bin/env python3
"""Two universes, one merge: build the lead / event universe for a public-agency asset manager (BUILD SPEC Section 4).

Order: (1) ingest_servicing_extract.py (the agency's own book, RECORDED) -> (2) ohcs_inventory_targets.py -> (3) optional HUD Sec 8,
HUD FHASL, OHCS forecast, REAC adapters -> (4) merge_leads with plb/book_join (crosswalk > address > fuzzy > unmatched) and universe tagging
-> (5) plb/units.py fills (units at risk, coterminous senior cliff, public UPB at risk, recapture exposure) -> (6) plb/agency_calendar.py
(withdrawal anchor, both PuSH windows, every AGENCY_DEADLINE, NOTICE_COMPLIANCE_BREACH, stale HAP dates, owner cliff / agency act-by / action band).

Outputs in --out-dir: adapter_<schema>/..., leads.csv, events.csv, rejects.csv, merge_log.csv, servicing_unmatched.csv, book_join_gaps.csv,
pipeline_not_scored.csv, calendar_summary.json (basis header with helper and agency act-by segments). Without --book the run is universe-only
(book_match book_absent for every row; the degraded statement is written into calendar_summary.json).

Usage:
  python scripts/build_universe.py --pack <dir> --mode metro_core --agency-profile hfa --ohcs <csv> [--book <csv>] [--book-coverage partial]
      [--hud-sec8 <csv> [--hud-sec8-properties <csv>]] [--hud-fhasl <xlsx> [--hud-fhasl-terminated <xlsx>]] [--forecast <csv> [--prior-forecast <csv>]]
      [--reac <csv>] [--zip-crosswalk <csv>] [--include-proxies] [--noah-watch --noah <csv>] --horizon-years 10 --out-dir <dir> [--as-of YYYY-MM-DD] [--internal]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from typing import Any, Dict, List, Optional

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from merge_leads import merge  # noqa: E402
from plb import agency_calendar as AC  # noqa: E402
from plb.book_join import join_book, load_crosswalk  # noqa: E402
from plb.calendar import header_line  # noqa: E402
from plb.dates import parse_as_of  # noqa: E402
from plb.schema import EVENT_COLUMNS, LEAD_COLUMNS, REJECT_COLUMNS, agency_profile, load_market_params  # noqa: E402
from plb.units import fill_units_block  # noqa: E402
from query_calendar import summarize  # noqa: E402

PY = sys.executable


def run_cmd(args: List[str], log: List[str]) -> int:
    log.append("$ " + " ".join(args))
    p = subprocess.run(args, capture_output=True, text=True)
    log.append(p.stdout.strip())
    print(p.stdout.strip())
    if p.returncode != 0:
        log.append("STDERR: " + p.stderr.strip())
        print(p.stderr.strip(), file=sys.stderr)
    elif p.stderr.strip():
        print(p.stderr.strip(), file=sys.stderr)
    return p.returncode


def _read(path: str) -> Optional[pd.DataFrame]:
    return pd.read_csv(path, dtype=str, keep_default_na=False) if os.path.exists(path) else None


def build(a) -> Dict[str, Any]:
    as_of = parse_as_of(a.as_of)
    out = a.out_dir
    os.makedirs(out, exist_ok=True)
    log: List[str] = []
    pack_args = ["--pack", a.pack] if a.pack else []
    prof = agency_profile(a.agency_profile, a.pack)
    params = load_market_params(a.pack)
    hz = str(a.horizon_years)
    counties = a.counties
    adapter_dirs: Dict[str, str] = {}
    book_dir = None
    if a.book:
        book_dir = os.path.join(out, "adapter_agency_servicing")
        cmd = [PY, os.path.join(HERE, "ingest_servicing_extract.py"), "--input", a.book, "--agency-profile", a.agency_profile, "--out-dir", book_dir, "--as-of", as_of.isoformat(),
               "--horizon-years", hz, *pack_args]
        if a.zip_crosswalk:
            cmd += ["--zip-crosswalk", a.zip_crosswalk]
        if a.internal:
            cmd += ["--internal"]
        if run_cmd(cmd, log) != 0:
            raise SystemExit(2)
        adapter_dirs["agency_servicing_extract"] = book_dir
    ohcs_dir = os.path.join(out, "adapter_ohcs_affordable_housing_inventory")
    cmd = [PY, os.path.join(HERE, "ohcs_inventory_targets.py"), "--input", a.ohcs, "--mode", a.mode, "--out-dir", ohcs_dir, "--as-of", as_of.isoformat(), "--horizon-years", hz,
           "--regulatory-horizon-years", str(a.regulatory_horizon_years or a.horizon_years), *pack_args]
    if counties:
        cmd += ["--counties", counties]
    if a.city:
        cmd += ["--city", a.city]
    if a.include_proxies:
        cmd += ["--include-proxies", "true"]
    if run_cmd(cmd, log) != 0:
        raise SystemExit(2)
    adapter_dirs["ohcs_affordable_housing_inventory"] = ohcs_dir
    county_list = counties or ",".join(json.load(open(os.path.join(ohcs_dir, "calendar_summary.json")))["counties"])
    if a.hud_sec8:
        d = os.path.join(out, "adapter_hud_mf_assistance_sec8")
        cmd = [PY, os.path.join(HERE, "normalize_hud_sec8.py"), "--input", a.hud_sec8, "--out-dir", d, "--as-of", as_of.isoformat(), "--horizon-years", hz, "--counties", county_list, *pack_args]
        if a.hud_sec8_properties:
            cmd += ["--properties", a.hud_sec8_properties]
        if a.zip_crosswalk:
            cmd += ["--zip-crosswalk", a.zip_crosswalk]
        if run_cmd(cmd, log) == 0:
            adapter_dirs["hud_mf_assistance_sec8"] = d
    if a.hud_fhasl:
        d = os.path.join(out, "adapter_hud_fhasl_active")
        cmd = [PY, os.path.join(HERE, "normalize_hud_insured.py"), "--input", a.hud_fhasl, "--out-dir", d, "--as-of", as_of.isoformat(), "--horizon-years", hz, "--counties", county_list, *pack_args]
        if a.hud_fhasl_terminated:
            cmd += ["--terminated", a.hud_fhasl_terminated]
        if a.zip_crosswalk:
            cmd += ["--zip-crosswalk", a.zip_crosswalk]
        if run_cmd(cmd, log) == 0:
            adapter_dirs["hud_fhasl_active"] = d
    if a.forecast:
        d = os.path.join(out, "adapter_ohcs_push_forecast")
        cmd = [PY, os.path.join(HERE, "normalize_ohcs_forecast.py"), "--input", a.forecast, "--out-dir", d, "--as-of", as_of.isoformat(), "--horizon-years", hz, "--counties", county_list,
               "--ohcs-leads", os.path.join(ohcs_dir, "leads.csv"), *pack_args]
        if a.prior_forecast:
            cmd += ["--prior", a.prior_forecast]
        if run_cmd(cmd, log) == 0:
            adapter_dirs["ohcs_push_forecast"] = d
    if a.reac:
        d = os.path.join(out, "adapter_hud_reac_scores")
        cmd = [PY, os.path.join(HERE, "normalize_reac_scores.py"), "--input", a.reac, "--out-dir", d, "--as-of", as_of.isoformat(), "--horizon-years", hz, "--counties", county_list, *pack_args]
        if a.zip_crosswalk:
            cmd += ["--zip-crosswalk", a.zip_crosswalk]
        if run_cmd(cmd, log) == 0:
            adapter_dirs["hud_reac_scores"] = d
    if a.noah_watch and a.noah:
        d = os.path.join(out, "adapter_noah_candidates")
        if run_cmd([PY, os.path.join(HERE, "noah_watch.py"), "--input", a.noah, "--out-dir", d, "--as-of", as_of.isoformat(), "--horizon-years", hz, *pack_args], log) == 0:
            adapter_dirs["noah_candidates"] = d

    # ---- merge with book join
    order = [k for k in adapter_dirs if k != "agency_servicing_extract"] + (["agency_servicing_extract"] if book_dir else [])
    lf = [_read(os.path.join(adapter_dirs[k], "leads.csv")) for k in order]
    ef = [_read(os.path.join(adapter_dirs[k], "events.csv")) for k in order]
    lf = [f if f is not None else pd.DataFrame(columns=LEAD_COLUMNS) for f in lf]
    ef = [f if f is not None else pd.DataFrame(columns=EVENT_COLUMNS) for f in ef]
    book_index = order.index("agency_servicing_extract") if book_dir else None
    id_map, grades, jlog = {}, {}, []
    if book_index is not None:
        inv = pd.concat([f for i, f in enumerate(lf) if i != book_index], ignore_index=True)
        xw = load_crosswalk(a.crosswalk or (os.path.join(a.pack, "book_crosswalk.csv") if a.pack else None))
        decisions, jlog = join_book(lf[book_index], inv, xw)
        id_map = {k: v["inventory_pid"] for k, v in decisions.items() if v["inventory_pid"]}
        grades = {k: v["grade"] for k, v in decisions.items()}
    leads, events, mlog, unmatched, conflicts = merge(lf, ef, as_of, a.horizon_years, a.regulatory_horizon_years or a.horizon_years, book_index, id_map, grades, prof, a.book_coverage)
    if jlog:
        mlog = pd.concat([pd.DataFrame(jlog), mlog], ignore_index=True)
    # ---- units block, then agency calendar
    leads = fill_units_block(leads, as_of)
    leads, events = AC.derive(leads, events, as_of, params, prof, int(a.horizon_years * 12))
    leads = fill_units_block(leads, as_of)  # public_upb_at_risk / board_impact need owner_cliff_band
    # ---- book join gaps
    gaps = leads[leads["book_match"] == "unmatched_expected"][["property_id", "property_name", "book_match", "ohcs_funded", "programs"]].copy() if len(leads) else pd.DataFrame()
    if len(gaps):
        gaps["expected_book_flag"] = prof.get("expected_book_flag")
        gaps["note"] = "expected in book under book_coverage full; servicing extract did not match (Verify — Book Join; capital factor 0, queue not capped)"
        leads.loc[leads["book_match"] == "unmatched_expected", "verify_flags"] = leads.loc[leads["book_match"] == "unmatched_expected", "verify_flags"].map(
            lambda v: ";".join(dict.fromkeys([x for x in str(v).split(";") if x] + ["Verify — Book Join"])))
    # ---- rejects
    rej = [_read(os.path.join(d, "rejects.csv")) for d in adapter_dirs.values()]
    rej = [r for r in rej if r is not None and len(r)]
    rejects = pd.concat(rej + ([conflicts] if len(conflicts) else []), ignore_index=True) if (rej or len(conflicts)) else pd.DataFrame(columns=REJECT_COLUMNS)
    # ---- calendar summary
    sel, cal = summarize(events, as_of, a.horizon_years, a.regulatory_horizon_years or a.horizon_years)
    cal.pop("_helper_rows", None)
    cal.pop("_agency_rows", None)
    ohcs_cal = json.load(open(os.path.join(ohcs_dir, "calendar_summary.json")))
    cal.update({"agency_profile": a.agency_profile, "agency_name": prof.get("agency_name"), "geography_mode": a.mode, "counties": county_list.split(","),
                "horizon_years": a.horizon_years, "regulatory_horizon_years": a.regulatory_horizon_years or a.horizon_years,
                "rows_in_geography": ohcs_cal.get("rows_in_geography"), "rows_excluded_in_development": ohcs_cal.get("rows_excluded_in_development"),
                "pipeline_not_scored": ohcs_cal.get("pipeline_not_scored", []), "book_present": bool(book_dir), "book_coverage": a.book_coverage,
                "book_rows": int(len(lf[book_index])) if book_index is not None else 0, "book_rows_matched": int(len([k for k, v in grades.items() if v != "unmatched"])),
                "book_rows_unmatched": int(len(unmatched)), "book_join_grades": pd.Series(list(grades.values())).value_counts().to_dict() if grades else {},
                "book_match_counts": leads["book_match"].value_counts().to_dict() if len(leads) else {},
                "stale_contract_dates": int(leads.attrs.get("stale_contract_dates", 0)), "notice_compliance_breaches": int(leads.attrs.get("notice_compliance_breaches", 0)),
                "push_window_open_count": int(leads["signals"].astype(str).str.contains("push_window_open_prep").sum()) if len(leads) else 0,
                "notice_log_unknown_share": round(float((leads["notice_status"].astype(str).isin(["", "unknown"])).mean()), 3) if len(leads) else 0.0,
                "include_proxies": bool(a.include_proxies), "noah_watch": bool(a.noah_watch),
                "degraded_note": ("book absent: capital factor 0 for all rows; outputs are preservation targeting and notice compliance only. " if not book_dir else "")
                                 + ("forecast / CA notice statuses absent: notice_status unknown for inventory rows (silence is not inferred). " if not a.forecast else ""),
                "adapters": list(adapter_dirs), "log": log})
    cal["header"] = header_line(cal)
    leads.to_csv(os.path.join(out, "leads.csv"), index=False)
    events.to_csv(os.path.join(out, "events.csv"), index=False)
    rejects.to_csv(os.path.join(out, "rejects.csv"), index=False)
    mlog.to_csv(os.path.join(out, "merge_log.csv"), index=False)
    if not len(unmatched.columns):
        unmatched = pd.DataFrame(columns=["property_id", "property_name", "address", "zip", "book_kind", "agency_loan_ids", "grant_ids", "note"])
    if not len(gaps.columns):
        gaps = pd.DataFrame(columns=["property_id", "property_name", "book_match", "ohcs_funded", "programs"])
    unmatched.to_csv(os.path.join(out, "servicing_unmatched.csv"), index=False)   # header-only when empty (never a 0-byte file)
    gaps.to_csv(os.path.join(out, "book_join_gaps.csv"), index=False)
    pd.DataFrame(cal.get("pipeline_not_scored") or []).to_csv(os.path.join(out, "pipeline_not_scored.csv"), index=False)
    json.dump(cal, open(os.path.join(out, "calendar_summary.json"), "w"), indent=2, default=str)
    print(f"[universe] leads {len(leads)} ({leads['universe'].value_counts().to_dict() if len(leads) else {}}) events {len(events)} book_match {cal['book_match_counts']} "
          f"join grades {cal['book_join_grades']} unmatched book rows {len(unmatched)} stale HUD dates {cal['stale_contract_dates']} breaches {cal['notice_compliance_breaches']}")
    print(f"[universe] header: {cal['header']}")
    return cal


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack", default=None)
    ap.add_argument("--mode", default="metro_core", choices=["city_limits", "county", "metro_core", "cbsa"])
    ap.add_argument("--counties", default=None)
    ap.add_argument("--city", default=None)
    ap.add_argument("--agency-profile", default="hfa", choices=["hfa", "city_housing", "county", "pha_am", "cdbg_home"])
    ap.add_argument("--ohcs", required=True)
    ap.add_argument("--book", default=None, help="agency servicing extract (optional; without it the run is universe-only)")
    ap.add_argument("--book-coverage", default="partial", choices=["full", "partial"])
    ap.add_argument("--crosswalk", default=None, help="book_crosswalk.csv (default: <pack>/book_crosswalk.csv)")
    ap.add_argument("--hud-sec8", default=None)
    ap.add_argument("--hud-sec8-properties", default=None)
    ap.add_argument("--hud-fhasl", default=None)
    ap.add_argument("--hud-fhasl-terminated", default=None)
    ap.add_argument("--forecast", default=None)
    ap.add_argument("--prior-forecast", default=None)
    ap.add_argument("--reac", default=None)
    ap.add_argument("--zip-crosswalk", default=None)
    ap.add_argument("--include-proxies", action="store_true")
    ap.add_argument("--noah-watch", action="store_true")
    ap.add_argument("--noah", default=None, help="noah_candidates.csv (only with --noah-watch)")
    ap.add_argument("--horizon-years", type=float, default=10)
    ap.add_argument("--regulatory-horizon-years", type=float, default=None)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--internal", action="store_true")
    build(ap.parse_args(argv))


if __name__ == "__main__":
    main()
