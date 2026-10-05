# Canonical Servicing and Grant Extract (`agency_servicing_extract`)

The agency's own loan, grant, owned-asset and administered-contract ledger is the primary tape of this skill and the only RECORDED source for its own maturities, affordability periods, recapture terms, covenant status, notice log and QC log. This file defines the canonical columns the adapter `scripts/ingest_servicing_extract.py` reads, how a row is validated by `book_kind`, which events it emits, and how it joins the inventory universe. No real agency extract existed when this pack was built; the schema is a design proposal grounded in generic soft-debt conventions (residual-receipts and cash-flow notes, 40-75 year terms, due-on-sale, coterminous seconds) and the pack ships a synthetic fixture (`scripts/tests/fixtures/agency_servicing_sample.csv`) keyed to real OHCS property names so the join is exercised.

## Contents

1. Why the extract comes first
2. Schema detection and `book_kind` validation
3. Canonical columns
4. Events emitted
5. Join to the inventory (book_match, book_join_grade, book_coverage)
6. Date formats, numerics, enums
7. Profile notes (hfa, city_housing, county, pha_am, cdbg_home)
8. What the extract never carries

---

## 1. Why the extract comes first

`build_universe.py` runs `ingest_servicing_extract.py` before the OHCS, HUD and forecast adapters so that every later adapter can match property ids against the book. Every book row becomes a lead with `universe = our_book` and `in_inventory = false` until the join confirms it. Without an extract the run is universe-only: every row is `book_match = book_absent`, the our_capital_at_risk factor is 0 for all rows, and the brief's Run Summary says "book absent: capital factor 0 for all rows; outputs are preservation targeting and notice compliance only". The `--book` argument is optional for that reason; tests cover both modes.

## 2. Schema detection and `book_kind` validation

`dataset-schemas.yaml` block `agency_servicing_extract`:

- `match_columns: [book_kind, program]`
- `match_any`: `{any: [agency_loan_id, grant_id, asset_id, contract_id]}`, `{any: [maturity, affordability_end, recapture_end, contract_expiration]}`, `{any: [ohcs_property_key, parcel_id, address, property_id]}`. `plb/schema.detect_schema()` honors `match_any`: a block matches when every `match_columns` entry and at least one column from every `match_any` group are present.

Per-row validation by `book_kind` (exit 2 naming the failing rule when every row fails; otherwise the failing rows go to `rejects.csv` with `Rejected — Out of Range`):

| book_kind | required | typical holder |
|---|---|---|
| `loan` | `agency_loan_id` + `upb` + `maturity` | hfa, city_housing, county |
| `grant` | `grant_id` + (`affordability_end` or `recapture_end`) | cdbg_home, county, city_housing |
| `owned_asset` | `asset_id` + `units_assisted` + (`affordability_end` or `contract_expiration`) | pha_am |
| `administered_contract` | `contract_id` + `contract_expiration` + `units_assisted` | pha_am (PBV), hfa as PBCA |

A file missing `book_kind` and every date column (fixture `agency_servicing_bad_schema.csv`) fails detection and exits 2 with the rule named.

## 3. Canonical columns

snake_case; the user spec's `UPB` maps to `upb`, `recapture` maps to `recapture_type` / `recapture_method` / `recapture_amount` / `recapture_start` / `recapture_end`.

| column | type / enum | required | notes |
|---|---|---|---|
| `book_kind` | `loan` \| `grant` \| `owned_asset` \| `administered_contract` | yes | drives validation and Board_Totals variant |
| `agency_loan_id` | string | loan | the agency's loan number; event ids embed it |
| `grant_id` | string | grant | |
| `asset_id` | string | owned_asset | PHA AMP / asset id |
| `contract_id` | string | administered_contract | PBV / HAP contract number |
| `property_name` | string | | copied as the agency writes it; OHCS names may be upper case |
| `address`, `city`, `zip`, `county_fips` | string | address for join | USPS-normalized at ingest; zip5 |
| `parcel_id` | string | | kept for a future assessor / NOAH source; the address grade is computed regardless |
| `property_id` | string | | if the agency already carries the pack's id |
| `ohcs_property_key` | string | | `Property Name|Address` as printed in the OHCS file; compared after upper() + normalize |
| `program` | `program` enum | yes | HOME, CDBG, HTF, LIFT, GHAP, HDGP, OAHTC, OTHER_OHCS, LOCAL_REG, PHB_LOAN, TIF, LEVY, PBV, HAP ... |
| `units_assisted` | int | owned_asset, administered_contract | overrides program unit counts for SOFT_PROGRAM_END / AFFORDABILITY_PERIOD_END units_at_risk |
| `upb` | number | loan | unpaid principal balance as of `as_of` |
| `accrued_interest` | number | | deferred / residual-receipts notes |
| `rate` | number (decimal) | | 0.0 for 0% notes |
| `rate_type` | `fixed` \| `variable` | | |
| `payment_type` | `hard_pay` \| `residual_receipts` \| `deferred` \| `forgivable` | | a change between runs is the `loan_recast` KPI flip |
| `origination_date` | date | | |
| `maturity` | date | loan | -> AGENCY_LOAN_MATURITY |
| `affordability_end` | date | grant / owned_asset | -> AFFORDABILITY_PERIOD_END (program carried) |
| `contract_expiration` | date | administered_contract | -> HAP_EXPIRATION program PBV / HAP, confidence 0.90 |
| `recapture_type` | `home_recapture` \| `home_resale` \| `home_rental_repayment` \| `cdbg` \| `shared_appreciation` \| `none` | | `home_recapture` / `home_resale` are HOMEBUYER positions (24 CFR 92.254); a rental HOME loan or grant is `home_rental_repayment`: 24 CFR 92.503(b) requires repayment of ALL HOME funds invested when the 92.252 affordability period is not met (method `full`), unless the RECORDED written agreement states a schedule |
| `recapture_method` | `full` \| `prorata_reducing` \| `forgiveness_schedule` \| `cdbg_fmv_share` \| `none` | | pack `agency-profiles.yaml` supplies the default per program: rental HOME `full` (92.503(b)); `prorata_reducing` is the homebuyer 92.254(a)(5)(ii) reduction (profile key `HOME_HOMEBUYER`); `forgiveness_schedule` only when the PJ's recorded loan agreement states one |
| `recapture_amount`, `recapture_start`, `recapture_end` | number, date, date | | `recapture_end` -> GRANT_RECAPTURE_END; `recap-math.recapture_exposure` |
| `covenant_status` | `current` \| `watch` \| `default` \| `cured` \| `released` | | `default` -> COVENANT_DEFAULT; `watch` -> signal covenant_watch |
| `lien_position` | int | | |
| `coterminous_with` | string (agency_loan_id) | | |
| `shared_appreciation_pct` | number | | > 0 with `maturity` -> SHARED_APPRECIATION_DUE |
| `senior_lien_type` | `senior_lien_type` enum | | |
| `senior_maturity`, `senior_upb` | date, number | | -> LOAN_MATURITY REPORTED, detail `lender_type=<senior_lien_type>`; feeds `coterminous_senior_cliff` |
| `notice_log_status` | `received` \| `not_received_confirmed` \| `unknown` | | the agency's own PuSH-CP log (hfa) or received-notice file (local government); blank -> unknown and reported in Run Summary |
| `notice_received_date` | date | | with `received` -> PRESERVATION_NOTICE_RECEIVED (Needs Anchor Date when blank) |
| `notice_detail` | `push_first` \| `push_second` \| `hap_optout` | | |
| `tenant_notice_status` | `confirmed` \| `not_confirmed` \| `unknown` \| `n/a_pre_operative` | | SB 973 tenant notice (verify operative date) |
| `hap_renewal_request_status` | `received` \| `not_received` \| `unknown` | | from the CA; drives optout_response routing |
| `hap_renewal_option` | `1a` \| `1b` \| `2` \| `3` \| `4` \| `5` \| `6_optout` \| `unknown` | | Section 8 Renewal Guide options (verify) |
| `qc_request_date`, `qc_request_complete_date` | date | | complete date starts QC_RESPONSE_DUE (+1 yr); request date alone adds a Needs Anchor Date note |
| `qc_waived` | `true` \| `false` \| `unknown` | | `true` -> QC_REQUEST_INELIGIBLE, no clock |
| `third_party_offer_mailed_date`, `third_party_offer_received_date` | date | | mailed -> THIRD_PARTY_OFFER_RECEIVED + ROFR_MATCH_DEADLINE (+30 d); received-only -> `Verify — Mailing Date` |
| `qp_offer_delivered_date` | date | | the qualified purchaser's offer (with notice of intent to record) delivered to the owner -> ROFR_RECORDABLE_DATE (+30 d; ORS 456.262: the Notice of ROFR is recordable only after the offer plus 30 days, verify) |
| `usda_prepay_request_date` | date | | -> USDA_PREPAY_REQUEST_RECEIVED + USDA_PUBLIC_BODY_OFFER_WINDOW_END (+180 d, verify) |
| `rad_chap_date`, `section_18_application_date` | date | | -> RAD_CHAP, SECTION_18_APPLICATION |
| `last_inspection_date` | date | | -> INSPECTION_DUE (+1/2/3 yrs by units for HOME per 24 CFR 92.504(d); +3 yrs LIHTC per 26 CFR 1.42-5) |
| `open_findings_count`, `last_8823_date` | int, date | | -> NONCOMPLIANCE_FINDING (detail open_finding / 8823_filed, value count) |
| `last_reac_score`, `last_reac_date` | int, date | | -> REAC_SCORE RECORDED |
| `apps_flag` | bool | | HUD 2530 / APPS flag on a controlling participant |
| `recap_status` | `none` \| `announced` \| `under_application` \| `closed` | | the agency's own application pipeline is REPORTED-or-better evidence |
| `notice_address` | string | | where statutory notices to the owner go |
| `notice_address_source` | `regulatory_agreement` \| `hap_contract` \| `loan_docs` \| `sos_registered_agent` \| `unknown` | | |
| `am_officer` | string | | asset manager assigned (name and role); organization scope, a public record |
| `am_officer_email` | string | | INTERNAL only; never written without `--internal` |
| `basis` | `basis` enum | | default RECORDED |
| `as_of` | date | | ledger date; the run's `--as-of` may differ |

## 4. Events emitted

Every event: `source = agency_servicing`, basis from the `basis` column (default RECORDED), `detail = <id_kind>=<id>` so same-type events on one property survive merge, `event_id = {property_id}:{event_type}:{loan_or_grant_id}:{date}`.

| column(s) | event | family (direction) | notes |
|---|---|---|---|
| `maturity` (loan) | AGENCY_LOAN_MATURITY | DEBT (PRESSURE) | the OHCS PROXY LOAN_MATURITY on the same property is dropped at merge |
| `affordability_end` | AFFORDABILITY_PERIOD_END | REGULATORY (PRESSURE) | `program` carried; enters the PuSH withdrawal anchor |
| `contract_expiration` (administered_contract) | HAP_EXPIRATION | REGULATORY (PRESSURE) | program PBV / HAP; confidence 0.90 |
| `recapture_end` | GRANT_RECAPTURE_END | REGULATORY (PRESSURE) | |
| `covenant_status = default` | COVENANT_DEFAULT | OPERATING (PRESSURE) | dated `as_of`; non-decaying while open |
| `shared_appreciation_pct > 0` and `maturity` | SHARED_APPRECIATION_DUE | DEBT (PRESSURE) | |
| `qc_request_complete_date` (or `qc_request_date` with a Needs Anchor Date note) with `qc_waived != true` | QC_ELIGIBILITY status=requested + QC_RESPONSE_DUE (+1 yr) | REGULATORY (PRESSURE) + AGENCY_DEADLINE | IRC 42(h)(6)(I) |
| `qc_waived = true` | QC_REQUEST_INELIGIBLE | REGULATORY (ROUTING) | intervention qc_waiver_acknowledgement; no clock |
| `third_party_offer_mailed_date` | THIRD_PARTY_OFFER_RECEIVED + ROFR_MATCH_DEADLINE (+30 d) | REGULATORY (ROUTING) + AGENCY_DEADLINE | ORS 456.263 (verify) |
| `qp_offer_delivered_date` | ROFR_RECORDABLE_DATE (+30 d) | AGENCY_DEADLINE | ORS 456.262; OAR 813-115-0060 (verify) |
| `notice_log_status = received` | PRESERVATION_NOTICE_RECEIVED (detail `notice_detail`) + RECORDS_REQUEST_DUE (+10 d) | REGULATORY (PRESSURE) + AGENCY_DEADLINE | Needs Anchor Date when `notice_received_date` blank |
| `usda_prepay_request_date` | USDA_PREPAY_REQUEST_RECEIVED + USDA_PUBLIC_BODY_OFFER_WINDOW_END (+180 d) | REGULATORY (ROUTING) + AGENCY_DEADLINE | 7 CFR 3560.659 (verify) |
| `rad_chap_date` | RAD_CHAP | REGULATORY (ROUTING) | |
| `section_18_application_date` | SECTION_18_APPLICATION | REGULATORY (ROUTING) | |
| `open_findings_count > 0` or `last_8823_date` | NONCOMPLIANCE_FINDING | OPERATING (PRESSURE) | detail open_finding / 8823_filed; value = count |
| `last_reac_score` | REAC_SCORE | OPERATING (PRESSURE) | RECORDED when from the agency file |
| `last_inspection_date` | INSPECTION_DUE | AGENCY_DEADLINE (PRESSURE) | cadence from pack market-params `inspection_cadence_home` / `inspection_cadence_lihtc` |
| `senior_maturity` | LOAN_MATURITY | DEBT (PRESSURE) | REPORTED; detail `lender_type=<senior_lien_type>` |

`notice_log_status = not_received_confirmed` emits no event itself; `plb/agency_calendar.py` emits NOTICE_COMPLIANCE_BREACH when PUSH_FIRST_NOTICE_DUE has passed.

## 5. Join to the inventory

Order recorded per row as `book_join_grade` (`plb/book_join.py`; `pipeline-contract.md` Section 10):

1. `crosswalk`: `references/sources/<pack>/book_crosswalk.csv` (`agency_loan_id` or `grant_id` -> `property_id`, analyst-confirmed; grows run over run as fuzzy matches are confirmed).
2. `address`: the v2 `property_id` (`addr:` + sha1 of normalized address + `|` + zip5) computed for every servicing row regardless of `parcel_id`; `ohcs_property_key` compared after upper() + normalize_address() because OHCS prints some rows in upper case.
3. `fuzzy`: upper(name) token-set ratio >= 0.92 AND same zip5 AND phase tokens equal or absent on both sides. REPORTED-grade; written to `merge_log.csv`; never auto-promoted. Phase tokens {I, II, III, IV, A, B, C, 1, 2, 3, Phase n} are hard discriminators ("Powell Plaza I" vs "Powell Plaza II" scores 0.966 and must not join). Fixture: "Village Gardens Apartments", 97205 -> Village Garden Apartments at 0.98.
4. `unmatched`: written to `servicing_unmatched.csv` with candidate matches; the lead stays in `our_book` with `in_inventory = false` and scores on capital, servicing events and `units_assisted` (eval E5 Hollow Oak Commons; E3 Sumner Street Flats).

`book_match` and `book_coverage`: see `pipeline-contract.md` Section 10. Under `book_coverage: full` an inventory row the profile expects in book (`expected_book_flag`) that did not join is `unmatched_expected` (our_capital_at_risk 0, factor status WATCH, `Verify — Book Join`, Book_Join_Gaps row; queue not capped). Under `partial` it is `not_in_extract` with no flag. Never a guessed balance.

Scattered-site rows join on the first address and carry `scattered_site_join`.

## 6. Date formats, numerics, enums

Dates are declared per column in `dataset-schemas.yaml` (`format: iso` default); profile a new extract with `python3 scripts/date_profile.py <file>` first and paste the snippet. Numeric: `upb, accrued_interest, rate, recapture_amount, units_assisted, shared_appreciation_pct, senior_upb, open_findings_count, last_reac_score` (commas stripped). Enums are validated; an unknown value rejects the row with `Rejected — Out of Range` and the brief counts it.

## 7. Profile notes

| profile | book_sources | expected_book_flag | book_kinds | notes |
|---|---|---|---|---|
| `hfa` (OHCS) | `ohcs_funded_flag`, `agency_servicing_extract` | OHCS `OHCS Funded?` == true (420 of 810 metro rows) | loan, grant, administered_contract (as PBCA) | the only profile that administers QC; notice_log_status is the PuSH-CP log |
| `city_housing` (PHB) | `phb_loan_extract` | null (unmatched_expected only when the extract names the property) | loan, grant | PHB loans and the City's 60-year covenant (COVENANT_END) |
| `county` | `home_cdbg_levy_extract` | null | loan, grant | HOME / CDBG / Metro bond / levy awards |
| `pha_am` (Home Forward) | `pha_owned_assets`, `pbv_contracts` | null; `self_owner_tokens` set `self_owned` | owned_asset, administered_contract | Board_Totals variant `owned_assets` (owned_units, pbv_households, rad_section18_status) |
| `cdbg_home` (PJ) | `home_cdbg_affordability_extract` | programs intersect {HOME, CDBG} | grant, loan | INSPECTION_DUE by 24 CFR 92.504(d); recapture review in place of PuSH enforcement; metro OHCS has 0 HOME-only rows, so the PJ's own extract is the only RECORDED source for AFFORDABILITY_PERIOD_END |

## 8. What the extract never carries

Tenant-level data (TRACS / 50059, names, incomes), owner personal phone or email, skip-trace output. `am_officer_email` is accepted but written only with `--internal`. The extract is an agency working file: disclosable subject to ORS 192.345 / 192.355 review (verify), tenant data excluded by design (`pii-and-sunshine.md`).
