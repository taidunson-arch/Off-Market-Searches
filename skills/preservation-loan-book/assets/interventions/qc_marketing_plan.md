---
id: qc_marketing_plan
routes:
  - qc_admin
trigger_events:
  - QC_ELIGIBILITY (requested)
  - QC_RESPONSE_DUE (<= 12 months)
  - QC_ELIGIBILITY (lapsed_decontrol)
agency_owner: compliance_officer
statutory_cite:
  - cite: "IRC 42(h)(6)(F); Treas. Reg. 1.42-18"
    verified_live: false
    note: "qualified contract price"
  - cite: "IRC 42(h)(6)(I)"
    verified_live: false
    note: "one-year period to present a buyer"
  - cite: "OHCS Draft Qualified Contract Procedure"
    verified_live: false
    note: "presenting a bona fide signed contract at the QC price, regardless of closing, removes the possibility of terminating the extended use period; verify"
owner_notice: "presentment of a bona fide contract to the owner before QC_RESPONSE_DUE"
tenant_notice: "agency notice of status per policy"
timeline: "market from acknowledgement; identify a buyer by month 8; present the contract no later than QC_RESPONSE_DUE - 30 days"
pii_scope: organization
first_action: "compute the QC price band (recap_math.qc_price_band, ESTIMATED, memo-only) as a budget order of magnitude pending the owner's certification; invite mission sponsors; line up the gap award; present the contract"
kpi_flip_on_success: qc_presented
notice_address_rule: "print notice_address and notice_address_source; agency file first (regulatory_agreement > hap_contract > loan_docs), SOS registered agent fallback with Verify — Notice Address; hold the letter when source is unknown"
---

# Intervention: `qc_marketing_plan`

> **Confirm current statutory text before sending.** Every cite in this build is `verified_live: false`: statute and regulation text was not read from an official source. Agency counsel reviews the cite, the window and the recipient before any letter leaves. Nothing here treats an owner as a counterparty to a sale; there is no bid and no purchase language unless the agency is exercising a statutory purchase right. PuSH enforcement is never described as a fine or penalty (ORS 456.265 is titled "Sanctions against withdrawing property owner prohibited"; verify).

## Purpose
The agency's plan to present a bona fide contract within the one-year period. The agency does not have to close the sale; presentment removes the exit permanently (OHCS draft procedure; verify). The intervention card says "present a contract", not "find a buyer who closes".

## Plan skeleton
```
Property [property_name]; QC_RESPONSE_DUE [date]; [n] months remaining
QC price: owner certification [received | requested]; agency band [recap_math.qc_price_band — ESTIMATED, order of magnitude only; superseded by certification]
Marketing: mission sponsors invited [list]; information package from push_records_request / qc acknowledgement records
Funding: [mandate_eligible_products]; bridge; new regulatory term
Presentment: bona fide signed contract by [QC_RESPONSE_DUE - 30 days]; counsel review; delivery by certified mail to [notice_address]
If lapsed (status lapsed_decontrol): three-year tenant protection monitoring (42(h)(6)(E)(ii)); last-chance preservation award; kpi lost only on evidence of termination
```
