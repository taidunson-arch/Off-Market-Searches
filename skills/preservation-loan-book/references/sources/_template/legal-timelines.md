# Legal Timelines: <State> (preservation and loan-book posture)

Statutory and regulatory clocks the agency-calendar and event-derivation rules encode for this market, from the seat of the HFA, the city or county housing office, the PHA and the HOME / CDBG participating jurisdiction. Cite section numbers from the current statute text, record the edition / date you read, and mark anything taken from summaries `verify`. Every day / month count the scripts use lives in `market-params.json`, never here as a bare fact. Nothing here is legal advice; counsel reviews every intervention letter before it leaves. No foreclosure-clock, telephone-solicitation, wholesaler or equity-purchaser sections belong in this pack.

## Contents

1. State preservation-notice and purchase-right law
2. LIHTC federal mechanics (IRC 42) and the HFA's clocks
3. HOME, HTF and CDBG affordability, recapture, inspections
4. Project-based Section 8: opt-out notice, renewal options, PBCA, PRAC
5. HUD legacy programs and ownership review
6. USDA Section 515 prepayment and MPR
7. PHA repositioning: RAD and Section 18
8. Physical and compliance: NSPIRE / REAC and Form 8823
9. State public records law for packet redaction
10. Book-risk stub
11. Assessment regime (short)
12. Entity law (one row)

---

## 1. State preservation-notice and purchase-right law

Copy the state's row from `references/sources/federal/preservation-notice-laws-by-state.md` and verify it against statute text.

| element | section | rule | pack encoding | status |
|---|---|---|---|---|
| definition of covered housing (unit threshold, program set) | <section> | | `PUSH_COVERED_PROGRAMS`, `min_units`; `agency-profiles.yaml` `is_qualified_purchaser` | verify |
| owner notice timing to agency / local government (first; second if any) | <section> | <months — write the statute's own words, e.g. Oregon reads "no sooner than 30 and at least 24 months before withdrawal"; do not infer an earlier "window opens" month from a tenant-notice bound> | `PRESERVATION_NOTICE_WINDOW` windows (the earliest row may be an INTERNAL prep window — say so); `PUSH_FIRST_NOTICE_DUE`, `PUSH_SECOND_NOTICE_DUE` (`market-params` push_*_months) | verify |
| purchase right: offer, recording sequence, duration, match content | <section> | <e.g. Oregon ORS 456.262: qualified purchaser's offer first, Notice of ROFR recordable after 30 days, expires 24 months after withdrawal; ORS 456.263: 30-day match from certified mailing, match must carry an affordability commitment> | `qp_offer_delivered_date` -> `ROFR_RECORDABLE_DATE`; `ROFR_MATCH_DEADLINE`; `rofr_duration_months_after_termination` | verify |
| covered programs | <section> | <which assistance makes a property covered; whether HOME-only / LIHTC-only count> | `push_program_coverage_verified` (false -> `Verify — PuSH Coverage` on HOME-only / LIHTC-only rows) | verify |
| withdrawal bar | <section> | | basis of `NOTICE_COMPLIANCE_BREACH` reading | verify |
| agency designee / appointment on silence | <section> | | `designee_rofr` route on breach | verify |
| purchase right / ROFR / offer period and its duration | <section> | <days to match; duration> | `ROFR_RECORDED`, `THIRD_PARTY_OFFER_RECEIVED`, `ROFR_MATCH_DEADLINE` (`rofr_match_days`) | verify |
| owner records duty | <section> | <days> | `RECORDS_RESPONSE_DUE` (`records_request_response_days`) | verify |
| tenant and applicant notice | <section> | <months; languages; remedy for non-notice> | `TENANT_NOTICE_WINDOW` (`tenant_notice_months`); `tenant_notice_check` | verify |
| public registry of notices | <agency page or dataset> | | `notice_log_source` in `agency-profiles.yaml`; `PRESERVATION_NOTICE_RECEIVED` RECORDED only from the agency log, a records request or a recorder instrument | verify |
| sanctions / remedies | <section> | <describe exactly; many states bar sanctions on a withdrawing owner> | no fines language in the catalog unless the statute provides them | verify |

## 2. LIHTC federal mechanics (IRC 42) and the HFA's clocks

IRC 42(i)(1) compliance period (`LIHTC_COMPLIANCE_END`, any owner); 42(h)(6) extended use (state minimum beyond 15 years: <years>; `LIHTC_EXTENDED_USE_END`); 42(h)(6)(E)(i)(II) QC termination trigger and 42(h)(6)(I) one-year agency clock (`QC_RESPONSE_DUE`, `qc_response_months` 12); 42(h)(6)(F) / Treas. Reg. 1.42-18 price (`recap_math.qc_price_band`, memo-only); 42(h)(6)(E)(ii) three-year tenant protection; 42(i)(7) nonprofit / government ROFR (`ta_sponsor_engagement`); 42(m)(1)(B)(iii) and 26 CFR 1.42-5 monitoring and Form 8823 (`INSPECTION_DUE` 36 months; `enforcement_8823`; 45 days). State QC policy and first waiver year: `federal/qc-policy-by-state.md` row; `qc_waived` from the recorded extended-use agreement or the HFA's QC log.

## 3. HOME, HTF and CDBG affordability, recapture, inspections

24 CFR 92.252(e) rental affordability periods (`AFFORDABILITY_PERIOD_END`; store pre / post 2025 final-rule vintage; thresholds verify); 92.252(e) foreclosure termination and PJ options (`recap_committee` workout); 92.504(d) inspections (`INSPECTION_DUE`, `inspection_cadence_home`); 92.254(a)(5) recapture / resale (`recapture_type`, `recapture_method`, `recap_math.recapture_exposure`); 92.503 repayment (`covenant_recapture_review`); 24 CFR 93.302 HTF 30 years; 24 CFR 570.505 / 570.208 CDBG change of use (`cdbg_fmv_share`). Add the PJ's own written-agreement conventions here.

## 4. Project-based Section 8: opt-out notice, renewal options, PBCA, PRAC

42 U.S.C. 1437f(c)(8) and 24 CFR 402.8 one-year notice (`HAP_OPTOUT_NOTICE_DEADLINE`); Section 8 Renewal Policy Guidebook ch. 11 120-day package (`HAP_OPTOUT_PACKAGE_DUE`; verify chapter), chs. 2-3, 15 renewal options (`hap_renewal_option`; REAC >= 60 for MU2M); 42 U.S.C. 1437f(t) enhanced vouchers; the state's PBCA identity (`is_pbca`; CA opt-out log RECORDED); Notice H 2022-05 PRAC five-year renewals (`prac_renewal_coordination`; never `optout_response`). Note the state inventory's HAP date freshness: past dates with no termination evidence are `STALE_CONTRACT_DATE`.

## 5. HUD legacy programs and ownership review

NHA Section 250 / Notice H 2013-25 (236 / BMIR prepayment notice 150-270 days; IRP decoupling); Notice H 2013-17 / 24 CFR 891.530 (202 prepayment, 20-year use agreement, TPVs); 24 CFR 200 subpart H / HUD-2530 / APPS (`apps_flag`); TPA for ownership changes. Encode in `hud_legacy_response`; all verify.

## 6. USDA Section 515 prepayment and MPR

7 CFR 3560.653-.662 (request; RD tenant notice +30 d; incentives; 180-day nonprofit / public-body offer; 10-year restrictive-use extension; vouchers) -> `USDA_PREPAY_REQUEST_RECEIVED`, `USDA_PUBLIC_BODY_OFFER_WINDOW_END` (`usda_public_body_offer_days`); MPR notices -> `mandate.json` usda_mpr. All verify.

## 7. PHA repositioning: RAD and Section 18

RAD Notice H-2019-09 / PIH-2019-23 REV-4 (`RAD_CHAP`); Section 18 / 24 CFR 970 (`SECTION_18_APPLICATION`); PIH 2024-40 / 2026-23 blends. Encode in `pha_repositioning`; verify current deadlines.

## 8. Physical and compliance: NSPIRE / REAC and Form 8823

HUD NSPIRE scoring notice (fail < 60; `nspire_fail_score`); DEC referral thresholds (verify whether re-issued); 26 CFR 1.42-5(e) Form 8823 timing.

## 9. State public records law for packet redaction

| element | section | rule | pack encoding | status |
|---|---|---|---|---|
| presumption of disclosure | <section> | | `records_classification` | verify |
| personal-information exemption | <section> | <home address, personal phone / email treatment> | `pii_scope` public_packet redactions; Redaction_Log cite | verify |
| conditional exemptions / balancing | <section> | | | verify |

## 10. Book-risk stub

| instrument | section | why it matters | event |
|---|---|---|---|
| judicial / non-judicial foreclosure filing on a regulated asset | <section> | junior covenant and agency note can be extinguished | `JUDICIAL_FORECLOSURE_FILED`, `LIS_PENDENS` -> `recap_committee` |
| receivership; bankruptcy | <section>; 11 U.S.C. 362 | counterparty changes; automatic stay | `RECEIVER_APPOINTED`, `BANKRUPTCY_FILED` (gate counsel_only) |

## 11. Assessment regime (short)

<Does assessed value track market value? This pack carries no value on a lead; set `av_is_market` in market-params.json so downstream siblings do not scale AV.>

## 12. Entity law (one row)

| element | section | rule | use |
|---|---|---|---|
| LLC / LP annual report contents; administrative dissolution | <sections> | <managers / members / GPs listed?; days after missed report; reinstatement window> | `org_resolution_grade`; `ENTITY_ADMIN_DISSOLVED`; notice-address confirmation |
