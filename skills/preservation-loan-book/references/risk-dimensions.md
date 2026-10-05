# Four independent assessments

The agency workflow presents preservation urgency, financial risk, data confidence
and intervention readiness separately. It does not average them or use one axis
to reduce another. Each property can appear in multiple attention lists.

| Dimension | Question | Basis and limits |
|---|---|---|
| Preservation urgency | How soon is the owner-side preservation cliff? | Existing calendar bands computed from the owner-cliff date; UNKNOWN when no usable date/band exists |
| Financial risk | Does current evidence breach an agency threshold? | DSCR, days past due, occupancy and reserve funding compared with versioned agency policy |
| Data confidence | What evidence needs verification or completion? | Missing preservation dates/source basis, source verification flags, financial completeness/freshness and policy coverage |
| Intervention readiness | What prevents staff from advancing an intervention? | Dated staff review of authority, owner engagement, funding, documents and staff capacity, plus mandate/verification gates |

An urgent preservation cliff remains urgent when financial statements are missing.
A DSCR breach remains visible when restrictions extend another 15 years. A blocked
intervention stays blocked even if a legacy score is high. Covenant status is shown
as context; a generic covenant default alone is not treated as payment default.

## Financial evidence and policy

Configure `financial_observations` with a CSV path. Required columns are
`property_id,period_end,source`; supported numeric columns are
`dscr,days_past_due,occupancy,reserve_funded_ratio`. Occupancy is a fraction in [0,1],
not a percentage. Reserve funding is a ratio and can exceed 1. Values must be finite.
Negative DSCR is allowed; negative delinquency, occupancy or reserve ratios are not.

The latest observation dated on or before `as_of` is selected per property. Later
records stay in the history and do not affect the current assessment. Conflicting
observations for one property/period fail validation. A newer partial observation
does not silently borrow missing figures from an older period.

The `financial_policy` configuration object must name its version. For example,
these are demonstration thresholds, not recommended underwriting policy:

```json
{
  "version": "agency-approved-demo-v1",
  "max_age_days": 365,
  "min_dscr": 1.1,
  "max_days_past_due": 30,
  "min_occupancy": 0.9,
  "min_reserve_funded_ratio": 1.0
}
```

Current evidence breaching any configured threshold gives WATCH. All four metrics
and all four rules must be present on current evidence before the result can be
NO_CONFIGURED_BREACH. That label is not a credit rating or guarantee of health.
Missing policy, incomplete evidence without a known current breach, stale evidence,
and future-only evidence yield UNKNOWN. Historical breaches remain in the reasons
but do not become claims about current condition. Freshness defaults to 365 days
when not explicitly configured; the policy version and actual source/period are
included in every result.

## Readiness review

Configure `readiness_observations` with a CSV containing:

```csv
property_id,reviewed_on,source,authority_confirmed,owner_engaged,funding_identified,documents_complete,staff_capacity_confirmed
PROPERTY_ID,2026-10-01,staff-review-123,true,true,false,true,true
```

Gates accept true/false, yes/no, blank or unknown. The latest nonfuture review is
selected; conflicting same-day reviews fail. A review older than 180 days requires
verification under assessment version `four-dimensions-v1`.

- UNASSESSED: no review supplied.
- NEEDS_INPUT: one or more gates are unknown.
- BLOCKED: a current gate is false, or the proposed intervention is mandate-ineligible.
- REQUIRES_VERIFICATION: the review is stale or unresolved source/action verification
  prevents relying on an otherwise complete review.
- READY_FOR_REVIEW: all five staff-reported gates are met and no configured blocker
  is present. This does not approve the action or close its case.

Readiness evidence is staff-reported. Source availability does not establish legal
authority or document authenticity. Financial/preservation data confidence remains
separate from readiness gate status; source-specific gaps explain each result.

## Staff and board outputs

The four assessments and reason columns lead `leads_scored.csv` and the staff queue.
Default row order follows preservation urgency, then property ID. It is explicitly
not a composite priority ranking; use the separate attention lists for the other
review needs:

- `preservation_attention.csv`: owner cliffs within 36 months, including overdue.
- `financial_attention.csv`: current configured financial breaches, regardless of
  preservation horizon or legacy routing exclusions.
- `data_gaps_attention.csv`: incomplete or unverified assessment evidence.
- `readiness_gaps_attention.csv`: work not yet READY_FOR_REVIEW.

The working workbook and public board packet include `Risk_Dimensions`,
`Preservation_Attention`, `Financial_Attention`, `Data_Gaps` and `Readiness_Gaps`.
The main brief and board summary include separate dimension summaries. Workbook
privacy rules also apply to these sheets and the CSV attention lists. Public packets retain assessment labels and safe summary reasons; detailed source references and staff assessment notes remain in the staff file.

`risk_dimensions.json`, `risk_dimensions.csv` and `result.json.risk_dimensions`
carry assessment version, as-of date, source periods, financial policy version,
reasons and machine-readable `dimension_explanations_json`. The latter retains
individual financial breaches and blocked/unknown readiness gates.
`dimension_counts.json` and `result.json.dimension_counts` count each axis
independently. `financial_history.json` and `readiness_history.json` retain supplied
observations, including future-dated rows excluded from assessment.

For direct scoring, supply `--financial-observations`, `--financial-policy` (a JSON
file) and `--readiness-observations`. Pipeline configuration accepts the two CSV
paths and the financial policy object. Unknown property IDs fail rather than attach
evidence to a guessed property. The pipeline records input hashes for both CSVs.

## Compatibility

The existing `intervention_score`, `queue_band`, legacy route suggestions and
`board_impact` remain available for older consumers. They do not determine the
new assessment results, attention-list membership or default ordering. Staff
workbooks label score fields `legacy_*`; the brief labels old route suggestions.
Book verdicts and units-at-risk totals retain their existing preservation/coverage
meaning and should not be read as financial-health ratings.

These are explainable screening assessments, not a calibrated loss model. Thresholds,
readiness judgments and real-book acceptance still require the agency's review.
