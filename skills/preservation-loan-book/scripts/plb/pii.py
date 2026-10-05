"""Sunshine / PII scopes (references/pii-and-sunshine.md).

Three scopes:
  public_packet : allow-listed columns only; natural-person owners withheld; residential registered-agent addresses omitted;
                  every redaction logged (Redaction_Log) with the cite ORS 192.355(2) / 192.345 (verify)
  organization  : default. Everything except NEVER and INTERNAL columns; am_officer (name and role) stays, since a public
                  employee's assignment on a loan file is a public record
  internal      : adds am_officer_email and officer_names from public filings (SOS, 990); still never NEVER columns

NEVER columns are dropped at adapter write and at every output regardless of scope.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

import pandas as pd

from .entities import is_natural_person
from .schema import PII_SCOPES

NEVER_COLUMNS = {"owner_phone", "owner_email", "cell", "cell_phone", "personal_email", "decision_maker_name", "dm_source", "owner_main_phone_number_text"}
NEVER_PREFIXES = ("skip_trace",)
INTERNAL_COLUMNS = {"am_officer_email", "officer_names"}
PUBLIC_PACKET_ALLOW = [
    "property_id", "property_name", "address", "city", "zip", "county_name", "jurisdiction", "units", "programs", "hud_contract", "property_type",
    "owner_name", "owner_type", "developer_name", "manager_name", "registered_agent", "registered_agent_address", "universe", "book_kind",
    "restricted_units", "units_basis", "units_at_risk", "hap_units_at_risk", "prac_units_at_risk", "other_ra_units", "psh_units_at_risk",
    "vulnerability_flags", "public_upb", "public_upb_at_risk", "public_grant_at_risk", "our_maturity", "our_maturity_basis", "affordability_end",
    "covenant_status", "first_debt_event_type", "first_debt_event_date", "first_debt_basis", "first_reg_event_type", "first_reg_event_date",
    "first_reg_basis", "owner_cliff_type", "owner_cliff_date", "owner_cliff_band", "agency_action_type", "agency_action_date", "action_band",
    "notice_status", "tenant_notice_status", "recap_status", "qc_status", "intervention_score", "board_impact", "queue_band", "urgency_band",
    "primary_route", "secondary_routes", "intervention", "intervention_owner", "statutory_cite", "verify_flags", "signals", "as_of_date",
    "withdrawal_anchor_date", "push_anchor_source", "kpi_flags", "next_expected_expiration", "sponsor_cliff_count", "mandate_fit",
]
REDACTION_CITE = "ORS 192.355(2) personal information exemption; ORS 192.345 conditional exemptions (verify current text)"
WITHHELD = "individual owner (name withheld; see internal file)"
RESIDENTIAL_RE = re.compile(r"\b(APT|APARTMENT|UNIT|#)\s*\w+", re.I)
BUSINESS_RE = re.compile(r"\b(SUITE|STE|FLOOR|FL|PO BOX|P\.O\. BOX)\b", re.I)


def is_residential_agent_address(addr: str, owner_mailing: str = "") -> bool:
    a = str(addr or "").strip()
    if not a:
        return False
    if BUSINESS_RE.search(a):
        return False
    if RESIDENTIAL_RE.search(a):
        return True
    if owner_mailing and a.upper() == str(owner_mailing).upper():
        return True
    return False


def drop_never_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in df.columns if c in NEVER_COLUMNS or any(str(c).startswith(p) for p in NEVER_PREFIXES)]
    return df.drop(columns=cols) if cols else df


def apply_pii_scope(df: pd.DataFrame, scope: str = "organization") -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
    """Return (frame, redaction_log). Never mutates the input."""
    if scope not in PII_SCOPES:
        raise ValueError(f"pii_scope {scope} not in {PII_SCOPES}")
    out = drop_never_columns(df.copy())
    log: List[Dict[str, Any]] = []
    if scope == "internal":
        return out, log
    internal_present = [c for c in out.columns if c in INTERNAL_COLUMNS]
    if internal_present:
        out = out.drop(columns=internal_present)
    if scope == "organization":
        return out, log
    # public packet
    keep = [c for c in PUBLIC_PACKET_ALLOW if c in out.columns]
    dropped = [c for c in out.columns if c not in keep]
    out = out[keep].copy()
    if dropped:
        log.append({"field": ";".join(dropped), "rows_redacted": int(len(out)), "action": "column omitted from packet", "cite": REDACTION_CITE})
    if "owner_name" in out.columns:
        mask = [is_natural_person(n, t) for n, t in zip(out["owner_name"], out.get("owner_type", pd.Series([""] * len(out), index=out.index)))]
        n = int(sum(mask))
        if n:
            out.loc[pd.Series(mask, index=out.index), "owner_name"] = WITHHELD
            log.append({"field": "owner_name", "rows_redacted": n, "action": WITHHELD, "cite": REDACTION_CITE})
    if "registered_agent_address" in out.columns:
        mask = out["registered_agent_address"].map(lambda a: is_residential_agent_address(a))
        n = int(mask.sum())
        if n:
            out.loc[mask, "registered_agent_address"] = "(residential address omitted)"
            log.append({"field": "registered_agent_address", "rows_redacted": n, "action": "residential address omitted", "cite": REDACTION_CITE})
    return out, log


def assert_no_pii(df: pd.DataFrame) -> List[str]:
    """Return the NEVER / INTERNAL columns present with any non-blank value (empty list = clean)."""
    bad = []
    for c in df.columns:
        if c in NEVER_COLUMNS or c in INTERNAL_COLUMNS or any(str(c).startswith(p) for p in NEVER_PREFIXES):
            if (df[c].astype(str).str.strip() != "").any():
                bad.append(c)
    return bad


RECORDS_CLASSIFICATION = "agency working file; disclosable subject to ORS 192.345/192.355 review; tenant data excluded by design"
