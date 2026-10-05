"""Versioned instrument graph. Source observations are evidence, never verified documents.

Unscoped public-inventory events remain property events. Only explicit instrument
identifiers (including legacy servicing ID tags) establish instrument ownership.
"""
import hashlib
import json
import re
from datetime import date
from decimal import Decimal, InvalidOperation

from .instruments import parse_instruments, ID_FIELD

VERSION = 2
TERMINAL = {"REJECTED", "SUPPRESSED", "RESOLVED", "COMPLETED", "SUPERSEDED", "CANCELLED"}
EVENT_COVENANT = {"AGENCY_LOAN_MATURITY": "repayment", "SHARED_APPRECIATION_DUE": "repayment",
                  "AFFORDABILITY_PERIOD_END": "affordability", "GRANT_RECAPTURE_END": "recapture",
                  "HAP_EXPIRATION": "contract_term", "COVENANT_DEFAULT": "compliance",
                  "INSPECTION_DUE": "compliance", "NONCOMPLIANCE_FINDING": "compliance",
                  "HAP_OPTOUT_NOTICE_DEADLINE": "contract_term", "HAP_OPTOUT_PACKAGE_DUE": "contract_term"}
LEGACY_IDS = {"agency_loan_id": "loan", "grant_id": "grant", "asset_id": "owned_asset", "contract_id": "administered_contract"}


def identity(prefix, *parts):
    return prefix + ":" + hashlib.sha256(json.dumps(parts, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()[:32]


def cents(raw):
    if raw in (None, ""):
        return None
    try:
        value = Decimal(str(raw)) * 100
        if not value.is_finite() or value != value.to_integral_value() or value < 0 or value > 9223372036854775807:
            raise ValueError("principal must be a nonnegative amount with at most two decimal places")
        return int(value)
    except InvalidOperation as exc:
        raise ValueError("invalid principal amount") from exc


def build_model(leads, events, calendar=(), manifest=None):
    manifest = manifest or {}
    graph = {"schema_version": VERSION, "properties": [], "instruments": [], "covenants": [], "events": [],
             "evidence": [], "event_evidence": [], "actions": [], "action_events": [], "linkage_issues": []}
    properties, instruments, covenants, event_map, evidence = {}, {}, {}, {}, {}
    for lead in leads:
        pid = str(lead["property_id"])
        if pid in properties:
            raise ValueError(f"duplicate property {pid}")
        properties[pid] = {"property_id": pid, "property_name": lead.get("property_name", "")}
        for r in parse_instruments(lead.get("instruments_json")):
            iid, kind = r.get("instrument_id"), r.get("book_kind")
            if not iid or kind not in ID_FIELD:
                raise ValueError("instrument requires a supported kind and stable ID")
            source_id = str(r.get(ID_FIELD[kind]) or "")
            if not source_id or iid != f"{kind}:{source_id}":
                raise ValueError(f"instrument identifier mismatch: {iid}")
            if iid in instruments:
                raise ValueError(f"instrument {iid} assigned more than once")
            instruments[iid] = {"instrument_id": iid, "property_id": pid, "kind": kind, "source_id": source_id,
                                "program": r.get("agency_programs", ""), "principal_minor": cents(r.get("public_upb")),
                                "currency": "USD", "terms": r}
            definitions = [("compliance", "", "", r.get("covenant_status", ""))]
            if kind == "loan":
                definitions.append(("repayment", r.get("origination_date", ""), r.get("our_maturity", ""), ""))
            if r.get("affordability_end"):
                definitions.append(("affordability", "", r["affordability_end"], ""))
            if r.get("recapture_type") not in (None, "", "none") or r.get("recapture_method") not in (None, "", "none"):
                definitions.append(("recapture", r.get("recapture_start", ""), r.get("recapture_end", ""), ""))
            if kind == "administered_contract" or r.get("contract_expiration"):
                definitions.append(("contract_term", "", r.get("contract_expiration", ""), ""))
            for ctype, start, end, status in definitions:
                cid = identity("covenant", iid, ctype)
                covenants[cid] = {"covenant_id": cid, "instrument_id": iid, "property_id": pid, "covenant_type": ctype,
                                  "effective_from": start or None, "effective_to": end or None, "status": status or "unknown",
                                  "terms": {k: r.get(k) for k in ("payment_type", "our_rate", "recapture_type", "recapture_method", "recapture_amount")},
                                  "verification": "source_extract_only"}
    observations = list(events)
    # Legacy callers can supply only a calendar; retain that observation explicitly.
    for row in calendar:
        pid, et, due = row["property_id"], row["agency_action_type"], row["due_date"]
        if not any(str(e.get("property_id")) == pid and e.get("event_type") == et and e.get("event_date") == due
                   and (not row.get("instrument_id") or e.get("instrument_id") == row["instrument_id"]) for e in observations):
            observations.append({"property_id": pid, "event_type": et, "event_family": "AGENCY_DEADLINE", "event_date": due,
                                 "source": "legacy_calendar", "status": row.get("status", ""), "basis": row.get("basis", ""),
                                 "instrument_id": row.get("instrument_id", "")})
    for row in observations:
        pid = str(row["property_id"])
        if pid not in properties:
            # Scored populations may exclude inventory events; never attach them to another property.
            graph["linkage_issues"].append({"property_id": pid, "reason": "event outside selected property population", "source_event_id": row.get("event_id", "")})
            continue
        iid = str(row.get("instrument_id") or "").strip()
        if not iid:
            tags = re.findall(r"(?:^|;\s*)(agency_loan_id|grant_id|asset_id|contract_id)=([^;]+)", str(row.get("detail") or ""))
            candidates = {f"{LEGACY_IDS[k]}:{v.strip()}" for k, v in tags}
            if len(candidates) == 1:
                iid = next(iter(candidates))
            elif candidates:
                raise ValueError("ambiguous legacy instrument tags")
        if iid and (iid not in instruments or instruments[iid]["property_id"] != pid):
            raise ValueError(f"event references missing or wrong-property instrument {iid}")
        ctype = EVENT_COVENANT.get(row.get("event_type"))
        cid = identity("covenant", iid, ctype) if iid and ctype else None
        if cid not in covenants:
            cid = None
        eid = identity("event", pid, iid or None, row.get("event_type"), row.get("event_date"), row.get("program", ""), "" if iid else row.get("detail", ""))
        event = {"event_id": eid, "property_id": pid, "instrument_id": iid or None, "covenant_id": cid,
                 "event_type": row.get("event_type", ""), "event_family": row.get("event_family", ""), "event_date": row.get("event_date") or None,
                 "status": row.get("status", ""), "scope": "instrument" if iid else "property",
                 "source_event_id": row.get("event_id", "")}
        if eid in event_map and any(event_map[eid][k] != event[k] for k in ("status", "covenant_id", "event_family")):
            raise ValueError(f"conflicting observations for event {eid}")
        event_map.setdefault(eid, event)
        proof = {"source": row.get("source", ""), "source_vintage": row.get("source_vintage", ""), "basis": row.get("basis", ""),
                 "reference": row.get("event_id", ""), "observation": row,
                 "input_files": [{k: f.get(k) for k in ("file", "sha256", "vintage")} for f in manifest.get("inputs", [])],
                 "verification": "unverified_source_observation"}
        evid = identity("evidence", proof)
        evidence[evid] = {"evidence_id": evid, **proof}
        link = {"event_id": eid, "evidence_id": evid, "relationship": "supported_by"}
        if link not in graph["event_evidence"]:
            graph["event_evidence"].append(link)
    for eid, event in event_map.items():
        if event["event_family"] != "AGENCY_DEADLINE" or str(event["status"]).upper() in TERMINAL:
            continue
        if not event["event_date"]:
            graph["linkage_issues"].append({"event_id": eid, "reason": "deadline without date requires review"})
            continue
        date.fromisoformat(event["event_date"])
        aid = identity("action", eid)
        graph["actions"].append({"action_id": aid, "property_id": event["property_id"], "instrument_id": event["instrument_id"],
                                  "covenant_id": event["covenant_id"], "action_type": event["event_type"], "due_date": event["event_date"],
                                  "scope": event["scope"]})
        graph["action_events"].append({"action_id": aid, "event_id": eid, "relationship": "triggered_by"})
    graph["properties"] = list(properties.values())
    graph["instruments"] = list(instruments.values())
    graph["covenants"] = list(covenants.values())
    graph["events"] = list(event_map.values())
    graph["evidence"] = list(evidence.values())
    return graph


DDL = [
    "CREATE TABLE IF NOT EXISTS schema_migrations(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)",
    """CREATE TABLE IF NOT EXISTS model_instruments(run_id TEXT, instrument_id TEXT, property_id TEXT NOT NULL,
       kind TEXT NOT NULL CHECK(kind IN ('loan','grant','owned_asset','administered_contract')), source_id TEXT NOT NULL,
       program TEXT, principal_minor INTEGER CHECK(principal_minor>=0), currency TEXT NOT NULL, terms_json TEXT NOT NULL,
       PRIMARY KEY(run_id,instrument_id), UNIQUE(run_id,instrument_id,property_id),
       FOREIGN KEY(run_id,property_id) REFERENCES properties(run_id,property_id))""",
    """CREATE TABLE IF NOT EXISTS model_covenants(run_id TEXT, covenant_id TEXT, instrument_id TEXT NOT NULL, property_id TEXT NOT NULL,
       covenant_type TEXT NOT NULL, effective_from TEXT, effective_to TEXT, status TEXT NOT NULL, terms_json TEXT NOT NULL,
       PRIMARY KEY(run_id,covenant_id), UNIQUE(run_id,covenant_id,instrument_id,property_id),
       FOREIGN KEY(run_id,instrument_id,property_id) REFERENCES model_instruments(run_id,instrument_id,property_id))""",
    """CREATE TABLE IF NOT EXISTS model_events(run_id TEXT, event_id TEXT, property_id TEXT NOT NULL, instrument_id TEXT,
       covenant_id TEXT, event_type TEXT NOT NULL, event_date TEXT, status TEXT, payload TEXT NOT NULL,
       PRIMARY KEY(run_id,event_id), UNIQUE(run_id,event_id,property_id), CHECK(covenant_id IS NULL OR instrument_id IS NOT NULL),
       FOREIGN KEY(run_id,property_id) REFERENCES properties(run_id,property_id),
       FOREIGN KEY(run_id,instrument_id,property_id) REFERENCES model_instruments(run_id,instrument_id,property_id),
       FOREIGN KEY(run_id,covenant_id,instrument_id,property_id) REFERENCES model_covenants(run_id,covenant_id,instrument_id,property_id))""",
    """CREATE TABLE IF NOT EXISTS model_evidence(run_id TEXT REFERENCES runs(run_id), evidence_id TEXT, source TEXT,
       source_vintage TEXT, basis TEXT, reference TEXT, payload TEXT NOT NULL, PRIMARY KEY(run_id,evidence_id))""",
    """CREATE TABLE IF NOT EXISTS model_event_evidence(run_id TEXT, event_id TEXT, evidence_id TEXT, relationship TEXT NOT NULL,
       PRIMARY KEY(run_id,event_id,evidence_id), FOREIGN KEY(run_id,event_id) REFERENCES model_events(run_id,event_id),
       FOREIGN KEY(run_id,evidence_id) REFERENCES model_evidence(run_id,evidence_id))""",
    """CREATE TABLE IF NOT EXISTS model_actions(run_id TEXT REFERENCES runs(run_id), action_id TEXT, property_id TEXT NOT NULL,
       instrument_id TEXT, covenant_id TEXT, action_type TEXT NOT NULL, due_date TEXT NOT NULL, case_id TEXT REFERENCES cases(case_id),
       PRIMARY KEY(run_id,action_id), UNIQUE(run_id,action_id,property_id), CHECK(covenant_id IS NULL OR instrument_id IS NOT NULL),
       FOREIGN KEY(run_id,property_id) REFERENCES properties(run_id,property_id),
       FOREIGN KEY(run_id,instrument_id,property_id) REFERENCES model_instruments(run_id,instrument_id,property_id),
       FOREIGN KEY(run_id,covenant_id,instrument_id,property_id) REFERENCES model_covenants(run_id,covenant_id,instrument_id,property_id))""",
    """CREATE TABLE IF NOT EXISTS model_action_events(run_id TEXT, action_id TEXT, event_id TEXT, property_id TEXT NOT NULL,
       relationship TEXT NOT NULL, PRIMARY KEY(run_id,action_id,event_id),
       FOREIGN KEY(run_id,action_id,property_id) REFERENCES model_actions(run_id,action_id,property_id),
       FOREIGN KEY(run_id,event_id,property_id) REFERENCES model_events(run_id,event_id,property_id))""",
    "CREATE TABLE IF NOT EXISTS model_linkage_issues(run_id TEXT REFERENCES runs(run_id), detail TEXT NOT NULL)",
    """CREATE TRIGGER IF NOT EXISTS model_action_scope BEFORE INSERT ON model_action_events
        WHEN EXISTS(SELECT 1 FROM model_actions a JOIN model_events e ON a.run_id=e.run_id
          WHERE a.run_id=NEW.run_id AND a.action_id=NEW.action_id AND e.event_id=NEW.event_id
          AND (a.instrument_id IS NOT e.instrument_id OR a.covenant_id IS NOT e.covenant_id))
        BEGIN SELECT RAISE(ABORT,'action and event scope mismatch'); END""",
]


def persist_graph(db, rid, graph, migrate=False):
    from .operations import _audit
    for r in graph["instruments"]:
        db.execute("INSERT INTO model_instruments VALUES(?,?,?,?,?,?,?,?,?)", (rid,r["instrument_id"],r["property_id"],r["kind"],r["source_id"],r["program"],r["principal_minor"],r["currency"],json.dumps(r["terms"])))
    for r in graph["covenants"]:
        db.execute("INSERT INTO model_covenants VALUES(?,?,?,?,?,?,?,?,?)", (rid,r["covenant_id"],r["instrument_id"],r["property_id"],r["covenant_type"],r["effective_from"],r["effective_to"],r["status"],json.dumps(r["terms"])))
    for r in graph["events"]:
        db.execute("INSERT INTO model_events VALUES(?,?,?,?,?,?,?,?,?)", (rid,r["event_id"],r["property_id"],r["instrument_id"],r["covenant_id"],r["event_type"],r["event_date"],r["status"],json.dumps(r)))
    for r in graph["evidence"]:
        db.execute("INSERT INTO model_evidence VALUES(?,?,?,?,?,?,?)", (rid,r["evidence_id"],r["source"],r["source_vintage"],r["basis"],r["reference"],json.dumps(r)))
    for r in graph["event_evidence"]:
        db.execute("INSERT INTO model_event_evidence VALUES(?,?,?,?)", (rid,r["event_id"],r["evidence_id"],r["relationship"]))
    for r in graph["actions"]:
        aid = r["action_id"]
        existing = db.execute("SELECT case_id FROM model_actions WHERE action_id=? AND case_id IS NOT NULL LIMIT 1", (aid,)).fetchone()
        case_id = existing[0] if existing else None
        if not case_id and migrate:
            matches = list(db.execute("SELECT case_id FROM cases WHERE property_id=? AND event_type=? AND due_date=?", (r["property_id"],r["action_type"],r["due_date"])))
            siblings = [x for x in graph["actions"] if (x["property_id"],x["action_type"],x["due_date"]) == (r["property_id"],r["action_type"],r["due_date"])]
            if len(matches) == len(siblings) == 1:
                case_id = matches[0][0]
            else:
                graph["linkage_issues"].append({"action_id": aid, "reason": "legacy case cannot be uniquely linked; review required"})
        if not case_id and not migrate:
            case_id = aid
            if not db.execute("SELECT 1 FROM cases WHERE case_id=?", (case_id,)).fetchone():
                db.execute("INSERT INTO cases(case_id,property_id,event_type,due_date,source_run) VALUES(?,?,?,?,?)", (case_id,r["property_id"],r["action_type"],r["due_date"],rid))
                if "created_at" in {c[1] for c in db.execute("PRAGMA table_info(cases)")} :
                    from .cases import initialize
                    initialize(db, case_id)
                _audit(db,case_id,"pipeline","CREATED",{"run_id":rid,"instrument_id":r["instrument_id"],"action_id":aid})
        db.execute("INSERT INTO model_actions VALUES(?,?,?,?,?,?,?,?)", (rid,aid,r["property_id"],r["instrument_id"],r["covenant_id"],r["action_type"],r["due_date"],case_id))
    actions = {r["action_id"]:r for r in graph["actions"]}
    for r in graph["action_events"]:
        db.execute("INSERT INTO model_action_events VALUES(?,?,?,?,?)", (rid,r["action_id"],r["event_id"],actions[r["action_id"]]["property_id"],r["relationship"]))
    for issue in graph["linkage_issues"]:
        db.execute("INSERT INTO model_linkage_issues VALUES(?,?)", (rid,json.dumps(issue)))


def migrate(db):
    from datetime import datetime, timezone
    with db:
        db.execute("BEGIN IMMEDIATE")
        for statement in DDL:
            db.execute(statement)
        if db.execute("SELECT 1 FROM schema_migrations WHERE version=?", (VERSION,)).fetchone():
            return
        for run in db.execute("SELECT * FROM runs ORDER BY as_of,run_id").fetchall():
            rid = run["run_id"]
            leads = [json.loads(r[0]) for r in db.execute("SELECT payload FROM properties WHERE run_id=?", (rid,))]
            events = [json.loads(r[0]) for r in db.execute("SELECT payload FROM evidence WHERE run_id=?", (rid,))]
            calendar = [{"property_id":r[0],"agency_action_type":r[1],"due_date":r[2]} for r in db.execute("SELECT property_id,event_type,due_date FROM cases WHERE source_run=?", (rid,))]
            persist_graph(db,rid,build_model(leads,events,calendar,json.loads(run["manifest"])),migrate=True)
        for table in ("model_instruments","model_covenants","model_events","model_evidence","model_event_evidence","model_actions","model_action_events","model_linkage_issues"):
            for op in ("UPDATE","DELETE"):
                db.execute(f"CREATE TRIGGER IF NOT EXISTS {table}_no_{op.lower()} BEFORE {op} ON {table} BEGIN SELECT RAISE(ABORT,'immutable model snapshot'); END")
        db.execute("INSERT INTO schema_migrations VALUES(?,?)", (VERSION,datetime.now(timezone.utc).isoformat()))
