# Output Contract

The fixed structure of everything `preservation-loan-book` produces: the JSON result, the Excel workbooks (working file and board packet), the markdown brief and board packet, the queue CSVs, and the handoff payloads for sibling skills. The structure is the deliverable's contract; vary the content, not the shape. Column names repeat `pipeline-contract.md` Section 5 exactly. Units-at-risk and UPB-at-risk totals are computed once (`plb/units.py` -> `units_at_risk.json`) and read by the workbook and the brief; a test asserts the three agree.

## Contents

1. JSON result (full jsonc)
2. Excel workbook specification (working file)
3. Board packet (second workbook + markdown)
4. Markdown brief template
5. Lead card format
6. Queue CSVs
7. Handoff payload field maps
8. PII scopes applied to every output
9. Pipeline Mode checkpoint

---

## 1. JSON result

```jsonc
{
  "run": {
    "skill": "preservation-loan-book",
    "version": "1.0",
    "as_of_date": "YYYY-MM-DD",                       // date.today() unless --as-of
    "market_id": "us-or-multnomah",
    "agency_profile": "hfa | city_housing | county | pha_am | cdbg_home",
    "agency_name": "Oregon Housing and Community Services",
    "universe": "all | our_book | universe_not_held",
    "mandate_file": "references/sources/oregon-portland/mandate.json",
    "pii_scope": "organization",
    "book_coverage": "partial",
    "book_extract": "runs/2026-10-04/inputs/agency_servicing.csv | null",
    "horizon_years": 10,
    "regulatory_horizon_years": 10,
    "noah_watch": false,
    "include_proxies": false,
    "degraded": true,                                 // true when the book extract or forecast notice statuses are absent
    "degraded_reason": "book absent: capital factor 0 for all rows; outputs are preservation targeting and notice compliance only",
    "records_classification": "agency working file; disclosable subject to ORS 192.345/192.355 review; tenant data excluded by design",
    "header": "RECORDED n / REPORTED n / DERIVED n / ESTIMATED n / PROXY n / Suppressed n / Rejected n | helper deadlines n (notice arithmetic, LATEST duplicates; not counted above) | agency act-by n (next 90 days m)",
    "manifest_path": "runs/YYYY-MM-DD/manifest.json"
  },
  "geography": {
    "mode": "metro_core",
    "label": "Portland metro core (Multnomah, Washington, Clackamas)",
    "county_fips": ["41051", "41067", "41005"],
    "jurisdictions": ["Portland", "Gresham", "Beaverton"],
    "resolution_order": ["county_field", "zip_crosswalk", "point_in_polygon", "city_name_weak"],
    "rows_by_grade": {"county_field": 810, "zip_crosswalk": 0, "point_in_polygon": 0, "city_name_weak": 0},
    "sources_stopping_at_state_line": ["ohcs_oahi", "metro_rlis_affordable"]
  },
  "sources": [
    {"source_id": "agency_servicing_extract", "publisher": "the agency's own loan / grant system", "access": "manual", "verified_live": true,
     "vintage": "2026-10-04", "vintage_source": "header", "file": "agency_servicing.csv", "sha256": "string", "rows_ingested": 14, "rows_matched": 11, "events_emitted": 0,
     "caveats": ["RECORDED for our own loans; notice_log_status blank in n rows"]},
    {"source_id": "ohcs_oahi", "publisher": "Oregon Housing and Community Services", "access": "free-public", "verified_live": false,
     "vintage": "2026-10-02", "vintage_source": "filename", "file": "Oregon_Affordable_Housing_Inventory_20261002.csv", "sha256": "string",
     "rows_ingested": 1819, "rows_in_geography": 810, "events_emitted": 0, "caveats": ["expiration dates are regulatory, not loan maturities", "33 HUD dates already past -> STALE_CONTRACT_DATE"]}
  ],
  "assumptions": {
    "market_params_as_of": "YYYY-MM-DD",
    "cap_rate_affordable": {"value": 0.0675, "source": "derived", "verify": true},
    "senior_dscr_floor": 1.15,
    "recap_loan_rate": 0.0,
    "upb_at_risk_rule": "upb where any owner-cliff PRESSURE event <= 36 mo OR covenant_status in {watch, default} OR coterminous_senior_cliff",
    "band_rules": "Board_Totals and Units_by_Year band on owner_cliff_band; the queue sorts on action_band = min(agency act-by, owner cliff); bands are months",
    "equity_overlay": "absent; stacking_geography_equity modifiers scored 0",
    "statutory_text_status": "every cite verified_live: false in this build; confirm current text before sending",
    "av_is_market": false
  },
  "calendar_summary": { /* pipeline-contract.md Section 8 object */ },
  "summary": {
    "properties_in_geography": 810,
    "properties_with_event_in_horizon": 0,
    "book_rows": 14, "book_rows_monitored": 5, "book_rows_on_watch": 9,
    "book_join_grades": {"crosswalk": 1, "address": 9, "fuzzy": 1, "unmatched": 3},
    "book_match": {"matched": 11, "self_owned": 0, "unmatched_expected": 0, "not_in_extract": 799, "not_in_book": 0, "book_absent": 0},
    "queue_counts": {"ESCALATE": 0, "ACT": 0, "PLAN": 0, "WATCH": 0, "EXCLUDED": 0},
    "route_counts": {"optout_response": 0, "notice_compliance": 0, "qc_admin": 0, "designee_rofr": 0, "recap_committee": 0, "servicing_watch": 0, "nofa_offer": 0, "ta_sponsor": 0, "none": 0, "excluded": 0},
    "units_at_risk": { /* units_at_risk.json */ },
    "sponsor_exposure": [{"owner_org": "string", "properties": 0, "units": 0, "restricted_units": 0, "hap_units": 0, "public_upb": 0, "upb_share": 0.0, "cliffs_36mo": 0, "covenant_defaults": 0, "open_findings": 0, "sponsor_concentration": false}],
    "book_verdict": "STABLE | WATCH | STRESSED | CRITICAL",
    "owner_type_unknown_share": 0.0,
    "notice_log_unknown_share": 0.0,
    "data_gaps": [{"gap": "no agency servicing extract", "effect": "our_capital_at_risk 0 for every row; book_match book_absent", "fix": "run ingest_servicing_extract.py on the loan/grant system export"}]
  },
  "leads": [ { /* every column of pipeline-contract.md Section 5, same names, same order, plus factors{} from score_preservation.py factors_json */ } ],
  "book_watchlist": [ /* our_book leads incl. primary_route none */ ],
  "preservation_queue": [ /* universe_not_held leads */ ],
  "notice_compliance_queue": [ {"req_id": "PUSH-01", "property_id": "", "property_name": "", "statute_cite": "ORS 456.260 / OAR 813-115-0030 (owner notice no sooner than 30 months before withdrawal; (1)/(2) split unread) (verify)", "requirement": "", "window_start": "", "window_end": "", "due_date": "", "status": "", "evidence": "", "finding": "", "remediation_ask": "", "owner_response": "", "date_resolved": ""} ],
  "optout_qc_responses": [ /* leads with primary_route optout_response or qc_admin */ ],
  "agency_calendar": [ {"property_id": "", "property_name": "", "agency_action_type": "PUSH_FIRST_NOTICE_DUE", "due_date": "", "months_out": 0.0, "urgency_band": "", "basis": "DERIVED", "derived_from": "LIHTC_EXTENDED_USE_END 2029-06-01", "agency_owner": "push_program_manager", "statutory_cite": "ORS 456.260(1) (verify)", "status": "open"} ],
  "status_flips": [ {"property_id": "", "property_name": "", "flip_type": "notice_filed", "prior_value": "", "new_value": "", "evidence": "", "basis": "", "change": "escalated"} ],
  "rejects": [ {"property_key": "", "column": "", "raw_value": "", "reason": "", "flag": "Rejected — Out of Range", "alt_dates": []} ],
  "pipeline_not_scored": [ {"property_id": "", "property_name": "", "status": "In Development", "pointer": "map-progress-monitor / map-troubled-project-escalator"} ],
  "handoffs": {
    "critical-dates-tracker": "handoff/critical-dates-tracker.json",
    "front-door-lihtc-underwriting": "handoff/front-door-lihtc-underwriting.json",
    "sizing-lihtc-permanent-debt": "handoff/sizing-lihtc-permanent-debt.json",
    "physical-condition-assessment": "handoff/physical-condition-assessment.json",
    "lihtc-lpa-reviewer": "handoff/lihtc-lpa-reviewer.json",
    "sponsor-credibility-assessor": "handoff/sponsor-credibility-assessor.json",
    "off-market-deal-finder": "handoff/off-market-deal-finder.json"   // NOAH only
  }
}
```

## 2. Excel workbook specification (working file)

Build with openpyxl (`plb/workbook.py`); read `/mnt/skills/public/xlsx/SKILL.md` first when available and run its recalc script afterwards if present (do not fail when absent). File name pattern: `{Market}_{Mode}_Preservation_LoanBook_{horizon}yr.xlsx` (sample: `Portland_TriCounty_Preservation_LoanBook_10yr.xlsx`). Tab order is fixed.

| # | tab | contents | formatting |
|---|---|---|---|
| 1 | `Summary` | agency_profile and agency_name, geography object, horizon, calendar header verbatim (three segments), degraded statement, book_coverage and join-grade counts, book rows monitored vs on watch, pii_scope, records_classification banner, sources still `verified_live=false`, reject count (= Rejects_Verify rows), "bands are months, not days" | labels col A, values col B; inputs blue font `0000FF` |
| 2 | `Board_Totals` | rows: owner_cliff_band OVERDUE, CRITICAL, URGENT, APPROACHING, MONITOR, SCHEDULED, then `stale contract date — verify`, `no dated cliff`, `beyond horizon`, grouped by jurisdiction (county, then city); columns `properties, units_at_risk, hap_units_at_risk, prac_units_at_risk, other_ra_units, psh_units_at_risk, public_upb_at_risk, public_grant_at_risk, being_preserved_units`; pha_am variant swaps the two UPB columns for `owned_units, pbv_households, rad_section18_status`; below: `Units_by_Year` block (2026 ... 2036, same columns); KPI rows: units preserved since last run, units lost (evidence-based), book verdict STABLE / WATCH / STRESSED / CRITICAL (share of book UPB on watch/default and units with cliffs <= 24 mo) | totals row bold; stale row italic grey; every number traces to units_at_risk.json |
| 3 | `Intervention_Queue` | one row per lead with `primary_route` in the eight routes; col A `AM status` dropdown {New, Assigned, Letter Sent, Awaiting Response, Committee, Closed} (no free-text Notes column); front order: `queue_band, intervention_score, board_impact, primary_route, secondary_routes, universe, property_name, address, jurisdiction, units, units_at_risk, hap_units_at_risk, prac_units_at_risk, psh_units_at_risk, owner_name, owner_type, programs, agency_action_type, agency_action_date, owner_cliff_type, owner_cliff_date, owner_cliff_band, first_reg_event_type, first_reg_event_date, first_reg_months_out, first_reg_basis, first_reg_source, first_debt_event_type, first_debt_event_date, first_debt_months_out, first_debt_basis, first_debt_source, public_upb, our_maturity, affordability_end, covenant_status, am_officer, intervention, intervention_owner, statutory_cite, notice_status, verify_flags`, then the remaining Section 5 columns | freeze A2; autofilter; queue fill ESCALATE `F4CCCC`, ACT `FFEB9C`, PLAN `E7E6E6`, WATCH none; basis fill on `first_debt_basis`, `first_reg_basis`, `our_maturity_basis`, `senior_maturity_basis`, `agency_action_basis`: RECORDED `C6EFCE`, REPORTED `DDEBF7`, DERIVED `E2EFDA`, ESTIMATED `FFF2CC`, PROXY `E7E6E6` italic; widths property_name 32, address 30, owner_name 30, intervention 28, events_in_horizon 60, others 14 |
| 4 | `Book_Watchlist` | every `universe = our_book` row including `primary_route none` (AM status `Monitoring`): `agency_loan_ids, grant_ids, book_kind, agency_programs, public_upb, our_rate, payment_type, our_maturity, our_maturity_basis, affordability_end, recapture_type, recapture_method, recapture_amount, recapture_exposure, covenant_status, senior_lien_type, senior_maturity, senior_maturity_basis, senior_upb, coterminous_senior_cliff, am_officer, primary_route, queue_band, agency_action_type, agency_action_date` | basis fills; covenant_status default red-tint, watch amber |
| 5 | `Preservation_Queue` | every `universe = universe_not_held` row with the Intervention_Queue front order | queue fills |
| 6 | `Sponsor_Exposure` | normalized owner organization (case-folded): properties, units, restricted_units, hap_units, public_upb, upb_share, cliffs_36mo, covenant_defaults, open_findings, sponsor_concentration (upb_share >= 0.10 or cliffs_36mo >= 3) | concentration rows amber |
| 7 | `Notice_Compliance` | Req-ID rows: `PUSH-01` owner notice earliest date / designee trigger (ORS 456.260 / .262; OAR 813-115-0030, 30 months); `PUSH-02` owner notice latest date (24 months; the ORS 456.260 (1)/(2) split is unread); `PUSH-03` tenant notice SB 973 / ORS 456.259; `PUSH-04` applicant disclosure SB 973; `HAP-01` one-year tenant / CA notice 24 CFR 402.8; `HAP-02` 120-day opt-out package (Renewal Guide ch. 11); columns `req_id, property_id, property_name, statute_cite, requirement, window_start, window_end, due_date, status, evidence, finding, remediation_ask, owner_response, date_resolved`; every row cites the window and the statute with `(verify)` | status Breach red-tint, Open amber, Prep none, Satisfied green |
| 8 | `Agency_Calendar` | `property_id, property_name, agency_action_type, due_date, months_out, urgency_band, basis, derived_from, agency_owner, statutory_cite, status`; owner and cite from `AGENCY_DEADLINE_META` | OVERDUE red-tint; next 90 days amber |
| 9 | `Mandate_Fit` | per lead: `mandate_fit, mandate_eligible_products, mandate_ineligible_reason`, plus the mandate.json products table (product_id, status, eligible_programs, min_units, application_window, verified_live) | ineligible grey |
| 10 | `Events` | events.csv rows sorted by property then date; AGENCY_DEADLINE rows grouped after owner-side rows | basis fills; SUPPRESSION grey italic; STALE_CONTRACT_DATE italic with flag |
| 11 | `Regulatory` | programs, compliance_start, year15_date, extended_use_end, hap_expiration (+ confidence, detail, status), hap_renewal_request_status, hap_renewal_option, next_expected_expiration, usda dates, soft program ends, affordability_end, withdrawal_anchor_date, push_anchor_source, window start/end (first, second), notice_status, tenant_notice_status, qc_status, qc_waived, rofr_recorded, latest_end | basis fills |
| 12 | `Owners_Sponsors` | organization level: owner_name, owner_type, owner_archetype, developer_name, manager_name, registered_agent (labeled service address, not owner), registered_agent_address, sos_status, notice_address, notice_address_source, sponsor_contact_role, org_resolution_grade, sponsor_cliff_count, worklist reason | grade A green, B amber, C none; `Verify — Notice Address` rows flagged |
| 13 | `Book_Join_Gaps` | `book_join_gaps.csv`: property, expected_book_flag, reason, candidate matches (fuzzy ratio), suggested crosswalk row | |
| 14 | `Status_Flips` | `status_flips.csv` when `--prior` given, else a single note row | preserved green, lost red-tint, notice_filed amber |
| 15 | `Sources_Vintages` | source_id, file, sha256, vintage, vintage_source, file_verified, url_verified_live, verified_live, access, url, note | non-true verified `FFEB9C` |
| 16 | `Assumptions` | market-params.json flattened (name, value, as_of, source, verify); UPB-at-risk rule; band rules; equity overlay absence; records_classification; statutory text status | inputs blue |
| 17 | `Rejects_Verify` | rejects.csv rows plus lead-level verify_flags | |

Removed from v2: `Targets`, `Capital_Stack`, `Owners_DecisionMakers`, `Signals` (replaced by `Interventions` detail inside factors_json and the queue tabs), `Diff_vs_Prior` (replaced by `Status_Flips`).

## 3. Board packet (second workbook + markdown)

`--board-packet` (config `board_packet: true`) writes `{Market}_{Mode}_Board_Packet.xlsx` and `board_packet.md` in `pii_scope = public_packet`. Tabs: `Board_Totals`, `Preservation_Queue` (organization + registered agent + program facts only), `Sponsor_Exposure`, `Status_Flips`, `Redaction_Log` (field, rows redacted, cite ORS 192.355(2) / 192.345 (verify)), `Assumptions`. `board_packet.md` sections: title `# Preservation and Loan-Book Review — Board Packet: [agency_name] — as of [date]`; `## Book Verdict and Headline`; `## Units at Risk by Band and Jurisdiction`; `## Units by Year (10-year list)` (SB 32 fields: expiration, units, assistance type, income level, preservation status); `## Status Since Last Report`; `## Sponsor Concentration`; `## Redactions Applied`; `## Assumptions and Limits`. Natural-person owners print as "individual owner (name withheld; see internal file)"; residential registered-agent addresses are omitted; every redaction is logged.

## 4. Markdown brief template

Fixed section order. Quote the calendar header before any count. Bands are months.

```markdown
# Preservation and Loan-Book Review: [agency_profile] — [market_id] — as of [as_of_date]

## Run Summary
- Agency: [agency_name] ([agency_profile]) · geography_mode [mode] ([county FIPS list]) · horizon [10] years · universe [all]
- Files and vintages: agency_servicing_extract [vintage | absent]; ohcs_oahi [vintage]; hud_mf_assist_sec8 [vintage | absent]; ohcs_push_forecast [vintage | absent]; ...
- Basis breakdown: RECORDED n / REPORTED n / DERIVED n / ESTIMATED n / PROXY n / Suppressed n / Rejected n | helper deadlines n (notice arithmetic, LATEST duplicates; not counted above) | agency act-by n (next 90 days m)
- Book: coverage [partial]; joins crosswalk n / address n / fuzzy n / unmatched n; book rows monitored n vs on watch n; book_match unmatched_expected n
- Degraded run: [yes/no — e.g. "book absent: capital factor 0 for all rows; outputs are preservation targeting and notice compliance only"; which files would lift it]
- pii_scope [organization]; records_classification: agency working file; disclosable subject to ORS 192.345/192.355 review; tenant data excluded by design
- Urgency bands are months (OVERDUE / CRITICAL 0-12 / URGENT 12-24 / APPROACHING 24-36 / MONITOR 36-60 / SCHEDULED 60-120 / BEYOND), not critical-dates-tracker's days
- Notice log: n of m PuSH-covered rows have no notice_log_status (unknown) — reported, not scored
- Owner type unknown: n of m rows (SOS worklist)

## Board Totals
Book verdict: [STABLE | WATCH | STRESSED | CRITICAL] — [one-line reason]
[n] properties / [n] restricted units / [n] HAP units / [n] PRAC units / [n] PSH units / $[x] public UPB with an owner cliff inside 36 months
| owner_cliff_band | properties | units_at_risk | hap_units_at_risk | prac_units_at_risk | other_ra_units | psh_units_at_risk | public_upb_at_risk | public_grant_at_risk | being_preserved_units |
| OVERDUE | ... |
| CRITICAL | ... |
| URGENT | ... |
| APPROACHING | ... |
| MONITOR | ... |
| SCHEDULED | ... |
| stale contract date — verify | ... |
| no dated cliff | ... |
| beyond horizon | ... |
By county: [Multnomah ... / Washington ... / Clackamas ...]
Top 5 sponsors by exposure: [org — properties, units, $UPB, cliffs in 36 mo]

## Agency Act-By Calendar (overdue and next 90 days)
| due date | property | agency_action_type | agency owner | cite | derived from | status |

## Intervention Queue
[cards, Section 5 format, grouped by primary_route in precedence order (optout_response, notice_compliance, qc_admin, designee_rofr, recap_committee, servicing_watch, nofa_offer, ta_sponsor); action_band CRITICAL / URGENT / APPROACHING only; the rest summarized by band and route]

## Book Watchlist
[our_book rows: ids, book_kind, upb, payment_type, maturity (basis), affordability_end, covenant_status, am_officer, primary_route or "monitoring"]

## Preservation Queue (not in our book)
[universe_not_held rows above WATCH, with mandate_fit]

## Notice Compliance
| req_id | property | statute cite (verify) | window | due date | status | evidence | remediation ask |

## Mandate Fit
- Products open as of [as_of]: [product_id list]; eligible leads n; ineligible n (top reasons)

## Status Flips Since Last Run
| property | flip_type | prior | new | evidence | basis |
KPI: notice filed n · tenant notice confirmed n · QC requested n · QC presented n · HAP renewed n · loan extended n · loan recast n · covenant cured n · recap closed n · preserved n (units) · lost n (units, evidence-based)

## Pipeline, not scored
- n rows Status = In Development -> map-progress-monitor / map-troubled-project-escalator

## Data Gaps and Verification Queue
- Stale contract dates: n (request current HAP contract / TRACS)
- Notice log unknown after due date: n (Verify — Notice Log)
- CA log unknown after opt-out notice deadline: n (Verify — CA Log)
- Book join gaps: n (Verify — Book Join; suggested crosswalk rows)
- Documents to request from our own file room: n (feeds critical-dates-tracker)
- SOS worklist: n organizations

## Assumptions, Statutory Cites and Limits
- Every statutory cite in this run is verified_live: false; confirm current text before sending any letter
- UPB-at-risk rule; band rules (owner_cliff_band for totals, action_band for the queue); equity overlay [present | absent]
- Market params as of ...; cap_rate_affordable (verify); senior_dscr_floor 1.15; recap_loan_rate 0.0
- Proxy-only leads capped at PLAN; no inferred maturities; the agency's own ledger is RECORDED
- Sources not verified live: ...
```

## 5. Lead card format

```markdown
### [#n] [property_name] — [jurisdiction]  Route [notice_compliance] Queue [ESCALATE] Score [78] Units at risk [96] Public UPB $[1,200,000]
- Units [120] · restricted [96] (units_basis total_assumed_restricted) · HAP [0] · PRAC [0] · other RA [12] · PSH [8] · flags [elderly]
- First agency act-by: [PUSH_FIRST_NOTICE_DUE 2026-12-01 [DERIVED] — 1.9 months · owner push_program_manager · ORS 456.260 / OAR 813-115-0030 (owner notice no sooner than 30 months before withdrawal) (verify)]
- Owner cliff: [LIHTC_EXTENDED_USE_END 2029-06-01 [REPORTED] ohcs_oahi:LIHTC_9_Expiration_Date — 31.9 months] · [next_expected_expiration for annual HAP]
- Declared intent / notice status: [notice_status unknown · tenant_notice_status n/a_pre_operative · hap_renewal_request_status n/a · recap_status none]
- Our position: [loan OHCS-2014-0117 (loan) · $1,200,000 residual_receipts · matures 2031-06-30 [RECORDED] · affordability_end 2029-06-01 · recapture none · covenant_status current · am_officer J. Rivera] | "not in book" | "expected in book — join missing (Verify — Book Join)" | "book absent"
- Physical: [REAC 72 (NSPIRE) 2025-11 · no open findings]
- Sponsor capacity: [lihtc_partnership_forprofit_gp · Village Garden, LLC · SOS Active · agent change 2025 · sponsor_cliff_count 1]
- Intervention: [push_window_prep — push_program_manager — ORS 456.260 / OAR 813-115-0030 (verify; confirm current text before sending) — owner notice: not yet (prep) · tenant notice: n/a — notice address: [from regulatory_agreement]]
- Evidence: [evt ids with basis]
- Verify before acting: [notice log at PuSH-CP; LURA/REUA end date from our file; current HAP contract]
- Handoffs ready: [critical-dates-tracker; front-door-lihtc-underwriting]
```

## 6. Queue CSVs

Written by `score_preservation.py` (and `diff_forecast.py`, `build_universe.py`) into the run directory:

| file | columns | source |
|---|---|---|
| `notice_compliance_queue.csv` | `req_id, property_id, property_name, jurisdiction, units_at_risk, statute_cite, requirement, window_start, window_end, due_date, status, evidence, finding, remediation_ask, owner_org, registered_agent, notice_address, notice_address_source, owner_response, date_resolved` | Notice_Compliance tab |
| `nofa_targets.csv` | `property_id, property_name, jurisdiction, units_at_risk, hap_units_at_risk, psh_units_at_risk, owner_cliff_type, owner_cliff_date, owner_cliff_band, owner_type, mandate_eligible_products, recap_gap_estimate (our_book only), intervention` | nofa_offer primary or secondary |
| `agency_calendar.csv` | Agency_Calendar tab columns | `plb/agency_calendar.py` |
| `sponsor_exposure.csv` | Sponsor_Exposure tab columns | `score_preservation.py` |
| `servicing_unmatched.csv` | every servicing extract column + `book_join_grade unmatched` + candidate fuzzy matches | `merge_leads.py` / `plb/book_join.py` |
| `book_join_gaps.csv` | `property_id, property_name, expected_book_flag, reason, candidate_agency_loan_id, candidate_ratio, suggested_crosswalk_row` | `plb/book_join.py` |
| `status_flips.csv` | `property_id, property_name, flip_type, prior_value, new_value, evidence, basis, change` (`change` is the v2 enum new / escalated / de_escalated / retired) | `diff_forecast.py` |
| `units_at_risk.json` | Section 8 object | `plb/units.py` via `score_preservation.py` |

## 7. Handoff payload field maps

`scripts/make_handoffs.py` writes one JSON per sibling for the routes in `handoff_routes` (default: every route except `none`). Each file: `{"from": "preservation-loan-book", "as_of": "...", "agency_profile": "...", "count": n, "items": [{"property_id", "property_name", "queue_band", "primary_route", "payload"}]}`. Field names for `lihtc_context` are identical to v2 so both skills produce the same shape.

| sibling | when | item payload |
|---|---|---|
| `critical-dates-tracker` | every route | `seed_dates: [{event_type, date, basis, source}]` (owner cliffs and agency act-by dates, each with basis), `documents_to_request: [...]` — one entry per non-RECORDED governing event; for book loans the documents are the agency's own note, trust deed, regulatory agreement, HAP contract and grant agreement, so the request goes to the agency's file room (including the notice clause), not to the owner; note the scale difference: this pack's bands are months |
| `front-door-lihtc-underwriting` | recap_committee, nofa_offer | `composition_mode: true`, `lihtc_context: {credit_type, compliance_start, year15_date, extended_use_end, ami_units: {30, 40, 50, 60, 80, market}, hud_contract, hap_expiration, soft_debt_sources: [], sponsor_type, qc_eligible, preservation_notice_status}`, `agency_soft_debt: [{agency_loan_id, program, upb, rate, payment_type, maturity, affordability_end, recapture_type}]`, `existing_debt: {upb, rate, maturity, basis, lender_type: senior_lien_type}` |
| `sizing-lihtc-permanent-debt` | recap_committee, servicing_watch with a recast question | two scenarios `{scenario: before_recast | after_recast, noi_year1: est_restricted_noi, noi_source, mandatory_soft_debt_annual, residual_receipts_soft_debt, lender_type: state_HFA, state_hfa, dscr_floor: senior_dscr_floor, dscr_floor_source: agency_program_manual}`; consume `max_loan`, `binding_constraint` |
| `physical-condition-assessment` | physical_reac_occupancy fired | `{property_address, year_built, unit_count, deal_strategy: preservation_rehab}`; consume `conditionScore` and 5-year CapEx as rehab-need input; label ESTIMATED/DERIVED; not the program CNA |
| `lihtc-lpa-reviewer` | designee_rofr, recap_committee with an LPA on file | `{deal_name, deal_state, document_type: full_lpa, gp_entity, lp_investor, review_focus: ["2C"]}`; consume `agent_findings.2C_year_15_exit_rofr` (`rofr_42i7_compliant`, `exit_provisions[]`) as RECORDED evidence for sponsor_capacity and declared intent; never adopt its developer-advocate posture |
| `sponsor-credibility-assessor` | only when `recap_status` in {announced, under_application} or TA requested (trigger recorded in payload) | `{organization, type: nonprofit \| pha \| for_profit, portfolio_year15_30_events_36mo: sponsor_cliff_count, compliance_flags: [REAC, 8823], target_deal: {units, credit_type, recap}, trigger}`; consume Dimension 3 (track record) only |
| `off-market-deal-finder` | NOAH only | `{asset_class: market_rate_mf, geography, property_ids, owner_outreach: false, purpose: public_acquisition_screen}` |

Also written: `documents_to_request.csv` (`property_id, property_name, queue_band, event_type, event_date, basis, document, where_to_get, est_cost`; `DOC_FOR_EVENT` adds AGENCY_LOAN_MATURITY -> our note / loan agreement, AFFORDABILITY_PERIOD_END -> HOME written agreement, GRANT_RECAPTURE_END -> grant agreement, HAP_EXPIRATION -> HAP contract / renewal request (HUD-9624), QC_ELIGIBILITY -> QC price certification, STALE_CONTRACT_DATE -> current HAP contract / TRACS; `where_to_get` is "agency file room" for our_book rows), `sos_worklist.csv` (`owner_name_raw, normalized_name, state, registry_search_url, reason, property_ids`; organization level) and `board_packet.csv` (organization + registered agent + program facts, pii_scope public_packet).

## 8. PII scopes applied to every output

`plb/pii.py` `apply_pii_scope(df, scope)` runs on every CSV, JSON, workbook and markdown writer (`pii-and-sunshine.md`). NEVER columns (dropped at adapter write): `owner_phone, owner_email, cell, personal_email, decision_maker_name, skip_trace_*`. INTERNAL-only (`--internal`): `am_officer_email`, `officer_names` (SOS / 990 only). ORGANIZATION (default): everything else including `am_officer`. PUBLIC_PACKET allow-list: property identity, programs, units*, dates / bases, owner organization, registered_agent (+ business address), route, intervention, statutory_cite, flags; natural-person owner names and residential registered-agent addresses redacted and logged. The manifest records `pii_scope` and `records_classification`.

## 9. Pipeline Mode checkpoint

`data/status/{market_id}/asset_management/preservation-loan-book.json`:

```jsonc
{
  "agent": "preservation-loan-book",
  "phase": "asset_management",
  "market_id": "us-or-multnomah",
  "status": "COMPLETE | PARTIAL | FAILED",
  "as_of": "YYYY-MM-DD",
  "payload": {
    "result_json": "path", "workbook": "path", "board_packet": "path", "brief": "path",
    "queue_counts": {"ESCALATE": 0, "ACT": 0, "PLAN": 0, "WATCH": 0, "EXCLUDED": 0},
    "units_at_risk_headline": {"properties": 0, "units_at_risk": 0, "hap_units_at_risk": 0, "psh_units_at_risk": 0, "public_upb_at_risk": 0},
    "book_verdict": "STABLE",
    "degraded": true,
    "handoffs": {}
  }
}
```

Append a line to `data/logs/{market_id}/asset_management.log` with timestamp, status and the calendar header.
