"""Shared fixture runs for the test suite (not discovered by run_tests.py: no test_ prefix).

`hfa_fixture_run()` builds the hfa universe from the fixture OHCS inventory + the synthetic servicing extract (crosswalk,
REAC, forecast) and scores it once per test session; `real_run()` does the same against the real OHCS inventory when the
file is present (skipped otherwise). Both return dicts of DataFrames / JSON keyed by output name.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from typing import Any, Dict

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
PACK = os.path.normpath(os.path.join(SCRIPTS, "..", "references", "sources", "oregon-portland"))
FX = os.path.join(HERE, "fixtures")
REAL = os.environ.get("OHCS_CSV", "/tmp/claude-0/-home-user/7bb5c89e-a260-588a-815c-3462cdc087de/scratchpad/d/Oregon_Affordable_Housing_Inventory_20261002.csv")
AS_OF = "2026-10-04"
_CACHE: Dict[str, Dict[str, Any]] = {}


def run(cmd, cwd=SCRIPTS):
    p = subprocess.run([sys.executable, *cmd], capture_output=True, text=True, cwd=cwd)
    assert p.returncode == 0, f"{cmd[0]} failed rc={p.returncode}\n{p.stderr[-4000:]}"
    return p


def _load(out: str) -> Dict[str, Any]:
    def csv(name):
        path = os.path.join(out, name)
        return pd.read_csv(path, dtype=str, keep_default_na=False) if os.path.exists(path) else None

    res = {"dir": out, "leads": csv("leads.csv"), "events": csv("events.csv"), "rejects": csv("rejects.csv"), "merge_log": csv("merge_log.csv"),
           "unmatched": csv("servicing_unmatched.csv"), "gaps": csv("book_join_gaps.csv"), "scored": csv("leads_scored.csv"),
           "notice": csv("notice_compliance_queue.csv"), "agency_calendar": csv("agency_calendar.csv"), "nofa": csv("nofa_targets.csv"),
           "cal": json.load(open(os.path.join(out, "calendar_summary.json"))) if os.path.exists(os.path.join(out, "calendar_summary.json")) else {},
           "uar": json.load(open(os.path.join(out, "units_at_risk.json"))) if os.path.exists(os.path.join(out, "units_at_risk.json")) else {}}
    return res


def hfa_fixture_run(profile: str = "hfa", book: str = "agency_servicing_sample.csv", coverage: str = "full", extra=()) -> Dict[str, Any]:
    key = f"{profile}|{book}|{coverage}|{'|'.join(extra)}"
    if key in _CACHE:
        return _CACHE[key]
    out = tempfile.mkdtemp(prefix=f"plb_fx_{profile}_")
    cmd = [os.path.join(SCRIPTS, "build_universe.py"), "--pack", PACK, "--mode", "metro_core", "--agency-profile", profile, "--ohcs", os.path.join(FX, "ohcs_sample.csv"),
           "--book", os.path.join(FX, book), "--book-coverage", coverage, "--crosswalk", os.path.join(FX, "book_crosswalk_sample.csv"),
           "--reac", os.path.join(FX, "reac_scores_sample.csv"), "--horizon-years", "10", "--as-of", AS_OF, "--out-dir", out, *extra]
    run(cmd)
    run([os.path.join(SCRIPTS, "score_preservation.py"), "--leads", os.path.join(out, "leads.csv"), "--events", os.path.join(out, "events.csv"), "--pack", PACK,
         "--agency-profile", profile, "--as-of", AS_OF, "--out", os.path.join(out, "leads_scored.csv")])
    _CACHE[key] = _load(out)
    return _CACHE[key]


def real_available() -> bool:
    return os.path.exists(REAL)


def real_run(horizon: str = "10") -> Dict[str, Any]:
    key = f"real|{horizon}"
    if key in _CACHE:
        return _CACHE[key]
    out = tempfile.mkdtemp(prefix="plb_real_")
    run([os.path.join(SCRIPTS, "build_universe.py"), "--pack", PACK, "--mode", "metro_core", "--agency-profile", "hfa", "--ohcs", REAL,
         "--book", os.path.join(FX, "agency_servicing_sample.csv"), "--crosswalk", os.path.join(FX, "book_crosswalk_sample.csv"),
         "--horizon-years", horizon, "--as-of", AS_OF, "--out-dir", out])
    run([os.path.join(SCRIPTS, "score_preservation.py"), "--leads", os.path.join(out, "leads.csv"), "--events", os.path.join(out, "events.csv"), "--pack", PACK,
         "--agency-profile", "hfa", "--horizon-years", horizon, "--as-of", AS_OF, "--out", os.path.join(out, "leads_scored.csv")])
    _CACHE[key] = _load(out)
    return _CACHE[key]


def by_name(df: pd.DataFrame, name: str) -> Dict[str, Any]:
    rows = df[df["property_name"].str.upper() == name.upper()]
    assert len(rows) >= 1, f"{name} not in frame"
    return rows.iloc[0].to_dict()
