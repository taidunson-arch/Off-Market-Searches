import json
import sqlite3
from contextlib import closing
from unittest.mock import patch

from plb.book_model import build_model, cents, migrate
from plb.operations import connect, import_run, change_case
from inspect_instrument import inspect


def leads():
    return [{"property_id": "p", "instruments_json": json.dumps([
        {"instrument_id": "loan:1", "book_kind": "loan", "agency_loan_ids": "1", "public_upb": "100.01", "our_maturity": "2030-01-01", "affordability_end": "2040-01-01"},
        {"instrument_id": "grant:1", "book_kind": "grant", "grant_ids": "1", "recapture_type": "recapture", "recapture_end": "2035-01-01"},
        {"instrument_id": "administered_contract:1", "book_kind": "administered_contract", "contract_ids": "1", "contract_expiration": "2031-01-01"}])}]


def event(iid="loan:1", **kw):
    return dict({"property_id": "p", "instrument_id": iid, "event_id": iid + ":inspection", "event_type": "INSPECTION_DUE",
                 "event_family": "AGENCY_DEADLINE", "event_date": "2027-01-01", "source": "servicing", "status": "OPEN"}, **kw)


def rejects(fn):
    try:
        fn()
    except (ValueError, sqlite3.IntegrityError):
        return
    raise AssertionError("invalid input accepted")


def test_book_model_distinct_instruments_same_day_and_trace():
    with closing(connect(":memory:")) as db:
        import_run(db, {"run_id": "r", "as_of_date": "2026-10-04"}, leads(), [event(), event("grant:1")], [])
        assert db.execute("SELECT count(*) FROM cases").fetchone()[0] == 2
        trace = inspect(db, "r", "loan:1")
        assert trace["instrument"]["principal_minor"] == 10001
        assert len(trace["covenants"]) == 3
        assert len(trace["events"]) == len(trace["evidence"]) == len(trace["actions"]) == 1
        assert trace["actions"][0]["covenant_id"] in {c["covenant_id"] for c in trace["covenants"]}
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []
        rejects(lambda: db.execute("DELETE FROM model_events"))


def test_book_model_evidence_fanout_and_stable_workflow():
    with closing(connect(":memory:")) as db:
        import_run(db, {"run_id": "r1", "as_of_date": "2026-10-04"}, leads(), [event(), event(source="reviewed_tape", detail="updated source note")], [])
        trace = inspect(db, "r1", "loan:1")
        assert len(trace["events"]) == 1 and len(trace["evidence"]) == 2
        cid = trace["actions"][0]["case_id"]
        change_case(db, cid, "manager", 1, "cancel", evidence="duplicate inspection")
        import_run(db, {"run_id": "r2", "as_of_date": "2026-10-05"}, leads(), [event(detail="changed note")], [])
        assert inspect(db, "r2", "loan:1")["actions"][0]["current_status"] == "CANCELLED"
        assert db.execute("SELECT count(*) FROM cases").fetchone()[0] == 1


def test_book_model_rejects_orphans_wrong_property_and_invalid_money():
    with closing(connect(":memory:")) as db:
        for bad in (event("loan:missing"), event(property_id="other")):
            population = leads() + [{"property_id": "other"}]
            rejects(lambda: import_run(db, {"run_id": "bad", "as_of_date": "2026-10-04"}, population, [bad], []))
            assert db.execute("SELECT count(*) FROM runs").fetchone()[0] == 0
    for raw in ("1.001", "NaN", "-1", "Infinity", "x"):
        rejects(lambda: cents(raw))
    assert cents("") is None and cents("0") == 0


def test_book_model_unscoped_and_terminal_events():
    graph = build_model(leads(), [event(""), event(status="COMPLETED"), event("grant:1", event_date="")])
    assert len(graph["actions"]) == 1 and graph["actions"][0]["instrument_id"] is None
    assert len(graph["linkage_issues"]) == 1
    assert all(p["verification"] == "unverified_source_observation" for p in graph["evidence"])


def test_book_model_legacy_migration_preserves_case_and_audit():
    # Create the actual pre-model schema, then seed an old immutable snapshot.
    with patch("plb.book_model.migrate"), closing(connect(":memory:")) as db:
        manifest = {"run_id": "old", "as_of_date": "2026-10-04"}
        db.execute("INSERT INTO runs VALUES(?,?,?)", ("old", "2026-10-04", json.dumps(manifest)))
        db.execute("INSERT INTO properties VALUES(?,?,?)", ("old", "p", json.dumps(leads()[0])))
        db.execute("INSERT INTO evidence VALUES(?,?,?,?)", ("old", "e", "p", json.dumps(event())))
        db.execute("INSERT INTO cases(case_id,property_id,event_type,due_date,status,source_run) VALUES('legacy','p','INSPECTION_DUE','2027-01-01','CLOSED','old')")
        db.execute("INSERT INTO audit(case_id,actor,operation,at,detail) VALUES('legacy','reviewer','APPROVE','2026-10-04','{}')")
        db.commit()
        migrate(db)
        migrate(db)
        assert inspect(db, "old", "loan:1")["actions"][0]["case_id"] == "legacy"
        assert inspect(db, "old", "loan:1")["actions"][0]["current_status"] == "CLOSED"
        assert db.execute("SELECT count(*) FROM audit").fetchone()[0] == 1


def test_book_model_two_loans_same_day_cannot_cross_link_actions():
    population = leads()
    positions = json.loads(population[0]["instruments_json"])
    positions.append(dict(positions[0], instrument_id="loan:2", agency_loan_ids="2"))
    population[0]["instruments_json"] = json.dumps(positions)
    with closing(connect(":memory:")) as db:
        import_run(db, {"run_id": "r", "as_of_date": "2026-10-04"}, population, [event(), event("loan:2")], [])
        one, two = inspect(db, "r", "loan:1"), inspect(db, "r", "loan:2")
        assert one["actions"][0]["case_id"] != two["actions"][0]["case_id"]
        rejects(lambda: db.execute("INSERT INTO model_action_events VALUES(?,?,?,?,?)",
            ("r", one["actions"][0]["action_id"], two["events"][0]["event_id"], "p", "triggered_by")))


def test_book_model_ambiguous_legacy_case_is_not_guessed():
    with patch("plb.book_model.migrate"), closing(connect(":memory:")) as db:
        db.execute("INSERT INTO runs VALUES('old','2026-10-04','{}')")
        db.execute("INSERT INTO properties VALUES(?,?,?)", ("old", "p", json.dumps(leads()[0])))
        for iid in ("loan:1", "grant:1"):
            db.execute("INSERT INTO evidence VALUES(?,?,?,?)", ("old", iid, "p", json.dumps(event(iid))))
        db.execute("INSERT INTO cases(case_id,property_id,event_type,due_date,status,source_run) VALUES('legacy','p','INSPECTION_DUE','2027-01-01','CLOSED','old')")
        db.commit()
        migrate(db)
        assert db.execute("SELECT count(*) FROM model_actions WHERE case_id IS NULL").fetchone()[0] == 2
        assert db.execute("SELECT count(*) FROM model_linkage_issues").fetchone()[0] == 2
        assert db.execute("SELECT status FROM cases WHERE case_id='legacy'").fetchone()[0] == "CLOSED"


def test_book_model_bad_legacy_snapshot_rolls_back_migration():
    with patch("plb.book_model.migrate"), closing(connect(":memory:")) as db:
        db.execute("INSERT INTO runs VALUES('old','2026-10-04','{}')")
        db.execute("INSERT INTO properties VALUES(?,?,?)", ("old", "p", json.dumps(leads()[0])))
        db.execute("INSERT INTO evidence VALUES(?,?,?,?)", ("old", "bad", "p", json.dumps(event("loan:missing"))))
        db.commit()
        rejects(lambda: migrate(db))
        assert db.execute("SELECT count(*) FROM runs").fetchone()[0] == 1
        assert not db.execute("SELECT 1 FROM sqlite_master WHERE name='schema_migrations'").fetchone()
