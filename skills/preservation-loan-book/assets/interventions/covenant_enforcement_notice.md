---
id: covenant_enforcement_notice
routes:
  - servicing_watch
  - recap_committee
trigger_events:
  - COVENANT_DEFAULT
  - REAC_SCORE (< 60)
  - NONCOMPLIANCE_FINDING
  - TAX_DELINQUENT_YEARS
  - TAX_FORECLOSURE_LIST
  - TAX_EXEMPTION_LOST
  - CODE_CASE_OPEN
  - DANGEROUS_BUILDING
  - ENTITY_ADMIN_DISSOLVED
  - INSPECTION_DUE
agency_owner: am_officer
statutory_cite:
  - cite: "agency loan and regulatory agreement covenants"
    verified_live: false
    note: "default, notice and cure provisions as written in the agency's own documents"
  - cite: "24 CFR 92.504(d)"
    verified_live: false
    note: "HOME on-site inspection cadence 3/2/1 years by project size; annual rent / income / occupancy review"
  - cite: "26 CFR 1.42-5"
    verified_live: false
    note: "LIHTC monitoring: inspection at least every 3 years, 20% of low-income units"
  - cite: "HUD NSPIRE scoring notice (July 2023); HUD 'Administrative Procedures for Multifamily Properties Scoring Below 60'"
    verified_live: false
    note: "fail below 60; <= 30 automatic DEC referral (pre-NSPIRE procedure; verify)"
owner_notice: "owner default / cure notice per the loan documents, or an inspection / compliance notice"
tenant_notice: "none"
timeline: "per the cure period in the documents (typically 30-90 days); inspection per INSPECTION_DUE"
pii_scope: organization
first_action: "pull the covenant and cure provisions from our file; confirm the trigger evidence; send the notice; calendar the cure deadline; escalate to recap_committee if REAC < 60, DSCR breach or senior cliff within 24 months"
kpi_flip_on_success: covenant_cured
notice_address_rule: "print notice_address and notice_address_source; agency file first (regulatory_agreement > hap_contract > loan_docs), SOS registered agent fallback with Verify — Notice Address; hold the letter when source is unknown"
---

# Intervention: `covenant_enforcement_notice`

> **Confirm current statutory text before sending.** Every cite in this build is `verified_live: false`: statute and regulation text was not read from an official source. Agency counsel reviews the cite, the window and the recipient before any letter leaves. Nothing here treats an owner as a counterparty to a sale; there is no bid and no purchase language unless the agency is exercising a statutory purchase right. PuSH enforcement is never described as a fine or penalty (ORS 456.265 is titled "Sanctions against withdrawing property owner prohibited"; verify).

## Purpose
The asset manager's covenant notice on an agency-held loan or regulatory agreement: a default or watch condition, a failed inspection, an open finding, unpaid taxes or a lost exemption. Troubled-asset management, not a bid discount.

## Notice skeleton
```
[Agency letterhead]                                                         [date]
[Owner entity], [role]; [notice_address] (source [notice_address_source])
Re: [property_name] — Loan / Regulatory Agreement [ids]; notice under Section [ ]

[Agency]'s records show: [COVENANT_DEFAULT since date | REAC/NSPIRE score n on date | n open findings / 8823 filed date |
property taxes delinquent n years | exemption removed | code case n | entity administratively dissolved].
Under Section [ ] of the [note / regulatory agreement] this constitutes [a default | a covenant breach | a reporting failure].
Please cure by [cure deadline] by [specific action], or contact [am_officer role] to propose a corrective action plan.
Nothing in this letter waives any right or remedy of [agency].
```

## Record
AM status Letter Sent; cure deadline on the calendar; covenant_status -> cured on evidence (kpi covenant_cured); escalation to loan_extension_recast_memo if the plan requires a workout.
