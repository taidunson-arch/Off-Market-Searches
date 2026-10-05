"""Trace an instrument through covenants, events, source evidence and action cases."""
import argparse
import json
from contextlib import closing
from plb.operations import connect


def inspect(db, run_id, instrument_id):
    def rows(sql, args):
        return [dict(r) for r in db.execute(sql, args)]
    args = (run_id, instrument_id)
    instruments = rows("SELECT * FROM model_instruments WHERE run_id=? AND instrument_id=?", args)
    if not instruments:
        raise ValueError("instrument not present in this run")
    return {
        "instrument": instruments[0],
        "covenants": rows("SELECT * FROM model_covenants WHERE run_id=? AND instrument_id=?", args),
        "events": rows("SELECT * FROM model_events WHERE run_id=? AND instrument_id=?", args),
        "evidence": rows("""SELECT DISTINCT p.* FROM model_evidence p
            JOIN model_event_evidence l USING(run_id,evidence_id)
            JOIN model_events e USING(run_id,event_id) WHERE e.run_id=? AND e.instrument_id=?""", args),
        "actions": rows("""SELECT a.*, c.status AS current_status, c.assigned_to, c.version
            FROM model_actions a LEFT JOIN cases c USING(case_id)
            WHERE a.run_id=? AND a.instrument_id=?""", args),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--instrument-id", required=True)
    args = parser.parse_args()
    with closing(connect(args.db)) as db:
        print(json.dumps(inspect(db, args.run_id, args.instrument_id), indent=2))


if __name__ == "__main__":
    main()
