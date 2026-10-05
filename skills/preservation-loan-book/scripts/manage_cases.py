#!/usr/bin/env python3
"""Local HFA case workflow. Run --help for commands. Actor names are not authentication."""
import argparse
import json
from datetime import date
from plb.operations import connect, change_case, list_cases


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", required=True)
    sub = ap.add_subparsers(dest="command", required=True)
    ls = sub.add_parser("list")
    ls.add_argument("--as-of", required=True)
    ls.add_argument("--include-closed", action="store_true")
    change = sub.add_parser("change")
    change.add_argument("case_id")
    change.add_argument("operation", choices=["assign", "start", "submit", "approve", "escalate", "cancel", "reopen"])
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
            print(json.dumps(list_cases(db, date.fromisoformat(a.as_of), a.include_closed), indent=2))
        elif a.command == "audit":
            print(json.dumps([dict(r) for r in db.execute("SELECT * FROM audit WHERE case_id=? ORDER BY seq", (a.case_id,))], indent=2))
        else:
            change_case(db, a.case_id, a.actor, a.version, a.operation, a.value, a.evidence)
            print("Case updated")
    finally:
        db.close()


if __name__ == "__main__":
    main()
