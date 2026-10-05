---
id: optout_tenant_notice_check
routes:
  - optout_response
trigger_events:
  - HAP_EXPIRATION (HAP / RAC / PBV, <= 12 months, renewal status unknown)
  - HAP_OPTOUT_NOTICE_DEADLINE
  - HAP_OPTOUT_PACKAGE_DUE
  - PRESERVATION_NOTICE_RECEIVED (hap_optout)
agency_owner: pbca_liaison
statutory_cite:
  - cite: "42 U.S.C. 1437f(c)(8)(A)-(B) (MAHRA)"
    verified_live: false
    note: "owner not renewing must give one year's notice to tenants, HUD and the contract administrator; defective notice: tenants stay at the last assisted rent until one year after proper notice"
  - cite: "24 CFR 402.8"
    verified_live: false
    note: "one-year notice content and timing"
  - cite: "HUD Section 8 Renewal Policy Guidebook (March 2023) ch. 11"
    verified_live: false
    note: "opt-out request and certification not less than 120 days before expiration; CA reviews tenant notification letters; deficient letters restart the clock; taping to doors not acceptable — chapter cite from secondary summaries, verify"
owner_notice: "none from the agency to the owner at this step; this is a CA-side check of what the owner has filed"
tenant_notice: "none from the agency; the check verifies the owner's one-year tenant notice"
timeline: "act by HAP_EXPIRATION - 365 days (notice review) and HAP_EXPIRATION - 120 days (package); when HAP_OPTOUT_NOTICE_DEADLINE has already passed with status unknown -> signal optout_notice_deadline_passed_unconfirmed, flag Verify — CA Log"
pii_scope: organization
first_action: "confirm renewal request / opt-out notice at CA (hap_renewal_request_status received | not_received; hap_renewal_option); if an opt-out letter exists, review the tenant letters for sufficiency; set the clock accordingly"
kpi_flip_on_success: hap_renewed (renewal request received) or hap_optout (opt-out confirmed)
notice_address_rule: "print notice_address and notice_address_source; agency file first (regulatory_agreement > hap_contract > loan_docs), SOS registered agent fallback with Verify — Notice Address; hold the letter when source is unknown"
---

# Intervention: `optout_tenant_notice_check`

> **Confirm current statutory text before sending.** Every cite in this build is `verified_live: false`: statute and regulation text was not read from an official source. Agency counsel reviews the cite, the window and the recipient before any letter leaves. Nothing here treats an owner as a counterparty to a sale; there is no bid and no purchase language unless the agency is exercising a statutory purchase right. PuSH enforcement is never described as a fine or penalty (ORS 456.265 is titled "Sanctions against withdrawing property owner prohibited"; verify).

## Purpose
The contract administrator's check of where a Section 8 contract stands inside its last year: renewal request received, opt-out notice received, or nothing yet. Applies to HAP, RAC and PBV; never to PRAC / PAC (prac_renewal_coordination). A deficient tenant notice does not start the owner's clock, and the CA can say so.

## Checklist
```
Property [property_name]; contract [contract_number if known]; program [HAP | RAC | PBV]; expiration [HAP_EXPIRATION date] ([basis], confidence [0.70 | 0.90], detail [annual / mahra])
HAP_OPTOUT_NOTICE_DEADLINE [date] — [passed? -> Verify — CA Log]; HAP_OPTOUT_PACKAGE_DUE [date]
CA record: hap_renewal_request_status [received | not_received | unknown]; hap_renewal_option [1a | 1b | 2 | ... | 6_optout]
If opt-out letter on file: date delivered to tenants / HUD / CA; content review (24 CFR 402.8 elements); languages; delivery method;
   finding [sufficient | deficient -> clock restarts; tenants remain at last assisted rent]
If renewal request on file: option, term, rent comparability status -> signal optout_window_closed_for_term; kpi hap_renewed
If nothing on file inside 120 days: contact owner/agent (optout_response_plan step 1)
Households: [hap_units_at_risk] assisted units; enhanced-voucher planning with the PHA (42 U.S.C. 1437f(t)) if opt-out proceeds
Req-ID rows: HAP-01, HAP-02 in Notice_Compliance
```
