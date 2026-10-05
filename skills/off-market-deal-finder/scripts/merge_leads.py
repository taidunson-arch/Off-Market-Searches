#!/usr/bin/env python3
"""Union adapter outputs (OHCS, HUD FHASL, HUD Sec 8, recorder extracts ...) into one lead table + one event table.

Join key is `property_id` (`{state}-{county}-{parcel}` or `addr:<sha1-12>` of the normalized address + zip5).
When two rows share no id but their upper-cased name + zip5 match at >= 0.92 token ratio, they are merged and the
decision is logged to merge_log.csv. For each lead field the value from the higher-basis source wins
(RECORDED > REPORTED > DERIVED > ESTIMATED > PROXY); losing dates are kept in `alt_dates` on the event.
SUPPRESS_UNTIL events in the future mark DEBT-family events SUPPRESSED, then first_debt / first_reg are recomputed.

Usage:
  python scripts/merge_leads.py --inputs a/leads.csv b/leads.csv --events a/events.csv b/events.csv \
      --out-dir runs/merged [--horizon-years 5] [--regulatory-horizon-years 5] [--as-of YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import sys
from typing import Dict, List

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from omdf.dates import months_between, parse_as_of, urgency_band  # noqa: E402
from omdf.geo import zip5  # noqa: E402
from omdf.schema import BASIS_MULTIPLIER, EVENT_COLUMNS, HELPER_EVENTS, LEAD_COLUMNS, family_of  # noqa: E402
BASIS_RANK = {b: i for i, b in enumerate(["RECORDED", "REPORTED", "DERIVED", "ESTIMATED", "PROXY"])}


def _rank(b: str) -> int:
    return BASIS_RANK.get(str(b or "").upper(), 9)


def fuzzy_key(name: str, z: str) -> str:
    return f"{str(name or '').upper().strip()}|{zip5(z)}"


_PHASE_RE = __import__("re").compile(r"\b(\d+|[IVX]+|PHASE\s*\w+|[A-Z])\b")


def phase_tokens(name: str) -> frozenset:
    """Digits, roman numerals and single letters that distinguish 'Powell Plaza I' from 'Powell Plaza II'."""
    return frozenset(m.group(0).replace(" ", "") for m in _PHASE_RE.finditer(str(name or "").upper()))


def merge(lead_frames: List[pd.DataFrame], event_frames: List[pd.DataFrame], as_of, horizon_years: float, reg_horizon_years: float):
    for i, f in enumerate(lead_frames):
        f["_src"] = i  # rows from the same adapter output are distinct properties; never fuzzy-merge within a source
    leads = pd.concat(lead_frames, ignore_index=True) if lead_frames else pd.DataFrame(columns=LEAD_COLUMNS + ["_src"])
    events = pd.concat(event_frames, ignore_index=True) if event_frames else pd.DataFrame(columns=EVENT_COLUMNS)
    for c in LEAD_COLUMNS:
        if c not in leads.columns:
            leads[c] = ""
    log = []
    # ---- fuzzy id reconciliation
    canon: Dict[str, str] = {}
    by_key: Dict[str, tuple] = {}  # fuzzy key -> (canonical pid, source index, phase tokens)
    for _, r in leads.iterrows():
        pid = str(r["property_id"])
        k = fuzzy_key(r["property_name"], r["zip"])
        src = r.get("_src")
        toks = phase_tokens(r["property_name"])
        matched = None
        if pid not in canon and k.split("|")[1]:
            for other_k, (other_pid, other_src, other_toks) in by_key.items():
                if other_src == src or other_pid == pid or other_k.split("|")[1] != k.split("|")[1]:
                    continue
                if other_toks != toks:
                    continue  # 'Phase I' vs 'Phase II' or '4' vs '5': siblings, not duplicates
                ratio = difflib.SequenceMatcher(None, other_k.split("|")[0], k.split("|")[0]).ratio()
                if ratio >= 0.92:
                    matched = other_pid
                    log.append({"property_id": pid, "merged_into": other_pid, "name": r["property_name"], "ratio": round(ratio, 3)})
                    break
        canon[pid] = matched or canon.get(pid, pid)
        by_key.setdefault(k, (canon[pid], src, toks))
    leads = leads.drop(columns=["_src"])
    leads["property_id"] = leads["property_id"].map(lambda p: canon.get(str(p), str(p)))
    if len(events):
        events["property_id"] = events["property_id"].map(lambda p: canon.get(str(p), str(p)))

    # ---- field-level merge preferring higher basis (first_* basis as proxy for the row's evidence quality)
    def row_rank(r):
        return min(_rank(r.get("first_debt_basis")), _rank(r.get("first_reg_basis")))

    merged_rows = []
    for pid, grp in leads.groupby("property_id", sort=False):
        grp = grp.copy()
        grp["_rank"] = grp.apply(row_rank, axis=1)
        grp = grp.sort_values("_rank")
        base = grp.iloc[0].to_dict()
        fill_cols = [c for c in grp.columns if not str(c).startswith("_")]  # canonical plus adapter extras (mailing_address, lender_type, on_state_expiring_list ...)
        for _, other in grp.iloc[1:].iterrows():
            for c in fill_cols:
                if (base.get(c) in ("", None) or (isinstance(base.get(c), float) and pd.isna(base.get(c)))) and other.get(c) not in ("", None):
                    base[c] = other[c]
            for c in ("signals", "verify_flags", "programs", "source_vintages", "compliance_gates"):
                a_, b_ = str(base.get(c) or ""), str(other.get(c) or "")
                items = [x for x in (a_ + ";" + b_).split(";") if x.strip()]
                base[c] = ";".join(dict.fromkeys(items))
        base.pop("_rank", None)
        merged_rows.append(base)
    extra_cols = [c for c in leads.columns if c not in LEAD_COLUMNS and not c.startswith("_")]
    out = pd.DataFrame(merged_rows, columns=LEAD_COLUMNS + extra_cols).astype(object)

    # ---- events: dedupe same (property, type, program, date); keep best basis, record alternates
    if len(events):
        events["_rank"] = events["basis"].map(_rank)
        events = events.sort_values(["property_id", "event_type", "_rank"])
        keep = []
        for (pid, et, prog), grp in events.groupby(["property_id", "event_type", events["program"].fillna("")], sort=False):
            best = grp.iloc[0].to_dict()
            alts = sorted({str(d) for d in grp["event_date"].tolist() if str(d) and str(d) != str(best["event_date"])})
            if alts:
                prev = [x for x in str(best.get("alt_dates") or "").split(";") if x]
                best["alt_dates"] = ";".join(dict.fromkeys(prev + alts))
                if not best.get("verify_flag"):
                    best["verify_flag"] = "Verify — Conflicting Sources"
            keep.append(best)
        events = pd.DataFrame(keep).astype(object)
        events = events.drop(columns=[c for c in ["_rank"] if c in events.columns])
        # suppression
        d = pd.to_datetime(events["event_date"], errors="coerce")
        events["months_out"] = [months_between(as_of, x.date()) if pd.notna(x) else "" for x in d]
        events["urgency_band"] = events["months_out"].map(lambda m: urgency_band(m) if m != "" else "")
        sup = events[(events["event_type"] == "SUPPRESS_UNTIL") & (d > pd.Timestamp(as_of))]
        for pid in set(sup["property_id"]):
            m = (events["property_id"] == pid) & (events["event_family"] == "DEBT") & (events["event_type"] != "SUPPRESS_UNTIL")
            events.loc[m, "status"] = "SUPPRESSED"
            log.append({"property_id": pid, "merged_into": pid, "name": "SUPPRESS_UNTIL applied", "ratio": ""})

        # recompute first_debt / first_reg
        hz, rz = horizon_years * 12, reg_horizon_years * 12
        live = events[~events["status"].isin(["REJECTED", "SUPPRESSED"])]
        for i, r in out.iterrows():
            ev = live[live["property_id"] == r["property_id"]]
            ev = ev[ev["direction"] == "PRESSURE"]
            debt = ev[(ev["event_family"] == "DEBT") & (pd.to_numeric(ev["months_out"], errors="coerce") >= 0) & (pd.to_numeric(ev["months_out"], errors="coerce") <= hz)]
            reg = ev[(ev["event_family"] == "REGULATORY") & (~ev["event_type"].isin(HELPER_EVENTS)) & (pd.to_numeric(ev["months_out"], errors="coerce") >= 0) & (pd.to_numeric(ev["months_out"], errors="coerce") <= rz)]
            for prefix, sub in (("first_debt", debt), ("first_reg", reg)):
                if len(sub):
                    f = sub.sort_values("event_date").iloc[0]
                    out.at[i, f"{prefix}_event_type"] = f["event_type"]; out.at[i, f"{prefix}_event_date"] = f["event_date"]
                    out.at[i, f"{prefix}_months_out"] = f["months_out"]; out.at[i, f"{prefix}_basis"] = f["basis"]; out.at[i, f"{prefix}_source"] = f["source"]
                else:
                    for s in ("_event_type", "_event_date", "_months_out", "_basis", "_source"):
                        out.at[i, prefix + s] = ""
            inh = ev[pd.to_numeric(ev["months_out"], errors="coerce").between(0, max(hz, rz))].sort_values("event_date")
            out.at[i, "events_in_horizon"] = json.dumps([{k: rr.get(k, "") for k in ("event_type", "event_date", "months_out", "basis", "confidence", "source", "verify_flag", "alt_dates", "window_start", "window_end", "direction")} for rr in inh.to_dict(orient="records")])
        out["as_of_date"] = as_of.isoformat()
    return out, events, pd.DataFrame(log, columns=["property_id", "merged_into", "name", "ratio"])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--inputs", nargs="+", required=True, help="leads.csv files")
    ap.add_argument("--events", nargs="+", required=True, help="events.csv files (same order not required)")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--horizon-years", type=float, default=5)
    ap.add_argument("--regulatory-horizon-years", type=float, default=None)
    ap.add_argument("--as-of", default=None)
    a = ap.parse_args(argv)
    as_of = parse_as_of(a.as_of)
    lf = [pd.read_csv(p, dtype=str, keep_default_na=False) for p in a.inputs if os.path.exists(p)]
    ef = [pd.read_csv(p, dtype=str, keep_default_na=False) for p in a.events if os.path.exists(p)]
    out, events, log = merge(lf, ef, as_of, a.horizon_years, a.regulatory_horizon_years or a.horizon_years)
    os.makedirs(a.out_dir, exist_ok=True)
    out.to_csv(os.path.join(a.out_dir, "leads.csv"), index=False)
    events.to_csv(os.path.join(a.out_dir, "events.csv"), index=False)
    log.to_csv(os.path.join(a.out_dir, "merge_log.csv"), index=False)
    print(f"[merge] inputs {len(lf)} lead files / {len(ef)} event files -> {len(out)} leads, {len(events)} events; fuzzy merges/suppressions logged: {len(log)}")


if __name__ == "__main__":
    main()
