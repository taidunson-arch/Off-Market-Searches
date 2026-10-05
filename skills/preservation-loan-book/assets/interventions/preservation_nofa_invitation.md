---
id: preservation_nofa_invitation
routes:
  - nofa_offer
  - ta_sponsor
trigger_events:
  - LIHTC_EXTENDED_USE_END
  - HAP_EXPIRATION
  - QC_ELIGIBILITY
  - PRESERVATION_NOTICE_RECEIVED
  - USDA_515_PREPAY_ELIGIBLE
  - HUD_DIRECT_LOAN_MATURITY
  - SOFT_PROGRAM_END
  - AFFORDABILITY_PERIOD_END
agency_owner: nofa_program_manager
statutory_cite:
  - cite: "ORS ch. 456 / 458 (LIFT, OAHTC, GHAP enabling statutes)"
    verified_live: false
    note: "state product authority; verify sections"
  - cite: "24 CFR part 92 (HOME); 24 CFR part 93 (HTF)"
    verified_live: false
    note: "new affordability periods on re-investment (HOME 92.252(e); HTF 30 years 93.302)"
  - cite: "IRC 42 (4% credits with tax-exempt bonds)"
    verified_live: false
    note: "recapitalization credits"
  - cite: "24 CFR 570 subpart M (Section 108); Metro Measure 26-199; local TIF / PCEF authority"
    verified_live: false
    note: "local gap and acquisition sources; verify"
owner_notice: "invitation letter to the owner or to the mission sponsor to apply to an open product named in mandate.json"
tenant_notice: "none"
timeline: "align the award cohort (OHCS Feb-May; PHB spring RFP) to land 12-24 months before the cliff; bridge with NOAH OHAF when the cliff is inside 12 months"
pii_scope: organization
first_action: "confirm mandate_fit eligible and the product's application_window; send the invitation naming the product, the new regulatory term and the pre-application meeting"
kpi_flip_on_success: recap_closed / preserved
notice_address_rule: "print notice_address and notice_address_source; agency file first (regulatory_agreement > hap_contract > loan_docs), SOS registered agent fallback with Verify — Notice Address; hold the letter when source is unknown"
---

# Intervention: `preservation_nofa_invitation`

> **Confirm current statutory text before sending.** Every cite in this build is `verified_live: false`: statute and regulation text was not read from an official source. Agency counsel reviews the cite, the window and the recipient before any letter leaves. Nothing here treats an owner as a counterparty to a sale; there is no bid and no purchase language unless the agency is exercising a statutory purchase right. PuSH enforcement is never described as a fine or penalty (ORS 456.265 is titled "Sanctions against withdrawing property owner prohibited"; verify).

## Purpose
Award-side outreach: the agency invites an owner or mission sponsor to apply for an open preservation product. The letter names the product, its eligibility, the new regulatory term the award carries, and the cohort timing. It never offers to buy and never implies an award is made.

## Letter skeleton
```
[Agency letterhead]                                                         [date]
[Owner / sponsor organization], [role]; [notice_address] (source [notice_address_source])

Re: [property_name], [address] — [units_at_risk] restricted units with [owner_cliff_type] on [owner_cliff_date]

[Agency]'s [product name] ([product_id]) is [open | opens on date] for applications through [application_window end]. Based on
the property's programs ([programs]) and your organization's type, the property appears eligible [mandate_eligible_products].
An award would carry a new affordability term of [new_covenant_years] years under [regulatory instrument] and may be paired
with [4% LIHTC / OAHTC rate buy-down / 0% rehab recap] and, where timing requires, bridge financing from [external partner].
We would welcome a pre-application meeting; please contact [nofa_program_manager role] at [program email].
[If our_book: Our existing [loan/grant ids] ($[public_upb], [payment_type], maturing [our_maturity]) can be considered for
extension or resubordination as part of the application.]
```

## Record
AM status Letter Sent; kpi recap_closed on award closing; being_preserved_units in Board_Totals once recap_status is under_application with the application on file.
