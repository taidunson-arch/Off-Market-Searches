#!/usr/bin/env python3
"""Write one handoff JSON per sibling skill for the selected tier (references/output-contract.md Section 5), plus
the two analyst worklists the decision-maker step needs: sos_worklist.csv and documents_to_request.csv.

Field maps:
  comp-analyzer                        {subject_address, property_type, unit_count, year_built, valuation_mode: as_is}
  underwriting-market-rate-multifamily {deal_name, asset_address, total_units, year_built, estimated_in_place_rent,
                                        existing_debt{upb, rate, maturity, basis}, needs_sponsor_data[]}
  front-door-lihtc-underwriting        {lihtc_context{credit_type, compliance_start, year15_date, extended_use_end, ami_units,
                                        hud_contract, soft_debt_sources[], sponsor_type, qc_eligible, preservation_notice_status}}
  residential-deal-underwriter         {address, units, value_est, liens[]}
  critical-dates-tracker               {seed_dates[] (event_type/date/basis), documents_to_request[] for every non-RECORDED event}
  forward-pipeline-and-news-intelligence {asset_location, asset_class, deal_strategy}
  legal-title-risk-assessment          {parcel_id, recorded_instruments[]}
  deal-finder                          {leads[]: address, apn, units, property_type}  (run BEFORE outreach; active listing -> on_market)

Worklists (decision-maker-enrichment.md Section 6; output-contract.md Section 5):
  sos_worklist.csv            owner_name_raw, normalized_name, state, registry_search_url, reason, property_ids
                              one row per distinct owner entity whose decision maker is still `not in public record`
  documents_to_request.csv    property_id, property_name, event_type, event_date, basis, document, where_to_get, est_cost
                              one row per non-RECORDED governing event; recorder image cost from market-params
                              (multco_recorder_image_fee, verify: true) when the document is a recorded instrument

Usage: python scripts/make_handoffs.py --leads runs/x/leads_scored.csv --tier A [--tier B] --out-dir runs/x/handoff/ [--pack <dir>]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from omdf.entities import sos_worklist_row  # noqa: E402
from omdf.schema import load_market_params, param  # noqa: E402

DOC_FOR_EVENT = {
    "LOAN_MATURITY": ("loan note / loan agreement; recorded trust deed image (maturity recital)", "recorder image (county) or owner"),
    "HUD_DIRECT_LOAN_MATURITY": ("HUD note and regulatory agreement", "HUD account executive / owner"),
    "USDA_515_MATURITY": ("RD promissory note / restrictive-use covenant", "USDA RD state office / owner"),
    "SOFT_LOAN_MATURITY": ("soft-loan note and trust deed", "recorder image; PHB / OHCS records request"),
    "LIHTC_EXTENDED_USE_END": ("LURA / Reservation and Extended Use Agreement", "recorder image (recorded declaration); OHCS"),
    "LIHTC_COMPLIANCE_END": ("Forms 8609 (first credit year) and partnership agreement (ROFR / purchase option)", "owner / syndicator"),
    "HAP_EXPIRATION": ("HAP contract and latest renewal (TRACS)", "HUD MF Assistance & Sec 8 database; PBCA"),
    "SOFT_PROGRAM_END": ("program regulatory agreement / declaration of restrictive covenants", "recorder image; OHCS"),
    "REGULATORY_LATEST_END": ("every recorded regulatory agreement on title", "title report; recorder index"),
    "PREPAY_WINDOW_OPEN": ("note prepayment rider", "owner / servicer"),
    "IO_EXPIRATION": ("note / loan agreement", "owner / tape"),
    "PRESERVATION_NOTICE_WINDOW": ("PuSH owner notice (first / second) if any was filed", "records request: OHCS PuSH-CP Program Manager; affected city"),
    "HAP_OPTOUT_NOTICE_DEADLINE": ("Section 8 opt-out / renewal-intent notice", "PBCA / HUD contract administrator records request"),
    "RATE_CAP_EXPIRY": ("rate-cap agreement and bridge loan agreement", "owner; SOS UCC collateral description"),
}
RECORDER_DOCS = {"LOAN_MATURITY", "SOFT_LOAN_MATURITY", "LIHTC_EXTENDED_USE_END", "SOFT_PROGRAM_END", "REGULATORY_LATEST_END"}


def _events(lead: Dict[str, Any]) -> List[Dict[str, Any]]:
    try:
        return json.loads(lead.get("events_in_horizon") or "[]")
    except Exception:
        return []


def _programs(lead) -> List[str]:
    return [p for p in str(lead.get("programs") or "").split(";") if p]


def _num(v):
    try:
        return float(str(v).replace(",", "")) if str(v).strip() not in ("", "nan") else None
    except ValueError:
        return None


def _first(evs, types):
    for e in evs:
        if e.get("event_type") in types:
            return e
    return None


def handoffs_for(lead: Dict[str, Any]) -> Dict[str, Any]:
    evs = _events(lead)
    cls = lead.get("asset_class")
    progs = _programs(lead)
    out: Dict[str, Any] = {}
    out["deal-finder"] = {"leads": [{"address": lead.get("address"), "apn": lead.get("property_id") if not str(lead.get("property_id", "")).startswith("addr:") else None,
                                     "units": _num(lead.get("units")), "property_type": "multifamily" if cls != "sfr_small_res" else "residential"}],
                          "instruction": "dedupe against active listings before outreach; any hit sets on_market=true"}
    out["comp-analyzer"] = {"subject_address": lead.get("address"), "property_type": "multifamily" if cls != "sfr_small_res" else "residential",
                            "unit_count": _num(lead.get("units")), "year_built": lead.get("year_built"), "valuation_mode": "as_is",
                            "replaces": {"est_value": _num(lead.get("est_value")), "value_source": lead.get("value_source")}}
    debt = _first(evs, {"LOAN_MATURITY", "HUD_DIRECT_LOAN_MATURITY", "USDA_515_MATURITY"})
    out["critical-dates-tracker"] = {
        "seed_dates": [{"event_type": e.get("event_type"), "date": e.get("event_date"), "basis": e.get("basis"), "source": e.get("source"),
                        "verify_flag": e.get("verify_flag") or None, "alt_dates": e.get("alt_dates") or None} for e in evs],
        "documents_to_request": sorted({DOC_FOR_EVENT.get(e.get("event_type"), ("source document", ""))[0] for e in evs if e.get("basis") != "RECORDED"}),
    }
    out["legal-title-risk-assessment"] = {"parcel_id": lead.get("property_id"), "address": lead.get("address"),
                                          "recorded_instruments": [e for e in evs if e.get("basis") == "RECORDED"],
                                          "ask": "confirm recorded trust deeds, balances, junior liens, regulatory agreements and any Notice of Right of First Refusal"}
    if cls == "affordable_regulated":
        strategy = "Year-15 LIHTC resyndication / preservation acquisition" if _first(evs, {"LIHTC_COMPLIANCE_END"}) else \
            ("expiring-use preservation acquisition" if _first(evs, {"LIHTC_EXTENDED_USE_END", "REGULATORY_LATEST_END"}) else "HAP renewal-with-sale / preservation recap")
        y15 = _first(evs, {"LIHTC_COMPLIANCE_END"}); eue = _first(evs, {"LIHTC_EXTENDED_USE_END"})
        out["front-door-lihtc-underwriting"] = {"mode": "composition", "lihtc_context": {
            "credit_type": "9%" if "LIHTC_9" in progs else ("4%" if "LIHTC_4" in progs else "none/unknown"),
            "compliance_start": None, "year15_date": y15.get("event_date") if y15 else None, "year15_basis": y15.get("basis") if y15 else None,
            "extended_use_end": eue.get("event_date") if eue else None,
            "ami_units": {"le_60": _num(lead.get("ami_30_60_units")), "80": _num(lead.get("ami_80_units")), "market": _num(lead.get("market_rate_units"))},
            "hud_contract": lead.get("hud_contract") or None, "rental_assistance_units": _num(lead.get("rental_assistance_units")),
            "soft_debt_sources": [p for p in progs if p in ("HOME", "OAHTC", "GHAP", "HDGP", "LIFT", "HTF", "OTHER_OHCS")],
            "sponsor_type": lead.get("owner_type"), "qc_eligible": "QC_ELIGIBILITY" in {e.get("event_type") for e in evs},
            "preservation_notice_status": "received" if _first(evs, {"PRESERVATION_NOTICE_RECEIVED"}) else ("window open now; request records" if "push_window_open" in str(lead.get("signals") or "") else "none on file"),
            "needs_sponsor_data": ["rent roll / max rents by AMI band", "T-12 operating statement", "existing debt terms", "partnership agreement (ROFR / purchase option)", "LURA"]}}
    elif cls == "market_rate_mf":
        strategy = "maturity-driven recapitalization or sale of existing apartments"
        out["underwriting-market-rate-multifamily"] = {
            "deal_name": lead.get("property_name"), "asset_address": lead.get("address"), "total_units": _num(lead.get("units")), "year_built": lead.get("year_built"),
            "estimated_in_place_rent": None,
            "existing_debt": {"upb": _num(lead.get("est_loan_balance")), "rate": _num(lead.get("note_rate")), "maturity": debt.get("event_date") if debt else None,
                              "basis": debt.get("basis") if debt else None, "lender_type": lead.get("lender_type") or None},
            "needs_sponsor_data": ["unit mix and in-place rents", "T-12 OpEx", "existing note terms", "capex plan"]}
    else:
        strategy = "distressed or estate residential acquisition"
        out["residential-deal-underwriter"] = {"address": lead.get("address"), "units": _num(lead.get("units")), "value_est": _num(lead.get("est_value")),
                                               "value_source": lead.get("value_source"),
                                               "liens": [e for e in evs if e.get("event_type") in ("HECM_ON_RECORD", "DOR_DEFERRAL_LIEN", "JUDGMENT_LIEN", "MECHANICS_LIEN", "TAX_DELINQUENT_YEARS")]}
    out["forward-pipeline-and-news-intelligence"] = {"asset_location": f"{lead.get('address')}, {lead.get('city')}, {lead.get('county_name')} County", "asset_class": cls, "deal_strategy": strategy}
    return out


def _state_for(lead: Dict[str, Any]) -> str:
    f = str(lead.get("county_fips") or "")
    return {"41": "OR", "53": "WA"}.get(f[:2], "OR")


def worklist_rows(sel: pd.DataFrame) -> List[Dict[str, str]]:
    """Group selected leads by owner entity; one SOS worklist row per entity still unresolved."""
    groups: Dict[tuple, Dict[str, Any]] = {}
    for lead in sel.to_dict(orient="records"):
        name = str(lead.get("owner_name") or "").strip()
        if not name:
            continue
        if str(lead.get("contact_grade") or "C") == "A" and str(lead.get("decision_maker_name") or "") not in ("", "not in public record"):
            continue
        ot = str(lead.get("owner_type") or "unknown")
        reason = {"lihtc_partnership_forprofit_gp": "gp_resolution", "lihtc_partnership_nonprofit_gp": "gp_resolution",
                  "single_asset_llc": "manager_resolution", "regional_operator": "sibling_cluster", "nonprofit": "status_check",
                  "unknown": "manager_resolution"}.get(ot, "status_check")
        key = (name.upper(), _state_for(lead))
        g = groups.setdefault(key, {"name": name, "state": key[1], "reason": reason, "pids": []})
        g["pids"].append(str(lead.get("property_id")))
    return [sos_worklist_row(g["name"], g["state"], g["pids"], g["reason"]) for g in groups.values()]


def document_rows(sel: pd.DataFrame, image_fee) -> List[Dict[str, Any]]:
    rows = []
    for lead in sel.to_dict(orient="records"):
        for e in _events(lead):
            if e.get("basis") == "RECORDED" or e.get("direction") == "SUPPRESSION":
                continue
            et = e.get("event_type")
            doc, where = DOC_FOR_EVENT.get(et, ("source document", "owner"))
            cost = ""
            if et in RECORDER_DOCS and image_fee is not None and str(lead.get("county_fips") or "") == "41051":
                cost = f"${image_fee} per Multnomah image (fee from market-params, verify: true)"
            elif et in RECORDER_DOCS and str(lead.get("county_fips") or "").startswith("53"):
                cost = "free (Clark County WA images online; unverified)"
            elif et in RECORDER_DOCS:
                cost = "county image fee unverified"
            rows.append({"property_id": lead.get("property_id"), "property_name": lead.get("property_name"), "tier": lead.get("tier"), "event_type": et,
                         "event_date": e.get("event_date"), "basis": e.get("basis"), "document": doc, "where_to_get": where, "est_cost": cost})
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--leads", required=True)
    ap.add_argument("--tier", action="append", default=None, help="tier(s) to export (default A)")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--max", type=int, default=50)
    ap.add_argument("--pack", default=None, help="market pack (for the recorder image fee in documents_to_request.csv)")
    a = ap.parse_args(argv)
    tiers = a.tier or ["A"]
    leads = pd.read_csv(a.leads, dtype=str, keep_default_na=False)
    sel = leads[leads["tier"].isin(tiers)].head(a.max) if "tier" in leads.columns else leads.head(a.max)
    os.makedirs(a.out_dir, exist_ok=True)
    per_sibling: Dict[str, List[Dict[str, Any]]] = {}
    for lead in sel.to_dict(orient="records"):
        h = handoffs_for(lead)
        for sib, payload in h.items():
            per_sibling.setdefault(sib, []).append({"property_id": lead.get("property_id"), "property_name": lead.get("property_name"),
                                                    "tier": lead.get("tier"), "route": lead.get("route"), "payload": payload})
    for sib, items in per_sibling.items():
        with open(os.path.join(a.out_dir, f"{sib}.json"), "w", encoding="utf-8") as fh:
            json.dump({"skill": sib, "from": "off-market-deal-finder", "count": len(items), "items": items}, fh, indent=2, default=str)
    params = load_market_params(a.pack)
    fee = param(params, "multco_recorder_image_fee", None)
    wl = worklist_rows(sel)
    pd.DataFrame(wl, columns=["owner_name_raw", "normalized_name", "state", "registry_search_url", "reason", "property_ids"]).to_csv(os.path.join(a.out_dir, "sos_worklist.csv"), index=False)
    docs = document_rows(sel, fee)
    pd.DataFrame(docs, columns=["property_id", "property_name", "tier", "event_type", "event_date", "basis", "document", "where_to_get", "est_cost"]).to_csv(os.path.join(a.out_dir, "documents_to_request.csv"), index=False)
    print(f"[handoffs] {len(sel)} leads (tiers {tiers}) -> {len(per_sibling)} sibling payload files, sos_worklist.csv ({len(wl)} entities), documents_to_request.csv ({len(docs)} rows) in {a.out_dir}")


if __name__ == "__main__":
    main()
