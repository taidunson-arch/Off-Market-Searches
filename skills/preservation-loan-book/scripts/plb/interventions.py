"""Intervention catalog metadata (mirror of assets/interventions/<id>.md front blocks; references/intervention-catalog.md).

The score step, make_handoffs.py and the workbook read `first_action`, `agency_owner`, `statutory_cite`, owner / tenant notice
flags and the PII scope from here. Every cite is unverified in this build (verified_live false) and every template carries
the banner "Confirm current statutory text before sending". No entry addresses an owner as a seller; PuSH enforcement is
never described as a fine (ORS 456.265 prohibits sanctions against a withdrawing owner).
"""
from __future__ import annotations

from typing import Any, Dict, List

VERIFY = " (verify current text before sending)"

CATALOG: Dict[str, Dict[str, Any]] = {
    "push_window_prep": {"routes": ["notice_compliance"], "agency_owner": "push_program_manager", "statutory_cite": "OAR 813-115-0030; ORS 456.260",
                         "owner_notice": False, "tenant_notice": False, "pii_scope": "organization",
                         "first_action": "Confirm the PuSH-CP notice log; pull the LURA/REUA and HAP contract from our file; confirm the notice address; pre-draft the records request",
                         "kpi_flip_on_success": "notice_filed"},
    "push_notice_demand_letter": {"routes": ["notice_compliance"], "agency_owner": "push_program_manager", "statutory_cite": "ORS 456.260; ORS 456.262; OAR 813-115-0030; SB 973 (2025) per-tenant extension",
                                  "owner_notice": True, "tenant_notice": False, "pii_scope": "organization",
                                  "first_action": "Send the owner a notice-deficiency letter asserting the withdrawal bar (ORS 456.262) and the extended restriction for un-noticed tenants; consider designee appointment on silence (HB 2095)",
                                  "kpi_flip_on_success": "notice_filed"},
    "push_records_request": {"routes": ["notice_compliance", "designee_rofr"], "agency_owner": "push_program_manager", "statutory_cite": "OAR 813-115-0050 (qualified purchaser access to property, records and documents; ORS 456.262(6)-(7)); 30-day response period not found in rule text",
                             "owner_notice": True, "tenant_notice": False, "pii_scope": "organization",
                             "first_action": "Send the property-records request (compliance reports, approved rent schedule with actual rents) within 10 days of the owner's notice; track a 30-day working response date (period unverified)", "kpi_flip_on_success": ""},
    "tenant_notice_check": {"routes": ["notice_compliance"], "agency_owner": "compliance_officer", "statutory_cite": "SB 973 (2025); ORS 456.259",
                            "owner_notice": True, "tenant_notice": True, "pii_scope": "organization",
                            "first_action": "Confirm the owner's tenant and applicant notices (30-36 months, five languages) and assert the per-tenant affordability extension where missing",
                            "kpi_flip_on_success": "tenant_notice_confirmed"},
    "rofr_notice_recording": {"routes": ["designee_rofr"], "agency_owner": "legal_counsel", "statutory_cite": "ORS 456.262; OAR 813-115-0060",
                              "owner_notice": True, "tenant_notice": False, "pii_scope": "organization",
                              "first_action": "Step 1: deliver the qualified purchaser's offer with the statutory notice of intent to record; step 2: record the Notice of ROFR with the county recorder no earlier than offer + 30 days (ROFR_RECORDABLE_DATE); deliver any designee appointment to the owner", "kpi_flip_on_success": ""},
    "rofr_match_offer": {"routes": ["designee_rofr"], "agency_owner": "legal_counsel", "statutory_cite": "ORS 456.263; OAR 813-115-0070",
                         "owner_notice": True, "tenant_notice": False, "pii_scope": "organization",
                         "first_action": "Deliver the matching offer by certified mail within 30 days of the owner's mailing; the first match must be accepted", "kpi_flip_on_success": "preserved"},
    "rofr_assignment_memo": {"routes": ["designee_rofr"], "agency_owner": "legal_counsel", "statutory_cite": "ORS 456.262 (assignability)",
                             "owner_notice": True, "tenant_notice": False, "pii_scope": "organization",
                             "first_action": "Assign the recorded ROFR to a mission sponsor with recap capacity; notify the owner", "kpi_flip_on_success": "preserved"},
    "optout_tenant_notice_check": {"routes": ["optout_response"], "agency_owner": "pbca_liaison", "statutory_cite": "42 U.S.C. 1437f(c)(8); 24 CFR 402.8; Section 8 Renewal Policy Guide ch. 11",
                                   "owner_notice": True, "tenant_notice": True, "pii_scope": "organization",
                                   "first_action": "confirm renewal request / opt-out notice at CA", "kpi_flip_on_success": "hap_renewed"},
    "optout_response_plan": {"routes": ["optout_response"], "agency_owner": "pbca_liaison", "statutory_cite": "42 U.S.C. 1437f(c)(8); 24 CFR 402.8; Section 8 Renewal Guide chs. 2-3, 11, 15; 42 U.S.C. 1437f(t)",
                             "owner_notice": True, "tenant_notice": True, "pii_scope": "organization",
                             "first_action": "Review the owner's tenant letters at the CA (defective notice restarts the clock); counteroffer MU2M / 20-year renewal; line up a nonprofit transfer with HAP assignment and enhanced vouchers",
                             "kpi_flip_on_success": "hap_renewed"},
    "prac_renewal_coordination": {"routes": ["servicing_watch"], "agency_owner": "hud_mf_asset_manager", "statutory_cite": "Notice H 2022-05 (five-year PRAC renewals)",
                                  "owner_notice": False, "tenant_notice": False, "pii_scope": "organization",
                                  "first_action": "Confirm the PRAC renewal with HUD and the sponsor; appropriation and sponsor capacity, not opt-out, are the risk", "kpi_flip_on_success": "hap_renewed"},
    "hud_legacy_response": {"routes": ["recap_committee"], "agency_owner": "hud_mf_asset_manager", "statutory_cite": "Notice H 2013-17; 24 CFR 891.530; Notice H 2013-25; Section 250 NHA",
                            "owner_notice": True, "tenant_notice": True, "pii_scope": "organization",
                            "first_action": "Coordinate 202 prepayment (20-year use agreement) or 236 IRP decoupling with HUD; 150-270 day Section 250 notice", "kpi_flip_on_success": "preserved"},
    "usda_prepay_response": {"routes": ["designee_rofr"], "agency_owner": "rd_state_office", "statutory_cite": "7 CFR 3560.653-.662",
                             "owner_notice": True, "tenant_notice": True, "pii_scope": "organization",
                             "first_action": "Track the RD prepayment request; prepare the public-body offer inside the 180-day window; pair MPR with 4% credits", "kpi_flip_on_success": "preserved"},
    "qc_request_acknowledgement": {"routes": ["qc_admin"], "agency_owner": "compliance_officer", "statutory_cite": "IRC 42(h)(6)(E)(i)(II); 42(h)(6)(F); 42(h)(6)(I); 42(h)(6)(E)(ii)",
                                   "owner_notice": True, "tenant_notice": True, "pii_scope": "organization",
                                   "first_action": "Acknowledge the qualified-contract request, verify the price certification, start the one-year presentment clock and notify tenants of the 3-year protection",
                                   "kpi_flip_on_success": "qc_requested"},
    "qc_waiver_acknowledgement": {"routes": ["qc_admin"], "agency_owner": "compliance_officer", "statutory_cite": "QAP qualified-contract waiver condition (vintage, verify)",
                                  "owner_notice": True, "tenant_notice": False, "pii_scope": "organization",
                                  "first_action": "Acknowledge the request as ineligible under the allocation's QC waiver; no clock runs", "kpi_flip_on_success": ""},
    "qc_marketing_plan": {"routes": ["qc_admin"], "agency_owner": "compliance_officer", "statutory_cite": "IRC 42(h)(6)(F); OHCS Draft Qualified Contract Procedure",
                          "owner_notice": False, "tenant_notice": False, "pii_scope": "organization",
                          "first_action": "Present a bona fide contract within the one-year period; presentment alone removes the exit", "kpi_flip_on_success": "qc_presented"},
    "qc_coordination_with_hfa": {"routes": ["nofa_offer", "ta_sponsor"], "agency_owner": "nofa_program_manager", "statutory_cite": "IRC 42(h)(6); HFA QC procedure",
                                 "owner_notice": False, "tenant_notice": False, "pii_scope": "organization",
                                 "first_action": "Coordinate with the HFA qualified-contract administrator; line up a mission buyer within the year", "kpi_flip_on_success": "qc_presented"},
    "preservation_nofa_invitation": {"routes": ["nofa_offer"], "agency_owner": "nofa_program_manager", "statutory_cite": "ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%)",
                                     "owner_notice": False, "tenant_notice": False, "pii_scope": "organization",
                                     "first_action": "Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff", "kpi_flip_on_success": "preserved"},
    "loan_extension_recast_memo": {"routes": ["recap_committee"], "agency_owner": "am_officer", "statutory_cite": "loan documents; NHA 236(e)(2); Notice H 2013-25; 24 CFR 92.252",
                                   "owner_notice": True, "tenant_notice": False, "pii_scope": "organization",
                                   "first_action": "Draft the committee memo: UPB, payment-type change, extension or resubordination, senior cliff, restricted-NOI capacity", "kpi_flip_on_success": "loan_extended"},
    "zero_pct_recap_term_sheet": {"routes": ["recap_committee"], "agency_owner": "am_officer", "statutory_cite": "agency lending authority; loan documents",
                                  "owner_notice": True, "tenant_notice": False, "pii_scope": "organization",
                                  "first_action": "Term sheet for a 0% recapitalization or recast tied to a new regulatory term", "kpi_flip_on_success": "loan_recast"},
    "covenant_enforcement_notice": {"routes": ["servicing_watch"], "agency_owner": "am_officer", "statutory_cite": "loan / regulatory agreement covenants; 24 CFR 92.504(d); NSPIRE scoring notice",
                                    "owner_notice": True, "tenant_notice": False, "pii_scope": "organization",
                                    "first_action": "Covenant monitoring: default / cure notice per loan documents; inspection and reserve review", "kpi_flip_on_success": "covenant_cured"},
    "servicing_watch_memo": {"routes": ["servicing_watch"], "agency_owner": "am_officer", "statutory_cite": "loan / regulatory agreement (monitoring only)",
                             "owner_notice": False, "tenant_notice": False, "pii_scope": "organization",
                             "first_action": "Servicing watch memo: confirm the trigger (our maturity, affordability end, senior cliff) against the loan file; calendar the recast / extension decision; no enforcement correspondence while covenant_status is current",
                             "kpi_flip_on_success": "loan_extended"},
    "enforcement_8823": {"routes": ["servicing_watch"], "agency_owner": "compliance_officer", "statutory_cite": "26 CFR 1.42-5(e); IRS Form 8823",
                         "owner_notice": True, "tenant_notice": False, "pii_scope": "organization",
                         "first_action": "Notice of noncompliance with correction period; Form 8823 within 45 days after the period", "kpi_flip_on_success": "covenant_cured"},
    "covenant_recapture_review": {"routes": ["servicing_watch"], "agency_owner": "cpd_program_manager", "statutory_cite": "24 CFR 92.252(e); 92.254(a)(5); 92.503; 24 CFR 93.302; 24 CFR 570.505",
                                  "owner_notice": True, "tenant_notice": False, "pii_scope": "organization",
                                  "first_action": "Review the recapture / resale or CDBG change-of-use position; demand repayment where triggered", "kpi_flip_on_success": ""},
    "pha_repositioning": {"routes": ["recap_committee"], "agency_owner": "pha_development", "statutory_cite": "RAD Notice H-2019-09 / PIH-2019-23 REV-4; 24 CFR part 970",
                          "owner_notice": False, "tenant_notice": True, "pii_scope": "organization",
                          "first_action": "Board memo on RAD or Section 18 repositioning of our own asset; resident consultation and TPV planning", "kpi_flip_on_success": "preserved"},
    "ta_sponsor_engagement": {"routes": ["ta_sponsor"], "agency_owner": "nofa_program_manager", "statutory_cite": "IRC 42(i)(7); SB 51 (2025)",
                              "owner_notice": False, "tenant_notice": False, "pii_scope": "organization",
                              "first_action": "Offer technical assistance for the 42(i)(7) ROFR or recapitalization; fund exit taxes / debt payoff via a 0% recap", "kpi_flip_on_success": "preserved"},
    "board_packet_summary": {"routes": ["*"], "agency_owner": "board_liaison", "statutory_cite": "SB 32 (2025); ORS 192.355(2); ORS 192.345",
                             "owner_notice": False, "tenant_notice": False, "pii_scope": "public_packet",
                             "first_action": "Publish the 10-year expiring list and status flips; organization and registered agent only", "kpi_flip_on_success": ""},
}


def meta(intervention_id: str) -> Dict[str, Any]:
    return CATALOG.get(intervention_id, {"agency_owner": "", "statutory_cite": "", "owner_notice": False, "tenant_notice": False, "first_action": "", "pii_scope": "organization"})


def cite(intervention_id: str) -> str:
    c = meta(intervention_id).get("statutory_cite", "")
    return (c + VERIFY) if c else ""


def ids_for_route(route: str) -> List[str]:
    return [k for k, v in CATALOG.items() if route in v.get("routes", [])]
