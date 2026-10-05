# HOME, HTF and CDBG: Affordability Periods, Recapture, Inspections

Federal rules behind `AFFORDABILITY_PERIOD_END`, `GRANT_RECAPTURE_END`, `RECAPTURE_TRIGGER`, `INSPECTION_DUE`, `recapture_type` / `recapture_method`, `recap_math.recapture_exposure` and the `cdbg_home` profile. Every row is `verified_live: false` (ecfr.gov and law.cornell.edu were egress-blocked); figures come from search snippets of the regulations and of HUD / NCSHA summaries. The participating jurisdiction's own written agreements and IDIS records are the RECORDED source for every date and amount; this file tells the pack which rule to derive from when the agreement is silent.

## Contents

1. HOME rental affordability periods (24 CFR 92.252(e))
2. HOME enforcement, foreclosure and PJ options
3. HOME inspections (24 CFR 92.504(d))
4. HOME homebuyer recapture vs resale (24 CFR 92.254(a)(5)); repayment (92.503)
5. Housing Trust Fund (24 CFR 93.302)
6. CDBG real property change of use (24 CFR 570.505; 570.208)
7. Encoding summary
8. What to verify

---

## 1. HOME rental affordability periods (24 CFR 92.252(e))

| per-unit HOME investment (pre-2025 rule) | minimum period | pack derivation |
|---|---|---|
| under $15,000 | 5 years | `AFFORDABILITY_PERIOD_END` = completion + 5 y (DERIVED) when the written agreement is silent |
| $15,000 to $40,000 | 10 years | + 10 y |
| over $40,000, or any rehabilitation involving refinancing | 15 years | + 15 y |
| new construction or acquisition of newly constructed housing | 20 years | + 20 y |

The period begins after project completion and runs regardless of the loan term, the note's maturity or any transfer of ownership. The 2025 HOME final rule (published 2025-01-06, effective 2025-02-05) raised the dollar thresholds. Post-2025 Table 1 to 24 CFR 92.252 (snippet of the current regulation): under $25,000 per unit -> 5 years; $25,000-$50,000 -> 10 years; over $50,000, or rehabilitation involving refinancing -> 15 years; new construction -> 20 years. Applicable only to projects committed under the new rule (new commitments) or that opt in by amending the written agreement; pre-2025 projects keep the $15,000 / $40,000 breakpoints above. Note: the table now appears under paragraph (d)(4) in the 2025 numbering while this pack cites 92.252(e) throughout — paragraph lettering may have moved from (e) to (d)(4); verify before quoting. Store the rule vintage per project (`agency-profiles.yaml` `home_rule_vintage_note`) and read the written agreement; the agreement's stated period is RECORDED and governs.

## 2. HOME enforcement, foreclosure and PJ options

Affordability must be imposed by deed restriction, covenant running with the land or another HUD-approved mechanism. The restriction may terminate upon foreclosure or transfer in lieu of foreclosure; the PJ may use purchase options, rights of first refusal or other preemptive rights to purchase the housing before foreclosure to preserve affordability, and the restriction revives if the owner (or an affiliate) reacquires the property (24 CFR 92.252(e)(3)-(4) under the 2013 numbering; verify the current paragraph). Pack effect: a senior default, receiver, lis pendens or bankruptcy on a HOME property is a covenant-extinguishment risk for the PJ -> `recap_committee` with `loan_extension_recast_memo` option (e) (cure, payoff, PJ purchase at foreclosure).

## 3. HOME inspections (24 CFR 92.504(d))

| project size | on-site inspection frequency | pack |
|---|---|---|
| 1-4 units | every 3 years | `INSPECTION_DUE` = last_inspection_date + 36 months |
| 5-25 units | every 2 years | + 24 months |
| 26 or more units | annually | + 12 months |

Plus annual review of rents, incomes and occupancy. Parameters in `market-params.json` `inspection_cadence_home`. A missed inspection is an agency-side compliance gap surfaced on the Agency_Calendar, not an owner event; `servicing_watch` when `INSPECTION_DUE` <= 6 months.

## 4. HOME homebuyer recapture vs resale (24 CFR 92.254(a)(5)); repayment (92.503)

For homebuyer assistance the PJ elects, in its written agreement, either resale (the property stays affordable to a subsequent low-income buyer at an affordable price with a fair return to the homeowner) or recapture (the PJ recovers all or part of the direct HOME subsidy, limited to net proceeds) over a 5 / 10 / 15-year period keyed to the direct subsidy per unit (under $15,000: 5; $15,000-$40,000: 10; over $40,000: 15). Recapture options include full recapture, a reduction pro rata by time in the period, shared net proceeds, and owner-investment returned first. RENTAL projects are different: 24 CFR 92.503(b) requires the PJ to repay ALL HOME funds invested in a project that does not meet its 92.252 affordability requirements for the full period — there is no pro-rata reduction unless the written agreement provides one. Pack: `recapture_type` home_recapture / home_resale (homebuyer, 92.254) or home_rental_repayment (rental, 92.503(b)); `recapture_method` full / prorata_reducing / forgiveness_schedule (the written agreement governs; the profile default for HOME rental is `full`, `HOME_HOMEBUYER` is prorata_reducing, and `forgiveness_schedule` is used only when the recorded loan agreement states one); `recap_math.recapture_exposure`; a sale, payoff or foreclosure inside the period is `RECAPTURE_TRIGGER` -> `covenant_recapture_review`.

## 5. Housing Trust Fund (24 CFR 93.302)

HTF-assisted rental units must remain affordable for not less than 30 years after project completion (the grantee may require longer), with ELI rent limits (the greater of 30% of the poverty line or 30% of 30% AMI), enforced by deed restriction / covenant; restrictions may terminate on foreclosure or transfer in lieu with grantee preemptive rights. Pack: `SOFT_PROGRAM_END` program HTF = completion + 30 years (DERIVED) when no explicit end; the OHCS HTF_Expiration_Date column is REPORTED where present; ELI units count toward the PSH / ELI weighting of units at risk where identifiable; profile recapture method full.

## 6. CDBG real property change of use (24 CFR 570.505; 570.208)

For real property acquired or improved with more than $25,000 of CDBG funds, from the first expenditure until five years after closeout of the grant, the recipient may not change the use (or planned use) without providing affected citizens reasonable notice and opportunity to comment and then either (a) meeting a new national objective under 570.208 (not a general-government building), or (b) reimbursing the CDBG program for the current fair market value of the property less any non-CDBG share. Pack: `recapture_type` cdbg; `recapture_method` cdbg_fmv_share (requires an FMV input, else `Missing Source — Request Document`); CDBG covenants are short and recapture-based, so a change of use is a `covenant_recapture_review` / qc_admin-style compliance event, not a preservation cliff; `AFFORDABILITY_PERIOD_END` program CDBG = closeout + 5 years when the agreement is silent.

## 7. Encoding summary

| rule | event | basis | profile route | intervention |
|---|---|---|---|---|
| HOME rental period end | AFFORDABILITY_PERIOD_END (program HOME) | RECORDED (agreement) / DERIVED (completion + period) | cdbg_home / county / city_housing: servicing_watch; nofa_offer for re-investment | covenant_recapture_review; preservation_nofa_invitation |
| HOME recapture period end | GRANT_RECAPTURE_END | RECORDED | servicing_watch | covenant_recapture_review (rental: `full` exposure under 92.503(b) until the period ends; homebuyer: prorata per 92.254(a)(5)(ii)) |
| sale / payoff / foreclosure inside the period | RECAPTURE_TRIGGER | RECORDED (recorder / payoff) | recap_committee | covenant_recapture_review (demand) |
| inspection due | INSPECTION_DUE (AGENCY_DEADLINE) | DERIVED | servicing_watch (<= 6 mo) | servicing_watch_memo (current loan) / covenant_enforcement_notice (watch, default, finding) |
| HTF 30-year end | SOFT_PROGRAM_END (program HTF) | REPORTED / DERIVED | nofa_offer | preservation_nofa_invitation |
| CDBG change of use | AFFORDABILITY_PERIOD_END (program CDBG); RECAPTURE_TRIGGER | RECORDED / DERIVED | servicing_watch | covenant_recapture_review (citizen notice and comment) |

## 8. What to verify

The 2025 Table 1 to 92.252 thresholds ($25,000 / $50,000, from a snippet) and which projects opted in; whether the affordability table now sits at 92.252(d)(4) rather than (e); the 92.503(b) repayment text for rental projects; the foreclosure-termination paragraph numbering and the exact PJ preemptive-rights text; 92.504(d) current frequencies; 92.254(a)(5) recapture option wording; 93.302 ELI rent limit definition; 570.505 dollar threshold and the five-years-after-closeout clock. Read each from eCFR and record the date; until then every derived period is DERIVED with `verify`.
