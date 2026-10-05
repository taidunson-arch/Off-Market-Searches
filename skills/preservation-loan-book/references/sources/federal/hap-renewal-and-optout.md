# Project-Based Section 8: Renewal Options, Opt-Out Notice, the 120-Day Package, PBCA and PRAC

Federal rules behind `HAP_EXPIRATION` confidence, `HAP_OPTOUT_NOTICE_DEADLINE`, `HAP_OPTOUT_PACKAGE_DUE`, `hap_renewal_request_status`, `hap_renewal_option`, the `optout_response` route and its two interventions, the PRAC distinction and the `pbca_liaison` role. Every row is `verified_live: false` (hud.gov, law.cornell.edu and govinfo.gov were egress-blocked); chapter cites for the Renewal Guide come from state HFA summaries (WHEDA, WVHDF, Minnesota Housing) and must be checked against the March 2023 Guidebook.

## Contents

1. The one-year opt-out notice (MAHRA 8(c)(8); 24 CFR 402.8)
2. The 120-day opt-out package and CA letter review (Renewal Guide ch. 11)
3. Renewal options and what they mean for confidence (Renewal Guide chs. 2-3, 15)
4. Enhanced vouchers (42 U.S.C. 1437f(t))
5. The contract administrator's role (PBCA)
6. PRAC and PAC (Notice H 2022-05): not an opt-out risk
7. Stale contract dates and annual renewal
8. Encoding summary
9. The Portland pattern (bridge -> extension -> 4% -> 20-year HAP)
10. What to verify

---

## 1. The one-year opt-out notice (MAHRA 8(c)(8); 24 CFR 402.8)

An owner that does not intend to renew a project-based Section 8 HAP contract must provide written notice to tenants, HUD and the contract administrator not less than one year before the contract expires or terminates (42 U.S.C. 1437f(c)(8)(A)). If the owner does not give the notice, the owner may not evict the tenants or increase their rent until one year after proper notice is given; assisted tenants remain at a rent no higher than their last assisted-month rent even if HUD's HAP payments stop (1437f(c)(8)(B)). 24 CFR 402.8 sets content and delivery.

Pack: `HAP_OPTOUT_NOTICE_DEADLINE` = `HAP_EXPIRATION` - 12 months (`hap_optout_notice_months`), programs HAP / RAC / PBV only, status FUTURE only, never from a STALE_CONTRACT_DATE. When the deadline has passed and `hap_renewal_request_status` is unknown: signal `optout_notice_deadline_passed_unconfirmed`, flag `Verify — CA Log`, first action "confirm renewal request / opt-out notice at CA". Req-ID HAP-01.

## 2. The 120-day opt-out package and CA letter review (Renewal Guide ch. 11)

To opt out the owner must satisfy the one-year notification requirements and submit the opt-out request and certification to HUD / the CA not less than 120 days before expiration. Every tenant notification letter is reviewed by the AE / CA; a deficient letter requires a corrected notice and the one-year clock does not start until proper notice has reached HUD, the CA and the residents. Taping notices to doors is not an acceptable delivery method.

Pack: `HAP_OPTOUT_PACKAGE_DUE` = `HAP_EXPIRATION` - 120 days (`hap_optout_package_days`); the agency act-by for `optout_response_unconfirmed`; intervention `optout_tenant_notice_check` records the sufficiency finding and, when deficient, that the clock has not started. Req-ID HAP-02. An HFA that is the PBCA holds the clock by rejecting a defective letter.

## 3. Renewal options and what they mean for confidence (Renewal Guide chs. 2-3, 15)

| option | summary (verify) | pack reading |
|---|---|---|
| Option 1A / 1B — Mark-Up-To-Market | 1A entitlement when comparable market rent potential is at or above FMR and other conditions are met; 1B discretionary for projects serving >50% elderly / disabled / large families or in markets with <3% vacancy; 5-year minimum term up to 20 years; REAC score >= 60 with no uncorrected EH&S required; nonprofit exception path with a 20-year recorded Use Agreement (ch. 15) | the agency's counteroffer to an opt-out; `REAC_SCORE` < 60 blocks it (physical factor couples to the HAP factor) |
| Option 2 — OCAF / budget-based renewal | contract rents at or below market adjusted by OCAF or budget; 20-year MAHRA contracts available | detail `mahra_20yr_recent` when a 20-year term started within 24 months -> confidence 0.90 and modifier -5 (owner staying) |
| Options 3, 4, 5 | referral to Mark-to-Market; exception projects; portfolio reengineering demonstration / preservation projects | `hap_renewal_option` enum values 3 / 4 / 5; M2M portfolio membership informational |
| Option 6 — opt-out | one-year notice; 120-day package; enhanced vouchers | `6_optout`; `PRESERVATION_NOTICE_RECEIVED` detail hap_optout when the CA log records it |

Confidence rule unchanged from v2: `HAP_EXPIRATION` carries 0.70 when the renewal term is <= 5 years or unknown (OHCS-only rows: detail `term_unknown_annual_assumed`), 0.90 for a 20-year MAHRA renewal or an agency PBV / HAP contract from the servicing extract. Detail `short_renewal_pattern` / `annual_renewal` adds +2 (the owner keeps options open every year). `hap_renewal_request_status = received` (HUD-9624 on file) closes the opt-out question for the term: signal `optout_window_closed_for_term`, kpi `hap_renewed`, agency act-by = `next_expected_expiration` - 12 months.

## 4. Enhanced vouchers (42 U.S.C. 1437f(t))

On opt-out, expiration or termination, eligible assisted families may elect to remain and receive tenant-based enhanced vouchers. Pack: units-at-risk accounting distinguishes households protected by enhanced vouchers (household loss mitigated) from the unit loss (the restricted unit leaves the inventory); `hap_units_at_risk` stays the unit count; `optout_response_plan` step 4 opens enhanced-voucher planning with the PHA; the PHA (`pha_am`) owns the voucher administration task.

## 5. The contract administrator's role (PBCA)

Under PBCA annual contributions contracts the CA conducts management and occupancy reviews, adjusts contract rents, processes HAP contract expirations and terminations, pays vouchers, resolves health and safety issues, renews expiring contracts and reviews owner tenant-notification letters for opt-outs. Pack: `agency-profiles.yaml` `is_pbca` (Oregon: OHCS HCA historically administered ~260 contracts; identity under the 2024-2025 HUD re-solicitation not checked); when true, the CA's opt-out log and renewal-request log are RECORDED sources for `PRESERVATION_NOTICE_RECEIVED` (hap_optout) and `hap_renewal_request_status`; `pbca_liaison` is the agency owner of both opt-out interventions; `optout_response` requires `is_pbca` or `receives_push_notice`.

## 6. PRAC and PAC (Notice H 2022-05): not an opt-out risk

Section 202 / 811 Project Rental Assistance Contracts (and PACs) are renewed by HUD subject to appropriations; Notice H-2022-05 phased Section 202 PRACs onto five-year renewal terms (2023-2025, subject to appropriations) and updated the renewal amendment language for both 202 and 811 PRACs; it did not itself move 811 PRACs to five-year terms (811 PRAC term change: verify). The owner (a nonprofit or PHA sponsor of elderly / disabled housing) cannot opt out the way a Section 8 owner can. Pack: `prac_le_24` 10 points (appropriation and sponsor-capacity risk), `prac_units_at_risk` counted separately from `hap_units_at_risk`, never `optout_response`, intervention `prac_renewal_coordination` (hud_mf_asset_manager) and `hud_legacy_response` when a 202 recap is warranted; no HAP opt-out deadlines derive from a PRAC / PAC date.

## 7. Stale contract dates and annual renewal

Under annual renewal the TRACS expiration rolls every year; a state inventory snapshot that is not refreshed shows dates in the past. In the 2026-10-02 OHCS file 33 of 130 metro HUD dates are already past. Pack: a HAP / PRAC / PAC expiration past as_of with no termination evidence (HUD tape terminated / expired-not-renewed, CA log) is `STALE_CONTRACT_DATE` (`Verify — Stale Contract Date`), excluded from OVERDUE and from `lost`, with `next_expected_expiration` = date + 12 months, no agency deadlines, and a `Missing Source — Request Document` for the current HAP contract / TRACS. The HUD MF Assistance tape's current expiration overrides the OHCS column when both exist.

## 8. Encoding summary

| rule | event / column | pack parameter | intervention |
|---|---|---|---|
| one-year notice | HAP_OPTOUT_NOTICE_DEADLINE (AGENCY_DEADLINE, helper) | `hap_optout_notice_months` 12 | optout_tenant_notice_check (HAP-01) |
| 120-day package | HAP_OPTOUT_PACKAGE_DUE (AGENCY_DEADLINE, helper) | `hap_optout_package_days` 120 | optout_tenant_notice_check (HAP-02) |
| opt-out notice on file | PRESERVATION_NOTICE_RECEIVED detail hap_optout (RECORDED) | | optout_response_plan |
| renewal request on file | hap_renewal_request_status received; hap_renewal_option | | none (protective signal; kpi hap_renewed) |
| renewal term | HAP_EXPIRATION confidence 0.70 / 0.90; detail short_renewal_pattern / annual_renewal / mahra_20yr_recent / term_unknown_annual_assumed | | |
| PRAC / PAC | HAP_EXPIRATION program PRAC / PAC; prac_le_24; prac_units_at_risk | `prac_renewal_term_years` 5 | prac_renewal_coordination |
| stale date | status STALE_CONTRACT_DATE; next_expected_expiration | `hap_annual_renewal_roll_months` 12 | request current contract |

## 9. The Portland pattern (bridge -> extension -> 4% -> 20-year HAP)

Portland Housing Bureau's preservation program transfers privately owned expiring properties to mission nonprofits that renew the HUD contract for 20 years, with PHB acquisition gap financing (General Fund, Section 108 guarantee fund, CDBG / HOME, TIF; Spring 2025 RFP: $6.7M CDBG, $4.5M HOME, $12M PCEF, LIHTC recapitalization priority) and the City's 60-year affordability covenant. The "11x13" campaign (e.g. Hawthorne East, 71 units) used short-term acquisition financing plus a 3-year HAP extension, then 4% LIHTC acquisition / rehab and a new 20-year HAP contract; NOAH's Oregon Housing Acquisition Fund bridges acquisitions while renewals are negotiated. Pack: the canonical `optout_response_plan` sequence and the `phb_preservation_rfp` / `noah_ohaf_bridge` / `lihtc_4pct_gap` products in `mandate.json` (placeholders; verify).

## 10. What to verify

Renewal Guide (March 2023) chapter and section numbers for the 120-day package (ch. 11), Option 1B criteria and the nonprofit exception (ch. 15); 24 CFR 402.8 current text; the Oregon PBCA identity; Notice H 2022-05 PRAC renewal terms; HUD-9624 current form; the PHB RFP and 11x13 figures.
