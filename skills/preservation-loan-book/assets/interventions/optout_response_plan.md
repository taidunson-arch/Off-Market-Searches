---
id: optout_response_plan
routes:
  - optout_response
trigger_events:
  - PRESERVATION_NOTICE_RECEIVED (hap_optout)
  - HAP_EXPIRATION with hap_renewal_request_status not_received
  - REAC_SCORE (< 60 blocks MU2M)
agency_owner: pbca_liaison
statutory_cite:
  - cite: "HUD Section 8 Renewal Policy Guidebook chs. 2-3, 15"
    verified_live: false
    note: "Option 1 Mark-Up-To-Market (1A entitlement when comparable market rent >= FMR; 1B discretionary), 5-20 year terms, REAC >= 60 required; Option 2 OCAF / 20-year MAHRA renewal; nonprofit exception with 20-year recorded use agreement (ch. 15); Option 6 opt-out — from secondary summaries, verify"
  - cite: "42 U.S.C. 1437f(t)"
    verified_live: false
    note: "enhanced vouchers for eligible families on opt-out"
  - cite: "42 U.S.C. 1437f(c)(8); 24 CFR 402.8"
    verified_live: false
    note: "one-year notice; defective notice consequences"
owner_notice: "CA / preservation-office letter to the owner proposing renewal alternatives and, if the owner persists, a transfer with HAP assignment"
tenant_notice: "PHA issues enhanced vouchers to eligible households at termination; the agency coordinates, it does not notice tenants itself"
timeline: "counteroffer inside the one-year notice period; bridge acquisition + 1-3 year HAP extension, then 4% LIHTC and a 20-year renewal (Portland 11x13 / Hawthorne East pattern)"
pii_scope: organization
first_action: "pbca_liaison and nofa_program_manager meet within 10 days of a confirmed opt-out: counteroffer (MU2M / 20-year), identify a mission transferee, line up bridge and gap, open enhanced-voucher planning with the PHA"
kpi_flip_on_success: hap_renewed or recap_closed
notice_address_rule: "print notice_address and notice_address_source; agency file first (regulatory_agreement > hap_contract > loan_docs), SOS registered agent fallback with Verify — Notice Address; hold the letter when source is unknown"
---

# Intervention: `optout_response_plan`

> **Confirm current statutory text before sending.** Every cite in this build is `verified_live: false`: statute and regulation text was not read from an official source. Agency counsel reviews the cite, the window and the recipient before any letter leaves. Nothing here treats an owner as a counterparty to a sale; there is no bid and no purchase language unless the agency is exercising a statutory purchase right. PuSH enforcement is never described as a fine or penalty (ORS 456.265 is titled "Sanctions against withdrawing property owner prohibited"; verify).

## Purpose
The agency's response to a confirmed or likely opt-out: keep the contract on the property through a renewal counteroffer or a transfer to a mission owner that renews for 20 years, and protect the households if neither lands. The agency IS the contract administrator / AE counterpart; it does not represent HUD's decisions, it coordinates them.

## Plan skeleton
```
Property [property_name]; [hap_units_at_risk] assisted units of [units]; expiration [date]; notice status [hap_optout received date | not_received]
Step 1 — Counteroffer (CA): renewal option analysis — comparable market rents vs contract rents (rent_to_fmr_ratio [x]); MU2M eligibility (REAC [score] >= 60?; Option 1A/1B); 20-year Option 2; owner's stated reason.
Step 2 — Transfer path: mission transferee candidates [sponsors]; HAP assignment with HUD approval (2530 / TPA, verify); new regulatory term per mandate ([new_covenant_years]).
Step 3 — Financing sequence: bridge [NOAH OHAF if listed] -> short HAP extension (1-3 yrs) -> 4% LIHTC + gap [lihtc_4pct_gap / phb_preservation_rfp] -> 20-year HAP renewal.
Step 4 — Household protection: enhanced voucher count [hap_units_at_risk]; PHA coordination; tenant letter sufficiency (optout_tenant_notice_check).
Step 5 — Calendar: HAP_OPTOUT_PACKAGE_DUE [date]; decision points; owner meeting [date].
Handoffs: front-door-lihtc-underwriting (composition), sizing-lihtc-permanent-debt, critical-dates-tracker.
```

## Do not
- Suggest opt-out as a tactic or frame it as value; describe HUD positions as the agency's commitments; contact tenants directly (the PHA's voucher process does that).
