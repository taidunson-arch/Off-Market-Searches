"""references/pipeline-contract.md is the source of truth: Section 3 (event taxonomy) must equal plb.schema.EVENT_TAXONOMY and
Section 6 (events.csv columns) must equal EVENT_COLUMNS. Section 1 enums must list the eight routes in precedence order."""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from plb.schema import AGENCY_PROFILES, EVENT_COLUMNS, EVENT_TAXONOMY, LEAD_COLUMNS, QUEUE_BANDS, ROUTES  # noqa: E402

CONTRACT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "references", "pipeline-contract.md"))


def _text() -> str:
    return open(CONTRACT, encoding="utf-8").read()


def _parse_contract_events():
    sec = _text().split("## 3. Event taxonomy", 1)[1].split("\n## 4.", 1)[0]
    rows = {}
    for line in sec.splitlines():
        if not line.startswith("| ") or line.startswith("| event_type") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        m0 = re.match(r"`?([A-Z][A-Z_0-9]+)`?", cells[0])
        m = re.match(r"`?([A-Z_]+)`?(?:\s*\((PRESSURE|SUPPRESSION|ROUTING)\))?", cells[1])
        if not (m0 and m):
            continue
        rows[m0.group(1)] = {"family": m.group(1), "direction": m.group(2) or "PRESSURE"}
    return rows


def test_contract_table_matches_schema_taxonomy():
    rows = _parse_contract_events()
    assert len(rows) >= 45
    missing_in_code = sorted(set(rows) - set(EVENT_TAXONOMY))
    missing_in_contract = sorted(set(EVENT_TAXONOMY) - set(rows))
    assert not missing_in_code, f"in contract but not in schema.py: {missing_in_code}"
    assert not missing_in_contract, f"in schema.py but not in contract: {missing_in_contract}"
    drift = {et: (rows[et], EVENT_TAXONOMY[et]) for et in rows if rows[et] != EVENT_TAXONOMY[et]}
    assert not drift, f"family/direction drift: {drift}"


def test_contract_events_csv_columns_match_schema():
    sec = _text().split("## 6.", 1)[1].split("\n## 7.", 1)[0]
    m = re.search(r"`(event_id,[^`]+)`", sec)
    assert m, "Section 6 must list the columns in a backticked comma list"
    cols = [c.strip() for c in m.group(1).split(",")]
    assert cols == EVENT_COLUMNS, f"contract {cols} != schema {EVENT_COLUMNS}"


def test_contract_names_the_eight_routes_and_profiles():
    text = _text()
    for r in ROUTES:
        assert f"`{r}`" in text or r in text, f"route {r} missing from the contract"
    for p in AGENCY_PROFILES:
        assert p in text
    for q in QUEUE_BANDS:
        assert q in text
    assert ROUTES == ["optout_response", "notice_compliance", "qc_admin", "designee_rofr", "recap_committee", "servicing_watch", "nofa_offer", "ta_sponsor"]
    # no buyer-side vocabulary survives in the shared enums
    for banned in ("acquisition", "partnership_preservation", "lender_counterparty", "assumption_play", "buyer_profile", "motivation_score", "outreach_template"):
        assert banned not in LEAD_COLUMNS and banned not in ROUTES
