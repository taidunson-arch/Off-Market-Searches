"""Calendar header: helper deadlines, LATEST duplicates and the agency's own act-by dates never enter the five basis counts;
the header carries three segments (basis | helper deadlines | agency act-by)."""
from __future__ import annotations

import os
import sys
from datetime import date

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from plb.calendar import header_line, split_helper_rows  # noqa: E402
from plb.schema import AGENCY_ACTION_EVENTS, HELPER_EVENTS  # noqa: E402
from query_calendar import summarize  # noqa: E402

AS_OF = date(2026, 10, 4)


def _ev(pid, et, d, basis="REPORTED", fam=None, status="FUTURE", **kw):
    e = {"event_id": f"{pid}:{et}:{d}", "property_id": pid, "event_type": et, "event_family": fam or "", "direction": "PRESSURE",
         "event_date": d, "basis": basis, "confidence": "1.0", "source": "test", "status": status, "program": "", "verify_flag": ""}
    e.update(kw)
    return e


def test_helper_and_agency_events_excluded_from_by_basis():
    ev = pd.DataFrame([
        _ev("p1", "HAP_EXPIRATION", "2027-12-10", program="HAP"),
        _ev("p1", "HAP_OPTOUT_NOTICE_DEADLINE", "2026-12-10", "DERIVED"),
        _ev("p1", "HAP_OPTOUT_PACKAGE_DUE", "2027-08-12", "DERIVED"),
        _ev("p1", "PRESERVATION_NOTICE_WINDOW", "2027-01-01", "DERIVED", window_start="2027-01-01", window_end="2027-07-01"),
        _ev("p1", "PUSH_FIRST_NOTICE_DUE", "2026-12-01", "DERIVED"),
        _ev("p1", "LIHTC_EXTENDED_USE_END", "2029-06-01"),
        _ev("p1", "REGULATORY_LATEST_END", "2029-06-01"),          # duplicates the extended-use end -> helper
        _ev("p2", "REGULATORY_LATEST_END", "2030-01-01"),          # no component with that date -> counted
        _ev("p2", "AGENCY_LOAN_MATURITY", "2028-05-01", "RECORDED"),
    ])
    sel, s = summarize(ev, AS_OF, 10, 10)
    assert s["by_basis"] == {"RECORDED": 1, "REPORTED": 3, "DERIVED": 0, "ESTIMATED": 0, "PROXY": 0}
    assert s["helper_events"] == 5 and s["helper_by_type"]["PRESERVATION_NOTICE_WINDOW"] == 1 and s["helper_by_type"]["REGULATORY_LATEST_END"] == 1
    assert s["agency_act_by"] == 3 and s["agency_act_by_next_90_days"] == 2  # PUSH_FIRST_NOTICE_DUE 2026-12-01 and HAP_OPTOUT_NOTICE_DEADLINE 2026-12-10 fall inside 90 days
    assert set(sel["event_type"]) == {"HAP_EXPIRATION", "LIHTC_EXTENDED_USE_END", "REGULATORY_LATEST_END", "AGENCY_LOAN_MATURITY"}
    assert s["header"] == ("RECORDED 1 / REPORTED 3 / DERIVED 0 / ESTIMATED 0 / PROXY 0 / Suppressed 0 / Rejected 0 | helper deadlines 5 "
                           "(notice arithmetic, LATEST duplicates; not counted above) | agency act-by 3 (next 90 days 2)")
    core, helper = split_helper_rows(ev)
    assert len(core) == 4 and len(helper) == 5


def test_header_line_format_three_segments():
    s = {"by_basis": {"RECORDED": 2, "REPORTED": 1, "DERIVED": 0, "ESTIMATED": 0, "PROXY": 0}, "suppressed": 1, "rejected": 0, "helper_events": 5,
         "agency_act_by": 7, "agency_act_by_next_90_days": 2}
    assert header_line(s) == ("RECORDED 2 / REPORTED 1 / DERIVED 0 / ESTIMATED 0 / PROXY 0 / Suppressed 1 / Rejected 0 | helper deadlines 5 "
                              "(notice arithmetic, LATEST duplicates; not counted above) | agency act-by 7 (next 90 days 2)")


def test_every_agency_deadline_type_is_a_helper():
    assert AGENCY_ACTION_EVENTS <= HELPER_EVENTS and "PRESERVATION_NOTICE_WINDOW" in HELPER_EVENTS
    for et in ("PUSH_FIRST_NOTICE_DUE", "PUSH_SECOND_NOTICE_DUE", "RECORDS_REQUEST_DUE", "ROFR_MATCH_DEADLINE", "QC_RESPONSE_DUE", "HAP_OPTOUT_NOTICE_DEADLINE", "INSPECTION_DUE"):
        assert et in HELPER_EVENTS


def test_suppressed_rejected_and_stale_counted_separately():
    ev = pd.DataFrame([
        _ev("p1", "LOAN_MATURITY", "2027-12-10", "RECORDED", status="SUPPRESSED"),
        _ev("p1", "LOAN_MATURITY", "2099-12-10", "RECORDED", status="REJECTED"),
        _ev("p1", "HAP_EXPIRATION", "2024-09-30", "REPORTED", status="STALE_CONTRACT_DATE", program="HAP"),
        _ev("p1", "SUPPRESS_UNTIL", "2031-01-01", "DERIVED", direction="SUPPRESSION"),
    ])
    _, s = summarize(ev, AS_OF, 10, 10)
    assert s["suppressed"] == 1 and s["rejected"] == 1 and s["stale_contract_dates"] == 1 and sum(s["by_basis"].values()) == 0
