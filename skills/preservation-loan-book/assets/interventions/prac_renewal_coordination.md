---
id: prac_renewal_coordination
routes:
  - servicing_watch
  - optout_response (never primary for PRAC)
trigger_events:
  - HAP_EXPIRATION (program PRAC / PAC)
agency_owner: hud_mf_asset_manager
statutory_cite:
  - cite: "Notice H 2022-05"
    verified_live: false
    note: "Section 202 and 811 PRAC renewals moved to five-year terms with budget-based or OCAF adjustments; verify"
  - cite: "Notice H 2002-17 (superseded)"
    verified_live: false
    note: "prior annual PRAC renewals"
owner_notice: "none required; sponsor coordination letter optional"
tenant_notice: "none"
timeline: "start 12 months before PRAC expiration; renewal depends on appropriations, not owner intent"
pii_scope: organization
first_action: "confirm the renewal term and funding status with the HUD asset manager; assess sponsor capacity (nonprofit / PHA) and physical condition; never route optout_response"
kpi_flip_on_success: hap_renewed
notice_address_rule: "print notice_address and notice_address_source; agency file first (regulatory_agreement > hap_contract > loan_docs), SOS registered agent fallback with Verify — Notice Address; hold the letter when source is unknown"
---

# Intervention: `prac_renewal_coordination`

> **Confirm current statutory text before sending.** Every cite in this build is `verified_live: false`: statute and regulation text was not read from an official source. Agency counsel reviews the cite, the window and the recipient before any letter leaves. Nothing here treats an owner as a counterparty to a sale; there is no bid and no purchase language unless the agency is exercising a statutory purchase right. PuSH enforcement is never described as a fine or penalty (ORS 456.265 is titled "Sanctions against withdrawing property owner prohibited"; verify).

## Purpose
PRAC / PAC contracts (202 / 811 elderly and disabled housing) renew on appropriations and sponsor capacity; the owner cannot opt out the way a Section 8 owner can. The risk the agency manages is a struggling nonprofit sponsor or a building that needs a recap, not a departure.

## Checklist
```
Property [property_name]; program [PRAC | PAC]; expiration [date] (confidence 0.70); sponsor [owner_name] ([owner_type]); elderly/disabled flags [vulnerability_flags]
HUD asset manager contact: renewal term [5-year per H 2022-05, verify]; funding status; rent adjustment method
Sponsor: capacity signals (SOS status, open findings, REAC [score]); TA need (ta_sponsor_engagement)
Recap need: 202 prepayment / refinance with 20-year use agreement (hud_legacy_response) if debt or condition warrants
Units: [prac_units_at_risk] assisted
```
