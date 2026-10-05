"""Date parsing: declared formats win, auto mode flags ambiguity, USDA format, Excel serials, ranges."""
from __future__ import annotations

import os
import sys
from datetime import date

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from plb import dates as D  # noqa: E402
from plb.schema import FLAG_AMBIGUOUS, FLAG_NO_FORMAT, FLAG_REJECTED  # noqa: E402


def test_declared_day_first_never_guesses():
    p = D.parse_value("26/01/2022", "%d/%m/%Y")
    assert p.value == date(2022, 1, 26) and p.flag is None and p.quality == "declared_format"
    # 03/04/2031 under a declared day-first format is 3 April, with no ambiguity flag
    p = D.parse_value("03/04/2031", "%d/%m/%Y")
    assert p.value == date(2031, 4, 3) and p.flag is None


def test_declared_month_first():
    assert D.parse_value("02/14/2074", "%m/%d/%Y").value == date(2074, 2, 14)
    # month 14 cannot parse month-first -> rejected, never swapped
    p = D.parse_value("14/02/2030", "%m/%d/%Y")
    assert p.value is None and p.flag == FLAG_REJECTED


def test_auto_mode_flags_ambiguous_and_keeps_both():
    p = D.parse_value("03/04/2031", "auto", date_order="month_first")
    assert p.flag == FLAG_AMBIGUOUS and p.value == date(2031, 3, 4) and set(p.alt_dates) == {"2031-03-04", "2031-04-03"}
    p = D.parse_value("03/04/2031", "auto", date_order="day_first")
    assert p.value == date(2031, 4, 3)
    assert D.parse_value("26/01/2022", "auto").value == date(2022, 1, 26) and D.parse_value("26/01/2022", "auto").flag is None
    assert D.parse_value("01/26/2022", "auto").value == date(2022, 1, 26)


def test_usda_format():
    assert D.parse_value("2038 Nov 17 12:00:00 AM", "%Y %b %d %I:%M:%S %p").value == date(2038, 11, 17)


def test_excel_serial_and_iso():
    assert D.parse_value(45000, "excel_date").value == date(2023, 3, 15)
    assert D.parse_value("2027-06-01", "excel_date").value == date(2027, 6, 1)
    assert D.parse_value(pd.Timestamp("2029-01-31"), "excel_date").value == date(2029, 1, 31)


def test_no_format_declared_and_range():
    assert D.parse_value("01/02/2030", None).flag == FLAG_NO_FORMAT
    assert D.parse_value("01/02/1901", "%m/%d/%Y").flag == FLAG_REJECTED
    assert D.parse_value("", "%m/%d/%Y").value is None and D.parse_value("", "%m/%d/%Y").flag is None


def test_parse_column_rejects_frame():
    s = pd.Series(["26/01/2022", "13/13/2022", None, "05/06/2020"])
    dates, rej = D.parse_column(s, "%d/%m/%Y")
    assert dates.iloc[0] == date(2022, 1, 26) and dates.iloc[1] is None and dates.iloc[3] == date(2020, 6, 5)
    assert len(rej) == 1 and rej.iloc[0]["flag"] == FLAG_REJECTED


def test_profile_series():
    p = D.profile_series(pd.Series(["26/01/2022", "13/05/2019", "02/03/2020", "30/12/2021", "01/01/2018"]))
    assert p["proposed_format"] == "%d/%m/%Y" and p["first_gt12"] == 3 and p["second_gt12"] == 0
    p = D.profile_series(pd.Series(["01/02/2022", "02/03/2019", "03/04/2020", "05/06/2021", "07/08/2018"]))
    assert p["proposed_format"] == "auto"


def test_months_and_urgency():
    as_of = date(2026, 10, 4)
    assert D.months_between(as_of, date(2027, 10, 4)) == 12.0
    assert D.urgency_band(6) == "CRITICAL" and D.urgency_band(12) == "URGENT" and D.urgency_band(30) == "APPROACHING"
    assert D.urgency_band(48) == "MONITOR" and D.urgency_band(72) == "SCHEDULED"
    assert D.timing_fraction(13) == 0.75 and D.timing_fraction(61) == 0.0
    assert D.add_years(date(2024, 2, 29), 15) == date(2039, 2, 28)
    assert D.add_months(date(2030, 1, 31), -12) == date(2029, 1, 31) and D.add_months(date(2030, 3, 31), -1) == date(2030, 2, 28)


def test_overdue_and_beyond_bands_months_not_days():
    assert D.urgency_band(-0.1) == "OVERDUE" and D.urgency_band(-30) == "OVERDUE"
    assert D.urgency_band(0) == "CRITICAL" and D.urgency_band(119.9) == "SCHEDULED" and D.urgency_band(120) == "BEYOND" and D.urgency_band(500) == "BEYOND"
    assert D.timing_fraction(-5) == 1.0 and D.timing_fraction(0) == 1.0 and D.timing_fraction(12) == 0.75 and D.timing_fraction(24) == 0.5
    assert D.timing_fraction(36) == 0.25 and D.timing_fraction(60) == 0.0 and D.timing_fraction(130) == 0.0 and D.timing_fraction(None) == 0.0
    assert D.urgency_band(None) is None
