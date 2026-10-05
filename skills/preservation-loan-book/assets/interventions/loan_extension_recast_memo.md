---
id: loan_extension_recast_memo
routes:
  - recap_committee
trigger_events:
  - AGENCY_LOAN_MATURITY
  - SHARED_APPRECIATION_DUE
  - LOAN_MATURITY (senior) with coterminous_senior_cliff
  - COVENANT_DEFAULT
  - HUD_DIRECT_LOAN_MATURITY
  - RECEIVER_APPOINTED
  - BANKRUPTCY_FILED
agency_owner: am_officer
statutory_cite:
  - cite: "agency loan documents and lending authority"
    verified_live: false
    note: "residual-receipts / cash-flow / deferred / shared-appreciation note terms; extension, resubordination, forgiveness approval path"
  - cite: "NHA Section 250; Notice H 2013-25"
    verified_live: false
    note: "236 / BMIR prepayment notice 150-270 days; IRP decoupling where the senior is a 236 loan"
  - cite: "24 CFR 92.252(e)(3)-(4) (paragraph numbering verify)"
    verified_live: false
    note: "HOME affordability restriction may terminate on foreclosure; PJ purchase / revival options"
owner_notice: "owner application for extension / recast; agency default and cure notices per loan documents when applicable"
tenant_notice: "none for an agency-only recast; HUD-required tenant notice if a 236 / BMIR prepayment is involved"
timeline: "start at maturity - 18 months; committee cycle 60-120 days; Section 250 notice window when applicable"
pii_scope: organization
first_action: "pull our note, trust deed and regulatory agreement; compute the recap gap (recap_math.recap_gap, ESTIMATED, our_book only); hand before/after recast scenarios to sizing-lihtc-permanent-debt; draft the committee memo"
kpi_flip_on_success: loan_extended / loan_recast / covenant_cured
notice_address_rule: "print notice_address and notice_address_source; agency file first (regulatory_agreement > hap_contract > loan_docs), SOS registered agent fallback with Verify — Notice Address; hold the letter when source is unknown"
---

# Intervention: `loan_extension_recast_memo`

> **Confirm current statutory text before sending.** Every cite in this build is `verified_live: false`: statute and regulation text was not read from an official source. Agency counsel reviews the cite, the window and the recipient before any letter leaves. Nothing here treats an owner as a counterparty to a sale; there is no bid and no purchase language unless the agency is exercising a statutory purchase right. PuSH enforcement is never described as a fine or penalty (ORS 456.265 is titled "Sanctions against withdrawing property owner prohibited"; verify).

## Purpose
The committee memo for extending, recasting, resubordinating or restructuring the agency's own note, or for a workout when the asset is troubled. It is about the agency's capital and covenant, written for the agency's loan committee / council / board; the owner is the borrower.

## Memo skeleton
```
Property [property_name], [address]; sponsor [owner_name] ([owner_type]); am_officer [name/role]
Our position: [agency_loan_ids] $[public_upb] [payment_type] at [our_rate]; maturity [our_maturity] ([basis]); affordability_end [date]; covenant_status [status]; recapture [type/method/exposure]
Senior: [senior_lien_type] $[senior_upb] maturing [senior_maturity] ([basis]); coterminous_senior_cliff [yes/no]; HAP / PRAC [expiration, renewal status]
Trigger: [AGENCY_LOAN_MATURITY in n months | COVENANT_DEFAULT since date | REAC score | receiver / bankruptcy (counsel_only)]
Restricted NOI: $[est_restricted_noi] ([noi_source]); supportable senior at DSCR [1.15] / rate [x]: $[ ] ; uses $[ ] ; gap $[recap_gap_estimate] (ESTIMATED, +/-15%)
Options: (a) extend coterminous with the new senior; (b) recast hard-pay to residual receipts / 0%; (c) resubordinate behind a new first; (d) forgive / write down per authority; (e) workout: cure, payoff, PJ purchase at foreclosure (HOME 92.252, verify)
Covenant: extend the affordability term to [years] as a condition
Units protected: [units_at_risk] restricted / [hap_units_at_risk] assisted / [psh_units_at_risk] PSH
Handoffs: sizing-lihtc-permanent-debt (before/after), front-door-lihtc-underwriting (composition, agency_soft_debt)
Recommendation and approval path: [committee / council / board]; decision date [ ]
```
