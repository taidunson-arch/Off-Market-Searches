---
id: servicing_watch_memo
routes:
  - servicing_watch
trigger_events:
  - AGENCY_LOAN_MATURITY (<= 60 months)
  - AFFORDABILITY_PERIOD_END (ours, <= 60 months)
  - GRANT_RECAPTURE_END / SHARED_APPRECIATION_DUE (<= 60 months)
  - LOAN_MATURITY / HUD_DIRECT_LOAN_MATURITY (senior cliff <= 60 months)
  - INSPECTION_DUE (<= 6 months)
agency_owner: am_officer
statutory_cite:
  - cite: "loan and regulatory agreement (monitoring only)"
    verified_live: false
    note: "no statutory trigger: this memo exists so a healthy loan with a dated cliff is calendared without an enforcement notice"
owner_notice: "none — internal monitoring memo; no correspondence to the owner while covenant_status is current"
tenant_notice: "none"
timeline: "open when the trigger lands inside 60 months; convert to loan_extension_recast_memo (recap_committee) when the maturity falls inside 24 months or the sponsor applies"
pii_scope: organization
first_action: "confirm the trigger (our maturity, affordability end, senior cliff) against the loan file; calendar the recast / extension decision date; note the restricted-NOI capacity (sizing-lihtc-permanent-debt handoff) for the committee"
kpi_flip_on_success: loan_extended
notice_address_rule: "n/a (no letter); confirm notice_address and notice_address_source in the file for later steps"
---

# Intervention: `servicing_watch_memo`

> **Confirm current statutory text before sending.** Nothing is sent from this memo. It exists because `servicing_watch` fires on a current loan whose only trigger is a dated maturity, affordability end or senior cliff inside 60 months; naming an enforcement notice on such a card misreads a healthy asset. Enforcement correspondence (`covenant_enforcement_notice`) is reserved for covenant_status watch / default, a failing REAC / NSPIRE score or an open noncompliance finding.

## Purpose
Keeps a healthy book loan on the AM officer's calendar with the right reading: "our dollars and these units have a dated decision point; nothing is wrong today."

## Memo skeleton
```
Property: [property_name], [address], [jurisdiction]; ids [agency_loan_ids / grant_ids]; book_kind [book_kind]; am_officer [am_officer]
Trigger: [AGENCY_LOAN_MATURITY | AFFORDABILITY_PERIOD_END | GRANT_RECAPTURE_END | senior LOAN_MATURITY] [date] ([basis]) — [months_out] months
Position: UPB $[public_upb] [payment_type] at [our_rate]; affordability_end [affordability_end]; recapture [recapture_type] exposure $[recapture_exposure]; covenant_status current
Senior lien: [senior_lien_type] matures [senior_maturity] ([senior_maturity_basis]); coterminous_senior_cliff [true/false]
Units: [units_at_risk] restricted / [hap_units_at_risk] HAP / [prac_units_at_risk] PRAC / [psh_units_at_risk] PSH
Decision date: [our maturity - 24 months] -> recap_committee (loan_extension_recast_memo) if no sponsor plan by then
Handoffs: sizing-lihtc-permanent-debt (restricted-NOI capacity), critical-dates-tracker (seed dates)
```

## Record
AM status Monitoring -> Assigned; kpi `loan_extended` when `our_maturity` moves later between runs.
