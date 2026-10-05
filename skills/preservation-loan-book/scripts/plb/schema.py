"""Shared vocabulary for preservation-loan-book.

Every enum string here is the exact string used in references/pipeline-contract.md, the scoring JSON files and
the output workbook. Scripts import from this module rather than retyping literals so a typo cannot silently
create a new category. `scripts/tests/test_contract.py` fails when the contract's Section 3 table or Section 6
column list drifts from EVENT_TAXONOMY / EVENT_COLUMNS.

The embedded dataset schemas, market parameters, agency profiles and mandate mirror the files under
references/sources/oregon-portland/. When a jurisdiction pack directory is supplied (`--pack`) the pack files win;
the embedded copies exist so the scripts run before the pack is written and so tests are hermetic.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - pyyaml is in requirements.txt
    yaml = None

# --------------------------------------------------------------------------- enums
ASSET_CLASSES = ["affordable_regulated", "noah_unregulated"]
SCORING_CLASS_FOR_ASSET = {"affordable_regulated": "affordable_public_am", "noah_unregulated": "noah_unregulated"}
AGENCY_PROFILES = ["hfa", "city_housing", "county", "pha_am", "cdbg_home"]
GEOGRAPHY_MODES = ["city_limits", "county", "metro_core", "cbsa", "custom"]
GEO_GRADES = ["county_field", "zip_crosswalk", "point_in_polygon", "city_name_weak"]

BASIS_LEVELS = ["RECORDED", "REPORTED", "DERIVED", "ESTIMATED", "PROXY"]
BASIS_MULTIPLIER = {"RECORDED": 1.00, "REPORTED": 0.90, "DERIVED": 0.80, "ESTIMATED": 0.50, "PROXY": 0.30}
AMBIGUOUS_MULTIPLIER = 0.40

VERIFY_FLAGS = [
    "Verify — Ambiguous",
    "Verify — Conflicting Sources",
    "Needs Anchor Date",
    "Missing Source — Request Document",
    "Rejected — Out of Range",
    "No Format Declared",
    "Verify — Book Join",
    "Verify — Notice Log",
    "Verify — Stale Contract Date",
    "Verify — Notice Address",
    "Verify — Mailing Date",
    "Verify — CA Log",
    "Verify — PuSH Coverage",
]
FLAG_AMBIGUOUS = "Verify — Ambiguous"
FLAG_CONFLICT = "Verify — Conflicting Sources"
FLAG_ANCHOR = "Needs Anchor Date"
FLAG_MISSING_SOURCE = "Missing Source — Request Document"
FLAG_REJECTED = "Rejected — Out of Range"
FLAG_NO_FORMAT = "No Format Declared"
FLAG_BOOK_JOIN = "Verify — Book Join"
FLAG_NOTICE_LOG = "Verify — Notice Log"
FLAG_STALE_CONTRACT = "Verify — Stale Contract Date"
FLAG_NOTICE_ADDRESS = "Verify — Notice Address"
FLAG_MAILING_DATE = "Verify — Mailing Date"
FLAG_CA_LOG = "Verify — CA Log"
FLAG_PUSH_COVERAGE = "Verify — PuSH Coverage"

EVENT_FAMILIES = ["DEBT", "REGULATORY", "HARD_DISTRESS", "TAX_LIEN", "PHYSICAL", "OWNERSHIP", "OPERATING", "AGENCY_DEADLINE"]
DIRECTIONS = ["PRESSURE", "SUPPRESSION", "ROUTING"]
EVENT_STATUS = ["FUTURE", "PAST", "STALE_CONTRACT_DATE", "SUPPRESSED", "RETIRED", "REJECTED"]

# (band, lo_months_inclusive, hi_months_exclusive, timing_fraction); months, not days
URGENCY_BANDS = [
    ("OVERDUE", None, 0, 1.00),
    ("CRITICAL", 0, 12, 1.00),
    ("URGENT", 12, 24, 0.75),
    ("APPROACHING", 24, 36, 0.50),
    ("MONITOR", 36, 60, 0.25),
    ("SCHEDULED", 60, 120, 0.00),
    ("BEYOND", 120, None, 0.00),
]
URGENCY_ORDER = [b[0] for b in URGENCY_BANDS]

OWNER_TYPES = [
    "individual_owner_of_record", "trust_estate", "single_asset_llc", "regional_operator",
    "institutional", "lihtc_partnership_forprofit_gp", "lihtc_partnership_nonprofit_gp", "nonprofit",
    "housing_authority", "government", "lender_reo_receiver", "self_owned", "unknown",
]
MISSION_OWNER_TYPES = {"nonprofit", "lihtc_partnership_nonprofit_gp", "housing_authority", "government"}
FORPROFIT_OWNER_TYPES = {"lihtc_partnership_forprofit_gp", "institutional", "regional_operator", "single_asset_llc"}
ORG_RESOLUTION_GRADES = ["A", "B", "C"]

ROUTES = ["optout_response", "notice_compliance", "qc_admin", "designee_rofr", "recap_committee", "servicing_watch", "nofa_offer", "ta_sponsor"]
PRIMARY_ROUTE_SENTINELS = ["none", "excluded"]
EXCLUSION_REASONS = ["in_development", "outside_geography", "under_5_units_no_program_event", "no_dated_cliff_in_horizon"]
QUEUE_BANDS = ["ESCALATE", "ACT", "PLAN", "WATCH", "EXCLUDED"]
QUEUE_MIN_SCORE = {"ESCALATE": 70, "ACT": 50, "PLAN": 30}

UNIVERSES = ["our_book", "universe_not_held"]
BOOK_MATCH = ["matched", "self_owned", "book_only", "unmatched_expected", "not_in_extract", "not_in_book", "book_absent"]
BOOK_JOIN_GRADES = ["crosswalk", "address", "fuzzy", "unmatched"]
BOOK_COVERAGE = ["full", "partial"]
BOOK_KINDS = ["loan", "grant", "owned_asset", "administered_contract"]

NOTICE_STATUS = ["received", "not_received_confirmed", "unknown"]
TENANT_NOTICE_STATUS = ["confirmed", "not_confirmed", "unknown", "n/a_pre_operative"]
HAP_RENEWAL_REQUEST_STATUS = ["received", "not_received", "unknown"]
HAP_RENEWAL_OPTIONS = ["1a", "1b", "2", "3", "4", "5", "6_optout", "unknown"]
RECAP_STATUS = ["none", "announced", "under_application", "closed"]
UNITS_BASIS = ["reported_buckets", "total_assumed_restricted", "proxy"]
PII_SCOPES = ["public_packet", "organization", "internal"]
MANDATE_FIT = ["eligible", "ineligible", "no_mandate_file"]
NOTICE_ADDRESS_SOURCES = ["regulatory_agreement", "hap_contract", "loan_docs", "sos_registered_agent", "unknown"]
QC_WAIVED = ["true", "false", "unknown"]
PAYMENT_TYPES = ["hard_pay", "residual_receipts", "deferred", "forgivable"]
COVENANT_STATUS = ["current", "watch", "default", "cured", "released"]
RECAPTURE_TYPES = ["home_recapture", "home_resale", "home_rental_repayment", "cdbg", "shared_appreciation", "none"]
RECAPTURE_METHODS = ["full", "prorata_reducing", "forgiveness_schedule", "cdbg_fmv_share", "none"]
SENIOR_LIEN_TYPES = ["hud_fha", "usda_rd", "fannie_dus", "freddie_k_sb", "bank_cu", "state_soft", "local_soft", "none", "unknown"]
AGENCY_ROLES = ["am_officer", "compliance_officer", "push_program_manager", "nofa_program_manager", "legal_counsel", "pbca_liaison",
                "board_liaison", "hud_mf_asset_manager", "rd_state_office", "cpd_program_manager", "pha_development"]
AM_STATUS = ["New", "Assigned", "Letter Sent", "Awaiting Response", "Committee", "Closed"]
FLIP_TYPES = ["notice_filed", "tenant_notice_confirmed", "qc_requested", "qc_presented", "hap_renewed", "hap_optout", "loan_extended",
              "loan_recast", "covenant_cured", "covenant_default", "recap_closed", "preserved", "lost", "new_to_list", "left_list"]

PROGRAMS = [
    "LIHTC_9", "LIHTC_4", "HAP", "PRAC", "RAC", "PAC", "PBV", "HUD_INSURED", "HUD_236", "HUD_202_811", "USDA_515",
    "HOME", "CDBG", "OAHTC", "GHAP", "HDGP", "LIFT", "HTF", "OTHER_OHCS", "LOCAL_REG", "PHB_LOAN", "TIF", "LEVY", "IH_SET_ASIDE",
]
HUD_CONTRACT_TO_PROGRAM = {
    "Housing Assistance Payment": "HAP",
    "Project Rental Assistance Contract": "PRAC",
    "Rental Assistance Contract": "RAC",
    "Project Assistance Contract": "PAC",
}
HAP_LIKE_PROGRAMS = {"HAP", "RAC", "PBV"}      # owner opt-out regime (one-year notice; MAHRA options)
PRAC_LIKE_PROGRAMS = {"PRAC", "PAC"}           # appropriation / sponsor-capacity regime, never opt-out
PUSH_COVERED_PROGRAMS = {"HAP", "PRAC", "RAC", "PAC", "LIHTC_9", "LIHTC_4", "HUD_236", "HUD_202_811", "USDA_515",
                         "HOME", "OAHTC", "GHAP", "HDGP", "LIFT", "HTF", "OTHER_OHCS"}
# restriction-type ends that anchor the PuSH withdrawal clocks (HAP/PRAC only with a non-renewal signal)
WITHDRAWAL_ANCHOR_EVENTS = {"LIHTC_EXTENDED_USE_END", "SOFT_PROGRAM_END", "AFFORDABILITY_PERIOD_END", "COVENANT_END", "USDA_515_MATURITY"}

# --------------------------------------------------------------------------- event taxonomy
EVENT_TAXONOMY: Dict[str, Dict[str, str]] = {
    # DEBT
    "LOAN_MATURITY": {"family": "DEBT", "direction": "PRESSURE"},
    "PREPAY_WINDOW_OPEN": {"family": "DEBT", "direction": "PRESSURE"},
    "LOAN_MODIFIED": {"family": "DEBT", "direction": "PRESSURE"},
    "HUD_DIRECT_LOAN_MATURITY": {"family": "DEBT", "direction": "PRESSURE"},
    "USDA_515_MATURITY": {"family": "DEBT", "direction": "PRESSURE"},
    "USDA_515_PREPAY_ELIGIBLE": {"family": "DEBT", "direction": "PRESSURE"},
    "USDA_EXIT_PROJECTED": {"family": "DEBT", "direction": "PRESSURE"},
    "SOFT_LOAN_MATURITY": {"family": "DEBT", "direction": "PRESSURE"},
    "AGENCY_LOAN_MATURITY": {"family": "DEBT", "direction": "PRESSURE"},
    "SHARED_APPRECIATION_DUE": {"family": "DEBT", "direction": "PRESSURE"},
    "REFINANCE_CLOSED": {"family": "DEBT", "direction": "SUPPRESSION"},
    "SUPPRESS_UNTIL": {"family": "DEBT", "direction": "SUPPRESSION"},
    # REGULATORY
    "LIHTC_COMPLIANCE_END": {"family": "REGULATORY", "direction": "PRESSURE"},
    "LIHTC_EXTENDED_USE_END": {"family": "REGULATORY", "direction": "PRESSURE"},
    "QC_ELIGIBILITY": {"family": "REGULATORY", "direction": "PRESSURE"},
    "HAP_EXPIRATION": {"family": "REGULATORY", "direction": "PRESSURE"},
    "PRESERVATION_NOTICE_WINDOW": {"family": "REGULATORY", "direction": "PRESSURE"},
    "PRESERVATION_NOTICE_RECEIVED": {"family": "REGULATORY", "direction": "PRESSURE"},
    "SOFT_PROGRAM_END": {"family": "REGULATORY", "direction": "PRESSURE"},
    "REGULATORY_LATEST_END": {"family": "REGULATORY", "direction": "PRESSURE"},
    "GRANT_RECAPTURE_END": {"family": "REGULATORY", "direction": "PRESSURE"},
    "AFFORDABILITY_PERIOD_END": {"family": "REGULATORY", "direction": "PRESSURE"},
    "COVENANT_END": {"family": "REGULATORY", "direction": "PRESSURE"},
    "RECAPTURE_TRIGGER": {"family": "REGULATORY", "direction": "PRESSURE"},
    "NOTICE_COMPLIANCE_BREACH": {"family": "REGULATORY", "direction": "PRESSURE"},
    "ROFR_RECORDED": {"family": "REGULATORY", "direction": "ROUTING"},
    "THIRD_PARTY_OFFER_RECEIVED": {"family": "REGULATORY", "direction": "ROUTING"},
    "QC_REQUEST_INELIGIBLE": {"family": "REGULATORY", "direction": "ROUTING"},
    "USDA_PREPAY_REQUEST_RECEIVED": {"family": "REGULATORY", "direction": "ROUTING"},
    "SECTION_18_APPLICATION": {"family": "REGULATORY", "direction": "ROUTING"},
    "RAD_CHAP": {"family": "REGULATORY", "direction": "ROUTING"},
    # AGENCY_DEADLINE (all helpers: the agency's own act-by dates)
    "PUSH_WINDOW_PREP": {"family": "AGENCY_DEADLINE", "direction": "PRESSURE"},
    "PUSH_FIRST_NOTICE_DUE": {"family": "AGENCY_DEADLINE", "direction": "PRESSURE"},
    "PUSH_SECOND_NOTICE_DUE": {"family": "AGENCY_DEADLINE", "direction": "PRESSURE"},
    "TENANT_NOTICE_WINDOW": {"family": "AGENCY_DEADLINE", "direction": "PRESSURE"},
    "RECORDS_REQUEST_DUE": {"family": "AGENCY_DEADLINE", "direction": "PRESSURE"},
    "RECORDS_RESPONSE_DUE": {"family": "AGENCY_DEADLINE", "direction": "PRESSURE"},
    "ROFR_RECORDABLE_DATE": {"family": "AGENCY_DEADLINE", "direction": "PRESSURE"},
    "ROFR_MATCH_DEADLINE": {"family": "AGENCY_DEADLINE", "direction": "PRESSURE"},
    "QC_RESPONSE_DUE": {"family": "AGENCY_DEADLINE", "direction": "PRESSURE"},
    "HAP_OPTOUT_NOTICE_DEADLINE": {"family": "AGENCY_DEADLINE", "direction": "PRESSURE"},
    "HAP_OPTOUT_PACKAGE_DUE": {"family": "AGENCY_DEADLINE", "direction": "PRESSURE"},
    "INSPECTION_DUE": {"family": "AGENCY_DEADLINE", "direction": "PRESSURE"},
    "USDA_PUBLIC_BODY_OFFER_WINDOW_END": {"family": "AGENCY_DEADLINE", "direction": "PRESSURE"},
    # OPERATING
    "REAC_SCORE": {"family": "OPERATING", "direction": "PRESSURE"},
    "TAX_EXEMPTION_LOST": {"family": "OPERATING", "direction": "PRESSURE"},
    "STABILIZATION_AWARD": {"family": "OPERATING", "direction": "PRESSURE"},
    "OCCUPANCY_DROP": {"family": "OPERATING", "direction": "PRESSURE"},
    "MGMT_CHANGE": {"family": "OPERATING", "direction": "PRESSURE"},
    "COVENANT_DEFAULT": {"family": "OPERATING", "direction": "PRESSURE"},
    "NONCOMPLIANCE_FINDING": {"family": "OPERATING", "direction": "PRESSURE"},
    # TAX_LIEN
    "TAX_DELINQUENT_YEARS": {"family": "TAX_LIEN", "direction": "PRESSURE"},
    "TAX_FORECLOSURE_LIST": {"family": "TAX_LIEN", "direction": "PRESSURE"},
    "TAX_REDEMPTION_END": {"family": "TAX_LIEN", "direction": "PRESSURE"},
    "MECHANICS_LIEN": {"family": "TAX_LIEN", "direction": "PRESSURE"},
    "JUDGMENT_LIEN": {"family": "TAX_LIEN", "direction": "PRESSURE"},
    "CODE_LIEN_REFERRAL": {"family": "TAX_LIEN", "direction": "PRESSURE"},
    "UTILITY_LIEN_CERTIFIED": {"family": "TAX_LIEN", "direction": "PRESSURE"},
    # PHYSICAL
    "CODE_CASE_OPEN": {"family": "PHYSICAL", "direction": "PRESSURE"},
    "DANGEROUS_BUILDING": {"family": "PHYSICAL", "direction": "PRESSURE"},
    # OWNERSHIP
    "ENTITY_ADMIN_DISSOLVED": {"family": "OWNERSHIP", "direction": "PRESSURE"},
    "MANAGER_CHANGE": {"family": "OWNERSHIP", "direction": "PRESSURE"},
    "REGISTERED_AGENT_CHANGE": {"family": "OWNERSHIP", "direction": "PRESSURE"},
    "UNENCUMBERED": {"family": "OWNERSHIP", "direction": "PRESSURE"},
    "HOLD_YEARS": {"family": "OWNERSHIP", "direction": "PRESSURE"},
    "ABSENTEE_TIER": {"family": "OWNERSHIP", "direction": "PRESSURE"},
    "DEPRECIATION_EXHAUSTED": {"family": "OWNERSHIP", "direction": "PRESSURE"},
    # HARD_DISTRESS kept as book-risk signals on a regulated asset
    "JUDICIAL_FORECLOSURE_FILED": {"family": "HARD_DISTRESS", "direction": "PRESSURE"},
    "LIS_PENDENS": {"family": "HARD_DISTRESS", "direction": "PRESSURE"},
    "UCC_MEZZ_PLEDGE": {"family": "HARD_DISTRESS", "direction": "PRESSURE"},
    "UCC_ART9_SALE": {"family": "HARD_DISTRESS", "direction": "PRESSURE"},
    "RECEIVER_APPOINTED": {"family": "HARD_DISTRESS", "direction": "ROUTING"},
    "BANKRUPTCY_FILED": {"family": "HARD_DISTRESS", "direction": "ROUTING"},
}
EVENT_TYPES = sorted(EVENT_TAXONOMY)
AGENCY_ACTION_EVENTS = {et for et, v in EVENT_TAXONOMY.items() if v["family"] == "AGENCY_DEADLINE"}
# Helper deadlines are arithmetic on another event of the same property. They are never a property's "first" event
# and are reported on their own segments of the calendar header, not inside the five basis counts.
HELPER_EVENTS = set(AGENCY_ACTION_EVENTS) | {"PRESERVATION_NOTICE_WINDOW"}
ROLLUP_EVENTS = {"REGULATORY_LATEST_END"}
# event types that are not dated owner cliffs even though they sit in REGULATORY / DEBT
NOT_OWNER_CLIFF = HELPER_EVENTS | {"LIHTC_COMPLIANCE_END", "PRESERVATION_NOTICE_RECEIVED", "QC_ELIGIBILITY", "NOTICE_COMPLIANCE_BREACH",
                                   "RECAPTURE_TRIGGER", "SUPPRESS_UNTIL", "REFINANCE_CLOSED", "REGULATORY_LATEST_END"}
PERMANENT_EVENT_TYPES = {"ENTITY_ADMIN_DISSOLVED", "UNENCUMBERED", "HOLD_YEARS"}
NON_DECAYING_WHILE_OPEN = {"COVENANT_DEFAULT", "NOTICE_COMPLIANCE_BREACH", "NONCOMPLIANCE_FINDING", "QC_ELIGIBILITY",
                           "THIRD_PARTY_OFFER_RECEIVED", "USDA_PREPAY_REQUEST_RECEIVED", "RECAPTURE_TRIGGER"}
ASSESSOR_DERIVED = {"HOLD_YEARS", "ABSENTEE_TIER", "TAX_DELINQUENT_YEARS", "DEPRECIATION_EXHAUSTED"}


def family_of(event_type: str) -> str:
    return EVENT_TAXONOMY.get(event_type, {}).get("family", "OPERATING")


def direction_of(event_type: str) -> str:
    return EVENT_TAXONOMY.get(event_type, {}).get("direction", "PRESSURE")


# --------------------------------------------------------------------------- canonical tables
LEAD_COLUMNS: List[str] = [
    # identity and geography (v2 verbatim)
    "property_id", "property_name", "address", "city", "zip", "county_fips", "county_name", "jurisdiction",
    "geo_modes", "geo_grade", "lat", "lon", "asset_class", "status", "units", "year_built", "rehab_year",
    "property_type", "programs", "hud_contract", "ami_30_60_units", "ami_80_units", "market_rate_units", "rental_assistance_units",
    # owner and sponsor (organization level)
    "owner_name", "owner_type", "owner_archetype", "developer_name", "manager_name", "registered_agent", "registered_agent_address",
    "sos_status", "notice_address", "notice_address_source", "sponsor_contact_role", "org_resolution_grade",
    # universe and book
    "universe", "in_inventory", "book_match", "book_join_grade", "book_kind", "ohcs_funded", "site_type",
    # units at risk
    "restricted_units", "units_basis", "units_at_risk", "hap_units_at_risk", "prac_units_at_risk", "other_ra_units", "psh_units_at_risk",
    "family_3br_plus_units", "vulnerability_flags",
    # our position
    "instruments_json", "asset_ids", "contract_ids", "agency_loan_ids", "grant_ids", "agency_programs", "public_upb", "public_upb_at_risk", "public_grant_at_risk", "our_rate", "payment_type",
    "our_maturity", "our_maturity_basis", "affordability_end", "recapture_type", "recapture_method", "recapture_amount", "recapture_exposure",
    "covenant_status", "senior_lien_type", "senior_maturity", "senior_maturity_basis", "senior_upb", "coterminous_senior_cliff", "am_officer",
    # first events (v2 verbatim)
    "first_debt_event_type", "first_debt_event_date", "first_debt_months_out", "first_debt_basis", "first_debt_source",
    "first_reg_event_type", "first_reg_event_date", "first_reg_months_out", "first_reg_basis", "first_reg_source",
    # anchors and clocks
    "withdrawal_anchor_date", "push_anchor_source", "owner_cliff_type", "owner_cliff_date", "owner_cliff_band",
    "agency_action_type", "agency_action_date", "agency_action_months_out", "agency_action_basis", "agency_action_owner", "action_band",
    "events_in_horizon",
    # recap sizing (our_book only)
    "est_restricted_noi", "noi_source", "recap_gap_estimate",
    # status and intent
    "notice_status", "tenant_notice_status", "hap_renewal_request_status", "hap_renewal_option", "next_expected_expiration", "recap_status",
    "qc_status", "qc_waived", "rofr_recorded", "apps_flag",
    # mandate
    "mandate_fit", "mandate_eligible_products", "mandate_ineligible_reason",
    # sponsor
    "sponsor_cliff_count",
    # scoring
    "signals", "verify_flags", "score_raw", "intervention_score", "board_impact", "queue_band", "urgency_band", "primary_route", "secondary_routes",
    "exclusion_reason",
    # intervention
    "intervention", "intervention_owner", "statutory_cite", "owner_notice_required", "tenant_notice_required", "verify_before_action", "next_action",
    "compliance_gates", "kpi_flags",
    # run
    "pii_scope", "source_vintages", "as_of_date",
]

EVENT_COLUMNS: List[str] = [
    "event_id", "property_id", "event_type", "event_family", "direction", "event_date", "months_out", "urgency_band",
    "basis", "confidence", "source", "source_vintage", "derivation", "program", "detail", "value", "verify_flag",
    "alt_dates", "window_start", "window_end", "status", "event_date_quality",
]

REJECT_COLUMNS = ["property_key", "property_id", "column", "raw_value", "reason", "flag", "alt_dates"]

SERVICING_COLUMNS: List[str] = [
    "book_kind", "agency_loan_id", "grant_id", "asset_id", "contract_id", "property_name", "address", "city", "zip", "county_fips", "parcel_id",
    "property_id", "ohcs_property_key", "program", "units_assisted", "upb", "accrued_interest", "rate", "rate_type", "payment_type",
    "origination_date", "maturity", "affordability_end", "contract_expiration", "recapture_type", "recapture_method", "recapture_amount",
    "recapture_start", "recapture_end", "covenant_status", "lien_position", "coterminous_with", "shared_appreciation_pct", "senior_lien_type",
    "senior_maturity", "senior_upb", "notice_log_status", "notice_received_date", "notice_detail", "tenant_notice_status",
    "hap_renewal_request_status", "hap_renewal_option", "qc_request_date", "qc_request_complete_date", "qc_waived",
    "third_party_offer_mailed_date", "third_party_offer_received_date", "qp_offer_delivered_date", "usda_prepay_request_date", "rad_chap_date",
    "section_18_application_date", "last_inspection_date", "open_findings_count", "last_8823_date", "last_reac_score", "last_reac_date",
    "apps_flag", "recap_status", "notice_address", "notice_address_source", "am_officer", "am_officer_email", "basis", "as_of",
]
SERVICING_DATE_COLUMNS = ["origination_date", "maturity", "affordability_end", "contract_expiration", "recapture_start", "recapture_end",
                          "senior_maturity", "notice_received_date", "qc_request_date", "qc_request_complete_date", "third_party_offer_mailed_date",
                          "third_party_offer_received_date", "qp_offer_delivered_date", "usda_prepay_request_date", "rad_chap_date", "section_18_application_date",
                          "last_inspection_date", "last_8823_date", "last_reac_date", "as_of"]
SERVICING_NUMERIC_COLUMNS = ["upb", "accrued_interest", "rate", "recapture_amount", "units_assisted", "shared_appreciation_pct", "senior_upb",
                             "open_findings_count", "last_reac_score", "lien_position"]
SERVICING_ENUMS = {
    "book_kind": BOOK_KINDS, "payment_type": PAYMENT_TYPES, "covenant_status": COVENANT_STATUS, "recapture_type": RECAPTURE_TYPES,
    "recapture_method": RECAPTURE_METHODS, "senior_lien_type": SENIOR_LIEN_TYPES, "notice_log_status": NOTICE_STATUS,
    "notice_detail": ["push_first", "push_second", "hap_optout"], "tenant_notice_status": TENANT_NOTICE_STATUS,
    "hap_renewal_request_status": HAP_RENEWAL_REQUEST_STATUS, "hap_renewal_option": HAP_RENEWAL_OPTIONS, "qc_waived": QC_WAIVED,
    "recap_status": RECAP_STATUS, "notice_address_source": NOTICE_ADDRESS_SOURCES, "basis": BASIS_LEVELS, "rate_type": ["fixed", "variable"],
    "program": PROGRAMS,
}
# required columns per book_kind; tuples are "any of"
SERVICING_REQUIRED_BY_KIND = {
    "loan": ["agency_loan_id", "upb", "maturity"],
    "grant": ["grant_id", ("affordability_end", "recapture_end")],
    "owned_asset": ["asset_id", "units_assisted", ("affordability_end", "contract_expiration")],
    "administered_contract": ["contract_id", "contract_expiration", "units_assisted"],
}

# --------------------------------------------------------------------------- default dataset schemas
DEFAULT_DATASET_SCHEMAS_YAML = r"""
agency_servicing_extract:
  match_columns: ["book_kind", "program"]
  match_any:
    - ["agency_loan_id", "grant_id", "asset_id", "contract_id"]
    - ["maturity", "affordability_end", "recapture_end", "contract_expiration"]
    - ["ohcs_property_key", "parcel_id", "address", "property_id"]
  key: ["book_kind", "agency_loan_id", "grant_id", "asset_id", "contract_id"]
  dates:
    origination_date:             {format: iso, basis: RECORDED}
    maturity:                     {format: iso, basis: RECORDED, event: AGENCY_LOAN_MATURITY}
    affordability_end:            {format: iso, basis: RECORDED, event: AFFORDABILITY_PERIOD_END}
    contract_expiration:          {format: iso, basis: RECORDED, event: HAP_EXPIRATION, confidence: 0.90}
    recapture_start:              {format: iso, basis: RECORDED}
    recapture_end:                {format: iso, basis: RECORDED, event: GRANT_RECAPTURE_END}
    senior_maturity:              {format: iso, basis: REPORTED, event: LOAN_MATURITY}
    notice_received_date:         {format: iso, basis: RECORDED}
    qc_request_date:              {format: iso, basis: RECORDED}
    qc_request_complete_date:     {format: iso, basis: RECORDED}
    third_party_offer_mailed_date: {format: iso, basis: RECORDED}
    third_party_offer_received_date: {format: iso, basis: RECORDED}
    qp_offer_delivered_date:      {format: iso, basis: RECORDED}
    usda_prepay_request_date:     {format: iso, basis: RECORDED}
    rad_chap_date:                {format: iso, basis: RECORDED}
    section_18_application_date:  {format: iso, basis: RECORDED}
    last_inspection_date:         {format: iso, basis: RECORDED}
    last_8823_date:               {format: iso, basis: RECORDED}
    last_reac_date:               {format: iso, basis: RECORDED}
    as_of:                        {format: iso}
  numeric:
    float_columns: ["upb", "accrued_interest", "rate", "recapture_amount", "shared_appreciation_pct", "senior_upb"]
    int_columns: ["units_assisted", "open_findings_count", "last_reac_score", "lien_position"]
  enums:
    covenant_status: [current, watch, default, cured, released]
    payment_type: [hard_pay, residual_receipts, deferred, forgivable]
    recapture_type: [home_recapture, home_resale, home_rental_repayment, cdbg, shared_appreciation, none]
    recapture_method: [full, prorata_reducing, forgiveness_schedule, cdbg_fmv_share, none]
    program: [LIHTC_9, LIHTC_4, HAP, PRAC, RAC, PAC, PBV, HUD_INSURED, HUD_236, HUD_202_811, USDA_515, HOME, CDBG, OAHTC, GHAP, HDGP, LIFT, HTF, OTHER_OHCS, LOCAL_REG, PHB_LOAN, TIF, LEVY, IH_SET_ASIDE]
  optional: [grant_id, am_officer, property_name, address, zip, county_fips, parcel_id, senior_lien_type, shared_appreciation_pct, ohcs_property_key]
ohcs_affordable_housing_inventory:
  match_columns: ["Property Name", "LATEST_Expiration_Date", "Financial_Closing_Date"]
  encoding: utf-8-sig
  key: ["Property Name", "Address"]
  dates:
    Financial_Closing_Date:     {format: "%d/%m/%Y", basis: REPORTED}
    Compliance_Start_Date:      {format: "%m/%d/%Y", basis: REPORTED}
    LIHTC_4_Expiration_Date:    {format: "%m/%d/%Y", basis: REPORTED, event: LIHTC_EXTENDED_USE_END, program: LIHTC_4}
    LIHTC_9_Expiration_Date:    {format: "%m/%d/%Y", basis: REPORTED, event: LIHTC_EXTENDED_USE_END, program: LIHTC_9}
    HOME_Expiration_Date:       {format: "%m/%d/%Y", basis: REPORTED, event: SOFT_PROGRAM_END, program: HOME}
    OAHTC_Expiration_Date:      {format: "%m/%d/%Y", basis: REPORTED, event: SOFT_PROGRAM_END, program: OAHTC}
    GHAP_Expiration_Date:       {format: "%m/%d/%Y", basis: REPORTED, event: SOFT_PROGRAM_END, program: GHAP}
    HDGP_Expiration_Date:       {format: "%m/%d/%Y", basis: REPORTED, event: SOFT_PROGRAM_END, program: HDGP}
    LIFT_Expiration_Date:       {format: "%m/%d/%Y", basis: REPORTED, event: SOFT_PROGRAM_END, program: LIFT}
    HTF_Expiration_Date:        {format: "%m/%d/%Y", basis: REPORTED, event: SOFT_PROGRAM_END, program: HTF}
    Other_OHCS_Expiration_Date: {format: "%m/%d/%Y", basis: REPORTED, event: SOFT_PROGRAM_END, program: OTHER_OHCS}
    HUD_MF_Expiration_Date:     {format: "%m/%d/%Y", basis: REPORTED, event: HAP_EXPIRATION, confidence: 0.70}
    USDA_RD_Expiration_Date:    {format: "%Y %b %d %I:%M:%S %p", basis: REPORTED, event: USDA_515_MATURITY}
    LATEST_Expiration_Date:     {format: "%m/%d/%Y", basis: REPORTED, event: REGULATORY_LATEST_END, recompute_if_blank: max_of_components}
  derived_events:
    LIHTC_COMPLIANCE_END:        {from: Compliance_Start_Date, add_years: 15, basis: DERIVED, window_months: 12}
    LOAN_MATURITY:               {from: Financial_Closing_Date, add_years: 15, add_years_if_program: {LIHTC_4: 17}, basis: PROXY, window_months: 36, derivation: "Financial_Closing_Date + 15y mini-perm (17y 4% bond); opt-in with --include-proxies"}
    PRESERVATION_NOTICE_WINDOW:  {anchor: withdrawal_anchor_date, windows: [[36, 30], [30, 24]], basis: DERIVED, min_units: 5, require_programs: push_covered,
                                  due_dates: {PUSH_WINDOW_PREP: 36, PUSH_FIRST_NOTICE_DUE: 30, PUSH_SECOND_NOTICE_DUE: 24},
                                  derivation: "withdrawal_anchor_date - 36..30 (internal prep window; no statutory 36-month start found) / 30..24 months (owner notice no sooner than 30 and at least 24 months before withdrawal per OAR 813-115-0030 summary; ORS 456.260 text unread)"}
  validations:
    - {rule: month_le_12, on_fail: "Rejected — Out of Range"}
    - {rule: latest_equals_max_components, whitelist: ["Casa Sonada 4", "Riverside Terrace"], on_fail: "Verify — Conflicting Sources"}
    - {rule: expiration_ge_compliance_start, when_both_present: true, on_fail: "Verify — Conflicting Sources"}
    - {rule: compliance_start_within_months_after_closing, months: 36, when_both_present: true, on_fail: "Verify — Conflicting Sources"}
  normalize:
    County: title_case
    City: {title_case: true, typo_map: {Portalnd: Portland}}
    "Owner Type": {title_case: true, map: {Profit: For-Profit, "Non-profit": Non-Profit, Government: Government}, blank: infer_from_owner_name}
    "Property Type": {drop_values: ["0", "ERROR: #N/A"]}
  numeric:
    int_columns: ["Rehab Year", "Year Built", "Total Units", "Total_30_AMI_Units", "Total_40_AMI_Units", "Total_50_AMI_Units",
                  "Total_60_AMI_Units", "Total_80_AMI_Units", "Market_Rate_Units", "Rental_Assistance_Count", "PSH_Units",
                  "Total_SRO_Units", "Total_Efficiency_Units", "Total_1_BR_Units", "Total_2_BR_Units", "Total_3_BR_Units", "Total_4Plus_BR_Units",
                  "No_Accessible_Units"]
  lead_columns: {PSH_Units: psh_units_at_risk, "OHCS Funded?": ohcs_funded, "Scattered/Single Site": site_type}
  filters:
    exclude: {Status: ["In Development"]}
  value_proxy: {fallback: none, rent_limits_file: rent-limits.json}
  county_fips: {Multnomah: "41051", Washington: "41067", Clackamas: "41005", Columbia: "41009", Yamhill: "41071"}
hud_fhasl_active:
  match_columns: ["HUD Project Number", "Maturity Date", "Section of the Act"]
  dates: {"Initial Endorsement Date": {format: excel_date}, "Final Endorsement Date": {format: excel_date}, "Maturity Date": {format: excel_date, basis: RECORDED, event: LOAN_MATURITY}}
  derived_events: {PREPAY_WINDOW_OPEN: {from: "Final Endorsement Date", add_years: 10, basis: DERIVED, window_months: 6}}
  soa_affordable_codes: ["236", "221(d)(3)", "202", "811", "542"]
hud_mf_assistance_sec8:
  match_columns: ["property_id", "tracs_overall_expiration_date"]
  dates: {tracs_effective_date: {format: excel_date}, tracs_overall_expiration_date: {format: excel_date, basis: REPORTED, event: HAP_EXPIRATION, confidence: 0.70}}
ohcs_push_forecast:
  match_columns: ["Property Name", "Preservation Status"]
  dates: {"Expiration Date": {format: "%m/%d/%Y", basis: REPORTED, event: REGULATORY_LATEST_END}, "Notice Date": {format: "%m/%d/%Y", basis: RECORDED}}
  status_map:
    notice_received: ["First Notice Received", "Second Notice Received", "Notice Received", "Opt-Out Notice Received", "Opt Out Notice Received", "Owner Notice Received"]
    second_notice: ["Second Notice Received"]
    preserved: ["Preserved", "Resyndicated", "Extended", "Stabilized", "Transferred to Nonprofit"]
    monitoring: ["Monitoring", "At Risk", "Watch"]
hud_reac_scores:
  match_columns: ["property_id", "inspection_score"]
  dates: {inspection_date: {format: iso, basis: REPORTED}}
"""

DEFAULT_MARKET_PARAMS: Dict[str, Any] = {
    "_note": "Embedded fallback mirroring references/sources/oregon-portland/market-params.json. Pack file wins when present. Every statutory figure is unverified in this build (verify: true).",
    "cap_rate_affordable": {"value": 0.0675, "as_of": "2026-10", "source": "Class C + 100 bp house assumption", "verify": True},
    "vacancy": {"value": 0.071, "as_of": "2026-Q2", "source": "Kidder Mathews (snippet, verified_live=false)"},
    "vacancy_hap_units": {"value": 0.03, "as_of": "2026", "source": "house assumption for assisted units"},
    "opex_per_unit_regulated": {"value": 8700, "as_of": "2026", "source": "OHCS FY24 $8,198 inflated"},
    "opex_ratio_affordable": {"value": 0.50, "as_of": "2026", "source": "house assumption for regulated stock"},
    "dscr_floor_affordable": {"value": 1.15, "as_of": "2026-05", "source": "sizing-lihtc-permanent-debt"},
    "senior_dscr_floor": {"value": 1.15, "as_of": "2026-05", "source": "sizing-lihtc-permanent-debt"},
    "ltv_max_affordable": {"value": 0.80, "as_of": "2026-05", "source": "sizing-lihtc-permanent-debt"},
    "debt_yield_floor": {"value": 0.08, "as_of": "2026-05", "source": "multifamily-benchmarks Quick Reference"},
    "ust10": {"value": 0.0415, "as_of": "placeholder", "source": "verify before use", "verify": True},
    "senior_rate_default": {"value": 0.0590, "as_of": "placeholder", "source": "ust10 + 175 bp house assumption", "verify": True},
    "av_is_market": {"value": False, "as_of": "n/a", "source": "Oregon Measure 50"},
    "multco_recorder_image_fee": {"value": 3.75, "as_of": "2026", "source": "Multnomah County Recording (snippet)", "verify": True},
    "benchmarks_source": {"value": "multifamily-benchmarks Quick Reference 2026-05", "as_of": "2026-05", "source": "sibling skill"},
    # agency product terms and statutory clocks (verify)
    "recap_loan_rate": {"value": 0.0, "as_of": "2026", "source": "0% recap convention", "verify": True},
    "rehab_loan_rate": {"value": 0.01, "as_of": "2026", "source": "placeholder", "verify": True},
    "records_request_response_days": {"value": 30, "as_of": "2026", "source": "OAR 813-115-0050 (qualified purchaser access to records); 30-day response period not found in rule text (verify ORS 456.262(6)-(7))", "verify": True},
    "records_request_after_notice_days": {"value": 10, "as_of": "2026", "source": "internal target", "verify": False},
    "rofr_match_days": {"value": 30, "as_of": "2026", "source": "ORS 456.263 (verify)", "verify": True},
    "rofr_duration_months_after_termination": {"value": 24, "as_of": "2026", "source": "ORS 456.262: ROFR expires 24 months after the withdrawal date (verify)", "verify": True},
    "rofr_recordable_days_after_offer": {"value": 30, "as_of": "2026", "source": "ORS 456.262: qualified purchaser may record a Notice of ROFR after 30 days from delivering its offer (verify)", "verify": True},
    "push_program_coverage_verified": {"value": False, "as_of": "2026", "source": "OAR 813-115-0010 program list not read; HOME-only / LIHTC-only rows get Verify — PuSH Coverage until true", "verify": True},
    "qc_response_months": {"value": 12, "as_of": "2026", "source": "IRC 42(h)(6)(I)", "verify": True},
    "hap_optout_notice_months": {"value": 12, "as_of": "2026", "source": "42 U.S.C. 1437f(c)(8); 24 CFR 402.8", "verify": True},
    "hap_optout_package_days": {"value": 120, "as_of": "2026", "source": "Section 8 Renewal Policy Guide ch. 11 (verify)", "verify": True},
    "push_first_notice_months": {"value": 30, "as_of": "2026", "source": "ORS 456.260 / OAR 813-115-0030: owner notice no sooner than 30 months before withdrawal; ORS 456.262 designee trigger (verify; (1)/(2) split unread)", "verify": True},
    "push_second_notice_months": {"value": 24, "as_of": "2026", "source": "ORS 456.260 / OAR 813-115-0030: owner notice at least 24 months before withdrawal (verify)", "verify": True},
    "push_window_prep_months": {"value": 36, "as_of": "2026", "source": "internal prep date (anchor - 36 months); no statutory basis found for a 36-month owner-notice start (rule text reads no sooner than 30 / at least 24 months)", "verify": True},
    "tenant_notice_months": {"value": [36, 30], "as_of": "2026", "source": "SB 973 (2025) (verify)", "verify": True},
    "sb973_operative_restriction_date": {"value": "2028-07-01", "as_of": "2026", "source": "SB 973 phase-in as noted in v2; operative date unconfirmed", "verify": True},
    "usda_public_body_offer_days": {"value": 180, "as_of": "2026", "source": "7 CFR 3560.659 (verify)", "verify": True},
    "inspection_cadence_home": {"value": {"1-4": 36, "5-25": 24, "26+": 12}, "as_of": "2026", "source": "24 CFR 92.504(d) (verify)", "verify": True},
    "inspection_cadence_lihtc": {"value": 36, "as_of": "2026", "source": "26 CFR 1.42-5 (verify)", "verify": True},
}

DEFAULT_AGENCY_PROFILES: Dict[str, Dict[str, Any]] = {
    "hfa": {
        "agency_name": "Oregon Housing and Community Services", "roles": ["lender", "grantor", "qualified_purchaser", "qc_administrator", "pbca"],
        "book_sources": ["ohcs_funded_flag", "agency_servicing_extract"], "expected_book_flag": "ohcs_funded",
        "is_qualified_purchaser": True, "is_designee": False, "receives_push_notice": True, "administers_qc": True, "is_pbca": True,
        "self_owner_tokens": [], "recapture_methods": {"HOME": "full", "HOME_HOMEBUYER": "prorata_reducing", "CDBG": "cdbg_fmv_share", "HTF": "full", "default": "full"},
        "statutory_cites": ["ORS 456.250-.265", "OAR 813-115", "IRC 42(h)(6)", "24 CFR 402.8"], "pii_level_public_packet": "public_packet",
        "mandate_file": "mandate.json", "board_totals_variant": "loan_book",
    },
    "city_housing": {
        "agency_name": "Portland Housing Bureau", "roles": ["lender", "grantor", "affected_local_government", "qualified_purchaser"],
        "book_sources": ["phb_loan_extract"], "expected_book_flag": None,
        "is_qualified_purchaser": True, "is_designee": False, "receives_push_notice": True, "administers_qc": False, "is_pbca": False,
        "self_owner_tokens": [], "recapture_methods": {"HOME": "full", "HOME_HOMEBUYER": "prorata_reducing", "CDBG": "cdbg_fmv_share", "default": "full"},
        "statutory_cites": ["ORS 456.250-.265", "24 CFR 92.252", "24 CFR 570.505"], "pii_level_public_packet": "public_packet",
        "mandate_file": "mandate.json", "board_totals_variant": "loan_book",
    },
    "county": {
        "agency_name": "Multnomah / Washington / Clackamas County housing offices", "roles": ["lender", "grantor", "affected_local_government", "qualified_purchaser"],
        "book_sources": ["home_cdbg_levy_extract"], "expected_book_flag": None,
        "is_qualified_purchaser": True, "is_designee": False, "receives_push_notice": True, "administers_qc": False, "is_pbca": False,
        "self_owner_tokens": [], "recapture_methods": {"HOME": "full", "HOME_HOMEBUYER": "prorata_reducing", "CDBG": "cdbg_fmv_share", "default": "full"},
        "statutory_cites": ["ORS 456.250-.265", "24 CFR 92.252"], "pii_level_public_packet": "public_packet",
        "mandate_file": "mandate.json", "board_totals_variant": "loan_book",
    },
    "pha_am": {
        "agency_name": "Home Forward", "roles": ["owner", "pbv_administrator"],
        "book_sources": ["pha_owned_assets", "pbv_contracts"], "expected_book_flag": None,
        "is_qualified_purchaser": False, "is_designee": False, "receives_push_notice": False, "administers_qc": False, "is_pbca": False,
        "self_owner_tokens": ["Home Forward", "Housing Authority of Portland"], "recapture_methods": {"default": "full"},
        "statutory_cites": ["RAD Notice H-2019-09 / PIH-2019-23 REV-4", "24 CFR part 970"], "pii_level_public_packet": "public_packet",
        "mandate_file": "mandate.json", "board_totals_variant": "owned_assets",
    },
    "cdbg_home": {
        "agency_name": "Portland Consortium HOME/CDBG participating jurisdiction", "roles": ["grantor", "pj"],
        "book_sources": ["home_cdbg_affordability_extract"], "expected_book_flag": "home_cdbg_programs",
        "is_qualified_purchaser": False, "is_designee": False, "receives_push_notice": False, "administers_qc": False, "is_pbca": False,
        "self_owner_tokens": [], "recapture_methods": {"HOME": "full", "HOME_HOMEBUYER": "prorata_reducing", "CDBG": "cdbg_fmv_share", "HTF": "full", "default": "full"},
        "statutory_cites": ["24 CFR 92.252(e)", "24 CFR 92.254(a)(5)", "24 CFR 92.504(d)", "24 CFR 570.505"], "pii_level_public_packet": "public_packet",
        "mandate_file": "mandate.json", "board_totals_variant": "loan_book",
    },
}

DEFAULT_MANDATE: Dict[str, Any] = {
    "_note": "Embedded fallback mirroring references/sources/oregon-portland/mandate.json; every product is a placeholder (verified_live false).",
    "agency_profile_defaults": {"hfa": ["ohcs_preservation_nofa", "lihtc_4pct_gap", "zero_pct_rehab_recap"], "city_housing": ["phb_preservation_rfp", "metro_bond_acquisition"],
                                "county": ["metro_bond_acquisition"], "pha_am": [], "cdbg_home": ["phb_preservation_rfp"]},
    "products": [
        {"product_id": "ohcs_preservation_nofa", "name": "OHCS centralized preservation NOFA (LIFT / OAHTC / GHAP / HOME / HTF / PSH bonds)", "agency_owner": "nofa_program_manager",
         "status": "rolling", "eligible_programs": [], "eligible_owner_types": [], "ineligible_owner_types": [], "min_units": 5, "max_per_unit": None,
         "application_window": None, "new_covenant_years": 60, "source": "OHCS 2025 Affordable Rental Housing NOFA (snippet)", "verified_live": False},
        {"product_id": "lihtc_4pct_gap", "name": "4% LIHTC / tax-exempt bond gap loan for recapitalization", "agency_owner": "nofa_program_manager",
         "status": "rolling", "eligible_programs": ["LIHTC_9", "LIHTC_4", "HAP", "PRAC", "HUD_236", "HUD_202_811", "USDA_515", "OTHER_OHCS", "OAHTC", "GHAP", "HDGP", "HOME", "HTF", "LIFT"],
         "eligible_owner_types": [], "ineligible_owner_types": [], "min_units": 20, "max_per_unit": None, "application_window": None, "new_covenant_years": 30,
         "source": "placeholder", "verified_live": False},
        {"product_id": "zero_pct_rehab_recap", "name": "0% rehab / recapitalization loan for mission sponsors", "agency_owner": "nofa_program_manager",
         "status": "open", "eligible_programs": [], "eligible_owner_types": ["nonprofit", "lihtc_partnership_nonprofit_gp", "housing_authority", "government"],
         "ineligible_owner_types": [], "min_units": 5, "max_per_unit": 75000, "application_window": None, "new_covenant_years": 30, "source": "placeholder", "verified_live": False},
        {"product_id": "phb_preservation_rfp", "name": "PHB Affordable Housing Preservation RFP (CDBG / HOME / PCEF)", "agency_owner": "nofa_program_manager",
         "status": "closed", "eligible_programs": [], "eligible_owner_types": ["nonprofit", "lihtc_partnership_nonprofit_gp"], "ineligible_owner_types": [],
         "min_units": 5, "max_per_unit": None, "application_window": {"open": "2025-03-19", "close": "2025-05-30"}, "new_covenant_years": 60,
         "source": "PHB Spring 2025 Preservation RFP (snippet)", "verified_live": False},
        {"product_id": "metro_bond_acquisition", "name": "Metro Measure 26-199 acquisition / preservation funds", "agency_owner": "nofa_program_manager",
         "status": "rolling", "eligible_programs": [], "eligible_owner_types": [], "ineligible_owner_types": [], "min_units": 5, "max_per_unit": None,
         "application_window": None, "new_covenant_years": 60, "source": "Metro bond local implementation strategy (snippet)", "verified_live": False},
        {"product_id": "noah_ohaf_bridge", "name": "NOAH Oregon Housing Acquisition Fund bridge (external)", "agency_owner": "nofa_program_manager",
         "status": "rolling", "eligible_programs": [], "eligible_owner_types": ["nonprofit", "lihtc_partnership_nonprofit_gp", "housing_authority", "government"],
         "ineligible_owner_types": [], "min_units": 5, "max_per_unit": None, "application_window": None, "new_covenant_years": None, "source": "external partner", "verified_live": False},
        {"product_id": "usda_mpr", "name": "USDA Multifamily Preservation and Revitalization (external)", "agency_owner": "rd_state_office",
         "status": "rolling", "eligible_programs": ["USDA_515"], "eligible_owner_types": [], "ineligible_owner_types": [], "min_units": 1, "max_per_unit": None,
         "application_window": None, "new_covenant_years": 20, "source": "external partner", "verified_live": False},
    ],
}

# --------------------------------------------------------------------------- loaders
HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
DEFAULT_PACK_DIR = os.path.join(SKILL_ROOT, "references", "sources", "oregon-portland")
DEFAULT_SCORING_DIR = os.path.join(SKILL_ROOT, "references", "scoring")


def _load_yaml(path: str):
    if yaml is None:
        raise RuntimeError("pyyaml is required (pip install pyyaml)")
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_dataset_schemas(pack_dir: Optional[str] = None) -> Dict[str, Any]:
    """Return dataset schemas from the pack's dataset-schemas.yaml (default pack when none given), else the embedded
    default. A pack file that lacks a block the scripts need is completed from the embedded copy."""
    base = yaml.safe_load(DEFAULT_DATASET_SCHEMAS_YAML) if yaml is not None else {}
    for d in (pack_dir, DEFAULT_PACK_DIR):
        if not d:
            continue
        path = os.path.join(d, "dataset-schemas.yaml")
        if os.path.exists(path) and yaml is not None:
            data = _load_yaml(path)
            if isinstance(data, dict) and data:
                for k, v in base.items():
                    data.setdefault(k, v)
                return data
    if yaml is None:
        raise RuntimeError("pyyaml is required to parse dataset schemas (pip install pyyaml)")
    return base


def clean_numeric(value, as_int: bool = True):
    """'2,021' -> 2021; '35.0' -> 35; '$4,200,000' -> 4200000.0; blank/NaN/text -> None."""
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value) if as_int else float(value)
    s = str(value).strip().replace(",", "").replace("$", "")
    if not s or s.lower() in ("nan", "none", "nat", "null"):
        return None
    try:
        f = float(s)
    except ValueError:
        return None
    if f != f:
        return None
    if as_int:
        return int(round(f)) if abs(f - round(f)) < 1e-9 else f
    return f


def apply_numeric_block(df, spec: Dict[str, Any]):
    num = spec.get("numeric") or {}
    for col in num.get("int_columns", []) or []:
        if col in df.columns:
            df[col] = df[col].map(lambda v: clean_numeric(v, True))
    for col in num.get("float_columns", []) or []:
        if col in df.columns:
            df[col] = df[col].map(lambda v: clean_numeric(v, False))
    return df


def _load_json_first(paths: List[Optional[str]], default: Dict[str, Any]) -> Dict[str, Any]:
    for path in paths:
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict) and data:
                return data
    return default


def load_market_params(pack_dir: Optional[str] = None, explicit_path: Optional[str] = None) -> Dict[str, Any]:
    data = _load_json_first([explicit_path, os.path.join(pack_dir, "market-params.json") if pack_dir else None,
                             os.path.join(DEFAULT_PACK_DIR, "market-params.json")], DEFAULT_MARKET_PARAMS)
    for k, v in DEFAULT_MARKET_PARAMS.items():
        data.setdefault(k, v)
    return data


def param(params: Dict[str, Any], key: str, default: Any = None) -> Any:
    v = params.get(key, default)
    if isinstance(v, dict) and "value" in v:
        return v["value"]
    return v


def load_agency_profiles(pack_dir: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """agency-profiles.yaml from the pack (default pack when none given), completed from the embedded defaults."""
    out = {k: dict(v) for k, v in DEFAULT_AGENCY_PROFILES.items()}
    for d in (pack_dir, DEFAULT_PACK_DIR):
        if not d:
            continue
        path = os.path.join(d, "agency-profiles.yaml")
        if os.path.exists(path) and yaml is not None:
            data = _load_yaml(path)
            profiles = data.get("profiles", data) if isinstance(data, dict) else {}
            for k, v in (profiles or {}).items():
                if isinstance(v, dict) and k in AGENCY_PROFILES:
                    merged = dict(out.get(k, {}))
                    merged.update(v)
                    out[k] = merged
            break
    return out


def agency_profile(name: str, pack_dir: Optional[str] = None) -> Dict[str, Any]:
    if name not in AGENCY_PROFILES:
        raise ValueError(f"unknown agency_profile {name}; expected one of {AGENCY_PROFILES}")
    p = dict(load_agency_profiles(pack_dir)[name])
    p["profile"] = name
    p["routes_enabled"] = routes_enabled_for(p)
    return p


def routes_enabled_for(p: Dict[str, Any]) -> List[str]:
    out = []
    for r in ROUTES:
        if r == "qc_admin" and not p.get("administers_qc"):
            continue
        if r == "designee_rofr" and not (p.get("is_qualified_purchaser") or p.get("is_designee")):
            continue
        if r == "optout_response" and not (p.get("is_pbca") or p.get("receives_push_notice")):
            continue
        if r == "notice_compliance" and not (p.get("receives_push_notice") or p.get("is_qualified_purchaser")):
            continue
        out.append(r)
    return out


def load_mandate(pack_dir: Optional[str] = None, explicit_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """mandate.json: explicit path > pack > default pack > embedded default. `explicit_path="none"` disables the mandate (mandate_fit no_mandate_file)."""
    if explicit_path and str(explicit_path).strip().lower() == "none":
        return None
    for path in [explicit_path, os.path.join(pack_dir, "mandate.json") if pack_dir else None, os.path.join(DEFAULT_PACK_DIR, "mandate.json")]:
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict) and data.get("products"):
                return data
    return DEFAULT_MANDATE if explicit_path != "none" else None


def detect_schema(columns: List[str], schemas: Dict[str, Any]) -> Optional[str]:
    """Return the schema id whose match_columns are all present and, when declared, at least one column of every
    match_any group is present. Specific schemas (more match requirements) win over generic ones."""
    cols = set(c.strip() for c in columns)
    best, best_n = None, -1
    for sid, spec in schemas.items():
        if not isinstance(spec, dict):
            continue
        req = spec.get("match_columns") or []
        if not req or not all(c in cols for c in req):
            continue
        groups = [(g.get("any") or []) if isinstance(g, dict) else list(g) for g in (spec.get("match_any") or [])]
        if any(not any(c in cols for c in grp) for grp in groups):
            continue
        n = len(req) + len(groups)
        if n > best_n:
            best, best_n = sid, n
    return best
