"""JSON-driven scoring engine for off-market-deal-finder v2.

The canonical weights live in references/scoring/{sfr_small_res,market_rate_mf,affordable_regulated}.json
and references/scoring/shared_adjustments.json. This module evaluates those files directly:

  factor.bands[]      -> take max (or sum) of matching bands; each band has event_type|signal + match
  factor.modifiers[]  -> additive after the band; cap and floor applied after modifiers
  apply_basis_multiplier -> min basis multiplier across contributing events; `Verify — Ambiguous` forces 0.40
  shared penalties / suppressions / routing_rules / caps / decay / stacking independence

There is no embedded copy of the tables: when the scoring directory is missing the engine raises
FileNotFoundError naming the path, because a silently different rubric is worse than no score (an
earlier embedded fallback had drifted from the JSON by dozens of bands).

The `match` DSL: a leaf {field, op, value, inclusive?} or {all: [...]} / {any: [...]}.
ops: between (lo <= x < hi; <= hi when inclusive), eq, in, lt, lte, gt, gte, exists.
Fields resolve against the event being tested first, then the lead/feature context.
`event_present` is a virtual field: eq X is true when an event of type X is on the lead.
"""
from __future__ import annotations

import json
import math
import os
from datetime import date, datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .dates import days_since as _days_since
from .dates import months_between, urgency_band
from .entities import archetype
from .schema import (AMBIGUOUS_MULTIPLIER, ASSESSOR_DERIVED, ASSET_CLASSES, BASIS_MULTIPLIER, EVENT_TAXONOMY, FLAG_AMBIGUOUS,
                     HELPER_EVENTS, PERMANENT_EVENT_TYPES, TIER_MIN_SCORE, clean_numeric, direction_of, family_of)

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SCORING_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "references", "scoring"))

ASSISTED_PROGRAMS = {"HAP", "PRAC", "RAC", "PAC", "HUD_236", "HUD_202_811", "USDA_515", "HUD_INSURED"}


# --------------------------------------------------------------------------- loading
def load_scoring(scoring_dir: Optional[str] = None) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Any], str]:
    """Return (class_tables, shared, source) where source is 'json:<dir>'.

    Raises FileNotFoundError when any class file or shared_adjustments.json is missing: the JSON files are
    the only rubric, and tests/test_score.py asserts their weights sum to 100 per class.
    """
    d = scoring_dir or DEFAULT_SCORING_DIR
    tables: Dict[str, Dict[str, Any]] = {}
    missing = []
    for cls in ASSET_CLASSES:
        p = os.path.join(d, f"{cls}.json")
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as fh:
                tables[cls] = json.load(fh)
        else:
            missing.append(p)
    sp = os.path.join(d, "shared_adjustments.json")
    if os.path.exists(sp):
        with open(sp, "r", encoding="utf-8") as fh:
            shared = json.load(fh)
    else:
        shared = {}
        missing.append(sp)
    if missing:
        raise FileNotFoundError("scoring tables missing (no embedded fallback by design): " + "; ".join(missing))
    return tables, shared, f"json:{d}"


def weights_sum(table: Dict[str, Any]) -> int:
    return int(sum(int(f.get("weight", 0)) for f in table.get("factors", [])))


def referenced_event_types(table: Dict[str, Any]) -> List[str]:
    out = set()
    for f in table.get("factors", []):
        for b in list(f.get("bands", [])) + list(f.get("modifiers", [])):
            if b.get("event_type"):
                out.add(b["event_type"])
    return sorted(out)


# --------------------------------------------------------------------------- helpers
def _num(x) -> Optional[float]:
    """Numeric coercion that tolerates thousands separators ('2,021' -> 2021.0) and blanks."""
    if x is None:
        return None
    if isinstance(x, bool):
        return float(x)
    v = clean_numeric(x, as_int=False)
    return None if v is None else float(v)


def _bool(x) -> Optional[bool]:
    if isinstance(x, bool):
        return x
    if x is None:
        return None
    s = str(x).strip().lower()
    if s in ("true", "1", "yes", "y", "t"):
        return True
    if s in ("false", "0", "no", "n", "f"):
        return False
    return None


def _coerce_like(val, ref):
    """Coerce context value toward the type of the reference value in the match."""
    if isinstance(ref, bool):
        return _bool(val)
    if isinstance(ref, (int, float)) or (isinstance(ref, list) and ref and all(isinstance(r, (int, float)) and not isinstance(r, bool) for r in ref)):
        return _num(val)
    if ref is None:
        return val
    if isinstance(ref, list):
        return None if val is None else str(val)
    return None if val is None else str(val)


def _leaf(m: Dict[str, Any], ctx: Dict[str, Any], present: set) -> bool:
    field, op, ref = m.get("field"), m.get("op"), m.get("value")
    if field == "event_present":
        if op == "eq":
            return ref in present
        if op == "in":
            return any(r in present for r in (ref or []))
        return False
    raw = ctx.get(field)
    if op == "exists":
        return raw is not None and raw != ""
    val = _coerce_like(raw, ref if op != "between" else (ref[0] if ref else 0))
    if val is None:
        return False
    if op == "eq":
        return val == ref
    if op == "in":
        return val in (ref or [])
    if op in ("lt", "lte", "gt", "gte"):
        r = _num(ref)
        if r is None:
            return False
        return {"lt": val < r, "lte": val <= r, "gt": val > r, "gte": val >= r}[op]
    if op == "between":
        lo, hi = _num(ref[0]), _num(ref[1])
        if lo is not None and val < lo:
            return False
        if hi is None:
            return True
        return val <= hi if m.get("inclusive") else val < hi
    return False


def match(m: Dict[str, Any], ctx: Dict[str, Any], present: set) -> bool:
    if not m:
        return False
    if "all" in m:
        return all(match(x, ctx, present) for x in m["all"])
    if "any" in m:
        return any(match(x, ctx, present) for x in m["any"])
    return _leaf(m, ctx, present)


# --------------------------------------------------------------------------- event preparation
def _parse_date(s) -> Optional[date]:
    if s is None:
        return None
    if isinstance(s, datetime):
        return s.date()
    if isinstance(s, date):
        return s
    s = str(s).strip()
    if not s or s.lower() in ("nan", "none", "nat"):
        return None
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def prepare_events(events: Iterable[Dict[str, Any]], as_of: date) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Normalize raw event rows: dates, months_out, days_since, status; apply suppression and cures.

    Returns (scorable_events, notes) where notes records suppressed/retired event ids.
    """
    evs: List[Dict[str, Any]] = []
    for raw in events:
        e = dict(raw)
        e["event_type"] = str(e.get("event_type", "")).strip()
        if not e["event_type"]:
            continue
        if str(e.get("status", "")).upper() in ("REJECTED",):
            continue
        d = _parse_date(e.get("event_date"))
        e["_date"] = d
        if d is not None:
            e["months_out"] = months_between(as_of, d)
            e["days_since"] = _days_since(as_of, d)
            e["urgency_band"] = urgency_band(e["months_out"])
        else:
            e["months_out"] = _num(e.get("months_out"))
            e["days_since"] = None
        e["event_family"] = e.get("event_family") or family_of(e["event_type"])
        e["direction"] = e.get("direction") or direction_of(e["event_type"])
        e["basis"] = (e.get("basis") or "ESTIMATED").upper()
        e["confidence"] = _num(e.get("confidence")) if e.get("confidence") not in (None, "") else 1.0
        e["value"] = e.get("value") if e.get("value") not in ("", None) else None
        e["detail"] = e.get("detail") if e.get("detail") not in ("", None) else None
        e["verify_flag"] = e.get("verify_flag") if e.get("verify_flag") not in ("", None) else None
        evs.append(e)

    notes: Dict[str, Any] = {"suppressed": [], "retired": [], "suppress_until": None}
    # suppression: SUPPRESS_UNTIL in the future zeroes DEBT-family factors
    future_suppress = [e for e in evs if e["event_type"] == "SUPPRESS_UNTIL" and e["_date"] and e["_date"] > as_of]
    if future_suppress:
        notes["suppress_until"] = max(e["_date"] for e in future_suppress).isoformat()
        kept = []
        for e in evs:
            if e["event_family"] == "DEBT" and e["event_type"] != "SUPPRESS_UNTIL":
                e["status"] = "SUPPRESSED"
                notes["suppressed"].append(e.get("event_id") or e["event_type"])
            else:
                kept.append(e)
        evs = kept
    # cure: NOD_RESCISSION after NOD_RECORDED retires the NOD and its derived clocks
    nods = [e for e in evs if e["event_type"] == "NOD_RECORDED" and e["_date"]]
    resc = [e for e in evs if e["event_type"] == "NOD_RESCISSION" and e["_date"]]
    if nods and resc and max(r["_date"] for r in resc) >= max(n["_date"] for n in nods):
        retired = {"NOD_RECORDED", "TRUSTEE_SALE_EARLIEST", "CURE_DEADLINE"}
        notes["retired"] = [e.get("event_id") or e["event_type"] for e in evs if e["event_type"] in retired]
        evs = [e for e in evs if e["event_type"] not in retired]
    return evs, notes


# --------------------------------------------------------------------------- feature context
def _split(s) -> List[str]:
    if s is None:
        return []
    if isinstance(s, list):
        return [str(x) for x in s]
    s = str(s).strip()
    if not s or s.lower() == "nan":
        return []
    return [x.strip() for x in s.replace("|", ";").split(";") if x.strip()]


def build_context(lead: Dict[str, Any], evs: List[Dict[str, Any]], as_of: date, shared: Dict[str, Any],
                  horizon_months: int = 60) -> Dict[str, Any]:
    ctx: Dict[str, Any] = {}
    for k, v in lead.items():
        if isinstance(v, float) and math.isnan(v):
            v = None
        if isinstance(v, str) and v.strip() == "":
            v = None
        ctx[k] = v
    for k in ("refi_gap_pct", "est_dscr_refi", "equity_cushion_pct", "est_ltv", "units", "year_built", "rehab_year",
              "first_debt_months_out", "first_reg_months_out", "hold_years", "av_rmv_ratio", "rent_gap_pct",
              "fed_filings_12mo", "tenant_cases_24mo", "sponsor_loans_maturing_36mo", "origination_year",
              "sponsor_other_properties_hitting_y15_30_36mo", "rate_spread_bp"):
        if k in ctx:
            ctx[k] = _num(ctx[k])
    for k in ("usps_vacant", "returned_mail_or_no_stat", "on_market", "assumable_debt", "extension_test_pass",
              "inside_portland_city_limits", "on_state_expiring_list", "m2m_portfolio", "lp_transferred_recent",
              "sibling_asset_sold_12mo", "ownership_changed_since_year15"):
        if k in ctx:
            ctx[k] = _bool(ctx[k])
    present = {e["event_type"] for e in evs}
    ctx["event_present_set"] = present
    programs = _split(lead.get("programs"))
    ctx["programs_list"] = programs
    geo_modes = _split(lead.get("geo_modes"))
    if ctx.get("inside_portland_city_limits") is None:
        ctx["inside_portland_city_limits"] = ("city_limits" in geo_modes) or (str(lead.get("jurisdiction") or "").title() == "Portland")
    yb = _num(lead.get("year_built"))
    ctx["building_age_years"] = (as_of.year - yb) if yb else None
    # hold years from event if not on the lead
    if ctx.get("hold_years") is None:
        for e in evs:
            if e["event_type"] == "HOLD_YEARS":
                ctx["hold_years"] = _num(e.get("value"))
    if "lender_type" not in ctx or ctx.get("lender_type") is None:
        for e in evs:
            if e["event_family"] == "DEBT" and e.get("lender_type"):
                ctx["lender_type"] = e["lender_type"]
                break
    if ctx.get("code_cases_open") is None:
        ctx["code_cases_open"] = sum(1 for e in evs if e["event_type"] == "CODE_CASE_OPEN") or None
    # stacking independence with decay
    half_after = int((shared.get("decay") or {}).get("half_weight_after_days", 180))
    permanent = set((shared.get("decay") or {}).get("permanent_event_types", sorted(PERMANENT_EVENT_TYPES)))
    fam_weight: Dict[str, float] = {}
    for e in evs:
        if e["direction"] != "PRESSURE":
            continue
        if e["basis"] == "PROXY":
            continue  # a proxied date is not an independent record
        fam = "ASSESSOR" if e["event_type"] in ASSESSOR_DERIVED else e["event_family"]
        w = 1.0
        if e.get("days_since") is not None and e["days_since"] > half_after and e["event_type"] not in permanent:
            w = 0.5
        fam_weight[fam] = max(fam_weight.get(fam, 0.0), w)
    ctx["independent_families"] = round(sum(fam_weight.values()), 1)
    ctx["families_present"] = sorted(fam_weight)
    ctx["combo_nod_probate"] = "NOD_RECORDED" in present and "PROBATE_FILED" in present
    ctx["combo_pre_nod_both"] = "SUCCESSOR_TRUSTEE_APPOINTED" in present and "OFAP_CERT_RECORDED" in present
    # regulatory stacking: max number of distinct (event_type, program) REGULATORY ends inside any 24-month window
    # one key per program (or per event type when no program): Year 15 and the derived notice deadlines are not program ends
    not_program_ends = {"REGULATORY_LATEST_END", "LIHTC_COMPLIANCE_END", "PRESERVATION_NOTICE_WINDOW", "HAP_OPTOUT_NOTICE_DEADLINE",
                        "PRESERVATION_NOTICE_RECEIVED", "ROFR_RECORDED", "QC_ELIGIBILITY"}
    reg = sorted([(e["_date"], (e.get("program") or e["event_type"])) for e in evs
                  if e["event_family"] == "REGULATORY" and e["direction"] == "PRESSURE" and e["_date"] and e["months_out"] is not None and e["months_out"] >= 0
                  and e["event_type"] not in not_program_ends])
    best = 0
    for i, (d0, _) in enumerate(reg):
        keys = {k for d, k in reg if 0 <= (d - d0).days <= 730}
        best = max(best, len(keys))
    ctx["programs_ending_same_24mo"] = best
    hap = [e["_date"] for e in evs if e["event_type"] == "HAP_EXPIRATION" and e["_date"]]
    eue = [e["_date"] for e in evs if e["event_type"] == "LIHTC_EXTENDED_USE_END" and e["_date"]]
    ctx["hap_and_extended_use_same_24mo"] = any(abs((h - x).days) <= 730 for h in hap for x in eue)
    # Oregon PuSH: the first-notice window is open right now -> request the notice from OHCS / the city
    open_now = False
    for e in evs:
        if e["event_type"] == "PRESERVATION_NOTICE_WINDOW":
            ws, we = _parse_date(e.get("window_start")), _parse_date(e.get("window_end"))
            if ws and we and ws <= as_of <= we:
                open_now = True
    ctx["push_window_open"] = open_now
    # horizon facts
    in_h = [e for e in evs if e["direction"] == "PRESSURE" and e["months_out"] is not None and 0 <= e["months_out"] <= horizon_months]
    ctx["has_debt_in_horizon"] = any(e["event_family"] == "DEBT" for e in in_h)
    ctx["has_reg_in_horizon"] = any(e["event_family"] == "REGULATORY" for e in in_h)
    ctx["has_pressure_in_horizon"] = bool(in_h) or any(e["direction"] == "PRESSURE" and e["event_family"] in ("HARD_DISTRESS", "TAX_LIEN", "PHYSICAL", "OWNERSHIP", "OPERATING") for e in evs)
    ctx["has_hard_distress"] = any(e["event_family"] == "HARD_DISTRESS" and e["direction"] == "PRESSURE" for e in evs)
    return ctx


# --------------------------------------------------------------------------- factor evaluation
def _event_ctx(ctx: Dict[str, Any], e: Dict[str, Any]) -> Dict[str, Any]:
    c = dict(ctx)
    for k in ("months_out", "days_since", "detail", "value", "status", "basis", "confidence", "program", "source", "verify_flag"):
        c[k] = e.get(k)
    c["value"] = _num(e.get("value")) if _num(e.get("value")) is not None else e.get("value")
    return c


def _eval_band(band: Dict[str, Any], ctx: Dict[str, Any], evs: List[Dict[str, Any]], present: set) -> Optional[Dict[str, Any]]:
    """Return {points, evidence(event or None), band} if the band matches, else None."""
    et = band.get("event_type")
    m = band.get("match") or {}
    if et:
        cands = [e for e in evs if e["event_type"] == et]
        for e in cands:
            if match(m, _event_ctx(ctx, e), present):
                pts = float(band.get("points", 0))
                conf = e.get("confidence")
                if conf is not None and 0 < conf < 1:
                    pts = pts * conf
                return {"points": pts, "event": e, "band": band}
        # bands keyed to an event type but phrased against lead fields (event_present / any) still get a chance
        if not cands and any(k in json.dumps(m) for k in ("event_present", '"any"')):
            if match(m, ctx, present):
                return {"points": float(band.get("points", 0)), "event": None, "band": band}
        return None
    if match(m, ctx, present):
        return {"points": float(band.get("points", 0)), "event": None, "band": band}
    return None


def _evidence_item(hit: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
    e = hit.get("event")
    b = hit["band"]
    if e is not None:
        return {"band": b.get("id"), "event_id": e.get("event_id"), "event_type": e["event_type"],
                "event_date": e["_date"].isoformat() if e.get("_date") else None, "months_out": e.get("months_out"),
                "basis": e.get("basis"), "confidence": e.get("confidence"), "source": e.get("source"),
                "verify_flag": e.get("verify_flag"), "points": round(hit["points"], 2)}
    sig = b.get("signal") or (b.get("match") or {}).get("field")
    return {"band": b.get("id"), "signal": sig, "value": ctx.get(sig) if sig else None, "points": round(hit["points"], 2)}


def score_factor(factor: Dict[str, Any], ctx: Dict[str, Any], evs: List[Dict[str, Any]], shared: Dict[str, Any],
                 lead: Dict[str, Any]) -> Dict[str, Any]:
    present = ctx["event_present_set"]
    hits = [h for h in (_eval_band(b, ctx, evs, present) for b in factor.get("bands", [])) if h]
    take = factor.get("take", "max")
    if hits:
        if take == "sum":
            base_hits = hits
            base = sum(h["points"] for h in hits)
        else:
            best = max(hits, key=lambda h: h["points"])
            base_hits = [best]
            base = best["points"]
    else:
        base_hits, base = [], 0.0
    mod_hits = [h for h in (_eval_band(b, ctx, evs, present) for b in factor.get("modifiers", [])) if h]
    mods = sum(h["points"] for h in mod_hits)
    raw = base + mods
    cap = float(factor.get("cap", factor.get("weight", 0)))
    floor = float(factor.get("floor", 0))
    raw = max(floor, min(cap, raw))
    contributing = base_hits + mod_hits
    evidence = [_evidence_item(h, ctx) for h in contributing]
    if not evidence:
        raw = 0.0
    # basis multiplier
    mult = 1.0
    mults = shared.get("basis_multipliers", BASIS_MULTIPLIER)
    overrides = shared.get("verify_flag_multiplier_overrides", {FLAG_AMBIGUOUS: AMBIGUOUS_MULTIPLIER})
    if factor.get("apply_basis_multiplier"):
        ev_events = [h["event"] for h in contributing if h.get("event") is not None]
        if ev_events:
            ms = []
            for e in ev_events:
                m = float(mults.get(e.get("basis", "ESTIMATED"), 0.5))
                if e.get("verify_flag") in overrides:
                    m = float(overrides[e["verify_flag"]])
                ms.append(m)
            mult = min(ms)
        elif factor.get("name") == "equity":
            bb = str(lead.get("balance_basis") or "ESTIMATED").upper()
            mult = float(mults.get(bb, 0.5))
    post = []
    pts = raw * mult
    for pm in factor.get("post_multipliers", []) or []:
        pid = pm.get("id")
        if pid == "noi_source":
            src = str(lead.get("noi_source") or "").lower()
            w = shared.get("post_score_multipliers", {}).get("noi_source_weight", {})
            f = float(w.get("benchmark_estimate", 0.7)) if any(t in src for t in ("estimat", "proxy", "benchmark")) else 1.0
            post.append({"id": pid, "factor": f})
            pts *= f
        elif pid == "maturity_proximity":
            mo = ctx.get("first_debt_months_out")
            f = 0.0 if mo is None else (1.0 if mo < 24 else (0.5 if mo <= 60 else 0.0))
            post.append({"id": pid, "factor": f})
            pts *= f
    reading = lever = ""
    if base_hits:
        reading = base_hits[0]["band"].get("reading", "")
        lever = base_hits[0]["band"].get("lever", "")
    return {"name": factor["name"], "weight": factor.get("weight"), "points_raw": round(raw, 2), "basis_multiplier": mult,
            "post_multipliers": post, "points": round(pts, 2), "evidence": evidence, "reading": reading, "lever": lever,
            "matched_bands": [h["band"].get("id") for h in contributing]}


# --------------------------------------------------------------------------- lead scoring
def _unit_fit(units: Optional[float], unit_range, shared: Dict[str, Any], strict: bool) -> Tuple[float, str]:
    cfg = shared.get("post_score_multipliers", {}).get("deal_size_fit", {})
    inside = float(cfg.get("inside_band", 1.0)); near = float(cfg.get("within_25pct_outside", 0.85)); far = float(cfg.get("beyond_25pct_outside", 0.6))
    if units is None or not unit_range:
        return 1.0, "no_size_test"
    lo, hi = unit_range
    lo = _num(lo); hi = _num(hi)
    if (lo is None or units >= lo) and (hi is None or units <= hi):
        return inside, "inside"
    if strict:
        return 0.0, "excluded_strict"
    if lo is not None and units < lo:
        return (near if units >= lo * 0.75 else far), ("within_25pct" if units >= lo * 0.75 else "beyond_25pct")
    if hi is not None and units > hi:
        return (near if units <= hi * 1.25 else far), ("within_25pct" if units <= hi * 1.25 else "beyond_25pct")
    return inside, "inside"


def _tier_from_score(score: float, shared: Dict[str, Any]) -> str:
    bands = sorted([b for b in shared.get("tier_bands", []) if b.get("tier") in ("A", "B", "C")],
                   key=lambda b: -float(b.get("min_score", 0)))
    if not bands:
        bands = [{"tier": t, "min_score": s} for t, s in TIER_MIN_SCORE.items()]
    for b in bands:
        if score >= float(b["min_score"]):
            return b["tier"]
    return "WATCH"


def _cap_tier(tier: str, cap: Optional[str]) -> str:
    order = {"A": 3, "B": 2, "C": 1, "WATCH": 0, "EXCLUDED": -1}
    if cap is None or tier not in order or cap not in order:
        return tier
    return tier if order[tier] <= order[cap] else cap


def score_lead(lead: Dict[str, Any], events: Iterable[Dict[str, Any]], asset_class: str, tables: Dict[str, Dict[str, Any]],
               shared: Dict[str, Any], as_of: date, unit_range=None, price_band=None, strict_size_fit: bool = False,
               programs_filter: Optional[List[str]] = None, horizon_months: int = 60,
               owner_types_include: Optional[List[str]] = None, owner_types_exclude: Optional[List[str]] = None,
               lender_types: Optional[List[str]] = None, buyer_profile: str = "principal",
               query_type: str = "all") -> Dict[str, Any]:
    """Score one lead. Returns a dict of the scoring columns plus `factors` and `explain` data.

    Run-config inputs that reach the score: `owner_types_include` / `owner_types_exclude` and `lender_types`
    route a non-matching lead to `excluded` with a reason; `buyer_profile` adds the wholesaler gate (class 1)
    or the designee strategy signal (class 3); `query_type` sets `query_hit` (does the lead carry the kind of
    event the user asked about) so a `maturity` run can rank regulatory-only leads as secondary instead of
    silently returning the same list as `all`.
    """
    table = tables[asset_class]
    evs, notes = prepare_events(events, as_of)
    ctx = build_context(lead, evs, as_of, shared, horizon_months)
    if notes.get("suppress_until"):
        ctx["first_debt_months_out"] = None
    factors = [score_factor(f, ctx, evs, shared, lead) for f in table.get("factors", [])]
    score_raw = sum(f["points"] for f in factors)

    # penalties
    penalties = []
    hold = ctx.get("hold_years")
    present = ctx["event_present_set"]
    for p in shared.get("penalties", []):
        if asset_class not in (p.get("classes") or [asset_class]):
            continue
        if p.get("id") == "recent_1031" and ("RECENT_1031_ACQUISITION" in present or (hold is not None and hold < 3)):
            penalties.append({"id": "recent_1031", "points": float(p.get("points", -10))})
        if p.get("id") == "recent_rehab":
            ry = _num(lead.get("rehab_year"))
            if ry and ry >= as_of.year - 5:
                penalties.append({"id": "recent_rehab", "points": float(p.get("points", -15))})
    score = score_raw + sum(p["points"] for p in penalties)

    # post-score multipliers
    unit_range = unit_range or (shared.get("deal_size_defaults", {}).get(asset_class, {}) or {}).get("unit_range")
    size_mult, size_note = _unit_fit(_num(lead.get("units")), unit_range, shared, strict_size_fit)
    multipliers = [{"id": "deal_size_fit", "factor": size_mult, "note": size_note}]
    if asset_class == "affordable_regulated" and programs_filter:
        if not set(programs_filter) & set(ctx["programs_list"]):
            mm = float(shared.get("post_score_multipliers", {}).get("mission_fit_affordable", {}).get("mismatch", 0.6))
            multipliers.append({"id": "mission_fit", "factor": mm, "note": "programs filter mismatch"})
    for m in multipliers:
        score *= m["factor"]
    score = max(0.0, min(100.0, round(score, 1)))

    # routing
    signals = _split(lead.get("signals"))
    gates = _split(lead.get("compliance_gates"))
    route = archetype(str(lead.get("owner_type") or "unknown")).get("route", "acquisition")
    tier_cap = None
    reasons: List[str] = []
    ot = str(lead.get("owner_type") or "unknown")
    status = str(lead.get("status") or "")
    cushion = _num(lead.get("equity_cushion_pct"))
    if status.strip().lower() == "in development":
        route = "excluded"; reasons.append("status In Development")
    if ctx.get("on_market") is True:
        route = "excluded"; reasons.append("active listing (on_market)")
    if size_note == "excluded_strict":
        route = "excluded"; reasons.append("outside unit_range with strict_size_fit")
    if owner_types_include and ot not in owner_types_include:
        route = "excluded"; reasons.append(f"owner_type {ot} not in owner_types_include")
    if owner_types_exclude and ot in owner_types_exclude:
        route = "excluded"; reasons.append(f"owner_type {ot} in owner_types_exclude")
    lt = str(lead.get("lender_type") or ctx.get("lender_type") or "")
    if lender_types and lt and lt not in lender_types:
        route = "excluded"; reasons.append(f"lender_type {lt} not in lender_types")
    # price_or_value_band: same post-score multiplier as unit_range, applied only when est_value is known
    pv = _num(lead.get("est_value"))
    if price_band and pv is not None:
        pmult, pnote = _unit_fit(pv, price_band, shared, strict_size_fit)
        multipliers.append({"id": "price_band_fit", "factor": pmult, "note": pnote})
        if pnote == "excluded_strict":
            route = "excluded"; reasons.append("outside price_or_value_band with strict_size_fit")
        else:
            score = max(0.0, min(100.0, round(score * pmult, 1)))
    # buyer_profile gating (outreach-and-compliance.md Section 3)
    if buyer_profile == "wholesaler" and asset_class == "sfr_small_res" and "wholesaler_registration" not in gates:
        gates.append("wholesaler_registration")
    if buyer_profile in ("nonprofit_preservation", "qualified_purchaser") and asset_class == "affordable_regulated":
        if "designee_strategy" not in signals:
            signals.append("designee_strategy")
    # query_type hit: does the lead carry the kind of event the user asked about?
    debt_hit = bool(ctx.get("has_debt_in_horizon"))
    reg_hit = bool(ctx.get("has_reg_in_horizon"))
    distress_hit = bool(ctx.get("has_hard_distress")) or any(e["event_family"] in ("TAX_LIEN", "PHYSICAL") and e["direction"] == "PRESSURE" for e in evs)
    query_hit = {"maturity": debt_hit, "regulatory_expiry": reg_hit, "distress": distress_hit}.get(query_type, True)
    if route != "excluded":
        if "TRUSTEES_DEED" in present or ot == "lender_reo_receiver" or (asset_class == "sfr_small_res" and ot == "institutional"):
            route = "lender_counterparty"; reasons.append("trustee's deed / lender-owned")
        elif ("RECEIVER_APPOINTED" in present or "SPECIAL_SERVICING" in present) and (cushion is None or cushion <= 0):
            route = "lender_counterparty"; reasons.append("receiver or special servicer with no equity cushion")
        elif asset_class == "market_rate_mf" and cushion is not None and cushion <= 0:
            route = "lender_counterparty"; reasons.append("equity_cushion_pct <= 0")
        if ot in ("housing_authority", "government"):
            route = "partnership_preservation"; tier_cap = "B"; reasons.append("housing authority / government owner")
        if ot in ("lihtc_partnership_nonprofit_gp", "nonprofit"):
            route = "partnership_preservation"; reasons.append("nonprofit owner (ROFR / mission)")
        if "ROFR_RECORDED" in present:
            route = "partnership_preservation"
            if "rofr_encumbered" not in signals:
                signals.append("rofr_encumbered")
            reasons.append("ROFR recorded")
        if "BANKRUPTCY_FILED" in present and "counsel_only" not in gates:
            gates.append("counsel_only")
        rs = _num(lead.get("rate_spread_bp")) or _num(ctx.get("rate_spread_bp"))
        if ctx.get("assumable_debt") is True and rs is not None and rs > 150 and not ctx.get("has_hard_distress"):
            if "assumption_play" not in signals:
                signals.append("assumption_play")
            if route == "acquisition" and score < 30:
                route = "assumption_play"
    # tier
    governing = [ev for f in factors for ev in f["evidence"] if ev.get("event_type")]
    cap_labels: List[str] = []
    tier = _tier_from_score(score, shared)
    if governing and all(ev.get("basis") == "PROXY" for ev in governing):
        tier_cap = _cap_tier("C", tier_cap) if tier_cap else "C"; cap_labels.append("proxy-only")
    if asset_class in ("market_rate_mf", "affordable_regulated") and not ctx["has_debt_in_horizon"] and not ctx["has_reg_in_horizon"]:
        tier_cap = _cap_tier("C", tier_cap) if tier_cap else "C"; cap_labels.append("no DEBT/REGULATORY event in horizon")
    if ot in ("housing_authority", "government"):
        cap_labels.append("housing authority cap B")
    tier = _cap_tier(tier, tier_cap)
    if route == "excluded":
        tier = "EXCLUDED"
    elif tier == "WATCH":
        if ctx["has_pressure_in_horizon"]:
            if route == "acquisition":
                route = "watch"
        else:
            tier = "EXCLUDED"; route = "excluded"; reasons.append("no dated PRESSURE event inside horizon")
    for lab in cap_labels:
        tag = "cap:" + lab.replace(" ", "_")
        if tag not in signals:
            signals.append(tag)
    for f in factors:
        for b in f["matched_bands"]:
            if b and b not in signals:
                signals.append(b)
    # outreach
    arch = archetype(ot)
    template = arch["template"]
    if route == "lender_counterparty":
        template = "receiver_lender"
    elif asset_class == "affordable_regulated" and ot in ("lihtc_partnership_forprofit_gp", "single_asset_llc", "regional_operator", "institutional") \
            and set(ctx["programs_list"]) & ASSISTED_PROGRAMS and template == "lihtc_gp_year15" and "LIHTC_9" not in ctx["programs_list"] and "LIHTC_4" not in ctx["programs_list"]:
        template = "hud_usda_assisted_owner"
    verify = []
    for ev in governing:
        if ev.get("basis") != "RECORDED":
            doc = {"LOAN_MATURITY": "loan note / recorded trust deed image", "HAP_EXPIRATION": "HAP contract (TRACS)",
                   "LIHTC_EXTENDED_USE_END": "LURA / REUA", "LIHTC_COMPLIANCE_END": "8609 / Compliance_Start confirmation",
                   "SOFT_PROGRAM_END": "regulatory agreement", "USDA_515_MATURITY": "RD loan docs"}.get(ev.get("event_type"), "source document")
            s = f"confirm {ev.get('event_type')} {ev.get('event_date')} [{ev.get('basis')}] via {doc}"
            if s not in verify:
                verify.append(s)
    next_action = {"A": "Verify governing dates, resolve decision maker to grade A/B, first touch this month",
                   "B": "Resolve decision maker; buy recorder images; schedule outreach next 60 days",
                   "C": "Monitor; add tapes that upgrade PROXY/ESTIMATED dates", "WATCH": "Quarterly re-check",
                   "EXCLUDED": "No action"}.get(tier, "")
    if route == "partnership_preservation":
        next_action = "Partnership track: mission/recap conversation, not a distress script. " + next_action
    if route == "lender_counterparty":
        next_action = "Lender/receiver track: register as qualified buyer; owner_outreach=false. " + next_action
    return {
        "score_raw": round(score_raw, 1), "motivation_score": score, "tier": tier, "route": route,
        "outreach_template": template, "outreach_angle": arch["angle"], "signals": ";".join(signals),
        "compliance_gates": ";".join(gates), "verify_before_outreach": "; ".join(verify), "next_action": next_action,
        "query_type": query_type, "query_hit": query_hit, "buyer_profile": buyer_profile,
        "factors": factors, "penalties": penalties, "multipliers": multipliers, "route_reasons": reasons,
        "tier_caps": cap_labels, "suppression": notes, "context": {k: v for k, v in ctx.items() if k in (
            "independent_families", "families_present", "programs_ending_same_24mo", "hap_and_extended_use_same_24mo",
            "has_debt_in_horizon", "has_reg_in_horizon", "first_debt_months_out", "first_reg_months_out", "hold_years")},
    }


def explain(result: Dict[str, Any], lead: Dict[str, Any]) -> str:
    lines = [f"== {lead.get('property_name') or lead.get('property_id')}  ({lead.get('asset_class')}, owner_type={lead.get('owner_type')})"]
    for f in result["factors"]:
        pm = " ".join(f"x{m['factor']}({m['id']})" for m in f["post_multipliers"]) if f["post_multipliers"] else ""
        lines.append(f"  {f['name']:<32} raw {f['points_raw']:>6.2f} x basis {f['basis_multiplier']:.2f} {pm} = {f['points']:>6.2f} / {f['weight']}")
        for ev in f["evidence"]:
            if ev.get("event_type"):
                lines.append(f"      - {ev['band']}: {ev['event_type']} {ev.get('event_date')} [{ev.get('basis')}] months_out={ev.get('months_out')} src={ev.get('source')} pts={ev['points']}")
            else:
                lines.append(f"      - {ev['band']}: {ev.get('signal')}={ev.get('value')} pts={ev['points']}")
        if f["reading"]:
            lines.append(f"      reading: {f['reading']}")
            lines.append(f"      lever:   {f['lever']}")
    lines.append(f"  score_raw {result['score_raw']}  penalties {result['penalties']}  multipliers {[(m['id'], m['factor']) for m in result['multipliers']]}")
    lines.append(f"  motivation_score {result['motivation_score']}  tier {result['tier']}  caps {result['tier_caps']}  route {result['route']} ({'; '.join(result['route_reasons']) or 'default'})")
    if result["suppression"].get("suppress_until"):
        lines.append(f"  DEBT factors suppressed until {result['suppression']['suppress_until']}")
    ctx = result["context"]
    lines.append(f"  families {ctx.get('families_present')} (independent={ctx.get('independent_families')}); programs_ending_same_24mo={ctx.get('programs_ending_same_24mo')}")
    return "\n".join(lines)
