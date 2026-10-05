#!/usr/bin/env python3
"""Score and tier a canonical lead table using references/scoring/*.json.

Reads leads.csv + events.csv (from the adapters or merge_leads.py), evaluates the per-class factor tables and
shared adjustments (basis multipliers, urgency bands, deal-size multiplier, suppressions, caps, routes) and writes
a scored CSV with `motivation_score`, `tier`, `route`, `outreach_template`, `compliance_gates`,
`verify_before_outreach`, `next_action`, `query_hit` and a `factors_json` column holding evidence / reading /
lever per factor. `--xlsx` also renders the workbook.

The JSON files are the only rubric: a missing scoring directory is an error, never a silent fallback.

Run-config inputs honoured here (they used to be documented but ignored):
  --owner-types-include / --owner-types-exclude   non-matching owner_type -> route excluded (reason recorded)
  --lender-types                                   non-matching lender_type -> route excluded
  --buyer-profile                                  wholesaler adds the HB 4058 gate on class 1; nonprofit_preservation /
                                                   qualified_purchaser add the designee_strategy signal on class 3
  --query-type                                     maturity | regulatory_expiry | distress | all; sets `query_hit` and ranks
                                                   hits first so a maturity run shows regulatory-only leads as secondary
  --price-band                                     lo,hi dollars; same multiplier as --unit-range when est_value is present

Usage:
  python scripts/score_leads.py --leads runs/x/leads.csv --events runs/x/events.csv \
      [--scoring-dir references/scoring] [--class auto|sfr_small_res|market_rate_mf|affordable_regulated] \
      [--unit-range 20,120] [--strict-size-fit] [--programs LIHTC_9,HAP] [--horizon-years 5] [--query-type maturity] \
      [--owner-types-exclude housing_authority,government] [--buyer-profile principal] \
      --out runs/x/leads_scored.csv [--xlsx runs/x/targets.xlsx] [--explain <property_id>] [--as-of YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from omdf.dates import parse_as_of  # noqa: E402
from omdf.scoring import explain, load_scoring, score_lead  # noqa: E402

TIER_ORDER = {"A": 0, "B": 1, "C": 2, "WATCH": 3, "EXCLUDED": 4}


def _parse_range(s):
    if not s:
        return None
    parts = [p.strip() for p in str(s).split(",")]
    lo = float(parts[0]) if parts[0] not in ("", "None") else None
    hi = float(parts[1]) if len(parts) > 1 and parts[1] not in ("", "None") else None
    return [lo, hi]


def _list(s) -> Optional[List[str]]:
    if s is None:
        return None
    if isinstance(s, list):
        return [str(x) for x in s if str(x).strip()] or None
    items = [p.strip() for p in str(s).split(",") if p.strip()]
    return items or None


def score_frame(leads: pd.DataFrame, events: pd.DataFrame, as_of, scoring_dir=None, asset_class="auto", unit_range=None,
                strict=False, programs=None, horizon_years=5.0, price_band=None, owner_types_include=None,
                owner_types_exclude=None, lender_types=None, buyer_profile="principal", query_type="all"):
    tables, shared, src = load_scoring(scoring_dir)
    ev_by_pid: Dict[str, List[Dict[str, Any]]] = {}
    if events is not None and len(events):
        for rec in events.to_dict(orient="records"):
            ev_by_pid.setdefault(str(rec.get("property_id")), []).append(rec)
    results, rows = [], []
    for lead in leads.to_dict(orient="records"):
        cls = asset_class if asset_class != "auto" else str(lead.get("asset_class") or "market_rate_mf")
        if cls not in tables:
            cls = "market_rate_mf"
        res = score_lead(lead, ev_by_pid.get(str(lead.get("property_id")), []), cls, tables, shared, as_of,
                         unit_range=unit_range, price_band=price_band, strict_size_fit=strict, programs_filter=programs,
                         horizon_months=int(horizon_years * 12), owner_types_include=owner_types_include,
                         owner_types_exclude=owner_types_exclude, lender_types=lender_types, buyer_profile=buyer_profile,
                         query_type=query_type)
        results.append(res)
        out = dict(lead)
        for k in ("score_raw", "motivation_score", "tier", "route", "outreach_template", "outreach_angle", "signals",
                  "compliance_gates", "verify_before_outreach", "next_action", "query_hit"):
            out[k] = res[k]
        out["factors_json"] = json.dumps({"factors": res["factors"], "penalties": res["penalties"], "multipliers": res["multipliers"],
                                          "route_reasons": res["route_reasons"], "tier_caps": res["tier_caps"],
                                          "suppression": res["suppression"], "query_type": query_type, "buyer_profile": buyer_profile}, default=str)
        rows.append(out)
    scored = pd.DataFrame(rows)
    if len(scored):
        scored["_t"] = scored["tier"].map(lambda t: TIER_ORDER.get(t, 9))
        scored["_q"] = scored["query_hit"].map(lambda h: 0 if bool(h) else 1)
        scored = scored.sort_values(["_q", "_t", "motivation_score"], ascending=[True, True, False]).drop(columns=["_t", "_q"]).reset_index(drop=True)
    return scored, results, src


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--leads", required=True)
    ap.add_argument("--events", required=True)
    ap.add_argument("--scoring-dir", default=None, help="default: <skill>/references/scoring (required to exist)")
    ap.add_argument("--class", dest="asset_class", default="auto", choices=["auto", "sfr_small_res", "market_rate_mf", "affordable_regulated"])
    ap.add_argument("--unit-range", default=None, help="lo,hi (e.g. 20,120); default per class")
    ap.add_argument("--price-band", default=None, help="lo,hi in dollars; applied when est_value present")
    ap.add_argument("--strict-size-fit", action="store_true")
    ap.add_argument("--programs", default=None, help="comma list; affordable mission-fit multiplier when no overlap")
    ap.add_argument("--owner-types-include", default=None, help="comma list of owner_type values to keep")
    ap.add_argument("--owner-types-exclude", default=None, help="comma list of owner_type values to exclude")
    ap.add_argument("--lender-types", default=None, help="comma list of lender_type values to keep (leads with a known lender_type only)")
    ap.add_argument("--buyer-profile", default="principal", choices=["principal", "wholesaler", "nonprofit_preservation", "qualified_purchaser"])
    ap.add_argument("--query-type", default="all", choices=["all", "maturity", "regulatory_expiry", "distress"])
    ap.add_argument("--horizon-years", type=float, default=5)
    ap.add_argument("--out", required=True)
    ap.add_argument("--xlsx", default=None, help="also write the workbook to this path")
    ap.add_argument("--explain", default=None, help="property_id to explain (prints arithmetic)")
    ap.add_argument("--as-of", default=None)
    a = ap.parse_args(argv)

    as_of = parse_as_of(a.as_of)
    leads = pd.read_csv(a.leads, dtype=str, keep_default_na=False)
    events = pd.read_csv(a.events, dtype=str, keep_default_na=False)
    scored, results, src = score_frame(leads, events, as_of, a.scoring_dir, a.asset_class, _parse_range(a.unit_range),
                                       a.strict_size_fit, _list(a.programs), a.horizon_years, _parse_range(a.price_band),
                                       _list(a.owner_types_include), _list(a.owner_types_exclude), _list(a.lender_types),
                                       a.buyer_profile, a.query_type)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    scored.to_csv(a.out, index=False)
    print(f"[score] scoring tables: {src}; as_of {as_of}; leads {len(scored)}; query_type {a.query_type}; buyer_profile {a.buyer_profile}")
    if len(scored):
        print("[score] tiers:", scored["tier"].value_counts().to_dict(), "routes:", scored["route"].value_counts().to_dict())
        hits = int(scored["query_hit"].astype(bool).sum())
        if a.query_type != "all":
            print(f"[score] {a.query_type} hits: {hits} leads carry a dated {a.query_type} event; {len(scored) - hits} shown as secondary (other event families only)")
    if a.explain:
        idx = {str(l.get("property_id")): i for i, l in enumerate(leads.to_dict(orient="records"))}
        if a.explain in idx:
            print(explain(results[idx[a.explain]], leads.to_dict(orient="records")[idx[a.explain]]))
        else:
            print(f"[score] property_id {a.explain} not found")
    if a.xlsx:
        from omdf.workbook import build_workbook
        cal_path = os.path.join(os.path.dirname(os.path.abspath(a.events)), "calendar_summary.json")
        calendar = json.load(open(cal_path)) if os.path.exists(cal_path) else {}
        rej_path = os.path.join(os.path.dirname(os.path.abspath(a.events)), "rejects.csv")
        rejects = pd.read_csv(rej_path, dtype=str, keep_default_na=False) if os.path.exists(rej_path) else None
        build_workbook(a.xlsx, scored, events, calendar, rejects, run_meta={"as_of_date": as_of.isoformat(), "scoring_source": src,
                                                                           "geography_mode": calendar.get("geography_mode", ""),
                                                                           "counties": calendar.get("counties", []),
                                                                           "horizon_years": calendar.get("horizon_years", a.horizon_years),
                                                                           "regulatory_horizon_years": calendar.get("regulatory_horizon_years", ""),
                                                                           "asset_class": a.asset_class, "degraded_note": calendar.get("degraded_note", ""),
                                                                           "query_type": a.query_type, "buyer_profile": a.buyer_profile})
        print(f"[score] wrote {a.xlsx}")
    print(f"[score] wrote {a.out}")


if __name__ == "__main__":
    main()
