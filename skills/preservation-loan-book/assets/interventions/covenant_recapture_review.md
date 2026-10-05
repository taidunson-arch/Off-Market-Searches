---
id: covenant_recapture_review
routes:
  - servicing_watch
  - recap_committee
trigger_events:
  - AFFORDABILITY_PERIOD_END
  - GRANT_RECAPTURE_END
  - RECAPTURE_TRIGGER
  - SOFT_PROGRAM_END
  - UNENCUMBERED
  - JUDICIAL_FORECLOSURE_FILED
agency_owner: cpd_program_manager
statutory_cite:
  - cite: "24 CFR 92.252(e)"
    verified_live: false
    note: "HOME rental affordability periods 5 / 10 / 15 / 20 years by per-unit HOME investment; 2025 final rule raised thresholds (opt-in) — exact figures verify"
  - cite: "24 CFR 92.254(a)(5)"
    verified_live: false
    note: "homebuyer recapture vs resale over 5 / 10 / 15 years"
  - cite: "24 CFR 92.503"
    verified_live: false
    note: "repayment of HOME funds"
  - cite: "24 CFR 93.302"
    verified_live: false
    note: "HTF 30-year affordability"
  - cite: "24 CFR 570.505; 570.208"
    verified_live: false
    note: "CDBG real property change of use: citizen notice and comment; new national objective or reimbursement of the CDBG share of FMV; five years after closeout"
owner_notice: "repayment demand or change-of-use determination to the owner; citizen notice and comment for a CDBG change of use"
tenant_notice: "none"
timeline: "trigger on sale / transfer / payoff / foreclosure inside the period; CDBG rule runs until five years after closeout"
pii_scope: organization
first_action: "compute recapture_exposure (recap_math, method per program); confirm the trigger (RECAPTURE_TRIGGER) or the approaching period end; decide re-investment (new period) vs recapture; send the determination"
kpi_flip_on_success: covenant_cured (re-invested) or none (recaptured)
notice_address_rule: "print notice_address and notice_address_source; agency file first (regulatory_agreement > hap_contract > loan_docs), SOS registered agent fallback with Verify — Notice Address; hold the letter when source is unknown"
---

# Intervention: `covenant_recapture_review`

> **Confirm current statutory text before sending.** Every cite in this build is `verified_live: false`: statute and regulation text was not read from an official source. Agency counsel reviews the cite, the window and the recipient before any letter leaves. Nothing here treats an owner as a counterparty to a sale; there is no bid and no purchase language unless the agency is exercising a statutory purchase right. PuSH enforcement is never described as a fine or penalty (ORS 456.265 is titled "Sanctions against withdrawing property owner prohibited"; verify).

## Purpose
The PJ's review when a HOME / CDBG / HTF affordability period approaches its end or a triggering event occurs inside it: recapture the public dollars or re-invest for a new period. The letter names the method and the amount.

## Determination skeleton
```
Property [property_name]; program [HOME | CDBG | HTF]; grant/loan [ids]; period [recapture_start]..[recapture_end] / affordability_end [date]
Trigger: [RECAPTURE_TRIGGER (sale / payoff / foreclosure on date) | period ends in n months]
Method: [full (rental HOME: 24 CFR 92.503(b) — all HOME funds invested are repayable when the 92.252 period is not met; verify) | prorata_reducing (HOMEBUYER assistance only, 92.254(a)(5)(ii)) | forgiveness_schedule (only when the recorded written agreement states one) | cdbg_fmv_share]; exposure as of [as_of]: $[recapture_exposure] (DERIVED from RECORDED terms)
Note: 92.252 paragraph lettering may have moved from (e) to (d)(4) under the 2025 HOME rule — verify the cite before sending
Options: (a) recapture $[ ] per 92.503 / 570.505 [verify]; (b) re-invest [product_id] for a new [years]-year period (92.252(e) / 93.302); (c) CDBG change of use: citizen notice and comment, new national objective
Units affected: [units_assisted]; INSPECTION_DUE status [date]
```
