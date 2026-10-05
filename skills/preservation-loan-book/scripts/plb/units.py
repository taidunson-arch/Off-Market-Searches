"""Units, households and public dollars at risk (computed once; read by the score step, the workbook and the brief).

Rules (BUILD SPEC R4 / R5 / R29 / R30; affordable_public_am.json units_at_risk_rule):
  restricted_units   = Total Units - Market_Rate_Units (blank market = 0 -> units_basis total_assumed_restricted);
                       AMI buckets that sum to Total Units -> reported_buckets; Total Units blank -> blank + Missing Source flag
  hap_units_at_risk  = Rental_Assistance_Count only when HUD Contract is HAP or RAC; prac_units_at_risk when PRAC / PAC;
                       otherwise other_ra_units. The three are never summed. PSH_Units is an overlay.
  units_at_risk      = restricted_units (book-only rows: units_assisted)
  public_upb_at_risk = upb where any owner-cliff PRESSURE event <= 36 mo OR covenant_status in {watch, default} OR coterminous_senior_cliff
  public_grant_at_risk = recapture_exposure
  board_impact       = units_at_risk x timing_fraction(owner_cliff_band)
Board_Totals band on owner_cliff_band; the queue sorts on action_band.
"""
from __future__ import annotations

import json
from datetime import date
from typing import Any, Dict, List, Optional

import pandas as pd

from .dates import months_between, parse_iso, timing_fraction
from .recap_math import recapture_exposure
from .schema import FLAG_MISSING_SOURCE, URGENCY_BANDS, URGENCY_ORDER, clean_numeric

BAND_ROWS = ["OVERDUE", "CRITICAL", "URGENT", "APPROACHING", "MONITOR", "SCHEDULED", "BEYOND", "stale_contract_date_verify", "no_dated_cliff"]
TOTAL_COLS = ["properties", "units_at_risk", "hap_units_at_risk", "prac_units_at_risk", "other_ra_units", "psh_units_at_risk",
              "public_upb_at_risk", "public_grant_at_risk", "being_preserved_units"]
OWNED_COLS = ["properties", "units_at_risk", "owned_units", "pbv_households", "psh_units_at_risk", "rad_section18_status", "being_preserved_units"]


def _num(v) -> Optional[float]:
    x = clean_numeric(v, as_int=False)
    return None if x is None else float(x)


def _int(v) -> int:
    x = clean_numeric(v, as_int=True)
    return int(x) if x is not None else 0


def ohcs_units(row: Dict[str, Any]) -> Dict[str, Any]:
    """Units block from one OHCS inventory row (raw column names)."""
    total = clean_numeric(row.get("Total Units"), True)
    market = _int(row.get("Market_Rate_Units"))
    buckets = [_int(row.get(f"Total_{b}_AMI_Units")) for b in ("30", "40", "50", "60", "80")]
    out: Dict[str, Any] = {"restricted_units": "", "units_basis": "", "units_at_risk": "", "flag": ""}
    if total is None:
        out["flag"] = FLAG_MISSING_SOURCE + ": Total Units blank; units at risk cannot be counted"
    else:
        restricted = max(0, int(total) - market)
        out["restricted_units"] = restricted
        out["units_at_risk"] = restricted
        out["units_basis"] = "reported_buckets" if sum(buckets) + market == int(total) and sum(buckets) > 0 else "total_assumed_restricted"
    ra = _int(row.get("Rental_Assistance_Count"))
    contract = str(row.get("HUD Contract") or "").strip()
    prog = {"Housing Assistance Payment": "HAP", "Rental Assistance Contract": "RAC", "Project Rental Assistance Contract": "PRAC", "Project Assistance Contract": "PAC"}.get(contract, "")
    out["hap_units_at_risk"] = ra if prog in ("HAP", "RAC") else 0
    out["prac_units_at_risk"] = ra if prog in ("PRAC", "PAC") else 0
    out["other_ra_units"] = ra if prog == "" and ra else 0
    out["psh_units_at_risk"] = _int(row.get("PSH_Units"))
    out["family_3br_plus_units"] = _int(row.get("Total_3_BR_Units")) + _int(row.get("Total_4Plus_BR_Units"))
    flags = []
    pt = str(row.get("Property Type") or "").lower()
    if "elderly" in pt:
        flags.append("elderly")
    if "disabled" in pt:
        flags.append("disabled")
    if "veteran" in pt:
        flags.append("veteran")
    if "single room" in pt or "sro" in pt:
        flags.append("sro")
    if out["psh_units_at_risk"] > 0:
        flags.append("psh")
    out["vulnerability_flags"] = ";".join(flags)
    return out


def _events_for(lead: Dict[str, Any]) -> List[Dict[str, Any]]:
    try:
        return json.loads(lead.get("events_in_horizon") or "[]")
    except Exception:
        return []


def fill_units_block(leads: pd.DataFrame, as_of: date) -> pd.DataFrame:
    """Post-merge fills: book-only rows take units_assisted; coterminous_senior_cliff; public_upb_*; recapture_exposure; board_impact."""
    out = leads.copy().astype(object)
    for i, r in out.iterrows():
        units_at_risk = _num(r.get("units_at_risk"))
        if units_at_risk is None:
            ua = _num(r.get("units_assisted")) if "units_assisted" in out.columns else None
            if ua is None:
                ua = _num(r.get("restricted_units"))
            if ua is None:
                ua = _num(r.get("units"))
            if ua is not None:
                out.at[i, "units_at_risk"] = int(ua)
                if r.get("restricted_units") in ("", None):
                    out.at[i, "restricted_units"] = int(ua)
                if r.get("units_basis") in ("", None):
                    out.at[i, "units_basis"] = "proxy" if "units_assisted" not in out.columns or _num(r.get("units_assisted")) is None else "reported_buckets"
                units_at_risk = ua
        for c in ("hap_units_at_risk", "prac_units_at_risk", "other_ra_units", "psh_units_at_risk", "family_3br_plus_units"):
            if r.get(c) in ("", None):
                out.at[i, c] = 0
        # coterminous senior cliff: senior maturity within 24 months of our maturity
        om, sm = parse_iso(r.get("our_maturity")), parse_iso(r.get("senior_maturity"))
        cot = bool(om and sm and abs((om - sm).days) <= 730)
        if not cot and om:
            for e in _events_for(r):
                if e.get("event_type") in ("LOAN_MATURITY", "HUD_DIRECT_LOAN_MATURITY", "HAP_EXPIRATION") and e.get("status") != "STALE_CONTRACT_DATE":
                    d = parse_iso(e.get("event_date"))
                    if d and abs((om - d).days) <= 730:
                        cot = True
        out.at[i, "coterminous_senior_cliff"] = bool(cot) if (om or sm) else ""
        # public upb at risk
        upb = _num(r.get("public_upb"))
        if upb is not None and str(r.get("book_match")) in ("matched", "self_owned", "book_only"):
            cliff_mo = _num(r.get("owner_cliff_months_out")) if "owner_cliff_months_out" in out.columns else None
            if cliff_mo is None:
                d = parse_iso(r.get("owner_cliff_date"))
                cliff_mo = months_between(as_of, d) if d else None
            at_risk = (cliff_mo is not None and cliff_mo <= 36) or str(r.get("covenant_status")) in ("watch", "default") or cot
            out.at[i, "public_upb_at_risk"] = upb if at_risk else 0.0
        elif upb is None:
            out.at[i, "public_upb_at_risk"] = ""
        # recapture exposure
        amt = _num(r.get("recapture_amount"))
        method = str(r.get("recapture_method") or ("none" if not amt else "full"))
        if amt is not None or method == "cdbg_fmv_share":
            rx = recapture_exposure(amt, parse_iso(r.get("recapture_start")) if "recapture_start" in out.columns else None,
                                    parse_iso(r.get("recapture_end")) if "recapture_end" in out.columns else None, as_of, method)
            out.at[i, "recapture_exposure"] = rx["exposure"] if rx["exposure"] is not None else ""
            out.at[i, "public_grant_at_risk"] = rx["exposure"] if rx["exposure"] is not None else ""
            if rx["flag"]:
                vf = str(r.get("verify_flags") or "")
                out.at[i, "verify_flags"] = ";".join([x for x in vf.split(";") if x] + [rx["flag"]])
        # board impact
        band = str(r.get("owner_cliff_band") or "")
        frac = 0.0
        for b, lo, hi, f in URGENCY_BANDS:
            if b == band:
                frac = f
        out.at[i, "board_impact"] = round(float(units_at_risk or 0) * frac, 1)
    return out


def _add(acc: Dict[str, float], r: Dict[str, Any], cols: List[str]) -> None:
    acc["properties"] = acc.get("properties", 0) + 1
    for c in cols:
        if c in ("properties", "rad_section18_status"):
            continue
        if c == "being_preserved_units":
            v = _num(r.get("units_at_risk")) if str(r.get("recap_status")) in ("under_application", "closed") else 0
        elif c == "owned_units":
            v = _num(r.get("units_at_risk")) if str(r.get("book_match")) == "self_owned" else 0
        elif c == "pbv_households":
            v = _num(r.get("hap_units_at_risk")) if "PBV" in str(r.get("programs") or "") or str(r.get("book_kind")) == "administered_contract" else 0
        else:
            v = _num(r.get(c))
        acc[c] = round(acc.get(c, 0) + (v or 0), 1)
    if "rad_section18_status" in cols:
        sig = str(r.get("signals") or "")
        if "RAD_CHAP" in sig or "SECTION_18" in sig:
            acc["rad_section18_status"] = acc.get("rad_section18_status", 0) + 1


def units_at_risk_json(leads: pd.DataFrame, as_of: date, profile: str = "hfa", variant: str = "loan_book", kpi: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """The Board_Totals pivot: by owner_cliff_band, by jurisdiction (county then city), by year, headline, book verdict."""
    cols = OWNED_COLS if variant == "owned_assets" else TOTAL_COLS
    empty = lambda: {c: 0 for c in cols}  # noqa: E731
    by_band: Dict[str, Dict[str, Any]] = {b: empty() for b in BAND_ROWS}
    by_jur: Dict[str, Dict[str, Dict[str, Any]]] = {}
    by_year: Dict[str, Dict[str, Any]] = {str(as_of.year + k): empty() for k in range(0, 11)}
    headline = {"properties": 0, "units_at_risk": 0, "hap_units_at_risk": 0, "prac_units_at_risk": 0, "psh_units_at_risk": 0, "public_upb_at_risk": 0.0, "window_months": 36}
    upb_total = 0.0
    upb_watch = 0.0
    units_le24 = 0.0
    units_total = 0.0
    for r in leads.to_dict(orient="records"):
        if str(r.get("exclusion_reason")) in ("in_development", "outside_geography"):
            continue
        band = str(r.get("owner_cliff_band") or "")
        stale = "hap_date_stale" in str(r.get("signals") or "") and not band
        row_band = band if band in by_band else ("stale_contract_date_verify" if stale else "no_dated_cliff")
        _add(by_band[row_band], r, cols)
        jur = str(r.get("county_name") or "unknown") or "unknown"
        by_jur.setdefault(jur, {b: empty() for b in BAND_ROWS})
        _add(by_jur[jur][row_band], r, cols)
        d = parse_iso(r.get("owner_cliff_date"))
        if d and str(d.year) in by_year:
            _add(by_year[str(d.year)], r, cols)
        mo = months_between(as_of, d) if d else None
        ua = _num(r.get("units_at_risk")) or 0
        units_total += ua
        if mo is not None and mo <= 36 and band in ("OVERDUE", "CRITICAL", "URGENT", "APPROACHING"):
            headline["properties"] += 1
            headline["units_at_risk"] += ua
            headline["hap_units_at_risk"] += _num(r.get("hap_units_at_risk")) or 0
            headline["prac_units_at_risk"] += _num(r.get("prac_units_at_risk")) or 0
            headline["psh_units_at_risk"] += _num(r.get("psh_units_at_risk")) or 0
            headline["public_upb_at_risk"] += _num(r.get("public_upb_at_risk")) or 0
        if mo is not None and mo <= 24:
            units_le24 += ua
        if str(r.get("book_match")) in ("matched", "self_owned", "book_only"):
            upb = _num(r.get("public_upb")) or 0
            upb_total += upb
            if str(r.get("covenant_status")) in ("watch", "default") or (_num(r.get("public_upb_at_risk")) or 0) > 0:
                upb_watch += upb
    for k in ("units_at_risk", "hap_units_at_risk", "prac_units_at_risk", "psh_units_at_risk"):
        headline[k] = int(headline[k])
    headline["public_upb_at_risk"] = round(headline["public_upb_at_risk"], 0)
    share_upb = (upb_watch / upb_total) if upb_total else 0.0
    share_units = (units_le24 / units_total) if units_total else 0.0
    verdict = "CRITICAL" if share_upb >= 0.50 or share_units >= 0.25 else ("STRESSED" if share_upb >= 0.25 or share_units >= 0.12 else ("WATCH" if share_upb >= 0.10 or share_units >= 0.05 else "STABLE"))
    return {"as_of": as_of.isoformat(), "agency_profile": profile, "board_totals_variant": variant, "columns": cols,
            "by_owner_cliff_band": by_band, "by_jurisdiction": by_jur, "by_year": by_year, "headline": headline,
            "public_upb_total": round(upb_total, 0), "public_upb_on_watch": round(upb_watch, 0), "book_verdict": verdict,
            "book_verdict_rule": "CRITICAL >= 50% of book UPB on watch/default or >= 25% of units with a cliff <= 24 mo; STRESSED >= 25% / 12%; WATCH >= 10% / 5%; else STABLE",
            "kpi": kpi or {"units_preserved_since_prior": 0, "units_lost_since_prior": 0, "flips": {}}}
