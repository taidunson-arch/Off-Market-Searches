---
id: qc_coordination_with_hfa
routes:
  - nofa_offer
  - ta_sponsor
trigger_events:
  - QC_ELIGIBILITY (any status) seen by a non-HFA profile
agency_owner: nofa_program_manager
statutory_cite:
  - cite: "IRC 42(h)(6)(E)-(I)"
    verified_live: false
    note: "the housing credit agency administers the qualified contract; a city, county or PHA does not"
owner_notice: "none; coordination letter to the HFA QC administrator"
tenant_notice: "none"
timeline: "on first sight of a QC signal"
pii_scope: organization
first_action: "notify the HFA QC administrator; offer a gap award or a mission sponsor for the HFA's presentment; never open a notice_compliance case on a QC signal"
kpi_flip_on_success: qc_presented (HFA)
notice_address_rule: "print notice_address and notice_address_source; agency file first (regulatory_agreement > hap_contract > loan_docs), SOS registered agent fallback with Verify — Notice Address; hold the letter when source is unknown"
---

# Intervention: `qc_coordination_with_hfa`

> **Confirm current statutory text before sending.** Every cite in this build is `verified_live: false`: statute and regulation text was not read from an official source. Agency counsel reviews the cite, the window and the recipient before any letter leaves. Nothing here treats an owner as a counterparty to a sale; there is no bid and no purchase language unless the agency is exercising a statutory purchase right. PuSH enforcement is never described as a fine or penalty (ORS 456.265 is titled "Sanctions against withdrawing property owner prohibited"; verify).

## Purpose
For city_housing, county, pha_am and cdbg_home profiles a qualified-contract signal is not the agency's clock; it is the HFA's. The local agency's contribution is money or a sponsor for the contract the HFA must present.

## Memo skeleton
```
To: [HFA compliance / QC administrator]
Property [property_name]; QC status [requested | eligible | lapsed] per [source]; QC_RESPONSE_DUE [date if known]
Local offer: gap award [product_id] up to [max_per_unit x units]; mission sponsor [organization] prepared to contract
Our position: [our_book: ids, upb, maturity; resubordination available] | not in book
```
