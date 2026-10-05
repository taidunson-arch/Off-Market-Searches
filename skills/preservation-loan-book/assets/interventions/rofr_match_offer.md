---
id: rofr_match_offer
routes:
  - designee_rofr
trigger_events:
  - THIRD_PARTY_OFFER_RECEIVED
  - ROFR_MATCH_DEADLINE
agency_owner: legal_counsel
statutory_cite:
  - cite: "ORS 456.263"
    verified_live: false
    note: "owner must mail any third-party offer or its terms to each recorded ROFR holder by registered/certified mail; qualified purchaser has 30 days from mailing to deliver a matching offer; owner must accept the first matching offer. CONTENT REQUIREMENT (snippet): the matching offer must contain the qualified purchaser's commitment to preserve the property as affordable on terms determined by OHCS; permitted variations from the third-party terms: earnest money not less than the least of the third-party deposit, 2% of price or $250,000, refundable until the earlier of 90 days or closing; closing scheduled at least 240 days after execution — verify"
  - cite: "OAR 813-115-0070"
    verified_live: false
    note: "third-party offer procedure"
owner_notice: "matching offer delivered to the owner by certified mail within the 30-day window"
tenant_notice: "none"
timeline: "ROFR_MATCH_DEADLINE = third_party_offer_mailed_date + 30 days (received_date fallback carries Verify — Mailing Date); days remaining printed on the card"
pii_scope: organization
first_action: "confirm the certified mailing date; counsel confirms the terms to be matched; committee or director decision on matching or assigning within the window"
kpi_flip_on_success: preserved (on closing) / recap_closed
notice_address_rule: "print notice_address and notice_address_source; agency file first (regulatory_agreement > hap_contract > loan_docs), SOS registered agent fallback with Verify — Notice Address; hold the letter when source is unknown"
---

# Intervention: `rofr_match_offer`

> **Confirm current statutory text before sending.** Every cite in this build is `verified_live: false`: statute and regulation text was not read from an official source. Agency counsel reviews the cite, the window and the recipient before any letter leaves. Nothing here treats an owner as a counterparty to a sale; there is no bid and no purchase language unless the agency is exercising a statutory purchase right. PuSH enforcement is never described as a fine or penalty (ORS 456.265 is titled "Sanctions against withdrawing property owner prohibited"; verify).

## Purpose
The qualified purchaser's statutory match. This is the one intervention in the pack that contains purchase language, because the agency is exercising its own right of first refusal.

## Decision memo skeleton
```
Property [property_name]; ROFR recorded [date]; third-party offer mailed [third_party_offer_mailed_date] (Verify — Mailing Date if from received_date)
ROFR_MATCH_DEADLINE [date] — [n] days remaining
Terms to match: price [ ], financing contingencies [ ], closing date [ ], other material terms [ ] (from the mailed offer)
REQUIRED: affordability-preservation commitment on OHCS-determined terms (ORS 456.263; verify) — without it the match may not be a valid match
Permitted variations (ORS 456.263; verify): earnest money >= least of [third-party deposit] / [2% of price] / [$250,000], refundable until the earlier of 90 days or closing; closing scheduled >= 240 days after execution
Options: (a) match as [OHCS | local government]; (b) assign to a qualified purchaser / mission sponsor (rofr_assignment_memo); (c) decline (document why)
Funding: [mandate_eligible_products]; bridge [NOAH OHAF if listed]; recap gap estimate [recap_gap_estimate if our_book]
Units preserved if matched: [units_at_risk] restricted / [hap_units_at_risk] HAP / [psh_units_at_risk] PSH
Handoffs: front-door-lihtc-underwriting (composition mode), sizing-lihtc-permanent-debt
Decision by: [director / committee] on [date]; matching offer by certified mail no later than [deadline - 2 business days]
```

## Record
On match: kpi recap_closed at closing; preserved when the new regulatory term is recorded. On decline: document; keep notice_compliance / tenant_notice_check running.
