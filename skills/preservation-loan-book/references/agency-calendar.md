# Agency Calendar: the dates the agency must act

Owner cliffs tell the board what is at risk; agency act-by dates tell the asset manager what to do this month. `plb/agency_calendar.py` derives both from the merged universe, emits every `AGENCY_DEADLINE` event, the two PuSH windows and `NOTICE_COMPLIANCE_BREACH`, and stamps `STALE_CONTRACT_DATE` statuses. The notice-deadline trap from `critical-dates-tracker` applies on the agency side: urgency runs off the act-by date, not the owner's cliff, so `action_band = min(agency act-by, owner cliff)` drives the queue sort while `Board_Totals` band on `owner_cliff_band`.

Every statutory figure below is unverified in this build (`verified_live: false`); the pack's `legal-timelines.md` carries the same banner and the AGENCY_DEADLINE_META table repeats the cite on every row. Months are 30.4-day months as everywhere in the pack; bands are months, not days.

## Contents

1. The withdrawal anchor
2. Derivations
3. Stale contract dates
4. AGENCY_DEADLINE_META
5. Notice window states and the breach rule
6. Surfaces (header, tab, brief, card)
7. Worked examples (Oregon, as of 2026-10-04)

---

## 1. The withdrawal anchor

`withdrawal_anchor_date` = max of restriction-type ends only: LIHTC_EXTENDED_USE_END, SOFT_PROGRAM_END, AFFORDABILITY_PERIOD_END, COVENANT_END, USDA_515_MATURITY, HUD use-agreement end. A HAP / PRAC / PAC expiration enters the anchor only with a non-renewal signal: PRESERVATION_NOTICE_RECEIVED detail hap_optout, a CA log opt-out, `hap_renewal_request_status = not_received`, or HAP_EXPIRATION detail mahra_20yr term ending. `push_anchor_source` in {restriction_end, hap_nonrenewal_signal, none} is stored on the window event.

Why: in the 2026-10-02 OHCS metro file 27 of the 61 LATEST dates inside 60 months are driven by an annual HUD contract date, and 33 HUD dates are already past. Anchoring a 30-month statutory notice on a date that rolls every year would put most of the HAP stock permanently "in breach". The withdrawal the statute regulates is the end of the restriction, so that is the anchor; an opt-out is a declared intent and enters the anchor as such.

PuSH derivations are gated on units >= 5, programs intersecting `PUSH_COVERED_PROGRAMS`, the profile having `receives_push_notice` or `is_qualified_purchaser`, and an anchor being present. A HAP-only property with an annual date eight months out therefore emits no PuSH window and no breach.

## 2. Derivations

All DERIVED unless anchored on a RECORDED log date (then the deadline is still DERIVED but its anchor is RECORDED; the card shows both).

| event | formula | pack parameter (market-params.json) | cite (verify) |
|---|---|---|---|
| PUSH_WINDOW_PREP | anchor - 36 mo | `push_window_prep_months` 36 | INTERNAL prep date with no statutory basis found: the only rule text surfaced (OAR 813-115-0030 summary; ORS 456.260 summary) says the owner's notice is given "no sooner than 30 months prior and at least 24 months prior" to withdrawal; 36 months is SB 973's TENANT-notice outer bound |
| PUSH_FIRST_NOTICE_DUE | anchor - 30 mo | `push_first_notice_months` 30 | ORS 456.260 / OAR 813-115-0030: earliest owner-notice date; ORS 456.262 lets OHCS appoint a designee after the owner's notice OR 30 months before expiry, whichever is earlier (not conditioned on non-compliance). Reading: "the clock has not started; designee appointment available", not a statutory breach |
| PUSH_SECOND_NOTICE_DUE | anchor - 24 mo | `push_second_notice_months` 24 | ORS 456.260 / OAR 813-115-0030: owner notice at least 24 months before withdrawal; the (1)/(2) split and the 30-after-(1) / 24-after-(2) withdrawal bar in ORS 456.262 are unread |
| TENANT_NOTICE_WINDOW | anchor - 36 .. - 30 mo; only when anchor >= `sb973_operative_restriction_date`, else `tenant_notice_status = n/a_pre_operative` | `tenant_notice_months` [36, 30]; `sb973_operative_restriction_date` | SB 973 (2025) / ORS 456.259 |
| PRESERVATION_NOTICE_WINDOW (helper, two rows) | [anchor - 36, anchor - 30] detail push_first_window (internal prep window); [anchor - 30, anchor - 24] detail push_second_window (the owner-notice period as understood) | `push_program_coverage_verified` false -> HOME-only / LIHTC-only rows carry `Verify — PuSH Coverage` | OAR 813-115-0030 (30 / 24 months); OAR 813-115-0010 covered programs unread |
| RECORDS_REQUEST_DUE | PRESERVATION_NOTICE_RECEIVED + 10 d | `records_request_after_notice_days` 10 | the qualified purchaser's records right follows the owner's notice; internal target |
| RECORDS_RESPONSE_DUE | RECORDED request date + 30 d | `records_request_response_days` 30 | OAR 813-115-0050 Qualified Purchaser Access to Property, Records and Documents (ORS 456.262(6)-(7); compliance reports, approved rent schedule with actual rents). The 30-day period was not found in rule text: working target |
| ROFR_RECORDABLE_DATE | `qp_offer_delivered_date` + 30 d | `rofr_recordable_days_after_offer` 30 | ORS 456.262: the qualified purchaser first delivers an offer that includes notice that it may, after 30 days, record a Notice of ROFR; OAR 813-115-0060 (recording) |
| ROFR_MATCH_DEADLINE | `third_party_offer_mailed_date` + 30 d (fallback received_date + `Verify — Mailing Date`) | `rofr_match_days` 30 | ORS 456.263 |
| QC_RESPONSE_DUE | `qc_request_complete_date` + 1 yr | `qc_response_months` 12 | IRC 42(h)(6)(I) |
| HAP_OPTOUT_NOTICE_DEADLINE | HAP_EXPIRATION - 12 mo; program HAP / RAC / PBV only; status FUTURE only; never from STALE_CONTRACT_DATE | `hap_optout_notice_months` 12 | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 |
| HAP_OPTOUT_PACKAGE_DUE | HAP_EXPIRATION - 120 d; program HAP / RAC / PBV only | `hap_optout_package_days` 120 | Section 8 Renewal Policy Guide ch. 11 |
| INSPECTION_DUE | `last_inspection_date` + 36 / 24 / 12 mo for 1-4 / 5-25 / 26+ units (HOME); + 36 mo (LIHTC) | `inspection_cadence_home`, `inspection_cadence_lihtc` | 24 CFR 92.504(d); 26 CFR 1.42-5 |
| USDA_PUBLIC_BODY_OFFER_WINDOW_END | USDA_PREPAY_REQUEST_RECEIVED + 180 d | `usda_public_body_offer_days` 180 | 7 CFR 3560.659 |
| NOTICE_COMPLIANCE_BREACH (REGULATORY, not a helper) | emitted when PUSH_FIRST_NOTICE_DUE has passed AND `notice_status = not_received_confirmed`; event_date = the due date; detail `push_first_due_passed; notice_status=not_received_confirmed`. WORKING LABEL: its reading is "the withdrawal clock has not started and designee appointment is available", not a statutory breach finding, until ORS 456.260 / .262 are read | | ORS 456.262 ("whichever is earlier" designee trigger); ORS 456.260 |

The score step only consumes these; it never derives a date.

## 3. Stale contract dates

HAP / PRAC / PAC expirations already past as_of with no termination evidence (HUD tape status terminated / expired-not-renewed, CA log) -> event status `STALE_CONTRACT_DATE`, flag `Verify — Stale Contract Date`, signal `hap_date_stale`, a `Missing Source — Request Document: current HAP contract / TRACS` request, no agency deadlines, exclusion from the OVERDUE Board_Totals row (own row "stale contract date — verify") and from `lost`, `next_expected_expiration = last date + 12 mo` on the card. The clock factor scores such a row through `hap_stale_le_12_past` (6 points) only when the date is within the last 12 months. The HUD MF Assistance tape's current expiration overrides the OHCS date when both exist.

## 4. AGENCY_DEADLINE_META

Mirrored as a dict in `plb/agency_calendar.py`; `test_agency_calendar.py` asserts every AGENCY_DEADLINE type has a row. The Agency_Calendar tab and the brief read `agency_owner` and `statutory_cite` from this table; `detail` on the event names the owner cliff it derives from. EVENT_COLUMNS are unchanged.

| event_type | agency_owner (AGENCY_ROLES) | statutory_cite | verified_live | derives_from |
|---|---|---|---|---|
| PUSH_WINDOW_PREP | push_program_manager | internal prep date (anchor - 36 months); no statutory basis found for a 36-month owner-notice start | false | withdrawal_anchor_date |
| PUSH_FIRST_NOTICE_DUE | push_program_manager | ORS 456.260 / OAR 813-115-0030 (owner notice no sooner than 30 months before withdrawal); ORS 456.262 designee-appointment trigger at 30 months ('whichever is earlier') | false | withdrawal_anchor_date |
| PUSH_SECOND_NOTICE_DUE | push_program_manager | ORS 456.260 / OAR 813-115-0030 (owner notice at least 24 months before withdrawal; the (1)/(2) split is unread) | false | withdrawal_anchor_date |
| TENANT_NOTICE_WINDOW | compliance_officer | SB 973 (2025); ORS 456.259 | false | withdrawal_anchor_date |
| RECORDS_REQUEST_DUE | push_program_manager | OAR 813-115-0050 (qualified purchaser access to property, records and documents; ORS 456.262(6)-(7)); 10-day target is internal | false | PRESERVATION_NOTICE_RECEIVED |
| RECORDS_RESPONSE_DUE | push_program_manager | OAR 813-115-0050; 30-day response period not found in rule text (working target) | false | records request date |
| ROFR_RECORDABLE_DATE | legal_counsel | ORS 456.262 (Notice of ROFR recordable after 30 days from the qualified purchaser's offer); OAR 813-115-0060 (recording) | false | qp_offer_delivered_date |
| ROFR_MATCH_DEADLINE | legal_counsel | ORS 456.263; OAR 813-115-0070 | false | THIRD_PARTY_OFFER_RECEIVED |
| QC_RESPONSE_DUE | compliance_officer | IRC 42(h)(6)(I) | false | QC_ELIGIBILITY (requested) |
| HAP_OPTOUT_NOTICE_DEADLINE | pbca_liaison | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 | false | HAP_EXPIRATION |
| HAP_OPTOUT_PACKAGE_DUE | pbca_liaison | Section 8 Renewal Policy Guide ch. 11 | false | HAP_EXPIRATION |
| INSPECTION_DUE | compliance_officer (cpd_program_manager for HOME) | 24 CFR 92.504(d); 26 CFR 1.42-5 | false | last_inspection_date |
| USDA_PUBLIC_BODY_OFFER_WINDOW_END | rd_state_office (agency: nofa_program_manager) | 7 CFR 3560.659 | false | USDA_PREPAY_REQUEST_RECEIVED |

## 5. Notice window states and the breach rule

`notice_window_state` (build_context) from the PRESERVATION_NOTICE_WINDOW rows and the PUSH_*_DUE dates vs as_of: `not_open` (as_of < anchor - 36 mo), `open_first` (anchor - 36 <= as_of < anchor - 30), `open_second` (anchor - 30 <= as_of < anchor - 24 with a first notice received), `closed_first_due` (as_of >= anchor - 30 and no first notice), `closed_second_due` (as_of >= anchor - 24 and no second notice).

| state | notice_status | declared_intent_vs_silence | route | intervention |
|---|---|---|---|---|
| open_first | not received | 0 points; signal `push_window_open_prep`; PUSH_WINDOW_PREP calendar row | notice_compliance secondary only | push_window_prep (internal: confirm log, pull LURA/REUA and HAP contract from our file, confirm notice address, pre-draft records request) |
| closed_first_due / closed_second_due | `not_received_confirmed` | NOTICE_COMPLIANCE_BREACH 15 | notice_compliance primary; designee_rofr when is_qualified_purchaser | push_notice_demand_letter; designee appointment on silence (ORS 456.262 / HB 2095) |
| closed_first_due / closed_second_due | `unknown` | 6 points + `Verify — Notice Log`; Data Gaps | notice_compliance SECONDARY ("confirm against PuSH-CP log / ask OHCS") when no notice log is loaded for the run, so recap_committee / optout_response / servicing_watch keep the card; PRIMARY only when `profile.notice_log_loaded` (any lead carries a populated notice_status from the servicing extract or PuSH forecast) | push_window_prep (confirm) |
| any | `received` | PRESERVATION_NOTICE_RECEIVED 15 | designee_rofr (qualified purchaser) | push_records_request (10 days), rofr_notice_recording |

For `hfa` the share of PuSH-covered rows with a blank `notice_log_status` is reported in the Run Summary, not scored. Absence in our data is never owner silence.

## 6. Surfaces

- Calendar header third segment: `| agency act-by n (next 90 days m)` (`query_calendar.summarize()` computes `agency_act_by` and `next_90_days`; `plb/calendar.py` renders).
- `Agency_Calendar` tab and `agency_calendar.csv`: property, agency_action_type, due date, months_out, urgency, basis, derived_from, agency_owner, statutory_cite, status.
- Brief section `## Agency Act-By Calendar (overdue and next 90 days)` (OVERDUE agency act-by rows first, then the next 90 days).
- Card line `First agency act-by: [type date [basis] — months · owner · cite (verify)]`.
- Lead columns `agency_action_type, agency_action_date, agency_action_months_out, agency_action_basis, agency_action_owner, action_band` = the earliest AGENCY_DEADLINE event with months_out >= -12 (OVERDUE kept twelve months), else blank.

## 7. Worked examples (Oregon, as of 2026-10-04)

| property | anchor | push_anchor_source | PUSH_WINDOW_PREP | PUSH_FIRST_NOTICE_DUE | PUSH_SECOND_NOTICE_DUE | state | agency act-by shown |
|---|---|---|---|---|---|---|---|
| Village Garden Apartments, Portland (35 units, LIHTC/OHCS, OHCS Funded) | 2029-06-01 (restriction_end) | restriction_end | 2026-06-01 (OVERDUE, acted on now) | 2026-12-01 | 2027-06-01 | open_first | PUSH_WINDOW_PREP 2026-06-01; no RECORDS_REQUEST_DUE until a notice is received |
| Powell Plaza I, Portland (47 units, HAP 2027-03-31 annual, LIHTC to 2035-01-01) | 2035-01-01 (LIHTC; HAP excluded, no non-renewal signal) | restriction_end | 2032-01-01 | 2032-07-01 | 2033-01-01 | not_open | HAP_OPTOUT_PACKAGE_DUE 2026-12-01 (HAP_OPTOUT_NOTICE_DEADLINE 2026-03-31 passed -> `optout_notice_deadline_passed_unconfirmed`, `Verify — CA Log`) |
| Yards at Union Station A, Portland (158 units, Home Forward, LATEST 2028-01-01) | 2028-01-01 | restriction_end | 2025-01-01 | 2025-07-01 (passed) | 2026-01-01 (passed) | closed_second_due unless notice received | pha_am: self_owned, PuSH rows suppressed (own asset); hfa: PUSH_SECOND_NOTICE_DUE 2026-01-01 OVERDUE with notice_status unknown -> 6 pts + Verify — Notice Log |
| Garden Grove Apartments, Forest Grove (48 units, HAP 2040-01-31) | none inside horizon | none | — | — | — | not_open | none (BEYOND; EXCLUDED no_dated_cliff_in_horizon) |
| Park Terrace (HAP date 2024-09-30, no termination evidence) | — | — | — | — | — | — | STALE_CONTRACT_DATE; next_expected_expiration 2025-09-30 -> 2026-09-30 roll; no deadlines; "stale contract date — verify" row |
