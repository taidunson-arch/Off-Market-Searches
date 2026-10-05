# Pipeline Contract

Canonical vocabulary, tables and file formats shared by every script, module and output of `preservation-loan-book`. When any other file in this skill disagrees with this one, this file governs and the other file is reconciled. `scripts/plb/schema.py` is the single code source for every enum here; `scripts/tests/test_contract.py` fails when the Section 3 table or the Section 6 column list drifts from the code.

This contract is a delta from off-market-deal-finder v2's: the basis levels, verify flags, date handling, geography, event names and events table are reused verbatim so outputs of the two skills join without translation. What changed is the posture: the user is a lender, grantor or qualified purchaser, the routes are agency interventions, and the agency's own ledger is a RECORDED source.

## Contents

1. Enumerations
2. Basis levels and verify flags
3. Event taxonomy
4. Event validation rules and helper deadlines
5. Canonical lead table (leads.csv)
6. Companion events table (events.csv)
7. Rejects table (rejects.csv)
8. Calendar summary (calendar_summary.json) and units_at_risk.json
9. Run manifest (runs/<as_of>/manifest.json)
10. Identity, join, dedupe and date-conflict rules
11. Scoring JSON schema (references/scoring/*.json)
12. Route precedence and sentinels
13. Canonical servicing extract (agency_servicing_extract)

---

## 1. Enumerations

Use these exact strings. Scripts reject unknown values rather than coercing them.

| Enum | Values |
|---|---|
| `agency_profile` | `hfa` \| `city_housing` \| `county` \| `pha_am` \| `cdbg_home` |
| `asset_class` | `affordable_regulated` \| `noah_unregulated` (NOAH only with `--noah-watch`) |
| `universe` | `our_book` \| `universe_not_held` (a property in both inventory and book, or self-owned, is `our_book`; `in_inventory` carries the other fact) |
| `book_match` | `matched` \| `self_owned` \| `book_only` \| `unmatched_expected` \| `not_in_extract` \| `not_in_book` \| `book_absent` |
| `book_join_grade` | `crosswalk` \| `address` \| `fuzzy` \| `unmatched` |
| `book_coverage` | `full` \| `partial` |
| `book_kind` | `loan` \| `grant` \| `owned_asset` \| `administered_contract` |
| `geography_mode` | `city_limits` \| `county` \| `metro_core` \| `cbsa` \| `custom` |
| `geo_grade` | `county_field` \| `zip_crosswalk` \| `point_in_polygon` \| `city_name_weak` |
| `basis` | `RECORDED` \| `REPORTED` \| `DERIVED` \| `ESTIMATED` \| `PROXY` |
| `verify_flag` | `null` \| `Verify — Ambiguous` \| `Verify — Conflicting Sources` \| `Needs Anchor Date` \| `Missing Source — Request Document` \| `Rejected — Out of Range` \| `No Format Declared` \| `Verify — Book Join` \| `Verify — Notice Log` \| `Verify — Stale Contract Date` \| `Verify — Notice Address` \| `Verify — Mailing Date` \| `Verify — CA Log` \| `Verify — PuSH Coverage` |
| `event_family` | `DEBT` \| `REGULATORY` \| `HARD_DISTRESS` \| `TAX_LIEN` \| `PHYSICAL` \| `OWNERSHIP` \| `OPERATING` \| `AGENCY_DEADLINE` |
| `direction` | `PRESSURE` \| `SUPPRESSION` \| `ROUTING` |
| `event_status` | `FUTURE` \| `PAST` \| `STALE_CONTRACT_DATE` \| `SUPPRESSED` \| `RETIRED` \| `REJECTED` |
| `urgency_band` | `OVERDUE` (< 0 mo) \| `CRITICAL` (0-12) \| `URGENT` (12-24) \| `APPROACHING` (24-36) \| `MONITOR` (36-60) \| `SCHEDULED` (60-120) \| `BEYOND` (> 120, outside horizon, never scored) — **months, not days** |
| `queue_band` | `ESCALATE` (score >= 70) \| `ACT` (50-69) \| `PLAN` (30-49) \| `WATCH` (< 30 with a dated PRESSURE event inside horizon) \| `EXCLUDED` |
| `primary_route` | `optout_response` \| `notice_compliance` \| `qc_admin` \| `designee_rofr` \| `recap_committee` \| `servicing_watch` \| `nofa_offer` \| `ta_sponsor` (the eight routes, in precedence order) \| sentinels `none` \| `excluded` |
| `secondary_routes` | `;` list drawn from the eight routes |
| `exclusion_reason` | `in_development` \| `outside_geography` \| `under_5_units_no_program_event` \| `no_dated_cliff_in_horizon` |
| `owner_type` | `individual_owner_of_record` \| `trust_estate` \| `single_asset_llc` \| `regional_operator` \| `institutional` \| `lihtc_partnership_forprofit_gp` \| `lihtc_partnership_nonprofit_gp` \| `nonprofit` \| `housing_authority` \| `government` \| `lender_reo_receiver` \| `self_owned` \| `unknown` |
| `org_resolution_grade` | `A` \| `B` \| `C` (definitions in `sponsor-resolution.md`; replaces v2 `contact_grade`) |
| `notice_status` | `received` \| `not_received_confirmed` \| `unknown` |
| `tenant_notice_status` | `confirmed` \| `not_confirmed` \| `unknown` \| `n/a_pre_operative` |
| `hap_renewal_request_status` | `received` \| `not_received` \| `unknown` |
| `hap_renewal_option` | `1a` \| `1b` \| `2` \| `3` \| `4` \| `5` \| `6_optout` \| `unknown` |
| `recap_status` | `none` \| `announced` \| `under_application` \| `closed` |
| `units_basis` | `reported_buckets` \| `total_assumed_restricted` \| `proxy` |
| `pii_scope` | `public_packet` \| `organization` (default) \| `internal` |
| `mandate_fit` | `eligible` \| `ineligible` \| `no_mandate_file` |
| `notice_address_source` | `regulatory_agreement` \| `hap_contract` \| `loan_docs` \| `sos_registered_agent` \| `unknown` |
| `qc_waived` | `true` \| `false` \| `unknown` |
| `payment_type` | `hard_pay` \| `residual_receipts` \| `deferred` \| `forgivable` |
| `covenant_status` | `current` \| `watch` \| `default` \| `cured` \| `released` |
| `recapture_type` | `home_recapture` \| `home_resale` \| `home_rental_repayment` \| `cdbg` \| `shared_appreciation` \| `none` | (`home_recapture` / `home_resale` are HOMEBUYER positions under 24 CFR 92.254; rental HOME is `home_rental_repayment`, repayable in full under 24 CFR 92.503(b) while the 92.252 period runs)
| `recapture_method` | `full` \| `prorata_reducing` \| `forgiveness_schedule` \| `cdbg_fmv_share` \| `none` |
| `senior_lien_type` | `hud_fha` \| `usda_rd` \| `fannie_dus` \| `freddie_k_sb` \| `bank_cu` \| `state_soft` \| `local_soft` \| `none` \| `unknown` |
| `agency_role` | `am_officer` \| `compliance_officer` \| `push_program_manager` \| `nofa_program_manager` \| `legal_counsel` \| `pbca_liaison` \| `board_liaison` \| `hud_mf_asset_manager` \| `rd_state_office` \| `cpd_program_manager` \| `pha_development` |
| `program` | `LIHTC_9` \| `LIHTC_4` \| `HAP` \| `PRAC` \| `RAC` \| `PAC` \| `PBV` \| `HUD_INSURED` \| `HUD_236` \| `HUD_202_811` \| `USDA_515` \| `HOME` \| `CDBG` \| `OAHTC` \| `GHAP` \| `HDGP` \| `LIFT` \| `HTF` \| `OTHER_OHCS` \| `LOCAL_REG` \| `PHB_LOAN` \| `TIF` \| `LEVY` \| `IH_SET_ASIDE` |
| `AM status` (workbook dropdown) | `New` \| `Assigned` \| `Letter Sent` \| `Awaiting Response` \| `Committee` \| `Closed` (Book_Watchlist adds `Monitoring`) |
| `flip_type` (status_flips.csv) | `notice_filed` \| `tenant_notice_confirmed` \| `qc_requested` \| `qc_presented` \| `hap_renewed` \| `hap_optout` \| `loan_extended` \| `loan_recast` \| `covenant_cured` \| `covenant_default` \| `recap_closed` \| `preserved` \| `lost` \| `new_to_list` \| `left_list` |

Constant sets: `HUD_CONTRACT_TO_PROGRAM = {Housing Assistance Payment: HAP, Project Rental Assistance Contract: PRAC, Rental Assistance Contract: RAC, Project Assistance Contract: PAC}`; `PUSH_COVERED_PROGRAMS = {HAP, PRAC, RAC, PAC, LIHTC_9, LIHTC_4, HUD_236, HUD_202_811, USDA_515, HOME, OAHTC, GHAP, HDGP, LIFT, HTF, OTHER_OHCS}` (whether a LIHTC LURA alone makes a property "publicly supported housing" under ORS 456.250 is unconfirmed; see `public-am-module.md` Known gaps). Portland `geography_mode` definitions: `county` = 41051; `metro_core` = 41051, 41067, 41005; `cbsa` = 41005, 41009, 41051, 41067, 41071, 53011, 53059 (`sources/oregon-portland/geography.md`).

Urgency band timing fractions: OVERDUE 1.00, CRITICAL 1.00, URGENT 0.75, APPROACHING 0.50, MONITOR 0.25, SCHEDULED 0.00, BEYOND 0.00. Default horizon 10 years for both families. `A`, `B`, `C` as tiers never appear in any output; the only A/B/C in the pack is `org_resolution_grade`.

Removed from v2: `query_type` (replaced by `--universe`), `buyer_profile`, `tier`, `route` (acquisition / partnership_preservation / lender_counterparty / assumption_play / watch), `lender_type` as a lead enum (kept only inside `senior_lien_type`), `contact_grade` (renamed), SFR and market-rate asset classes.

## 2. Basis levels and verify flags

A date or dollar figure is only as good as where it came from. Every value carries a `basis` and a `source`; scoring multiplies factor points by the basis multiplier of the governing event. Keeping the five levels separate is what lets a board see "7 recorded maturities on our book, 40 reported program ends, 12 derived Year-15 dates" instead of "59 cliffs".

| basis | multiplier | meaning | typical examples | what upgrades it |
|---|---|---|---|---|
| `RECORDED` | 1.00 | taken from a recorded instrument, court order, or a government ledger that is the system of record for that loan, grant or program. **The agency's own servicing and grant ledger is RECORDED for its own loans, grants, covenants, notice log and QC log.** | agency servicing extract (`maturity`, `affordability_end`, `covenant_status`, `notice_log_status`, `qc_request_complete_date`), HUD FHASL Maturity Date, recorded LURA / Notice of ROFR, SOS status, PBCA opt-out log | nothing; this is the ceiling |
| `REPORTED` | 0.90 | reported by a party to the loan or program to a disclosure system; current but not the instrument itself | HUD Sec 8 `tracs_overall_expiration_date`, OHCS `*_Expiration_Date`, REAC score from the HUD export, HUD FHASL UPB, a fuzzy book join | the instrument or the agency's own file |
| `DERIVED` | 0.80 | arithmetic on a RECORDED or REPORTED anchor using a rule fixed by statute, regulation or program design | Year 15 = Compliance_Start + 15y; HOME period = completion + 24 CFR 92.252(e) years; every AGENCY_DEADLINE (anchor minus statutory months); NOTICE_COMPLIANCE_BREACH | the program document stating the actual date |
| `ESTIMATED` | 0.50 | arithmetic on an anchor using a market convention with an explicit window | QC price band (`recap_math.qc_price_band`, memo-only) | the owner's certification |
| `PROXY` | 0.30 | a stand-in from a dataset that does not describe the thing being dated | OHCS `Financial_Closing_Date + 15y` as a loan maturity (opt-in only, `--include-proxies`; dropped when a RECORDED AGENCY_LOAN_MATURITY exists) | any of the above |

`AMBIGUOUS` is not a basis. A value whose format could not be disambiguated keeps its declared basis but carries `verify_flag = Verify — Ambiguous`, which forces the multiplier to 0.40 regardless of basis and stores both parses in `alt_dates`.

Verify flags (vocabulary shared with `critical-dates-tracker`; six are new to this pack):

| flag | when to set | downstream effect |
|---|---|---|
| `Verify — Ambiguous` | slash date with both fields <= 12 under `format: auto` | multiplier 0.40; `alt_dates` populated; Rejects_Verify |
| `Verify — Conflicting Sources` | two sources give different dates for the same (event_type, program, detail), both >= REPORTED and > 1 month apart; OHCS LATEST != max of components; expiration before compliance start | keep the higher-basis value (agency RECORDED governs ties); Rejects_Verify |
| `Needs Anchor Date` | a DERIVED event has no anchor (no notice date, no completion date, no QC complete date) | event not emitted or emitted undated; property keeps the flag |
| `Missing Source — Request Document` | event exists only below RECORDED and a document would settle it; Total Units blank | `documents_to_request.csv` (the agency's own file room first) |
| `Rejected — Out of Range` | fails a Section 4 validation or an enum check on the servicing extract | rejects.csv; not scored |
| `No Format Declared` | column has date-like values but no schema format | adapter stops; run `date_profile.py` |
| `Verify — Book Join` | `book_match = unmatched_expected` under `book_coverage: full` | our_capital_at_risk 0 with factor status WATCH; Book_Join_Gaps row; queue not capped |
| `Verify — Notice Log` | PUSH_FIRST_NOTICE_DUE passed and `notice_status = unknown` | 6 points in declared_intent_vs_silence; Data Gaps |
| `Verify — Stale Contract Date` | HAP/PRAC/PAC expiration already past as_of with no termination evidence | event status STALE_CONTRACT_DATE; never OVERDUE in Board_Totals; never `lost`; no agency deadlines derive from it |
| `Verify — Notice Address` | notice_address came from the SOS registered agent, not the agency file | print the source beside the address on every letter |
| `Verify — Mailing Date` | ROFR match clock anchored on received_date because `third_party_offer_mailed_date` is blank | ROFR_MATCH_DEADLINE flagged |
| `Verify — CA Log` | HAP_OPTOUT_NOTICE_DEADLINE passed and `hap_renewal_request_status = unknown` | signal `optout_notice_deadline_passed_unconfirmed`; first action confirm at the CA |

## 3. Event taxonomy

One list for the pack. Every v2 affordable event name is reused verbatim; the additions carry the agency's book and the agency's own deadlines. `scripts/plb/schema.py` `EVENT_TAXONOMY` is generated to match this table and `scripts/tests/test_contract.py` fails when the two drift. Every row states `FAMILY (DIRECTION)` explicitly. Rows marked helper are in `HELPER_EVENTS` (all `AGENCY_DEADLINE` types plus `PRESERVATION_NOTICE_WINDOW`); `REGULATORY_LATEST_END` is the only `ROLLUP_EVENTS` member.

| event_type | family (direction) | derivation / source | default basis | owner or agency calendar | decays |
|---|---|---|---|---|---|
| LOAN_MATURITY | DEBT (PRESSURE) | HUD FHASL `Maturity Date` (RECORDED); servicing extract `senior_maturity` with detail `lender_type=<senior_lien_type>` (REPORTED); OHCS `Financial_Closing_Date + 15y` (17y if LIHTC_4) only with `--include-proxies` (PROXY, +/-36 mo) | per source | owner | yes |
| PREPAY_WINDOW_OPEN | DEBT (PRESSURE) | HUD final endorsement + 10y (DERIVED, +/-6 mo) | DERIVED | owner | yes |
| LOAN_MODIFIED | DEBT (PRESSURE) | recorded Modification / Extension; agency loan_recast flip | RECORDED | owner | yes |
| HUD_DIRECT_LOAN_MATURITY | DEBT (PRESSURE) | FHASL rows with SOA in {236, 221(d)(3), 202}; detail `236_irp` / `no_hap_overlay` | RECORDED | owner | yes |
| USDA_515_MATURITY | DEBT (PRESSURE) | USDA MFH exit data (RECORDED); OHCS USDA_RD_Expiration_Date (REPORTED) | RECORDED / REPORTED | owner | yes |
| USDA_515_PREPAY_ELIGIBLE | DEBT (PRESSURE) | USDA MFH exit data prepay flag / date | RECORDED | owner | yes |
| USDA_EXIT_PROJECTED | DEBT (PRESSURE) | USDA estimated exit year (Dec 31) | REPORTED (+/-12 mo) | owner | yes |
| SOFT_LOAN_MATURITY | DEBT (PRESSURE) | another public lender's soft-note maturity when a recorded trust deed or loan document states it (our own notes are AGENCY_LOAN_MATURITY) | RECORDED | owner | yes |
| AGENCY_LOAN_MATURITY | DEBT (PRESSURE) | servicing extract `maturity` (book_kind loan); detail `agency_loan_id=<id>`; event_id includes the loan id | RECORDED | owner cliff, ours | yes |
| SHARED_APPRECIATION_DUE | DEBT (PRESSURE) | servicing extract `maturity` when `shared_appreciation_pct > 0` | RECORDED | owner cliff, ours | yes |
| REFINANCE_CLOSED | DEBT (SUPPRESSION) | FHASL Terminated row matched on digits-only HUD Project Number; emits SUPPRESS_UNTIL | RECORDED | n/a | n/a |
| SUPPRESS_UNTIL | DEBT (SUPPRESSION) | from REFINANCE_CLOSED (= new origination + min term) | DERIVED | n/a | n/a |
| LIHTC_COMPLIANCE_END | REGULATORY (PRESSURE) | Dec 31 of (YR_PIS + 14); fallback Compliance_Start_Date + 15y (only when programs contain LIHTC); flag `+15 election possible` | DERIVED (0.80, +12 mo) | owner | yes |
| LIHTC_EXTENDED_USE_END | REGULATORY (PRESSURE) | OHCS LIHTC_4/9_Expiration_Date or recorded REUA / LURA (REPORTED / RECORDED); fallback Dec 31 (YR_PIS + 29) (DERIVED) | REPORTED | owner; anchor for PuSH | yes |
| QC_ELIGIBILITY | REGULATORY (PRESSURE) | `status` in {eligible, requested, lapsed_decontrol}; `requested` only from the agency's QC log (`qc_request_complete_date`, or `qc_request_date` with Needs Anchor Date note) with `qc_waived != true`; `eligible` from allocation vintage is a watch note and never scores | RECORDED (requested / lapsed) / DERIVED (eligible) | owner; starts QC_RESPONSE_DUE | no while requested |
| HAP_EXPIRATION | REGULATORY (PRESSURE) | HUD Sec 8 `tracs_overall_expiration_date` (overrides OHCS); OHCS HUD_MF_Expiration_Date stamped `program = HUD_CONTRACT_TO_PROGRAM[HUD Contract]` and `detail = term_unknown_annual_assumed`; servicing `contract_expiration` (administered_contract, program PBV/HAP, confidence 0.90); detail `short_renewal_pattern` / `annual_renewal` / `mahra_20yr_recent`; a past date with no termination evidence gets status STALE_CONTRACT_DATE | REPORTED, confidence 0.70 (annual / unknown) or 0.90 (20-year MAHRA; agency PBV contract) | owner; enters the PuSH anchor only with a non-renewal signal | yes |
| PRESERVATION_NOTICE_WINDOW | REGULATORY (PRESSURE) | helper. Windows [[36,30],[30,24]] months before `withdrawal_anchor_date`; detail `push_first_window` / `push_second_window`. The 36..30 window is an INTERNAL prep window (no statutory 36-month owner-notice start was found: OAR 813-115-0030 reads "no sooner than 30 and at least 24 months" before withdrawal; ORS 456.260 text unread); the 30..24 window is the owner-notice period as understood. `push_anchor_source` recorded; gated on units >= 5, PUSH_COVERED_PROGRAMS, profile receives_push_notice or is_qualified_purchaser; HOME-only / LIHTC-only rows carry `Verify — PuSH Coverage` until the pack sets `push_program_coverage_verified` | DERIVED (statute text unverified) | owner window | n/a |
| PRESERVATION_NOTICE_RECEIVED | REGULATORY (PRESSURE) | servicing `notice_log_status = received` + `notice_received_date` (RECORDED; Needs Anchor Date when undated); forecast status flip; CA opt-out log; `detail` in {push_first, push_second, hap_optout} | RECORDED | owner declared; starts RECORDS_REQUEST_DUE | yes |
| SOFT_PROGRAM_END | REGULATORY (PRESSURE) | each OHCS HOME/OAHTC/GHAP/HDGP/LIFT/HTF/Other_OHCS date (affordability period end, not a note maturity); HTF completion + 30y (DERIVED) when no explicit end | REPORTED | owner; anchor for PuSH | yes |
| REGULATORY_LATEST_END | REGULATORY (PRESSURE) | OHCS LATEST_Expiration_Date (recompute as max of components when blank); rollup: counted only when its date differs from every component | REPORTED | owner | yes |
| GRANT_RECAPTURE_END | REGULATORY (PRESSURE) | servicing extract `recapture_end` (book_kind grant); detail `grant_id=<id>` | RECORDED | owner cliff, ours | yes |
| AFFORDABILITY_PERIOD_END | REGULATORY (PRESSURE) | servicing extract `affordability_end` with `program` carried (HOME 24 CFR 92.252(e); CDBG 570.505; HTF 93.302; local covenants); PJ records completion + period (DERIVED); detail `<id_kind>=<id>` | RECORDED / DERIVED | owner cliff, ours; anchor for PuSH | yes |
| COVENANT_END | REGULATORY (PRESSURE) | local regulatory agreement end from the servicing extract or a recorded agreement | RECORDED | owner cliff; anchor for PuSH | yes |
| RECAPTURE_TRIGGER | REGULATORY (PRESSURE) | recorder sale, payoff or foreclosure inside the affordability / recapture period | RECORDED | ours | no while open |
| NOTICE_COMPLIANCE_BREACH | REGULATORY (PRESSURE) | `plb/agency_calendar.py`: PUSH_FIRST_NOTICE_DUE passed AND `notice_status = not_received_confirmed`; event_date = the due date; detail `push_first_due_passed; notice_status=not_received_confirmed` | DERIVED | agency compliance case | no while open |
| ROFR_RECORDED | REGULATORY (ROUTING) | recorder index "Notice of Right of First Refusal" (OAR 813-115-0060) / designee agreement; servicing `rofr_recorded` | RECORDED | our right | n/a |
| THIRD_PARTY_OFFER_RECEIVED | REGULATORY (ROUTING) | servicing / PuSH-CP log `third_party_offer_mailed_date` (fallback received_date + `Verify — Mailing Date`); starts ROFR_MATCH_DEADLINE | RECORDED | our 30-day match | no until ROFR_MATCH_DEADLINE |
| QC_REQUEST_INELIGIBLE | REGULATORY (ROUTING) | servicing `qc_waived = true` with a QC request on file | RECORDED | n/a (no clock) | n/a |
| USDA_PREPAY_REQUEST_RECEIVED | REGULATORY (ROUTING) | RD / servicing `usda_prepay_request_date`; starts USDA_PUBLIC_BODY_OFFER_WINDOW_END | RECORDED | our offer window | no until window end |
| SECTION_18_APPLICATION | REGULATORY (ROUTING) | PHA / HUD SAC `section_18_application_date` | RECORDED | repositioning marker | n/a |
| RAD_CHAP | REGULATORY (ROUTING) | PHA `rad_chap_date` | RECORDED | repositioning marker | n/a |
| PUSH_WINDOW_PREP | AGENCY_DEADLINE (PRESSURE) | helper. `withdrawal_anchor_date` - 36 mo (internal: confirm log, pull LURA/REUA and HAP contract from our file, confirm notice address) | DERIVED | agency | n/a |
| PUSH_FIRST_NOTICE_DUE | AGENCY_DEADLINE (PRESSURE) | helper. anchor - 30 mo: the earliest owner-notice date ("no sooner than 30 months", OAR 813-115-0030 summary) and the ORS 456.262 designee-appointment trigger ("whichever is earlier"); the (1)/(2) split in ORS 456.260 is unread; verify | DERIVED | agency | n/a |
| PUSH_SECOND_NOTICE_DUE | AGENCY_DEADLINE (PRESSURE) | helper. anchor - 24 mo: owner notice "at least 24 months" before withdrawal (OAR 813-115-0030 summary; ORS 456.260 unread; verify) | DERIVED | agency | n/a |
| TENANT_NOTICE_WINDOW | AGENCY_DEADLINE (PRESSURE) | helper. anchor - 36..-30 mo (SB 973; only when anchor >= pack `sb973_operative_restriction_date`, else tenant_notice_status n/a_pre_operative; verify) | DERIVED | agency check | n/a |
| RECORDS_REQUEST_DUE | AGENCY_DEADLINE (PRESSURE) | helper. PRESERVATION_NOTICE_RECEIVED + 10 d (the qualified purchaser's records right follows the owner's notice; never before) | DERIVED | agency | n/a |
| RECORDS_RESPONSE_DUE | AGENCY_DEADLINE (PRESSURE) | helper. RECORDED request date + 30 d working target (OAR 813-115-0050 qualified purchaser access to property, records and documents; the 30-day period was not found in rule text — read ORS 456.262(6)-(7)) | DERIVED | owner response, agency follow-up | n/a |
| ROFR_RECORDABLE_DATE | AGENCY_DEADLINE (PRESSURE) | helper. `qp_offer_delivered_date` + 30 d: earliest date the qualified purchaser may record its Notice of ROFR (ORS 456.262: offer first, with notice of intent to record; recording after 30 days; OAR 813-115-0060 recording; verify) | DERIVED | agency | n/a |
| ROFR_MATCH_DEADLINE | AGENCY_DEADLINE (PRESSURE) | helper. `third_party_offer_mailed_date` + 30 d (ORS 456.263, verify) | DERIVED | agency | n/a |
| QC_RESPONSE_DUE | AGENCY_DEADLINE (PRESSURE) | helper. `qc_request_complete_date` + 1 yr (IRC 42(h)(6)(I)) | DERIVED | agency (HFA) | n/a |
| HAP_OPTOUT_NOTICE_DEADLINE | AGENCY_DEADLINE (PRESSURE) | helper (re-familied from v2 REGULATORY). HAP_EXPIRATION - 12 mo; program HAP / RAC / PBV only; status FUTURE only; never from STALE_CONTRACT_DATE | DERIVED | agency check (24 CFR 402.8) | n/a |
| HAP_OPTOUT_PACKAGE_DUE | AGENCY_DEADLINE (PRESSURE) | helper. HAP_EXPIRATION - 120 d (Section 8 Renewal Guide ch. 11, verify); program HAP / RAC / PBV only | DERIVED | agency check | n/a |
| INSPECTION_DUE | AGENCY_DEADLINE (PRESSURE) | helper. `last_inspection_date` + 3/2/1 yrs by units for HOME (24 CFR 92.504(d)); + 3 yrs for LIHTC (26 CFR 1.42-5) | DERIVED | agency | n/a |
| USDA_PUBLIC_BODY_OFFER_WINDOW_END | AGENCY_DEADLINE (PRESSURE) | helper. USDA_PREPAY_REQUEST_RECEIVED + 180 d (7 CFR 3560.659, verify) | DERIVED | agency | n/a |
| REAC_SCORE | OPERATING (PRESSURE) | HUD inspection export (`value` score, `detail` protocol / decline_ge_15) (REPORTED); servicing `last_reac_score` (RECORDED) | REPORTED / RECORDED | troubled-asset AM | yes |
| TAX_EXEMPTION_LOST | OPERATING (PRESSURE) | assessor exemption-code diff | RECORDED | troubled-asset AM | yes |
| STABILIZATION_AWARD | OPERATING (PRESSURE) | HFA award list / forecast status Preserved; kpi `preserved` | RECORDED | n/a | yes |
| OCCUPANCY_DROP | OPERATING (PRESSURE) | agency AM report / HUD tape | REPORTED | troubled-asset AM | yes |
| MGMT_CHANGE | OPERATING (PRESSURE) | observed / HUD Sec 8 agent change | REPORTED | n/a | yes |
| COVENANT_DEFAULT | OPERATING (PRESSURE) | servicing `covenant_status = default`, dated as_of | RECORDED | ours | no while open |
| NONCOMPLIANCE_FINDING | OPERATING (PRESSURE) | servicing `open_findings_count > 0` or `last_8823_date`; detail `open_finding` / `8823_filed`, value count | RECORDED | ours (compliance) | no while open |
| TAX_DELINQUENT_YEARS | TAX_LIEN (PRESSURE) | assessor payment history; `value` 1 / 2 / 3+ | RECORDED | troubled-asset AM | yes |
| TAX_FORECLOSURE_LIST | TAX_LIEN (PRESSURE) | county list (ORS 312) | RECORDED | covenant extinguishment risk | yes |
| TAX_REDEMPTION_END | TAX_LIEN (PRESSURE) | judgment + 2 y | DERIVED | | yes |
| MECHANICS_LIEN | TAX_LIEN (PRESSURE) | recorder Claim of Lien | RECORDED | | yes |
| JUDGMENT_LIEN | TAX_LIEN (PRESSURE) | recorder / judgment index | RECORDED | | yes |
| CODE_LIEN_REFERRAL | TAX_LIEN (PRESSURE) | council referral lists | RECORDED | | yes |
| UTILITY_LIEN_CERTIFIED | TAX_LIEN (PRESSURE) | annual certification ordinance | RECORDED | | yes |
| CODE_CASE_OPEN | PHYSICAL (PRESSURE) | city open-case lists; `detail` case type | REPORTED | troubled-asset AM | yes |
| DANGEROUS_BUILDING | PHYSICAL (PRESSURE) | city dangerous-building list | REPORTED | troubled-asset AM | yes |
| ENTITY_ADMIN_DISSOLVED | OWNERSHIP (PRESSURE) | SOS registry status | RECORDED | sponsor capacity; notice address | permanent |
| MANAGER_CHANGE | OWNERSHIP (PRESSURE) | SOS annual report diff; detail `aggregator` / `lp_transfer` when known | RECORDED | sponsor capacity | yes |
| REGISTERED_AGENT_CHANGE | OWNERSHIP (PRESSURE) | SOS annual report diff | RECORDED | notice address | yes |
| UNENCUMBERED | OWNERSHIP (PRESSURE) | Reconveyance with no new lien | RECORDED | | permanent |
| HOLD_YEARS | OWNERSHIP (PRESSURE) | NOAH only: assessor deed date; `value` years | RECORDED | n/a | permanent |
| ABSENTEE_TIER | OWNERSHIP (PRESSURE) | NOAH only: mailing vs situs | RECORDED | n/a | permanent |
| DEPRECIATION_EXHAUSTED | OWNERSHIP (PRESSURE) | NOAH only: HOLD_YEARS >= 27.5 | RECORDED | n/a | permanent |
| JUDICIAL_FORECLOSURE_FILED | HARD_DISTRESS (PRESSURE) | court index (ORS 88) on a regulated asset: covenant-extinguishment risk | RECORDED | book risk | yes |
| LIS_PENDENS | HARD_DISTRESS (PRESSURE) | recorder (ORS 93.740) | RECORDED | book risk | yes |
| UCC_MEZZ_PLEDGE | HARD_DISTRESS (PRESSURE) | SOS UCC debtor = owner; collateral = membership interests | RECORDED | book risk | yes |
| UCC_ART9_SALE | HARD_DISTRESS (PRESSURE) | Article 9 disposition notice | RECORDED | book risk | yes |
| RECEIVER_APPOINTED | HARD_DISTRESS (ROUTING) | court order (ORS ch. 37) | RECORDED | recap_committee workout | n/a |
| BANKRUPTCY_FILED | HARD_DISTRESS (ROUTING) | PACER; `detail` chapter and SARE flag; compliance gate counsel_only | RECORDED | recap_committee workout | n/a |

Dropped from v2: every SFR and market-rate HARD_DISTRESS, foreclosure-clock, HECM, DOR deferral, probate, dissolution, partition, 1031, listing, insurance, rate-cap, IO, balloon, special-servicing and watchlist event. `PERMANENT_EVENT_TYPES = {ENTITY_ADMIN_DISSOLVED, UNENCUMBERED, HOLD_YEARS}`; `NON_DECAYING_WHILE_OPEN = {COVENANT_DEFAULT, NOTICE_COMPLIANCE_BREACH, NONCOMPLIANCE_FINDING, QC_ELIGIBILITY (status requested), THIRD_PARTY_OFFER_RECEIVED, USDA_PREPAY_REQUEST_RECEIVED, RECAPTURE_TRIGGER}`; `AGENCY_ACTION_EVENTS` = the twelve AGENCY_DEADLINE types.

## 4. Event validation rules and helper deadlines

Run before an event is accepted; failures write a rejects.csv row with `Rejected — Out of Range` and the event is not scored.

| rule | applies to | test |
|---|---|---|
| loan range | DEBT events with an origination anchor | `orig_date < event_date < orig_date + 75 years` (agency soft notes run 40-75 years) |
| subsidy anchor | REGULATORY events when `Compliance_Start_Date` present | `event_date >= Compliance_Start_Date` (fail -> `Verify — Conflicting Sources`, not rejected) |
| plausible year | all | `1960 <= year <= 2100` |
| development status | all | `Status != In Development` (row EXCLUDED with exclusion_reason in_development; counted in `rows_excluded_in_development`) |
| month sanity | all slash dates | parsed month <= 12 |
| servicing enums | agency_servicing_extract | `book_kind`, `program`, `payment_type`, `covenant_status`, `recapture_type`, `recapture_method`, `notice_log_status`, `hap_renewal_*`, `qc_waived` must be enum values |
| servicing required by kind | agency_servicing_extract | loan: agency_loan_id + upb + maturity; grant: grant_id + (affordability_end \| recapture_end); owned_asset: asset_id + units_assisted + (affordability_end \| contract_expiration); administered_contract: contract_id + contract_expiration + units_assisted (exit 2 naming the rule when every row fails; otherwise rejects.csv) |

**Helper deadlines and the withdrawal anchor.** Every `AGENCY_DEADLINE` type and `PRESERVATION_NOTICE_WINDOW` are arithmetic on another event of the same property; `REGULATORY_LATEST_END` restates a component program end when the dates coincide. They are never a property's `first_*` event, never enter `events_in_horizon`, never count toward `programs_ending_same_24mo`, and are reported on the calendar header's `helper deadlines` segment outside the five basis counts; the thirteen agency types are additionally counted on the third segment `agency act-by n (next 90 days m)`. PuSH windows, `PUSH_*_DUE` and `TENANT_NOTICE_WINDOW` anchor on `withdrawal_anchor_date` = max of restriction-type ends only (LIHTC_EXTENDED_USE_END, SOFT_PROGRAM_END, AFFORDABILITY_PERIOD_END, COVENANT_END, USDA_515_MATURITY, HUD use-agreement end); a HAP / PRAC / PAC expiration enters the anchor only with a non-renewal signal (PRESERVATION_NOTICE_RECEIVED hap_optout, CA log opt-out, `hap_renewal_request_status = not_received`, or HAP_EXPIRATION detail mahra_20yr term ending). `push_anchor_source` in {restriction_end, hap_nonrenewal_signal, none} is stored on the window event. Each AGENCY_DEADLINE type has a row in `AGENCY_DEADLINE_META` (`agency-calendar.md`) giving its agency owner role, statutory cite (`verified_live: false`) and the owner cliff it derives from; EVENT_COLUMNS are unchanged and `detail` names the owner cliff.

**Stale contract dates.** A HAP / PRAC / PAC expiration already past as_of with no termination evidence (HUD tape terminated / expired-not-renewed, CA log) gets status `STALE_CONTRACT_DATE`, flag `Verify — Stale Contract Date`, signal `hap_date_stale`, a `Missing Source — Request Document` request for the current HAP contract / TRACS, its own Board_Totals row ("stale contract date — verify"), no derived agency deadlines, exclusion from `lost`, and `next_expected_expiration = last date + 12 mo` on the card. The HUD MF Assistance tape's current expiration overrides OHCS when both exist. In the 2026-10-02 OHCS file 33 of 130 metro HUD dates are already past; that is why this rule exists.

## 5. Canonical lead table (leads.csv)

Flat CSV, one row per property. Same column names appear in JSON `leads[]` and in the workbook `Intervention_Queue`, `Book_Watchlist` and `Preservation_Queue` tabs. `LEAD_COLUMNS` in `schema.py` fixes the order.

| block | columns | notes |
|---|---|---|
| identity and geography (v2 verbatim) | `property_id`, `property_name`, `address`, `city`, `zip`, `county_fips`, `county_name`, `jurisdiction`, `geo_modes`, `geo_grade`, `lat`, `lon`, `asset_class`, `status`, `units`, `year_built`, `rehab_year`, `property_type`, `programs`, `hud_contract`, `ami_30_60_units`, `ami_80_units`, `market_rate_units`, `rental_assistance_units` | `property_id` = `{state}-{county_fips}-{parcel_id}` when parcel known, else `addr:` + first 12 hex of sha1(upper USPS-normalized address + `|` + zip5); `programs` is a `;` list of `program` values; AMI buckets are descriptive only |
| owner and sponsor (organization level) | `owner_name`, `owner_type`, `owner_archetype`, `developer_name`, `manager_name`, `registered_agent`, `registered_agent_address`, `sos_status`, `notice_address`, `notice_address_source`, `sponsor_contact_role`, `org_resolution_grade` | no personal names, phones or emails; `notice_address` order: agency file (regulatory_agreement, hap_contract, loan_docs) then sos_registered_agent with `Verify — Notice Address` |
| universe and book | `universe`, `in_inventory`, `book_match`, `book_join_grade`, `book_kind` (a `;`-list in BOOK_KINDS order, loan first, when several instruments sit on one property; `payment_type` / `our_rate` then come from the first loan row and `recapture_*` from the row carrying a recapture position), `ohcs_funded`, `site_type` | `site_type` from OHCS `Scattered/Single Site`; scattered rows flag `scattered_site_join` |
| units at risk | `restricted_units`, `units_basis`, `units_at_risk`, `hap_units_at_risk`, `prac_units_at_risk`, `other_ra_units`, `psh_units_at_risk`, `family_3br_plus_units`, `vulnerability_flags` | computed once in `plb/units.py` (rules in `affordable_public_am.json` `units_at_risk_rule`); `vulnerability_flags` `;` list of elderly / disabled / veteran / sro / psh from OHCS Property Type and PSH_Units |
| our position | `agency_loan_ids`, `grant_ids`, `agency_programs`, `public_upb`, `public_upb_at_risk`, `public_grant_at_risk`, `our_rate`, `payment_type`, `our_maturity`, `our_maturity_basis`, `affordability_end`, `recapture_type`, `recapture_method`, `recapture_amount`, `recapture_exposure`, `covenant_status`, `senior_lien_type`, `senior_maturity`, `senior_maturity_basis`, `senior_upb`, `coterminous_senior_cliff`, `am_officer` | book columns come only from the servicing adapter; `public_upb_at_risk` = upb where any owner-cliff PRESSURE event <= 36 mo OR covenant_status in {watch, default} OR coterminous_senior_cliff; `public_grant_at_risk` = recapture_exposure (`recap-math.md`); `am_officer` is organization scope (a public employee's assignment is a public record); `am_officer_email` is internal only and never a lead column |
| first events (v2 verbatim) | `first_debt_event_type`, `first_debt_event_date`, `first_debt_months_out`, `first_debt_basis`, `first_debt_source`, `first_reg_event_type`, `first_reg_event_date`, `first_reg_months_out`, `first_reg_basis`, `first_reg_source` | earliest non-helper PRESSURE event of the family inside the horizon, not suppressed, not STALE_CONTRACT_DATE |
| anchors and clocks | `withdrawal_anchor_date`, `push_anchor_source`, `owner_cliff_type`, `owner_cliff_date`, `owner_cliff_band`, `agency_action_type`, `agency_action_date`, `agency_action_months_out`, `agency_action_basis`, `agency_action_owner`, `action_band` | `owner_cliff_*` = earliest owner-side PRESSURE event (REGULATORY non-helper, DEBT; excluding STALE_CONTRACT_DATE); `agency_action_*` = earliest AGENCY_DEADLINE event with months_out >= -12, else blank — except that the score step overrides `agency_action_*` with the primary route's own act-by when a route names one (optout_response -> HAP_OPTOUT_PACKAGE_DUE; a passed HAP_OPTOUT_NOTICE_DEADLINE becomes signal `optout_notice_deadline_passed_unconfirmed` + `Verify — CA Log` instead of an OVERDUE act-by), so leads.csv and leads_scored.csv can differ on these columns by design; `action_band` = min(agency act-by, owner cliff) and is the lead's `urgency_band` |
| events | `events_in_horizon` | JSON list of `{event_type, event_date, months_out, basis, confidence, source, verify_flag, alt_dates, window_start, window_end, direction}`; AGENCY_DEADLINE family excluded |
| recap sizing (our_book only) | `est_restricted_noi`, `noi_source`, `recap_gap_estimate` | blank unless `rent-limits.json` is populated and universe is our_book with recap_status announced / under_application |
| status and intent | `notice_status`, `tenant_notice_status`, `hap_renewal_request_status`, `hap_renewal_option`, `next_expected_expiration`, `recap_status`, `qc_status`, `qc_waived`, `rofr_recorded`, `apps_flag` | |
| mandate | `mandate_fit`, `mandate_eligible_products`, `mandate_ineligible_reason` | from `plb/mandate.py` against the pack `mandate.json` |
| sponsor | `sponsor_cliff_count` | properties of the same normalized owner organization with a cliff inside 36 months |
| scoring | `signals`, `verify_flags`, `score_raw`, `intervention_score`, `board_impact`, `queue_band`, `urgency_band`, `primary_route`, `secondary_routes`, `exclusion_reason` | `board_impact` = units_at_risk x timing_fraction(owner_cliff_band); `urgency_band` = `action_band` |
| intervention | `intervention`, `intervention_owner`, `statutory_cite`, `owner_notice_required`, `tenant_notice_required`, `verify_before_action`, `next_action`, `compliance_gates`, `kpi_flags` | `intervention` is a catalog id from `assets/interventions/`; `statutory_cite` always carries "(verify)" in this build; `compliance_gates` from {counsel_only, fair_housing_tenant_data, preservation_law, lihtc_tenant_protections} |
| run | `pii_scope`, `source_vintages`, `as_of_date` | `source_vintages` = `source_id=vintage;...` |

Removed from v2: `est_value`, `value_source` (NOAH adapter extras only), `est_noi` (renamed `est_restricted_noi`), `est_loan_balance`, `balance_basis`, `est_ltv`, `est_dscr_refi`, `refi_gap_pct`, `equity_cushion_pct`, `assumable_debt`, `decision_maker_name`, `dm_source`, `contact_grade`, `motivation_score`, `tier`, `route`, `outreach_angle`, `outreach_template`, `verify_before_outreach`. `months_out` = (event_date - as_of_date).days / 30.4, rounded to one decimal.

## 6. Companion events table (events.csv)

One row per event. Columns (instrument lineage added; `scripts/plb/schema.py` `EVENT_COLUMNS`; `test_contract.py` compares the two lists): `event_id, property_id, instrument_id, event_type, event_family, direction, event_date, months_out, urgency_band, basis, confidence, source, source_vintage, derivation, program, detail, value, verify_flag, alt_dates, window_start, window_end, status, event_date_quality`.

- `event_id` is unique within a run: `{property_id}:{n}` for the OHCS adapter, `{kind}:{source_id}:{property_id}:{event_type}:{source_id}:{date}` for the servicing adapter (two loans maturing the same day survive), `{property_id}:{event_type}:{date}` for the others. Legacy CSV comparisons join on `property_id` + `instrument_id` + `event_type` + `program` + `detail`. Use the separate stable IDs in `book_model.json` for instrument workflow lineage; see [instrument model](instrument-model.md).
- `urgency_band` is the Section 1 band for `months_out` (OVERDUE through BEYOND); `program` is the `program` enum value the event belongs to (blank when none); `event_date_quality` in `declared_format | auto_unambiguous | ambiguous | rejected | blank`.
- `status` in `FUTURE | PAST | STALE_CONTRACT_DATE | SUPPRESSED | RETIRED | REJECTED`. SUPPRESSED is set by `merge_leads.py` on DEBT events while `SUPPRESS_UNTIL` is in the future; STALE_CONTRACT_DATE per Section 4; RETIRED when a ROUTING event closes the lead; REJECTED rows are kept for Rejects_Verify and never scored.
- `derivation` is a human-readable formula, e.g. `withdrawal_anchor_date (LIHTC_EXTENDED_USE_END 2029-06-01) - 30 months (owner notice no sooner than this date per OAR 813-115-0030; ORS 456.262 designee trigger, verify)`.
- For AGENCY_DEADLINE rows `detail` names the owner cliff the deadline derives from; agency owner role and cite come from `AGENCY_DEADLINE_META`, not from new columns.
- Servicing-sourced rows carry `source = agency_servicing` exactly and `detail = <id_kind>=<id>` (e.g. `agency_loan_id=OHCS-2014-0117`).

## 7. Rejects table (rejects.csv)

`property_key, property_id, column, raw_value, reason, flag, alt_dates`. Every row in the workbook `Rejects_Verify` tab comes from this file: parse rejections, servicing enum rejections (`Rejected — Out of Range`) and lead-level conflict flags (`Verify — Conflicting Sources`, `Verify — Ambiguous`). `Missing Source — Request Document` requests go to `documents_to_request.csv`; `Verify — Book Join` rows go to `book_join_gaps.csv`; `Verify — Stale Contract Date`, `Verify — Notice Log` and `Verify — CA Log` are counted in the brief's Data Gaps.

## 8. Calendar summary (calendar_summary.json) and units_at_risk.json

```jsonc
{
  "as_of": "YYYY-MM-DD",
  "horizon_years": 10,
  "regulatory_horizon_years": 10,
  "agency_profile": "hfa",
  "rows_in_geography": 810,
  "rows_excluded_in_development": 46,
  "book_rows": 14, "book_rows_matched": 11, "book_rows_unmatched": 3, "book_coverage": "partial",
  "by_basis": {"RECORDED": 0, "REPORTED": 0, "DERIVED": 0, "ESTIMATED": 0, "PROXY": 0},
  "by_family": {"DEBT": {}, "REGULATORY": {}, "HARD_DISTRESS": {}, "TAX_LIEN": {}, "PHYSICAL": {}, "OWNERSHIP": {}, "OPERATING": {}},
  "by_urgency": {"OVERDUE": 0, "CRITICAL": 0, "URGENT": 0, "APPROACHING": 0, "MONITOR": 0, "SCHEDULED": 0, "BEYOND": 0},
  "suppressed": 0,
  "rejected": 0,
  "stale_contract_dates": 33,
  "helper_events": 0,
  "helper_by_type": {"PRESERVATION_NOTICE_WINDOW": 0, "PUSH_WINDOW_PREP": 0, "PUSH_FIRST_NOTICE_DUE": 0, "PUSH_SECOND_NOTICE_DUE": 0, "TENANT_NOTICE_WINDOW": 0, "RECORDS_REQUEST_DUE": 0, "RECORDS_RESPONSE_DUE": 0, "ROFR_MATCH_DEADLINE": 0, "QC_RESPONSE_DUE": 0, "HAP_OPTOUT_NOTICE_DEADLINE": 0, "HAP_OPTOUT_PACKAGE_DUE": 0, "INSPECTION_DUE": 0, "USDA_PUBLIC_BODY_OFFER_WINDOW_END": 0, "REGULATORY_LATEST_END": 0},
  "agency_act_by": 0,
  "agency_act_by_next_90_days": 0,
  "push_window_open_count": 0,
  "notice_compliance_breaches": 0,
  "notice_log_unknown_share": 0.0,
  "header": "RECORDED 0 / REPORTED 0 / DERIVED 0 / ESTIMATED 0 / PROXY 0 / Suppressed 0 / Rejected 0 | helper deadlines 0 (notice arithmetic, LATEST duplicates; not counted above) | agency act-by 0 (next 90 days 0)"
}
```

The `header` string is what the brief quotes before any count. The five basis counts cover owner-side PRESSURE events that carry their own information; helper deadlines (every AGENCY_DEADLINE type, PRESERVATION_NOTICE_WINDOW, duplicate REGULATORY_LATEST_END) are counted on the second segment so that `DERIVED` means Year-15 and HOME-period dates, not notice arithmetic; the third segment counts the agency's own act-by dates and how many fall inside 90 days (`query_calendar.summarize()` computes `agency_act_by` and `next_90_days`; `plb/calendar.py` renders the string).

`units_at_risk.json` (written once by `score_preservation.py` from `plb/units.py`; read by the workbook and the brief; the three must agree):

```jsonc
{
  "as_of": "YYYY-MM-DD", "agency_profile": "hfa", "board_totals_variant": "loan_book",
  "by_owner_cliff_band": {"OVERDUE": {"properties": 0, "units_at_risk": 0, "hap_units_at_risk": 0, "prac_units_at_risk": 0, "other_ra_units": 0, "psh_units_at_risk": 0, "public_upb_at_risk": 0, "public_grant_at_risk": 0, "being_preserved_units": 0},
                          "CRITICAL": {}, "URGENT": {}, "APPROACHING": {}, "MONITOR": {}, "SCHEDULED": {}, "BEYOND": {},
                          "stale_contract_date_verify": {}, "no_dated_cliff": {}},
  "by_jurisdiction": {"Multnomah": {"<band>": {}}, "Washington": {}, "Clackamas": {}},
  "by_year": {"2026": {}, "2027": {}, "...": {}, "2036": {}},
  "headline": {"properties": 0, "units_at_risk": 0, "hap_units_at_risk": 0, "prac_units_at_risk": 0, "psh_units_at_risk": 0, "public_upb_at_risk": 0, "window_months": 36},
  "public_upb_total": 0,
  "book_verdict": "STABLE | WATCH | STRESSED | CRITICAL",
  "kpi": {"units_preserved_since_prior": 0, "units_lost_since_prior": 0, "flips": {"notice_filed": 0, "hap_renewed": 0, "loan_extended": 0, "qc_requested": 0}}
}
```

pha_am (`board_totals_variant: owned_assets`) swaps the UPB columns for `owned_units`, `pbv_households`, `rad_section18_status`.

## 9. Run manifest (runs/<as_of>/manifest.json)

```jsonc
{
  "as_of": "YYYY-MM-DD",
  "market_id": "us-or-multnomah",
  "config": {},                                  // full run_config snapshot
  "inputs": [{"file": "", "schema": "", "sha256": "", "vintage": "YYYY-MM-DD", "vintage_source": "filename | mtime | header"}],
  "pack": "references/sources/oregon-portland",
  "plb_version": "1.0.x",
  "flags": {"agency_profile": "hfa", "universe": "all", "mandate_file": "references/sources/oregon-portland/mandate.json", "pii_scope": "organization",
            "book_coverage": "partial", "noah_watch": false, "horizon_years": 10, "include_proxies": false,
            "records_classification": "agency working file; disclosable subject to ORS 192.345/192.355 review; tenant data excluded by design"},
  "sources_verified_live_false": ["..."],
  "outputs": {"run_dir_files": [], "handoff_files": [], "worklists": ["handoff/sos_worklist.csv", "handoff/documents_to_request.csv", "handoff/board_packet.csv"],
              "queues": ["notice_compliance_queue.csv", "nofa_targets.csv", "agency_calendar.csv", "sponsor_exposure.csv", "servicing_unmatched.csv", "book_join_gaps.csv", "status_flips.csv", "units_at_risk.json"]}
}
```

Removed flags: `query_type`, `buyer_profile`, `unit_range`, `price_or_value_band`, `strict_size_fit`, `lender_types`.

## 10. Identity, join, dedupe and date-conflict rules

- Normalize addresses with USPS abbreviations, strip unit designators for building-level keys, upper-case, collapse whitespace. OHCS prints some rows in upper case (`GOING 42`, `4636 NE 42ND AVE`); compare keys after upper() + normalize_address().
- OHCS rows: key `Property Name + Address`; never row order (row count changed 1,763 -> 1,819 between releases). HUD Project Number vs Ginnie case number: digits only.
- **Book join** (`plb/book_join.py`), recorded per row as `book_join_grade`: (1) `crosswalk` from `references/sources/<pack>/book_crosswalk.csv` (agency_loan_id or grant_id -> property_id, analyst-confirmed, grows run over run); (2) `address` via the v2 `property_id` construction computed for every servicing row regardless of parcel_id, with `ohcs_property_key` compared after upper() + normalize; (3) `fuzzy` when upper(name) token-set ratio >= 0.92 AND same zip5 AND phase tokens equal or absent on both sides (REPORTED-grade join, written to `merge_log.csv`, never auto-promoted); (4) `unmatched` -> `servicing_unmatched.csv`. Phase tokens {I, II, III, IV, A, B, C, 1, 2, 3, Phase n} are hard discriminators: "Powell Plaza I" vs "Powell Plaza II" scores 0.966 and must not join. Scattered-site rows join on the first address and flag `scattered_site_join`.
- **book_match**: book and inventory both -> `matched`, universe our_book, in_inventory true; owner_name matching the profile's `self_owner_tokens` -> `self_owned`, universe our_book; inventory-only under `book_coverage: full` and the profile's `expected_book_flag` true (hfa: `OHCS Funded?` = true; cdbg_home: programs intersect {HOME, CDBG}; others: the extract names the property but the join failed) -> `unmatched_expected`; inventory-only under `partial` -> `not_in_extract`; inventory-only with the flag false -> `not_in_book`; no extract at all -> every row `book_absent` (one Run Summary line, no per-row flags). Book-only rows (in our book, not found in the inventory at any join grade) are `book_only`, universe `our_book`, in_inventory false, `book_join_grade = unmatched`, listed in `servicing_unmatched.csv`, and scored on capital (`our_capital_at_risk` requires book_match in {matched, self_owned, book_only}), servicing events and `units_assisted`. Several book rows joining one property: `book_kind` becomes a `;`-list (loan first), `public_upb` sums, `our_maturity` is the earliest, `agency_loan_ids` / `grant_ids` union.
- **Field merge**: higher basis wins per field (v2 rule); book columns come only from the servicing adapter; owner_name blank in OHCS -> HUD Sec 8 `owner_organization_name` -> servicing property owner.
- **Event dedupe key** = (property_id, event_type, program, detail). Rows with event_family AGENCY_DEADLINE, event_type PRESERVATION_NOTICE_WINDOW, or source agency_servicing are exempt from the conflict-flag path (they are legitimately plural per property).
- **Date conflicts**: distinct event types never conflict. The OHCS PROXY LOAN_MATURITY is dropped when a RECORDED AGENCY_LOAN_MATURITY exists on the property (merge_log note). Same (event_type, program, detail) from two sources: keep both, higher basis governs `first_*`; both >= REPORTED and > 1 month apart -> `Verify — Conflicting Sources` on both and a Rejects_Verify row; agency RECORDED governs ties. Forecast notice statuses (RECORDED) override extract `notice_status` only if dated later. HUD Sec 8 tape HAP_EXPIRATION overrides the OHCS HUD_MF date.
- OHCS and the OHCS 10-Year Forecast share an upstream; agreement between them is not corroboration. Agency servicing rows, HUD tapes, SOS records and recorder documents are the independent legs.

## 11. Scoring JSON schema (references/scoring/*.json)

Class file shape (v2 Section 11 plus the four additions marked NEW):

```jsonc
{
  "class": "affordable_public_am",
  "version": "1.0",
  "total_weight": 100,
  "factors": [
    {
      "name": "units_households_at_risk",
      "weight": 25,
      "take": "max",                              // max | sum across matched bands (then modifiers added)
      "event_driven": false,                      // true: bands match events.csv rows; false: bands match lead / context fields
      "apply_basis_multiplier": true,
      "basis_from": "governing_event",            // NEW: attribute factor borrows the governing owner-cliff event's basis multiplier
      "requires": {"field": "owner_cliff_months_out", "op": "between", "value": [-12, 60], "inclusive": true},   // NEW: factor scores 0 when false
      "on_requires_fail": {"unmatched_expected": {"factor_status": "WATCH", "points": 0, "flag": "Verify — Book Join"}},  // NEW (optional)
      "cap": 25, "floor": 0,
      "bands": [
        {"id": "units_100_plus", "event_type": null, "signal": "units_at_risk",
         "match": {"field": "units_at_risk", "op": "gte", "value": 100}, "points": 25,
         "reading": "one line: how the agency asset manager experiences it (public-interest / book-risk reading)",
         "intervention": "the tool the agency can deploy, by catalog id (assets/interventions/<id>.md)",
         "sets_flag": "Verify — Notice Log"}  // optional
      ],
      "modifiers": [ /* same shape; additive after take */ ],
      "post_multipliers": [{"id": "recap_status"}],   // ids defined in shared_adjustments.multipliers
      "notes": ""
    }
  ],
  "hard_filters": [], "routes": {"precedence": [], "sentinels": [], "profile_gates": {}, "self_owned_skips": [], "rules": []}, "quality_rules": []
}
```

`match.op` values: `between` (inclusive low, exclusive high unless `inclusive: true`), `lt`, `lte`, `gt`, `gte`, `eq`, `in`, `exists`, `days_since_between`, and NEW `absent` (field blank or missing) and `contains` (`;`-list membership). `match.field` for event bands resolves on the event first (`months_out`, `value`, `detail`, `days_since`, `status`, `basis`, `confidence`, `program`, `source`, `verify_flag`) then on the lead / context; virtual field `event_present` (`eq X` / `in [...]`). Multiple conditions use `"all": [...]` / `"any": [...]`. `lever` from v2 is renamed `intervention`.

Context fields computed by `build_context` (exact names): `units_at_risk`, `restricted_units`, `hap_units_at_risk`, `prac_units_at_risk`, `psh_units_at_risk`, `family_3br_plus_units`, `units` (numeric), `family_3br_share`, `hap_share`, `elderly_or_disabled`, `vulnerability_flags_list`, `notice_window_state` in {not_open, open_first, open_second, closed_first_due, closed_second_due}, `notice_status`, `tenant_notice_status`, `hap_renewal_request_status`, `owner_cliff_months_out`, `lihtc_compliance_end_months_out`, `agency_action_months_out`, `coterminous_senior_cliff`, `sponsor_cliff_count`, `apps_flag`, `out_of_state_sponsor`, `ownership_changed`, `ownership_changed_since_year15`, `lp_transferred_recent`, `as_of_year`, `recent_rehab` (rehab_year >= as_of_year - 5), `book_match`, `self_owned`, `recap_status`, `recap_evidence_basis`, `mandate_fit`, `programs_list`, `programs_ending_same_24mo` (excludes NOTICE_COMPLIANCE_BREACH and helpers), `hap_and_extended_use_same_24mo`, `has_pressure_in_horizon`, `independent_families`, `families_present`, `building_age_years`, `code_cases_open`, `high_displacement_tract`, `underserved_district`, `rent_to_fmr_ratio` (NOAH).

Factor output: `{name, weight, points_raw, basis_multiplier, post_multipliers, points, factor_status (scored | WATCH | n/a), evidence[], reading, intervention, matched_bands}`; empty evidence -> points 0.

**Basis arithmetic (one rule, mirrored in `shared_adjustments.governing_event_rule` and `public-am-module.md` Section 5):** `points = (sum of base-band take + modifiers, capped at the weight) x basis_multiplier x post_multipliers`, where the basis multiplier is the minimum across the BASE bands that scored (for `basis_from: governing_event`, the governing owner-cliff event); modifiers never move the basis multiplier. An event's `confidence` (< 1) scales the points of every band or modifier that event matched (HAP_EXPIRATION 0.70 annual / term-unknown; 0.90 20-year MAHRA or agency PBV contract). `Verify — Ambiguous` on a base event forces 0.40. Worked example (Powell Plaza I, hfa): hap_le_24 18 x 0.70 = 12.6, hap_annual_renewal 2 x 0.70 = 1.4, hap_optout_package_due_le_6 3 (DERIVED, no basis effect) -> 17.0 x 0.90 (REPORTED HAP_EXPIRATION) = 15.3 of 20. Shared mechanics live in `shared_adjustments.json`; class files never restate multipliers, queue bands or caps.

## 12. Route precedence and sentinels

The eight user routes are the only intervention routes. `primary_route` is chosen by fixed precedence, statutory clocks first, then money, then programs: `optout_response > notice_compliance > qc_admin > designee_rofr > recap_committee > servicing_watch > nofa_offer > ta_sponsor`. Every other matched route goes to `secondary_routes`. Each rule is gated by the profile's `routes_enabled` (`agency-profiles.yaml`): `qc_admin` needs `administers_qc`; `designee_rofr` needs `is_qualified_purchaser` or `is_designee`; `optout_response` needs `is_pbca` or `receives_push_notice`; `cdbg_home` receives INSPECTION_DUE and recapture review in place of PuSH enforcement. `self_owned` rows skip notice_compliance, designee_rofr, nofa_offer and ta_sponsor. `notice_compliance` is PRIMARY on NOTICE_COMPLIANCE_BREACH, on `notice_status = not_received_confirmed` past a due date, on an unconfirmed tenant notice inside the SB 973 window, or on `notice_status = unknown` past a due date ONLY when a notice log is loaded for the run (`profile.notice_log_loaded`: any lead carries a populated notice_status from the servicing extract or PuSH forecast); with no log loaded, unknown silence registers notice_compliance as a SECONDARY "confirm the PuSH-CP log" route with `Verify — Notice Log` and the 6-point intent band, so recap_committee / optout_response / servicing_watch keep the card. When a route names its own act-by (optout_response -> HAP_OPTOUT_PACKAGE_DUE) the score step overrides `agency_action_*` with it (Section 5). Two sentinels: `none` (scored, has_pressure_in_horizon, no rule hit; Book_Watchlist or Preservation_Queue with AM status Monitoring; not in the Intervention Queue) and `excluded` (`exclusion_reason` names the cause). `servicing_watch` is primary only on a trigger <= 60 months, covenant_status in {watch, default}, REAC < 60, an open NONCOMPLIANCE_FINDING, INSPECTION_DUE <= 6 months or a senior cliff <= 60 months; a healthy book loan is `none`. The precedence list is stored in both scoring JSONs as `routes.precedence` so tests can assert it. Rule conditions are in `affordable_public_am.json` `routes.rules`.

## 13. Canonical servicing extract (agency_servicing_extract)

Full specification in `servicing-extract.md`. Schema id `agency_servicing_extract`; detection by `match_columns: [book_kind, program]` plus `match_any` groups `{any: [agency_loan_id, grant_id, asset_id, contract_id]}`, `{any: [maturity, affordability_end, recapture_end, contract_expiration]}`, `{any: [ohcs_property_key, parcel_id, address, property_id]}` (`detect_schema()` honors `match_any`). Columns (snake_case): `book_kind, agency_loan_id, grant_id, asset_id, contract_id, property_name, address, city, zip, county_fips, parcel_id, property_id, ohcs_property_key, program, units_assisted, upb, accrued_interest, rate, rate_type, payment_type, origination_date, maturity, affordability_end, contract_expiration, recapture_type, recapture_method, recapture_amount, recapture_start, recapture_end, covenant_status, lien_position, coterminous_with, shared_appreciation_pct, senior_lien_type, senior_maturity, senior_upb, notice_log_status, notice_received_date, notice_detail, tenant_notice_status, hap_renewal_request_status, hap_renewal_option, qc_request_date, qc_request_complete_date, qc_waived, third_party_offer_mailed_date, third_party_offer_received_date, qp_offer_delivered_date, usda_prepay_request_date, rad_chap_date, section_18_application_date, last_inspection_date, open_findings_count, last_8823_date, last_reac_score, last_reac_date, apps_flag, recap_status, notice_address, notice_address_source, am_officer, am_officer_email, basis, as_of`. The user spec's `UPB` maps to `upb`; `recapture` maps to `recapture_type` / `recapture_method` / `recapture_amount` / `recapture_start` / `recapture_end`. Events emitted are listed in `servicing-extract.md` Section 4 and all carry `source = agency_servicing`, basis from the `basis` column (default RECORDED).
