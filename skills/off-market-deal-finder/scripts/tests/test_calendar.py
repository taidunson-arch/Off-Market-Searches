"""Calendar header: helper deadlines and LATEST duplicates never appear in the five basis counts."""
from __future__ import annotations

import os
import sys
from datetime import date

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from omdf.calendar import header_line, split_helper_rows  # noqa: E402
from query_calendar import summarize  # noqa: E402

AS_OF = date(2026, 10, 4)


def _ev(pid, et, d, basis="REPORTED", fam=None, status="FUTURE", **kw):
    e = {"event_id": f"{pid}:{et}:{d}", "property_id": pid, "event_type": et, "event_family": fam or "", "direction": "PRESSURE",
         "event_date": d, "basis": basis, "confidence": "1.0", "source": "test", "status": status, "program": "", "verify_flag": ""}
    e.update(kw)
    return e


def test_helper_events_excluded_from_by_basis():
    ev = pd.DataFrame([
        _ev("p1", "HAP_EXPIRATION", "2027-12-10"),
        _ev("p1", "HAP_OPTOUT_NOTICE_DEADLINE", "2026-12-10", "DERIVED"),
        _ev("p1", "PRESERVATION_NOTICE_WINDOW", "2027-01-01", "DERIVED", window_start="2027-01-01", window_end="2027-07-01"),
        _ev("p1", "LIHTC_EXTENDED_USE_END", "2029-06-01"),
        _ev("p1", "REGULATORY_LATEST_END", "2029-06-01"),          # duplicates the extended-use end -> helper
        _ev("p2", "REGULATORY_LATEST_END", "2030-01-01"),          # no component with that date -> counted
        _ev("p2", "LOAN_MATURITY", "2028-05-01", "PROXY"),
    ])
    sel, s = summarize(ev, AS_OF, 5, 5)
    assert s["by_basis"] == {"RECORDED": 0, "REPORTED": 3, "DERIVED": 0, "ESTIMATED": 0, "PROXY": 1}
    assert s["helper_events"] == 3 and s["helper_by_type"] == {"HAP_OPTOUT_NOTICE_DEADLINE": 1, "PRESERVATION_NOTICE_WINDOW": 1, "REGULATORY_LATEST_END": 1}
    assert set(sel["event_type"]) == {"HAP_EXPIRATION", "LIHTC_EXTENDED_USE_END", "REGULATORY_LATEST_END", "LOAN_MATURITY"}
    assert "helper deadlines 3" in s["header"] and s["header"].startswith("RECORDED 0 / REPORTED 3 / DERIVED 0 / ESTIMATED 0 / PROXY 1 / Suppressed 0 / Rejected 0")
    core, helper = split_helper_rows(ev)
    assert len(core) == 4 and len(helper) == 3


def test_header_line_format():
    s = {"by_basis": {"RECORDED": 2, "REPORTED": 1, "DERIVED": 0, "ESTIMATED": 0, "PROXY": 0}, "suppressed": 1, "rejected": 0, "helper_events": 5}
    assert header_line(s) == "RECORDED 2 / REPORTED 1 / DERIVED 0 / ESTIMATED 0 / PROXY 0 / Suppressed 1 / Rejected 0 | helper deadlines 5 (notice arithmetic, LATEST duplicates; not counted above)"


def test_suppressed_and_rejected_counted_separately():
    ev = pd.DataFrame([
        _ev("p1", "LOAN_MATURITY", "2027-12-10", "RECORDED", status="SUPPRESSED"),
        _ev("p1", "LOAN_MATURITY", "2099-12-10", "RECORDED", status="REJECTED"),
        _ev("p1", "SUPPRESS_UNTIL", "2031-01-01", "DERIVED", direction="SUPPRESSION"),
    ])
    _, s = summarize(ev, AS_OF, 5, 5)
    assert s["suppressed"] == 1 and s["rejected"] == 1 and sum(s["by_basis"].values()) == 0
