---
id: enforcement_8823
routes:
  - servicing_watch
  - qc_admin
trigger_events:
  - NONCOMPLIANCE_FINDING
  - REAC_SCORE
  - CODE_CASE_OPEN
  - OCCUPANCY_DROP
  - TAX_EXEMPTION_LOST
agency_owner: compliance_officer
statutory_cite:
  - cite: "IRC 42(m)(1)(B)(iii)"
    verified_live: false
    note: "agency monitoring duty"
  - cite: "26 CFR 1.42-5(e)"
    verified_live: false
    note: "notice to owner, correction period (up to 90 days, extendable to 6 months), Form 8823 filed no later than 45 days after the end of the correction period; verify"
  - cite: "IRS Form 8823 instructions; IRS 8823 Audit Guide (Pub. 5913)"
    verified_live: false
    note: "reporting categories"
owner_notice: "notice of noncompliance with the correction period"
tenant_notice: "none"
timeline: "correction period up to 90 days (extendable to 6 months); 8823 within 45 days after the correction period ends"
pii_scope: organization
first_action: "document the finding; send the owner notice of noncompliance with the correction period; calendar the 8823 filing date; record NONCOMPLIANCE_FINDING"
kpi_flip_on_success: covenant_cured (finding closed) or none
notice_address_rule: "print notice_address and notice_address_source; agency file first (regulatory_agreement > hap_contract > loan_docs), SOS registered agent fallback with Verify — Notice Address; hold the letter when source is unknown"
---

# Intervention: `enforcement_8823`

> **Confirm current statutory text before sending.** Every cite in this build is `verified_live: false`: statute and regulation text was not read from an official source. Agency counsel reviews the cite, the window and the recipient before any letter leaves. Nothing here treats an owner as a counterparty to a sale; there is no bid and no purchase language unless the agency is exercising a statutory purchase right. PuSH enforcement is never described as a fine or penalty (ORS 456.265 is titled "Sanctions against withdrawing property owner prohibited"; verify).

## Purpose
The HFA's LIHTC noncompliance instrument. A finding feeds the physical / compliance factor and justifies enforcement routing; it is never a reason to discount the asset.

## Notice skeleton
```
Re: [property_name]; BIN(s) [ ]; noncompliance identified on [date] during [inspection | file review]
Findings: [category per Form 8823 line; units affected]
Correction period ends [date] [verify]; evidence of correction to be delivered to [compliance_officer role]
Form 8823 will be filed with the IRS no later than 45 days after the correction period [verify], reporting the finding and whether it was corrected.
```
