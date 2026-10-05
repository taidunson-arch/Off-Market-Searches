"""plb: library package for the preservation-loan-book skill.

Self-contained copy of the affordable spine of off-market-deal-finder v2 (dates, geography, calendar,
adapters, workbook plumbing) recast for a public-agency asset manager: the user is a lender, grantor or
qualified purchaser, the routes are agency interventions, and the agency's own ledger is a RECORDED source.

Modules
  schema          enums, event taxonomy, lead / event tables, embedded pack defaults and loaders
  dates           declared-format date parsing, month arithmetic, urgency bands (months, OVERDUE..BEYOND)
  geo             county-FIPS geography modes, address normalization, property ids
  calendar        basis header with helper-deadline and agency act-by segments
  adapters        shared file-drop adapter helpers
  entities        owner_type inference, sponsor archetypes (intervention owner, not outreach angle)
  recap_math      restricted NOI, loan constant, recap gap, recapture exposure
  pii             sunshine / PII scopes (public_packet, organization, internal)
  mandate         NOFA product eligibility predicate (route-level hard filter)
  book_join       servicing extract <-> inventory join (crosswalk > address > fuzzy > unmatched)
  units           units / households / public dollars at risk and the Board_Totals pivot
  agency_calendar withdrawal anchor, PuSH windows, AGENCY_DEADLINE events, stale contract dates
  scoring         JSON-driven scoring engine (affordable_public_am), routes, queue bands
  workbook        openpyxl renderer for the working file and the board packet
"""
__version__ = "1.0.0"

# pandas >= 3 defaults to a dedicated string dtype that refuses non-string assignments into columns created from "".
# Every table in this pack is an object-dtype frame read with dtype=str / keep_default_na=False, so restore that behaviour.
try:  # pragma: no cover - option name differs across pandas versions
    import pandas as _pd
    _pd.set_option("future.infer_string", False)
except Exception:
    pass
