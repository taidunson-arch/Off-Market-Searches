"""Persistent, version-checked case workflow for a single agency's local store."""
import json
import uuid
from datetime import date, datetime, timezone

TERMINAL = {"CLOSED", "CANCELLED"}
ACTIVE = {"OPEN", "IN_PROGRESS", "ESCALATED"}
OPERATIONS = ("assign", "start", "reschedule", "priority", "note", "attach", "submit", "approve", "reject", "escalate", "deescalate", "cancel", "reopen")
FIELDS = ("title", "original_due_date", "priority", "escalated_to", "escalation_reason", "escalated_at",
          "created_at", "updated_at", "completed_at", "submitted_evidence_id")


def now():
    return datetime.now(timezone.utc).isoformat()


def actor_key(value):
    return " ".join(value.split()).casefold()


def migrate(db):
    """Append schema v3; retain old evidence strings and audit entries verbatim."""
    with db:
        db.execute("BEGIN IMMEDIATE")
        db.execute("CREATE TABLE IF NOT EXISTS schema_migrations(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)")
        if db.execute("SELECT 1 FROM schema_migrations WHERE version=3").fetchone():
            return
        columns = {r[1] for r in db.execute("PRAGMA table_info(cases)")}
        for field in FIELDS:
            if field not in columns:
                default = "NORMAL" if field == "priority" else ""
                db.execute(f"ALTER TABLE cases ADD COLUMN {field} TEXT NOT NULL DEFAULT '{default}'")
        db.execute("""CREATE TABLE case_evidence(evidence_id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases,
            case_version INTEGER NOT NULL, purpose TEXT NOT NULL, reference TEXT NOT NULL, note TEXT NOT NULL,
            added_by TEXT NOT NULL, added_at TEXT NOT NULL, origin TEXT NOT NULL, UNIQUE(evidence_id,case_id))""")
        db.execute("""CREATE TABLE case_decisions(decision_id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases,
            submitted_version INTEGER NOT NULL, decision TEXT NOT NULL CHECK(decision IN ('APPROVED','REJECTED')),
            reviewer TEXT NOT NULL, decided_at TEXT NOT NULL, completion_evidence_id TEXT REFERENCES case_evidence,
            decision_evidence_id TEXT NOT NULL REFERENCES case_evidence,
            FOREIGN KEY(completion_evidence_id,case_id) REFERENCES case_evidence(evidence_id,case_id),
            FOREIGN KEY(decision_evidence_id,case_id) REFERENCES case_evidence(evidence_id,case_id))""")
        db.execute("""CREATE TABLE case_scope(case_id TEXT PRIMARY KEY REFERENCES cases,
            run_id TEXT NOT NULL, property_id TEXT NOT NULL, instrument_id TEXT,
            FOREIGN KEY(run_id,property_id) REFERENCES properties(run_id,property_id),
            FOREIGN KEY(run_id,instrument_id,property_id) REFERENCES model_instruments(run_id,instrument_id,property_id))""")
        for row in db.execute("SELECT * FROM cases").fetchall():
            # Original v2 due dates are unchanged by its workflow; no inferred history.
            db.execute("UPDATE cases SET original_due_date=due_date,title=event_type WHERE case_id=?", (row["case_id"],))
            if row["evidence"]:
                eid = _evidence(db, row["case_id"], row["version"], "legacy_completion", row["evidence"], "",
                                row["submitted_by"], origin="legacy_import")
                db.execute("UPDATE cases SET submitted_evidence_id=? WHERE case_id=?", (eid, row["case_id"]))
        for table in ("case_evidence", "case_decisions", "case_scope"):
            for op in ("UPDATE", "DELETE"):
                db.execute(f"CREATE TRIGGER {table}_no_{op.lower()} BEFORE {op} ON {table} BEGIN SELECT RAISE(ABORT,'append-only case record'); END")
        db.execute("INSERT INTO schema_migrations VALUES(3,?)", (now(),))


def initialize(db, case_id):
    timestamp = now()
    db.execute("UPDATE cases SET title=event_type,original_due_date=due_date,created_at=?,updated_at=? WHERE case_id=?",
               (timestamp, timestamp, case_id))


def _evidence(db, cid, version, purpose, reference, note, actor, origin="workflow"):
    if not reference.strip():
        raise ValueError("evidence reference or recorded rationale required")
    eid = "evidence:" + uuid.uuid4().hex
    db.execute("INSERT INTO case_evidence VALUES(?,?,?,?,?,?,?,?,?)",
               (eid, cid, version, purpose, reference.strip(), note.strip(), actor, now(), origin))
    return eid


def create(db, *, run_id, property_id, title, due_date, owner, actor, instrument_id=None, priority="NORMAL"):
    from .operations import _audit
    if not all(str(v).strip() for v in (title, owner, actor)):
        raise ValueError("title, named owner and actor required")
    due = date.fromisoformat(due_date).isoformat()
    if priority not in ("LOW", "NORMAL", "HIGH", "URGENT"):
        raise ValueError("unsupported priority")
    with db:
        db.execute("BEGIN IMMEDIATE")
        if not db.execute("SELECT 1 FROM properties WHERE run_id=? AND property_id=?", (run_id, property_id)).fetchone():
            raise ValueError("property not present in source run")
        if instrument_id and not db.execute("SELECT 1 FROM model_instruments WHERE run_id=? AND property_id=? AND instrument_id=?",
                                           (run_id, property_id, instrument_id)).fetchone():
            raise ValueError("instrument does not belong to this property and run")
        cid = "case:" + uuid.uuid4().hex
        db.execute("INSERT INTO cases(case_id,property_id,event_type,due_date,assigned_to,source_run) VALUES(?,?,?,?,?,?)",
                   (cid, property_id, "MANUAL", due, owner.strip(), run_id))
        initialize(db, cid)
        db.execute("UPDATE cases SET title=?,priority=? WHERE case_id=?", (title.strip(), priority, cid))
        db.execute("INSERT INTO case_scope VALUES(?,?,?,?)", (cid, run_id, property_id, instrument_id or None))
        _audit(db, cid, actor.strip(), "CREATED", {"after": dict(db.execute("SELECT * FROM cases WHERE case_id=?", (cid,)).fetchone()), "instrument_id": instrument_id})
    return cid


def change(db, case_id, actor, expected_version, operation, value="", evidence=""):
    from .operations import _audit
    actor = actor.strip()
    if not actor:
        raise ValueError("actor required")
    with db:
        db.execute("BEGIN IMMEDIATE")
        record = db.execute("SELECT * FROM cases WHERE case_id=?", (case_id,)).fetchone()
        if not record:
            raise ValueError("unknown case")
        row = dict(record)
        if row["version"] != expected_version:
            raise ValueError("case changed; reload before editing")
        before = dict(row)
        status, version = row["status"], expected_version + 1
        eid = None
        if operation not in OPERATIONS:
            raise ValueError("unsupported operation")
        if status in TERMINAL and operation not in ("reopen", "note", "attach"):
            raise ValueError("reopen the closed case first")
        if status == "PENDING_APPROVAL" and operation in ("assign", "reschedule", "priority", "start"):
            raise ValueError("review the pending submission before changing its work terms")
        if operation == "assign":
            if not value.strip():
                raise ValueError("named owner required")
            row["assigned_to"] = value.strip()
        elif operation == "start":
            if status != "OPEN" or not row["assigned_to"]:
                raise ValueError("an assigned OPEN case is required")
            row["status"] = "IN_PROGRESS"
        elif operation == "reschedule":
            if not evidence.strip():
                raise ValueError("deadline change reason required")
            row["due_date"] = date.fromisoformat(value).isoformat()
        elif operation == "priority":
            if value not in ("LOW", "NORMAL", "HIGH", "URGENT") or not evidence.strip():
                raise ValueError("valid priority and change reason required")
            row["priority"] = value
        elif operation in ("note", "attach"):
            eid = _evidence(db, case_id, version, operation, evidence, value, actor)
        elif operation == "submit":
            if status not in ACTIVE or not row["assigned_to"] or actor_key(actor) != actor_key(row["assigned_to"]):
                raise ValueError("assigned owner must submit an active case")
            eid = _evidence(db, case_id, version, "completion", evidence, value, actor)
            row.update(status="PENDING_APPROVAL", evidence=evidence.strip(), submitted_by=actor,
                       submitted_evidence_id=eid, approved_by="", completed_at="")
        elif operation in ("approve", "reject"):
            if status != "PENDING_APPROVAL" or actor_key(actor) in {actor_key(row["submitted_by"]), actor_key(row["assigned_to"])}:
                raise ValueError("pending submission and independent reviewer required")
            if not row["submitted_evidence_id"]:
                raise ValueError("completion evidence required")
            eid = _evidence(db, case_id, version, operation, evidence, value, actor)
            submitted = db.execute("SELECT case_version FROM case_evidence WHERE evidence_id=? AND case_id=?",
                                   (row["submitted_evidence_id"], case_id)).fetchone()
            if not submitted:
                raise ValueError("completion evidence must belong to this case")
            db.execute("INSERT INTO case_decisions VALUES(?,?,?,?,?,?,?,?)",
                       ("decision:" + uuid.uuid4().hex, case_id, submitted[0], "APPROVED" if operation == "approve" else "REJECTED",
                        actor, now(), row["submitted_evidence_id"], eid))
            if operation == "approve":
                row.update(status="CLOSED", approved_by=actor, completed_at=now(), escalated_to="", escalation_reason="", escalated_at="")
            else:
                row.update(status="ESCALATED" if row["escalated_to"] else "IN_PROGRESS", submitted_by="", submitted_evidence_id="", approved_by="", evidence="")
        elif operation == "escalate":
            if not value.strip() or not evidence.strip():
                raise ValueError("named escalation recipient and reason required")
            row.update(status="ESCALATED", escalated_to=value.strip(), escalation_reason=evidence.strip(), escalated_at=now(),
                       submitted_by="", submitted_evidence_id="", approved_by="", evidence="")
        elif operation == "deescalate":
            if status != "ESCALATED" or not evidence.strip():
                raise ValueError("escalated case and resolution reason required")
            row.update(status="IN_PROGRESS" if row["assigned_to"] else "OPEN", escalated_to="", escalation_reason="", escalated_at="")
        elif operation == "cancel":
            if not evidence.strip():
                raise ValueError("cancellation reason required")
            row.update(status="CANCELLED", submitted_by="", submitted_evidence_id="", approved_by="",
                       escalated_to="", escalation_reason="", escalated_at="")
        elif operation == "reopen":
            if status not in TERMINAL or not evidence.strip():
                raise ValueError("closed case and reopening reason required")
            row.update(status="OPEN", submitted_by="", submitted_evidence_id="", approved_by="", evidence="", completed_at="",
                       escalated_to="", escalation_reason="", escalated_at="")
        row.update(version=version, updated_at=now())
        mutable = ("assigned_to", "status", "version", "evidence", "submitted_by", "approved_by", "due_date", *FIELDS)
        db.execute("UPDATE cases SET " + ",".join(f"{key}=?" for key in mutable) + " WHERE case_id=?",
                   (*[row[key] for key in mutable], case_id))
        _audit(db, case_id, actor, operation.upper(), {"before": before, "after": row, "evidence": evidence, "evidence_id": eid})
    return row


def detail(db, case_id):
    record = db.execute("SELECT * FROM cases WHERE case_id=?", (case_id,)).fetchone()
    if not record:
        raise ValueError("unknown case")
    result = {"case": dict(record)}
    for key, table, order in (("evidence", "case_evidence", "case_version,evidence_id"), ("decisions", "case_decisions", "submitted_version,decision_id"), ("history", "audit", "seq")):
        result[key] = [dict(r) for r in db.execute(f"SELECT * FROM {table} WHERE case_id=? ORDER BY {order}", (case_id,))]
    for item in result["history"]:
        item["detail"] = json.loads(item["detail"])
    result["scope"] = [dict(r) for r in db.execute("SELECT * FROM case_scope WHERE case_id=?", (case_id,))]
    result["actions"] = [dict(r) for r in db.execute("SELECT * FROM model_actions WHERE case_id=? ORDER BY run_id", (case_id,))]
    return result


def queue(db, as_of, include_closed=False, owner=None, status=None, due_by=None, escalated_to=None):
    rows = []
    for record in db.execute("SELECT * FROM cases ORDER BY due_date,case_id"):
        row = dict(record)
        if not include_closed and row["status"] in TERMINAL:
            continue
        if owner is not None and actor_key(row["assigned_to"]) != actor_key(owner):
            continue
        if status and row["status"] != status:
            continue
        if escalated_to is not None and (row["status"] in TERMINAL or actor_key(row["escalated_to"]) != actor_key(escalated_to)):
            continue
        due = date.fromisoformat(row["due_date"])
        if due_by and due > due_by:
            continue
        row["overdue_days"] = max(0, (as_of - due).days) if row["status"] not in TERMINAL else 0
        row["unassigned"] = not bool(row["assigned_to"].strip())
        rows.append(row)
    return rows
