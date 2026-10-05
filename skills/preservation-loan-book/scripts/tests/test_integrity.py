"""Adversarial regressions for agency book calculations and publication boundaries."""
import json
import os
import tempfile
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from plb.adapters import blank_lead
from plb.agency_calendar import agency_action, owner_cliff
from plb.instruments import collect_instruments
from plb.schema import EVENT_COLUMNS
from plb.units import fill_units_block, units_at_risk_json
from merge_leads import merge
import run_agency_pipeline as pipeline

AS_OF = date(2026, 10, 4)


def test_integrity_book_verdict_invariant_to_outside_inventory():
    book = blank_lead(property_id="book", universe="our_book", book_match="matched", units_at_risk=10,
                      owner_cliff_date="2027-01-01", owner_cliff_band="CRITICAL", public_upb=0)
    outside = blank_lead(property_id="outside", universe="universe_not_held", book_match="not_in_book", units_at_risk=990,
                         owner_cliff_date="2035-01-01", owner_cliff_band="SCHEDULED")
    one = units_at_risk_json(pd.DataFrame([book]), AS_OF)
    both = units_at_risk_json(pd.DataFrame([book, outside]), AS_OF)
    assert one["book_verdict"] == both["book_verdict"] == "CRITICAL"
    assert one["book_coverage"] == both["book_coverage"]
    assert units_at_risk_json(pd.DataFrame([outside]), AS_OF)["book_verdict"] == "INSUFFICIENT_DATA"
    assert units_at_risk_json(pd.DataFrame(), AS_OF)["book_verdict"] == "INSUFFICIENT_DATA"


def test_integrity_missing_book_data_is_not_healthy():
    row = blank_lead(property_id="p", universe="our_book", book_match="matched", book_kind="loan", units_at_risk=10)
    result = units_at_risk_json(pd.DataFrame([row]), AS_OF)
    assert result["book_verdict"] == "INSUFFICIENT_DATA"
    assert len(result["book_coverage"]["data_gaps"]) == 2


def grants():
    return [blank_lead(property_id="p", property_name="Test", address="1 Main", zip="97201", universe="our_book",
                       book_match="matched", book_kind="grant", grant_ids=gid, recapture_type="recapture",
                       recapture_method=method, recapture_amount=100000, recapture_start="2020-01-01", recapture_end="2030-01-01")
            for gid, method in (("g1", "full"), ("g2", "prorata_reducing"))]


def test_integrity_grant_aggregation_preserves_terms_and_roundtrip():
    expected = sum(fill_units_block(pd.DataFrame(grants()), AS_OF)["recapture_exposure"])
    assert expected == 132439
    for rows in (grants(), list(reversed(grants())), grants() + [grants()[0]]):
        merged = merge([pd.DataFrame(rows)], [pd.DataFrame(columns=EVENT_COLUMNS)], AS_OF, 10, 10, book_index=0)[0]
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "leads.csv")
            merged.to_csv(path, index=False)
            restored = pd.read_csv(path, dtype=str, keep_default_na=False)
            got = fill_units_block(restored, AS_OF).iloc[0]
        assert got["recapture_exposure"] == expected
        assert float(got["recapture_amount"]) == 200000
        assert len(json.loads(got["instruments_json"])) == 2
        assert got["recapture_method"] == "mixed"


def test_integrity_duplicate_instrument_conflicts_fail_closed():
    rows = grants()
    conflicting = dict(rows[0], recapture_amount=200000)
    try:
        collect_instruments([rows[0], conflicting])
    except ValueError as exc:
        assert "conflicting" in str(exc)
    else:
        raise AssertionError("conflicting instrument accepted")


def test_integrity_unknown_grant_component_does_not_become_zero():
    rows = grants()
    rows[1]["recapture_method"] = "cdbg_fmv_share"
    merged = merge([pd.DataFrame(rows)], [pd.DataFrame(columns=EVENT_COLUMNS)], AS_OF, 10, 10, book_index=0)[0]
    got = fill_units_block(merged, AS_OF).iloc[0]
    assert got["public_grant_at_risk"] == ""
    assert "FMV" in got["verify_flags"]


def test_integrity_overdue_owner_obligation_precedes_future_cliff():
    overdue = dict(event_type="AGENCY_LOAN_MATURITY", event_family="DEBT", event_date="2026-01-01", direction="PRESSURE", basis="RECORDED", status="OVERDUE")
    future = dict(event_type="LIHTC_EXTENDED_USE_END", event_family="REGULATORY", event_date="2035-01-01", direction="PRESSURE", basis="RECORDED", status="FUTURE")
    assert owner_cliff([overdue, future], AS_OF)["event_type"] == "AGENCY_LOAN_MATURITY"
    for status in ("RESOLVED", "SUPERSEDED", "COMPLETED", "CANCELLED"):
        assert owner_cliff([dict(overdue, status=status), future], AS_OF)["event_type"] == "LIHTC_EXTENDED_USE_END"


def test_integrity_overdue_action_retained_until_resolution():
    event = dict(event_type="ROFR_MATCH_DEADLINE", event_family="AGENCY_DEADLINE", event_date="2025-01-01", status="OVERDUE")
    assert agency_action([event], AS_OF)["date"] == date(2025, 1, 1)
    for status in ("RESOLVED", "SUPERSEDED", "COMPLETED", "CANCELLED", "SUPPRESSED"):
        assert agency_action([dict(event, status=status)], AS_OF) is None


def test_integrity_pipeline_subprocess_failure_raises():
    from types import SimpleNamespace
    with patch.object(pipeline.subprocess, "run", return_value=SimpleNamespace(returncode=7, stdout="", stderr="bad source")):
        try:
            pipeline.run_cmd(["python", "score_preservation.py"], [])
        except RuntimeError as exc:
            assert "rc=7" in str(exc)
        else:
            raise AssertionError("failed score did not stop pipeline")


def test_integrity_failed_rerun_never_publishes_stale_success():
    with tempfile.TemporaryDirectory() as d:
        cfg = Path(d)/"config.json"
        cfg.write_text(json.dumps(dict(out_dir=d, as_of_date="2026-10-04", pipeline_mode=True, pipeline_root=d, market_id="test")))
        seen = []
        def succeed(argv, run_dir, run_id):
            seen.append(run_dir)
            (Path(run_dir)/"result.json").write_text('{"fresh": true}')
        with patch.object(pipeline, "execute", side_effect=succeed):
            good = pipeline.main(["--config", str(cfg)])
        pointer = Path(d)/"2026-10-04/latest.json"
        before = pointer.read_bytes()
        def fail(argv, run_dir, run_id):
            assert run_dir != good
            assert not (Path(run_dir)/"result.json").exists()
            seen.append(run_dir)
            raise RuntimeError("workbook failure")
        with patch.object(pipeline, "execute", side_effect=fail):
            try:
                pipeline.main(["--config", str(cfg)])
            except RuntimeError:
                pass
            else:
                raise AssertionError("failure swallowed")
        assert pointer.read_bytes() == before
        assert json.loads((Path(seen[1])/"failure.json").read_text())["status"] == "FAILED"
        checkpoint = Path(d)/"data/status/test/asset_management/preservation-loan-book.json"
        assert json.loads(checkpoint.read_text())["status"] == "FAILED"


def test_integrity_partial_restart_rejected_before_artifact_reuse():
    with tempfile.TemporaryDirectory() as d:
        cfg = Path(d)/"config.json"
        cfg.write_text(json.dumps(dict(out_dir=d, as_of_date="2026-10-04")))
        try:
            pipeline.main(["--config", str(cfg), "--from", "score"])
        except ValueError as exc:
            assert "partial restarts" in str(exc)
        else:
            raise AssertionError("unverified resume accepted")


def test_integrity_missing_inventory_cannot_reuse_old_date_directory():
    with tempfile.TemporaryDirectory() as d:
        day = Path(d)/"2026-10-04"
        day.mkdir()
        (day/"leads_scored.csv").write_text("property_id,queue_band\np,ACT\n")
        cfg = Path(d)/"config.json"
        cfg.write_text(json.dumps(dict(out_dir=d, as_of_date="2026-10-04", local_datasets=[])))
        try:
            pipeline.main(["--config", str(cfg)])
        except ValueError as exc:
            assert "inventory" in str(exc)
        else:
            raise AssertionError("missing source accepted")
        assert not (day/"latest.json").exists()
        assert json.loads((day/"last_attempt.json").read_text())["status"] == "FAILED"


def test_integrity_calendar_reports_old_open_actions_and_excludes_closed():
    from query_calendar import summarize
    from plb.adapters import make_event
    events = [make_event("p", "ROFR_MATCH_DEADLINE", date(2024,1,1), "DERIVED", "test", AS_OF, "2026-10-04"),
              make_event("p", "INSPECTION_DUE", date(2024,2,1), "DERIVED", "test", AS_OF, "2026-10-04")]
    events[1]["status"] = "COMPLETED"
    _, report = summarize(pd.DataFrame(events), AS_OF, 10, 10)
    assert report["agency_act_by"] == 1
    assert report["agency_act_by_next_90_days"] == 0


def test_integrity_explicit_missing_book_is_an_error_not_inventory_only():
    with tempfile.TemporaryDirectory() as d:
        try:
            pipeline.discover({"servicing_extract": str(Path(d)/"missing.csv")}, {})
        except ValueError as exc:
            assert "configured input is missing" in str(exc)
        else:
            raise AssertionError("missing servicing extract silently ignored")
