#!/usr/bin/env python3
"""Profile the date columns of a CSV/XLSX for day-first vs month-first before declaring formats.

For each column with >= 5 values matching `^\\d{1,2}/\\d{1,2}/\\d{4}$` or `^\\d{4} \\w{3} \\d{1,2} `
print: rows, count with first field > 12, count with second field > 12, the proposed strptime
format (`%d/%m/%Y` if only the first field ever exceeds 12; `%m/%d/%Y` if only the second;
`auto` when both or neither do) and a ready-to-paste YAML snippet for dataset-schemas.yaml.

Expected on the OHCS inventory: Financial_Closing_Date -> %d/%m/%Y (222/0);
LATEST_Expiration_Date -> %m/%d/%Y (0/764); USDA_RD_Expiration_Date -> %Y %b %d %I:%M:%S %p.

Usage:
  python scripts/date_profile.py <file> [--sheet NAME] [--encoding utf-8-sig] [--yaml-only]
Exit code is always 0; this tool informs, it does not decide.
"""
from __future__ import annotations

import argparse
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plb.dates import profile_series  # noqa: E402


def load(path: str, sheet: str | None, encoding: str) -> pd.DataFrame:
    if path.lower().endswith((".xlsx", ".xlsm", ".xls")):
        return pd.read_excel(path, sheet_name=sheet or 0, dtype=str)
    return pd.read_csv(path, dtype=str, encoding=encoding, keep_default_na=False)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--sheet", default=None, help="worksheet name for Excel inputs")
    ap.add_argument("--encoding", default="utf-8-sig")
    ap.add_argument("--yaml-only", action="store_true", help="print only the YAML snippet")
    a = ap.parse_args(argv)

    df = load(a.file, a.sheet, a.encoding)
    results = []
    for col in df.columns:
        prof = profile_series(df[col].replace("", pd.NA))
        if prof:
            results.append((col, prof))
    if not results:
        print("no date-like columns found (need >= 5 values per column)")
        return 0
    if not a.yaml_only:
        print(f"{'column':<32}{'rows':>6}{'first>12':>10}{'second>12':>11}  proposed_format")
        for col, p in results:
            print(f"{col:<32}{p['rows']:>6}{p['first_gt12']:>10}{p['second_gt12']:>11}  {p['proposed_format']}")
        print()
        amb = [c for c, p in results if p["proposed_format"] == "auto"]
        if amb:
            print("Columns proposed as `auto` could not be disambiguated by the data; confirm with the publisher's")
            print("data dictionary or declare the format by hand. `auto` runs per-value detection and flags")
            print("every both-fields-<=12 value `Verify — Ambiguous`:", ", ".join(amb))
            print()
        print("YAML snippet for dataset-schemas.yaml -> dates:")
    for col, p in results:
        print(f"    {col}: {{format: \"{p['proposed_format']}\", basis: REPORTED}}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
