"""Shared vocabulary for off-market-deal-finder v2.

Every enum string here is the exact string used in references/pipeline-contract.md,
the scoring JSON files and the output workbook. Scripts import from this module rather
than retyping literals so a typo cannot silently create a new category.

The default dataset schema and market parameters embedded here mirror
references/sources/oregon-portland/dataset-schemas.yaml and market-params.json. When a
jurisdiction pack directory is supplied (`--pack`), the pack files win; the embedded
copies exist so the scripts run before the pack is written and so tests are hermetic.
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
ASSET_CLASSES = ["sfr_small_res", "market_rate_mf", "affordable_regulated"]
QUERY_TYPES = ["distress", "maturity", "regulatory_expiry", "all"]
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
]
FLAG_AMBIGUOUS = "Verify — Ambiguous"
FLAG_CONFLICT = "Verify — Conflicting Sources"
FLAG_ANCHOR = "Needs Anchor Date"
FLAG_MISSING_SOURCE = "Missing Source — Request Document"
FLAG_REJECTED = "Rejected — Out of Range"
FLAG_NO_FORMAT = "No Format Declared"

EVENT_FAMILIES = ["DEBT", "REGULATORY", "HARD_DISTRESS", "TAX_LIEN", "PHYSICAL", "OWNERSHIP", "OPERATING"]
DIRECTIONS = ["PRESSURE", "SUPPRESSION", "ROUTING"]

URGENCY_BANDS = [  # (band, lo_months_inclusive, hi_months_exclusive, timing_fraction)
    ("CRITICAL", 0, 12, 1.00),
    ("URGENT", 12, 24, 0.75),
    ("APPROACHING", 24, 36, 0.50),
    ("MONITOR", 36, 60, 0.25),
    ("SCHEDULED", 60, None, 0.00),
]

OWNER_TYPES = [
    "individual_occupant", "individual_absentee", "trust_estate", "single_asset_llc", "regional_operator",
    "institutional", "lihtc_partnership_forprofit_gp", "lihtc_partnership_nonprofit_gp", "nonprofit",
    "housing_authority", "government", "lender_reo_receiver", "unknown",
]
CONTACT_GRADES = ["A", "B", "C"]
ROUTES = ["acquisition", "partnership_preservation", "lender_counterparty", "assumption_play", "watch", "excluded"]
TIERS = ["A", "B", "C", "WATCH", "EXCLUDED"]
TIER_MIN_SCORE = {"A": 70, "B": 50, "C": 30}
BUYER_PROFILES = ["principal", "wholesaler", "nonprofit_preservation", "qualified_purchaser"]
LENDER_TYPES = [
    "hud_fha", "fannie_dus", "freddie_k_sb", "cmbs", "bank_cu", "life_co", "debt_fund_bridge", "usda_rd",
    "state_soft", "local_soft", "hecm", "seller_private", "unknown",
]
PROGRAMS = [
    "LIHTC_9", "LIHTC_4", "HAP", "PRAC", "RAC", "PAC", "HUD_INSURED", "HUD_236", "HUD_202_811", "USDA_515",
    "HOME", "OAHTC", "GHAP", "HDGP", "LIFT", "HTF", "OTHER_OHCS", "LOCAL_REG", "IH_SET_ASIDE",
]
HUD_CONTRACT_TO_PROGRAM = {
    "Housing Assistance Payment": "HAP",
    "Project Rental Assistance Contract": "PRAC",
    "Rental Assistance Contract": "RAC",
    "Project Assistance Contract": "PAC",
}

# --------------------------------------------------------------------------- event taxonomy
# event_type -> (family, direction). Names align to critical-dates-tracker's Loan/Financing and
# Regulatory/Compliance categories so the two skills' outputs join cleanly.
EVENT_TAXONOMY: Dict[str, Dict[str, str]] = {
    # DEBT
    "LOAN_MATURITY": {"family": "DEBT", "direction": "PRESSURE"},
    "IO_EXPIRATION": {"family": "DEBT", "direction": "PRESSURE"},
    "PREPAY_WINDOW_OPEN": {"family": "DEBT", "direction": "PRESSURE"},
    "RATE_CAP_EXPIRY": {"family": "DEBT", "direction": "PRESSURE"},
    "LOAN_MODIFIED": {"family": "DEBT", "direction": "PRESSURE"},
    "REFINANCE_CLOSED": {"family": "DEBT", "direction": "SUPPRESSION"},
    "HUD_DIRECT_LOAN_MATURITY": {"family": "DEBT", "direction": "PRESSURE"},
    "USDA_515_MATURITY": {"family": "DEBT", "direction": "PRESSURE"},
    "USDA_515_PREPAY_ELIGIBLE": {"family": "DEBT", "direction": "PRESSURE"},
    "USDA_EXIT_PROJECTED": {"family": "DEBT", "direction": "PRESSURE"},
    "SOFT_LOAN_MATURITY": {"family": "DEBT", "direction": "PRESSURE"},
    "SUPPRESS_UNTIL": {"family": "DEBT", "direction": "SUPPRESSION"},
    # HARD_DISTRESS
    "SPECIAL_SERVICING": {"family": "HARD_DISTRESS", "direction": "PRESSURE"},
    "MATURED_BALLOON": {"family": "HARD_DISTRESS", "direction": "PRESSURE"},
    "UCC_MEZZ_PLEDGE": {"family": "HARD_DISTRESS", "direction": "PRESSURE"},
    "UCC_ART9_SALE": {"family": "HARD_DISTRESS", "direction": "PRESSURE"},
    "NOD_RECORDED": {"family": "HARD_DISTRESS", "direction": "PRESSURE"},
    "SUCCESSOR_TRUSTEE_APPOINTED": {"family": "HARD_DISTRESS", "direction": "PRESSURE"},
    "OFAP_CERT_RECORDED": {"family": "HARD_DISTRESS", "direction": "PRESSURE"},
    "NOTS_RECORDED": {"family": "HARD_DISTRESS", "direction": "PRESSURE"},
    "TRUSTEE_SALE_EARLIEST": {"family": "HARD_DISTRESS", "direction": "PRESSURE"},
    "CURE_DEADLINE": {"family": "HARD_DISTRESS", "direction": "PRESSURE"},
    "NOD_RESCISSION": {"family": "HARD_DISTRESS", "direction": "SUPPRESSION"},
    "TRUSTEES_DEED": {"family": "HARD_DISTRESS", "direction": "ROUTING"},
    "JUDICIAL_FORECLOSURE_FILED": {"family": "HARD_DISTRESS", "direction": "PRESSURE"},
    "LIS_PENDENS": {"family": "HARD_DISTRESS", "direction": "PRESSURE"},
    "RECEIVER_APPOINTED": {"family": "HARD_DISTRESS", "direction": "ROUTING"},
    "BANKRUPTCY_FILED": {"family": "HARD_DISTRESS", "direction": "ROUTING"},
    "CH13_DISMISSED": {"family": "HARD_DISTRESS", "direction": "PRESSURE"},
    # OPERATING
    "WATCHLIST": {"family": "OPERATING", "direction": "PRESSURE"},
    "REAC_SCORE": {"family": "OPERATING", "direction": "PRESSURE"},
    "TAX_EXEMPTION_LOST": {"family": "OPERATING", "direction": "PRESSURE"},
    "STABILIZATION_AWARD": {"family": "OPERATING", "direction": "PRESSURE"},
    "OCCUPANCY_DROP": {"family": "OPERATING", "direction": "PRESSURE"},
    "LISTING_WITHDRAWN": {"family": "OPERATING", "direction": "PRESSURE"},
    "MGMT_CHANGE": {"family": "OPERATING", "direction": "PRESSURE"},
    "INSURANCE_NONRENEWAL_CONFIRMED": {"family": "OPERATING", "direction": "PRESSURE"},
    # REGULATORY
    "LIHTC_COMPLIANCE_END": {"family": "REGULATORY", "direction": "PRESSURE"},
    "LIHTC_EXTENDED_USE_END": {"family": "REGULATORY", "direction": "PRESSURE"},
    "QC_ELIGIBILITY": {"family": "REGULATORY", "direction": "PRESSURE"},
    "HAP_EXPIRATION": {"family": "REGULATORY", "direction": "PRESSURE"},
    "HAP_OPTOUT_NOTICE_DEADLINE": {"family": "REGULATORY", "direction": "PRESSURE"},
    "PRESERVATION_NOTICE_WINDOW": {"family": "REGULATORY", "direction": "PRESSURE"},
    "PRESERVATION_NOTICE_RECEIVED": {"family": "REGULATORY", "direction": "PRESSURE"},
    "ROFR_RECORDED": {"family": "REGULATORY", "direction": "ROUTING"},
    "SOFT_PROGRAM_END": {"family": "REGULATORY", "direction": "PRESSURE"},
    "REGULATORY_LATEST_END": {"family": "REGULATORY", "direction": "PRESSURE"},
    # OWNERSHIP
    "UNENCUMBERED": {"family": "OWNERSHIP", "direction": "PRESSURE"},
    "PROBATE_FILED": {"family": "OWNERSHIP", "direction": "PRESSURE"},
    "DISSOLUTION_FILED": {"family": "OWNERSHIP", "direction": "PRESSURE"},
    "PARTITION_FILED": {"family": "OWNERSHIP", "direction": "PRESSURE"},
    "ENTITY_ADMIN_DISSOLVED": {"family": "OWNERSHIP", "direction": "PRESSURE"},
    "MANAGER_CHANGE": {"family": "OWNERSHIP", "direction": "PRESSURE"},
    "REGISTERED_AGENT_CHANGE": {"family": "OWNERSHIP", "direction": "PRESSURE"},
    "HECM_ON_RECORD": {"family": "OWNERSHIP", "direction": "PRESSURE"},
    "DOR_DEFERRAL_LIEN": {"family": "OWNERSHIP", "direction": "PRESSURE"},
    "HOLD_YEARS": {"family": "OWNERSHIP", "direction": "PRESSURE"},
    "DEPRECIATION_EXHAUSTED": {"family": "OWNERSHIP", "direction": "PRESSURE"},
    "RECENT_1031_ACQUISITION": {"family": "OWNERSHIP", "direction": "SUPPRESSION"},
    "ABSENTEE_TIER": {"family": "OWNERSHIP", "direction": "PRESSURE"},
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
}
EVENT_TYPES = sorted(EVENT_TAXONOMY)
# Helper deadlines are arithmetic on another event of the same property (notice windows, opt-out deadlines).
# They are never a property's "first" event and are reported on their own line of the calendar header,
# not inside the RECORDED/REPORTED/DERIVED/ESTIMATED/PROXY counts (pipeline-contract.md Section 8).
HELPER_EVENTS = {"PRESERVATION_NOTICE_WINDOW", "HAP_OPTOUT_NOTICE_DEADLINE"}
# REGULATORY_LATEST_END restates a component program end on the same property; the calendar counts it only
# when its date differs from every component (i.e. it carries new information).
ROLLUP_EVENTS = {"REGULATORY_LATEST_END"}
# Programs whose restriction brings a 5+ unit property under Oregon ORS 456.250 (publicly supported housing):
# HUD/USDA rent assistance and OHCS-administered restrictions. Used to gate PRESERVATION_NOTICE_WINDOW.
PUSH_COVERED_PROGRAMS = {"HAP", "PRAC", "RAC", "PAC", "LIHTC_9", "LIHTC_4", "HUD_236", "HUD_202_811", "USDA_515",
                         "HOME", "OAHTC", "GHAP", "HDGP", "LIFT", "HTF", "OTHER_OHCS"}
# Permanent states are not decayed in stacking (shared_adjustments.json decay.permanent_event_types).
PERMANENT_EVENT_TYPES = {"HOLD_YEARS", "DEPRECIATION_EXHAUSTED", "ABSENTEE_TIER", "HECM_ON_RECORD",
                         "DOR_DEFERRAL_LIEN", "ENTITY_ADMIN_DISSOLVED", "UNENCUMBERED"}
# Assessor-derived facts count once in stacking independence.
ASSESSOR_DERIVED = {"HOLD_YEARS", "ABSENTEE_TIER", "TAX_DELINQUENT_YEARS", "DEPRECIATION_EXHAUSTED"}


def family_of(event_type: str) -> str:
    return EVENT_TAXONOMY.get(event_type, {}).get("family", "OPERATING")


def direction_of(event_type: str) -> str:
    return EVENT_TAXONOMY.get(event_type, {}).get("direction", "PRESSURE")


# --------------------------------------------------------------------------- canonical tables
LEAD_COLUMNS: List[str] = [
    "property_id", "property_name", "address", "city", "zip", "county_fips", "county_name", "jurisdiction",
    "geo_modes", "geo_grade", "lat", "lon", "asset_class", "status", "units", "year_built", "rehab_year",
    "property_type", "programs", "hud_contract", "ami_30_60_units", "ami_80_units", "market_rate_units",
    "rental_assistance_units", "owner_name", "owner_type", "owner_archetype", "developer_name", "manager_name",
    "decision_maker_name", "decision_maker_role", "dm_source", "contact_grade",
    "first_debt_event_type", "first_debt_event_date", "first_debt_months_out", "first_debt_basis", "first_debt_source",
    "first_reg_event_type", "first_reg_event_date", "first_reg_months_out", "first_reg_basis", "first_reg_source",
    "events_in_horizon", "est_value", "value_source", "est_noi", "noi_source", "est_loan_balance", "balance_basis",
    "est_ltv", "est_dscr_refi", "refi_gap_pct", "equity_cushion_pct", "assumable_debt", "signals", "verify_flags",
    "score_raw", "motivation_score", "tier", "route", "outreach_angle", "outreach_template", "compliance_gates",
    "verify_before_outreach", "next_action", "source_vintages", "as_of_date",
]

EVENT_COLUMNS: List[str] = [
    "event_id", "property_id", "event_type", "event_family", "direction", "event_date", "months_out", "urgency_band",
    "basis", "confidence", "source", "source_vintage", "derivation", "program", "detail", "value", "verify_flag",
    "alt_dates", "window_start", "window_end", "status", "event_date_quality",
]

REJECT_COLUMNS = ["property_key", "property_id", "column", "raw_value", "reason", "flag", "alt_dates"]

# --------------------------------------------------------------------------- default dataset schemas
DEFAULT_DATASET_SCHEMAS_YAML = r"""
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
    LOAN_MATURITY:               {from: Financial_Closing_Date, add_years: 15, add_years_if_program: {LIHTC_4: 17}, basis: PROXY, window_months: 36, derivation: "Financial_Closing_Date + 15y mini-perm (17y 4% bond)"}
  validations:
    - {rule: month_le_12, on_fail: "Rejected — Out of Range"}
    - {rule: latest_equals_max_components, whitelist: ["Casa Sonada 4", "Riverside Terrace"], on_fail: "Verify — Conflicting Sources"}
    - {rule: expiration_ge_compliance_start, when_both_present: true, on_fail: "Verify — Conflicting Sources"}
    - {rule: compliance_start_within_months_after_closing, months: 36, when_both_present: true, on_fail: "Verify — Conflicting Sources"}
    PRESERVATION_NOTICE_WINDOW:  {from: LATEST_Expiration_Date, window_months_before: [36, 30], basis: DERIVED, min_units: 5, require_programs: push_covered, derivation: "REGULATORY_LATEST_END - 36..30 months (OAR 813-115 first notice; statute text unverified)"}
  normalize:
    County: title_case
    City: {title_case: true, typo_map: {Portalnd: Portland}}
    "Owner Type": {title_case: true, map: {Profit: For-Profit, "Non-profit": Non-Profit, Government: Government}, blank: infer_from_owner_name}
    "Property Type": {drop_values: ["0", "ERROR: #N/A"]}
  numeric:
    int_columns: ["Rehab Year", "Year Built", "Total Units", "Total_30_AMI_Units", "Total_40_AMI_Units", "Total_50_AMI_Units",
                  "Total_60_AMI_Units", "Total_80_AMI_Units", "Market_Rate_Units", "Rental_Assistance_Count"]
  filters:
    exclude: {Status: ["In Development"]}
  value_proxy: {fallback: ppu_band, rent_limits_file: rent-limits.json}
  county_fips: {Multnomah: "41051", Washington: "41067", Clackamas: "41005", Columbia: "41009", Yamhill: "41071"}
hud_fhasl_active:
  match_columns: ["HUD Project Number", "Maturity Date", "Section of the Act"]
  dates: {"Initial Endorsement Date": {format: excel_date}, "Final Endorsement Date": {format: excel_date}, "Maturity Date": {format: excel_date, basis: RECORDED, event: LOAN_MATURITY}}
  derived_events: {PREPAY_WINDOW_OPEN: {from: "Final Endorsement Date", add_years: 10, basis: DERIVED, window_months: 6}}
  soa_affordable_codes: ["236", "221(d)(3)", "202", "811", "542"]
hud_mf_assistance_sec8:
  match_columns: ["property_id", "tracs_overall_expiration_date"]
  dates: {tracs_effective_date: {format: excel_date}, tracs_overall_expiration_date: {format: excel_date, basis: REPORTED, event: HAP_EXPIRATION, confidence: 0.70}}
"""

DEFAULT_MARKET_PARAMS: Dict[str, Any] = {
    "_note": "Embedded fallback mirroring references/sources/oregon-portland/market-params.json. Pack file wins when present. Every value carries as_of and source; values marked verify were not fetched live.",
    "cap_rate_market_avg": {"value": 0.064, "as_of": "2026-Q2", "source": "Kidder Mathews Portland Multifamily 2Q 2026 (snippet, verified_live=false)"},
    "cap_rate_class_a": {"value": 0.047, "as_of": "2026-09-12", "source": "ApartmentLoanStore indicative (unaudited)"},
    "cap_rate_class_b": {"value": 0.051, "as_of": "2026-09-12", "source": "ApartmentLoanStore indicative (unaudited)"},
    "cap_rate_class_c": {"value": 0.056, "as_of": "2026-09-12", "source": "ApartmentLoanStore indicative (unaudited)"},
    "cap_rate_affordable": {"value": 0.0675, "as_of": "2026-10", "source": "Class C + 100 bp house assumption", "verify": True},
    "price_per_unit_avg": {"value": 182489, "as_of": "2026-Q2", "source": "Kidder Mathews Q2 2026 average price per unit (snippet, verified_live=false)", "verify": True},
    "rmv_sales_ratio": {"value": 1.0, "as_of": "placeholder", "source": "neighborhood median SALE_PRICE / prior-year RMV; compute from the assessor export", "verify": True},
    "vacancy": {"value": 0.071, "as_of": "2026-Q2", "source": "Kidder Mathews"},
    "asking_rent_per_unit": {"value": 1656, "as_of": "2026-Q2", "source": "Kidder Mathews"},
    "opex_per_unit_market": {"value": 9400, "as_of": "2026", "source": "IREM 2023 Portland $8,637 inflated 3%/yr"},
    "opex_per_unit_regulated": {"value": 8700, "as_of": "2026", "source": "OHCS FY24 $8,198 inflated"},
    "opex_ratio_market": {"value": 0.42, "as_of": "2026", "source": "IREM implied OER"},
    "opex_ratio_affordable": {"value": 0.50, "as_of": "2026", "source": "house assumption for regulated stock"},
    "ust10": {"value": 0.0415, "as_of": "placeholder", "source": "verify before use", "verify": True},
    "refi_spread_bp": {"value": 175, "as_of": "2026", "source": "agency/bank spread assumption"},
    "dscr_floor_market": {"value": 1.25, "as_of": "2026-05", "source": "multifamily-benchmarks Quick Reference"},
    "dscr_floor_bank": {"value": 1.20, "as_of": "2026-05", "source": "multifamily-benchmarks Quick Reference"},
    "dscr_floor_affordable": {"value": 1.15, "as_of": "2026-05", "source": "sizing-lihtc-permanent-debt"},
    "debt_yield_floor": {"value": 0.08, "as_of": "2026-05", "source": "multifamily-benchmarks Quick Reference"},
    "ltv_max_market": {"value": 0.70, "as_of": "2026-05", "source": "multifamily-benchmarks Quick Reference"},
    "ltv_max_affordable": {"value": 0.80, "as_of": "2026-05", "source": "sizing-lihtc-permanent-debt"},
    "rent_cap_2026": {"value": 0.095, "as_of": "2026", "source": "Oregon OEA ORS 90.324 (snippet)"},
    "relocation_assistance": {"value": {"studio": 2900, "1br": 3300, "2br": 4200, "3br": 4500}, "as_of": "2026", "source": "PHB PCC 30.01.085 (snippet)"},
    "av_is_market": {"value": False, "as_of": "n/a", "source": "Oregon Measure 50"},
    "benchmarks_source": {"value": "multifamily-benchmarks Quick Reference 2026-05", "as_of": "2026-05", "source": "sibling skill"},
}

DEFAULT_LENDER_TERMS: Dict[str, Dict[str, Any]] = {
    # lender_type: min_term, typical, max_term (years), amort_years, rate_proxy
    "bank_cu": {"min_term": 5, "typical": 7, "max_term": 10, "amort": 30, "rate_proxy": "ust10+200"},
    "life_co": {"min_term": 10, "typical": 10, "max_term": 15, "amort": 30, "rate_proxy": "ust10+175"},
    "debt_fund_bridge": {"min_term": 2, "typical": 3, "max_term": 5, "amort": 0, "rate_proxy": "sofr+350"},
    "fannie_dus": {"min_term": 7, "typical": 10, "max_term": 12, "amort": 30, "rate_proxy": "tape"},
    "freddie_k_sb": {"min_term": 5, "typical": 10, "max_term": 10, "amort": 30, "rate_proxy": "tape"},
    "cmbs": {"min_term": 5, "typical": 10, "max_term": 10, "amort": 30, "rate_proxy": "tape"},
    "hud_fha": {"min_term": 35, "typical": 35, "max_term": 40, "amort": 35, "rate_proxy": "tape"},
    "usda_rd": {"min_term": 30, "typical": 50, "max_term": 50, "amort": 50, "rate_proxy": "tape"},
    "state_soft": {"min_term": 15, "typical": 30, "max_term": 60, "amort": 0, "rate_proxy": "coterminous with regulatory agreement"},
    "local_soft": {"min_term": 15, "typical": 30, "max_term": 60, "amort": 0, "rate_proxy": "coterminous with regulatory agreement"},
    "hecm": {"min_term": 0, "typical": 0, "max_term": 0, "amort": 0, "rate_proxy": "due on death/move-out"},
    "seller_private": {"min_term": 1, "typical": 5, "max_term": 10, "amort": 30, "rate_proxy": "unknown"},
    "unknown": {"min_term": 5, "typical": 10, "max_term": 10, "amort": 30, "rate_proxy": "ust10+200"},
}


# --------------------------------------------------------------------------- loaders
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PACK_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "references", "sources", "oregon-portland"))


def load_dataset_schemas(pack_dir: Optional[str] = None) -> Dict[str, Any]:
    """Return dataset schemas from the pack's dataset-schemas.yaml (the default pack when none is given),
    else the embedded condensed default (OHCS, HUD FHASL, HUD Sec 8 only)."""
    for d in (pack_dir, DEFAULT_PACK_DIR):
        if not d:
            continue
        path = os.path.join(d, "dataset-schemas.yaml")
        if os.path.exists(path) and yaml is not None:
            with open(path, "r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            if isinstance(data, dict) and data:
                return data
    if yaml is None:
        raise RuntimeError("pyyaml is required to parse dataset schemas (pip install pyyaml)")
    return yaml.safe_load(DEFAULT_DATASET_SCHEMAS_YAML)


def clean_numeric(value, as_int: bool = True):
    """'2,021' -> 2021; '35.0' -> 35; '$4,200,000' -> 4200000.0; blank/NaN/text -> None.

    OHCS stores Rehab Year with a thousands separator in 99 rows and pandas reads units as floats; a
    comma-bearing year defeated the recent-rehab penalty, so every numeric column passes through here.
    """
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
    if f != f:  # NaN
        return None
    if as_int:
        return int(round(f)) if abs(f - round(f)) < 1e-9 else f
    return f


def apply_numeric_block(df, spec: Dict[str, Any]):
    """Apply a schema's `numeric` block (int_columns / float_columns) in place; returns the frame."""
    num = spec.get("numeric") or {}
    for col in num.get("int_columns", []) or []:
        if col in df.columns:
            df[col] = df[col].map(lambda v: clean_numeric(v, True))
    for col in num.get("float_columns", []) or []:
        if col in df.columns:
            df[col] = df[col].map(lambda v: clean_numeric(v, False))
    return df


def load_market_params(pack_dir: Optional[str] = None, explicit_path: Optional[str] = None) -> Dict[str, Any]:
    """Return market params (pack market-params.json wins; embedded default otherwise)."""
    for path in [explicit_path, os.path.join(pack_dir, "market-params.json") if pack_dir else None, os.path.join(DEFAULT_PACK_DIR, "market-params.json")]:
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict) and data:
                return data
    return DEFAULT_MARKET_PARAMS


def param(params: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Read a market param whether it is stored as {value, as_of, source} or as a bare value."""
    v = params.get(key, default)
    if isinstance(v, dict) and "value" in v:
        return v["value"]
    return v


def load_lender_terms(pack_dir: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """Lender term assumptions. The pack's lender-term-assumptions.md is prose for humans; a
    machine-readable lender-terms.json beside it is honored when present."""
    if pack_dir:
        path = os.path.join(pack_dir, "lender-terms.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)
    return DEFAULT_LENDER_TERMS


def detect_schema(columns: List[str], schemas: Dict[str, Any]) -> Optional[str]:
    """Return the schema id whose match_columns are all present in `columns`."""
    cols = set(c.strip() for c in columns)
    for sid, spec in schemas.items():
        req = spec.get("match_columns") or []
        if req and all(c in cols for c in req):
            return sid
    return None
