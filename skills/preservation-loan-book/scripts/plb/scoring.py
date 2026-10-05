"""JSON-driven scoring engine for preservation-loan-book (class affordable_public_am; noah_unregulated optional).

The canonical weights live in references/scoring/affordable_public_am.json and shared_adjustments.json. This module
evaluates those files directly:

  factor.requires        -> match object on the context; the factor scores 0 (factor_status WATCH / n/a) when false
  factor.bands[]         -> take max (or sum) of matching bands; each band has event_type|signal + match
  factor.modifiers[]     -> additive after the band; cap and floor applied after modifiers
  apply_basis_multiplier -> min basis multiplier across the base events that scored (`basis_from: governing_event` borrows the
                            owner cliff's basis for an attribute factor); `Verify — Ambiguous` forces 0.40; HAP confidence 0.70 /
                            0.90 multiplies that band only
  post_multipliers       -> recap_status x0.5 on the clock and declared-intent factors (RECORDED/REPORTED evidence only)
  shared caps / suppressions / decay / queue bands; route rules (precedence) live here and are gated by the agency profile

There is no embedded copy of the tables: a missing scoring directory raises FileNotFoundError.
match DSL: leaf {field, op, value, inclusive?} or {all: [...]} / {any: [...]}; ops between, eq, in, lt, lte, gt, gte, exists,
absent, contains, days_since_between; virtual field event_present (eq X / in [...]).
"""
from __future__ import annotations

import json
import math
import os
from datetime import date, datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .dates import days_since as _days_since
from .dates import months_between, parse_iso, timing_fraction, urgency_band
from .interventions import cite as _cite
from .interventions import meta as _imeta
from .mandate import mandate_fit as _mandate_fit
from .schema import (AMBIGUOUS_MULTIPLIER, ASSESSOR_DERIVED, BASIS_MULTIPLIER, DEFAULT_SCORING_DIR, EVENT_TAXONOMY, FLAG_AMBIGUOUS, FLAG_BOOK_JOIN,
                     FLAG_CA_LOG, FLAG_NOTICE_LOG, FORPROFIT_OWNER_TYPES, HAP_LIKE_PROGRAMS, HELPER_EVENTS, MISSION_OWNER_TYPES, NON_DECAYING_WHILE_OPEN,
                     NOT_OWNER_CLIFF, PERMANENT_EVENT_TYPES, QUEUE_MIN_SCORE, ROUTES, SCORING_CLASS_FOR_ASSET, clean_numeric, direction_of, family_of)

QUEUE_ORDER = {"ESCALATE": 4, "ACT": 3, "PLAN": 2, "WATCH": 1, "EXCLUDED": 0}
DOC_FOR_EVENT = {"LOAN_MATURITY": "senior loan note / recorded trust deed", "HAP_EXPIRATION": "HAP contract / renewal request (HUD-9624) via the CA",
                 "LIHTC_EXTENDED_USE_END": "LURA / REUA from our file", "LIHTC_COMPLIANCE_END": "8609 / Compliance_Start confirmation",
                 "SOFT_PROGRAM_END": "regulatory agreement from our file", "USDA_515_MATURITY": "RD loan docs", "AFFORDABILITY_PERIOD_END": "HOME written agreement",
                 "GRANT_RECAPTURE_END": "grant agreement", "AGENCY_LOAN_MATURITY": "our note / loan agreement", "REGULATORY_LATEST_END": "every recorded regulatory agreement",
                 "QC_ELIGIBILITY": "QC request and price certification", "PRESERVATION_NOTICE_RECEIVED": "the owner's notice as logged"}


# --------------------------------------------------------------------------- loading
def load_scoring(scoring_dir: Optional[str] = None) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Any], str]:
    """Return (class_tables keyed by asset_class, shared, 'json:<dir>'). affordable_public_am.json and shared_adjustments.json are
    required; noah_watch.json is optional (loaded as noah_unregulated when present)."""
    d = scoring_dir or DEFAULT_SCORING_DIR
    tables: Dict[str, Dict[str, Any]] = {}
    missing = []
    p = os.path.join(d, "affordable_public_am.json")
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as fh:
            tables["affordable_regulated"] = json.load(fh)
    else:
        missing.append(p)
    pn = os.path.join(d, "noah_watch.json")
    if os.path.exists(pn):
        with open(pn, "r", encoding="utf-8") as fh:
            tables["noah_unregulated"] = json.load(fh)
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
    if isinstance(ref, bool):
        return _bool(val)
    if isinstance(ref, (int, float)) or (isinstance(ref, list) and ref and all(isinstance(r, (int, float)) and not isinstance(r, bool) for r in ref)):
        return _num(val)
    if ref is None:
        return val
    return None if val is None else str(val)


def _blank(v) -> bool:
    return v is None or (isinstance(v, float) and math.isnan(v)) or str(v).strip() == ""


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
        return not _blank(raw)
    if op == "absent":
        return _blank(raw)
    if op == "contains":
        items = [x.strip() for x in str(raw or "").replace("|", ";").split(";") if x.strip()]
        return (ref in items) if not isinstance(ref, list) else any(r in items for r in ref)
    if op == "days_since_between":
        v = _num(ctx.get("days_since"))
        return v is not None and _num(ref[0]) <= v < _num(ref[1])
    val = _coerce_like(raw, ref if op != "between" else (ref[0] if ref and ref[0] is not None else 0))
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
        lo = _num(ref[0]) if ref[0] is not None else None
        hi = _num(ref[1]) if ref[1] is not None else None
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
def prepare_events(events: Iterable[Dict[str, Any]], as_of: date) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Normalize raw event rows: dates, months_out, days_since, status; apply SUPPRESS_UNTIL (DEBT family only)."""
    evs: List[Dict[str, Any]] = []
    for raw in events:
        e = dict(raw)
        e["event_type"] = str(e.get("event_type", "")).strip()
        if not e["event_type"]:
            continue
        st = str(e.get("status") or "").upper()
        if st == "REJECTED":
            continue
        d = parse_iso(e.get("event_date"))
        e["_date"] = d
        if d is not None:
            e["months_out"] = months_between(as_of, d)
            e["days_since"] = _days_since(as_of, d)
            e["urgency_band"] = urgency_band(e["months_out"])
        else:
            e["months_out"] = _num(e.get("months_out"))
            e["days_since"] = None
        if st in ("", "PAST", "FUTURE") and d is not None:
            st = "PAST" if d < as_of else "FUTURE"
        e["status"] = st or "FUTURE"
        if e["event_type"] == "QC_ELIGIBILITY":
            # the QC lifecycle (eligible | requested | lapsed_decontrol) rides in detail beside the ledger id tag; surface it as status
            toks = [t.strip().lower() for t in str(e.get("detail") or "").split(";")]
            qc = next((t for t in toks if t in ("eligible", "requested", "lapsed_decontrol")), None)
            if qc and e["status"] not in ("SUPPRESSED", "RETIRED"):
                e["status"] = qc
        e["event_family"] = e.get("event_family") or family_of(e["event_type"])
        e["direction"] = e.get("direction") or direction_of(e["event_type"])
        e["basis"] = (str(e.get("basis")) if not _blank(e.get("basis")) else "ESTIMATED").upper()
        e["confidence"] = _num(e.get("confidence")) if not _blank(e.get("confidence")) else 1.0
        for k in ("value", "detail", "verify_flag", "program", "source"):
            e[k] = None if _blank(e.get(k)) else e.get(k)
        evs.append(e)
    notes: Dict[str, Any] = {"suppressed": [], "retired": [], "suppress_until": None}
    future_suppress = [e for e in evs if e["event_type"] == "SUPPRESS_UNTIL" and e["_date"] and e["_date"] > as_of]
    if future_suppress or any(e["status"] == "SUPPRESSED" for e in evs):
        if future_suppress:
            notes["suppress_until"] = max(e["_date"] for e in future_suppress).isoformat()
        kept = []
        for e in evs:
            if (e["event_family"] == "DEBT" and e["event_type"] != "SUPPRESS_UNTIL" and future_suppress) or e["status"] == "SUPPRESSED":
                e["status"] = "SUPPRESSED"
                notes["suppressed"].append(e.get("event_id") or e["event_type"])
            else:
                kept.append(e)
        evs = kept
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


def _owner_cliff_months(evs: List[Dict[str, Any]], as_of: date) -> Optional[float]:
    cands = [e for e in evs if e["direction"] == "PRESSURE" and e["event_family"] in ("REGULATORY", "DEBT") and e["event_type"] not in NOT_OWNER_CLIFF
             and e["status"] not in ("STALE_CONTRACT_DATE", "SUPPRESSED") and e["basis"] != "PROXY" and e["_date"]]
    if not cands:
        return None
    fut = [e for e in cands if e["_date"] >= as_of]
    e = min(fut, key=lambda x: x["_date"]) if fut else max(cands, key=lambda x: x["_date"])
    return e["months_out"]


def _window_state(evs: List[Dict[str, Any]], as_of: date, notice_status: str) -> str:
    wins = [e for e in evs if e["event_type"] == "PRESERVATION_NOTICE_WINDOW"]
    if not wins:
        return ""
    first = next((e for e in wins if "push_first" in str(e.get("detail") or "")), wins[0])
    second = next((e for e in wins if "push_second" in str(e.get("detail") or "")), None)
    ws, we = parse_iso(first.get("window_start")), parse_iso(first.get("window_end"))
    if not (ws and we):
        return ""
    if as_of < ws:
        return "not_open"
    if as_of < we:
        return "open_first"
    we2 = parse_iso(second.get("window_end")) if second else None
    if notice_status == "received":
        return "open_second" if (we2 is None or as_of < we2) else "closed_second_due_received"
    return "closed_first_due" if (we2 is None or as_of < we2) else "closed_second_due"


def build_context(lead: Dict[str, Any], evs: List[Dict[str, Any]], as_of: date, shared: Dict[str, Any],
                  horizon_months: int = 120, profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    ctx: Dict[str, Any] = {}
    for k, v in lead.items():
        if isinstance(v, float) and math.isnan(v):
            v = None
        if isinstance(v, str) and v.strip() == "":
            v = None
        ctx[k] = v
    for k in ("units", "units_at_risk", "restricted_units", "hap_units_at_risk", "prac_units_at_risk", "other_ra_units", "psh_units_at_risk",
              "family_3br_plus_units", "year_built", "rehab_year", "first_debt_months_out", "first_reg_months_out", "owner_cliff_months_out",
              "agency_action_months_out", "sponsor_cliff_count", "public_upb", "hold_years", "rent_to_fmr_ratio", "tax_delinquent_years"):
        if k in ctx:
            ctx[k] = _num(ctx[k])
    for k in ("apps_flag", "out_of_state_sponsor", "ownership_changed", "ownership_changed_since_year15", "lp_transferred_recent", "coterminous_senior_cliff",
              "in_inventory", "high_displacement_tract", "underserved_district", "ohcs_funded", "rofr_recorded"):
        if k in ctx:
            ctx[k] = _bool(ctx[k])
    present = {e["event_type"] for e in evs}
    ctx["event_present_set"] = present
    programs = _split(lead.get("programs"))
    ctx["programs_list"] = programs
    ctx["as_of_year"] = as_of.year
    yb = ctx.get("year_built")
    ctx["building_age_years"] = (as_of.year - yb) if yb else None
    ry = ctx.get("rehab_year")
    ctx["recent_rehab"] = bool(ry and ry >= as_of.year - 5)
    units = ctx.get("units")
    restricted = ctx.get("restricted_units") or ctx.get("units_at_risk")
    f3 = ctx.get("family_3br_plus_units")
    ctx["family_3br_share"] = (f3 / units) if (f3 is not None and units) else None
    hap = ctx.get("hap_units_at_risk")
    ctx["hap_share"] = (hap / restricted) if (hap is not None and restricted) else None
    vflags = _split(lead.get("vulnerability_flags"))
    ctx["vulnerability_flags_list"] = vflags
    ctx["elderly_or_disabled"] = bool(set(vflags) & {"elderly", "disabled"})
    ctx["notice_status"] = str(lead.get("notice_status") or "unknown") if not _blank(lead.get("notice_status")) else "unknown"
    if "PRESERVATION_NOTICE_RECEIVED" in present:
        ctx["notice_status"] = "received"
    ctx["tenant_notice_status"] = ctx.get("tenant_notice_status") or "unknown"
    ctx["hap_renewal_request_status"] = ctx.get("hap_renewal_request_status") or "unknown"
    ctx["recap_status"] = ctx.get("recap_status") or "none"
    reb = ctx.get("recap_evidence_basis")
    if not reb:
        reb = "RECORDED" if ("STABILIZATION_AWARD" in present or str(lead.get("book_match")) in ("matched", "self_owned", "book_only")) else "unknown"
    ctx["recap_evidence_basis"] = reb
    ctx["book_match"] = ctx.get("book_match") or "book_absent"
    ctx["self_owned"] = ctx["book_match"] == "self_owned" or str(lead.get("owner_type")) == "self_owned"
    ctx["universe"] = ctx.get("universe") or ("our_book" if ctx["book_match"] in ("matched", "self_owned", "book_only") else "universe_not_held")
    ctx["covenant_status"] = ctx.get("covenant_status") or ""
    if ctx.get("owner_cliff_months_out") is None:
        ctx["owner_cliff_months_out"] = _owner_cliff_months(evs, as_of)
    y15 = [e for e in evs if e["event_type"] == "LIHTC_COMPLIANCE_END" and e["_date"]]
    ctx["lihtc_compliance_end_months_out"] = min(e["months_out"] for e in y15) if y15 else None
    ws = ctx.get("notice_window_state") or _window_state(evs, as_of, ctx["notice_status"])
    ctx["notice_window_state"] = ws
    if ctx.get("code_cases_open") is None:
        ctx["code_cases_open"] = sum(1 for e in evs if e["event_type"] == "CODE_CASE_OPEN") or None
    if ctx.get("hold_years") is None:
        for e in evs:
            if e["event_type"] == "HOLD_YEARS":
                ctx["hold_years"] = _num(e.get("value"))
    # stacking independence with decay
    half_after = int((shared.get("decay") or {}).get("half_weight_after_days", 180))
    permanent = set((shared.get("decay") or {}).get("permanent_event_types", sorted(PERMANENT_EVENT_TYPES)))
    non_decay = {x.split(":")[0] for x in (shared.get("decay") or {}).get("non_decaying_while_open", sorted(NON_DECAYING_WHILE_OPEN))}
    fam_weight: Dict[str, float] = {}
    for e in evs:
        if e["direction"] != "PRESSURE" or e["basis"] == "PROXY" or e["event_family"] == "AGENCY_DEADLINE" or e["event_type"] in HELPER_EVENTS:
            continue
        fam = "ASSESSOR" if e["event_type"] in ASSESSOR_DERIVED else e["event_family"]
        w = 1.0
        if e.get("days_since") is not None and e["days_since"] > half_after and e["event_type"] not in permanent and e["event_type"] not in non_decay:
            w = 0.5
        fam_weight[fam] = max(fam_weight.get(fam, 0.0), w)
    ctx["independent_families"] = round(sum(fam_weight.values()), 1)
    ctx["families_present"] = sorted(fam_weight)
    not_program_ends = NOT_OWNER_CLIFF | {"NOTICE_COMPLIANCE_BREACH"}
    reg = sorted([(e["_date"], (e.get("program") or e["event_type"])) for e in evs
                  if e["event_family"] == "REGULATORY" and e["direction"] == "PRESSURE" and e["_date"] and e["months_out"] is not None and e["months_out"] >= 0
                  and e["event_type"] not in not_program_ends and e["status"] != "STALE_CONTRACT_DATE"])
    best = 0
    for d0, _ in reg:
        keys = {k for d, k in reg if 0 <= (d - d0).days <= 730}
        best = max(best, len(keys))
    ctx["programs_ending_same_24mo"] = best
    hap_d = [e["_date"] for e in evs if e["event_type"] == "HAP_EXPIRATION" and e["_date"] and e["status"] != "STALE_CONTRACT_DATE"]
    eue = [e["_date"] for e in evs if e["event_type"] == "LIHTC_EXTENDED_USE_END" and e["_date"]]
    ctx["hap_and_extended_use_same_24mo"] = any(abs((h - x).days) <= 730 for h in hap_d for x in eue)
    ctx["push_window_open"] = ws in ("open_first", "open_second")
    # horizon facts (owner-side)
    in_h = [e for e in evs if e["direction"] == "PRESSURE" and e["event_type"] not in HELPER_EVENTS and e["event_family"] != "AGENCY_DEADLINE"
            and e["status"] != "STALE_CONTRACT_DATE" and e["months_out"] is not None and 0 <= e["months_out"] <= horizon_months]
    ctx["has_debt_in_horizon"] = any(e["event_family"] == "DEBT" and e["basis"] != "PROXY" for e in in_h)
    ctx["has_reg_in_horizon"] = any(e["event_family"] == "REGULATORY" for e in in_h)
    recent_other = any(e["direction"] == "PRESSURE" and e["event_family"] in ("HARD_DISTRESS", "TAX_LIEN", "PHYSICAL", "OWNERSHIP", "OPERATING")
                       and (e["months_out"] is None or e["months_out"] >= -24 or e["event_type"] in non_decay | permanent) for e in evs)
    overdue_cliff = ctx.get("owner_cliff_months_out") is not None and -12 <= ctx["owner_cliff_months_out"] < 0
    stale_recent = any(e["event_type"] == "HAP_EXPIRATION" and e["status"] == "STALE_CONTRACT_DATE" and e["months_out"] is not None and e["months_out"] >= -12 for e in evs)
    ctx["has_pressure_in_horizon"] = bool([e for e in in_h if e["basis"] != "PROXY"]) or recent_other or overdue_cliff or stale_recent
    ctx["has_hard_distress"] = any(e["event_family"] == "HARD_DISTRESS" and e["direction"] == "PRESSURE" for e in evs)
    if profile:
        ctx["profile"] = profile.get("profile")
        ctx["administers_qc"] = bool(profile.get("administers_qc"))
        ctx["is_qualified_purchaser"] = bool(profile.get("is_qualified_purchaser") or profile.get("is_designee"))
    return ctx


# --------------------------------------------------------------------------- factor evaluation
def _event_ctx(ctx: Dict[str, Any], e: Dict[str, Any]) -> Dict[str, Any]:
    c = dict(ctx)
    for k in ("months_out", "days_since", "detail", "value", "status", "basis", "confidence", "program", "source", "verify_flag"):
        c[k] = e.get(k)
    c["value"] = _num(e.get("value")) if _num(e.get("value")) is not None else e.get("value")
    return c


def _eval_band(band: Dict[str, Any], ctx: Dict[str, Any], evs: List[Dict[str, Any]], present: set) -> Optional[Dict[str, Any]]:
    et = band.get("event_type")
    m = band.get("match") or {}
    if et:
        cands = [e for e in evs if e["event_type"] == et]
        best = None
        for e in cands:
            if match(m, _event_ctx(ctx, e), present):
                pts = float(band.get("points", 0))
                conf = e.get("confidence")
                if conf is not None and 0 < conf < 1:
                    pts = pts * conf
                hit = {"points": pts, "event": e, "band": band}
                if best is None or hit["points"] > best["points"] or (hit["points"] == best["points"] and BASIS_MULTIPLIER.get(e["basis"], 0) > BASIS_MULTIPLIER.get(best["event"]["basis"], 0)):
                    best = hit
        if best:
            return best
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


def _governing_cliff_event(evs: List[Dict[str, Any]], as_of: date) -> Optional[Dict[str, Any]]:
    cands = [e for e in evs if e["direction"] == "PRESSURE" and e["event_family"] in ("REGULATORY", "DEBT") and e["event_type"] not in NOT_OWNER_CLIFF
             and e["status"] not in ("STALE_CONTRACT_DATE", "SUPPRESSED") and e["basis"] != "PROXY" and e["_date"]]
    if not cands:
        return None
    fut = [e for e in cands if e["_date"] >= as_of]
    return min(fut, key=lambda x: x["_date"]) if fut else max(cands, key=lambda x: x["_date"])


def score_factor(factor: Dict[str, Any], ctx: Dict[str, Any], evs: List[Dict[str, Any]], shared: Dict[str, Any],
                 lead: Dict[str, Any], as_of: Optional[date] = None) -> Dict[str, Any]:
    present = ctx["event_present_set"]
    base_out = {"name": factor["name"], "weight": factor.get("weight"), "points_raw": 0.0, "basis_multiplier": 1.0, "post_multipliers": [],
                "points": 0.0, "factor_status": "scored", "evidence": [], "reading": "", "intervention": "", "matched_bands": [], "flags": []}
    req = factor.get("requires")
    if req and not match(req, ctx, present):
        rule = (factor.get("on_requires_fail") or {}).get(str(ctx.get("book_match")), None) if factor.get("on_requires_fail") else None
        if rule:
            base_out["factor_status"] = rule.get("factor_status", "n/a")
            if rule.get("flag"):
                base_out["flags"].append(rule["flag"])
        else:
            base_out["factor_status"] = "n/a"
        return base_out
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
    if not evidence or not base_hits:
        raw = 0.0 if not base_hits and not (take == "sum" and mod_hits) else raw
        if not base_hits:
            evidence = [] if not mod_hits else evidence
            raw = 0.0
    mult = 1.0
    mults = shared.get("basis_multipliers", BASIS_MULTIPLIER)
    overrides = shared.get("verify_flag_multiplier_overrides", {FLAG_AMBIGUOUS: AMBIGUOUS_MULTIPLIER})
    if factor.get("apply_basis_multiplier") and raw > 0:
        base_events = [h["event"] for h in base_hits if h.get("event") is not None]
        if factor.get("basis_from") == "governing_event" and not base_events and as_of is not None:
            g = _governing_cliff_event(evs, as_of)
            base_events = [g] if g else []
        if base_events:
            ms = []
            for e in base_events:
                m_ = float(mults.get(e.get("basis", "ESTIMATED"), 0.5))
                if e.get("verify_flag") in overrides:
                    m_ = float(overrides[e["verify_flag"]])
                ms.append(m_)
            mult = min(ms)
    post = []
    pts = raw * mult
    for pm in factor.get("post_multipliers", []) or []:
        pid = pm.get("id")
        if pid == "recap_status":
            cfg = (shared.get("multipliers") or {}).get("recap_status", {})
            st = str(ctx.get("recap_status") or "none")
            f = float(cfg.get(st, 1.0)) if str(ctx.get("recap_evidence_basis")) in ("RECORDED", "REPORTED") else 1.0
            if st in ("under_application", "closed") and f == 1.0:
                base_out["flags"].append("recap_status_unverified")
            post.append({"id": pid, "factor": f})
            pts *= f
    reading = intervention = ""
    if base_hits:
        reading = base_hits[0]["band"].get("reading", "")
        intervention = base_hits[0]["band"].get("intervention", base_hits[0]["band"].get("lever", ""))
    for h in contributing:
        sf = h["band"].get("sets_flag")
        if sf:
            base_out["flags"].append(sf)
    base_out.update({"points_raw": round(raw, 2), "basis_multiplier": mult, "post_multipliers": post, "points": round(pts, 2), "evidence": evidence,
                     "reading": reading, "intervention": intervention, "matched_bands": [h["band"].get("id") for h in contributing]})
    return base_out


# --------------------------------------------------------------------------- queue bands
def _queue_from_score(score: float, shared: Dict[str, Any]) -> str:
    bands = sorted([b for b in shared.get("queue_bands", []) if b.get("queue_band") in QUEUE_MIN_SCORE], key=lambda b: -float(b.get("min_score", 0)))
    if not bands:
        bands = [{"queue_band": t, "min_score": s} for t, s in QUEUE_MIN_SCORE.items()]
    for b in bands:
        if score >= float(b["min_score"]):
            return b["queue_band"]
    return "WATCH"


def _cap_queue(q: str, cap: Optional[str]) -> str:
    if cap is None or q not in QUEUE_ORDER or cap not in QUEUE_ORDER:
        return q
    return q if QUEUE_ORDER[q] <= QUEUE_ORDER[cap] else cap


# --------------------------------------------------------------------------- routing
def _mo(e: Dict[str, Any]) -> Optional[float]:
    return e.get("months_out")


def route_lead(ctx: Dict[str, Any], evs: List[Dict[str, Any]], score: float, profile: Dict[str, Any], as_of: date) -> Dict[str, Any]:
    """Evaluate every route rule; primary by precedence; others secondary. Returns routes, intervention, reasons, signals, flags."""
    present = ctx["event_present_set"]
    enabled = set(profile.get("routes_enabled") or ROUTES)
    self_owned = bool(ctx.get("self_owned"))
    our_book = ctx.get("universe") == "our_book"
    mission = str(ctx.get("owner_type")) in MISSION_OWNER_TYPES
    qualified = bool(profile.get("is_qualified_purchaser") or profile.get("is_designee"))
    administers_qc = bool(profile.get("administers_qc"))
    hits: Dict[str, Dict[str, Any]] = {}
    signals: List[str] = []
    flags: List[str] = []
    reasons: List[str] = []
    gates: List[str] = []
    kpi: List[str] = []
    agency_act_by_override = None

    def hit(route, intervention, reason, primary=True):
        if route not in enabled:
            reasons.append(f"{route} suppressed by profile ({profile.get('profile')})")
            return
        if self_owned and route in ("notice_compliance", "designee_rofr", "nofa_offer", "ta_sponsor"):
            return
        if route not in hits or (primary and not hits[route]["primary"]):
            hits[route] = {"intervention": intervention, "reason": reason, "primary": primary}

    hap_live = [e for e in evs if e["event_type"] == "HAP_EXPIRATION" and str(e.get("program") or "") in HAP_LIKE_PROGRAMS and e["status"] != "STALE_CONTRACT_DATE" and e["_date"]]
    hap_live = [e for e in hap_live if e["months_out"] is not None and e["months_out"] >= 0]
    rrs = str(ctx.get("hap_renewal_request_status") or "unknown")
    notice_received = [e for e in evs if e["event_type"] == "PRESERVATION_NOTICE_RECEIVED"]
    details = {str(e.get("detail") or "") for e in notice_received}
    # ---- optout_response (statutory clocks first)
    if "hap_optout" in details and hap_live:
        hit("optout_response", "optout_response_plan", "opt-out notice received (PRESERVATION_NOTICE_RECEIVED hap_optout)")
    elif rrs == "not_received" and any((e["_date"] - as_of).days <= 120 for e in hap_live):
        hit("optout_response", "optout_response_plan", "no renewal request at the CA within 120 days of HAP expiration")
    elif rrs == "unknown" and any(0 <= e["months_out"] <= 12 and str(e.get("detail") or "") != "mahra_20yr_recent" for e in hap_live):
        hit("optout_response", "optout_tenant_notice_check", "HAP expiration inside 12 months; renewal request status unknown at the CA")
        nd = [e for e in evs if e["event_type"] == "HAP_OPTOUT_NOTICE_DEADLINE" and e["_date"] and e["_date"] < as_of]
        if nd:
            signals.append("optout_notice_deadline_passed_unconfirmed")
            flags.append(FLAG_CA_LOG)
        pkg = [e for e in evs if e["event_type"] == "HAP_OPTOUT_PACKAGE_DUE" and e["_date"]]
        if pkg:
            agency_act_by_override = min(pkg, key=lambda e: e["_date"])
    if rrs == "received" and hap_live:
        signals.append("optout_window_closed_for_term")
        kpi.append("hap_renewed")
    # ---- notice_compliance
    ws = str(ctx.get("notice_window_state") or "")
    ns = str(ctx.get("notice_status") or "unknown")
    if "NOTICE_COMPLIANCE_BREACH" in present:
        hit("notice_compliance", "push_notice_demand_letter", "NOTICE_COMPLIANCE_BREACH: first notice due passed, not_received_confirmed")
    elif ws in ("closed_first_due", "closed_second_due") and ns != "received":
        if ns == "not_received_confirmed":
            hit("notice_compliance", "push_notice_demand_letter", f"{ws} and notice_status not_received_confirmed")
        else:
            # unknown silence: a compliance case only once a notice log is loaded for this run; otherwise a secondary "confirm the log"
            # route behind recap_committee / optout_response / servicing_watch (the row still earns the 6-point intent band + flag)
            log_loaded = bool(profile.get("notice_log_loaded"))
            hit("notice_compliance", "push_window_prep", f"{ws} and notice_status unknown: confirm against PuSH-CP log / ask OHCS"
                + ("" if log_loaded else " (no notice log loaded this run: secondary)"), primary=log_loaded)
            flags.append(FLAG_NOTICE_LOG)
    if str(ctx.get("tenant_notice_status")) == "not_confirmed" and "TENANT_NOTICE_WINDOW" in present:
        hit("notice_compliance", "tenant_notice_check", "tenant notice not confirmed inside / after the SB 973 window")
    if ws == "open_first" and ns != "received":
        hit("notice_compliance", "push_window_prep", "first-notice window open; owner not yet late (prep only)", primary=False)
    # ---- qc_admin / QC non-hfa
    qc_req = [e for e in evs if e["event_type"] == "QC_ELIGIBILITY" and str(e.get("status") or "") in ("requested", "lapsed_decontrol")
              or (e["event_type"] == "QC_ELIGIBILITY" and str(e.get("detail") or "") in ("requested", "lapsed_decontrol"))]
    qc_signal = bool(qc_req) or "QC_REQUEST_INELIGIBLE" in present
    qc_waived = str(ctx.get("qc_waived") or "").lower() == "true"
    if administers_qc:
        if qc_req and not qc_waived and any(e["basis"] == "RECORDED" for e in qc_req):
            due = [e for e in evs if e["event_type"] == "QC_RESPONSE_DUE" and e["_date"]]
            interv = "qc_marketing_plan" if due and min(e["months_out"] for e in due) <= 6 else "qc_request_acknowledgement"
            hit("qc_admin", interv, "RECORDED qualified-contract request on file (qc_waived != true)")
        if "QC_REQUEST_INELIGIBLE" in present:
            hit("qc_admin", "qc_waiver_acknowledgement", "QC request on an allocation that waived the qualified contract")
    elif qc_signal:
        hit("ta_sponsor" if mission else "nofa_offer", "qc_coordination_with_hfa", "QC signal; this profile does not administer qualified contracts")
    # ---- designee_rofr
    if "ROFR_RECORDED" in present:
        hit("designee_rofr", "rofr_assignment_memo" if mission else "rofr_notice_recording", "Notice of ROFR recorded (our right)")
    if "THIRD_PARTY_OFFER_RECEIVED" in present:
        hit("designee_rofr", "rofr_match_offer", "third-party offer mailed; 30-day match clock running")
    if qualified and (details & {"push_first", "push_second"}):
        hit("designee_rofr", "rofr_notice_recording", "owner's PuSH notice received; qualified purchaser")
    if "USDA_PREPAY_REQUEST_RECEIVED" in present:
        hit("designee_rofr", "usda_prepay_response", "RD prepayment request; public-body offer window")
    if qualified and "NOTICE_COMPLIANCE_BREACH" in present:
        hit("designee_rofr", "rofr_notice_recording", "designee appointment on silence (ORS 456.262 / HB 2095, verify)")
    # ---- recap_committee
    reac_lt60 = any(e["event_type"] == "REAC_SCORE" and _num(e.get("value")) is not None and _num(e.get("value")) < 60 for e in evs)
    our_mat_le24 = any(e["event_type"] == "AGENCY_LOAN_MATURITY" and e["months_out"] is not None and 0 <= e["months_out"] <= 24 for e in evs)
    cliff_mo = ctx.get("owner_cliff_months_out")
    hud_legacy = any(e["event_type"] in ("HUD_DIRECT_LOAN_MATURITY", "PREPAY_WINDOW_OPEN") for e in evs) or bool({"HUD_236", "HUD_202_811"} & set(ctx["programs_list"]))
    if our_book:
        workout = {"RECEIVER_APPOINTED", "BANKRUPTCY_FILED", "JUDICIAL_FORECLOSURE_FILED"} & present
        if self_owned and ({"RAD_CHAP", "SECTION_18_APPLICATION"} & present or (cliff_mo is not None and cliff_mo <= 24)):
            hit("recap_committee", "pha_repositioning", "our own asset: repositioning marker or owner cliff <= 24 mo")
        elif "COVENANT_DEFAULT" in present or "RECAPTURE_TRIGGER" in present or workout:
            hit("recap_committee", "loan_extension_recast_memo", "covenant default / recapture trigger / workout event on our book")
        elif reac_lt60:
            hit("recap_committee", "loan_extension_recast_memo", "REAC/NSPIRE below 60 on our book (troubled-asset AM)")
        elif our_mat_le24 or ctx.get("coterminous_senior_cliff") is True:
            hit("recap_committee", "hud_legacy_response" if hud_legacy else "loan_extension_recast_memo", "our maturity <= 24 mo or coterminous senior cliff")
        elif score >= 50:
            hit("recap_committee", "zero_pct_recap_term_sheet" if mission else "loan_extension_recast_memo", f"intervention_score {score} >= 50 on our book")
    # ---- servicing_watch
    if our_book:
        ours_le60 = any(e["event_type"] in ("AGENCY_LOAN_MATURITY", "GRANT_RECAPTURE_END", "SHARED_APPRECIATION_DUE") and e["months_out"] is not None and 0 <= e["months_out"] <= 60 for e in evs) \
            or any(e["event_type"] == "AFFORDABILITY_PERIOD_END" and str(e.get("source") or "") == "agency_servicing" and e["months_out"] is not None and 0 <= e["months_out"] <= 60 for e in evs) \
            or (self_owned and cliff_mo is not None and 0 <= cliff_mo <= 60)
        cov = str(ctx.get("covenant_status") or "")
        finding = "NONCOMPLIANCE_FINDING" in present
        insp = any(e["event_type"] == "INSPECTION_DUE" and e["months_out"] is not None and e["months_out"] <= 6 for e in evs)
        senior_le60 = any(e["event_type"] in ("LOAN_MATURITY", "HUD_DIRECT_LOAN_MATURITY") and e["months_out"] is not None and 0 <= e["months_out"] <= 60 and e["basis"] != "PROXY" for e in evs)
        prac = bool({"PRAC", "PAC"} & set(ctx["programs_list"]))
        if ours_le60 or cov in ("watch", "default") or reac_lt60 or finding or insp or senior_le60:
            if finding:
                interv = "enforcement_8823"
            elif cov in ("watch", "default") or reac_lt60:
                interv = "covenant_enforcement_notice"      # enforcement only on a covenant watch / default or a failing REAC
            elif "GRANT_RECAPTURE_END" in present or str(ctx.get("recapture_type") or "none") not in ("none", ""):
                interv = "covenant_recapture_review"
            elif prac:
                interv = "prac_renewal_coordination"
            else:
                interv = "servicing_watch_memo"             # healthy loan with a dated trigger: monitoring memo, never an enforcement notice
            why = []
            if ours_le60:
                why.append("our maturity / affordability / recapture end <= 60 mo")
            if cov in ("watch", "default"):
                why.append(f"covenant_status {cov}")
            if reac_lt60:
                why.append("REAC < 60")
            if finding:
                why.append("open noncompliance finding")
            if insp:
                why.append("inspection due <= 6 mo")
            if senior_le60:
                why.append("senior cliff <= 60 mo")
            hit("servicing_watch", interv, "; ".join(why))
    # ---- nofa_offer
    mf = str(ctx.get("mandate_fit") or "no_mandate_file")
    reg_debt_cliff = cliff_mo is not None and 0 <= cliff_mo <= 60
    if (not our_book or str(ctx.get("recap_status")) in ("announced", "under_application")) and reg_debt_cliff:
        if mf in ("eligible", "no_mandate_file"):
            hit("nofa_offer", "preservation_nofa_invitation", "owner cliff <= 60 mo; product eligible" if mf == "eligible" else "owner cliff <= 60 mo; no mandate file (mandate_unknown)")
            if mf == "no_mandate_file":
                signals.append("mandate_unknown")
        else:
            reasons.append("nofa_offer blocked: mandate_fit ineligible")
    # ---- ta_sponsor
    if mission and not self_owned:
        trig = any(e["event_type"] in ("LIHTC_COMPLIANCE_END", "LIHTC_EXTENDED_USE_END") and e["months_out"] is not None and 0 <= e["months_out"] <= 60 for e in evs) \
            or "ROFR_RECORDED" in present or (qc_signal and not administers_qc)
        if trig:
            hit("ta_sponsor", "ta_sponsor_engagement", "mission sponsor with a Year 15 / extended-use / ROFR / QC event inside 60 months")
    # ---- gates
    if "BANKRUPTCY_FILED" in present:
        gates.append("counsel_only")
    if ws and ws not in ("", "not_open", "not_tracked_by_profile"):
        gates.append("preservation_law")
    if any(e["event_type"] == "LIHTC_EXTENDED_USE_END" and e["months_out"] is not None and 0 <= e["months_out"] <= 36 for e in evs) or any(str(e.get("status")) == "lapsed_decontrol" for e in qc_req):
        gates.append("lihtc_tenant_protections")
    # ---- precedence
    primaries = [r for r in ROUTES if r in hits and hits[r]["primary"]]
    primary = primaries[0] if primaries else "none"
    secondary = [r for r in ROUTES if r in hits and r != primary]
    interv = hits[primary]["intervention"] if primary != "none" else ""
    for r in hits:
        reasons.append(f"{r}: {hits[r]['reason']}")
    # kpi flags from status columns
    if ns == "received":
        kpi.append("notice_filed")
    if str(ctx.get("recap_status")) == "closed":
        kpi.append("recap_closed")
    if "STABILIZATION_AWARD" in present:
        kpi.append("preserved")
    if qc_req:
        kpi.append("qc_requested")
    return {"primary_route": primary, "secondary_routes": secondary, "intervention": interv, "route_reasons": reasons, "signals": signals,
            "flags": flags, "compliance_gates": gates, "kpi_flags": sorted(set(kpi)), "agency_act_by_override": agency_act_by_override,
            "route_hits": {r: hits[r]["intervention"] for r in hits}}


# --------------------------------------------------------------------------- lead scoring
def score_lead(lead: Dict[str, Any], events: Iterable[Dict[str, Any]], asset_class: str, tables: Dict[str, Dict[str, Any]],
               shared: Dict[str, Any], as_of: date, profile: Optional[Dict[str, Any]] = None, mandate: Optional[Dict[str, Any]] = None,
               horizon_months: int = 120, owner_types_include: Optional[List[str]] = None, owner_types_exclude: Optional[List[str]] = None) -> Dict[str, Any]:
    """Score one lead. Returns the scoring columns plus factors, routes and explain data."""
    profile = profile or {"profile": "hfa", "routes_enabled": list(ROUTES), "administers_qc": True, "is_qualified_purchaser": True, "receives_push_notice": True, "is_pbca": True}
    table = tables.get(asset_class) or tables.get(SCORING_CLASS_FOR_ASSET.get(asset_class, ""), None)
    if table is None:
        table = tables["affordable_regulated"]
    evs, notes = prepare_events(events, as_of)
    ctx = build_context(lead, evs, as_of, shared, horizon_months, profile)
    # mandate fit (route-level only)
    mfit = _mandate_fit(mandate, ctx["programs_list"], str(lead.get("owner_type") or "unknown"), ctx.get("units"), as_of, profile.get("profile"))
    ctx.update(mfit)
    factors = [score_factor(f, ctx, evs, shared, lead, as_of) for f in table.get("factors", [])]
    score_raw = sum(f["points"] for f in factors)
    score = max(0.0, min(100.0, round(score_raw, 1)))
    flags: List[str] = []
    for f in factors:
        for fl in f.get("flags", []):
            if fl not in flags:
                flags.append(fl)
    signals = _split(lead.get("signals"))
    present = ctx["event_present_set"]
    ot = str(lead.get("owner_type") or "unknown")
    status = str(lead.get("status") or "")
    exclusion = ""
    reasons: List[str] = []
    if status.strip().lower() == "in development":
        exclusion = "in_development"
    elif str(lead.get("in_geography") or "").lower() == "false":
        exclusion = "outside_geography"
    if owner_types_include and ot not in owner_types_include:
        exclusion = exclusion or "owner_types_include"; reasons.append(f"owner_type {ot} not in owner_types_include")
    if owner_types_exclude and ot in owner_types_exclude:
        exclusion = exclusion or "owner_types_exclude"; reasons.append(f"owner_type {ot} in owner_types_exclude")
    # routes
    rt = route_lead(ctx, evs, score, profile, as_of) if not exclusion else {"primary_route": "excluded", "secondary_routes": [], "intervention": "", "route_reasons": [],
                                                                            "signals": [], "flags": [], "compliance_gates": [], "kpi_flags": [], "agency_act_by_override": None, "route_hits": {}}
    for s in rt["signals"]:
        if s not in signals:
            signals.append(s)
    for fl in rt["flags"]:
        if fl not in flags:
            flags.append(fl)
    # queue band + caps
    governing = [ev for f in factors for ev in f["evidence"] if ev.get("event_type")]
    cap_labels: List[str] = []
    queue = _queue_from_score(score, shared)
    qcap = None
    pressure_evs = [e for e in evs if e["direction"] == "PRESSURE" and e["event_type"] not in HELPER_EVENTS and e["event_family"] != "AGENCY_DEADLINE" and e["_date"]]
    proxy_only = (governing and all(ev.get("basis") == "PROXY" for ev in governing)) or (pressure_evs and all(e["basis"] == "PROXY" for e in pressure_evs))
    if proxy_only:
        qcap = "PLAN"; cap_labels.append("proxy-only")
    queue = _cap_queue(queue, qcap)
    units = ctx.get("units")
    # R24 / E3: a book row with no dated cliff inside the horizon stays on the Book_Watchlist as `none` (Monitoring); only
    # inventory rows with nothing dated inside the horizon are EXCLUDED.
    if not exclusion and queue == "WATCH" and not ctx["has_pressure_in_horizon"] and ctx.get("universe") != "our_book":
        exclusion = "no_dated_cliff_in_horizon"
    if not exclusion and units is not None and units < 5 and not (ctx["has_debt_in_horizon"] or ctx["has_reg_in_horizon"]) and not ctx.get("self_owned"):
        exclusion = "under_5_units_no_program_event"
    if exclusion:
        queue = "EXCLUDED"
        rt["primary_route"] = "excluded"
        rt["secondary_routes"] = []
        rt["intervention"] = ""
        reasons.append(f"excluded: {exclusion}")
    for lab in cap_labels:
        tag = "cap:" + lab.replace(" ", "_")
        if tag not in signals:
            signals.append(tag)
    if ctx.get("push_window_open") and str(ctx.get("notice_status")) != "received" and "push_window_open_prep" not in signals:
        signals.append("push_window_open_prep")
    if ot == "unknown" and "owner_type_unknown" not in signals:
        signals.append("owner_type_unknown")
    for f in factors:
        for b in f["matched_bands"]:
            if b and b not in signals:
                signals.append(b)
    if (ctx.get("units_at_risk") or 0) and ctx.get("owner_cliff_months_out") is not None and ctx["owner_cliff_months_out"] > 60 and not exclusion:
        pass
    # intervention metadata
    interv = rt["intervention"]
    im = _imeta(interv) if interv else {}
    verify = []
    for ev in governing:
        if ev.get("basis") != "RECORDED":
            doc = DOC_FOR_EVENT.get(ev.get("event_type"), "source document")
            s = f"confirm {ev.get('event_type')} {ev.get('event_date')} [{ev.get('basis')}] via {doc}"
            if s not in verify:
                verify.append(s)
    if FLAG_BOOK_JOIN in flags:
        verify.append("confirm book join: expected in book, servicing extract did not match (no guessed balance)")
    if FLAG_NOTICE_LOG in flags:
        verify.append("confirm owner notice against the PuSH-CP log / ask OHCS before any demand letter")
    act_date = lead.get("agency_action_date") or ""
    if rt.get("agency_act_by_override") is not None:
        act_date = rt["agency_act_by_override"]["_date"].isoformat()
    if rt["primary_route"] == "none":
        next_action = "Monitoring: no rule hit; re-check at the next run" + (f"; next agency act-by {act_date}" if act_date else "")
    elif rt["primary_route"] == "excluded":
        next_action = f"No action ({exclusion})"
    else:
        next_action = (im.get("first_action") or "") + (f"; agency act-by {act_date}" if act_date else "")
    board_impact = round(float(ctx.get("units_at_risk") or 0) * timing_fraction(ctx.get("owner_cliff_months_out")), 1) if ctx.get("owner_cliff_months_out") is not None else 0.0
    return {
        "score_raw": round(score_raw, 1), "intervention_score": score, "board_impact": board_impact, "queue_band": queue,
        "urgency_band": lead.get("action_band") or urgency_band(ctx.get("owner_cliff_months_out")) or "",
        "primary_route": rt["primary_route"], "secondary_routes": ";".join(rt["secondary_routes"]), "exclusion_reason": exclusion if exclusion in ("in_development", "outside_geography", "under_5_units_no_program_event", "no_dated_cliff_in_horizon") else ("" if not exclusion else exclusion),
        "intervention": interv, "intervention_owner": im.get("agency_owner", ""), "statutory_cite": _cite(interv) if interv else "",
        "owner_notice_required": bool(im.get("owner_notice")) if interv else "", "tenant_notice_required": bool(im.get("tenant_notice")) if interv else "",
        "verify_before_action": "; ".join(verify), "next_action": next_action, "compliance_gates": ";".join(dict.fromkeys(rt["compliance_gates"])),
        "kpi_flags": ";".join(rt["kpi_flags"]), "signals": ";".join(dict.fromkeys(signals)), "verify_flags_added": flags,
        "mandate_fit": mfit["mandate_fit"], "mandate_eligible_products": mfit["mandate_eligible_products"], "mandate_ineligible_reason": mfit["mandate_ineligible_reason"],
        "agency_action_date_override": act_date if rt.get("agency_act_by_override") is not None else "",
        "factors": factors, "route_reasons": reasons + rt["route_reasons"], "route_hits": rt["route_hits"], "caps": cap_labels, "suppression": notes,
        "context": {k: v for k, v in ctx.items() if k in (
            "independent_families", "families_present", "programs_ending_same_24mo", "hap_and_extended_use_same_24mo", "has_debt_in_horizon", "has_reg_in_horizon",
            "owner_cliff_months_out", "agency_action_months_out", "notice_window_state", "notice_status", "book_match", "universe", "recap_status", "mandate_fit",
            "units_at_risk", "hap_units_at_risk", "self_owned", "has_pressure_in_horizon")},
    }


def explain(result: Dict[str, Any], lead: Dict[str, Any]) -> str:
    lines = [f"== {lead.get('property_name') or lead.get('property_id')}  ({lead.get('asset_class')}, owner_type={lead.get('owner_type')}, universe={result['context'].get('universe')}, book_match={result['context'].get('book_match')})"]
    for f in result["factors"]:
        pm = " ".join(f"x{m['factor']}({m['id']})" for m in f["post_multipliers"]) if f["post_multipliers"] else ""
        lines.append(f"  {f['name']:<30} raw {f['points_raw']:>6.2f} x basis {f['basis_multiplier']:.2f} {pm} = {f['points']:>6.2f} / {f['weight']}  [{f['factor_status']}]")
        for ev in f["evidence"]:
            if ev.get("event_type"):
                lines.append(f"      - {ev['band']}: {ev['event_type']} {ev.get('event_date')} [{ev.get('basis')}] months_out={ev.get('months_out')} src={ev.get('source')} pts={ev['points']}")
            else:
                lines.append(f"      - {ev['band']}: {ev.get('signal')}={ev.get('value')} pts={ev['points']}")
        if f["reading"]:
            lines.append(f"      reading:      {f['reading']}")
            lines.append(f"      intervention: {f['intervention']}")
    lines.append(f"  score_raw {result['score_raw']}  intervention_score {result['intervention_score']}  queue {result['queue_band']}  caps {result['caps']}")
    lines.append(f"  primary_route {result['primary_route']}  secondary {result['secondary_routes'] or '-'}  intervention {result['intervention'] or '-'} ({result['intervention_owner'] or '-'})")
    for r in result["route_reasons"]:
        lines.append(f"      route: {r}")
    if result["suppression"].get("suppress_until"):
        lines.append(f"  DEBT factors suppressed until {result['suppression']['suppress_until']}")
    ctx = result["context"]
    lines.append(f"  families {ctx.get('families_present')} (independent={ctx.get('independent_families')}); programs_ending_same_24mo={ctx.get('programs_ending_same_24mo')}; "
                 f"owner_cliff_months_out={ctx.get('owner_cliff_months_out')}; notice_window_state={ctx.get('notice_window_state')}; mandate_fit={ctx.get('mandate_fit')}")
    return "\n".join(lines)
