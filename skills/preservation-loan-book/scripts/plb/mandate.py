"""NOFA / product eligibility predicate (route-level hard filter on nofa_offer; never an exclusion, never a multiplier).

A product qualifies when status in {open, rolling} AND (eligible_programs empty or intersects programs_list)
AND owner_type not in ineligible_owner_types AND (eligible_owner_types empty or owner_type in it) AND units >= min_units
(units, not units_at_risk) AND (application_window absent or as_of inside it).
mandate_fit = eligible if any product qualifies; ineligible if products exist and none qualifies (reason = first failing
test per product, ';'-joined); no_mandate_file when the pack has no mandate.json.
"""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, Iterable, List, Optional

from .dates import parse_iso


def product_qualifies(prod: Dict[str, Any], programs: Iterable[str], owner_type: str, units: Optional[float], as_of: date) -> Optional[str]:
    """Return None when the product qualifies, else the first failing test as a short reason."""
    status = str(prod.get("status") or "").lower()
    if status not in ("open", "rolling"):
        return f"status {status or 'unknown'}"
    elig = prod.get("eligible_programs") or []
    if elig and not (set(elig) & set(programs)):
        return "program not eligible"
    inel = prod.get("ineligible_owner_types") or []
    if owner_type in inel:
        return f"owner_type {owner_type} ineligible"
    elig_ot = prod.get("eligible_owner_types") or []
    if elig_ot and owner_type not in elig_ot:
        return f"owner_type {owner_type} not eligible"
    mu = prod.get("min_units")
    if mu is not None and (units is None or float(units) < float(mu)):
        return f"units {units if units is not None else 'unknown'} < min_units {mu}"
    win = prod.get("application_window")
    if win:
        o, c = parse_iso(win.get("open")), parse_iso(win.get("close"))
        if (o and as_of < o) or (c and as_of > c):
            return "outside application window"
    return None


def mandate_fit(mandate: Optional[Dict[str, Any]], programs: Iterable[str], owner_type: str, units: Optional[float], as_of: date,
                profile: Optional[str] = None) -> Dict[str, Any]:
    """{mandate_fit, mandate_eligible_products, mandate_ineligible_reason}."""
    if not mandate or not mandate.get("products"):
        return {"mandate_fit": "no_mandate_file", "mandate_eligible_products": "", "mandate_ineligible_reason": ""}
    products: List[Dict[str, Any]] = list(mandate.get("products") or [])
    defaults = (mandate.get("agency_profile_defaults") or {}).get(profile) if profile else None
    if defaults:
        subset = [p for p in products if p.get("product_id") in set(defaults)]
        if subset:
            products = subset
    ok, reasons = [], []
    for p in products:
        why = product_qualifies(p, programs, owner_type, units, as_of)
        if why is None:
            ok.append(str(p.get("product_id")))
        else:
            reasons.append(f"{p.get('product_id')}: {why}")
    if ok:
        return {"mandate_fit": "eligible", "mandate_eligible_products": ";".join(ok), "mandate_ineligible_reason": ""}
    return {"mandate_fit": "ineligible", "mandate_eligible_products": "", "mandate_ineligible_reason": "; ".join(reasons)}
