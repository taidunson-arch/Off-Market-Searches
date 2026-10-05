import json
import sqlite3
import tempfile
from contextlib import closing
from datetime import date
from pathlib import Path
from plb.operations import connect, import_run, change_case, list_cases
from plb.risk_dimensions import assess, financial_observations


def snapshot(db, run_id):
    import_run(db, {"run_id": run_id, "as_of_date": "2026-10-04"}, [{"property_id": "p"}], [],
               [{"property_id": "p", "agency_action_type": "INSPECTION_DUE", "due_date": "2025-01-01"}])


def rejects(fn):
    try:
        fn()
    except (ValueError, sqlite3.IntegrityError):
        return
    raise AssertionError("invalid operation accepted")


def test_case_lifecycle_independent_approval_and_reimport():
    with tempfile.TemporaryDirectory() as d, closing(connect(Path(d)/"agency.db")) as db:
        snapshot(db, "r1")
        case = list_cases(db, date(2026,10,4))[0]
        cid = case["case_id"]
        assert case["overdue_days"] > 365
        change_case(db, cid, "supervisor", 1, "assign", "officer")
        rejects(lambda: change_case(db, cid, "officer", 1, "start"))
        change_case(db, cid, "officer", 2, "start")
        rejects(lambda: change_case(db, cid, "officer", 3, "submit"))
        change_case(db, cid, "officer", 3, "submit", evidence="file:inspection-123")
        rejects(lambda: change_case(db, cid, "officer", 4, "approve", evidence="review"))
        change_case(db, cid, "supervisor", 4, "approve", evidence="file:approval-456")
        snapshot(db, "r2")
        assert list_cases(db, date(2026,10,4)) == []
        assert len(list_cases(db, date(2026,10,4), True)) == 1
        rejects(lambda: db.execute("DELETE FROM audit"))
        db.rollback()
        change_case(db, cid, "supervisor", 5, "reopen", evidence="inspection disputed")
        assert list_cases(db, date(2026,10,4))[0]["status"] == "OPEN"


def test_snapshot_import_rolls_back_on_conflicting_instrument():
    with tempfile.TemporaryDirectory() as d, closing(connect(Path(d)/"agency.db")) as db:
        pos=json.dumps([{"instrument_id":"loan:1"}])
        rejects(lambda: import_run(db, {"run_id":"r", "as_of_date":"2026-10-04"},
                                   [{"property_id":"p1","instruments_json":pos}, {"property_id":"p2","instruments_json":pos}], [], []))
        assert db.execute("SELECT count(*) FROM runs").fetchone()[0] == 0
        assert db.execute("SELECT count(*) FROM instruments").fetchone()[0] == 0


def test_risk_dimensions_do_not_infer_financial_health_from_long_restrictions():
    lead={"property_id":"p", "owner_cliff_band":"BEYOND", "covenant_status":"current"}
    as_of=date(2026,10,4)
    assert assess(lead,None,as_of)["financial_risk"] == "UNKNOWN"
    policy={"version":"agency-test-v1","min_dscr":1.1,"max_days_past_due":30,"min_occupancy":0.9,"min_reserve_funded_ratio":1}
    observation={"period_end":"2026-09-30","dscr":0.7,"days_past_due":60,"occupancy":0.8,"reserve_funded_ratio":0.4}
    r=assess(lead,observation,as_of,policy)
    assert r["preservation_urgency"] == "BEYOND" and r["financial_risk"] == "WATCH"
    assert "dscr" in r["financial_reasons"]
    assert assess(lead,dict(observation,dscr=1.5,days_past_due=0,occupancy=0.98,reserve_funded_ratio=1),as_of,policy)["financial_risk"] == "NO_CONFIGURED_BREACH"
    assert assess(lead,dict(observation,period_end="2024-09-30",dscr=1.5,days_past_due=0,occupancy=0.98,reserve_funded_ratio=1),as_of,policy)["financial_risk"] == "UNKNOWN"


def test_financial_observations_keep_history_without_future_leakage():
    rows=[{"property_id":"p","period_end":d,"source":"statement","dscr":v} for d,v in (("2026-06-30",0.8),("2026-09-30",1.2),("2027-03-31",1.5))]
    latest,history=financial_observations(rows,date(2026,10,4))
    assert latest["p"]["dscr"] == 1.2 and len(history)==3
    rejects(lambda: financial_observations([dict(rows[0],occupancy=80)],date(2026,10,4)))
    rejects(lambda: financial_observations(rows+[dict(rows[0],dscr=2)],date(2026,10,4)))
