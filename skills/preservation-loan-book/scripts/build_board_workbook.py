#!/usr/bin/env python3
"""Render the working-file workbook (17 tabs) and, with --board-packet, the stripped board packet (public_packet scope) + board_packet.md.

Every cell is a literal; recalc is unnecessary and off by default (`--recalc` runs /mnt/skills/public/xlsx/scripts/recalc.py when present).
Board_Totals is read from units_at_risk.json beside --leads-scored so the brief, the workbook and the JSON agree.

Usage:
  python scripts/build_board_workbook.py --leads-scored runs/x/leads_scored.csv --events runs/x/events.csv --calendar runs/x/calendar_summary.json
      --rejects runs/x/rejects.csv [--assumptions market-params.json] --pack <dir> [--sources runs/x/sources_used.json] [--prior runs/prior/leads_scored.csv]
      --agency-profile hfa --out runs/x/Portland_TriCounty_Preservation_LoanBook_10yr.xlsx [--board-packet] [--internal] [--recalc] [--as-of YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diff_forecast import kpi_summary, status_flips  # noqa: E402
from plb.dates import parse_as_of  # noqa: E402
from plb.schema import agency_profile, load_market_params  # noqa: E402
from plb.units import units_at_risk_json  # noqa: E402
from plb.workbook import board_totals_rows, build_board_packet, build_workbook, sponsor_exposure  # noqa: E402

RECALC = "/mnt/skills/public/xlsx/scripts/recalc.py"


def _read(path):
    return pd.read_csv(path, dtype=str, keep_default_na=False) if path and os.path.exists(path) else None


def write_board_packet_md(path: str, uar: dict, leads: pd.DataFrame, flips, redaction_log, prof: dict, as_of) -> str:
    from plb.pii import RECORDS_CLASSIFICATION, apply_pii_scope
    packet, _ = apply_pii_scope(leads, "public_packet")
    h = uar.get("headline", {})
    L = [f"# Preservation and Loan-Book Review — Board Packet: {prof.get('agency_name', '')} — as of {as_of.isoformat()}", "",
         "## Book Verdict and Headline", "",
         f"- Book verdict: **{uar.get('book_verdict', '')}** ({uar.get('book_verdict_rule', '')})",
         f"- {h.get('properties', 0)} properties / {h.get('units_at_risk', 0)} restricted units / {h.get('hap_units_at_risk', 0)} HAP units / {h.get('prac_units_at_risk', 0)} PRAC units / "
         f"{h.get('psh_units_at_risk', 0)} PSH units / ${h.get('public_upb_at_risk', 0):,.0f} public UPB with an owner cliff inside 36 months (bands are months, not days)", "",
         "## Units at Risk by Band and Jurisdiction", ""]
    cols = uar.get("columns", [])
    L.append("| jurisdiction | band | " + " | ".join(cols) + " |")
    L.append("|---|---|" + "---|" * len(cols))
    for r in board_totals_rows(uar)[1:]:
        if len(r) < 3 or r[1] in ("", None):
            if r and r[0] and r[0] != "Units_by_Year (owner cliff year)":
                jur = r[0]
            continue
        if r[0] == "" and isinstance(r[1], str) and r[1].isdigit():
            break
        L.append(f"| {r[0] or jur if r[0] or 'jur' in dir() else ''} | {r[1]} | " + " | ".join(str(x) for x in r[2:2 + len(cols)]) + " |")
    L += ["", "## Units by Year (10-year list)", "", "| year | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    for y, v in (uar.get("by_year") or {}).items():
        L.append(f"| {y} | " + " | ".join(str(v.get(c, 0)) for c in cols) + " |")
    L += ["", "SB 32 fields per property (expiration, units, assistance type, income level, preservation status) are in the Preservation_Queue tab of the packet workbook.", ""]
    from plb.risk_dimensions import dimension_counts
    L += ["## Independent Risk Dimensions", "", "Separate assessments; no overall score. See Risk_Dimensions and the four attention tabs.", ""]
    for axis, counts in dimension_counts(packet.to_dict(orient="records")).items():
        L.append(f"- {axis}: " + "; ".join(f"{status} {count}" for status, count in counts.items()))
    L += ["", "## Status Since Last Report", ""]
    if flips is not None and len(flips):
        for ft, n in flips["flip_type"].value_counts().items():
            if ft:
                L.append(f"- {ft}: {int(n)}")
    else:
        L.append("- no prior run supplied")
    L += ["", "## Sponsor Concentration", ""]
    se = sponsor_exposure(packet)
    for _, r in se.head(10).iterrows():
        L.append(f"- {r['sponsor_org']}: {r['properties']} properties, {r['units']} units, ${r['our_upb']:,.0f} our UPB ({r['upb_share']:.0%}), {r['cliffs_le_36mo']} cliffs <= 36 mo" + (" — concentration flag" if r["sponsor_concentration"] else ""))
    L += ["", "## Redactions Applied", ""]
    for x in redaction_log or []:
        L.append(f"- {x['field']}: {x['rows_redacted']} rows — {x['action']} ({x['cite']})")
    if not redaction_log:
        L.append("- none")
    L += ["", "## Assumptions and Limits", "", f"- {RECORDS_CLASSIFICATION}", "- Every statutory cite is verified_live false in this build; confirm current text before relying on it.",
          "- Board_Totals band on owner_cliff_band (owner-side restriction / contract / debt end); a past HAP date with no termination evidence is a stale record, never OVERDUE or lost.",
          "- Natural-person owners are withheld; residential registered-agent addresses are omitted; no phone or email appears in any output."]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--leads-scored", required=True)
    ap.add_argument("--events", required=True)
    ap.add_argument("--calendar", default=None)
    ap.add_argument("--rejects", default=None)
    ap.add_argument("--assumptions", default=None)
    ap.add_argument("--pack", default=None)
    ap.add_argument("--sources", default=None)
    ap.add_argument("--prior", default=None)
    ap.add_argument("--prior-events", default=None)
    ap.add_argument("--agency-profile", default="hfa")
    ap.add_argument("--out", required=True)
    ap.add_argument("--board-packet", action="store_true")
    ap.add_argument("--internal", action="store_true")
    ap.add_argument("--recalc", action="store_true")
    ap.add_argument("--as-of", default=None)
    a = ap.parse_args(argv)
    as_of = parse_as_of(a.as_of)
    leads = pd.read_csv(a.leads_scored, dtype=str, keep_default_na=False)
    events = pd.read_csv(a.events, dtype=str, keep_default_na=False)
    run_dir = os.path.dirname(os.path.abspath(a.leads_scored))
    calendar = json.load(open(a.calendar)) if a.calendar and os.path.exists(a.calendar) else {}
    rejects = _read(a.rejects)
    params = load_market_params(a.pack, a.assumptions)
    prof = agency_profile(a.agency_profile, a.pack)
    sources = json.load(open(a.sources)) if a.sources and os.path.exists(a.sources) else []
    prior = _read(a.prior)
    flips = status_flips(leads, prior, events, _read(a.prior_events)) if prior is not None else None
    kpi = kpi_summary(flips, leads) if flips is not None else None
    uar_path = os.path.join(run_dir, "units_at_risk.json")
    uar = json.load(open(uar_path)) if os.path.exists(uar_path) else units_at_risk_json(leads, as_of, a.agency_profile, prof.get("board_totals_variant", "loan_book"))
    if kpi:
        uar["kpi"] = kpi
        json.dump(uar, open(uar_path, "w"), indent=2)
    ac = _read(os.path.join(run_dir, "agency_calendar.csv"))
    nc = _read(os.path.join(run_dir, "notice_compliance_queue.csv"))
    gaps = _read(os.path.join(run_dir, "book_join_gaps.csv"))
    scope = "internal" if a.internal else "organization"
    meta = {"as_of_date": as_of.isoformat(), "agency_profile": a.agency_profile, "agency_name": prof.get("agency_name"), "geography_mode": calendar.get("geography_mode", ""),
            "counties": calendar.get("counties", []), "horizon_years": calendar.get("horizon_years", ""), "degraded_note": calendar.get("degraded_note", ""),
            "scoring_source": "references/scoring/affordable_public_am.json + shared_adjustments.json", "universe": "all", "book_coverage": calendar.get("book_coverage", ""), "pii_scope": scope}
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    build_workbook(a.out, leads, events, calendar, rejects, params, sources, flips, meta, uar, ac, nc, None, gaps, pii_scope=scope)
    print(f"[workbook] wrote {a.out} ({len(leads)} leads, {len(events)} events" + (f", status flips {len(flips)}" if flips is not None else "") + ")")
    if a.board_packet:
        bp = os.path.splitext(a.out)[0].replace("_Preservation_LoanBook", "").rsplit("_", 1)[0] + "_Board_Packet.xlsx" if "_Preservation_LoanBook" in a.out else os.path.splitext(a.out)[0] + "_Board_Packet.xlsx"
        res = build_board_packet(bp, leads, uar, flips, params, meta)
        md = write_board_packet_md(os.path.join(run_dir, "board_packet.md"), uar, leads, flips, res["redaction_log"], prof, as_of)
        print(f"[workbook] wrote board packet {bp} and {md} (public_packet scope; {len(res['redaction_log'])} redaction log rows)")
    if a.recalc:
        if os.path.exists(RECALC):
            try:
                subprocess.run([sys.executable, RECALC, a.out], check=False, timeout=120)
            except Exception as exc:  # pragma: no cover
                print(f"[workbook] recalc skipped: {exc}")
        else:
            print("[workbook] recalc requested but recalc.py is not present; workbook holds literals only")


if __name__ == "__main__":
    main()
