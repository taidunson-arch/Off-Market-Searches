---
id: qc_waiver_acknowledgement
routes:
  - qc_admin
trigger_events:
  - QC_REQUEST_INELIGIBLE (qc_waived true)
agency_owner: compliance_officer
statutory_cite:
  - cite: "IRC 42(h)(6)(E)(i)(II)"
    verified_live: false
    note: "QC request right exists only where not waived in the extended use agreement"
  - cite: "Oregon QAP (2016 and later; first waiver year unconfirmed)"
    verified_live: false
    note: "allocations conditioned on a QC waiver; OHCS REUAs; verify"
owner_notice: "letter to the owner: the recorded REUA / Declaration waives the qualified-contract option; no one-year period begins"
tenant_notice: "none"
timeline: "within 10 business days of the request; no clock"
pii_scope: organization
first_action: "read the recorded REUA waiver clause (from our own file); counsel confirms; send the acknowledgement; close the QC file; keep the property in the preservation queue on its other events"
kpi_flip_on_success: none
notice_address_rule: "print notice_address and notice_address_source; agency file first (regulatory_agreement > hap_contract > loan_docs), SOS registered agent fallback with Verify — Notice Address; hold the letter when source is unknown"
---

# Intervention: `qc_waiver_acknowledgement`

> **Confirm current statutory text before sending.** Every cite in this build is `verified_live: false`: statute and regulation text was not read from an official source. Agency counsel reviews the cite, the window and the recipient before any letter leaves. Nothing here treats an owner as a counterparty to a sale; there is no bid and no purchase language unless the agency is exercising a statutory purchase right. PuSH enforcement is never described as a fine or penalty (ORS 456.265 is titled "Sanctions against withdrawing property owner prohibited"; verify).

## Purpose
Tells an owner whose extended use agreement waived the qualified-contract option that no QC period begins. The waiver is read from the agency's own recorded REUA, never inferred from allocation vintage alone.

## Letter skeleton
```
Re: Qualified contract request — [property_name]; REUA recorded [date, instrument]
Section [ ] of the Reservation and Extended Use Agreement waives the owner's right to request a qualified contract under
IRC 42(h)(6)(E)(i)(II) [verify]. [HFA] therefore does not treat the [date] request as commencing a one-year period and the
extended use period continues through [LIHTC_EXTENDED_USE_END]. [HFA] remains available to discuss recapitalization options
[mandate_eligible_products] and the Oregon preservation notice requirements that apply as the restriction approaches its end.
```
