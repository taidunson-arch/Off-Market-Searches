#!/usr/bin/env python3
"""Status flips between two scored lead tables: the agency's KPI (notice filed, QC in, HAP renewed, our loan extended).

status_flips.csv columns: property_id, property_name, flip_type, prior_value, new_value, evidence, basis, change (v2 enum new / escalated /
de-escalated / retired as a secondary column). flip_type enum: notice_filed, tenant_notice_confirmed, qc_requested, qc_presented, hap_renewed,
hap_optout, loan_extended, loan_recast, covenant_cured, covenant_default, recap_closed, preserved, lost, new_to_list, left_list.
`lost` requires termination evidence (events with detail terminated / expired-not-renewed, or QC lapsed with extended use past);
a stale HAP date is never `lost`.

Usage: python scripts/diff_forecast.py --current runs/x/leads_scored.csv --prior runs/prior/leads_scored.csv
           [--current-events runs/x/events.csv --prior-events runs/prior/events.csv] --out runs/x/status_flips.csv [--summary runs/x/kpi_summary.json]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plb.dates import parse_iso  # noqa: E402

QUEUE_ORDER = {"ESCALATE": 4, "ACT": 3, "PLAN": 2, "WATCH": 1, "EXCLUDED": 0}
COLUMNS = ["property_id", "property_name", "flip_type", "prior_value", "new_value", "evidence", "basis", "change"]


def _g(row, key, default=""):
    v = row.get(key, default)
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return default
    return str(v)


def _hap_date(row) -> Optional[str]:
    try:
        for e in json.loads(row.get("events_in_horizon") or "[]"):
            if e.get("event_type") == "HAP_EXPIRATION" and e.get("status") != "STALE_CONTRACT_DATE":
                return e.get("event_date")
    except Exception:
        return None
    return None


def _terminated(events: Optional[pd.DataFrame], pid: str) -> Optional[str]:
    if events is None or not len(events):
        return None
    sub = events[(events["property_id"].astype(str) == pid)]
    for _, e in sub.iterrows():
        det = str(e.get("detail") or "").lower()
        if e.get("event_type") == "HAP_EXPIRATION" and ("terminated" in det or "expired_not_renewed" in det):
            return f"HAP termination evidence: {e.get('source')} {e.get('event_date')} ({det})"
        if e.get("event_type") == "QC_ELIGIBILITY" and str(e.get("status") or "") == "lapsed_decontrol":
            return f"QC lapsed / decontrol: {e.get('source')} {e.get('event_date')}"
    return None


def status_flips(cur: pd.DataFrame, prior: pd.DataFrame, cur_events: Optional[pd.DataFrame] = None, prior_events: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    p = prior.set_index("property_id") if len(prior) else pd.DataFrame()
    c = cur.set_index("property_id")

    def add(pid, name, ft, a, b, ev, basis, change=""):
        rows.append({"property_id": pid, "property_name": name, "flip_type": ft, "prior_value": a, "new_value": b, "evidence": ev, "basis": basis, "change": change})

    for pid, r in c.iterrows():
        name = _g(r, "property_name")
        if pid not in p.index:
            add(pid, name, "new_to_list", "", _g(r, "queue_band"), f"first seen; owner cliff {_g(r, 'owner_cliff_type')} {_g(r, 'owner_cliff_date')}", _g(r, "first_reg_basis") or _g(r, "first_debt_basis"), "new")
            continue
        q = p.loc[pid]
        if isinstance(q, pd.DataFrame):
            q = q.iloc[0]
        change = ""
        q0, q1 = QUEUE_ORDER.get(_g(q, "queue_band"), 0), QUEUE_ORDER.get(_g(r, "queue_band"), 0)
        if q1 > q0:
            change = "escalated"
        elif q1 < q0:
            change = "de-escalated"
        ns0, ns1 = _g(q, "notice_status"), _g(r, "notice_status")
        if ns1 == "received" and ns0 != "received":
            add(pid, name, "notice_filed", ns0, ns1, "notice_status -> received", "RECORDED", change)
        tn0, tn1 = _g(q, "tenant_notice_status"), _g(r, "tenant_notice_status")
        if tn1 == "confirmed" and tn0 != "confirmed":
            add(pid, name, "tenant_notice_confirmed", tn0, tn1, "tenant_notice_status -> confirmed", "RECORDED", change)
        qc0, qc1 = _g(q, "qc_status"), _g(r, "qc_status")
        if qc1 == "requested" and qc0 != "requested":
            add(pid, name, "qc_requested", qc0, qc1, "qc_status -> requested", "RECORDED", change)
        if qc1 == "presented" and qc0 != "presented":
            add(pid, name, "qc_presented", qc0, qc1, "qc_status -> presented", "RECORDED", change)
        h0, h1 = _hap_date(q), _hap_date(r)
        rr0, rr1 = _g(q, "hap_renewal_request_status"), _g(r, "hap_renewal_request_status")
        date_moved = bool(h0 and h1 and parse_iso(h1) and parse_iso(h0) and (parse_iso(h1) - parse_iso(h0)).days >= 330)
        if date_moved:
            add(pid, name, "hap_renewed", h0, h1, "HAP_EXPIRATION moved later >= 11 months", "REPORTED", change)
        elif rr1 == "received" and rr0 != "received":
            add(pid, name, "hap_renewed", f"hap_renewal_request_status={rr0 or 'unknown'}", f"hap_renewal_request_status={rr1}",
                "renewal request received at the CA (HAP date unchanged)", "RECORDED", change)
        if "hap_optout" in _g(r, "kpi_flags") or ("optout_response" == _g(r, "primary_route") and _g(q, "primary_route") != "optout_response"):
            if "hap_optout" not in _g(q, "signals"):
                add(pid, name, "hap_optout", _g(q, "primary_route"), _g(r, "primary_route"), "opt-out notice / optout_response route", "RECORDED", change)
        m0, m1 = parse_iso(_g(q, "our_maturity")), parse_iso(_g(r, "our_maturity"))
        if m0 and m1 and m1 > m0:
            add(pid, name, "loan_extended", m0.isoformat(), m1.isoformat(), "our_maturity later than prior run", "RECORDED", change)
        pt0, pt1 = _g(q, "payment_type"), _g(r, "payment_type")
        if pt0 and pt1 and pt0 != pt1:
            add(pid, name, "loan_recast", pt0, pt1, "payment_type changed", "RECORDED", change)
        cs0, cs1 = _g(q, "covenant_status"), _g(r, "covenant_status")
        if cs0 in ("default", "watch") and cs1 in ("cured", "current", "released") and cs0 != cs1:
            add(pid, name, "covenant_cured", cs0, cs1, "covenant_status cured / current", "RECORDED", change)
        if cs1 == "default" and cs0 != "default":
            add(pid, name, "covenant_default", cs0, cs1, "covenant_status -> default", "RECORDED", change)
        rs0, rs1 = _g(q, "recap_status"), _g(r, "recap_status")
        if rs1 == "closed" and rs0 != "closed":
            add(pid, name, "recap_closed", rs0, rs1, "recap_status -> closed", "RECORDED", change)
        if ("preserved" in _g(r, "kpi_flags") and "preserved" not in _g(q, "kpi_flags")) or (rs1 == "closed" and rs0 != "closed"):
            add(pid, name, "preserved", rs0, rs1 or "preserved", "STABILIZATION_AWARD / recap closed", "RECORDED", change)
        term = _terminated(cur_events, str(pid))
        if term and not _terminated(prior_events, str(pid)):
            add(pid, name, "lost", _g(q, "owner_cliff_type"), "terminated", term, "RECORDED", change)
        if change and not any(x["property_id"] == pid for x in rows[-3:]):
            rows.append({"property_id": pid, "property_name": name, "flip_type": "", "prior_value": _g(q, "queue_band"), "new_value": _g(r, "queue_band"),
                         "evidence": f"score {_g(q, 'intervention_score')} -> {_g(r, 'intervention_score')}", "basis": "", "change": change})
    for pid, q in (p.iterrows() if len(p) else []):
        if pid not in c.index:
            add(pid, _g(q, "property_name"), "left_list", _g(q, "queue_band"), "", "no longer in list (out of horizon, recapitalized, merged or suppressed); check events for the retiring event", "", "retired")
    return pd.DataFrame(rows, columns=COLUMNS)


def kpi_summary(flips: pd.DataFrame, cur: pd.DataFrame) -> Dict[str, Any]:
    units = cur.set_index("property_id")["units_at_risk"] if "units_at_risk" in cur.columns else pd.Series(dtype=str)

    def units_for(types):
        pids = set(flips[flips["flip_type"].isin(types)]["property_id"]) if len(flips) else set()
        return int(sum(float(units.get(p, 0) or 0) for p in pids if p in units.index))

    counts = flips["flip_type"].value_counts().to_dict() if len(flips) else {}
    return {"units_preserved_since_prior": units_for(["preserved", "recap_closed"]), "units_lost_since_prior": units_for(["lost"]),
            "flips": {k: int(v) for k, v in counts.items() if k}}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--current", required=True)
    ap.add_argument("--prior", required=True)
    ap.add_argument("--current-events", default=None)
    ap.add_argument("--prior-events", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--summary", default=None)
    a = ap.parse_args(argv)
    cur = pd.read_csv(a.current, dtype=str, keep_default_na=False)
    prior = pd.read_csv(a.prior, dtype=str, keep_default_na=False)
    ce = pd.read_csv(a.current_events, dtype=str, keep_default_na=False) if a.current_events and os.path.exists(a.current_events) else None
    pe = pd.read_csv(a.prior_events, dtype=str, keep_default_na=False) if a.prior_events and os.path.exists(a.prior_events) else None
    flips = status_flips(cur, prior, ce, pe)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    flips.to_csv(a.out, index=False)
    k = kpi_summary(flips, cur)
    if a.summary:
        json.dump(k, open(a.summary, "w"), indent=2)
    print(f"[diff] {len(flips)} status flips -> {a.out}; kpi {k}")


if __name__ == "__main__":
    main()
