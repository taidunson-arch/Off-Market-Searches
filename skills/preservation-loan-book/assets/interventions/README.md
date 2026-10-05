# Intervention catalog (assets)

One markdown file per intervention. Each file opens with a YAML front block (`id, routes, trigger_events, agency_owner, statutory_cite[] with verified_live:false and a note, owner_notice, tenant_notice, timeline, pii_scope, first_action, kpi_flip_on_success, notice_address_rule`), then the banner "Confirm current statutory text before sending", then a letter, memo or checklist skeleton. The index with route mapping, catalog semantics and how `score_preservation.py` selects an intervention is `references/intervention-catalog.md`.

No template treats an owner as a counterparty to a sale; there is no bid language and no fines language for PuSH (ORS 456.265 is titled "Sanctions against withdrawing property owner prohibited"; verify). The only purchase language in the catalog is `rofr_match_offer`, where the agency exercises its own statutory right.

| id | routes | agency_owner | owner notice | tenant notice |
|---|---|---|---|---|
| `push_window_prep` | notice_compliance (secondary) | push_program_manager | none yet — the owner is not late inside the window; no letter is sent | none |
| `push_notice_demand_letter` | notice_compliance | push_program_manager | owner-facing letter by certified mail to notice_address; copy to each affected l... | none from the agency; the letter restates the owner's own te... |
| `push_records_request` | notice_compliance, designee_rofr | push_program_manager | owner-facing written request to notice_address; sent only after the owner's noti... | none |
| `tenant_notice_check` | notice_compliance | compliance_officer | owner-facing request for proof of tenant and applicant notice (copies of notices... | none from the agency; the check verifies the owner's duty |
| `rofr_notice_recording` | designee_rofr | legal_counsel | owner receives a copy of the recorded notice and, where applicable, the designee... | none |
| `rofr_match_offer` | designee_rofr | legal_counsel | matching offer delivered to the owner by certified mail within the 30-day window | none |
| `rofr_assignment_memo` | designee_rofr, ta_sponsor | legal_counsel | owner notified of the assignment / designee appointment | none |
| `optout_tenant_notice_check` | optout_response | pbca_liaison | none from the agency to the owner at this step; this is a CA-side check of what ... | none from the agency; the check verifies the owner's one-yea... |
| `optout_response_plan` | optout_response | pbca_liaison | CA / preservation-office letter to the owner proposing renewal alternatives and,... | PHA issues enhanced vouchers to eligible households at termi... |
| `prac_renewal_coordination` | servicing_watch, optout_response (never primary for PRAC) | hud_mf_asset_manager | none required; sponsor coordination letter optional | none |
| `hud_legacy_response` | recap_committee | hud_mf_asset_manager | HUD requires owner tenant notice for 236 / BMIR prepayment and 202 prepayment / ... | HUD-required tenant notice (owner's duty); TPVs for pre-1974... |
| `usda_prepay_response` | designee_rofr, nofa_offer | nofa_program_manager | RD manages owner correspondence; the agency writes to RD as an interested party ... | RD tenant notice within 30 days of a complete request (RD's ... |
| `qc_request_acknowledgement` | qc_admin | compliance_officer | acknowledgement letter to the owner: request received, completeness determinatio... | tenant notice of QC status and of the 3-year protection if e... |
| `qc_waiver_acknowledgement` | qc_admin | compliance_officer | letter to the owner: the recorded REUA / Declaration waives the qualified-contra... | none |
| `qc_marketing_plan` | qc_admin | compliance_officer | presentment of a bona fide contract to the owner before QC_RESPONSE_DUE | agency notice of status per policy |
| `qc_coordination_with_hfa` | nofa_offer, ta_sponsor | nofa_program_manager | none; coordination letter to the HFA QC administrator | none |
| `preservation_nofa_invitation` | nofa_offer, ta_sponsor | nofa_program_manager | invitation letter to the owner or to the mission sponsor to apply to an open pro... | none |
| `loan_extension_recast_memo` | recap_committee | am_officer | owner application for extension / recast; agency default and cure notices per lo... | none for an agency-only recast; HUD-required tenant notice i... |
| `zero_pct_recap_term_sheet` | recap_committee, nofa_offer | am_officer | term sheet to the sponsor | none |
| `servicing_watch_memo` | servicing_watch | am_officer | none — internal monitoring memo for a current loan with a dated trigger | none |
| `covenant_enforcement_notice` | servicing_watch, recap_committee | am_officer | owner default / cure notice per the loan documents, or an inspection / complianc... | none |
| `enforcement_8823` | servicing_watch, qc_admin | compliance_officer | notice of noncompliance with the correction period | none |
| `covenant_recapture_review` | servicing_watch, recap_committee | cpd_program_manager | repayment demand or change-of-use determination to the owner; citizen notice and... | none |
| `pha_repositioning` | recap_committee, servicing_watch | pha_development | n/a (the PHA is the owner); HUD SAC / Office of Recapitalization submissions | resident consultation (970.9) and RAD relocation notices; TP... |
| `ta_sponsor_engagement` | ta_sponsor | nofa_program_manager | none to a third-party owner; engagement letter to the mission sponsor | none |
| `board_packet_summary` | all | board_liaison | none | none |
