---
id: push_window_prep
routes:
  - notice_compliance (secondary)
trigger_events:
  - PRESERVATION_NOTICE_WINDOW (push_first_window open)
  - PUSH_WINDOW_PREP
  - REGULATORY_LATEST_END
  - LIHTC_EXTENDED_USE_END
agency_owner: push_program_manager
statutory_cite:
  - cite: "OAR 813-115-0030"
    verified_live: false
    note: "owner first-notice window 36-30 months before withdrawal; section number from snippets"
  - cite: "ORS 456.260 (owner notice no sooner than 30 / at least 24 months before withdrawal per the OAR 813-115-0030 summary; the 36-month prep start is internal)"
    verified_live: false
    note: "owner first notice to OHCS and each affected local government; current text post-SB 973 not read"
owner_notice: "none yet — the owner is not late inside the window; no letter is sent"
tenant_notice: "none"
timeline: "open at anchor - 36 months (PUSH_WINDOW_PREP); runs until PUSH_FIRST_NOTICE_DUE (anchor - 30 months)"
pii_scope: organization
first_action: "confirm the PuSH-CP notice log for this property; pull the LURA/REUA and HAP contract from our own file; confirm notice_address and source; pre-draft (do not send) the records request"
kpi_flip_on_success: notice_filed (if a notice arrives) or none
notice_address_rule: "print notice_address and notice_address_source; agency file first (regulatory_agreement > hap_contract > loan_docs), SOS registered agent fallback with Verify — Notice Address; hold the letter when source is unknown"
---

# Intervention: `push_window_prep`

> **Confirm current statutory text before sending.** Every cite in this build is `verified_live: false`: statute and regulation text was not read from an official source. Agency counsel reviews the cite, the window and the recipient before any letter leaves. Nothing here treats an owner as a counterparty to a sale; there is no bid and no purchase language unless the agency is exercising a statutory purchase right. PuSH enforcement is never described as a fine or penalty (ORS 456.265 is titled "Sanctions against withdrawing property owner prohibited"; verify).

## Purpose
Internal preparation while the owner's first-notice window is open. The owner is not late; the agency gets ready so that the day PUSH_FIRST_NOTICE_DUE passes it can act within a week. This intervention produces no outbound letter.

## Checklist (internal memo)
```
Property: [property_name] — [address], [jurisdiction]   property_id [id]
Withdrawal anchor: [withdrawal_anchor_date] ([push_anchor_source]; derived from [owner_cliff_type] [basis])
Window: first notice [window_start]..[window_end]; PUSH_FIRST_NOTICE_DUE [date]; PUSH_SECOND_NOTICE_DUE [date]
1. Notice log: [notice_status] as of [as_of] (PuSH-CP log / local received-notice file). If unknown -> ask OHCS PuSH-CP; record the answer as RECORDED.
2. Our file: LURA/REUA end date [date, basis]; HAP contract term and current expiration [date]; loan/grant documents [ids].
3. Notice address: [notice_address] (source [notice_address_source]); SOS status [sos_status]; registered agent [name, business address].
4. Units at risk: [units_at_risk] restricted / [hap_units_at_risk] HAP / [psh_units_at_risk] PSH.
5. Pre-draft: push_records_request (held until a notice is received); push_notice_demand_letter (held until the due date passes with not_received_confirmed).
6. Mandate: open products [mandate_eligible_products]; TA sponsor candidates if the owner is a mission GP.
Owner at agency: push_program_manager. Next review: [PUSH_FIRST_NOTICE_DUE].
```

## Do not
- Send a demand or records request before the statutory trigger.
- Treat absence of a notice in a dataset as owner silence; only the agency's own log can say so.
