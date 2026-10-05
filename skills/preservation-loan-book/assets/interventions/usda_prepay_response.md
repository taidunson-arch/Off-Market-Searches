---
id: usda_prepay_response
routes:
  - designee_rofr
  - nofa_offer
trigger_events:
  - USDA_515_PREPAY_ELIGIBLE
  - USDA_PREPAY_REQUEST_RECEIVED
  - USDA_PUBLIC_BODY_OFFER_WINDOW_END
  - USDA_515_MATURITY
  - USDA_EXIT_PROJECTED
agency_owner: nofa_program_manager
statutory_cite:
  - cite: "7 CFR 3560.653"
    verified_live: false
    note: "prepayment request for pre-12/15/1989 loans"
  - cite: "7 CFR 3560.654"
    verified_live: false
    note: "RD notifies tenants within 30 days of a complete request; borrower posts the notice"
  - cite: "7 CFR 3560.656-.658"
    verified_live: false
    note: "incentives to remain; borrower acceptance or rejection"
  - cite: "7 CFR 3560.659"
    verified_live: false
    note: "if incentives are rejected the borrower offers the project for sale to a nonprofit or public body for 180 days using two appraisals; verify"
  - cite: "7 CFR 3560.660-.662"
    verified_live: false
    note: "unrestricted prepayment only if no good-faith offer; otherwise 10-year restrictive-use extension; RD vouchers"
  - cite: "USDA MPR program notices (82 FR 2017-09500)"
    verified_live: false
    note: "Multifamily Preservation and Revitalization restructuring"
owner_notice: "RD manages owner correspondence; the agency writes to RD as an interested party and to the borrower only as a prospective public-body purchaser inside the offer window"
tenant_notice: "RD tenant notice within 30 days of a complete request (RD's duty)"
timeline: "ask RD for the request date; public-body offer window 180 days after advertising; RD vouchers at prepayment; MPR + 4% credits for the take-out"
pii_scope: organization
first_action: "write to the RD state office to be notified of any prepayment request on this project; on USDA_PREPAY_REQUEST_RECEIVED, decide whether the agency (or a county housing authority) will make a good-faith offer as an eligible public body or sponsor a nonprofit offer; pair with MPR"
kpi_flip_on_success: preserved / recap_closed
notice_address_rule: "print notice_address and notice_address_source; agency file first (regulatory_agreement > hap_contract > loan_docs), SOS registered agent fallback with Verify — Notice Address; hold the letter when source is unknown"
---

# Intervention: `usda_prepay_response`

> **Confirm current statutory text before sending.** Every cite in this build is `verified_live: false`: statute and regulation text was not read from an official source. Agency counsel reviews the cite, the window and the recipient before any letter leaves. Nothing here treats an owner as a counterparty to a sale; there is no bid and no purchase language unless the agency is exercising a statutory purchase right. PuSH enforcement is never described as a fine or penalty (ORS 456.265 is titled "Sanctions against withdrawing property owner prohibited"; verify).

## Purpose
Section 515 prepayment is governed by RD's process, and that process names the public body as an eligible purchaser. The agency's job is to be in the room: know the request date, stand ready with an offer or a sponsor, and bring MPR and 4% credits to the take-out.

## Memo skeleton
```
Property [property_name]; 515 loan [project id if known]; USDA_515_MATURITY [date]; prepay eligible [yes | date]; request received [usda_prepay_request_date | none]
RD state office contact: request status; incentive offer status; tenant notice date (+30 d)
Offer window: USDA_PUBLIC_BODY_OFFER_WINDOW_END [date] (180 days, verify); appraisals (two independent)
Agency path: [public-body offer by agency / county housing authority | nonprofit sponsor offer with gap] + MPR + 4% credits; new restrictive-use term
Units: [units_at_risk]; RA units [other_ra_units]
```
