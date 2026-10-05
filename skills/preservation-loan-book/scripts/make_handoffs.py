#!/usr/bin/env python3
"""Write one handoff JSON per sibling skill for the selected routes (references/output-contract.md Section 7), plus the agency worklists:
sos_worklist.csv (organization level), documents_to_request.csv (the agency's own file room first), board_packet.csv (organization + registered agent only).

Siblings and triggers:
  critical-dates-tracker            every selected lead: seed_dates[] (owner cliffs + agency act-by dates) and documents_to_request[]
  front-door-lihtc-underwriting     recap_committee / nofa_offer: composition mode, v2 lihtc_context field names + agency_soft_debt[]
  sizing-lihtc-permanent-debt       recap_committee / servicing_watch on our book: before / after recast scenarios
  physical-condition-assessment     physical factor fired (REAC < 80, code case, dangerous building)
  lihtc-lpa-reviewer                designee_rofr / recap_committee on a LIHTC partnership (review_focus ["2C"])
  sponsor-credibility-assessor      only when recap_status in {announced, under_application} (trigger recorded in payload)
  off-market-deal-finder            NOAH rows only (asset_class noah_unregulated; owner_outreach false; purpose public_acquisition_screen)
  forward-pipeline-and-news-intelligence  preservation_strategy text per route
"from" is preservation-loan-book. No buyer payloads (deal-finder, comp-analyzer, underwriting-market-rate-multifamily, residential-deal-underwriter).

Usage: python scripts/make_handoffs.py --leads-scored runs/x/leads_scored.csv [--routes optout_response notice_compliance ...] [--queue ESCALATE ACT PLAN] --out-dir runs/x/handoff [--pack <dir>] [--max 200]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plb.entities import sos_worklist_row  # noqa: E402
from plb.pii import apply_pii_scope  # noqa: E402
from plb.schema import ROUTES, load_market_params, param  # noqa: E402

DOC_FOR_EVENT = {
    "AGENCY_LOAN_MATURITY": ("our note / loan agreement (maturity, payment type, extension rights)", "agency file room"),
    "AFFORDABILITY_PERIOD_END": ("HOME / program written agreement and recorded covenant (affordability period)", "agency file room; recorder image if the covenant is missing from the file"),
    "GRANT_RECAPTURE_END": ("grant agreement (recapture / resale provisions)", "agency file room"),
    "SHARED_APPRECIATION_DUE": ("shared-appreciation note", "agency file room"),
    "LOAN_MATURITY": ("senior loan note / recorded trust deed (maturity recital)", "senior lender via owner; recorder image"),
    "HUD_DIRECT_LOAN_MATURITY": ("HUD note and regulatory / use agreement", "HUD MF asset manager"),
    "USDA_515_MATURITY": ("RD promissory note / restrictive-use covenant", "USDA RD state office"),
    "LIHTC_EXTENDED_USE_END": ("LURA / Reservation and Extended Use Agreement", "our own file first; recorder image second"),
    "LIHTC_COMPLIANCE_END": ("Forms 8609 (first credit year); partnership agreement (ROFR / purchase option)", "our compliance file; owner"),
    "HAP_EXPIRATION": ("HAP contract and latest renewal request (HUD-9624)", "contract administrator (PBCA / HUD)"),
    "STALE_CONTRACT_DATE": ("current HAP contract / TRACS expiration", "contract administrator"),
    "QC_ELIGIBILITY": ("qualified-contract request and QC price certification", "owner (via our QC procedure)"),
    "SOFT_PROGRAM_END": ("program regulatory agreement / declaration of restrictive covenants", "our own file first; recorder image second"),
    "REGULATORY_LATEST_END": ("every recorded regulatory agreement on title", "title report; recorder index"),
    "PRESERVATION_NOTICE_WINDOW": ("owner's PuSH first / second notice if filed", "PuSH-CP notice log (OHCS); affected city file"),
    "PRESERVATION_NOTICE_RECEIVED": ("the owner's notice as logged; property records request response", "PuSH-CP notice log"),
    "COVENANT_END": ("local regulatory agreement", "agency file room"),
}
RECORDER_DOCS = {"LIHTC_EXTENDED_USE_END", "SOFT_PROGRAM_END", "REGULATORY_LATEST_END", "AFFORDABILITY_PERIOD_END", "LOAN_MATURITY"}
STRATEGY = {"optout_response": "HAP opt-out response: CA letter review, MU2M / 20-year counteroffer, nonprofit transfer with HAP assignment",
            "notice_compliance": "PuSH notice compliance: audit owner notices, assert the withdrawal bar and per-tenant extension, designee appointment on silence",
            "qc_admin": "qualified-contract administration: present a bona fide contract inside the one-year period",
            "designee_rofr": "qualified purchaser: record the ROFR, run the 30-day match from the mailing date, assign to a mission sponsor",
            "recap_committee": "loan recast / extension / resubordination on our book; 4% recapitalization",
            "servicing_watch": "covenant monitoring and troubled-asset asset management on our book",
            "nofa_offer": "preservation NOFA / gap award to a mission sponsor before the cliff",
            "ta_sponsor": "technical assistance to a nonprofit / PHA sponsor for the 42(i)(7) ROFR or recapitalization"}


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
    progs = _programs(lead)
    route = str(lead.get("primary_route") or "none")
    routes = {route} | {r for r in str(lead.get("secondary_routes") or "").split(";") if r}
    sig = str(lead.get("signals") or "")
    out: Dict[str, Any] = {}
    seeds = [{"event_type": e.get("event_type"), "date": e.get("event_date"), "basis": e.get("basis"), "source": e.get("source"), "verify_flag": e.get("verify_flag") or None,
              "alt_dates": e.get("alt_dates") or None, "status": e.get("status")} for e in evs]
    if lead.get("agency_action_date"):
        seeds.append({"event_type": lead.get("agency_action_type"), "date": lead.get("agency_action_date"), "basis": lead.get("agency_action_basis") or "DERIVED",
                      "source": "plb/agency_calendar.py", "verify_flag": None, "alt_dates": None, "status": "agency act-by (notice-deadline trap: urgency runs off this date)"})
    out["critical-dates-tracker"] = {"seed_dates": seeds, "scale_note": "months in this pack; critical-dates-tracker bands are days; never join on band label",
                                     "documents_to_request": sorted({DOC_FOR_EVENT.get(e.get("event_type"), ("source document", ""))[0] for e in evs if e.get("basis") != "RECORDED"} |
                                                                    ({"the PuSH notice clause of the regulatory agreement (notice address)"} if "notice_compliance" in routes else set()))}
    y15 = _first(evs, {"LIHTC_COMPLIANCE_END"}); eue = _first(evs, {"LIHTC_EXTENDED_USE_END"})
    if routes & {"recap_committee", "nofa_offer"}:
        out["front-door-lihtc-underwriting"] = {"mode": "composition", "lihtc_context": {
            "credit_type": "9%" if "LIHTC_9" in progs else ("4%" if "LIHTC_4" in progs else "none/unknown"), "compliance_start": None,
            "year15_date": y15.get("event_date") if y15 else None, "year15_basis": y15.get("basis") if y15 else None, "extended_use_end": eue.get("event_date") if eue else None,
            "ami_units": {"le_60": _num(lead.get("ami_30_60_units")), "80": _num(lead.get("ami_80_units")), "market": _num(lead.get("market_rate_units"))},
            "hud_contract": lead.get("hud_contract") or None, "rental_assistance_units": _num(lead.get("rental_assistance_units")),
            "soft_debt_sources": [p for p in progs if p in ("HOME", "OAHTC", "GHAP", "HDGP", "LIFT", "HTF", "OTHER_OHCS", "CDBG", "PHB_LOAN", "TIF", "LEVY")],
            "sponsor_type": lead.get("owner_type"), "qc_eligible": "QC_ELIGIBILITY" in {e.get("event_type") for e in evs},
            "preservation_notice_status": lead.get("notice_status") or "unknown"},
            "agency_soft_debt": [{"agency_loan_id": lead.get("agency_loan_ids") or None, "grant_id": lead.get("grant_ids") or None, "program": lead.get("agency_programs") or None,
                                  "upb": _num(lead.get("public_upb")), "rate": _num(lead.get("our_rate")), "payment_type": lead.get("payment_type") or None, "maturity": lead.get("our_maturity") or None,
                                  "affordability_end": lead.get("affordability_end") or None, "recapture_type": lead.get("recapture_type") or None}] if lead.get("universe") == "our_book" else [],
            "needs_sponsor_data": ["rent roll / max rents by AMI band", "T-12 operating statement", "senior debt terms", "partnership agreement (ROFR / purchase option)", "LURA"]}
    if routes & {"recap_committee", "servicing_watch"} and lead.get("universe") == "our_book" and _num(lead.get("public_upb")):
        upb = _num(lead.get("public_upb"))
        out["sizing-lihtc-permanent-debt"] = {"lender_type": "state_HFA", "state_hfa": "OHCS", "dscr_floor_source": "agency_program_manual",
                                              "noi_year1": _num(lead.get("est_restricted_noi")), "scenarios": [
                                                  {"name": "before_recast", "mandatory_soft_debt_annual": None, "note": f"our note {lead.get('payment_type') or 'payment type unknown'} UPB {upb:,.0f}"},
                                                  {"name": "after_recast", "residual_receipts_soft_debt": upb, "mandatory_soft_debt_annual": 0, "note": "our note converted to residual receipts / 0% / extended"}],
                                              "ask": "max_loan, binding_constraint and DSCR flags per scenario; the agency decides the recast"}
    if any(e.get("event_type") in ("REAC_SCORE", "CODE_CASE_OPEN", "DANGEROUS_BUILDING", "NONCOMPLIANCE_FINDING") for e in evs) or "reac_below_60" in sig:
        out["physical-condition-assessment"] = {"property_address": lead.get("address"), "year_built": lead.get("year_built"), "unit_count": _num(lead.get("units")),
                                                "deal_strategy": "preservation_rehab", "label": "ESTIMATED/DERIVED desktop; not the program CNA, not an ASTM PCA"}
    if routes & {"designee_rofr", "recap_committee"} and str(lead.get("owner_type", "")).startswith("lihtc_partnership"):
        out["lihtc-lpa-reviewer"] = {"deal_name": lead.get("property_name"), "deal_state": "OR", "document_type": "full_lpa", "gp_entity": lead.get("owner_name"), "lp_investor": None,
                                     "review_focus": ["2C"], "ask": "Year-15 exit / 42(i)(7) ROFR read on the LPA in our file; consume rofr_42i7_compliant as RECORDED evidence"}
    if str(lead.get("recap_status") or "none") in ("announced", "under_application"):
        out["sponsor-credibility-assessor"] = {"organization": lead.get("owner_name"), "type": "nonprofit" if "nonprofit" in str(lead.get("owner_type")) else ("pha" if lead.get("owner_type") == "housing_authority" else "for_profit"),
                                               "trigger": f"recap_status {lead.get('recap_status')}", "target_deal": {"units": _num(lead.get("units")), "credit_type": "4%" if "LIHTC_4" in progs else "9%/unknown", "recap": True},
                                               "portfolio_year15_30_events_36mo": _num(lead.get("sponsor_cliff_count"))}
    if lead.get("asset_class") == "noah_unregulated":
        out["off-market-deal-finder"] = {"asset_class": "market_rate_mf", "geography": {"county_fips": lead.get("county_fips")}, "property_ids": [lead.get("property_id")],
                                         "owner_outreach": False, "purpose": "public_acquisition_screen"}
    out["forward-pipeline-and-news-intelligence"] = {"asset_location": f"{lead.get('address')}, {lead.get('city')}, {lead.get('county_name')} County", "asset_class": lead.get("asset_class"),
                                                     "preservation_strategy": STRATEGY.get(route, "monitoring")}
    return out


def _state_for(lead: Dict[str, Any]) -> str:
    f = str(lead.get("county_fips") or "")
    return {"41": "OR", "53": "WA"}.get(f[:2], "OR")


def worklist_rows(sel: pd.DataFrame) -> List[Dict[str, str]]:
    groups: Dict[tuple, Dict[str, Any]] = {}
    for lead in sel.to_dict(orient="records"):
        name = str(lead.get("owner_name") or "").strip()
        if not name or str(lead.get("book_match")) == "self_owned":
            continue
        if str(lead.get("org_resolution_grade") or "C") == "A" and str(lead.get("registered_agent") or ""):
            continue
        ot = str(lead.get("owner_type") or "unknown")
        reason = {"lihtc_partnership_forprofit_gp": "gp_and_registered_agent", "lihtc_partnership_nonprofit_gp": "gp_and_registered_agent", "unknown": "entity_resolution",
                  "individual_owner_of_record": "notice_address_only"}.get(ot, "registered_agent_and_status")
        key = (name.upper(), _state_for(lead))
        g = groups.setdefault(key, {"name": name, "state": key[1], "reason": reason, "pids": []})
        g["pids"].append(str(lead.get("property_id")))
    return [sos_worklist_row(g["name"], g["state"], g["pids"], g["reason"]) for g in groups.values()]


def document_rows(sel: pd.DataFrame, image_fee) -> List[Dict[str, Any]]:
    rows = []
    for lead in sel.to_dict(orient="records"):
        for e in _events(lead):
            if e.get("direction") == "SUPPRESSION":
                continue
            et = e.get("event_type")
            if e.get("status") == "STALE_CONTRACT_DATE":
                et = "STALE_CONTRACT_DATE"
            elif e.get("basis") == "RECORDED":
                continue
            doc, where = DOC_FOR_EVENT.get(et, ("source document", "owner"))
            cost = ""
            if et in RECORDER_DOCS and image_fee is not None and str(lead.get("county_fips") or "") == "41051":
                cost = f"${image_fee} per Multnomah image only if absent from our own file (fee from market-params, verify)"
            rows.append({"property_id": lead.get("property_id"), "property_name": lead.get("property_name"), "queue_band": lead.get("queue_band"), "primary_route": lead.get("primary_route"),
                         "event_type": et, "event_date": e.get("event_date"), "basis": e.get("basis"), "document": doc, "where_to_get": where, "est_cost": cost})
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--leads-scored", "--leads", dest="leads", required=True)
    ap.add_argument("--routes", nargs="*", default=None, help="primary routes to export (default: all eight)")
    ap.add_argument("--queue", nargs="*", default=None, help="queue bands to export (default ESCALATE ACT PLAN)")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--max", type=int, default=200)
    ap.add_argument("--pack", default=None)
    a = ap.parse_args(argv)
    routes = a.routes or list(ROUTES)
    queues = a.queue or ["ESCALATE", "ACT", "PLAN"]
    leads = pd.read_csv(a.leads, dtype=str, keep_default_na=False)
    sel = leads[leads["primary_route"].isin(routes) & leads["queue_band"].isin(queues)].head(a.max) if "primary_route" in leads.columns else leads.head(a.max)
    os.makedirs(a.out_dir, exist_ok=True)
    per_sibling: Dict[str, List[Dict[str, Any]]] = {}
    for lead in sel.to_dict(orient="records"):
        for sib, payload in handoffs_for(lead).items():
            per_sibling.setdefault(sib, []).append({"property_id": lead.get("property_id"), "property_name": lead.get("property_name"), "queue_band": lead.get("queue_band"),
                                                    "primary_route": lead.get("primary_route"), "payload": payload})
    for sib, items in per_sibling.items():
        with open(os.path.join(a.out_dir, f"{sib}.json"), "w", encoding="utf-8") as fh:
            json.dump({"skill": sib, "from": "preservation-loan-book", "count": len(items), "items": items}, fh, indent=2, default=str)
    params = load_market_params(a.pack)
    fee = param(params, "multco_recorder_image_fee", None)
    wl = worklist_rows(sel)
    pd.DataFrame(wl, columns=["owner_name_raw", "normalized_name", "state", "registry_search_url", "reason", "property_ids"]).to_csv(os.path.join(a.out_dir, "sos_worklist.csv"), index=False)
    docs = document_rows(sel, fee)
    pd.DataFrame(docs, columns=["property_id", "property_name", "queue_band", "primary_route", "event_type", "event_date", "basis", "document", "where_to_get", "est_cost"]).to_csv(
        os.path.join(a.out_dir, "documents_to_request.csv"), index=False)
    packet, _ = apply_pii_scope(leads[leads["primary_route"].isin(routes)] if "primary_route" in leads.columns else leads, "public_packet")
    packet.to_csv(os.path.join(a.out_dir, "board_packet.csv"), index=False)
    print(f"[handoffs] {len(sel)} leads (routes {routes}; queues {queues}) -> {len(per_sibling)} sibling payload files, sos_worklist.csv ({len(wl)} entities), "
          f"documents_to_request.csv ({len(docs)} rows), board_packet.csv ({len(packet)} rows, public_packet scope) in {a.out_dir}")


if __name__ == "__main__":
    main()
