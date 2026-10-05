---
id: tenant_notice_check
routes:
  - notice_compliance
trigger_events:
  - TENANT_NOTICE_WINDOW
  - PRESERVATION_NOTICE_RECEIVED
  - PUSH_SECOND_NOTICE_DUE
agency_owner: compliance_officer
statutory_cite:
  - cite: "SB 973 (2025), amending ORS 456.259 and ORS ch. 90"
    verified_live: false
    note: "tenant notice 30-36 months before restriction expiry in the five most common non-English languages; applicant / new-tenant disclosure before any screening fee or rental agreement; per-tenant affordability extension for non-notice; operative date and the 2028-07-01 phase-in from snippets — verify"
  - cite: "HB 3042 (2023)"
    verified_live: false
    note: "prior 20-24 month tenant notice and 3-year post-withdrawal safe harbor"
owner_notice: "owner-facing request for proof of tenant and applicant notice (copies of notices, posting, language versions, mailing list without names)"
tenant_notice: "none from the agency; the check verifies the owner's duty"
timeline: "check at anchor - 30 months (end of TENANT_NOTICE_WINDOW); repeat at second notice"
pii_scope: organization
first_action: "set tenant_notice_status (confirmed / not_confirmed) from the owner's proof; when not_confirmed inside or after the window, route notice_compliance primary and record the extension position"
kpi_flip_on_success: tenant_notice_confirmed
notice_address_rule: "print notice_address and notice_address_source; agency file first (regulatory_agreement > hap_contract > loan_docs), SOS registered agent fallback with Verify — Notice Address; hold the letter when source is unknown"
---

# Intervention: `tenant_notice_check`

> **Confirm current statutory text before sending.** Every cite in this build is `verified_live: false`: statute and regulation text was not read from an official source. Agency counsel reviews the cite, the window and the recipient before any letter leaves. Nothing here treats an owner as a counterparty to a sale; there is no bid and no purchase language unless the agency is exercising a statutory purchase right. PuSH enforcement is never described as a fine or penalty (ORS 456.265 is titled "Sanctions against withdrawing property owner prohibited"; verify).

## Purpose
Verifies that the owner gave tenants and applicants the statutory notice. The remedy for non-notice under SB 973 is a per-tenant extension of the affordability restriction, so a missing tenant notice is itself preservation leverage: the agency asserts the extension rather than only chasing a sale.

## Checklist
```
Property [property_name] — anchor [withdrawal_anchor_date]; TENANT_NOTICE_WINDOW [start]..[end]
Applies: anchor >= sb973_operative_restriction_date [pack value; verify]  -> if not, tenant_notice_status n/a_pre_operative
Proof requested from owner: copies of tenant notice (all required languages), posting evidence, applicant disclosure form,
  count of households noticed vs occupied units (no names).
Finding: [confirmed | not_confirmed] — units not noticed [n] -> affordability extension position per SB 973 [verify]
Req-ID rows: PUSH-03 (tenant notice), PUSH-04 (applicant disclosure) in Notice_Compliance.
```

## Record
tenant_notice_status on the lead; Notice_Compliance tab rows PUSH-03 / PUSH-04 with window, due date, evidence, finding, remediation ask.
