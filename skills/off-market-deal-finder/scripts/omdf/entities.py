"""Owner-entity classification and decision-maker archetypes.

The SFR skip-trace model does not identify who can say yes for an LLC/LP/nonprofit owner.
This module infers `owner_type` from the inventory's Owner Type field plus name tokens, maps
it to an outreach archetype/template (references/decision-maker-enrichment.md), and builds the
Secretary-of-State worklist rows the analyst resolves by hand. It never names a person: the
decision maker is written `not in public record` until two independent filings corroborate it.
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional

NONPROFIT_TOKENS = re.compile(
    r"\b(INC|INCORPORATED|CORP|CORPORATION|COMMUNITY|FOUNDATION|MINISTRIES|CATHOLIC|LUTHERAN|HABITAT|CDC|"
    r"CHURCH|CHARIT|SERVICES|COALITION|ALLIANCE|COUNCIL|ASSOCIATION|SOCIETY|MISSION|CENTER|CENTRE|"
    r"NONPROFIT|NON-PROFIT|HOUSING WORKS|HOUSING DEVELOPMENT|DEVELOPMENT CORP|HOUSING CORP)\b", re.I)
PARTNERSHIP_TOKENS = re.compile(
    r"(?<!\w)(LLC|L\.L\.C\.?|LP|L\.P\.?|LLLP|LIMITED PARTNE\w*|LIMITED LIABILITY|GENERAL PARTNERSHIP|PARTNERSHIP|PARTNERS|"
    r"ASSOCIATES|VENTURES?|HOLDINGS|INVESTMENTS|PROPERTIES|APARTMENTS? (LLC|LP))(?!\w)", re.I)
INDIVIDUAL_NAME = re.compile(r"^[A-Za-z'\-\. ]+,\s*[A-Za-z'\-\. ]+$")  # "Last, First M"
HOUSING_AUTHORITY_TOKENS = re.compile(r"\b(HOUSING AUTHORITY|HOME FORWARD|HACSA|HOUSING AGENCY|HOUSING COMMISSION)\b", re.I)
GOVERNMENT_TOKENS = re.compile(r"\b(CITY OF|COUNTY OF|STATE OF|OREGON HOUSING|DEPARTMENT OF|TRIBE|TRIBAL|CONFEDERATED)\b", re.I)
TRUST_TOKENS = re.compile(r"\b(TRUST|TRUSTEE|ESTATE OF|LIVING TRUST|FAMILY TRUST|TTEE)\b", re.I)
LENDER_TOKENS = re.compile(r"\b(BANK|RECEIVER|SERVICER|FEDERAL NATIONAL|HUD|SECRETARY OF HOUSING|REO)\b", re.I)


def normalize_owner_type_field(raw: Optional[str]) -> str:
    """Title-case and map OHCS Owner Type variants (NON-PROFIT, PROFIT, HOUSING AUTHORITY ...)."""
    if raw is None:
        return ""
    s = str(raw).strip()
    if not s or s.lower() == "nan":
        return ""
    t = s.title()
    mapping = {"Profit": "For-Profit", "For Profit": "For-Profit", "Non-Profit": "Non-Profit", "Nonprofit": "Non-Profit",
               "Non Profit": "Non-Profit", "Housing Authority": "Housing Authority", "Government": "Government",
               "Limited Dividend": "Limited Dividend", "Tribal": "Government", "Tribe": "Government"}
    return mapping.get(t, t)


def infer_owner_type(owner_name: Optional[str], owner_type_field: Optional[str] = None,
                     developer_name: Optional[str] = None, asset_class: str = "affordable_regulated") -> str:
    """Infer the canonical owner_type enum.

    Rules (references/decision-maker-enrichment.md Section 2):
    * Housing Authority / Home Forward / HACSA tokens or Owner Type Housing Authority -> housing_authority
    * City/County/State/Tribe tokens or Owner Type Government -> government
    * Owner Type Non-Profit, or nonprofit tokens without partnership tokens -> nonprofit
    * LLC/LP tokens with Owner Type For-Profit/Limited Dividend or blank, and the owner/developer
      names do not read nonprofit -> lihtc_partnership_forprofit_gp (class 3) / single_asset_llc (class 2)
    * LLC/LP tokens where owner or developer reads nonprofit -> lihtc_partnership_nonprofit_gp
    * Trust/Estate tokens -> trust_estate
    * else unknown
    """
    name = (owner_name or "").strip()
    dev = (developer_name or "").strip()
    ot = normalize_owner_type_field(owner_type_field)
    if HOUSING_AUTHORITY_TOKENS.search(name) or ot == "Housing Authority" or HOUSING_AUTHORITY_TOKENS.search(dev) and not name:
        return "housing_authority"
    if ot == "Government" or GOVERNMENT_TOKENS.search(name):
        return "government"
    if LENDER_TOKENS.search(name) and not PARTNERSHIP_TOKENS.search(name):
        return "lender_reo_receiver"
    if TRUST_TOKENS.search(name) and not PARTNERSHIP_TOKENS.search(name):
        return "trust_estate"
    if name and INDIVIDUAL_NAME.match(name) and not PARTNERSHIP_TOKENS.search(name) and not NONPROFIT_TOKENS.search(name):
        return "individual_absentee"  # a person named as owner of record; occupancy is unknown for 5+ units
    is_partnership = bool(PARTNERSHIP_TOKENS.search(name))
    name_np = bool(NONPROFIT_TOKENS.search(name))
    dev_np = bool(NONPROFIT_TOKENS.search(dev)) or bool(HOUSING_AUTHORITY_TOKENS.search(dev))
    if ot == "Non-Profit" and not is_partnership:
        return "nonprofit"
    if is_partnership:
        if asset_class != "affordable_regulated":
            return "single_asset_llc"
        if ot in ("For-Profit", "Limited Dividend"):
            return "lihtc_partnership_forprofit_gp"
        if ot == "Non-Profit" or dev_np or name_np:
            # nonprofit sponsor acting as GP of a tax-credit partnership
            return "lihtc_partnership_nonprofit_gp"
        return "lihtc_partnership_forprofit_gp"
    if name_np:
        return "nonprofit"
    if ot in ("For-Profit", "Limited Dividend"):
        return "regional_operator" if asset_class != "sfr_small_res" else "individual_absentee"
    if not name:
        return "unknown"
    # an individual's name (no entity tokens)
    if asset_class == "sfr_small_res":
        return "individual_absentee"
    return "unknown"


ARCHETYPES: Dict[str, Dict[str, str]] = {
    "individual_occupant": {"archetype": "Individual owner", "decision_maker_role": "owner", "route": "acquisition",
                            "template": "individual_or_trust", "angle": "convenience, certainty, tax strategy; never price-first"},
    "individual_absentee": {"archetype": "Individual absentee owner", "decision_maker_role": "owner", "route": "acquisition",
                            "template": "individual_or_trust", "angle": "convenience, certainty, tax strategy; never price-first"},
    "trust_estate": {"archetype": "Trust / estate", "decision_maker_role": "trustee or personal representative", "route": "acquisition",
                     "template": "estate", "angle": "simple liquidation, stepped-up basis; letter to PR/estate counsel after 60-120 days"},
    "single_asset_llc": {"archetype": "Single-asset LLC", "decision_maker_role": "managing member", "route": "acquisition",
                         "template": "single_asset_llc", "angle": "maturity math, 1031/DST, regulatory fatigue; letter to principal office"},
    "regional_operator": {"archetype": "Regional operator", "decision_maker_role": "principal / acquisitions head", "route": "acquisition",
                          "template": "regional_operator", "angle": "portfolio liquidity; direct principal; respect live exclusives"},
    "institutional": {"archetype": "Institutional owner", "decision_maker_role": "asset manager / dispositions", "route": "acquisition",
                      "template": "institutional", "angle": "certainty, debt assumption; formal IOI, no retail letters"},
    "lihtc_partnership_forprofit_gp": {"archetype": "LIHTC partnership, for-profit GP", "decision_maker_role": "GP managing member + syndicator asset manager",
                                       "route": "acquisition", "template": "lihtc_gp_year15",
                                       "angle": "Year-15 buyout / resyndication, LP exit funding; respect 42(i)(7) ROFR and QC mechanics"},
    "lihtc_partnership_nonprofit_gp": {"archetype": "LIHTC partnership, nonprofit GP", "decision_maker_role": "executive director / CFO / board",
                                       "route": "partnership_preservation", "template": "nonprofit_partnership",
                                       "angle": "recap / JV, preservation capital, ROFR support; no distress script"},
    "nonprofit": {"archetype": "Nonprofit owner", "decision_maker_role": "executive director / CFO / board", "route": "partnership_preservation",
                  "template": "nonprofit_partnership", "angle": "mission partnership meeting; recap / JV; no distress script"},
    "housing_authority": {"archetype": "Housing authority", "decision_maker_role": "development director", "route": "partnership_preservation",
                          "template": "housing_authority_partnership", "angle": "RAD / conversion partner; do not expect a sale"},
    "government": {"archetype": "Government owner", "decision_maker_role": "housing / asset director", "route": "partnership_preservation",
                   "template": "housing_authority_partnership", "angle": "partnership only"},
    "lender_reo_receiver": {"archetype": "Lender / REO / receiver", "decision_maker_role": "receiver, special servicer or debtor's counsel",
                            "route": "lender_counterparty", "template": "receiver_lender", "angle": "register as qualified buyer; speed, no financing contingency"},
    "unknown": {"archetype": "Unresolved entity", "decision_maker_role": "not in public record", "route": "acquisition",
                "template": "single_asset_llc", "angle": "resolve via SOS registry before outreach"},
}


def archetype(owner_type: str) -> Dict[str, str]:
    return ARCHETYPES.get(owner_type, ARCHETYPES["unknown"])


def sos_worklist_row(owner_name: str, state: str, property_ids: List[str], reason: str) -> Dict[str, str]:
    """One row of the SOS worklist CSV (owner_name_raw, normalized_name, state, registry_search_url, reason, property_ids)."""
    normalized = re.sub(r"[^A-Z0-9 &]", " ", (owner_name or "").upper())
    normalized = re.sub(r"\s+", " ", normalized).strip()
    url = {"OR": "https://sos.oregon.gov/business/pages/find.aspx",
           "WA": "https://ccfs.sos.wa.gov/"}.get(state, "see pack sources.md (SOS registry)")
    return {"owner_name_raw": owner_name or "", "normalized_name": normalized, "state": state,
            "registry_search_url": url, "reason": reason, "property_ids": ";".join(property_ids)}


def contact_grade(evidence_count: int, named_person: bool) -> str:
    """A: named person with >= 2 independent filings; B: entity officer from one filing; C: entity + mailing only."""
    if named_person and evidence_count >= 2:
        return "A"
    if named_person and evidence_count == 1:
        return "B"
    return "C"
