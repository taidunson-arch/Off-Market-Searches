---
id: hud_legacy_response
routes:
  - recap_committee
trigger_events:
  - HUD_DIRECT_LOAN_MATURITY
  - PREPAY_WINDOW_OPEN
  - HAP_EXPIRATION (PRAC)
agency_owner: hud_mf_asset_manager
statutory_cite:
  - cite: "Notice H 2013-17; AHEO Act 2000 sec. 811; 24 CFR 891.530"
    verified_live: false
    note: "Section 202 direct-loan prepayment requires a 20-year use-agreement extension; TPVs for unassisted residents of pre-1974 projects; verify"
  - cite: "Notice H 2013-25; NHA 236(e)(2)"
    verified_live: false
    note: "IRP decoupling: IRP continues after the 236 mortgage is paid off, attached to new debt, with a use agreement"
  - cite: "NHA Section 250 (12 U.S.C. 1715z-15); Notice H 04-17"
    verified_live: false
    note: "236 / 221(d)(3) BMIR prepayment notice 150-270 days ahead with tenant notice; from summaries, verify"
owner_notice: "HUD requires owner tenant notice for 236 / BMIR prepayment and 202 prepayment / refinance; the agency's letter is a recap invitation to the sponsor"
tenant_notice: "HUD-required tenant notice (owner's duty); TPVs for pre-1974 202 residents"
timeline: "HUD prepayment review 90-180 days; Section 250 notice 150-270 days before prepayment; use agreement extended 20 years at closing"
pii_scope: organization
first_action: "meet the HUD multifamily asset manager and the sponsor; frame the recap (4% bond + gap with IRP decoupling or a 202 prepayment and 20-year use agreement); hand to front-door-lihtc-underwriting"
kpi_flip_on_success: recap_closed / preserved
notice_address_rule: "print notice_address and notice_address_source; agency file first (regulatory_agreement > hap_contract > loan_docs), SOS registered agent fallback with Verify — Notice Address; hold the letter when source is unknown"
---

# Intervention: `hud_legacy_response`

> **Confirm current statutory text before sending.** Every cite in this build is `verified_live: false`: statute and regulation text was not read from an official source. Agency counsel reviews the cite, the window and the recipient before any letter leaves. Nothing here treats an owner as a counterparty to a sale; there is no bid and no purchase language unless the agency is exercising a statutory purchase right. PuSH enforcement is never described as a fine or penalty (ORS 456.265 is titled "Sanctions against withdrawing property owner prohibited"; verify).

## Purpose
Aging 236, 221(d)(3) BMIR and 202 stock is a preservation opportunity when a mission sponsor is in place: a maturity ends the use agreement, but decoupling or a prepayment with a 20-year use agreement extends it. The agency's lever is the gap award and co-approval with HUD, not a bid.

## Memo skeleton
```
Property [property_name]; SOA [236 | 221(d)(3) | 202]; HUD_DIRECT_LOAN_MATURITY [date] ([basis]); PREPAY_WINDOW_OPEN [date]; HAP overlay [yes | no_hap_overlay]
Sponsor [owner_name] ([owner_type]); HUD asset manager [role]
Path: [IRP decoupling (H 2013-25) | 202 prepayment with 20-year use agreement (H 2013-17) | refinance with new use agreement]
Notices: Section 250 window [prepay date - 270 .. - 150 days, verify]; tenant notice (owner); TPV planning (pre-1974 202)
Agency products: [lihtc_4pct_gap, zero_pct_rehab_recap, ...]; our position if in book: [upb, maturity, payment_type] -> resubordinate / extend
Units: [units_at_risk] restricted / [hap_units_at_risk] assisted
Handoffs: front-door-lihtc-underwriting (composition, agency_soft_debt), sizing-lihtc-permanent-debt
```
