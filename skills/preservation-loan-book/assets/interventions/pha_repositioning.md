---
id: pha_repositioning
routes:
  - recap_committee
  - servicing_watch
trigger_events:
  - RAD_CHAP
  - SECTION_18_APPLICATION
  - REAC_SCORE
  - AGENCY_LOAN_MATURITY (owned asset)
  - HAP_EXPIRATION (owned asset / PBV)
  - AFFORDABILITY_PERIOD_END (owned asset)
agency_owner: pha_development
statutory_cite:
  - cite: "RAD Notice H-2019-09 / PIH-2019-23 REV-4"
    verified_live: false
    note: "public housing conversion to PBV (24 CFR 983) or PBRA (24 CFR 880); RAD / Section 18 blends; application deadline extended to 9/30/2029; verify"
  - cite: "Section 18 of the 1937 Act; 24 CFR part 970"
    verified_live: false
    note: "demolition / disposition through HUD SAC; 970.9 resident consultation; tenant protection vouchers"
  - cite: "PIH 2024-40; PIH 2026-23"
    verified_live: false
    note: "RAD-18 blend percentages by construction cost; verify"
owner_notice: "n/a (the PHA is the owner); HUD SAC / Office of Recapitalization submissions"
tenant_notice: "resident consultation (970.9) and RAD relocation notices; TPVs for removed units"
timeline: "RAD CHAP to closing 12-24 months; Section 18 SAC review 60-120 days"
pii_scope: organization
first_action: "pha_development confirms the repositioning path for the asset; HFA profile offers 4% bond + gap for the recap; record RAD_CHAP / SECTION_18_APPLICATION dates"
kpi_flip_on_success: recap_closed / preserved (new HAP / PBV events follow)
notice_address_rule: "print notice_address and notice_address_source; agency file first (regulatory_agreement > hap_contract > loan_docs), SOS registered agent fallback with Verify — Notice Address; hold the letter when source is unknown"
---

# Intervention: `pha_repositioning`

> **Confirm current statutory text before sending.** Every cite in this build is `verified_live: false`: statute and regulation text was not read from an official source. Agency counsel reviews the cite, the window and the recipient before any letter leaves. Nothing here treats an owner as a counterparty to a sale; there is no bid and no purchase language unless the agency is exercising a statutory purchase right. PuSH enforcement is never described as a fine or penalty (ORS 456.265 is titled "Sanctions against withdrawing property owner prohibited"; verify).

## Purpose
For the pha_am profile's own assets (self_owned): RAD conversion, Section 18 disposition or a blend, with the HFA as the 4% bond and gap partner. Sponsor capacity is the PHA's own; the levers are repositioning and recapitalization, never notice_compliance or designee_rofr on itself.

## Memo skeleton
```
Asset [asset_id] [property_name]; [units] units; current program [public housing | PBV | PBRA]; REAC [score]; cliff [owner_cliff_type date]
Path: [RAD PBV | RAD PBRA | Section 18 | RAD-18 blend at n% per PIH 2026-23 (verify)]
Milestones: CHAP [rad_chap_date] / SAC application [section_18_application_date]; resident consultation [dates]; TPV count; relocation plan
Financing: 4% bonds + gap [HFA products]; PHA capital funds; new HAP / PBV contract term
Board approval [date]; HUD approvals [dates]
Board_Totals (owned_assets variant): owned_units [n], pbv_households [n], rad_section18_status [status]
```
