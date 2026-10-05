---
id: zero_pct_recap_term_sheet
routes:
  - recap_committee
  - nofa_offer
trigger_events:
  - AGENCY_LOAN_MATURITY
  - LIHTC_COMPLIANCE_END (mission GP ROFR exercise)
  - LIHTC_EXTENDED_USE_END
  - REAC_SCORE (< 60, rehab need)
agency_owner: am_officer
statutory_cite:
  - cite: "agency lending authority; product terms in mandate.json (zero_pct_rehab_recap)"
    verified_live: false
    note: "0% recap / rehab loan terms; verify current product"
  - cite: "IRC 42(i)(7)"
    verified_live: false
    note: "nonprofit ROFR at debt + exit taxes — the recap often funds the exercise"
owner_notice: "term sheet to the sponsor"
tenant_notice: "none"
timeline: "committee cycle 60-120 days; fund at Year 15-16 for a ROFR exercise, or 12-24 months before a cliff"
pii_scope: organization
first_action: "size the recap gap and rehab need (physical-condition-assessment handoff when the physical factor fired); draft the term sheet; committee approval"
kpi_flip_on_success: recap_closed
notice_address_rule: "print notice_address and notice_address_source; agency file first (regulatory_agreement > hap_contract > loan_docs), SOS registered agent fallback with Verify — Notice Address; hold the letter when source is unknown"
---

# Intervention: `zero_pct_recap_term_sheet`

> **Confirm current statutory text before sending.** Every cite in this build is `verified_live: false`: statute and regulation text was not read from an official source. Agency counsel reviews the cite, the window and the recipient before any letter leaves. Nothing here treats an owner as a counterparty to a sale; there is no bid and no purchase language unless the agency is exercising a statutory purchase right. PuSH enforcement is never described as a fine or penalty (ORS 456.265 is titled "Sanctions against withdrawing property owner prohibited"; verify).

## Purpose
A non-binding term sheet for a 0% (or soft) recapitalization or rehabilitation loan from the agency: amount, rate, payment type, term coterminous with the senior, new affordability term, conditions. Used to fund a mission GP's ROFR exercise, a Year-15 recap or a troubled asset's capital needs.

## Term sheet skeleton
```
Borrower [sponsor organization]; property [property_name]; units [units] ([units_at_risk] restricted)
Loan amount: up to $[recap_gap_estimate + rehab_need] (ESTIMATED; final by underwriting)
Rate [0.0% per mandate recap_loan_rate]; payment type [residual_receipts | deferred]; term [coterminous with senior, max n years]; lien position [2nd/3rd]
Conditions: new regulatory agreement [years]; rent and income restrictions [AMI mix]; reserve funding; compliance monitoring cadence
Existing agency debt: [ids] to be [extended | resubordinated | consolidated]
Sources and uses summary; senior debt sizing from sizing-lihtc-permanent-debt
Approval path and timeline
```
