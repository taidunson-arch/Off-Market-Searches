# Intervention Catalog

What the agency can actually do about each event, who at the agency owns it, which statute or regulation it rests on, whether it is an owner-facing or tenant-facing notice, and when it is due. This replaces off-market-deal-finder v2's outreach templates and compliance gates: there is no approach angle, no first-touch cadence and no letter to a would-be counterparty to a sale. Each catalog entry is a file in `assets/interventions/<id>.md` with a YAML front block (`id, routes[], trigger_events[], agency_owner, statutory_cite[] ({cite, verified_live: false, note}), owner_notice, tenant_notice, timeline, pii_scope, first_action, kpi_flip_on_success, notice_address_rule`), a "confirm current statutory text before sending" banner, and a letter / memo / checklist skeleton. Every cite in this build is `verified_live: false`; the pack's `legal-timelines.md` carries the same banner.

## Contents

1. Selection rule
2. Route -> intervention map
3. Catalog table
4. Agency roles
5. Compliance gates carried from v2
6. Statutory trigger rule (what is never sent early)
7. KPI flips

---

## 1. Selection rule

`score_preservation.py` sets the lead's `intervention` from the primary route's rule in `affordable_public_am.json` `routes.rules` (each rule names its intervention), then `intervention_owner`, `statutory_cite`, `owner_notice_required`, `tenant_notice_required`, `verify_before_action` and `next_action` (= the catalog `first_action` + `agency_action_date`) from the catalog front block. Secondary routes' interventions are listed on the card under "Handoffs ready / also". A lead with `primary_route none` carries no intervention; `excluded` carries none. `board_packet_summary` applies to every run, not to a lead.

## 2. Route -> intervention map

| primary_route | interventions (first listed = default) | agency owner |
|---|---|---|
| `optout_response` | `optout_tenant_notice_check` (renewal status unknown / notice deadline passed), `optout_response_plan` (opt-out confirmed or no renewal request inside 120 days) | pbca_liaison; nofa_program_manager |
| `notice_compliance` | `push_window_prep` (window open; secondary only), `push_notice_demand_letter` (NOTICE_COMPLIANCE_BREACH), `push_records_request` (after a notice is received), `tenant_notice_check` (SB 973 window) | push_program_manager; compliance_officer |
| `qc_admin` | `qc_request_acknowledgement` (RECORDED request), `qc_waiver_acknowledgement` (qc_waived true), `qc_marketing_plan` (clock running) | compliance_officer |
| `designee_rofr` | `rofr_notice_recording`, `rofr_match_offer` (THIRD_PARTY_OFFER_RECEIVED), `rofr_assignment_memo`, `usda_prepay_response` (USDA_PREPAY_REQUEST_RECEIVED) | legal_counsel; push_program_manager; nofa_program_manager |
| `recap_committee` | `loan_extension_recast_memo`, `zero_pct_recap_term_sheet`, `hud_legacy_response` (236 / 202 / PRAC), `pha_repositioning` (self_owned) | am_officer; hud_mf_asset_manager; pha_development |
| `servicing_watch` | `servicing_watch_memo` (healthy loan with a dated trigger), `covenant_enforcement_notice` (covenant watch / default, REAC < 60), `enforcement_8823` (LIHTC finding), `covenant_recapture_review` (HOME / CDBG / HTF), `prac_renewal_coordination` (PRAC / PAC) | am_officer; compliance_officer; cpd_program_manager |
| `nofa_offer` | `preservation_nofa_invitation`, `qc_coordination_with_hfa` (non-hfa profile with a QC signal) | nofa_program_manager |
| `ta_sponsor` | `ta_sponsor_engagement`, `rofr_assignment_memo`, `qc_coordination_with_hfa` | nofa_program_manager; legal_counsel |
| all | `board_packet_summary` | board_liaison |

## 3. Catalog table

| id | trigger events | agency owner | statutory basis (verify) | owner notice | tenant notice | timeline | kpi on success |
|---|---|---|---|---|---|---|---|
| `push_window_prep` | PRESERVATION_NOTICE_WINDOW open, PUSH_WINDOW_PREP, REGULATORY_LATEST_END, LIHTC_EXTENDED_USE_END | push_program_manager | OAR 813-115-0030; ORS 456.260(1) | none (internal) | none | anchor - 36 to - 30 mo | notice_filed if a notice arrives |
| `push_notice_demand_letter` | NOTICE_COMPLIANCE_BREACH; PUSH_FIRST/SECOND_NOTICE_DUE passed with not_received_confirmed | push_program_manager | ORS 456.260 (owner notice no sooner than 30 / at least 24 months; (1)/(2) split unread)-(2); ORS 456.262 (withdrawal bar; designee on silence, HB 2095); OAR 813-115-0030; SB 973 per-tenant extension | certified mail to notice_address; cc local government / OHCS | restates the owner's duty | within 10 business days of the due date; 30-day response | notice_filed |
| `push_records_request` | PRESERVATION_NOTICE_RECEIVED, RECORDS_REQUEST_DUE | push_program_manager | OAR 813-115-0050 (qualified purchaser access to property, records and documents: compliance reports, approved rent schedule with actual rents); ORS 456.262(6)-(7) | written request after notice only | none | send within 10 days of notice (internal); 30-day response is a working target (period not found in rule text) | basis upgrade |
| `tenant_notice_check` | TENANT_NOTICE_WINDOW, PRESERVATION_NOTICE_RECEIVED, PUSH_SECOND_NOTICE_DUE | compliance_officer | SB 973 / ORS 456.259; HB 3042 | proof request | verifies the owner's duty | anchor - 30 mo | tenant_notice_confirmed |
| `rofr_notice_recording` | PRESERVATION_NOTICE_RECEIVED, NOTICE_COMPLIANCE_BREACH (designee on silence), LIHTC_EXTENDED_USE_END, ROFR_RECORDABLE_DATE | legal_counsel | ORS 456.262 (two-step: qualified purchaser's offer with notice of intent to record, then recording after 30 days); OAR 813-115-0060; OAR 813-115-0035 | step 1 offer to the owner; step 2 copy of recorded notice / appointment | none | step 1 on or after the designee-appointment date; step 2 no earlier than offer + 30 d (ROFR_RECORDABLE_DATE); the ROFR expires 24 mo after the withdrawal date (verify) | ROFR_RECORDED |
| `rofr_match_offer` | THIRD_PARTY_OFFER_RECEIVED, ROFR_MATCH_DEADLINE | legal_counsel | ORS 456.263 (match must include an affordability-preservation commitment on OHCS-determined terms; permitted earnest-money and 240-day closing variations); OAR 813-115-0070 | matching offer by certified mail | none | 30 days from certified mailing | preserved / recap_closed |
| `rofr_assignment_memo` | ROFR_RECORDED, THIRD_PARTY_OFFER_RECEIVED, PRESERVATION_NOTICE_RECEIVED | legal_counsel | ORS 456.262; ORS 456.250 | assignment / designee notice | none | before the match deadline | recap_closed |
| `optout_tenant_notice_check` | HAP_EXPIRATION (HAP/RAC/PBV <= 12 mo), HAP_OPTOUT_NOTICE_DEADLINE, HAP_OPTOUT_PACKAGE_DUE, PRESERVATION_NOTICE_RECEIVED hap_optout | pbca_liaison | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8; Renewal Guide ch. 11 | none (CA-side check) | verifies the owner's one-year notice | expiration - 365 d and - 120 d | hap_renewed / hap_optout |
| `optout_response_plan` | PRESERVATION_NOTICE_RECEIVED hap_optout; HAP_EXPIRATION with not_received; REAC < 60 | pbca_liaison | Renewal Guide chs. 2-3, 15; 42 U.S.C. 1437f(t); 24 CFR 402.8 | counteroffer / transfer letter | PHA enhanced vouchers | inside the one-year period; bridge -> extension -> 4% -> 20-yr HAP | hap_renewed / recap_closed |
| `prac_renewal_coordination` | HAP_EXPIRATION (PRAC / PAC) | hud_mf_asset_manager | Notice H 2022-05 | none required | none | 12 mo before expiration | hap_renewed |
| `hud_legacy_response` | HUD_DIRECT_LOAN_MATURITY, PREPAY_WINDOW_OPEN, HAP_EXPIRATION (PRAC) | hud_mf_asset_manager | Notice H 2013-17; 24 CFR 891.530; Notice H 2013-25; NHA Section 250 | recap invitation to sponsor; HUD-required owner tenant notice | HUD-required; TPVs pre-1974 202 | review 90-180 d; Section 250 150-270 d | recap_closed |
| `usda_prepay_response` | USDA_515_PREPAY_ELIGIBLE, USDA_PREPAY_REQUEST_RECEIVED, USDA_PUBLIC_BODY_OFFER_WINDOW_END, USDA_515_MATURITY, USDA_EXIT_PROJECTED | nofa_program_manager | 7 CFR 3560.653-.662; MPR notices | to RD as interested party; public-body offer inside the window | RD tenant notice (+30 d) | 180-day offer window | preserved / recap_closed |
| `qc_request_acknowledgement` | QC_ELIGIBILITY requested (RECORDED), QC_RESPONSE_DUE | compliance_officer | IRC 42(h)(6)(E)(i)(II); 42(h)(6)(I); 42(h)(6)(F); 1.42-18; 42(h)(6)(E)(ii); OHCS draft QC procedure | acknowledgement; price certification request | status notice per policy | acknowledge in 10 business days; one-year period | qc_requested |
| `qc_waiver_acknowledgement` | QC_REQUEST_INELIGIBLE | compliance_officer | IRC 42(h)(6)(E)(i)(II); QAP / REUA waiver | waiver letter | none | 10 business days; no clock | none |
| `qc_marketing_plan` | QC_ELIGIBILITY requested, QC_RESPONSE_DUE <= 12 mo, lapsed_decontrol | compliance_officer | IRC 42(h)(6)(F), (I); OHCS draft QC procedure | presentment of a bona fide contract | status notice per policy | present by QC_RESPONSE_DUE - 30 d | qc_presented |
| `qc_coordination_with_hfa` | QC signal seen by a non-HFA profile | nofa_program_manager | IRC 42(h)(6)(E)-(I) | none (to the HFA) | none | on first sight | qc_presented (HFA) |
| `preservation_nofa_invitation` | LIHTC_EXTENDED_USE_END, HAP_EXPIRATION, QC_ELIGIBILITY, PRESERVATION_NOTICE_RECEIVED, USDA_515_PREPAY_ELIGIBLE, HUD_DIRECT_LOAN_MATURITY, SOFT_PROGRAM_END, AFFORDABILITY_PERIOD_END | nofa_program_manager | ORS ch. 456 / 458; 24 CFR 92, 93; IRC 42 (4%); Section 108; Metro 26-199; TIF / PCEF | invitation to apply | none | cohort 12-24 mo before the cliff; bridge inside 12 | recap_closed / preserved |
| `loan_extension_recast_memo` | AGENCY_LOAN_MATURITY, SHARED_APPRECIATION_DUE, senior cliff, COVENANT_DEFAULT, HUD_DIRECT_LOAN_MATURITY, RECEIVER_APPOINTED, BANKRUPTCY_FILED | am_officer | agency loan documents; NHA 250 / H 2013-25; 24 CFR 92.252(e) foreclosure | owner application; default / cure notices | HUD-required for 236 prepayment only | maturity - 18 mo; committee 60-120 d | loan_extended / loan_recast / covenant_cured |
| `zero_pct_recap_term_sheet` | AGENCY_LOAN_MATURITY, LIHTC_COMPLIANCE_END (ROFR exercise), LIHTC_EXTENDED_USE_END, REAC < 60 | am_officer | agency lending authority; mandate zero_pct_rehab_recap; IRC 42(i)(7) | term sheet to sponsor | none | committee 60-120 d | recap_closed |
| `servicing_watch_memo` | AGENCY_LOAN_MATURITY / AFFORDABILITY_PERIOD_END / senior cliff <= 60 mo on a loan whose covenant_status is current | am_officer | loan / regulatory agreement (monitoring only) | none | none | calendar the recast / extension decision | loan_extended |
| `covenant_enforcement_notice` | COVENANT_DEFAULT, covenant_status watch, REAC < 60, NONCOMPLIANCE_FINDING, tax events, code, dissolution, INSPECTION_DUE | am_officer | loan / regulatory agreement covenants; 24 CFR 92.504(d); 26 CFR 1.42-5; NSPIRE notice | default / cure notice | none | per cure period | covenant_cured |
| `enforcement_8823` | NONCOMPLIANCE_FINDING, REAC_SCORE, CODE_CASE_OPEN, OCCUPANCY_DROP, TAX_EXEMPTION_LOST | compliance_officer | IRC 42(m)(1)(B)(iii); 26 CFR 1.42-5(e) | notice of noncompliance | none | correction period; 8823 within 45 d | covenant_cured |
| `covenant_recapture_review` | AFFORDABILITY_PERIOD_END, GRANT_RECAPTURE_END, RECAPTURE_TRIGGER, SOFT_PROGRAM_END, UNENCUMBERED, JUDICIAL_FORECLOSURE_FILED | cpd_program_manager | 24 CFR 92.252(e), 92.254(a)(5), 92.503, 93.302, 570.505, 570.208 | repayment demand / change-of-use determination | none (CDBG citizen notice) | on trigger or period end | covenant_cured |
| `pha_repositioning` | RAD_CHAP, SECTION_18_APPLICATION, REAC_SCORE, owned-asset cliffs | pha_development | RAD H-2019-09 / PIH-2019-23 REV-4; 24 CFR 970; PIH 2024-40 / 2026-23 | n/a (PHA is owner) | resident consultation; TPVs | CHAP to closing 12-24 mo | recap_closed / preserved |
| `ta_sponsor_engagement` | LIHTC_COMPLIANCE_END, LIHTC_EXTENDED_USE_END, ROFR_RECORDED, MANAGER_CHANGE, ENTITY_ADMIN_DISSOLVED, QC (non-HFA) | nofa_program_manager | IRC 42(i)(7); SB 51; QAP aggregator certifications (model) | engagement letter to sponsor | none | Year 13-14 start | recap_closed / preserved |
| `board_packet_summary` | all | board_liaison | SB 32; ORS 192.355(2) / 192.345 | none | none | per board cycle | reports all flips |

## 4. Agency roles

`AGENCY_ROLES`: `am_officer` (asset manager assigned to the loan / grant), `compliance_officer` (LIHTC monitoring, 8823, QC administration at the HFA, HOME inspections), `push_program_manager` (PuSH-CP / preservation notices and records requests), `nofa_program_manager` (centralized NOFA, preservation RFP, TA referrals), `legal_counsel` (recording, matching offers, assignments, workouts), `pbca_liaison` (contract administration: renewal requests, opt-out letters, tenant-letter review), `board_liaison` (board packet, public records officer for redaction), `hud_mf_asset_manager` (HUD regional center counterpart for 236 / 202 / PRAC), `rd_state_office` (USDA RD counterpart), `cpd_program_manager` (HOME / CDBG PJ), `pha_development` (PHA development and asset management). Oregon examples: OHCS Asset Management, PuSH-CP Program Manager, HCA contract administration, NOFA team, Compliance; PHB Asset Management and Preservation Program; Home Forward Development / Asset Management; county housing division; Portland Consortium PJ staff.

## 5. Compliance gates carried from v2

Only four gates survive, because the agency does not solicit: `preservation_law` (any Oregon property meeting ORS 456.250: the statutory clocks, the match right and the tenant-notice duty govern every action), `lihtc_tenant_protections` (IRC 42(h)(6)(E)(ii) three-year tail; enhanced vouchers at opt-out; USDA prepayment protections), `fair_housing_tenant_data` (tenant records never used; counts only), `counsel_only` (BANKRUPTCY_FILED active: automatic stay, 11 U.S.C. 362). Dropped: dnc_scrub, consent_capture, wholesaler_registration, equity_purchaser_rules, probate_cooling, broker_exclusive, assumption_approval.

## 6. Statutory trigger rule (what is never sent early)

No demand or records letter is generated before the statutory trigger it cites: `push_records_request` only after PRESERVATION_NOTICE_RECEIVED (RECORDS_REQUEST_DUE = notice + 10 days); `push_notice_demand_letter` only after PUSH_FIRST_NOTICE_DUE has passed with `notice_status = not_received_confirmed` (NOTICE_COMPLIANCE_BREACH); `rofr_match_offer` only on THIRD_PARTY_OFFER_RECEIVED with the certified mailing date; `qc_request_acknowledgement` only on a RECORDED request with `qc_waived != true`; `optout_response_plan` only on a confirmed opt-out or a missing renewal request inside 120 days. Inside the first-notice window the only intervention is `push_window_prep`, which sends nothing. Absence in a dataset is never owner silence. The quality check "every notice_compliance row cites the window and the statute" and "no demand letter before notice" are asserted in tests.

## 7. KPI flips

Each catalog entry names the `flip_type` its success produces (`status_flips.csv`, `diff_forecast.py`): notice_filed, tenant_notice_confirmed, qc_requested, qc_presented, hap_renewed, hap_optout, loan_extended, loan_recast, covenant_cured, covenant_default, recap_closed, preserved, lost, new_to_list, left_list. `lost` requires termination evidence (HUD tape terminated / expired-not-renewed, CA log, or LIHTC_EXTENDED_USE_END passed with QC lapsed), never a stale date. The board packet reports every flip since the prior run.
