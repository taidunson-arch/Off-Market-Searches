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
    return db


def _audit(db, cid, actor, operation, detail):
    db.execute("INSERT INTO audit(case_id,actor,operation,at,detail) VALUES(?,?,?,?,?)",
               (cid, actor, operation, datetime.now(timezone.utc).isoformat(), json.dumps(detail, sort_keys=True)))


def import_run(db, manifest, leads, events, calendar):
    """Atomic import; identical run IDs are never silently overwritten. Closed cases stay closed."""
    rid = manifest["run_id"]
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
            eid = row.get("event_id") or hashlib.sha256(json.dumps(row, sort_keys=True).encode()).hexdigest()
            existing = db.execute("SELECT payload FROM evidence WHERE run_id=? AND event_id=?", (rid, eid)).fetchone()
            payload = json.dumps(row, sort_keys=True)
            if existing and existing[0] != payload:
                raise ValueError(f"conflicting event identity {eid}")
            db.execute("INSERT OR IGNORE INTO evidence VALUES(?,?,?,?)", (rid, eid, row["property_id"], payload))
        for row in calendar:
            due = date.fromisoformat(row["due_date"]).isoformat()
            key = json.dumps([row["property_id"], row["agency_action_type"], due])
            cid = hashlib.sha256(key.encode()).hexdigest()[:24]
            if not db.execute("SELECT 1 FROM cases WHERE case_id=?", (cid,)).fetchone():
                db.execute("INSERT INTO cases(case_id,property_id,event_type,due_date,source_run) VALUES(?,?,?,?,?)",
                           (cid, row["property_id"], row["agency_action_type"], due, rid))
                _audit(db, cid, "pipeline", "CREATED", {"run_id": rid, "suggested_role": row.get("agency_owner", "")})


def change_case(db, case_id, actor, expected_version, operation, value="", evidence=""):
    """Optimistic concurrency and a separate reviewer for completion approval."""
    if not actor.strip():
        raise ValueError("actor required")
    with db:
        # Serialize read/modify/write across concurrent CLI processes.
        db.execute("BEGIN IMMEDIATE")
        record = db.execute("SELECT * FROM cases WHERE case_id=?", (case_id,)).fetchone()
        if not record:
            raise ValueError("unknown case")
        row = dict(record)
        if row["version"] != expected_version:
            raise ValueError("case changed; reload before editing")
        before = dict(row)
        if operation == "assign":
            if not value.strip() or row["status"] in ("CLOSED", "CANCELLED"):
                raise ValueError("assign an open case to a named officer")
            row["assigned_to"] = value.strip()
        elif operation == "start":
            if row["status"] != "OPEN" or not row["assigned_to"]:
                raise ValueError("an assigned OPEN case is required")
            row["status"] = "IN_PROGRESS"
        elif operation == "submit":
            if row["status"] not in ("OPEN", "IN_PROGRESS", "ESCALATED") or not row["assigned_to"] or not evidence.strip():
                raise ValueError("assigned active case and completion evidence required")
            row.update(status="PENDING_APPROVAL", evidence=evidence.strip(), submitted_by=actor, approved_by="")
        elif operation == "approve":
            if row["status"] != "PENDING_APPROVAL" or actor == row["submitted_by"] or not evidence.strip():
                raise ValueError("independent reviewer and approval evidence required")
            row.update(status="CLOSED", approved_by=actor)
        elif operation in ("escalate", "cancel", "reopen"):
            if not evidence.strip():
                raise ValueError("reason/evidence required")
            if operation == "reopen":
                if row["status"] not in ("CLOSED", "CANCELLED"):
                    raise ValueError("only a closed case can be reopened")
                row.update(status="OPEN", submitted_by="", approved_by="", evidence="")
            else:
                if row["status"] in ("CLOSED", "CANCELLED"):
                    raise ValueError("reopen the closed case first")
                row["status"] = "ESCALATED" if operation == "escalate" else "CANCELLED"
        else:
            raise ValueError("unsupported operation")
        db.execute("UPDATE cases SET assigned_to=?,status=?,version=version+1,evidence=?,submitted_by=?,approved_by=? WHERE case_id=?",
                   (row["assigned_to"], row["status"], row["evidence"], row["submitted_by"], row["approved_by"], case_id))
        _audit(db, case_id, actor, operation.upper(), {"before": before, "after": dict(row, version=expected_version+1), "evidence": evidence})


def list_cases(db, as_of, include_closed=False):
    rows = []
    for row in db.execute("SELECT * FROM cases ORDER BY due_date,case_id"):
        r = dict(row)
        if not include_closed and r["status"] in ("CLOSED", "CANCELLED"):
            continue
        r["overdue_days"] = max(0, (as_of-date.fromisoformat(r["due_date"])).days) if r["status"] not in ("CLOSED", "CANCELLED") else 0
        rows.append(r)
    return rows
