"""Agency calendar: the dates the agency must act (references/agency-calendar.md).

derive(leads, events, as_of, params, profile) returns (leads, events) with:
  * withdrawal_anchor_date / push_anchor_source per property (restriction-type ends only; HAP/PRAC enter the anchor only
    with a non-renewal signal)
  * PRESERVATION_NOTICE_WINDOW x2 (push_first_window 36..30, push_second_window 30..24) and the AGENCY_DEADLINE events
    PUSH_WINDOW_PREP, PUSH_FIRST_NOTICE_DUE, PUSH_SECOND_NOTICE_DUE, TENANT_NOTICE_WINDOW, RECORDS_REQUEST_DUE,
    RECORDS_RESPONSE_DUE, ROFR_MATCH_DEADLINE, QC_RESPONSE_DUE, HAP_OPTOUT_NOTICE_DEADLINE, HAP_OPTOUT_PACKAGE_DUE,
    INSPECTION_DUE, USDA_PUBLIC_BODY_OFFER_WINDOW_END
  * NOTICE_COMPLIANCE_BREACH when PUSH_FIRST_NOTICE_DUE passed and notice_status = not_received_confirmed
  * STALE_CONTRACT_DATE status on past HAP/PRAC/PAC expirations with no termination evidence (no deadlines derive from them)
  * notice_window_state, owner_cliff_*, agency_action_*, action_band on the lead
Every statutory figure is a pack parameter and unverified in this build (verified_live false).
"""
from __future__ import annotations

import json
from datetime import date
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from .adapters import EIH_KEYS, make_event
from .dates import add_days, add_months, months_between, parse_iso, urgency_band
from .schema import (EVENT_COLUMNS, FLAG_MISSING_SOURCE, FLAG_PUSH_COVERAGE, FLAG_STALE_CONTRACT, HAP_LIKE_PROGRAMS, HELPER_EVENTS, NOT_OWNER_CLIFF, PRAC_LIKE_PROGRAMS,
                     PUSH_COVERED_PROGRAMS, WITHDRAWAL_ANCHOR_EVENTS, clean_numeric, param)

SOURCE = "agency_calendar (plb/agency_calendar.py)"

# event_type -> agency owner role, statutory cite, derives_from. Mirrors references/agency-calendar.md Section 4.
AGENCY_DEADLINE_META: Dict[str, Dict[str, Any]] = {
    "PUSH_WINDOW_PREP": {"agency_owner": "push_program_manager", "statutory_cite": "internal prep date (anchor - 36 months); no statutory basis found for a 36-month owner-notice start", "verified_live": False, "derives_from": "withdrawal_anchor_date"},
    "PUSH_FIRST_NOTICE_DUE": {"agency_owner": "push_program_manager", "statutory_cite": "ORS 456.260 / OAR 813-115-0030 (owner notice no sooner than 30 months before withdrawal); ORS 456.262 designee-appointment trigger at 30 months ('whichever is earlier')", "verified_live": False, "derives_from": "withdrawal_anchor_date"},
    "PUSH_SECOND_NOTICE_DUE": {"agency_owner": "push_program_manager", "statutory_cite": "ORS 456.260 / OAR 813-115-0030 (owner notice at least 24 months before withdrawal; the (1)/(2) split is unread)", "verified_live": False, "derives_from": "withdrawal_anchor_date"},
    "TENANT_NOTICE_WINDOW": {"agency_owner": "compliance_officer", "statutory_cite": "SB 973 (2025); ORS 456.259", "verified_live": False, "derives_from": "withdrawal_anchor_date"},
    "RECORDS_REQUEST_DUE": {"agency_owner": "push_program_manager", "statutory_cite": "OAR 813-115-0050 (qualified purchaser access to property, records and documents; ORS 456.262(6)-(7)); 10-day target is internal", "verified_live": False, "derives_from": "PRESERVATION_NOTICE_RECEIVED"},
    "RECORDS_RESPONSE_DUE": {"agency_owner": "push_program_manager", "statutory_cite": "OAR 813-115-0050; 30-day response period not found in rule text (working target)", "verified_live": False, "derives_from": "records request date"},
    "ROFR_RECORDABLE_DATE": {"agency_owner": "legal_counsel", "statutory_cite": "ORS 456.262 (Notice of ROFR recordable after 30 days from the qualified purchaser's offer); OAR 813-115-0060 (recording)", "verified_live": False, "derives_from": "qp_offer_delivered_date"},
    "ROFR_MATCH_DEADLINE": {"agency_owner": "legal_counsel", "statutory_cite": "ORS 456.263; OAR 813-115-0070", "verified_live": False, "derives_from": "THIRD_PARTY_OFFER_RECEIVED"},
    "QC_RESPONSE_DUE": {"agency_owner": "compliance_officer", "statutory_cite": "IRC 42(h)(6)(I)", "verified_live": False, "derives_from": "QC_ELIGIBILITY (requested)"},
    "HAP_OPTOUT_NOTICE_DEADLINE": {"agency_owner": "pbca_liaison", "statutory_cite": "42 U.S.C. 1437f(c)(8); 24 CFR 402.8", "verified_live": False, "derives_from": "HAP_EXPIRATION"},
    "HAP_OPTOUT_PACKAGE_DUE": {"agency_owner": "pbca_liaison", "statutory_cite": "Section 8 Renewal Policy Guide ch. 11", "verified_live": False, "derives_from": "HAP_EXPIRATION"},
    "INSPECTION_DUE": {"agency_owner": "compliance_officer", "statutory_cite": "24 CFR 92.504(d); 26 CFR 1.42-5", "verified_live": False, "derives_from": "last_inspection_date"},
    "USDA_PUBLIC_BODY_OFFER_WINDOW_END": {"agency_owner": "rd_state_office", "statutory_cite": "7 CFR 3560.659", "verified_live": False, "derives_from": "USDA_PREPAY_REQUEST_RECEIVED"},
}
NON_RENEWAL_DETAILS = {"hap_optout"}


def _num(v):
    x = clean_numeric(v, as_int=False)
    return None if x is None else float(x)


def _mk(pid: str, etype: str, d: date, as_of: date, derivation: str, detail: str = "", basis: str = "DERIVED", **kw) -> Dict[str, Any]:
    ev = make_event(pid, etype, d, basis, SOURCE, as_of, as_of.isoformat(), derivation=derivation, detail=detail, **kw)
    return ev


def deadlines_from_servicing_row(pid: str, row: Dict[str, Any], as_of: date, params: Dict[str, Any], units: Optional[float] = None,
                                 programs: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """AGENCY_DEADLINE events that depend only on the agency's own ledger columns (shared by the adapter and derive())."""
    out: List[Dict[str, Any]] = []
    programs = programs or []
    qd = parse_iso(row.get("qc_request_complete_date")) or parse_iso(row.get("qc_request_date"))
    if qd and str(row.get("qc_waived") or "").lower() != "true":
        anchor_note = "" if parse_iso(row.get("qc_request_complete_date")) else "; qc_request_date only (Needs Anchor Date for the complete request)"
        out.append(_mk(pid, "QC_RESPONSE_DUE", add_months(qd, int(param(params, "qc_response_months", 12))), as_of,
                       f"qc_request_complete_date {qd} + 1 year (IRC 42(h)(6)(I), verify){anchor_note}", detail="QC_ELIGIBILITY requested"))
    md = parse_iso(row.get("third_party_offer_mailed_date"))
    rd = parse_iso(row.get("third_party_offer_received_date"))
    if md or rd:
        base = md or rd
        out.append(_mk(pid, "ROFR_MATCH_DEADLINE", add_days(base, int(param(params, "rofr_match_days", 30))), as_of,
                       f"third_party_offer_{'mailed' if md else 'received'}_date {base} + 30 days (ORS 456.263, verify)", detail="THIRD_PARTY_OFFER_RECEIVED",
                       verify_flag="" if md else "Verify — Mailing Date"))
    if str(row.get("notice_log_status") or "").lower() == "received":
        nd = parse_iso(row.get("notice_received_date")) or as_of
        out.append(_mk(pid, "RECORDS_REQUEST_DUE", add_days(nd, int(param(params, "records_request_after_notice_days", 10))), as_of,
                       f"PRESERVATION_NOTICE_RECEIVED {nd} + 10 days (qualified purchaser's records right follows the owner's notice)", detail="PRESERVATION_NOTICE_RECEIVED"))
    qp = parse_iso(row.get("qp_offer_delivered_date"))
    if qp:
        out.append(_mk(pid, "ROFR_RECORDABLE_DATE", add_days(qp, int(param(params, "rofr_recordable_days_after_offer", 30))), as_of,
                       f"qp_offer_delivered_date {qp} + 30 days: earliest date the Notice of ROFR may be recorded (ORS 456.262, verify)", detail="qp_offer_delivered_date"))
    rq = parse_iso(row.get("records_request_date"))
    if rq:
        out.append(_mk(pid, "RECORDS_RESPONSE_DUE", add_days(rq, int(param(params, "records_request_response_days", 30))), as_of,
                       f"records request {rq} + 30 days working target (OAR 813-115-0050; response period not found in rule text, verify)", detail="records request date"))
    ud = parse_iso(row.get("usda_prepay_request_date"))
    if ud:
        out.append(_mk(pid, "USDA_PUBLIC_BODY_OFFER_WINDOW_END", add_days(ud, int(param(params, "usda_public_body_offer_days", 180))), as_of,
                       f"USDA_PREPAY_REQUEST_RECEIVED {ud} + 180 days (7 CFR 3560.659, verify)", detail="USDA_PREPAY_REQUEST_RECEIVED"))
    li = parse_iso(row.get("last_inspection_date"))
    if li:
        prog = str(row.get("program") or "")
        u = units if units is not None else _num(row.get("units_assisted"))
        if prog == "HOME" or "HOME" in programs:
            cad = param(params, "inspection_cadence_home", {"1-4": 36, "5-25": 24, "26+": 12}) or {}
            months = int(cad.get("26+", 12)) if (u or 0) >= 26 else (int(cad.get("5-25", 24)) if (u or 0) >= 5 else int(cad.get("1-4", 36)))
            cite = "24 CFR 92.504(d)"
        else:
            months = int(param(params, "inspection_cadence_lihtc", 36))
            cite = "26 CFR 1.42-5"
        out.append(_mk(pid, "INSPECTION_DUE", add_months(li, months), as_of, f"last_inspection_date {li} + {months} months ({cite}, verify)", detail="last_inspection_date"))
    return out


def withdrawal_anchor(evs: List[Dict[str, Any]], lead: Dict[str, Any]) -> Tuple[Optional[date], str]:
    """max of restriction-type ends; HAP/PRAC/PAC only with a non-renewal signal."""
    cands: List[Tuple[date, str]] = []
    nonrenewal = any(e["event_type"] == "PRESERVATION_NOTICE_RECEIVED" and str(e.get("detail") or "") in NON_RENEWAL_DETAILS for e in evs) \
        or str(lead.get("hap_renewal_request_status") or "") == "not_received"
    for e in evs:
        if e.get("status") in ("REJECTED", "SUPPRESSED", "STALE_CONTRACT_DATE") or e.get("direction") != "PRESSURE":
            continue
        d = parse_iso(e.get("event_date"))
        if not d:
            continue
        if e["event_type"] in WITHDRAWAL_ANCHOR_EVENTS:
            cands.append((d, "restriction_end"))
        elif e["event_type"] == "HAP_EXPIRATION" and (nonrenewal or str(e.get("detail") or "") == "mahra_20yr_term_ending"):
            cands.append((d, "hap_nonrenewal_signal"))
    if not cands:
        return None, "none"
    d, src = max(cands, key=lambda x: x[0])
    return d, src


def _state(as_of: date, anchor: date, notice_status: str, received_details: set, m_prep: int, m_first: int, m_second: int) -> str:
    prep, first, second = add_months(anchor, -m_prep), add_months(anchor, -m_first), add_months(anchor, -m_second)
    if as_of < prep:
        return "not_open"
    if as_of < first:
        return "open_first"
    first_ok = notice_status == "received" and ("push_first" in received_details or "push_second" in received_details)
    if as_of < second:
        return "open_second" if first_ok else "closed_first_due"
    if first_ok and "push_second" in received_details:
        return "closed_second_due_received"
    return "closed_second_due" if first_ok else "closed_first_due"


def derive(leads: pd.DataFrame, events: pd.DataFrame, as_of: date, params: Dict[str, Any], profile: Dict[str, Any],
           horizon_months: int = 120) -> Tuple[pd.DataFrame, pd.DataFrame]:
    push_allowed = bool(profile.get("receives_push_notice") or profile.get("is_qualified_purchaser"))
    m_prep = int(param(params, "push_window_prep_months", 36))
    m_first = int(param(params, "push_first_notice_months", 30))
    m_second = int(param(params, "push_second_notice_months", 24))
    tn = param(params, "tenant_notice_months", [36, 30]) or [36, 30]
    sb973 = parse_iso(param(params, "sb973_operative_restriction_date", None))
    hap_notice_m = int(param(params, "hap_optout_notice_months", 12))
    hap_pkg_d = int(param(params, "hap_optout_package_days", 120))

    ev_rows = events.to_dict(orient="records") if len(events) else []
    by_pid: Dict[str, List[Dict[str, Any]]] = {}
    for e in ev_rows:
        by_pid.setdefault(str(e.get("property_id")), []).append(e)
    # drop prior AGENCY_DEADLINE / window / breach rows that this pass regenerates (idempotent re-runs); keep servicing-derived ones
    regen = {"PRESERVATION_NOTICE_WINDOW", "NOTICE_COMPLIANCE_BREACH", "PUSH_WINDOW_PREP", "PUSH_FIRST_NOTICE_DUE", "PUSH_SECOND_NOTICE_DUE",
             "TENANT_NOTICE_WINDOW", "HAP_OPTOUT_NOTICE_DEADLINE", "HAP_OPTOUT_PACKAGE_DUE"}
    kept: List[Dict[str, Any]] = [e for e in ev_rows if not (e.get("event_type") in regen and str(e.get("source")).startswith(("agency_calendar", "OHCS", "HUD")))]
    new_events: List[Dict[str, Any]] = []
    leads = leads.copy().astype(object)
    for col in ("withdrawal_anchor_date", "push_anchor_source", "owner_cliff_type", "owner_cliff_date", "owner_cliff_band", "agency_action_type",
                "agency_action_date", "agency_action_months_out", "agency_action_basis", "agency_action_owner", "action_band", "notice_window_state",
                "owner_cliff_months_out", "next_expected_expiration"):
        if col not in leads.columns:
            leads[col] = pd.Series([""] * len(leads), index=leads.index, dtype=object)
    leads = leads.astype(object)
    stale_count = 0
    breaches = 0
    for i, lead in leads.iterrows():
        pid = str(lead["property_id"])
        evs = [e for e in kept if str(e.get("property_id")) == pid]
        units = _num(lead.get("units"))
        programs = [p for p in str(lead.get("programs") or "").split(";") if p]
        notice_status = str(lead.get("notice_status") or "unknown") or "unknown"
        received_details = {str(e.get("detail") or "") for e in evs if e.get("event_type") == "PRESERVATION_NOTICE_RECEIVED"}
        if received_details and notice_status != "received":
            notice_status = "received"
            leads.at[i, "notice_status"] = "received"
        signals = [s for s in str(lead.get("signals") or "").split(";") if s]
        flags = [f for f in str(lead.get("verify_flags") or "").split(";") if f]
        # ---- stale HAP dates
        for e in evs:
            if e.get("event_type") == "HAP_EXPIRATION" and e.get("status") in ("PAST", "FUTURE"):
                d = parse_iso(e.get("event_date"))
                if d and d < as_of and "terminated" not in str(e.get("detail") or ""):
                    e["status"] = "STALE_CONTRACT_DATE"
                    e["verify_flag"] = e.get("verify_flag") or FLAG_STALE_CONTRACT
                    stale_count += 1
                    if "hap_date_stale" not in signals:
                        signals.append("hap_date_stale")
                    msg = FLAG_MISSING_SOURCE + ": current HAP contract / TRACS (stale expiration date)"
                    if msg not in flags:
                        flags.append(msg)
                    nxt = d
                    while nxt < as_of:
                        nxt = add_months(nxt, 12)
                    leads.at[i, "next_expected_expiration"] = nxt.isoformat()
        # ---- withdrawal anchor + PuSH clocks
        anchor, src = withdrawal_anchor(evs, lead)
        leads.at[i, "withdrawal_anchor_date"] = anchor.isoformat() if anchor else ""
        leads.at[i, "push_anchor_source"] = src
        state = ""
        self_owned = str(lead.get("book_match")) == "self_owned"
        push_ok = anchor is not None and anchor >= as_of and (units or 0) >= 5 and bool(set(programs) & PUSH_COVERED_PROGRAMS) and push_allowed and not self_owned
        if push_ok:
            first_ws, first_we = add_months(anchor, -m_prep), add_months(anchor, -m_first)
            second_ws, second_we = add_months(anchor, -m_first), add_months(anchor, -m_second)
            deriv = (f"withdrawal_anchor_date ({src} {anchor}) - 36..30 months (internal prep window; no statutory 36-month start found) / "
                     f"30..24 months (owner notice no sooner than 30 and at least 24 months before withdrawal per OAR 813-115-0030 summary; ORS 456.260 text unread)")
            coverage_only = set(programs) & PUSH_COVERED_PROGRAMS
            coverage_unverified = (not bool(param(params, "push_program_coverage_verified", False))) and coverage_only <= {"HOME", "LIHTC_9", "LIHTC_4"}
            if coverage_unverified and FLAG_PUSH_COVERAGE not in flags:
                flags.append(FLAG_PUSH_COVERAGE)   # HOME-only / LIHTC-only: ORS 456.250 coverage depends on OAR 813-115-0010 (unread)
            w1 = _mk(pid, "PRESERVATION_NOTICE_WINDOW", first_ws, as_of, deriv, detail="push_first_window" + ("; window_open_now" if first_ws <= as_of < first_we else ""),
                     window_start=first_ws.isoformat(), window_end=first_we.isoformat(), event_id=f"{pid}:PRESERVATION_NOTICE_WINDOW:first")
            w2 = _mk(pid, "PRESERVATION_NOTICE_WINDOW", second_ws, as_of, deriv, detail="push_second_window" + ("; window_open_now" if second_ws <= as_of < second_we else ""),
                     window_start=second_ws.isoformat(), window_end=second_we.isoformat(), event_id=f"{pid}:PRESERVATION_NOTICE_WINDOW:second")
            for w in (w1, w2):
                w["value"] = src
                if coverage_unverified:
                    w["verify_flag"] = FLAG_PUSH_COVERAGE
                new_events.append(w)
            new_events.append(_mk(pid, "PUSH_WINDOW_PREP", first_ws, as_of, f"withdrawal_anchor_date {anchor} - {m_prep} months (internal prep)", detail=f"anchor {anchor} ({src})"))
            new_events.append(_mk(pid, "PUSH_FIRST_NOTICE_DUE", first_we, as_of, f"withdrawal_anchor_date {anchor} - {m_first} months (owner notice no sooner than this date per OAR 813-115-0030; ORS 456.262 designee trigger, verify)", detail=f"anchor {anchor} ({src})"))
            new_events.append(_mk(pid, "PUSH_SECOND_NOTICE_DUE", second_we, as_of, f"withdrawal_anchor_date {anchor} - {m_second} months (owner notice at least 24 months before withdrawal, OAR 813-115-0030, verify)", detail=f"anchor {anchor} ({src})"))
            if sb973 is None or anchor >= sb973:
                t_ws, t_we = add_months(anchor, -int(tn[0])), add_months(anchor, -int(tn[1]))
                new_events.append(_mk(pid, "TENANT_NOTICE_WINDOW", t_ws, as_of, f"withdrawal_anchor_date {anchor} - {tn[0]}..{tn[1]} months (SB 973 / ORS 456.259, verify)",
                                      detail=f"anchor {anchor} ({src})", window_start=t_ws.isoformat(), window_end=t_we.isoformat()))
                if str(lead.get("tenant_notice_status") or "") == "":
                    leads.at[i, "tenant_notice_status"] = "unknown"
            else:
                leads.at[i, "tenant_notice_status"] = "n/a_pre_operative"
            state = _state(as_of, anchor, notice_status, received_details, m_prep, m_first, m_second)
            if state == "open_first" and notice_status != "received":
                if "push_window_open_prep" not in signals:
                    signals.append("push_window_open_prep")
            if state in ("closed_first_due", "closed_second_due") and notice_status == "not_received_confirmed":
                due = add_months(anchor, -m_first)
                new_events.append(_mk(pid, "NOTICE_COMPLIANCE_BREACH", due, as_of,
                                      f"PUSH_FIRST_NOTICE_DUE {due} passed; notice_status=not_received_confirmed. Working label: the withdrawal clock has not started and "
                                      f"designee appointment is available (ORS 456.262, 'whichever is earlier'); not a statutory breach finding until ORS 456.260/.262 are read",
                                      detail="push_first_due_passed; notice_status=not_received_confirmed"))
                breaches += 1
        elif anchor is not None and anchor >= as_of and (units or 0) >= 5 and bool(set(programs) & PUSH_COVERED_PROGRAMS) and not push_allowed:
            state = "not_tracked_by_profile"
        leads.at[i, "notice_window_state"] = state
        # ---- HAP opt-out clocks (HAP / RAC / PBV only; FUTURE only)
        for e in evs:
            if e.get("event_type") == "HAP_EXPIRATION" and e.get("status") == "FUTURE" and str(e.get("program") or "") in HAP_LIKE_PROGRAMS:
                d = parse_iso(e.get("event_date"))
                if d:
                    new_events.append(_mk(pid, "HAP_OPTOUT_NOTICE_DEADLINE", add_months(d, -hap_notice_m), as_of, f"HAP_EXPIRATION {d} - 12 months (42 U.S.C. 1437f(c)(8); 24 CFR 402.8, verify)",
                                          detail=f"HAP_EXPIRATION {d}", program=e.get("program")))
                    new_events.append(_mk(pid, "HAP_OPTOUT_PACKAGE_DUE", add_days(d, -hap_pkg_d), as_of, f"HAP_EXPIRATION {d} - 120 days (Section 8 Renewal Policy Guide ch. 11, verify)",
                                          detail=f"HAP_EXPIRATION {d}", program=e.get("program")))
        # ---- servicing-column deadlines (idempotent against the adapter's own emissions)
        existing = {(e.get("event_type"), e.get("event_date")) for e in evs}
        for d_ev in deadlines_from_servicing_row(pid, lead, as_of, params, units, programs):
            if (d_ev["event_type"], d_ev["event_date"]) not in existing:
                new_events.append(d_ev)
        # RECORDS_REQUEST_DUE from any PRESERVATION_NOTICE_RECEIVED event (forecast / adapter sourced)
        for e in evs:
            if e.get("event_type") == "PRESERVATION_NOTICE_RECEIVED":
                nd = parse_iso(e.get("event_date"))
                if nd:
                    due = add_days(nd, int(param(params, "records_request_after_notice_days", 10)))
                    if ("RECORDS_REQUEST_DUE", due.isoformat()) not in existing and not any(x["event_type"] == "RECORDS_REQUEST_DUE" and x["property_id"] == pid for x in new_events):
                        new_events.append(_mk(pid, "RECORDS_REQUEST_DUE", due, as_of, f"PRESERVATION_NOTICE_RECEIVED {nd} + 10 days", detail="PRESERVATION_NOTICE_RECEIVED"))
        leads.at[i, "signals"] = ";".join(dict.fromkeys(signals))
        leads.at[i, "verify_flags"] = ";".join(dict.fromkeys(flags))

    all_events = kept + new_events
    out_ev = pd.DataFrame(all_events, columns=EVENT_COLUMNS).astype(object) if all_events else pd.DataFrame(columns=EVENT_COLUMNS)
    # ---- owner cliff, agency action, action band per lead
    by_pid = {}
    for e in all_events:
        by_pid.setdefault(str(e.get("property_id")), []).append(e)
    for i, lead in leads.iterrows():
        pid = str(lead["property_id"])
        evs = by_pid.get(pid, [])
        cliff = owner_cliff(evs, as_of)
        if cliff:
            mo = months_between(as_of, cliff["date"])
            leads.at[i, "owner_cliff_type"] = cliff["event_type"]
            leads.at[i, "owner_cliff_date"] = cliff["date"].isoformat()
            leads.at[i, "owner_cliff_months_out"] = mo
            leads.at[i, "owner_cliff_band"] = urgency_band(mo)
        else:
            leads.at[i, "owner_cliff_type"] = ""
            leads.at[i, "owner_cliff_date"] = ""
            leads.at[i, "owner_cliff_months_out"] = ""
            leads.at[i, "owner_cliff_band"] = ""
        act = agency_action(evs, as_of)
        if act:
            mo = months_between(as_of, act["date"])
            leads.at[i, "agency_action_type"] = act["event_type"]
            leads.at[i, "agency_action_date"] = act["date"].isoformat()
            leads.at[i, "agency_action_months_out"] = mo
            leads.at[i, "agency_action_basis"] = act.get("basis", "DERIVED")
            leads.at[i, "agency_action_owner"] = AGENCY_DEADLINE_META.get(act["event_type"], {}).get("agency_owner", "")
        else:
            for c in ("agency_action_type", "agency_action_date", "agency_action_months_out", "agency_action_basis", "agency_action_owner"):
                leads.at[i, c] = ""
        mos = [m for m in (leads.at[i, "owner_cliff_months_out"], leads.at[i, "agency_action_months_out"]) if m not in ("", None)]
        leads.at[i, "action_band"] = urgency_band(min(mos)) if mos else ""
        leads.at[i, "urgency_band"] = leads.at[i, "action_band"]
        # refresh events_in_horizon (status changes such as STALE)
        inh = [e for e in evs if e.get("direction") == "PRESSURE" and e.get("event_type") not in HELPER_EVENTS and e.get("event_family") != "AGENCY_DEADLINE"
               and str(e.get("status") or "").upper() not in ("REJECTED", "SUPPRESSED", "RESOLVED", "COMPLETED", "SUPERSEDED", "CANCELLED")
               and e.get("months_out") not in ("", None) and float(e["months_out"]) <= horizon_months]
        inh.sort(key=lambda e: e["event_date"])
        leads.at[i, "events_in_horizon"] = json.dumps([{k: e.get(k, "") for k in EIH_KEYS} for e in inh])
    leads.attrs["stale_contract_dates"] = stale_count
    leads.attrs["notice_compliance_breaches"] = breaches
    return leads, out_ev


def owner_cliff(evs: List[Dict[str, Any]], as_of: date) -> Optional[Dict[str, Any]]:
    """Earliest unresolved owner-side obligation, including overdue events until explicitly resolved."""
    cands = []
    for e in evs:
        if e.get("direction") != "PRESSURE" or e.get("event_family") not in ("REGULATORY", "DEBT"):
            continue
        if e.get("event_type") in NOT_OWNER_CLIFF or str(e.get("status") or "").upper() in ("REJECTED", "SUPPRESSED", "STALE_CONTRACT_DATE", "RESOLVED", "COMPLETED", "SUPERSEDED", "CANCELLED") or str(e.get("basis")) == "PROXY":
            continue
        d = parse_iso(e.get("event_date"))
        if d:
            cands.append((d, e))
    if not cands:
        return None
    d, e = min(cands, key=lambda c: c[0])
    return {"event_type": e["event_type"], "date": d, "basis": e.get("basis"), "source": e.get("source")}


def agency_action(evs: List[Dict[str, Any]], as_of: date) -> Optional[Dict[str, Any]]:
    """Earliest unresolved AGENCY_DEADLINE. Age alone never closes an obligation."""
    cands = []
    for e in evs:
        if e.get("event_family") != "AGENCY_DEADLINE" or str(e.get("status") or "").upper() in ("REJECTED", "SUPPRESSED", "RESOLVED", "COMPLETED", "SUPERSEDED", "CANCELLED"):
            continue
        d = parse_iso(e.get("event_date"))
        if d:
            cands.append((d, e))
    if not cands:
        return None
    d, e = min(cands, key=lambda c: c[0])
    return {"event_type": e["event_type"], "date": d, "basis": e.get("basis"), "source": e.get("source")}
