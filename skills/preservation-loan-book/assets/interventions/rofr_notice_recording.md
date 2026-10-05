---
id: rofr_notice_recording
routes:
  - designee_rofr
trigger_events:
  - PRESERVATION_NOTICE_RECEIVED (push_first / push_second)
  - NOTICE_COMPLIANCE_BREACH (designee appointment on silence)
  - LIHTC_EXTENDED_USE_END
agency_owner: legal_counsel
statutory_cite:
  - cite: "OAR 813-115-0060"
    verified_live: false
    note: "qualified purchasers may record a Notice of Right of First Refusal in county real-property records; section from snippets"
  - cite: "ORS 456.262"
    verified_live: false
    note: "two-step sequence per the statute snippet: on or after the date OHCS may appoint a designee, the qualified purchaser first delivers an OFFER to purchase that includes notice that it may, AFTER 30 DAYS, record a notice of right of first refusal; the notice must declare that the ROFR expires 24 months after the withdrawal date; designee appointment after consulting the local government; assignable to a qualified purchaser — verify"
  - cite: "OAR 813-115-0035"
    verified_live: false
    note: "designee appointment procedure"
owner_notice: "owner receives a copy of the recorded notice and, where applicable, the designee appointment notice"
tenant_notice: "none"
timeline: "step 1 on or after the designee-appointment date (owner's notice received, or anchor - 30 months, whichever is earlier): deliver the qualified purchaser's offer with notice of intent to record (qp_offer_delivered_date); step 2: record no earlier than ROFR_RECORDABLE_DATE = offer + 30 days; the recorded ROFR expires 24 months after the withdrawal date (verify)"
pii_scope: organization
first_action: "step 1: counsel delivers the qualified purchaser's offer to the owner at notice_address with the statutory notice of intent to record (log qp_offer_delivered_date); step 2: prepare the Notice of ROFR for the county recorder and record on or after ROFR_RECORDABLE_DATE (offer + 30 d); confirm legal description and owner entity from our regulatory agreement; decide designee appointment with the affected local government"
kpi_flip_on_success: none (ROFR_RECORDED event; declared intent 8 points)
notice_address_rule: "print notice_address and notice_address_source; agency file first (regulatory_agreement > hap_contract > loan_docs), SOS registered agent fallback with Verify — Notice Address; hold the letter when source is unknown"
---

# Intervention: `rofr_notice_recording`

> **Confirm current statutory text before sending.** Every cite in this build is `verified_live: false`: statute and regulation text was not read from an official source. Agency counsel reviews the cite, the window and the recipient before any letter leaves. Nothing here treats an owner as a counterparty to a sale; there is no bid and no purchase language unless the agency is exercising a statutory purchase right. PuSH enforcement is never described as a fine or penalty (ORS 456.265 is titled "Sanctions against withdrawing property owner prohibited"; verify).

## Purpose
Perfects the agency's (or its designee's) right of first refusal against title so that any third-party sale must be offered to the qualified purchaser first. The statutory path (ORS 456.262 as summarized in snippets; verify) is a **two-step sequence**, not a recording on receipt of the owner's notice: (1) on or after the date OHCS may appoint a designee (the owner's notice, or 30 months before the restriction expires, whichever is earlier), the qualified purchaser delivers an **offer to purchase** that includes notice that it may, **after 30 days**, record a notice of right of first refusal; (2) the Notice of ROFR is recorded no earlier than `ROFR_RECORDABLE_DATE` = offer delivered + 30 days. Recording before the offer and the 30-day wait is not the statutory path and could produce a defective recording. The notice declares that the ROFR expires **24 months after the withdrawal date** (statute snippets and the OHCS designee page; no source supports 36). For OHCS this file also covers the designee appointment memo when the owner is silent (HB 2095; verify).

## Step 1 — qualified purchaser's offer skeleton (owner-facing)
```
To: [owner_name] at [notice_address] ([notice_address_source]); certified mail
From: [OHCS | affected local government | OHCS designee: entity, appointment date] as qualified purchaser (ORS 456.250; verify)
Property: [property_name], [address]
Basis: [PRESERVATION_NOTICE_RECEIVED date, detail] | [anchor - 30 months reached on [date]: designee appointment available, "whichever is earlier" — ORS 456.262; verify]
Offer to purchase on the terms attached, including a commitment to preserve the property as affordable on terms determined by OHCS
Statutory notice: the qualified purchaser may, after 30 days from delivery of this offer, record a notice of right of first refusal (ORS 456.262; verify)
qp_offer_delivered_date: [date] -> ROFR_RECORDABLE_DATE [date + 30 d]
```

## Step 2 — recording memo skeleton (on or after ROFR_RECORDABLE_DATE)
```
To: legal_counsel / county recorder ([county], [recording fee from market-params, verify])
Property: [property_name], [address]; legal description from [regulatory_agreement / vesting deed]; owner entity [owner_name] (SOS [status])
Offer delivered: [qp_offer_delivered_date]; recordable from [ROFR_RECORDABLE_DATE] (confirm today >= that date)
Qualified purchaser recording: [OHCS | affected local government | OHCS designee: entity, appointment date]
Instrument: Notice of Right of First Refusal under ORS 456.262 / OAR 813-115-0060 [verify]
Duration noted: expires 24 months after the withdrawal date [verify]
Assignability: to a qualified purchaser (see rofr_assignment_memo)
Copies: owner at [notice_address]; local government; OHCS PuSH-CP
```

## Record
ROFR_RECORDED (RECORDED, recording date); rofr_recorded true on the lead; readiness for rofr_match_offer.
