#!/usr/bin/env python3
"""Local HFA case workflow. Run --help for commands. Actor names are not authentication."""
import argparse
import json
from datetime import date
from plb.operations import connect, change_case, list_cases
from plb.cases import create, detail, OPERATIONS


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", required=True)
    sub = ap.add_subparsers(dest="command", required=True)
    ls = sub.add_parser("list")
    ls.add_argument("--as-of", required=True)
    ls.add_argument("--include-closed", action="store_true")
    ls.add_argument("--owner")
    ls.add_argument("--status", choices=["OPEN", "IN_PROGRESS", "PENDING_APPROVAL", "ESCALATED", "CLOSED", "CANCELLED"])
    ls.add_argument("--due-by")
    ls.add_argument("--escalated-to")
    show = sub.add_parser("show")
    show.add_argument("case_id")
    new = sub.add_parser("create")
    for field in ("run-id", "property-id", "title", "due-date", "owner", "actor"):
        new.add_argument("--" + field, required=True)
    new.add_argument("--instrument-id")
    new.add_argument("--priority", choices=["LOW", "NORMAL", "HIGH", "URGENT"], default="NORMAL")
    change = sub.add_parser("change")
    change.add_argument("case_id")
    change.add_argument("operation", choices=OPERATIONS)
    change.add_argument("--actor", required=True)
    change.add_argument("--version", type=int, required=True)
    change.add_argument("--value", default="")
    change.add_argument("--evidence", default="")
    audit = sub.add_parser("audit")
    audit.add_argument("case_id")
    a = ap.parse_args()
    db = connect(a.db)
    try:
        if a.command == "list":
            print(json.dumps(list_cases(db, date.fromisoformat(a.as_of), a.include_closed, owner=a.owner,
                status=a.status, due_by=date.fromisoformat(a.due_by) if a.due_by else None, escalated_to=a.escalated_to), indent=2))
        elif a.command == "show":
            print(json.dumps(detail(db, a.case_id), indent=2))
        elif a.command == "create":
            cid = create(db, run_id=a.run_id, property_id=a.property_id, title=a.title, due_date=a.due_date,
                         owner=a.owner, actor=a.actor, instrument_id=a.instrument_id, priority=a.priority)
            print(json.dumps(detail(db, cid), indent=2))
        elif a.command == "audit":
            print(json.dumps([dict(r) for r in db.execute("SELECT * FROM audit WHERE case_id=? ORDER BY seq", (a.case_id,))], indent=2))
        else:
            result = change_case(db, a.case_id, a.actor, a.version, a.operation, a.value, a.evidence)
            print(json.dumps(result, indent=2))
    except ValueError as exc:
        ap.exit(2, f"Case operation rejected: {exc}\n")
    finally:
        db.close()


if __name__ == "__main__":
    main()
