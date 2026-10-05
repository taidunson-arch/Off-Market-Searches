# Real-agency validation protocol

**Current status: not run against a real agency book.** The available servicing
fixtures are synthetic and the public inventory is not an independent agency
subledger. Passing software tests does not establish reconciled real balances,
reviewed legal rules, predictive performance, or agency acceptance.

## Required intake

Copy `validation-intake/` to a private working directory outside the repository.
Do not put borrower records, agency decisions or completed review evidence in a
public Git repository. The templates contain headers and empty policy values;
they are not sample agency evidence and cannot grant acceptance as shipped.

1. An authorized servicing extract and property/instrument crosswalk sufficient to
   run the pipeline. Use one agency and one explicitly dated snapshot.
2. `controls.csv`: an independently obtained accounting/subledger control tape,
   approved by the agency controller or delegate. Include every in-scope instrument,
   its property, kind, program, loan principal and applicable grant recapture basis.
   Record source, as-of, reviewer and evidence reference in `package.json`.
3. `rule_reviews.csv`: the agency's substantive review of all five runtime rule
   categories, with jurisdiction, reviewer, evidence, effective dates and exact
   `bundle_sha256` values from the run's `rule_inventory.json`.
4. `decisions.csv`: independently adjudicated property/dimension judgments based on
   evidence available by the snapshot date, with reviewer, rationale and references.
   Freeze judgments without exposing the model's predictions to reviewers.
5. An agency-approved acceptance policy and sampling plan fixed before evaluation.
   Enter sample-size requirements and maximum error/abstention rates for each axis.
   Do not choose thresholds after seeing the holdout results.

Public inventory can help check property coverage; it cannot substitute for these
accounting, policy and decision controls.

## Reconciliation

```sh
python scripts/run_agency_pipeline.py --config private_run_config.json
python scripts/validate_book.py --run-dir COMPLETED_RUN --package PRIVATE/package.json --out PRIVATE/validation-report.json
```

The run must be COMPLETE and its as-of date must match the validation package.
All money is compared in integer cents. Unknowns remain unknown. Duplicate IDs,
missing instruments, wrong property/kind/program links and per-instrument balance
differences stop the reconciliation from passing. Offsetting errors do not cancel.
The declared tolerance is an integer number of cents per instrument, default zero.

The report provides counts and balance rollups by kind and program. Loan UPB is
principal. Grant `recapture_amount` is the contractual recapture basis, **not** a
loan balance, award amount, loss estimate or modeled current recapture exposure.
Provide a supported basis from the grant record; an unknown basis is a gap rather
than zero. Contract and owned-asset records participate in identity/count controls.
All monetary controls in this version are USD.

Assessments are checked against properties in the independent control tape.
Missing assessment rows become unknown predictions and block signoff readiness.
Outside inventory does not enlarge the validation denominator. Input files and
the completed run artifacts receive SHA-256 fingerprints in the report. A control
file located inside the generated run directory is rejected as independent evidence.
File hashes do not prove source independence; that remains an agency attestation.

## Rule review

Every new pipeline run writes `rule_inventory.json` with the exact engine and
configuration fingerprints for:

- preservation calendar;
- financial thresholds;
- readiness gates;
- grant recapture terms;
- intervention mandate and legacy routing inputs.

All categories require a matching APPROVED human review record for the declared
jurisdiction and effective period. Missing configuration, missing review, expired
review, a future review date or a changed fingerprint blocks readiness for signoff.
An old review cannot silently approve changed code or a changed threshold file.

The review register must represent substantive agency review: policy owners review
financial/readiness rules and qualified agency staff or counsel review applicable
legal/calendar/recapture obligations. The tool matches attestations; it neither
authenticates the named reviewer nor determines whether their legal conclusion is
correct. Existing unverified rule text must not be relabeled approved without that
review. Runs created before rule inventories were added must be regenerated.

## Adjudication and measurement

Each decision row has one `property_id`, one `axis`, the snapshot `as_of`, a boolean
`expected_attention`, reviewer/date, evidence cutoff, rationale and evidence reference.
Valid axes and the positive class are:

| Axis | Positive means | Unknown prediction |
|---|---|---|
| preservation_urgency | Owner-side cliff within 36 months, including overdue | UNKNOWN/unrecognized calendar status |
| financial_risk | Current financial WATCH/default signal | UNKNOWN/unrecognized financial status |
| data_confidence | Verification/data-gap work is needed | Unrecognized confidence status |
| intervention_readiness | Readiness work remains, including an absent review | Unrecognized readiness status |

Readiness-gap positives are not predictions of asset failure. Adjudicate each axis
against its own definition. The decision evidence cutoff must be no later than the
snapshot date; a later review may examine those historical records, but future
financial facts cannot be used as if known at the snapshot. Duplicate judgments for
one property/axis are rejected. Resolve reviewer disagreements before freezing the
adjudicated file; retain that resolution in the evidence reference.

For each axis the report includes TP, FP, TN, FN, positive/negative abstentions,
sample sizes, review coverage and unreviewed-property counts:

- Precision = TP / (TP + FP).
- Recall = TP / all adjudicated positives, including positive abstentions.
- Missed risks = FN + positive abstentions; missed-risk rate uses all positives.
- False-alarm rate = FP / (FP + TN), among classified negative judgments.
- Abstention rate = all unknown predictions / all reviewed judgments.

Zero-denominator rates are null, never zero or perfect. Unknown true risks count
as missed risks. Negative abstentions remain explicit and are constrained by their
own acceptance criterion. Review coverage includes unreviewed properties so a small
convenient subset cannot look like a complete book review. Case results support
follow-up on false alarms, misses and unknowns.

Intervals are descriptive 95% Wilson binomial intervals. Selection bias, correlated
properties, unusual program mixes and nonrandom sampling can invalidate population
interpretation. The measurements describe the reviewed sample, not independently
observed realized losses or causal intervention effectiveness. A targeted high-risk
sample is useful diagnostically but cannot reach signoff readiness. Census sampling
requires complete per-axis coverage; a declared random holdout requires its sampling
plan evidence and must meet predeclared minimum positive and negative counts.

## Acceptance boundary

The result is BLOCKED unless reconciliation, matching rule review, label integrity,
sampling/independence declarations and every supplied acceptance criterion pass.
Each axis requires minimum reviewed, positive and negative counts plus maximum
missed-risk, false-alarm and abstention rates. Empty criteria cannot pass.

A technically passing package is only READY_FOR_AGENCY_SIGNOFF. It does not itself
approve deployment, certify legal compliance or establish that the system is best
in class. Reviewers and sampling design are supplied attestations; the local tool
does not authenticate them. The agency must inspect breaks, difficult cases,
confidence intervals and policy judgments, record a signed acceptance decision,
then monitor performance on later books without tuning on the held-out judgments.

The older `--controls` mode remains an aggregate diagnostic for compatibility. Its
PASS output is explicitly labeled aggregate-only and is not real-book acceptance.

Malformed or nonfinite input returns INVALID_INPUT with a nonzero exit code. The CLI
atomically replaces any prior report, so a failed attempt cannot leave an old
success report in place.
