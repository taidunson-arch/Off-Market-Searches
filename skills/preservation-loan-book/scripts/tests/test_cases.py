import json
import sqlite3
import subprocess
import sys
import tempfile
from contextlib import closing
from datetime import date
from pathlib import Path
from unittest.mock import patch

from plb.operations import connect, import_run, change_case, list_cases
from plb.cases import create, detail, migrate
from inspect_instrument import inspect


def setup(db):
    import_run(db, {"run_id": "r", "as_of_date": "2026-10-04"}, [{"property_id": "p", "instruments_json": json.dumps([
        {"instrument_id": "loan:1", "book_kind": "loan", "agency_loan_ids": "1"}])}], [], [])
    return create(db, run_id="r", property_id="p", instrument_id="loan:1", title="Review reserve shortfall",
                  due_date="2026-11-01", owner="Alex Officer", actor="Sam Manager")


def rejects(fn):
    try:
        fn()
    except (ValueError, sqlite3.IntegrityError):
        return
    raise AssertionError("invalid operation accepted")


def test_cases_persist_deadline_owner_evidence_approval_and_history():
    with tempfile.TemporaryDirectory() as root:
        path = Path(root)/"cases.sqlite"
        with closing(connect(path)) as db:
            cid = setup(db)
            change_case(db, cid, "Sam Manager", 1, "reschedule", "2026-11-15", "Borrower extension approved")
            change_case(db, cid, "Alex Officer", 2, "start")
            change_case(db, cid, "Alex Officer", 3, "submit", evidence="dms://reserve-review/1")
            rejects(lambda: change_case(db, cid, " alex   officer ", 4, "approve", evidence="self review"))
            change_case(db, cid, "Sam Manager", 4, "approve", evidence="dms://approval/1")
        with closing(connect(path)) as db:
            record = detail(db, cid)
            assert inspect(db, "r", "loan:1")["manual_cases"][0]["case_id"] == cid
            assert record["case"]["status"] == "CLOSED" and record["case"]["completed_at"]
            assert record["case"]["original_due_date"] == "2026-11-01"
            assert record["case"]["due_date"] == "2026-11-15"
            assert len(record["evidence"]) == 2 and len(record["decisions"]) == 1
            assert record["decisions"][0]["submitted_version"] == 4
            assert len(record["history"]) == 5 and record["scope"][0]["instrument_id"] == "loan:1"
            assert db.execute("PRAGMA foreign_key_check").fetchall() == []


@patch("plb.cases.now", new=lambda: "2026-10-04T00:00:00+00:00")
def test_cases_rejection_resubmission_and_reopen_keep_evidence():
    with closing(connect(":memory:")) as db:
        cid = setup(db)
        rejects(lambda: change_case(db, cid, "Other Officer", 1, "submit", evidence="dms://wrong-owner"))
        change_case(db, cid, "Alex Officer", 1, "submit", evidence="dms://draft")
        rejects(lambda: change_case(db, cid, "Sam Manager", 2, "reschedule", "2026-12-01", "extension"))
        change_case(db, cid, "Sam Manager", 2, "reject", evidence="Missing signed statement")
        change_case(db, cid, "Alex Officer", 3, "submit", evidence="dms://signed")
        change_case(db, cid, "Sam Manager", 4, "approve", evidence="dms://approval")
        change_case(db, cid, "Sam Manager", 5, "reopen", evidence="New bank discrepancy")
        record = detail(db, cid)
        assert record["case"]["status"] == "OPEN" and not record["case"]["completed_at"]
        assert [d["decision"] for d in record["decisions"]] == ["REJECTED", "APPROVED"]
        assert len(record["evidence"]) == 4 and len(record["history"]) == 6
        assert record["decisions"][0]["completion_evidence_id"] != record["decisions"][1]["completion_evidence_id"]


def test_cases_escalation_recipient_and_resolution_are_audited():
    with closing(connect(":memory:")) as db:
        cid = setup(db)
        rejects(lambda: change_case(db, cid, "Alex Officer", 1, "escalate", evidence="No response"))
        change_case(db, cid, "Alex Officer", 1, "escalate", "Pat Director", "Borrower nonresponse")
        rows = list_cases(db, date(2026,12,1), escalated_to="pat director", owner="Alex Officer")
        assert len(rows) == 1 and rows[0]["overdue_days"] == 30 and rows[0]["escalated_at"]
        change_case(db, cid, "Pat Director", 2, "deescalate", evidence="Response received")
        assert list_cases(db, date(2026,12,1), escalated_to="Pat Director") == []
        assert detail(db, cid)["history"][-1]["detail"]["before"]["escalation_reason"] == "Borrower nonresponse"


def test_cases_stale_connection_and_failed_changes_have_no_side_effects():
    with tempfile.TemporaryDirectory() as root:
        path = Path(root)/"cases.sqlite"
        with closing(connect(path)) as first, closing(connect(path)) as second:
            cid = setup(first)
            change_case(first, cid, "Sam Manager", 1, "assign", "New Officer")
            rejects(lambda: change_case(second, cid, "Alex Officer", 1, "submit", evidence="dms://stale"))
            rejects(lambda: change_case(second, cid, "Sam Manager", 2, "reschedule", "bad-date", "extension"))
            record = detail(first, cid)
            assert len(record["history"]) == 2 and not record["evidence"] and record["case"]["version"] == 2


def test_cases_evidence_and_decisions_are_append_only_and_scope_checked():
    with closing(connect(":memory:")) as db:
        cid = setup(db)
        change_case(db, cid, "Alex Officer", 1, "submit", evidence="dms://completion")
        change_case(db, cid, "Sam Manager", 2, "approve", evidence="dms://approval")
        for table in ("case_evidence", "case_decisions", "case_scope"):
            rejects(lambda: db.execute(f"DELETE FROM {table}"))
            db.rollback()
        count = db.execute("SELECT count(*) FROM cases").fetchone()[0]
        rejects(lambda: create(db, run_id="r", property_id="p", instrument_id="loan:missing", title="Bad", due_date="2026-11-01", owner="Alex", actor="Sam"))
        assert db.execute("SELECT count(*) FROM cases").fetchone()[0] == count


def test_cases_legacy_migration_retains_pending_submission_and_audit():
    with patch("plb.cases.migrate"), closing(connect(":memory:")) as db:
        db.execute("INSERT INTO runs VALUES('old','2026-10-04','{}')")
        db.execute("INSERT INTO cases(case_id,property_id,event_type,due_date,status,assigned_to,evidence,submitted_by,source_run) VALUES('legacy','p','INSPECTION_DUE','2026-11-01','PENDING_APPROVAL','Alex','file:legacy','Alex','old')")
        db.commit()
        migrate(db)
        migrate(db)
        assert detail(db, "legacy")["evidence"][0]["origin"] == "legacy_import"
        change_case(db, "legacy", "Sam", 1, "approve", evidence="dms://review")
        assert detail(db, "legacy")["case"]["status"] == "CLOSED"


def test_cases_cli_create_show_and_filter():
    with tempfile.TemporaryDirectory() as root:
        path = Path(root)/"cases.sqlite"
        with closing(connect(path)) as db:
            cid = setup(db)
        cli = Path(__file__).resolve().parents[1]/"manage_cases.py"
        result = subprocess.run([sys.executable, str(cli), "--db", str(path), "show", cid], capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)["case"]["title"] == "Review reserve shortfall"
        result = subprocess.run([sys.executable, str(cli), "--db", str(path), "list", "--as-of", "2026-12-01", "--owner", "Alex Officer", "--due-by", "2026-11-15"], capture_output=True, text=True)
        assert result.returncode == 0 and len(json.loads(result.stdout)) == 1
        result = subprocess.run([sys.executable, str(cli), "--db", str(path), "create", "--run-id", "r", "--property-id", "p",
            "--instrument-id", "loan:1", "--title", "Review cure plan", "--due-date", "2026-12-01", "--owner", "Pat", "--actor", "Sam"], capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)["scope"][0]["instrument_id"] == "loan:1"


def test_cases_reimport_preserves_working_due_date_and_original_obligation():
    with closing(connect(":memory:")) as db:
        population = [{"property_id": "p"}]
        calendar = [{"property_id": "p", "agency_action_type": "INSPECTION_DUE", "due_date": "2026-11-01"}]
        import_run(db, {"run_id": "r1", "as_of_date": "2026-10-04"}, population, [], calendar)
        row = list_cases(db, date(2026,10,4))[0]
        assert row["unassigned"] and row["created_at"]
        change_case(db, row["case_id"], "Sam", 1, "assign", "Alex")
        change_case(db, row["case_id"], "Sam", 2, "reschedule", "2026-11-15", "Internal follow-up extension")
        import_run(db, {"run_id": "r2", "as_of_date": "2026-10-05"}, population, [], calendar)
        record = detail(db, row["case_id"])
        assert record["case"]["due_date"] == "2026-11-15" and record["case"]["original_due_date"] == "2026-11-01"
        assert len(record["actions"]) == 2 and {a["due_date"] for a in record["actions"]} == {"2026-11-01"}
        assert len(list_cases(db, date(2026,10,5))) == 1


def test_cases_attachment_priority_and_cancellation_preserve_record():
    with closing(connect(":memory:")) as db:
        cid = setup(db)
        change_case(db, cid, "Alex Officer", 1, "attach", "Bank statement", "dms://bank/1")
        rejects(lambda: change_case(db, cid, "Sam Manager", 2, "priority", "URGENT"))
        change_case(db, cid, "Sam Manager", 2, "priority", "URGENT", "Reserve balance exhausted")
        change_case(db, cid, "Sam Manager", 3, "cancel", evidence="Case superseded by workout plan")
        rejects(lambda: change_case(db, cid, "Sam Manager", 4, "reschedule", "2026-12-01", "extension"))
        change_case(db, cid, "Sam Manager", 4, "note", evidence="See linked workout case")
        record = detail(db, cid)
        assert record["case"]["status"] == "CANCELLED" and record["case"]["priority"] == "URGENT"
        assert [e["purpose"] for e in record["evidence"]] == ["attach", "note"]
        assert record["evidence"][0]["note"] == "Bank statement"
        assert not record["case"]["completed_at"] and not record["decisions"]
