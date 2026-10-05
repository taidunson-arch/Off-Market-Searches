---
id: ta_sponsor_engagement
routes:
  - ta_sponsor
trigger_events:
  - LIHTC_COMPLIANCE_END
  - LIHTC_EXTENDED_USE_END
  - ROFR_RECORDED
  - MANAGER_CHANGE
  - ENTITY_ADMIN_DISSOLVED
  - QC_ELIGIBILITY (non-HFA profile)
agency_owner: nofa_program_manager
statutory_cite:
  - cite: "IRC 42(i)(7)(A)-(B)"
    verified_live: false
    note: "qualified nonprofit / government ROFR after the compliance period at minimum price = outstanding debt (excluding debt incurred in the prior five years) + exit taxes; SunAmerica Housing Fund 1050 v. Pathway of Pontiac (6th Cir. 2022) on third-party-offer triggers; verify"
  - cite: "SB 51 (2025)"
    verified_live: false
    note: "statewide preservation program; Housing Development Center TA funding; verify"
  - cite: "QAP aggregator / ROFR certifications (e.g., NHHFA Exhibit 20)"
    verified_live: false
    note: "investor and aggregator certification at Year 15 — model only"
owner_notice: "none to a third-party owner; engagement letter to the mission sponsor"
tenant_notice: "none"
timeline: "begin at Year 13-14 for nonprofit / PHA GP deals; fund the exit-tax / debt payoff via 0% recap at Year 15-16"
pii_scope: organization
first_action: "offer TA (agency staff or HDC / equivalent) on the Year-15 exit, the 42(i)(7) ROFR exercise, aggregator correspondence and the recap application; pair with zero_pct_recap_term_sheet"
kpi_flip_on_success: recap_closed / preserved
notice_address_rule: "print notice_address and notice_address_source; agency file first (regulatory_agreement > hap_contract > loan_docs), SOS registered agent fallback with Verify — Notice Address; hold the letter when source is unknown"
---

# Intervention: `ta_sponsor_engagement`

> **Confirm current statutory text before sending.** Every cite in this build is `verified_live: false`: statute and regulation text was not read from an official source. Agency counsel reviews the cite, the window and the recipient before any letter leaves. Nothing here treats an owner as a counterparty to a sale; there is no bid and no purchase language unless the agency is exercising a statutory purchase right. PuSH enforcement is never described as a fine or penalty (ORS 456.265 is titled "Sanctions against withdrawing property owner prohibited"; verify).

## Purpose
Capacity support to a nonprofit or PHA sponsor that holds (or should hold) the preservation position: exercising the 42(i)(7) ROFR, responding to an aggregator LP, assembling a recap application, or taking an assigned ROFR. Mission sponsors are high-priority partners; this is where that reads.

## Engagement letter skeleton
```
[Agency letterhead]                                                         [date]
[Sponsor organization], [executive director / development director role]; [notice_address]

Re: [property_name] — Year 15 [LIHTC_COMPLIANCE_END date] / extended use [LIHTC_EXTENDED_USE_END date]

[Agency] has identified [property_name] among properties whose compliance or extended-use period ends inside our planning horizon.
We can offer technical assistance on: (1) the partnership's Year-15 exit provisions and your right of first refusal under
IRC 42(i)(7) [verify], including review of the partnership agreement (we can arrange counsel review of the exit / ROFR provisions);
(2) correspondence with the limited partner or any transferee; (3) a recapitalization application to [mandate_eligible_products],
including a 0% recap loan to fund the ROFR price and exit taxes; (4) [SB 51 preservation program / HDC TA, verify].
[If our_book: Our existing [ids] ($[public_upb]) can be extended or resubordinated as part of the recapitalization.]
```

## Record
AM status Assigned / TA Engaged; handoffs lihtc-lpa-reviewer (review_focus 2C) when the LPA is in our file; sponsor-credibility-assessor only when the sponsor applies (recap_status announced / under_application).
