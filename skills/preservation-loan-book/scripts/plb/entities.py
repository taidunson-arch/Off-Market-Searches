"""Owner-entity classification and sponsor archetypes for a public-agency asset manager.

`infer_owner_type` reads the inventory's Owner Type field plus name tokens (rules unchanged from v2; OHCS Owner
Type values PROFIT / NON-PROFIT / HOUSING AUTHORITY / GOVERNMENT / Limited Dividend). The archetype table carries
no outreach angle or letter template: each owner_type maps to the organization role the agency corresponds with,
the agency role that owns the file, a default intervention route and a public-interest reading. Housing authorities
and nonprofits are partners with capacity, never "do not expect a sale".

PII_POLICY: default outputs carry organization, management agent and registered agent only (the service address for
statutory notices). No skip trace, no personal phone or email; natural persons named as owner of record print as
"individual owner (name withheld; see internal file)" in public packets (plb/pii.py).
"""
from __future__ import annotations

import re
from typing import Dict, Iterable, List, Optional

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
ENTITY_TOKENS = re.compile(r"\b(LLC|LP|INC|CORP|PARTNERSHIP|PARTNERS|ASSOCIATES|TRUST|AUTHORITY|FOUNDATION|COMPANY|CO|HOLDINGS|GROUP)\b", re.I)

PII_POLICY = {
    "default_scope": "organization",
    "organization": "owner entity, developer, management agent, registered agent (service address for notices), am_officer name and role",
    "never": ["owner_phone", "owner_email", "cell", "personal_email", "decision_maker_name", "skip_trace_*"],
    "internal_only": ["am_officer_email", "officer_names"],
    "public_packet": "organization + registered agent + program facts; natural-person owners withheld; residential agent addresses omitted; redactions logged",
    "authority": "ORS 192.355(2) personal information exemption; ORS 192.345 conditional exemptions (verify); HUD tenant data (TRACS/50059) never output",
}


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
    """Infer the canonical owner_type enum (rules in references/sponsor-resolution.md Section 2)."""
    name = (owner_name or "").strip()
    dev = (developer_name or "").strip()
    ot = normalize_owner_type_field(owner_type_field)
    if HOUSING_AUTHORITY_TOKENS.search(name) or ot == "Housing Authority" or (HOUSING_AUTHORITY_TOKENS.search(dev) and not name):
        return "housing_authority"
    if ot == "Government" or GOVERNMENT_TOKENS.search(name):
        return "government"
    if LENDER_TOKENS.search(name) and not PARTNERSHIP_TOKENS.search(name):
        return "lender_reo_receiver"
    if TRUST_TOKENS.search(name) and not PARTNERSHIP_TOKENS.search(name):
        return "trust_estate"
    if name and INDIVIDUAL_NAME.match(name) and not PARTNERSHIP_TOKENS.search(name) and not NONPROFIT_TOKENS.search(name):
        return "individual_owner_of_record"  # a person named as owner of record; occupancy is meaningless for a 5+ unit regulated asset
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
            return "lihtc_partnership_nonprofit_gp"
        return "lihtc_partnership_forprofit_gp"
    if name_np:
        return "nonprofit"
    if ot in ("For-Profit", "Limited Dividend"):
        return "regional_operator"
    if not name:
        return "unknown"
    return "unknown"


def is_self_owned(owner_name: Optional[str], self_owner_tokens: Iterable[str], developer_name: Optional[str] = None) -> bool:
    """True when the owner (or, for a PHA-sponsored LP, the developer) matches the agency's own entity tokens."""
    toks = [t for t in (self_owner_tokens or []) if t]
    if not toks:
        return False
    hay = f"{owner_name or ''} | {developer_name or ''}".upper()
    return any(t.upper() in hay for t in toks)


def is_natural_person(owner_name: Optional[str], owner_type: Optional[str] = None) -> bool:
    """Surname-comma pattern or the individual_owner_of_record owner_type with no entity tokens."""
    name = (owner_name or "").strip()
    if not name:
        return False
    if ENTITY_TOKENS.search(name) or PARTNERSHIP_TOKENS.search(name) or NONPROFIT_TOKENS.search(name):
        return False
    if INDIVIDUAL_NAME.match(name):
        return True
    return str(owner_type or "") == "individual_owner_of_record"


# owner_type -> organization role the agency corresponds with, agency role that owns the file, default route, reading
ARCHETYPES: Dict[str, Dict[str, str]] = {
    "lihtc_partnership_forprofit_gp": {"archetype": "LIHTC partnership, for-profit or Limited Dividend GP", "decision_maker_role": "general partner / managing member (organization)",
                                       "default_route": "notice_compliance", "intervention_owner": "push_program_manager",
                                       "reading": "Owner with the most reasons and fewest obligations to exit at Year 15/30; preservation risk, not a buy-side signal."},
    "lihtc_partnership_nonprofit_gp": {"archetype": "LIHTC partnership, nonprofit GP", "decision_maker_role": "nonprofit sponsor (executive office)",
                                       "default_route": "ta_sponsor", "intervention_owner": "nofa_program_manager",
                                       "reading": "Mission sponsor with recap capacity; fund the 42(i)(7) ROFR or resyndication, offer TA."},
    "nonprofit": {"archetype": "Nonprofit owner", "decision_maker_role": "nonprofit sponsor (executive office)", "default_route": "ta_sponsor",
                  "intervention_owner": "nofa_program_manager", "reading": "Mission owner; partner with capacity for a 0% recap or NOFA award."},
    "housing_authority": {"archetype": "Housing authority", "decision_maker_role": "PHA development / asset management", "default_route": "ta_sponsor",
                          "intervention_owner": "pha_development", "reading": "Public partner; repositioning (RAD / Section 18) and 4% recap are the tools, never a sale script."},
    "government": {"archetype": "Government owner", "decision_maker_role": "housing / asset director", "default_route": "recap_committee",
                   "intervention_owner": "am_officer", "reading": "Public partner; intergovernmental recap."},
    "self_owned": {"archetype": "Our own asset", "decision_maker_role": "the agency itself", "default_route": "servicing_watch",
                   "intervention_owner": "pha_development", "reading": "Our own units: repositioning via recap_committee / servicing_watch; PuSH enforcement does not apply to ourselves."},
    "institutional": {"archetype": "Institutional owner", "decision_maker_role": "asset management (organization)", "default_route": "notice_compliance",
                      "intervention_owner": "push_program_manager", "reading": "Portfolio owner; statutory notice and ROFR are the levers."},
    "regional_operator": {"archetype": "Regional for-profit operator", "decision_maker_role": "principal office (organization)", "default_route": "notice_compliance",
                          "intervention_owner": "push_program_manager", "reading": "For-profit operator; preservation risk at restriction end."},
    "single_asset_llc": {"archetype": "Single-asset LLC", "decision_maker_role": "managing member (organization)", "default_route": "notice_compliance",
                         "intervention_owner": "push_program_manager", "reading": "Single-asset owner; notice and records rights."},
    "individual_owner_of_record": {"archetype": "Individual owner of record", "decision_maker_role": "owner of record (withheld in public packets)", "default_route": "notice_compliance",
                                   "intervention_owner": "push_program_manager", "reading": "Natural-person owner; organization-level correspondence through the notice address only."},
    "trust_estate": {"archetype": "Trust / estate", "decision_maker_role": "trustee or personal representative (organization role)", "default_route": "notice_compliance",
                     "intervention_owner": "legal_counsel", "reading": "Fiduciary owner; notice address is counsel of record."},
    "lender_reo_receiver": {"archetype": "Lender / REO / receiver", "decision_maker_role": "receiver or servicer (organization)", "default_route": "recap_committee",
                            "intervention_owner": "legal_counsel", "reading": "Covenant-extinguishment risk; coordinate with counsel on the regulatory agreement's survival."},
    "unknown": {"archetype": "Unresolved entity", "decision_maker_role": "not in public record", "default_route": "notice_compliance",
                "intervention_owner": "push_program_manager", "reading": "Owner entity unresolved; SOS worklist before any notice."},
}


def archetype(owner_type: str) -> Dict[str, str]:
    return ARCHETYPES.get(owner_type, ARCHETYPES["unknown"])


def sos_worklist_row(owner_name: str, state: str, property_ids: List[str], reason: str) -> Dict[str, str]:
    normalized = re.sub(r"[^A-Z0-9 &]", " ", (owner_name or "").upper())
    normalized = re.sub(r"\s+", " ", normalized).strip()
    url = {"OR": "https://sos.oregon.gov/business/pages/find.aspx",
           "WA": "https://ccfs.sos.wa.gov/"}.get(state, "see pack sources.md (SOS registry)")
    return {"owner_name_raw": owner_name or "", "normalized_name": normalized, "state": state,
            "registry_search_url": url, "reason": reason, "property_ids": ";".join(property_ids)}


def org_resolution_grade(evidence_count: int, registered_agent_known: bool) -> str:
    """A: organization confirmed by >= 2 independent filings with registered agent; B: one filing; C: name only."""
    if registered_agent_known and evidence_count >= 2:
        return "A"
    if evidence_count >= 1:
        return "B"
    return "C"


def normalize_org(name: Optional[str]) -> str:
    """Case-folded organization key for Sponsor_Exposure group-bys (strips punctuation and entity suffix noise)."""
    s = re.sub(r"[^A-Z0-9 ]", " ", str(name or "").upper())
    s = re.sub(r"\b(THE|LLC|L L C|LP|L P|LLLP|INC|INCORPORATED|CORP|CORPORATION|LIMITED PARTNERSHIP|LIMITED|PARTNERSHIP|AN OREGON|A|OF)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()
