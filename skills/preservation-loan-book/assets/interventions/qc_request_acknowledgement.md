---
id: qc_request_acknowledgement
routes:
  - qc_admin
trigger_events:
  - QC_ELIGIBILITY (status requested, RECORDED)
  - QC_RESPONSE_DUE
agency_owner: compliance_officer
statutory_cite:
  - cite: "IRC 42(h)(6)(E)(i)(II)"
    verified_live: false
    note: "extended use period terminates when the agency fails to present a qualified contract within the one-year period after the owner's request (the termination trigger)"
  - cite: "IRC 42(h)(6)(I)"
    verified_live: false
    note: "the one-year period for the agency to find a buyer (the clock)"
  - cite: "IRC 42(h)(6)(F); Treas. Reg. 1.42-18"
    verified_live: false
    note: "qualified contract price formula (outstanding indebtedness + adjusted investor equity + other capital contributions - cash distributed; plus FMV of market units); COLA details not read — verify"
  - cite: "IRC 42(h)(6)(E)(ii)"
    verified_live: false
    note: "three-year tenant protection after termination: no eviction without good cause, no non-§42 rent increase"
  - cite: "OHCS Draft Qualified Contract Procedure"
    verified_live: false
    note: "the Department's only obligation is to present a bona fide contract; presentment alone removes the exit; draft, verify"
owner_notice: "acknowledgement letter to the owner: request received, completeness determination, QC_RESPONSE_DUE date, price certification requested"
tenant_notice: "tenant notice of QC status and of the 3-year protection if extended use ends (agency practice; MSHDA-style letters) — verify agency policy"
timeline: "QC_RESPONSE_DUE = qc_request_complete_date + 1 year; acknowledge within 10 business days of a complete request"
pii_scope: organization
first_action: "determine completeness (qc_request_complete_date); confirm qc_waived from the recorded REUA (true -> qc_waiver_acknowledgement instead); acknowledge in writing; start qc_marketing_plan"
kpi_flip_on_success: qc_requested
notice_address_rule: "print notice_address and notice_address_source; agency file first (regulatory_agreement > hap_contract > loan_docs), SOS registered agent fallback with Verify — Notice Address; hold the letter when source is unknown"
---

# Intervention: `qc_request_acknowledgement`

> **Confirm current statutory text before sending.** Every cite in this build is `verified_live: false`: statute and regulation text was not read from an official source. Agency counsel reviews the cite, the window and the recipient before any letter leaves. Nothing here treats an owner as a counterparty to a sale; there is no bid and no purchase language unless the agency is exercising a statutory purchase right. PuSH enforcement is never described as a fine or penalty (ORS 456.265 is titled "Sanctions against withdrawing property owner prohibited"; verify).

## Purpose
The HFA's formal acknowledgement of a qualified-contract request. It fixes the one-year clock, requests the owner's price certification, and tells the owner the agency intends to present a bona fide contract.

## Letter skeleton
```
[HFA letterhead]                                                            [date]
[Owner entity], [role]; [notice_address] (source [notice_address_source])

Re: Qualified contract request — [property_name], [address]; BIN(s) [ ]; allocation year [ ]

[HFA] received your request for a qualified contract on [qc_request_date] and determined it complete on [qc_request_complete_date].
The one-year period under IRC 42(h)(6)(I) [verify] ends [QC_RESPONSE_DUE]. [HFA] intends to present a bona fide contract to
purchase the low-income portion of the building(s) at the qualified contract price determined under IRC 42(h)(6)(F) [verify].
Please provide within 30 days: (1) the qualified contract price worksheet and certification with supporting schedules of
indebtedness, investor equity, other capital contributions and distributions; (2) the records listed in the attached request
(rent roll without household names, operating statements, debt schedule, partnership exit provisions).
If the extended use period were to terminate, existing low-income tenants retain the protections of IRC 42(h)(6)(E)(ii) for
three years [verify]; [HFA] will notify residents of the status of this request in accordance with its policy.
```

## Record
QC_ELIGIBILITY status requested (RECORDED); QC_RESPONSE_DUE calendar row; AM status Letter Sent; qc_marketing_plan opened.
