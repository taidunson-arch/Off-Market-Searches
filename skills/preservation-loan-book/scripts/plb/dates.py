"""Explicit-format date handling for preservation-loan-book (copied from off-market-deal-finder v2; bands changed).

Design rules (references/pipeline-contract.md):

* A column is parsed with its DECLARED format only. A column that was verified day-first
  (OHCS `Financial_Closing_Date`, `%d/%m/%Y`) is never re-tested row by row.
* `format: auto` is the only mode that runs per-value disambiguation. When both fields are
  <= 12 the row is flagged `Verify — Ambiguous` and both parses are stored in `alt_dates`.
* A missing format flags every value `No Format Declared` rather than guessing.
* `excel_date` accepts datetime/Timestamp objects or Excel serial numbers; `iso` is `%Y-%m-%d`.
* Values that cannot parse under the declared format are rejected with `Rejected — Out of Range`.

Urgency bands are MONTHS (30.4-day), not critical-dates-tracker's days: OVERDUE (< 0) / CRITICAL (0-12) /
URGENT (12-24) / APPROACHING (24-36) / MONITOR (36-60) / SCHEDULED (60-120) / BEYOND (>= 120, outside the
10-year horizon, never scored). Nothing here reads the system clock implicitly except parse_as_of(None).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Dict, Iterable, List, Optional, Tuple

import pandas as pd

from .schema import FLAG_AMBIGUOUS, FLAG_NO_FORMAT, FLAG_REJECTED, URGENCY_BANDS

SLASH_RE = re.compile(r"^\s*(\d{1,2})/(\d{1,2})/(\d{4})\s*$")
USDA_RE = re.compile(r"^\s*(\d{4}) ([A-Za-z]{3}) (\d{1,2})\b")
ISO_RE = re.compile(r"^\s*(\d{4})-(\d{2})-(\d{2})")
MIN_YEAR, MAX_YEAR = 1960, 2100


@dataclass
class ParsedDate:
    value: Optional[date]
    flag: Optional[str] = None
    alt_dates: Optional[List[str]] = None
    quality: str = "declared_format"  # declared_format | auto_unambiguous | ambiguous | rejected | blank


def _to_date(ts) -> Optional[date]:
    if ts is None:
        return None
    if isinstance(ts, datetime):
        return ts.date()
    if isinstance(ts, date):
        return ts
    if isinstance(ts, pd.Timestamp):
        if pd.isna(ts):
            return None
        return ts.date()
    return None


def parse_value(raw, fmt: Optional[str], date_order: str = "month_first") -> ParsedDate:
    """Parse one raw cell with a declared format (strptime format, `excel_date`, `iso`, or `auto`; None -> No Format Declared)."""
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return ParsedDate(None, quality="blank")
    if isinstance(raw, (datetime, date, pd.Timestamp)):
        d = _to_date(raw)
        return _range_check(d, str(raw))
    s = str(raw).strip()
    if s == "" or s.lower() in {"nan", "nat", "none", "null"}:
        return ParsedDate(None, quality="blank")
    if fmt is None:
        return ParsedDate(None, flag=FLAG_NO_FORMAT, quality="rejected")

    if fmt == "excel_date":
        try:
            serial = float(s)
            d = (datetime(1899, 12, 30) + timedelta(days=serial)).date()
            return _range_check(d, s)
        except ValueError:
            pass
        m = ISO_RE.match(s)
        if m:
            try:
                return _range_check(date(int(m.group(1)), int(m.group(2)), int(m.group(3))), s)
            except ValueError:
                return ParsedDate(None, flag=FLAG_REJECTED, quality="rejected")
        fmt = "%m/%d/%Y"

    if fmt == "iso":
        m = ISO_RE.match(s)
        if m:
            return _range_check(_safe_date(int(m.group(1)), int(m.group(2)), int(m.group(3))), s)
        return ParsedDate(None, flag=FLAG_REJECTED, quality="rejected")

    if fmt == "auto":
        m = SLASH_RE.match(s)
        if not m:
            m2 = ISO_RE.match(s)
            if m2:
                return _range_check(_safe_date(int(m2.group(1)), int(m2.group(2)), int(m2.group(3))), s, quality="auto_unambiguous")
            return ParsedDate(None, flag=FLAG_REJECTED, quality="rejected")
        a, b, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if a > 12 and b <= 12:
            return _range_check(_safe_date(y, b, a), s, quality="auto_unambiguous")
        if b > 12 and a <= 12:
            return _range_check(_safe_date(y, a, b), s, quality="auto_unambiguous")
        if a > 12 and b > 12:
            return ParsedDate(None, flag=FLAG_REJECTED, quality="rejected")
        mf, df_ = _safe_date(y, a, b), _safe_date(y, b, a)
        if a == b:
            return _range_check(mf, s, quality="auto_unambiguous")
        point = mf if date_order == "month_first" else df_
        alts = [x.isoformat() for x in (mf, df_) if x]
        pdate = _range_check(point, s, quality="ambiguous")
        pdate.flag = FLAG_AMBIGUOUS
        pdate.alt_dates = alts
        return pdate

    try:
        d = datetime.strptime(s, fmt).date()
    except ValueError:
        try:
            d = datetime.strptime(s.split(" ")[0], fmt).date()
        except ValueError:
            return ParsedDate(None, flag=FLAG_REJECTED, quality="rejected")
    return _range_check(d, s)


def _safe_date(y: int, m: int, d: int) -> Optional[date]:
    try:
        return date(y, m, d)
    except ValueError:
        return None


def _range_check(d: Optional[date], raw: str, quality: str = "declared_format") -> ParsedDate:
    if d is None:
        return ParsedDate(None, flag=FLAG_REJECTED, quality="rejected")
    if not (MIN_YEAR <= d.year <= MAX_YEAR):
        return ParsedDate(None, flag=FLAG_REJECTED, quality="rejected")
    return ParsedDate(d, quality=quality)


def parse_column(series: pd.Series, fmt: Optional[str], date_order: str = "month_first") -> Tuple[pd.Series, pd.DataFrame]:
    """Parse a whole column with its declared format -> (dates Series of date|None, rejects DataFrame)."""
    out: List[Optional[date]] = []
    rej_rows = []
    for idx, raw in series.items():
        p = parse_value(raw, fmt, date_order)
        out.append(p.value)
        if p.flag:
            rej_rows.append({"index": idx, "raw_value": raw, "flag": p.flag,
                             "alt_dates": ";".join(p.alt_dates or []), "quality": p.quality})
    rejects = pd.DataFrame(rej_rows, columns=["index", "raw_value", "flag", "alt_dates", "quality"])
    return pd.Series(out, index=series.index, dtype="object"), rejects


# --------------------------------------------------------------------------- profiling
def profile_series(series: pd.Series) -> Optional[Dict[str, object]]:
    """Profile a text column for day-first vs month-first. Returns None if < 5 date-like values."""
    vals = [str(v).strip() for v in series.dropna().tolist() if str(v).strip() not in ("", "nan")]
    slash = [SLASH_RE.match(v) for v in vals]
    slash = [m for m in slash if m]
    usda = [v for v in vals if USDA_RE.match(v)]
    iso_ = [v for v in vals if ISO_RE.match(v)]
    n = len(slash) + len(usda) + len(iso_)
    if n < 5:
        return None
    first_gt12 = sum(1 for m in slash if int(m.group(1)) > 12)
    second_gt12 = sum(1 for m in slash if int(m.group(2)) > 12)
    if usda and len(usda) >= len(slash):
        proposed = "%Y %b %d %I:%M:%S %p"
    elif iso_ and len(iso_) >= len(slash):
        proposed = "%Y-%m-%d"
    elif first_gt12 and not second_gt12:
        proposed = "%d/%m/%Y"
    elif second_gt12 and not first_gt12:
        proposed = "%m/%d/%Y"
    else:
        proposed = "auto"
    return {"rows": n, "slash_rows": len(slash), "first_gt12": first_gt12, "second_gt12": second_gt12,
            "usda_rows": len(usda), "iso_rows": len(iso_), "proposed_format": proposed}


# --------------------------------------------------------------------------- arithmetic
def add_years(d: date, years: int) -> date:
    try:
        return d.replace(year=d.year + years)
    except ValueError:  # Feb 29
        return d.replace(year=d.year + years, day=28)


def add_months(d: date, months: int) -> date:
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    last = [31, 29 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
    return date(y, m, min(d.day, last))


def add_days(d: date, days: int) -> date:
    return d + timedelta(days=days)


def months_between(as_of: date, d: date) -> float:
    """Signed months from as_of to d (positive = future), 30.4-day months, rounded to 0.1."""
    return round((d - as_of).days / 30.4, 1)


def days_since(as_of: date, d: date) -> int:
    return (as_of - d).days


def urgency_band(months_out: Optional[float]) -> Optional[str]:
    """OVERDUE (<0) / CRITICAL / URGENT / APPROACHING / MONITOR / SCHEDULED / BEYOND (>=120). Months, not days."""
    if months_out is None:
        return None
    for band, lo, hi, _ in URGENCY_BANDS:
        if (lo is None or months_out >= lo) and (hi is None or months_out < hi):
            return band
    return "BEYOND"


def timing_fraction(months_out: Optional[float]) -> float:
    if months_out is None:
        return 0.0
    for band, lo, hi, frac in URGENCY_BANDS:
        if (lo is None or months_out >= lo) and (hi is None or months_out < hi):
            return frac
    return 0.0


def band_for_date(as_of: date, d: Optional[date]) -> Optional[str]:
    return urgency_band(months_between(as_of, d)) if d else None


def parse_as_of(value: Optional[str]) -> date:
    """Resolve --as-of. None -> date.today(). The only place the clock is read."""
    if value is None or str(value).strip() == "":
        return date.today()
    return datetime.strptime(str(value).strip(), "%Y-%m-%d").date()


def parse_iso(s) -> Optional[date]:
    if s is None:
        return None
    if isinstance(s, datetime):
        return s.date()
    if isinstance(s, date):
        return s
    s = str(s).strip()
    if not s or s.lower() in ("nan", "none", "nat"):
        return None
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def iso(d: Optional[date]) -> str:
    return d.isoformat() if isinstance(d, date) else ""


def max_date(dates: Iterable[Optional[date]]) -> Optional[date]:
    ds = [d for d in dates if isinstance(d, date)]
    return max(ds) if ds else None
