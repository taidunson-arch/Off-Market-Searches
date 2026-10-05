"""Status flips (the agency KPI): notice filed, HAP renewed, loan extended, covenant default, QC requested, new / left list;
`lost` requires termination evidence and a stale HAP date never counts."""
from __future__ import annotations

import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _fixture_runs import FX, hfa_fixture_run  # noqa: E402
from diff_forecast import kpi_summary, status_flips  # noqa: E402
from plb.schema import FLIP_TYPES  # noqa: E402


def _row(pid, **kw):
    base = {"property_id": pid, "property_name": pid, "queue_band": "PLAN", "intervention_score": "40", "notice_status": "unknown", "tenant_notice_status": "", "qc_status": "",
            "hap_renewal_request_status": "", "our_maturity": "", "payment_type": "", "covenant_status": "current", "recap_status": "none", "kpi_flags": "", "signals": "",
            "primary_route": "none", "owner_cliff_type": "", "owner_cliff_date": "", "events_in_horizon": "[]", "units_at_risk": "40", "first_reg_basis": "REPORTED", "first_debt_basis": ""}
    base.update(kw)
    return base


def test_flip_types_detected():
    prior = pd.DataFrame([_row("a"), _row("b", our_maturity="2027-01-01"), _row("c"), _row("d", events_in_horizon=json.dumps([{"event_type": "HAP_EXPIRATION", "event_date": "2027-03-31", "status": "FUTURE"}])),
                          _row("gone"), _row("q"), _row("s", events_in_horizon=json.dumps([{"event_type": "HAP_EXPIRATION", "event_date": "2024-09-30", "status": "FUTURE"}]))])
    cur = pd.DataFrame([_row("a", notice_status="received", queue_band="ACT"), _row("b", our_maturity="2029-01-01"), _row("c", covenant_status="default"),
                        _row("d", events_in_horizon=json.dumps([{"event_type": "HAP_EXPIRATION", "event_date": "2028-03-31", "status": "FUTURE"}])), _row("new"), _row("q", qc_status="requested"),
                        _row("s", events_in_horizon=json.dumps([{"event_type": "HAP_EXPIRATION", "event_date": "2024-09-30", "status": "STALE_CONTRACT_DATE"}]), signals="hap_date_stale")])
    flips = status_flips(cur, prior)
    got = {(r["property_id"], r["flip_type"]) for _, r in flips.iterrows() if r["flip_type"]}
    assert {("a", "notice_filed"), ("b", "loan_extended"), ("c", "covenant_default"), ("d", "hap_renewed"), ("new", "new_to_list"), ("gone", "left_list"), ("q", "qc_requested")} <= got
    assert not any(ft == "lost" for _, ft in got)                       # stale date is never lost
    assert flips[flips["property_id"] == "a"]["change"].iloc[0] == "escalated"
    assert set(flips["flip_type"]) - {""} <= set(FLIP_TYPES)
    k = kpi_summary(flips, cur)
    assert k["flips"]["notice_filed"] == 1 and k["units_lost_since_prior"] == 0


def test_lost_requires_termination_evidence():
    prior = pd.DataFrame([_row("t")])
    cur = pd.DataFrame([_row("t")])
    ev = pd.DataFrame([{"property_id": "t", "event_type": "HAP_EXPIRATION", "event_date": "2026-06-30", "detail": "terminated", "source": "HUD tape", "status": "PAST"}])
    flips = status_flips(cur, prior, ev, None)
    assert (flips["flip_type"] == "lost").sum() == 1 and "termination evidence" in flips[flips["flip_type"] == "lost"].iloc[0]["evidence"]
    none = status_flips(cur, prior, pd.DataFrame([{"property_id": "t", "event_type": "HAP_EXPIRATION", "event_date": "2024-06-30", "detail": "term_unknown_annual_assumed", "source": "OHCS", "status": "STALE_CONTRACT_DATE"}]), None)
    assert (none["flip_type"] == "lost").sum() == 0


def test_prior_fixture_against_fixture_run():
    r = hfa_fixture_run()
    prior = pd.read_csv(os.path.join(FX, "prior_leads_scored_sample.csv"), dtype=str, keep_default_na=False)
    flips = status_flips(r["scored"], prior, r["events"], None)
    types = set(flips["flip_type"]) - {""}
    assert {"loan_extended", "covenant_default", "qc_requested", "new_to_list", "left_list"} <= types, types
    assert "lost" not in types
