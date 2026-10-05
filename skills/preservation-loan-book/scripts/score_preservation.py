#!/usr/bin/env python3
"""Score and route the merged universe with references/scoring/affordable_public_am.json (preservation urgency x units at risk x our book).

Reads leads.csv + events.csv (from build_universe.py), evaluates the seven-factor rubric and the shared adjustments (basis multipliers,
queue bands, caps, recap_status multiplier), applies the mandate hard filter on nofa_offer, routes by precedence under the agency profile,
and writes leads_scored.csv with intervention_score, board_impact, queue_band, primary_route, secondary_routes, intervention, intervention_owner,
statutory_cite (verify), next_action and a factors_json column. Also writes units_at_risk.json (the single source for Board_Totals),
notice_compliance_queue.csv, nofa_targets.csv, agency_calendar.csv, sponsor_exposure.csv and optout_qc_responses.csv.

The JSON files are the only rubric: a missing scoring directory is an error. A/B/C never appear; queue bands are ESCALATE / ACT / PLAN / WATCH / EXCLUDED.

Usage:
  python scripts/score_preservation.py --leads runs/x/leads.csv --events runs/x/events.csv --pack <dir> --agency-profile hfa [--mandate <json>|none]
      [--universe all|our_book|universe_not_held] [--scoring-dir references/scoring] [--horizon-years 10] [--owner-types-include a,b] [--owner-types-exclude a,b]
      [--noah-watch] --out runs/x/leads_scored.csv [--xlsx runs/x/book.xlsx] [--explain <property_id>] [--as-of YYYY-MM-DD] [--internal]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plb.agency_calendar import AGENCY_DEADLINE_META  # noqa: E402
from plb.dates import months_between, parse_as_of, parse_iso, urgency_band  # noqa: E402
from plb.entities import normalize_org  # noqa: E402
from plb.interventions import cite as icite  # noqa: E402
from plb.pii import apply_pii_scope  # noqa: E402
from plb.schema import ROUTES, agency_profile, load_mandate  # noqa: E402
from plb.scoring import explain, load_scoring, score_lead  # noqa: E402
from plb.units import units_at_risk_json  # noqa: E402
from plb.workbook import sponsor_exposure  # noqa: E402

QUEUE_ORDER = {"ESCALATE": 0, "ACT": 1, "PLAN": 2, "WATCH": 3, "EXCLUDED": 4}
ROUTE_ORDER = {r: i for i, r in enumerate(ROUTES + ["none", "excluded"])}


def _list(s) -> Optional[List[str]]:
    if s is None:
        return None
    if isinstance(s, list):
        return [str(x) for x in s if str(x).strip()] or None
    items = [p.strip() for p in str(s).split(",") if p.strip()]
    return items or None


def sponsor_cliff_counts(leads: pd.DataFrame) -> Dict[str, int]:
    """Properties per normalized owner organization with an owner cliff inside 36 months."""
    out: Dict[str, int] = {}
    if not len(leads):
        return out
    for _, r in leads.iterrows():
        org = normalize_org(r.get("owner_name"))
        if not org:
            continue
        band = str(r.get("owner_cliff_band") or "")
        if band in ("OVERDUE", "CRITICAL", "URGENT", "APPROACHING"):
            out[org] = out.get(org, 0) + 1
    return out


def score_frame(leads: pd.DataFrame, events: pd.DataFrame, as_of, scoring_dir=None, profile_name="hfa", pack=None, mandate_path=None, universe="all",
                horizon_years=10.0, owner_types_include=None, owner_types_exclude=None, noah_watch=False):
    tables, shared, src = load_scoring(scoring_dir)
    prof = agency_profile(profile_name, pack)
    # a notice log counts as loaded when any lead carries a populated (non-unknown) notice_status: servicing notice_log_status or the
    # PuSH forecast / CP log. Without one, "first due passed + unknown" is a secondary confirm-the-log route (critic finding 25).
    ns_col = leads["notice_status"].astype(str).str.strip().str.lower() if "notice_status" in leads.columns else pd.Series([], dtype=str)
    prof = dict(prof)
    prof["notice_log_loaded"] = bool((ns_col.isin(["received", "not_received_confirmed"])).any()) if len(ns_col) else False
    mandate = load_mandate(pack, mandate_path)
    ev_by_pid: Dict[str, List[Dict[str, Any]]] = {}
    if events is not None and len(events):
        for rec in events.to_dict(orient="records"):
            ev_by_pid.setdefault(str(rec.get("property_id")), []).append(rec)
    counts = sponsor_cliff_counts(leads)
    results, rows = [], []
    for lead in leads.to_dict(orient="records"):
        if universe != "all" and str(lead.get("universe")) != universe:
            continue
        cls = str(lead.get("asset_class") or "affordable_regulated")
        if cls == "noah_unregulated" and not noah_watch:
            continue
        if cls not in tables:
            cls = "affordable_regulated"
        lead["sponsor_cliff_count"] = counts.get(normalize_org(lead.get("owner_name")), 0)
        res = score_lead(lead, ev_by_pid.get(str(lead.get("property_id")), []), cls, tables, shared, as_of, profile=prof, mandate=mandate,
                         horizon_months=int(horizon_years * 12), owner_types_include=owner_types_include, owner_types_exclude=owner_types_exclude)
        results.append(res)
        out = dict(lead)
        for k in ("score_raw", "intervention_score", "board_impact", "queue_band", "primary_route", "secondary_routes", "exclusion_reason", "intervention",
                  "intervention_owner", "statutory_cite", "owner_notice_required", "tenant_notice_required", "verify_before_action", "next_action", "compliance_gates",
                  "kpi_flags", "signals", "mandate_fit", "mandate_eligible_products", "mandate_ineligible_reason"):
            out[k] = res[k]
        if res.get("urgency_band") and not out.get("urgency_band"):
            out["urgency_band"] = res["urgency_band"]
        if res.get("agency_action_date_override"):
            out["agency_action_type"] = "HAP_OPTOUT_PACKAGE_DUE"
            out["agency_action_date"] = res["agency_action_date_override"]
            d = parse_iso(res["agency_action_date_override"])
            if d:
                out["agency_action_months_out"] = months_between(as_of, d)
                out["agency_action_basis"] = "DERIVED"
                out["agency_action_owner"] = "pbca_liaison"
                # R29 / E2: action_band = min(agency act-by, owner cliff) must follow the overridden act-by (the passed
                # HAP_OPTOUT_NOTICE_DEADLINE is a Verify — CA Log signal, not an OVERDUE act-by)
                mos = [m for m in (lead.get("owner_cliff_months_out"), out["agency_action_months_out"]) if m not in ("", None)]
                mos = [float(m) for m in mos if str(m) != "nan"]
                if mos:
                    out["action_band"] = urgency_band(min(mos)) or out.get("action_band", "")
                    out["urgency_band"] = out["action_band"]
        flags = [x for x in str(out.get("verify_flags") or "").split(";") if x] + list(res.get("verify_flags_added") or [])
        out["verify_flags"] = ";".join(dict.fromkeys(flags))
        out["pii_scope"] = out.get("pii_scope") or "organization"
        out["factors_json"] = json.dumps({"factors": res["factors"], "route_reasons": res["route_reasons"], "route_hits": res["route_hits"], "caps": res["caps"],
                                          "suppression": res["suppression"], "context": res["context"], "agency_profile": profile_name}, default=str)
        rows.append(out)
    scored = pd.DataFrame(rows)
    if len(scored):
        scored["_q"] = scored["queue_band"].map(lambda t: QUEUE_ORDER.get(t, 9))
        scored["_r"] = scored["primary_route"].map(lambda t: ROUTE_ORDER.get(t, 9))
        scored["_u"] = scored["universe"].map(lambda u: 0 if u == "our_book" else 1)
        scored["_bi"] = pd.to_numeric(scored["board_impact"], errors="coerce").fillna(0)
        scored = scored.sort_values(["_q", "_u", "_r", "intervention_score", "_bi"], ascending=[True, True, True, False, False]).drop(columns=["_q", "_r", "_u", "_bi"]).reset_index(drop=True)
    return scored, results, src, prof


def notice_compliance_rows(scored: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    """Req-ID checklist rows (PUSH-01..04, HAP-01..02) for properties with a PuSH window or a HAP opt-out clock."""
    rows = []
    ev = events if events is not None else pd.DataFrame()
    by_pid: Dict[str, List[Dict[str, Any]]] = {}
    for rec in (ev.to_dict(orient="records") if len(ev) else []):
        by_pid.setdefault(str(rec["property_id"]), []).append(rec)
    for r in scored.to_dict(orient="records"):
        pid = str(r["property_id"])
        evs = by_pid.get(pid, [])
        wins = [e for e in evs if e["event_type"] == "PRESERVATION_NOTICE_WINDOW"]
        ns = str(r.get("notice_status") or "unknown")
        state = str(r.get("notice_window_state") or "")
        if wins:
            first = next((e for e in wins if "first" in str(e.get("detail"))), wins[0])
            second = next((e for e in wins if "second" in str(e.get("detail"))), None)
            due1 = next((e["event_date"] for e in evs if e["event_type"] == "PUSH_FIRST_NOTICE_DUE"), "")
            due2 = next((e["event_date"] for e in evs if e["event_type"] == "PUSH_SECOND_NOTICE_DUE"), "")
            st1 = "received" if ns == "received" else ("breach (not_received_confirmed)" if ns == "not_received_confirmed" and state.startswith("closed") else ("due passed; confirm log" if state.startswith("closed") else ("window open" if state == "open_first" else "not yet due")))
            rows.append({"req_id": "PUSH-01", "property_id": pid, "property_name": r.get("property_name"), "statute_cite": "ORS 456.260 / OAR 813-115-0030 (owner notice no sooner than 30 months before withdrawal; (1)/(2) split unread) (verify)",
                         "requirement": "Owner first notice of intent to withdraw to OHCS and each affected local government (>= 30 months)", "window_start": first.get("window_start"),
                         "window_end": first.get("window_end"), "due_date": due1, "status": st1, "evidence": f"notice_status={ns}; window_state={state}",
                         "finding": "NOTICE_COMPLIANCE_BREACH" if any(e["event_type"] == "NOTICE_COMPLIANCE_BREACH" for e in evs) else "", "remediation_ask": "notice-deficiency letter; designee appointment on silence (verify)" if st1.startswith("breach") else "", "owner_response": "", "date_resolved": ""})
            rows.append({"req_id": "PUSH-02", "property_id": pid, "property_name": r.get("property_name"), "statute_cite": "ORS 456.260 / OAR 813-115-0030 (owner notice at least 24 months before withdrawal) (verify)",
                         "requirement": "Owner second notice (>= 24 months)", "window_start": second.get("window_start") if second else "", "window_end": second.get("window_end") if second else "",
                         "due_date": due2, "status": "not yet due" if state in ("", "not_open", "open_first") else ("received" if "push_second" in str(r.get("notice_detail") or "") else "confirm log"),
                         "evidence": f"notice_status={ns}", "finding": "", "remediation_ask": "", "owner_response": "", "date_resolved": ""})
            tw = next((e for e in evs if e["event_type"] == "TENANT_NOTICE_WINDOW"), None)
            rows.append({"req_id": "PUSH-03", "property_id": pid, "property_name": r.get("property_name"), "statute_cite": "SB 973 (2025); ORS 456.259 (verify operative date)",
                         "requirement": "Tenant notice 30-36 months before restriction end, five languages; per-tenant extension when missing", "window_start": tw.get("window_start") if tw else "",
                         "window_end": tw.get("window_end") if tw else "", "due_date": tw.get("window_end") if tw else "", "status": str(r.get("tenant_notice_status") or ("n/a_pre_operative" if not tw else "unknown")),
                         "evidence": "", "finding": "", "remediation_ask": "tenant_notice_check" if tw else "", "owner_response": "", "date_resolved": ""})
            rows.append({"req_id": "PUSH-04", "property_id": pid, "property_name": r.get("property_name"), "statute_cite": "SB 973 (2025) applicant disclosure (verify)",
                         "requirement": "Applicant / new-tenant disclosure before screening fee or rental agreement", "window_start": tw.get("window_start") if tw else "", "window_end": "",
                         "due_date": "", "status": "unknown", "evidence": "", "finding": "", "remediation_ask": "", "owner_response": "", "date_resolved": ""})
        hap_dl = [e for e in evs if e["event_type"] == "HAP_OPTOUT_NOTICE_DEADLINE"]
        if hap_dl:
            dl = min(hap_dl, key=lambda e: e["event_date"])
            pkg = next((e["event_date"] for e in evs if e["event_type"] == "HAP_OPTOUT_PACKAGE_DUE"), "")
            rrs = str(r.get("hap_renewal_request_status") or "unknown")
            rows.append({"req_id": "HAP-01", "property_id": pid, "property_name": r.get("property_name"), "statute_cite": "42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify)",
                         "requirement": "One-year owner notice to tenants, HUD and the contract administrator before HAP expiration (or renewal request)", "window_start": "", "window_end": "",
                         "due_date": dl["event_date"], "status": f"renewal_request_status={rrs}" + ("; deadline passed unconfirmed" if parse_iso(dl["event_date"]) and parse_iso(dl["event_date"]) < parse_iso(r.get("as_of_date")) and rrs == "unknown" else ""),
                         "evidence": "Verify — CA Log" if rrs == "unknown" else "", "finding": "", "remediation_ask": "confirm renewal request / opt-out notice at CA", "owner_response": "", "date_resolved": ""})
            rows.append({"req_id": "HAP-02", "property_id": pid, "property_name": r.get("property_name"), "statute_cite": "Section 8 Renewal Policy Guide ch. 11 (verify)",
                         "requirement": "Opt-out request and certification to HUD / CA not less than 120 days before expiration", "window_start": "", "window_end": "", "due_date": pkg,
                         "status": f"renewal_request_status={rrs}", "evidence": "", "finding": "", "remediation_ask": "", "owner_response": "", "date_resolved": ""})
    return pd.DataFrame(rows, columns=["req_id", "property_id", "property_name", "statute_cite", "requirement", "window_start", "window_end", "due_date", "status", "evidence", "finding",
                                       "remediation_ask", "owner_response", "date_resolved"])


def agency_calendar_rows(scored: pd.DataFrame, events: pd.DataFrame, as_of) -> pd.DataFrame:
    names = scored.set_index("property_id")["property_name"].to_dict() if len(scored) else {}
    rows = []
    for e in (events.to_dict(orient="records") if events is not None and len(events) else []):
        if (e.get("event_family") != "AGENCY_DEADLINE" or str(e.get("property_id")) not in names
                or str(e.get("status") or "").upper() in ("REJECTED", "SUPPRESSED", "RESOLVED", "COMPLETED", "SUPERSEDED", "CANCELLED")):
            continue
        d = parse_iso(e.get("event_date"))
        mo = months_between(as_of, d) if d else None
        meta = AGENCY_DEADLINE_META.get(e["event_type"], {})
        rows.append({"property_id": e["property_id"], "property_name": names.get(str(e["property_id"]), ""), "agency_action_type": e["event_type"], "due_date": e.get("event_date"),
                     "months_out": mo, "urgency": urgency_band(mo), "basis": e.get("basis"), "derived_from": e.get("derivation"), "agency_owner": meta.get("agency_owner", ""),
                     "statutory_cite": (meta.get("statutory_cite", "") + " (verify)") if meta.get("statutory_cite") else "", "status": e.get("status")})
    df = pd.DataFrame(rows, columns=["property_id", "property_name", "agency_action_type", "due_date", "months_out", "urgency", "basis", "derived_from", "agency_owner", "statutory_cite", "status"])
    return df.sort_values(["due_date", "property_name"]).reset_index(drop=True) if len(df) else df


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--leads", required=True)
    ap.add_argument("--events", required=True)
    ap.add_argument("--pack", default=None)
    ap.add_argument("--agency-profile", default="hfa", choices=["hfa", "city_housing", "county", "pha_am", "cdbg_home"])
    ap.add_argument("--mandate", default=None, help="mandate.json path; 'none' disables (mandate_fit no_mandate_file)")
    ap.add_argument("--universe", default="all", choices=["all", "our_book", "universe_not_held"])
    ap.add_argument("--scoring-dir", default=None)
    ap.add_argument("--horizon-years", type=float, default=10)
    ap.add_argument("--owner-types-include", default=None)
    ap.add_argument("--owner-types-exclude", default=None)
    ap.add_argument("--noah-watch", action="store_true")
    ap.add_argument("--out", required=True)
    ap.add_argument("--xlsx", default=None)
    ap.add_argument("--explain", default=None)
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--internal", action="store_true")
    ap.add_argument("--prior", default=None, help="prior leads_scored.csv for KPI rows in units_at_risk.json")
    a = ap.parse_args(argv)
    as_of = parse_as_of(a.as_of)
    leads = pd.read_csv(a.leads, dtype=str, keep_default_na=False)
    events = pd.read_csv(a.events, dtype=str, keep_default_na=False)
    scored, results, src, prof = score_frame(leads, events, as_of, a.scoring_dir, a.agency_profile, a.pack, a.mandate, a.universe, a.horizon_years,
                                             _list(a.owner_types_include), _list(a.owner_types_exclude), a.noah_watch)
    out_dir = os.path.dirname(os.path.abspath(a.out))
    os.makedirs(out_dir, exist_ok=True)
    scope = "internal" if a.internal else "organization"
    scored_out, _ = apply_pii_scope(scored, scope)
    scored_out.to_csv(a.out, index=False)
    kpi = None
    if a.prior and os.path.exists(a.prior):
        from diff_forecast import kpi_summary, status_flips
        flips = status_flips(scored, pd.read_csv(a.prior, dtype=str, keep_default_na=False), events, None)
        kpi = kpi_summary(flips, scored)
    uar = units_at_risk_json(scored, as_of, a.agency_profile, prof.get("board_totals_variant", "loan_book"), kpi)
    json.dump(uar, open(os.path.join(out_dir, "units_at_risk.json"), "w"), indent=2)
    nc = notice_compliance_rows(scored, events)
    nc.to_csv(os.path.join(out_dir, "notice_compliance_queue.csv"), index=False)
    nofa = scored[(scored["primary_route"] == "nofa_offer") | scored["secondary_routes"].astype(str).str.contains("nofa_offer", na=False)] if len(scored) else scored
    nofa_cols = [c for c in ["property_id", "property_name", "jurisdiction", "units", "units_at_risk", "hap_units_at_risk", "psh_units_at_risk", "owner_name", "owner_type", "programs",
                             "owner_cliff_type", "owner_cliff_date", "owner_cliff_band", "mandate_fit", "mandate_eligible_products", "recap_gap_estimate", "intervention_score", "queue_band", "primary_route"] if c in scored.columns]
    nofa[nofa_cols].to_csv(os.path.join(out_dir, "nofa_targets.csv"), index=False)
    agency_calendar_rows(scored, events, as_of).to_csv(os.path.join(out_dir, "agency_calendar.csv"), index=False)
    sponsor_exposure(scored).to_csv(os.path.join(out_dir, "sponsor_exposure.csv"), index=False)
    oq = scored[scored["primary_route"].isin(["optout_response", "qc_admin"]) | scored["secondary_routes"].astype(str).str.contains("optout_response|qc_admin", na=False)] if len(scored) else scored
    oq[[c for c in ["property_id", "property_name", "primary_route", "secondary_routes", "programs", "hap_units_at_risk", "hap_renewal_request_status", "hap_renewal_option",
                    "next_expected_expiration", "qc_status", "qc_waived", "agency_action_type", "agency_action_date", "intervention", "intervention_owner", "statutory_cite", "verify_flags"] if c in scored.columns]].to_csv(
        os.path.join(out_dir, "optout_qc_responses.csv"), index=False)
    print(f"[score] scoring tables: {src}; as_of {as_of}; agency_profile {a.agency_profile}; universe {a.universe}; leads {len(scored)}; pii_scope {scope}")
    if len(scored):
        print("[score] queue:", scored["queue_band"].value_counts().to_dict(), "primary routes:", scored["primary_route"].value_counts().to_dict())
        for band, grp in scored.groupby("queue_band"):
            ua = pd.to_numeric(grp["units_at_risk"], errors="coerce").fillna(0).sum()
            hap = pd.to_numeric(grp["hap_units_at_risk"], errors="coerce").fillna(0).sum()
            prac = pd.to_numeric(grp["prac_units_at_risk"], errors="coerce").fillna(0).sum()
            psh = pd.to_numeric(grp["psh_units_at_risk"], errors="coerce").fillna(0).sum()
            upb = pd.to_numeric(grp["public_upb_at_risk"], errors="coerce").fillna(0).sum()
            print(f"[score]   {band:<9} properties {len(grp):>4}  units_at_risk {int(ua):>6}  HAP {int(hap):>5}  PRAC {int(prac):>5}  PSH {int(psh):>5}  $UPB at risk {upb:,.0f}")
        h = uar["headline"]
        print(f"[score] Board headline (owner cliff <= 36 mo): {h['properties']} properties / {h['units_at_risk']} restricted units / {h['hap_units_at_risk']} HAP / {h['prac_units_at_risk']} PRAC / "
              f"{h['psh_units_at_risk']} PSH / ${h['public_upb_at_risk']:,.0f} public UPB; book verdict {uar['book_verdict']}")
    if a.explain:
        idx = {str(l.get("property_id")): i for i, l in enumerate(leads.to_dict(orient="records"))}
        res_idx = {str(l.get("property_id")): i for i, l in enumerate([r for r in leads.to_dict(orient="records") if a.universe == "all" or r.get("universe") == a.universe])}
        if a.explain in res_idx and res_idx[a.explain] < len(results):
            print(explain(results[res_idx[a.explain]], leads.to_dict(orient="records")[idx[a.explain]]))
        else:
            print(f"[score] property_id {a.explain} not found")
    if a.xlsx:
        from plb.workbook import build_workbook
        cal_path = os.path.join(os.path.dirname(os.path.abspath(a.events)), "calendar_summary.json")
        calendar = json.load(open(cal_path)) if os.path.exists(cal_path) else {}
        rej_path = os.path.join(os.path.dirname(os.path.abspath(a.events)), "rejects.csv")
        rejects = pd.read_csv(rej_path, dtype=str, keep_default_na=False) if os.path.exists(rej_path) else None
        build_workbook(a.xlsx, scored, events, calendar, rejects, run_meta={"as_of_date": as_of.isoformat(), "scoring_source": src, "agency_profile": a.agency_profile,
                                                                           "agency_name": prof.get("agency_name"), "geography_mode": calendar.get("geography_mode", ""),
                                                                           "counties": calendar.get("counties", []), "horizon_years": calendar.get("horizon_years", a.horizon_years),
                                                                           "degraded_note": calendar.get("degraded_note", ""), "universe": a.universe, "pii_scope": scope},
                       units_at_risk=uar, agency_calendar=agency_calendar_rows(scored, events, as_of), notice_compliance=nc, pii_scope=scope)
        print(f"[score] wrote {a.xlsx}")
    print(f"[score] wrote {a.out}, units_at_risk.json, notice_compliance_queue.csv, nofa_targets.csv, agency_calendar.csv, sponsor_exposure.csv, optout_qc_responses.csv")


if __name__ == "__main__":
    main()
