---
id: board_packet_summary
routes:
  - all
trigger_events:
  - REGULATORY_LATEST_END
  - HAP_EXPIRATION
  - LIHTC_EXTENDED_USE_END
  - SOFT_PROGRAM_END
  - AGENCY_LOAN_MATURITY
  - AFFORDABILITY_PERIOD_END
  - STABILIZATION_AWARD
  - PRESERVATION_NOTICE_RECEIVED
agency_owner: board_liaison
statutory_cite:
  - cite: "SB 32 (2025)"
    verified_live: false
    note: "OHCS must publish expiration dates, unit counts, assistance type and source, income eligibility levels and preservation status for publicly supported housing; the packet mirrors those fields; verify"
  - cite: "ORS 192.355(2); ORS 192.345"
    verified_live: false
    note: "personal-information exemption and conditional exemptions for packet redaction; verify"
owner_notice: "none"
tenant_notice: "none"
timeline: "quarterly or per board cycle; diff vs prior_run"
pii_scope: public_packet
first_action: "run build_board_workbook.py --board-packet; review the Redaction_Log; brief the book verdict and the headline line; append status flips since the last packet"
kpi_flip_on_success: none (reports every KPI flip)
notice_address_rule: "print notice_address and notice_address_source; agency file first (regulatory_agreement > hap_contract > loan_docs), SOS registered agent fallback with Verify — Notice Address; hold the letter when source is unknown"
---

# Intervention: `board_packet_summary`

> **Confirm current statutory text before sending.** Every cite in this build is `verified_live: false`: statute and regulation text was not read from an official source. Agency counsel reviews the cite, the window and the recipient before any letter leaves. Nothing here treats an owner as a counterparty to a sale; there is no bid and no purchase language unless the agency is exercising a statutory purchase right. PuSH enforcement is never described as a fine or penalty (ORS 456.265 is titled "Sanctions against withdrawing property owner prohibited"; verify).

## Purpose
The 10-year expiring list and status-flip report for the board, council or commission, in public_packet scope: organization + registered agent + program facts only, SB 32 fields, redactions logged. Boards buy units, not lead scores: the headline is properties / restricted units / HAP units / PSH units / public UPB with an owner cliff inside 36 months, banded on the owner cliff.

## Packet skeleton (board_packet.md)
```
# Preservation and Loan-Book Review — Board Packet: [agency_name] — as of [date]
Prepared for public meeting; personal information redacted under ORS 192.355(2) [verify]. Bands are months.
## Book Verdict and Headline — [STABLE | WATCH | STRESSED | CRITICAL]; [n] properties / [n] restricted units / [n] HAP / [n] PRAC / [n] PSH / $[x] public UPB with an owner cliff inside 36 months
## Units at Risk by Band and Jurisdiction — Board_Totals table (owner_cliff_band x county; stale contract date — verify as its own row)
## Units by Year (10-year list) — SB 32 fields: property, jurisdiction, expiration date, units, assistance type, income level, preservation status, owner organization, registered agent
## Status Since Last Report — notice filed n, tenant notice confirmed n, QC requested / presented n, HAP renewed n, loan extended / recast n, covenant cured n, recap closed n, preserved n units, lost n units (evidence-based)
## Sponsor Concentration — top organizations by units, UPB share, cliffs in 36 months
## Redactions Applied — Redaction_Log summary
## Assumptions and Limits — statutory text status (verified_live false), UPB-at-risk rule, equity overlay status
```
