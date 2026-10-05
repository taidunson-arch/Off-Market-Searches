"""Local HFA work queue and immutable run snapshots.

This is a single-agency SQLite store. Actor names are audit attribution, not
authentication; a multiuser service must supply authenticated identities.
"""
import hashlib
import json
import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path

from .instruments import parse_instruments


def connect(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript("""
        CREATE TABLE IF NOT EXISTS runs(run_id TEXT PRIMARY KEY, as_of TEXT NOT NULL, manifest TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS properties(run_id TEXT REFERENCES runs, property_id TEXT, payload TEXT NOT NULL,
            PRIMARY KEY(run_id, property_id));
        CREATE TABLE IF NOT EXISTS instruments(run_id TEXT REFERENCES runs, instrument_id TEXT, property_id TEXT,
            payload TEXT NOT NULL, PRIMARY KEY(run_id, instrument_id));
        CREATE TABLE IF NOT EXISTS covenants(run_id TEXT, instrument_id TEXT, covenant_status TEXT,
            affordability_end TEXT, recapture_end TEXT, PRIMARY KEY(run_id, instrument_id),
            FOREIGN KEY(run_id,instrument_id) REFERENCES instruments(run_id,instrument_id));
        CREATE TABLE IF NOT EXISTS evidence(run_id TEXT REFERENCES runs, event_id TEXT, property_id TEXT,
            payload TEXT NOT NULL, PRIMARY KEY(run_id, event_id));
        CREATE TABLE IF NOT EXISTS cases(case_id TEXT PRIMARY KEY, property_id TEXT NOT NULL, event_type TEXT NOT NULL,
            due_date TEXT NOT NULL, assigned_to TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'OPEN',
            version INTEGER NOT NULL DEFAULT 1, evidence TEXT NOT NULL DEFAULT '', submitted_by TEXT NOT NULL DEFAULT '',
            approved_by TEXT NOT NULL DEFAULT '', source_run TEXT NOT NULL REFERENCES runs);
        CREATE TABLE IF NOT EXISTS audit(seq INTEGER PRIMARY KEY AUTOINCREMENT, case_id TEXT NOT NULL REFERENCES cases,
            actor TEXT NOT NULL, operation TEXT NOT NULL, at TEXT NOT NULL, detail TEXT NOT NULL);
        CREATE TRIGGER IF NOT EXISTS audit_no_update BEFORE UPDATE ON audit BEGIN SELECT RAISE(ABORT,'append-only audit'); END;
        CREATE TRIGGER IF NOT EXISTS audit_no_delete BEFORE DELETE ON audit BEGIN SELECT RAISE(ABORT,'append-only audit'); END;
    """)
    for table in ("runs", "properties", "instruments", "covenants", "evidence"):
        for operation in ("UPDATE", "DELETE"):
            db.execute(f"CREATE TRIGGER IF NOT EXISTS {table}_no_{operation.lower()} BEFORE {operation} ON {table} BEGIN SELECT RAISE(ABORT,'immutable run snapshot'); END")
    from .book_model import migrate
    try:
        migrate(db)
        from .cases import migrate as migrate_cases
        migrate_cases(db)
    except Exception:
        db.close()
        raise
    return db


def _audit(db, cid, actor, operation, detail):
    db.execute("INSERT INTO audit(case_id,actor,operation,at,detail) VALUES(?,?,?,?,?)",
               (cid, actor, operation, datetime.now(timezone.utc).isoformat(), json.dumps(detail, sort_keys=True)))


def import_run(db, manifest, leads, events, calendar):
    """Atomic import; identical run IDs are never silently overwritten. Closed cases stay closed."""
    rid = manifest["run_id"]
    from .book_model import build_model, persist_graph
    graph = build_model(leads, events, calendar, manifest)
    with db:
        if db.execute("SELECT 1 FROM runs WHERE run_id=?", (rid,)).fetchone():
            raise ValueError("run already imported")
        db.execute("INSERT INTO runs VALUES(?,?,?)", (rid, manifest["as_of_date"], json.dumps(manifest, sort_keys=True)))
        for row in leads:
            pid = row["property_id"]
            db.execute("INSERT INTO properties VALUES(?,?,?)", (rid, pid, json.dumps(row, sort_keys=True)))
            for position in parse_instruments(row.get("instruments_json")):
                db.execute("INSERT INTO instruments VALUES(?,?,?,?)", (rid, position["instrument_id"], pid, json.dumps(position, sort_keys=True)))
                db.execute("INSERT INTO covenants VALUES(?,?,?,?,?)", (rid, position["instrument_id"], position.get("covenant_status", ""),
                                                                      position.get("affordability_end", ""), position.get("recapture_end", "")))
        for row in events:
            eid = hashlib.sha256(json.dumps([row.get("source", ""), row.get("event_id") or row], sort_keys=True).encode()).hexdigest()
            existing = db.execute("SELECT payload FROM evidence WHERE run_id=? AND event_id=?", (rid, eid)).fetchone()
            payload = json.dumps(row, sort_keys=True)
            if existing and existing[0] != payload:
                raise ValueError(f"conflicting event identity {eid}")
            db.execute("INSERT OR IGNORE INTO evidence VALUES(?,?,?,?)", (rid, eid, row["property_id"], payload))
        persist_graph(db, rid, graph)


def change_case(db, case_id, actor, expected_version, operation, value="", evidence=""):
    from .cases import change
    return change(db, case_id, actor, expected_version, operation, value, evidence)


def list_cases(db, as_of, include_closed=False, **filters):
    from .cases import queue
    return queue(db, as_of, include_closed, **filters)
