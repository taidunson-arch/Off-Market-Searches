"""Calendar arithmetic shared by query_calendar.py, build_universe.py and run_agency_pipeline.py.

The brief quotes one header before any count of "what is coming due":

    RECORDED n / REPORTED n / DERIVED n / ESTIMATED n / PROXY n / Suppressed n / Rejected n
      | helper deadlines n (notice arithmetic, LATEST duplicates; not counted above) | agency act-by n (next 90 days m)

The five basis counts cover owner-side PRESSURE events that carry their own information. Two kinds of rows are
reported on the second segment instead (pipeline-contract.md Section 8):

* HELPER_EVENTS (every AGENCY_DEADLINE type plus PRESERVATION_NOTICE_WINDOW): arithmetic on another event of the
  same property. Counting them inflated "DERIVED" with notice arithmetic rather than Year-15 dates.
* ROLLUP_EVENTS (REGULATORY_LATEST_END) when the date equals a component program end on the same property.

The third segment counts the agency's own act-by dates (AGENCY_DEADLINE family) and how many fall inside 90 days.
"""
from __future__ import annotations

from typing import Any, Dict, Tuple

import pandas as pd

from .schema import AGENCY_ACTION_EVENTS, BASIS_LEVELS, HELPER_EVENTS, ROLLUP_EVENTS

BASES = list(BASIS_LEVELS)


def split_helper_rows(ev: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Return (core, helper) frames. `helper` holds HELPER_EVENTS plus ROLLUP duplicates."""
    if len(ev) == 0:
        return ev, ev
    is_helper = ev["event_type"].isin(HELPER_EVENTS)
    dup = pd.Series(False, index=ev.index)
    roll = ev[ev["event_type"].isin(ROLLUP_EVENTS)]
    if len(roll):
        comp = ev[~ev["event_type"].isin(ROLLUP_EVENTS | HELPER_EVENTS)]
        comp_keys = set(zip(comp["property_id"].astype(str), comp["event_date"].astype(str)))
        for idx, r in roll.iterrows():
            if (str(r["property_id"]), str(r["event_date"])) in comp_keys:
                dup.at[idx] = True
    helper_mask = is_helper | dup
    return ev[~helper_mask].copy(), ev[helper_mask].copy()


def agency_rows(ev: pd.DataFrame) -> pd.DataFrame:
    if len(ev) == 0:
        return ev
    return ev[ev["event_type"].isin(AGENCY_ACTION_EVENTS)].copy()


def basis_counts(df: pd.DataFrame) -> Dict[str, int]:
    if len(df) == 0:
        return {b: 0 for b in BASES}
    up = df["basis"].astype(str).str.upper()
    return {b: int((up == b).sum()) for b in BASES}


def header_line(summary: Dict[str, Any]) -> str:
    b = summary.get("by_basis", {})
    s = " / ".join(f"{k} {b.get(k, 0)}" for k in BASES)
    s += f" / Suppressed {summary.get('suppressed', 0)} / Rejected {summary.get('rejected', 0)}"
    s += f" | helper deadlines {summary.get('helper_events', 0)} (notice arithmetic, LATEST duplicates; not counted above)"
    s += f" | agency act-by {summary.get('agency_act_by', 0)} (next 90 days {summary.get('agency_act_by_next_90_days', 0)})"
    return s
