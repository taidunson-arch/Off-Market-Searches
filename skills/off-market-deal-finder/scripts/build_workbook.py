#!/usr/bin/env python3
"""Render the 11-tab target-list workbook from scored leads + events (references/output-contract.md).

Tabs: Summary, Targets, Events, Capital_Stack, Regulatory, Owners_DecisionMakers, Signals, Sources_Vintages,
Assumptions, Rejects_Verify, Diff_vs_Prior. Every cell is a literal (no formulas), so LibreOffice recalculation is
unnecessary and skipped by default; pass `--recalc` to run `/mnt/skills/public/xlsx/scripts/recalc.py <xlsx>` when
that script is available (its absence is not an error). An earlier default-on recalc timed out on a literal-only file.

Usage:
  python scripts/build_workbook.py --leads runs/x/leads_scored.csv --events runs/x/events.csv \
      --calendar runs/x/calendar_summary.json --rejects runs/x/rejects.csv \
      [--assumptions references/sources/oregon-portland/market-params.json] [--sources runs/x/sources_used.json] \
      [--prior runs/prior/leads_scored.csv] --out runs/x/targets.xlsx [--geography-mode metro_core] [--as-of YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from omdf.dates import parse_as_of  # noqa: E402
from omdf.schema import load_market_params  # noqa: E402
from omdf.workbook import build_workbook  # noqa: E402

RECALC = "/mnt/skills/public/xlsx/scripts/recalc.py"


def diff_frames(cur: pd.DataFrame, prior: pd.DataFrame) -> pd.DataFrame:
    """new / escalated / de-escalated / retired rows between two scored lead tables."""
    order = {"A": 3, "B": 2, "C": 1, "WATCH": 0, "EXCLUDED": -1}
    rows = []
    p = prior.set_index("property_id") if len(prior) else pd.DataFrame()
    c = cur.set_index("property_id")
    for pid, r in c.iterrows():
        if pid not in p.index:
            rows.append({"property_id": pid, "property_name": r.get("property_name"), "change": "new", "tier_prior": "", "tier_now": r.get("tier"),
                         "detail": f"first_debt {r.get('first_debt_event_type')} {r.get('first_debt_event_date')}; first_reg {r.get('first_reg_event_type')} {r.get('first_reg_event_date')}"})
        else:
            t0, t1 = p.loc[pid].get("tier"), r.get("tier")
            if order.get(t1, 0) > order.get(t0, 0):
                rows.append({"property_id": pid, "property_name": r.get("property_name"), "change": "escalated", "tier_prior": t0, "tier_now": t1, "detail": f"score {p.loc[pid].get('motivation_score')} -> {r.get('motivation_score')}"})
            elif order.get(t1, 0) < order.get(t0, 0):
                rows.append({"property_id": pid, "property_name": r.get("property_name"), "change": "de-escalated", "tier_prior": t0, "tier_now": t1, "detail": f"score {p.loc[pid].get('motivation_score')} -> {r.get('motivation_score')}"})
    for pid, r in (p.iterrows() if len(p) else []):
        if pid not in c.index:
            rows.append({"property_id": pid, "property_name": r.get("property_name"), "change": "retired", "tier_prior": r.get("tier"), "tier_now": "",
                         "detail": "no longer in list (refinanced, cured, sold, out of horizon or suppressed) - check events for the retiring event"})
    return pd.DataFrame(rows, columns=["property_id", "property_name", "change", "tier_prior", "tier_now", "detail"])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--leads", required=True)
    ap.add_argument("--events", required=True)
    ap.add_argument("--calendar", default=None)
    ap.add_argument("--rejects", default=None)
    ap.add_argument("--assumptions", default=None, help="market-params.json (default embedded Oregon params)")
    ap.add_argument("--pack", default=None)
    ap.add_argument("--sources", default=None, help="sources_used.json (list of {source_id,file,sha256,vintage,verified_live,access,url})")
    ap.add_argument("--prior", default=None, help="prior run's leads_scored.csv for Diff_vs_Prior")
    ap.add_argument("--out", required=True)
    ap.add_argument("--geography-mode", default=None)
    ap.add_argument("--query-type", default="all")
    ap.add_argument("--buyer-profile", default="principal")
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--recalc", action="store_true", help="run the xlsx skill's recalc.py afterwards (off by default: the workbook has no formulas)")
    ap.add_argument("--no-recalc", action="store_true", help="kept for backward compatibility; recalc is already off by default")
    a = ap.parse_args(argv)
    as_of = parse_as_of(a.as_of)
    leads = pd.read_csv(a.leads, dtype=str, keep_default_na=False)
    events = pd.read_csv(a.events, dtype=str, keep_default_na=False)
    calendar = json.load(open(a.calendar)) if a.calendar and os.path.exists(a.calendar) else {}
    rejects = pd.read_csv(a.rejects, dtype=str, keep_default_na=False) if a.rejects and os.path.exists(a.rejects) else None
    params = load_market_params(a.pack, a.assumptions)
    sources = json.load(open(a.sources)) if a.sources and os.path.exists(a.sources) else []
    diff = diff_frames(leads, pd.read_csv(a.prior, dtype=str, keep_default_na=False)) if a.prior and os.path.exists(a.prior) else None
    meta = {"as_of_date": as_of.isoformat(), "geography_mode": a.geography_mode or calendar.get("geography_mode", ""),
            "counties": calendar.get("counties", []), "asset_class": ";".join(sorted(set(leads.get("asset_class", pd.Series(dtype=str)).dropna()))) if len(leads) else "",
            "horizon_years": calendar.get("horizon_years", ""), "regulatory_horizon_years": calendar.get("regulatory_horizon_years", ""),
            "degraded_note": calendar.get("degraded_note", ""), "scoring_source": "references/scoring/*.json",
            "query_type": a.query_type, "buyer_profile": a.buyer_profile}
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    build_workbook(a.out, leads, events, calendar, rejects, params, sources, diff, meta)
    print(f"[workbook] wrote {a.out} ({len(leads)} leads, {len(events)} events" + (f", diff rows {len(diff)}" if diff is not None else "") + ")")
    if a.recalc and not a.no_recalc:
        if os.path.exists(RECALC):
            try:
                subprocess.run([sys.executable, RECALC, a.out], check=False, timeout=120)
            except Exception as exc:  # pragma: no cover
                print(f"[workbook] recalc skipped: {exc}")
        else:
            print("[workbook] recalc requested but /mnt/skills/public/xlsx/scripts/recalc.py is not present; workbook holds literals only")


if __name__ == "__main__":
    main()
