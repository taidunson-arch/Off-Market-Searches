"""pipeline-contract.md is the source of truth for the event taxonomy: parse its Section 3 table and compare family /
direction with omdf.schema.EVENT_TAXONOMY, and check the events.csv column list in Section 6 against EVENT_COLUMNS."""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from omdf.schema import EVENT_COLUMNS, EVENT_TAXONOMY  # noqa: E402

CONTRACT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "references", "pipeline-contract.md"))


def _parse_contract_events():
    text = open(CONTRACT, encoding="utf-8").read()
    sec = text.split("## 3. Event taxonomy", 1)[1].split("## 4.", 1)[0]
    rows = {}
    for line in sec.splitlines():
        if not line.startswith("| ") or line.startswith("| event_type") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        et, fam_cell = cells[0], cells[1]
        m = re.match(r"([A-Z_]+)(?:\s*\((PRESSURE|SUPPRESSION|ROUTING)\))?", fam_cell)
        if not m:
            continue
        rows[et] = {"family": m.group(1), "direction": m.group(2) or "PRESSURE"}
    return rows


def test_contract_table_matches_schema_taxonomy():
    rows = _parse_contract_events()
    assert len(rows) >= 60
    missing_in_code = sorted(set(rows) - set(EVENT_TAXONOMY))
    missing_in_contract = sorted(set(EVENT_TAXONOMY) - set(rows))
    assert not missing_in_code, f"in contract but not in schema.py: {missing_in_code}"
    assert not missing_in_contract, f"in schema.py but not in contract: {missing_in_contract}"
    drift = {et: (rows[et], EVENT_TAXONOMY[et]) for et in rows if rows[et] != EVENT_TAXONOMY[et]}
    assert not drift, f"family/direction drift: {drift}"


def test_contract_events_csv_columns_match_schema():
    text = open(CONTRACT, encoding="utf-8").read()
    sec = text.split("## 6. Companion events table", 1)[1].split("## 7.", 1)[0]
    m = re.search(r"Columns: `([^`]+)`", sec)
    assert m, "Section 6 must list the columns in a backticked comma list"
    cols = [c.strip() for c in m.group(1).split(",")]
    assert cols == EVENT_COLUMNS, f"contract {cols} != schema {EVENT_COLUMNS}"
