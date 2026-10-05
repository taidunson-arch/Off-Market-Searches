---
id: push_notice_demand_letter
routes:
  - notice_compliance
trigger_events:
  - NOTICE_COMPLIANCE_BREACH
  - PUSH_FIRST_NOTICE_DUE (passed, notice_status not_received_confirmed)
  - PUSH_SECOND_NOTICE_DUE (passed, no second notice)
agency_owner: push_program_manager
statutory_cite:
  - cite: "ORS 456.260"
    verified_live: false
    note: "owner notice to OHCS and each affected local government no sooner than 30 and at least 24 months before withdrawal per the OAR 813-115-0030 summary; the (1)/(2) split and any first/second distinction are unread; no 36-month owner-notice start was found"
  - cite: "ORS 456.262"
    verified_live: false
    note: "withdrawal and termination barred until 30 months after the (1) notices / 24 months after the (2) notices; OHCS may appoint a designee after the owner delivers notice OR 30 months before the contract term would expire, whichever is earlier (not conditioned on non-compliance; HB 2095, 2021)"
  - cite: "OAR 813-115-0030"
    verified_live: false
    note: "notice content and delivery"
  - cite: "SB 973 (2025)"
    verified_live: false
    note: "for each tenant not given notice the owner must extend the affordability restriction; operative date verify"
owner_notice: "owner-facing letter by certified mail to notice_address; copy to each affected local government (or to OHCS when the sender is the local government)"
tenant_notice: "none from the agency; the letter restates the owner's own tenant-notice duty (SB 973)"
timeline: "within 10 business days after PUSH_FIRST_NOTICE_DUE passes with not_received_confirmed; owner response requested within 30 days"
pii_scope: organization
first_action: "confirm not_received_confirmed against the PuSH-CP log; counsel reviews the cites; send by certified mail; calendar the 30-day response and the designee appointment decision"
kpi_flip_on_success: notice_filed
notice_address_rule: "print notice_address and notice_address_source; agency file first (regulatory_agreement > hap_contract > loan_docs), SOS registered agent fallback with Verify — Notice Address; hold the letter when source is unknown"
---

# Intervention: `push_notice_demand_letter`

> **Confirm current statutory text before sending.** Every cite in this build is `verified_live: false`: statute and regulation text was not read from an official source. Agency counsel reviews the cite, the window and the recipient before any letter leaves. Nothing here treats an owner as a counterparty to a sale; there is no bid and no purchase language unless the agency is exercising a statutory purchase right. PuSH enforcement is never described as a fine or penalty (ORS 456.265 is titled "Sanctions against withdrawing property owner prohibited"; verify).

## Purpose
A notice-deficiency letter from the qualified purchaser to the owner of publicly supported housing whose statutory first (or second) notice is past due and confirmed not received. It asserts the agency's position that the withdrawal clock has not started, states the agency's intent to consider a designee appointment, and reminds the owner of the tenant-notice duty and the per-tenant affordability extension. No fines or penalties are described.

## Letter skeleton
```
[Agency letterhead]                                                         [date]
CERTIFIED MAIL — RETURN RECEIPT REQUESTED
[Owner entity], [role: General Partner / Managing Member]
[notice_address]  (address source: [notice_address_source])

Re: [property_name], [address], [jurisdiction] — publicly supported housing, [units] units
    Affordability restriction(s) ending [withdrawal_anchor_date] ([owner_cliff_type], [basis])

[Agency] is [the Oregon Housing and Community Services Department / the affected local government] for the above property
within the meaning of ORS 456.250 [verify]. Our records show no notice of intent to withdraw under ORS 456.260 [verify]
as of [as_of]. The restriction(s) end [anchor]; [PUSH_FIRST_NOTICE_DUE] (30 months before that date) has passed. Under ORS 456.262
[verify] the withdrawal clocks run only from a delivered notice, and [Agency] may appoint a designee as qualified purchaser from
the earlier of your notice or that date. [Internal: NOTICE_COMPLIANCE_BREACH is a working label for "clock not started, designee
available"; do not assert a statutory breach or a missed deadline until ORS 456.260 / .262 text has been read.]

1. Position. Until proper notice is delivered to [OHCS and each affected local government], the restriction(s) may not be
   withdrawn or terminated before the later of the statutory clocks (ORS 456.262 [verify]).
2. Request. Please confirm in writing within 30 days whether you intend to withdraw the property from publicly supported
   housing, and if so deliver the required notice(s). If you do not intend to withdraw, please say so and this file closes.
3. Tenant notice. If you intend to withdraw, tenants and applicants must receive notice within the statutory window and
   in the required languages (SB 973 [verify operative date]); for each tenant not noticed the affordability restriction
   extends by operation of law [verify].
4. Qualified purchaser. [Agency] may appoint a designee as qualified purchaser and may record a notice of right of first
   refusal (ORS 456.262; OAR 813-115-0060 [verify]). We would welcome a conversation about preservation options,
   including [mandate_eligible_products].

Please direct your response to [push_program_manager role], [agency business address / program email].
cc: [affected local government housing director] / [OHCS PuSH-CP Program Manager]
```

## Record
On sending: event PRESERVATION_NOTICE demand sent (internal log), AM status Letter Sent, response due [date]. On the owner's notice: PRESERVATION_NOTICE_RECEIVED (RECORDED) -> push_records_request, rofr_notice_recording. On "no intent to withdraw": kpi none; close the breach; keep servicing_watch if in book.
