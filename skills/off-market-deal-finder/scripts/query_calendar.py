#!/usr/bin/env python3
"""Answer "what is coming due within N years" from an events.csv, with the basis breakdown first.

Prints the header the SKILL.md requires the brief to quote verbatim:
  RECORDED n / REPORTED n / DERIVED n / ESTIMATED n / PROXY n / Suppressed n / Rejected n | helper deadlines n
then the same breakdown by event family, then the event rows sorted by date.

The five basis counts exclude helper deadlines (PRESERVATION_NOTICE_WINDOW, HAP_OPTOUT_NOTICE_DEADLINE: arithmetic
on another event of the same property) and REGULATORY_LATEST_END rows whose date equals a component program end
on the same property. Those are counted on the `helper deadlines` line so DERIVED means Year-15 dates, not notice
arithmetic, and the header does not overstate how much is coming due (omdf/calendar.py).

`--within-years` applies to DEBT-family events; `--regulatory-within-years` (default = within) to
REGULATORY-family events; HARD_DISTRESS / TAX_LIEN / PHYSICAL / OWNERSHIP / OPERATING events are
always listed when dated inside the longer of the two horizons or undated-but-present.

Usage:
  python scripts/query_calendar.py --events runs/x/events.csv --within-years 5 [--regulatory-within-years 5]
      [--event-types LOAN_MATURITY,HAP_EXPIRATION] [--class affordable_regulated --leads runs/x/leads.csv]
      [--as-of YYYY-MM-DD] [--json runs/x/calendar_summary.json] [--limit 50] [--show-helpers]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from omdf.calendar import BASES, basis_counts, header_line, split_helper_rows  # noqa: E402
from omdf.dates import months_between, parse_as_of, urgency_band  # noqa: E402
from omdf.schema import family_of  # noqa: E402


def summarize(events: pd.DataFrame, as_of, within_years: float, reg_within_years: float, event_types=None):
    ev = events.copy()
    empty = {"by_basis": {b: 0 for b in BASES}, "suppressed": 0, "rejected": 0, "by_family": {}, "helper_events": 0, "helper_by_type": {},
             "events": 0, "properties": 0, "by_event_type": {}, "by_urgency": {}}
    if len(ev) == 0:
        empty["header"] = header_line(empty)
        return ev, empty
    ev["event_family"] = ev.apply(lambda r: r.get("event_family") or family_of(r["event_type"]), axis=1)
    d = pd.to_datetime(ev["event_date"], errors="coerce")
    ev["months_out"] = [months_between(as_of, x.date()) if pd.notna(x) else None for x in d]
    ev["urgency_band"] = ev["months_out"].map(urgency_band)
    status = ev.get("status", pd.Series([""] * len(ev))).fillna("").str.upper()
    rejected = int((status == "REJECTED").sum())
    suppressed = int((status == "SUPPRESSED").sum())
    live = ev[~status.isin(["REJECTED", "SUPPRESSED"])].copy()
    debt_h, reg_h = within_years * 12, reg_within_years * 12

    def keep(r):
        mo = r["months_out"]
        fam = r["event_family"]
        if mo is None:
            return fam not in ("DEBT", "REGULATORY")
        if fam == "DEBT":
            return 0 <= mo <= debt_h
        if fam == "REGULATORY":
            return 0 <= mo <= reg_h
        return mo <= max(debt_h, reg_h)

    sel_all = live[live.apply(keep, axis=1)].copy()
    if "direction" in sel_all.columns:  # only PRESSURE events are "coming due"; SUPPRESSION / ROUTING rows are reported through suppressed / routes
        sel_all = sel_all[sel_all["direction"].fillna("PRESSURE").replace("", "PRESSURE") == "PRESSURE"]
    if event_types:
        sel_all = sel_all[sel_all["event_type"].isin(event_types)]
    sel, helper = split_helper_rows(sel_all)
    sel = sel.sort_values(["event_date", "property_id"])
    by_family = {}
    for fam, grp in sel.groupby("event_family"):
        by_family[fam] = basis_counts(grp)
    summary = {"as_of_date": as_of.isoformat(), "within_years": within_years, "regulatory_within_years": reg_within_years,
               "events": int(len(sel)), "events_all": int(len(sel_all)), "by_basis": basis_counts(sel), "by_family": by_family,
               "suppressed": suppressed, "rejected": rejected,
               "helper_events": int(len(helper)), "helper_by_type": {k: int(v) for k, v in helper.groupby("event_type").size().items()} if len(helper) else {},
               "by_event_type": {k: int(v) for k, v in sel.groupby("event_type").size().items()},
               "by_urgency": {k: int(v) for k, v in sel.groupby("urgency_band").size().items()},
               "properties": int(sel["property_id"].nunique())}
    summary["header"] = header_line(summary)
    summary["_helper_rows"] = helper
    return sel, summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--events", required=True)
    ap.add_argument("--within-years", type=float, default=5)
    ap.add_argument("--regulatory-within-years", type=float, default=None)
    ap.add_argument("--event-types", default=None, help="comma list filter")
    ap.add_argument("--class", dest="asset_class", default=None, help="filter by asset_class (needs --leads)")
    ap.add_argument("--leads", default=None)
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--json", default=None, help="write calendar_summary.json here")
    ap.add_argument("--limit", type=int, default=60, help="rows to print (0 = all)")
    ap.add_argument("--show-helpers", action="store_true", help="also print the helper-deadline rows")
    a = ap.parse_args(argv)

    as_of = parse_as_of(a.as_of)
    ev = pd.read_csv(a.events, dtype=str, keep_default_na=False)
    if a.asset_class and a.leads:
        leads = pd.read_csv(a.leads, dtype=str, keep_default_na=False)
        pids = set(leads.loc[leads["asset_class"] == a.asset_class, "property_id"])
        ev = ev[ev["property_id"].isin(pids)]
    types = [t.strip() for t in a.event_types.split(",")] if a.event_types else None
    sel, summary = summarize(ev, as_of, a.within_years, a.regulatory_within_years or a.within_years, types)
    helper = summary.pop("_helper_rows", pd.DataFrame())
    print(f"Dated events within {a.within_years:g}y (debt) / {a.regulatory_within_years or a.within_years:g}y (regulatory) as of {as_of}: "
          f"{summary['events']} events on {summary['properties']} properties (+{summary['helper_events']} helper deadlines not counted)")
    print("BASIS: " + summary["header"])
    for fam, b in summary["by_family"].items():
        print(f"  {fam:<14}" + " / ".join(f"{k} {b[k]}" for k in BASES))
    if summary["helper_by_type"]:
        print("HELPER DEADLINES:", summary["helper_by_type"])
    print("URGENCY:", summary["by_urgency"])
    cols = [c for c in ["event_date", "months_out", "urgency_band", "event_type", "basis", "confidence", "program", "property_id", "source", "verify_flag"] if c in sel.columns]
    rows = sel[cols] if a.limit == 0 else sel[cols].head(a.limit)
    if len(rows):
        print(rows.to_string(index=False))
        if a.limit and len(sel) > a.limit:
            print(f"... {len(sel) - a.limit} more rows (use --limit 0)")
    if a.show_helpers and len(helper):
        print("helper deadlines:")
        print(helper[[c for c in cols if c in helper.columns]].head(a.limit or len(helper)).to_string(index=False))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=2)
        print(f"wrote {a.json}")


if __name__ == "__main__":
    main()
