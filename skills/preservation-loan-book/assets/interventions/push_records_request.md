---
id: push_records_request
routes:
  - notice_compliance
  - designee_rofr
trigger_events:
  - PRESERVATION_NOTICE_RECEIVED (push_first / push_second)
  - RECORDS_REQUEST_DUE
agency_owner: push_program_manager
statutory_cite:
  - cite: "OAR 813-115-0050 (Qualified Purchaser Access to Property, Records and Documents; implements ORS 456.262(6)-(7))"
    verified_live: false
    note: "covers the OHCS / HUD / RD compliance reports and the current approved rent schedule with actual rents; the 30-day response period was NOT found in any snippet — working target, read ORS 456.262(6)-(7). OAR 813-115-0060 is ROFR recording, not records"
  - cite: "ORS 456.262"
    verified_live: false
    note: "qualified purchaser status"
owner_notice: "owner-facing written request to notice_address; sent only after the owner's notice is on file"
tenant_notice: "none"
timeline: "send within 10 days of PRESERVATION_NOTICE_RECEIVED (RECORDS_REQUEST_DUE, internal target); owner response tracked at 30 days after the request (RECORDS_RESPONSE_DUE; period unverified)"
pii_scope: organization
first_action: "confirm PRESERVATION_NOTICE_RECEIVED is RECORDED with a date; send the request; calendar RECORDS_RESPONSE_DUE"
kpi_flip_on_success: none (upgrades basis of financial data from PROXY/ESTIMATED to REPORTED)
notice_address_rule: "print notice_address and notice_address_source; agency file first (regulatory_agreement > hap_contract > loan_docs), SOS registered agent fallback with Verify — Notice Address; hold the letter when source is unknown"
---

# Intervention: `push_records_request`

> **Confirm current statutory text before sending.** Every cite in this build is `verified_live: false`: statute and regulation text was not read from an official source. Agency counsel reviews the cite, the window and the recipient before any letter leaves. Nothing here treats an owner as a counterparty to a sale; there is no bid and no purchase language unless the agency is exercising a statutory purchase right. PuSH enforcement is never described as a fine or penalty (ORS 456.265 is titled "Sanctions against withdrawing property owner prohibited"; verify).

## Purpose
The qualified purchaser's statutory records request, which follows the owner's notice and never precedes it. It converts guesses into reported figures: rent roll, operating statements, contract rents, unit mix, debt schedule.

## Request skeleton
```
[Agency letterhead]                                                         [date]
[Owner entity], [role]
[notice_address]  (source: [notice_address_source])

Re: [property_name], [address] — request for property records under OAR 813-115-0050 and ORS 456.262(6)-(7) [verify]

[Agency] received your notice of intent dated [notice_received_date] ([detail]). As a qualified purchaser under
ORS 456.250 [verify], we request the following records (compliance reports and the approved rent schedule with actual rents are
named in the rule; the response period is [30 days — working target, verify ORS 456.262(6)-(7)]):
  1. Current rent roll with unit type, contract/restricted rent, utility allowance and assistance type per unit
  2. Operating statements for the last three fiscal years and the current year to date
  3. Current HAP/PRAC/RA contract(s), renewal requests and any opt-out correspondence
  4. Regulatory agreements, LURA/REUA and recorded covenants with amendments
  5. Debt schedule: lender, balance, rate, maturity, prepayment terms, reserves
  6. Most recent physical inspection (REAC/NSPIRE) and capital needs assessment
  7. Partnership agreement provisions on Year-15 exit, ROFR and qualified contract (or a summary)
Records may be delivered electronically to [program email]. [Agency] treats tenant-level information as confidential
and asks that unit-level records be provided without household names.
```

## Record
On response: upgrade est_restricted_noi (noi_source agency_file -> REPORTED), senior debt (REPORTED), HAP term; attach to the critical-dates-tracker handoff. On non-response at RECORDS_RESPONSE_DUE: escalate to legal_counsel; AM status Awaiting Response.
