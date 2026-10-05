---
id: rofr_assignment_memo
routes:
  - designee_rofr
  - ta_sponsor
trigger_events:
  - ROFR_RECORDED
  - THIRD_PARTY_OFFER_RECEIVED
  - PRESERVATION_NOTICE_RECEIVED
agency_owner: legal_counsel
statutory_cite:
  - cite: "ORS 456.262"
    verified_live: false
    note: "ROFR assignable to a qualified purchaser; OHCS designee appointment by written agreement; from snippets"
  - cite: "ORS 456.250"
    verified_live: false
    note: "qualified purchaser definition (OHCS, affected local government, OHCS designee)"
owner_notice: "owner notified of the assignment / designee appointment"
tenant_notice: "none"
timeline: "before the match deadline when a mission sponsor rather than the agency will take title"
pii_scope: organization
first_action: "identify the mission sponsor (nonprofit, PHA); confirm its capacity (ta_sponsor_engagement); execute the designee / assignment agreement; notify the owner"
kpi_flip_on_success: recap_closed
notice_address_rule: "print notice_address and notice_address_source; agency file first (regulatory_agreement > hap_contract > loan_docs), SOS registered agent fallback with Verify — Notice Address; hold the letter when source is unknown"
---

# Intervention: `rofr_assignment_memo`

> **Confirm current statutory text before sending.** Every cite in this build is `verified_live: false`: statute and regulation text was not read from an official source. Agency counsel reviews the cite, the window and the recipient before any letter leaves. Nothing here treats an owner as a counterparty to a sale; there is no bid and no purchase language unless the agency is exercising a statutory purchase right. PuSH enforcement is never described as a fine or penalty (ORS 456.265 is titled "Sanctions against withdrawing property owner prohibited"; verify).

## Purpose
Hands the agency's recorded right to a mission sponsor that will own and operate the property, with the agency's gap award behind it. The agency keeps the statutory position; the sponsor does the transaction.

## Memo skeleton
```
Property [property_name]; ROFR holder [agency]; proposed assignee / designee [sponsor organization] (owner_type [nonprofit | housing_authority]; SOS [status])
Capacity evidence: [sponsor-credibility-assessor Dimension 3 if run; portfolio Year-15/30 load; compliance history]
Funding plan: [product_id list]; new regulatory term [years] per mandate.json new_covenant_years
Designee agreement / assignment: parties, effective date, consultation with affected local government [date]
Owner notice: to [notice_address] (source [notice_address_source])
Match deadline (if an offer is pending): [ROFR_MATCH_DEADLINE]
```
