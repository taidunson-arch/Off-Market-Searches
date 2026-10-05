# HFA operations: integrity release and pilot workflow

## What is implemented

1. **Integrity corrections.** Book verdicts use agency-book denominators. Empty or materially incomplete data cannot produce a STABLE verdict. Unresolved overdue obligations remain visible. Grants retain their own terms and calculate recapture separately before summing. Duplicate identical instruments are counted once; conflicting identities stop processing. Failed stages stop publication.
2. **Instrument foundation.** `instruments.csv` contains stable kind-qualified IDs, individual terms, source vintage and recapture exposure. `covenants.csv` contains separate obligation rows with status and period endpoints. [The version-2 instrument model](instrument-model.md) links those obligations to events, source evidence and actions; `book_model.json` is the complete graph. The full structured positions remain in `instruments_json` on the working lead and in `result.json`. These covenant summaries do not yet encode every legal clause or borrower obligation.
3. **Local case workflow.** [Persistent case management](case-management.md) adds manual instrument-linked cases, named escalation, controlled work deadlines, immutable evidence and review decisions, and a full case view. Set `operations_db` to an agency-specific SQLite path. Successful runs persist property, instrument, covenant and event snapshots and create durable cases from agency deadlines. Imports do not reopen closed cases or silently delete missing cases. Changes require an expected version, record an audit entry, and require a different reviewer to approve completion. This local tool does not provide authentication, tenant isolation, document storage or a multiuser web interface.
4. **Separate risk dimensions.** [Four independent assessments](risk-dimensions.md) now lead the staff queue, brief, board packet and separate attention lists. `risk_dimensions.csv` and `result.json` expose preservation urgency, financial condition, data confidence and intervention readiness separately. No financial observations means UNKNOWN, even with long-dated restrictions. Supplied financial thresholds are agency policy, not a calibrated predictive model. The original intervention score remains available for compatibility.
5. **Acceptance harness.** The [real-agency validation protocol](agency-validation.md) adds instrument-level controls, fingerprinted human rule reviews and measured missed risks/false alarms with explicit abstentions and review coverage. Real-agency acceptance remains pending. `validate_book.py` compares generated results to independent control totals and adjudicated property cases. Synthetic tests pass only synthetic acceptance; they do not certify a real HFA book or legal rules.

## Run publication and migration

Run `python scripts/run_agency_pipeline.py --config run_config.json` from this skill directory.
All configured paths should be absolute for reproducibility.

Each attempt writes to `<out_dir>/<as_of>/<unique_run_id>/`. After successful generation,
`<out_dir>/<as_of>/latest.json` atomically points to the completed run. Read its `run_dir`;
do not assume outputs are directly in the date directory. `last_attempt.json` reports
the newest attempt, including failure; a failed attempt does not replace the last good pointer.
Failed attempt diagnostics are in its `failure.json`.

Unsafe partial restarts (`--from score`, etc.) are rejected. Re-run the full pipeline.
`--prior-run` must point to a completed run directory, not the parent date directory.
Keep old outputs for reproducibility; no automatic deletion is performed.

Add to the normal run configuration:

```json
{
  "agency_profile": "hfa",
  "operations_db": "C:/agency/preservation/agency.sqlite",
  "financial_observations": "C:/agency/inputs/financial_observations.csv",
  "financial_policy": {
    "version": "HFA-review-required-example",
    "max_age_days": 365,
    "min_dscr": 1.10,
    "max_days_past_due": 30,
    "min_occupancy": 0.90,
    "min_reserve_funded_ratio": 1.0
  }
}
```

The example thresholds are illustrative. Replace them with approved agency policy.
Omit financial inputs if unavailable; the output will identify the missing information.
The optional observations CSV uses `property_id,period_end,source,dscr,days_past_due,occupancy,reserve_funded_ratio`.
Occupancy and reserve ratios are fractions. History is retained in `financial_history.json`;
only the latest period on or before the run date informs that run. Conflicting duplicate
periods and properties outside the run's scored population stop the run.

## Work a case

```text
python scripts/manage_cases.py --db C:/agency/preservation/agency.sqlite list --as-of 2026-10-04
python scripts/manage_cases.py --db C:/agency/preservation/agency.sqlite change CASE_ID assign --actor supervisor --version 1 --value officer
python scripts/manage_cases.py --db C:/agency/preservation/agency.sqlite change CASE_ID start --actor officer --version 2
python scripts/manage_cases.py --db C:/agency/preservation/agency.sqlite change CASE_ID submit --actor officer --version 3 --evidence document-reference
python scripts/manage_cases.py --db C:/agency/preservation/agency.sqlite change CASE_ID approve --actor reviewer --version 4 --evidence approval-reference
python scripts/manage_cases.py --db C:/agency/preservation/agency.sqlite audit CASE_ID
```

Use the actual version returned by `list`. Escalate, cancel and reopen require evidence
or a documented reason. Actor strings are attribution only; users with direct database
access are trusted. Evidence references are recorded, not independently retrieved or validated.
Completing a local case does not amend the agency's source ledger or automatically resolve
an underlying loan maturity. Correct source records remain necessary on later runs.

## Real-HFA acceptance gate

Obtain an authorized servicing/grant export, financial statements or normalized observations,
source documents, approved thresholds, and independent totals from the HFA. Require a reviewed
crosswalk and investigate every rejected or unmatched instrument before sign-off.

Controls JSON example (replace every illustrative value):

```json
{
  "source": "HFA servicing control report and AM review, period ending ...",
  "reviewer": "authorized reviewer",
  "totals": {"book_properties": 100, "instruments": 150, "public_upb": 50000000, "unknown_loan_balances": 0},
  "dollar_tolerance": 0.01,
  "adjudicated_cases": [
    {"property_id": "actual-canonical-id", "expected": {"financial_risk": "WATCH", "preservation_urgency": "URGENT"}}
  ]
}
```

```text
python scripts/validate_book.py --run-dir COMPLETED_RUN --controls controls.json --out reconciliation.json
```

The command exits nonzero on a mismatch. It does not learn weights or certify legal deadlines.
Review missed risks, false alerts, stale observations, control-total gaps, and staff disposition
over consecutive periods before changing the score or calling the system production-ready.

## Remaining institutional work

- Counsel-approved, effective-dated rule registry and program applicability before authoritative legal calendars.
- Real HFA reconciliation and outcome-based calibration; no real servicing book is included in this repository.
- Full instrument-level payment histories, financial statement ingestion, covenant tests and capital-needs models.
- Authenticated service, role permissions, agency isolation, backups, retention, document access and deployment.
- A staff interface and complete origination/closing integration with the agency's systems of record.

The current release supplies a tested local foundation for these additions; it does not claim they are complete.
