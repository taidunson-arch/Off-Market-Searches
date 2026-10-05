"""omdf - shared library for the off-market-deal-finder v2 scripts.

Modules
-------
schema        enums, event taxonomy, canonical lead columns, default dataset schemas and market params
dates         explicit-format date parsing, day-first/month-first profiling, months_out and urgency bands
geo           county FIPS maps, geography modes, address normalization and property_id construction
capital_stack amortization, loan constant, NOI proxies, refinance test, inferred maturity windows
scoring       JSON-driven scoring engine (reads references/scoring/*.json), routes, tiers, explain
entities      owner_type inference from entity names, decision-maker archetype, SOS worklist rows
workbook      openpyxl renderer for the 11-tab target-list workbook

Nothing in this package performs network I/O. All dates are computed relative to an explicit
`as_of` date (default: date.today()), never a hardcoded date.
"""

__version__ = "2.0.0"
