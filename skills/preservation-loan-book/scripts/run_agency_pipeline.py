#!/usr/bin/env python3
"""Orchestrate the preservation-loan-book pipeline from a run_config.json (public-agency preservation and loan-book review).

Stages (full isolated runs; partial restarts are rejected to prevent stale output reuse):
  discover  -> scan `servicing_extract`, `inbox` and `local_datasets[]`; detect each file's schema from its header
               (agency_servicing_extract FIRST, then OHCS inventory, HUD FHASL, HUD Sec 8, OHCS forecast, REAC, NOAH candidates,
               ZIP crosswalk); date each file from its filename (YYYYMMDD / YYYY-MM-DD) else mtime (vintage_source recorded)
  universe  -> build_universe.py: servicing -> adapters -> merge with book join -> units -> agency calendar (two universes, one merge)
  calendar  -> query_calendar.py console view; confirms the header (five basis counts | helper deadlines | agency act-by) matches
  score     -> score_preservation.py (affordable_public_am rubric, mandate hard filter, routes by precedence under the agency profile)
  workbook  -> build_board_workbook.py (17-tab working file; --board-packet writes the stripped public_packet workbook + board_packet.md)
  handoffs  -> make_handoffs.py (sibling JSON, documents_to_request.csv to our own file room, sos_worklist.csv, board_packet.csv)
  brief     -> brief.md (fixed sections of references/output-contract.md Section 4; the calendar header is quoted verbatim before any count)
  diff      -> diff_forecast.py status_flips.csv + kpi_summary.json against the prior run (the agency KPI)

Also writes result.json (output-contract.md Section 1), manifest.json (config snapshot, every input's sha256 / vintage, flags incl.
agency_profile, universe, mandate_file, pii_scope, book_coverage, noah_watch, horizon_years, records_classification, plb_version) and,
when `pipeline_mode` is true, the checkpoint data/status/{market_id}/asset_management/preservation-loan-book.json.
No network calls; the clock is read only through --as-of / as_of_date (default date.today()).

Usage:
  python scripts/run_agency_pipeline.py --config run_config.json [--prior-run <completed-run-dir>] [--explain <property_id>] [--as-of YYYY-MM-DD]
Config keys: market_id, pack, agency_profile, universe, mandate_file, geography_mode, counties[], target_city, horizon_years (10),
regulatory_horizon_years (10), programs, owner_types_include, owner_types_exclude, servicing_extract, book_coverage ("partial"),
local_datasets[], inbox, zip_crosswalk, prior_run, prior_forecast, noah_watch (false), pii_scope ("organization"), board_packet (true),
include_proxies (false), handoff_routes[], max_results, workbook_name, out_dir, as_of_date, scoring_dir, pipeline_mode (false),
operations_db (optional), financial_observations (optional CSV), financial_policy (versioned agency thresholds).
Outputs live under out_dir/as_of/run_id; read out_dir/as_of/latest.json for the last successful run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Optional

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from plb import __version__ as PLB_VERSION  # noqa: E402
from plb.instruments import parse_instruments, grant_exposure  # noqa: E402
from plb.dates import months_between, parse_as_of, parse_iso  # noqa: E402
from plb.interventions import meta as imeta  # noqa: E402
from plb.pii import RECORDS_CLASSIFICATION, apply_pii_scope  # noqa: E402
from plb.schema import ROUTES, agency_profile, detect_schema, load_dataset_schemas, load_mandate, load_market_params, param  # noqa: E402
from smoke_test_sources import parse_tables  # noqa: E402

STAGES = ["discover", "universe", "calendar", "score", "workbook", "handoffs", "brief", "diff"]
PY = sys.executable
FILENAME_DATE_RE = re.compile(r"(20\d{2})[-_]?(\d{2})[-_]?(\d{2})")
# schema id -> (adapter script run by build_universe.py, sources.md source_id used to look up URL / access / verified_live)
ADAPTERS = {
    "agency_servicing_extract": ("ingest_servicing_extract.py", "agency_servicing_extract"),
    "ohcs_affordable_housing_inventory": ("ohcs_inventory_targets.py", "ohcs_oahi"),
    "hud_fhasl_active": ("normalize_hud_insured.py", "hud_fhasl_active"),
    "hud_mf_assistance_sec8": ("normalize_hud_sec8.py", "hud_mf_assist_sec8"),
    "ohcs_push_forecast": ("normalize_ohcs_forecast.py", "ohcs_push_forecast"),
    "hud_reac_scores": ("normalize_reac_scores.py", "hud_reac"),
    "noah_candidates": ("noah_watch.py", "noah_candidates"),
}
AFFORDABLE_SOURCE_IDS = ["agency_servicing_extract", "ohcs_oahi", "ohcs_push_forecast", "ohcs_hca_optout", "hud_fhasl_active", "hud_mf_assist_sec8", "hud_lihtc_db",
                         "hud_reac", "usda_mfh_exit", "nhpd", "multco_records", "oregon_sos_registry"]
ROUTE_LABEL = {"optout_response": "Opt-out responses", "notice_compliance": "Notice compliance", "qc_admin": "Qualified-contract administration",
               "designee_rofr": "Designee / ROFR", "recap_committee": "Recap committee", "servicing_watch": "Servicing watch",
               "nofa_offer": "NOFA / product offers", "ta_sponsor": "Sponsor TA"}
QUEUE_BANDS_IN_CARDS = ("OVERDUE", "CRITICAL", "URGENT", "APPROACHING")


# --------------------------------------------------------------------------- helpers
def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def file_vintage(path: str):
    """(vintage ISO, vintage_source): the date in the filename when present (Oregon_..._20261002.csv -> 2026-10-02), else mtime."""
    m = FILENAME_DATE_RE.search(os.path.basename(path))
    if m:
        y, mo, d = m.groups()
        try:
            return date(int(y), int(mo), int(d)).isoformat(), "filename"
        except ValueError:
            pass
    return date.fromtimestamp(os.path.getmtime(path)).isoformat(), "mtime"


def run_cmd(args: List[str], log: List[str]) -> int:
    log.append("$ " + " ".join(args))
    p = subprocess.run(args, capture_output=True, text=True)
    log.append(p.stdout.strip())
    if p.returncode != 0:
        log.append("STDERR: " + p.stderr.strip())
    print(p.stdout.strip())
    err = "\n".join(l for l in p.stderr.splitlines() if "Warning" not in l and "frame.insert" not in l and l.strip() and not l.startswith("  "))
    if err.strip():
        print(err, file=sys.stderr)
    if p.returncode != 0:
        raise RuntimeError(f"stage {os.path.basename(args[1])} failed rc={p.returncode}: {p.stderr[-2000:]}")
    return p.returncode


def header_columns(path: str) -> List[str]:
    try:
        if path.lower().endswith((".xlsx", ".xls", ".xlsm")):
            return [str(c).strip() for c in pd.read_excel(path, nrows=0).columns]
        return [str(c).strip() for c in pd.read_csv(path, nrows=0, dtype=str, encoding="utf-8-sig").columns]
    except Exception:
        return []


def load_source_directory(pack: str) -> Dict[str, Dict[str, str]]:
    """source_id -> {url, access, verified_live_declared, live_status (from sources_status.json when a live smoke test ran)}."""
    out: Dict[str, Dict[str, str]] = {}
    sp = os.path.join(pack, "sources.md")
    if os.path.exists(sp):
        with open(sp, "r", encoding="utf-8") as fh:
            for row in parse_tables(fh.read()):
                sid = row.get("source_id")
                if sid:
                    out[sid] = {"url": row.get("url", ""), "access": row.get("access", ""), "verified_live_declared": row.get("verified_live", ""),
                                "adapter": row.get("adapter", ""), "profile": row.get("profile", "")}
    st = os.path.join(pack, "sources_status.json")
    if os.path.exists(st):
        try:
            status = json.load(open(st))
            if status.get("mode") == "live":
                for r in status.get("results", []):
                    sid = r.get("source_id")
                    if sid in out:
                        out[sid]["live_status"] = "true" if r.get("verified_live") else f"false ({r.get('error') or r.get('status')})"
        except Exception:
            pass
    return out


def url_verified(entry: Dict[str, str]) -> str:
    live = entry.get("live_status")
    if live:
        return live
    decl = str(entry.get("verified_live_declared", "")).strip()
    low = decl.lower()
    if low.startswith("true") and "mirror" not in low and "file" not in low:
        return "true"
    if "file" in low:
        return "false (file verified on disk; live page not fetched in this build)"
    return f"false ({decl or 'not fetched in this build'})"


def discover(cfg: Dict[str, Any], schemas: Dict[str, Any]) -> List[Dict[str, Any]]:
    files: List[str] = []
    for path in ([cfg["servicing_extract"]] if cfg.get("servicing_extract") else []) + list(cfg.get("local_datasets") or []):
        if not os.path.isfile(path):
            raise ValueError(f"configured input is missing: {path}")
    if cfg.get("servicing_extract") and os.path.exists(cfg["servicing_extract"]):
        files.append(cfg["servicing_extract"])
    inbox = cfg.get("inbox")
    if inbox and os.path.isdir(inbox):
        for fn in sorted(os.listdir(inbox)):
            if fn.lower().endswith((".csv", ".xlsx", ".xls")):
                files.append(os.path.join(inbox, fn))
    for p in cfg.get("local_datasets", []) or []:
        if os.path.exists(p):
            files.append(p)
    out = []
    for f in dict.fromkeys(files):
        cols = header_columns(f)
        sid = detect_schema(cols, schemas) if cols else None
        if sid is None and any(c.lower() in ("zip", "county", "res_ratio") for c in cols) and len(cols) <= 8:
            sid = "zip_county_crosswalk"
        if sid is None and "Termination Date" in cols:
            sid = "hud_fhasl_terminated"
        if f == cfg.get("servicing_extract") and sid != "agency_servicing_extract":
            raise ValueError("configured servicing extract does not match the agency schema")
        v, vs = file_vintage(f)
        out.append({"file": f, "schema": sid, "sha256": sha256(f), "columns": cols[:12], "vintage": v, "vintage_source": vs})
    # servicing extract first so every later adapter can match property ids against the book
    order = {"agency_servicing_extract": 0, "ohcs_affordable_housing_inventory": 1}
    return sorted(out, key=lambda f: order.get(f["schema"], 2))


def _read(path: str) -> Optional[pd.DataFrame]:
    """CSV -> DataFrame of strings; None when missing; empty frame for a 0-byte / header-less file (degraded book-absent runs)."""
    if not path or not os.path.exists(path):
        return None
    if os.path.getsize(path) == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path, dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def _params_as_of(params) -> str:
    """Latest `as_of` stamped on any parameter in market-params.json (the file carries per-key vintages, not a top-level one)."""
    if not isinstance(params, dict):
        return "n/a"
    top = params.get("as_of")
    if isinstance(top, str) and top:
        return top
    vintages = sorted({str(v.get("as_of")) for v in params.values() if isinstance(v, dict) and v.get("as_of")})
    return vintages[-1] if vintages else "n/a"


def _equity_overlay_state(path: str) -> str:
    if not os.path.exists(path):
        return "absent"
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(open(path, encoding="utf-8")) or {}
    except Exception:
        return "present (unreadable; treated as placeholder)"
    def _has_items(v) -> bool:
        if isinstance(v, list):
            return len(v) > 0
        if isinstance(v, dict):
            return any(_has_items(x) for x in v.values())
        return False
    populated = any(_has_items(v) for k, v in data.items() if k not in ("source", "notes", "as_of", "verified_live"))
    return "present (populated)" if populated else "placeholder (no tract / district list)"


def _num(v) -> Optional[float]:
    try:
        s = str(v).replace(",", "").replace("$", "").strip()
        return float(s) if s and s.lower() not in ("nan", "none") else None
    except ValueError:
        return None


def _money(v) -> str:
    x = _num(v)
    return f"${x:,.0f}" if x is not None else "n/a"


def _int(v) -> str:
    x = _num(v)
    return str(int(x)) if x is not None else "0"


# --------------------------------------------------------------------------- brief
def _card(n: int, r: Dict[str, Any], docs_by_pid: Dict[str, List[str]], handoff_by_pid: Dict[str, List[str]]) -> List[str]:
    units_line = (f"- Units {r.get('units') or 'n/a'} · restricted {_int(r.get('restricted_units'))} (units_basis {r.get('units_basis') or 'n/a'}) · HAP {_int(r.get('hap_units_at_risk'))}"
                  f" · PRAC {_int(r.get('prac_units_at_risk'))} · other RA {_int(r.get('other_ra_units'))} · PSH {_int(r.get('psh_units_at_risk'))} · flags [{r.get('vulnerability_flags') or '-'}]")
    act = (f"{r.get('agency_action_type')} {r.get('agency_action_date')} [{r.get('agency_action_basis') or 'DERIVED'}] — {r.get('agency_action_months_out')} months · owner {r.get('agency_action_owner') or 'n/a'}"
           if r.get("agency_action_type") else "none inside 12 months past / horizon")
    cliff = (f"{r.get('owner_cliff_type')} {r.get('owner_cliff_date')} [{r.get('first_reg_basis') or r.get('first_debt_basis') or ''}] — band {r.get('owner_cliff_band')}"
             if r.get("owner_cliff_type") else "no dated owner cliff inside horizon")
    if r.get("next_expected_expiration"):
        cliff += f" · next_expected_expiration {r.get('next_expected_expiration')} (annual HAP, stale date)"
    bm = str(r.get("book_match") or "")
    if bm in ("matched", "self_owned", "book_only"):
        pos = (f"{r.get('book_kind') or 'book'} {r.get('agency_loan_ids') or r.get('grant_ids') or ''} · {_money(r.get('public_upb'))} {r.get('payment_type') or ''} · matures {r.get('our_maturity') or 'n/a'}"
               f" [{r.get('our_maturity_basis') or ''}] · affordability_end {r.get('affordability_end') or 'n/a'} · recapture {r.get('recapture_type') or 'none'}"
               f"{(' exposure ' + _money(r.get('recapture_exposure'))) if _num(r.get('recapture_exposure')) else ''} · covenant_status {r.get('covenant_status') or 'n/a'} · am_officer {r.get('am_officer') or 'n/a'}"
               + (" · self-owned asset" if bm == "self_owned" else ""))
    elif bm == "unmatched_expected":
        pos = "expected in book — join missing (Verify — Book Join; capital factor 0, no guessed balance)"
    elif bm == "book_absent":
        pos = "book absent (no servicing extract in this run)"
    else:
        pos = "not in book"
    im = imeta(r.get("intervention") or "") if r.get("intervention") else {}
    on = "yes" if str(r.get("owner_notice_required")).lower() == "true" else ("no" if r.get("intervention") else "n/a")
    tn = "yes" if str(r.get("tenant_notice_required")).lower() == "true" else ("no" if r.get("intervention") else "n/a")
    interv = (f"{r.get('intervention')} — {r.get('intervention_owner') or 'n/a'} — {r.get('statutory_cite') or 'no statutory cite'} — owner notice: {on} · tenant notice: {tn}"
              f" — notice address: {r.get('notice_address') or 'not on file'} [{r.get('notice_address_source') or 'unknown'}]"
              + (f" — first action: {im.get('first_action')}" if im.get("first_action") else "")) if r.get("intervention") else "none (monitoring)"
    ev = []
    try:
        for e in json.loads(r.get("events_in_horizon") or "[]")[:6]:
            ev.append(f"{e.get('event_type')} {e.get('event_date')} [{e.get('basis')}] {e.get('source') or ''}".strip())
    except Exception:
        pass
    physical = [s for s in str(r.get("signals") or "").split(";") if s.startswith(("reac_", "noncompliance", "code_case", "tax_delinq", "dangerous", "occupancy", "tax_exemption"))]
    return [
        f"### [#{n}] {r.get('property_name')} — {r.get('jurisdiction') or r.get('county_name') or ''}  Route [{r.get('primary_route')}] Preservation [{r.get('preservation_urgency')}] Financial [{r.get('financial_risk')}] "
        f"Units at risk [{_int(r.get('units_at_risk'))}] Public UPB {_money(r.get('public_upb_at_risk')) if _num(r.get('public_upb_at_risk')) else ('$0' if bm in ('matched', 'self_owned') else 'n/a')}",
        units_line,
        f"- Data confidence: {r.get('data_confidence')}: {r.get('data_confidence_reasons')}",
        f"- Readiness: {r.get('intervention_readiness')}: {r.get('readiness_reasons')}",
        f"- Financial reasons: {r.get('financial_reasons')}",
        f"- First agency act-by: {act}",
        f"- Owner cliff: {cliff}",
        f"- Declared intent / notice status: notice_status {r.get('notice_status') or 'unknown'} · tenant_notice_status {r.get('tenant_notice_status') or 'n/a'} · hap_renewal_request_status {r.get('hap_renewal_request_status') or 'n/a'} · recap_status {r.get('recap_status') or 'none'}"
        + (f" · secondary routes {r.get('secondary_routes')}" if r.get("secondary_routes") else ""),
        f"- Our position: {pos}",
        f"- Physical: {'; '.join(physical) if physical else 'no physical / REAC signal in this run'}",
        f"- Sponsor capacity: {r.get('owner_type') or 'unknown'} · {r.get('owner_name') or 'owner not on file'} · sponsor_cliff_count {r.get('sponsor_cliff_count') or 0}" + (" · registered agent " + str(r.get("registered_agent")) if r.get("registered_agent") else ""),
        f"- Intervention: {interv}",
        f"- Evidence: {'; '.join(ev) if ev else 'see Events tab'}",
        f"- Verify before acting: {r.get('verify_before_action') or '-'}" + (f" · flags {r.get('verify_flags')}" if r.get("verify_flags") else ""),
        f"- Handoffs ready: {', '.join(handoff_by_pid.get(str(r.get('property_id')), [])) or '-'}" + (f" · documents to request: {len(docs_by_pid.get(str(r.get('property_id')), []))}" if docs_by_pid.get(str(r.get("property_id"))) else ""),
        "",
    ]


def write_brief(run_dir: str, cfg: Dict[str, Any], as_of: date, sources_used: List[Dict[str, Any]], unverified: List[str], prof: Dict[str, Any], pack: str) -> str:
    leads = _read(os.path.join(run_dir, "leads_scored.csv"))
    if leads is None:
        leads = pd.DataFrame()
    cal = json.load(open(os.path.join(run_dir, "calendar_summary.json"))) if os.path.exists(os.path.join(run_dir, "calendar_summary.json")) else {}
    uar = json.load(open(os.path.join(run_dir, "units_at_risk.json"))) if os.path.exists(os.path.join(run_dir, "units_at_risk.json")) else {}
    ac = _read(os.path.join(run_dir, "agency_calendar.csv"))
    nc = _read(os.path.join(run_dir, "notice_compliance_queue.csv"))
    flips = _read(os.path.join(run_dir, "status_flips.csv"))
    gaps = _read(os.path.join(run_dir, "book_join_gaps.csv"))
    unmatched = _read(os.path.join(run_dir, "servicing_unmatched.csv"))
    pns = _read(os.path.join(run_dir, "pipeline_not_scored.csv"))
    docs = _read(os.path.join(run_dir, "handoff", "documents_to_request.csv"))
    sos = _read(os.path.join(run_dir, "handoff", "sos_worklist.csv"))
    sponsors = _read(os.path.join(run_dir, "sponsor_exposure.csv"))
    params = load_market_params(pack)
    mandate = load_mandate(pack, cfg.get("mandate_file"))
    profile_name = cfg.get("agency_profile", "hfa")
    scope = cfg.get("pii_scope", "organization")
    leads, _ = apply_pii_scope(leads, scope) if len(leads) else (leads, [])
    rows = leads.to_dict(orient="records") if len(leads) else []
    docs_by_pid: Dict[str, List[str]] = {}
    for d in (docs.to_dict(orient="records") if docs is not None and len(docs) else []):
        docs_by_pid.setdefault(str(d.get("property_id")), []).append(str(d.get("document")))
    handoff_by_pid: Dict[str, List[str]] = {}
    hdir = os.path.join(run_dir, "handoff")
    if os.path.isdir(hdir):
        for fn in sorted(os.listdir(hdir)):
            if fn.endswith(".json"):
                try:
                    for item in json.load(open(os.path.join(hdir, fn))).get("items", []):
                        handoff_by_pid.setdefault(str(item.get("property_id")), []).append(fn[:-5])
                except Exception:
                    pass

    L: List[str] = [f"# Preservation and Loan-Book Review: {profile_name} — {cfg.get('market_id', '')} — as of {as_of.isoformat()}", ""]
    # ---- Run Summary
    L += ["## Run Summary"]
    L.append(f"- Agency: {prof.get('agency_name', '')} ({profile_name}) · geography_mode {cfg.get('geography_mode')} ({', '.join(cfg.get('counties') or cal.get('counties') or [])}) · horizon {cfg.get('horizon_years', 10)} years"
             f" · universe {cfg.get('universe', 'all')}")
    files = "; ".join(f"{s['source_id']} {s['vintage']} ({s['vintage_source']})" for s in sources_used) or "none"
    have = {s["source_id"] for s in sources_used}
    absent = [sid for sid in ("agency_servicing_extract", "ohcs_oahi", "hud_mf_assist_sec8", "ohcs_push_forecast", "hud_reac") if sid not in have]
    L.append(f"- Files and vintages: {files}" + (f"; absent: {', '.join(absent)}" if absent else ""))
    L.append(f"- Basis breakdown: {cal.get('header', '')}")
    jg = cal.get("book_join_grades") or {}
    bm = cal.get("book_match_counts") or {}
    book_rows = [r for r in rows if r.get("universe") == "our_book"]
    monitored = sum(1 for r in book_rows if r.get("primary_route") == "none")
    L.append(f"- Book: coverage {cfg.get('book_coverage', 'partial')}; joins crosswalk {jg.get('crosswalk', 0)} / address {jg.get('address', 0)} / fuzzy {jg.get('fuzzy', 0)} / unmatched {jg.get('unmatched', 0)};"
             f" book rows monitored {monitored} vs on watch {len(book_rows) - monitored}; book_match unmatched_expected {bm.get('unmatched_expected', 0)}")
    degraded = cal.get("degraded_note") or ""
    L.append(f"- Degraded run: {'yes — ' + degraded.strip() if degraded.strip() else 'no'}")
    L.append(f"- pii_scope {scope}; records_classification: {RECORDS_CLASSIFICATION}")
    L.append("- Urgency bands are months (OVERDUE / CRITICAL 0-12 / URGENT 12-24 / APPROACHING 24-36 / MONITOR 36-60 / SCHEDULED 60-120 / BEYOND), not critical-dates-tracker's days")
    push_rows = [r for r in rows if r.get("notice_window_state") not in ("", None, "not_tracked_by_profile")] if rows and "notice_window_state" in leads.columns else []
    unknown = sum(1 for r in push_rows if str(r.get("notice_status") or "unknown") == "unknown")
    L.append(f"- Notice log: {unknown} of {len(push_rows)} PuSH-covered rows have no notice_log_status (unknown) — reported, not scored")
    ot_unknown = sum(1 for r in rows if str(r.get("owner_type")) in ("unknown", ""))
    L.append(f"- Owner type unknown: {ot_unknown} of {len(rows)} rows (SOS worklist)")
    L.append("")
    # ---- Board Totals
    L += ["## Board Totals"]
    h = uar.get("headline", {})
    L.append(f"Book verdict: {uar.get('book_verdict', 'n/a')} — {uar.get('book_verdict_rule', '')}; public UPB on watch {_money(uar.get('public_upb_on_watch'))} of {_money(uar.get('public_upb_total'))}")
    L.append(f"{h.get('properties', 0)} properties / {h.get('units_at_risk', 0)} restricted units / {h.get('hap_units_at_risk', 0)} HAP units / {h.get('prac_units_at_risk', 0)} PRAC units / "
             f"{h.get('psh_units_at_risk', 0)} PSH units / {_money(h.get('public_upb_at_risk'))} public UPB with an owner cliff inside 36 months or already past without termination evidence (OVERDUE rows; verify)")
    cols = uar.get("columns", [])
    L.append("")
    L.append("| owner_cliff_band | " + " | ".join(cols) + " |")
    L.append("|---|" + "---|" * len(cols))
    label = {"stale_contract_date_verify": "stale contract date — verify", "no_dated_cliff": "no dated cliff", "BEYOND": "beyond horizon"}
    for band, vals in (uar.get("by_owner_cliff_band") or {}).items():
        L.append(f"| {label.get(band, band)} | " + " | ".join(str(vals.get(c, 0)) for c in cols) + " |")
    L.append("")
    byj = uar.get("by_jurisdiction") or {}
    parts = []
    for jur, bands in byj.items():
        u36 = sum(_num(bands.get(b, {}).get("units_at_risk", 0)) or 0 for b in ("OVERDUE", "CRITICAL", "URGENT", "APPROACHING"))
        p36 = sum(_num(bands.get(b, {}).get("properties", 0)) or 0 for b in ("OVERDUE", "CRITICAL", "URGENT", "APPROACHING"))
        parts.append(f"{jur} {int(p36)} properties / {int(u36)} units inside 36 mo")
    L.append("By county: " + (" / ".join(parts) if parts else "n/a"))
    if sponsors is not None and len(sponsors):
        top = sponsors.head(5)
        L.append("Top 5 sponsors by exposure: " + "; ".join(f"{r.get('sponsor_org')} — {r.get('properties')} properties, {r.get('units')} units, {_money(r.get('our_upb'))} UPB, {r.get('cliffs_le_36mo')} cliffs in 36 mo"
                                                              for r in top.to_dict(orient="records")))
    L.append("")
    # ---- Agency Act-By Calendar
    L += ["## Agency Act-By Calendar (overdue and next 90 days)", "", "| due date | property | agency_action_type | agency owner | cite | derived from | status |", "|---|---|---|---|---|---|---|"]
    n90 = 0
    if ac is not None and len(ac):
        for r in ac.to_dict(orient="records"):
            d = parse_iso(r.get("due_date"))
            if d and -366 <= (d - as_of).days <= 90:
                n90 += 1
                L.append(f"| {r.get('due_date')} | {r.get('property_name')} | {r.get('agency_action_type')} | {r.get('agency_owner')} | {r.get('statutory_cite')} | {str(r.get('derived_from'))[:80]} | {r.get('urgency')} |")
    if not n90:
        L.append("| — | no agency act-by dates inside the next 90 days (or the past 12 months) | | | | | |")
    L.append("")
    # Independent attention lists include financial concerns even without a near-term cliff or legacy route.
    L += ["## Independent Risk Dimensions", "", "Read these four assessments separately. Legacy scores do not rank these lists.", ""]
    for lane, label in (("PRESERVATION", "Preservation attention"), ("FINANCIAL", "Financial attention"),
                        ("DATA_GAPS", "Data confidence gaps"), ("READINESS_GAPS", "Intervention readiness gaps")):
        selected = [r for r in rows if lane in str(r.get("attention_lanes") or "").split(";")]
        L += [f"### {label} ({len(selected)})", ""]
        for r in selected[:int(cfg.get("max_results") or 200)]:
            L.append(f"- {r.get('property_name')}: preservation {r.get('preservation_urgency')}; financial {r.get('financial_risk')}; confidence {r.get('data_confidence')}; readiness {r.get('intervention_readiness')}")
            reason_key = {"PRESERVATION": "preservation_reasons", "FINANCIAL": "financial_reasons", "DATA_GAPS": "data_confidence_reasons", "READINESS_GAPS": "readiness_reasons"}[lane]
            L.append(f"  Reason: {r.get(reason_key) or 'See risk_dimensions.json'}")
        if not selected:
            L.append("- None in this lane.")
        L.append("")
    # ---- Intervention Queue
    L += ["## Intervention Queue", "", "Legacy route suggestions follow. Use the independent attention lists above for risk review.", ""]
    queue = [r for r in rows if r.get("primary_route") in ROUTES]
    cards = [r for r in queue if str(r.get("action_band") or r.get("urgency_band") or "") in QUEUE_BANDS_IN_CARDS]
    rest = [r for r in queue if r not in cards]
    n = 0
    for route in ROUTES:
        grp = [r for r in cards if r.get("primary_route") == route]
        if not grp:
            continue
        L.append(f"### {ROUTE_LABEL.get(route, route)} ({route}) — {len(grp)} in CRITICAL / URGENT / APPROACHING")
        L.append("")
        for r in grp[: int(cfg.get("max_results") or 200)]:
            n += 1
            L += _card(n, r, docs_by_pid, handoff_by_pid)
    if not cards:
        L.append("No lead with an action band inside 36 months carries an intervention route in this run.")
        L.append("")
    if rest:
        summ: Dict[str, Dict[str, int]] = {}
        for r in rest:
            summ.setdefault(str(r.get("action_band") or r.get("urgency_band") or "no band"), {}).setdefault(str(r.get("primary_route")), 0)
            summ[str(r.get("action_band") or r.get("urgency_band") or "no band")][str(r.get("primary_route"))] += 1
        L.append("Beyond 36 months (summarized by band and route): " + "; ".join(f"{b}: " + ", ".join(f"{rt} {c}" for rt, c in v.items()) for b, v in summ.items()))
        L.append("")
    # ---- Book Watchlist
    L += ["## Book Watchlist", ""]
    if book_rows:
        L.append("| property | ids | book_kind | upb | payment_type | maturity (basis) | affordability_end | covenant_status | am_officer | route | preservation urgency |")
        L.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for r in book_rows:
            L.append(f"| {r.get('property_name')} | {r.get('agency_loan_ids') or r.get('grant_ids') or ''} | {r.get('book_kind')} | {_money(r.get('public_upb'))} | {r.get('payment_type') or ''} | "
                     f"{r.get('our_maturity') or 'n/a'} ({r.get('our_maturity_basis') or ''}) | {r.get('affordability_end') or ''} | {r.get('covenant_status') or ''} | {r.get('am_officer') or ''} | "
                     f"{r.get('primary_route') if r.get('primary_route') != 'none' else 'monitoring'} | {r.get('preservation_urgency')} |")
    else:
        L.append("No book rows in this run (book absent or no servicing extract matched).")
    if unmatched is not None and len(unmatched):
        L.append("")
        L.append(f"Book rows not found in the inventory (servicing_unmatched.csv): {len(unmatched)} — " + "; ".join(str(x) for x in unmatched["property_name"].head(10)))
    L.append("")
    # ---- Preservation Queue
    L += ["## Preservation Queue (not in our book)", ""]
    pres = [r for r in rows if r.get("universe") == "universe_not_held" and r.get("preservation_urgency") in ("OVERDUE", "CRITICAL", "URGENT", "APPROACHING")]
    if pres:
        L.append("| property | jurisdiction | preservation urgency | financial risk | route | owner cliff | units at risk | HAP | owner type | mandate_fit |")
        L.append("|---|---|---|---|---|---|---|---|---|---|")
        for r in pres[: int(cfg.get("max_results") or 200)]:
            L.append(f"| {r.get('property_name')} | {r.get('jurisdiction')} | {r.get('preservation_urgency')} | {r.get('financial_risk')} | {r.get('primary_route')} | {r.get('owner_cliff_type')} {r.get('owner_cliff_date')} | "
                     f"{_int(r.get('units_at_risk'))} | {_int(r.get('hap_units_at_risk'))} | {r.get('owner_type')} | {r.get('mandate_fit')} |")
    else:
        L.append("No inventory-only rows with a preservation cliff within 36 months.")
    L.append("")
    # ---- Notice Compliance
    L += ["## Notice Compliance", ""]
    if nc is not None and len(nc):
        L.append("| req_id | property | statute cite (verify) | window | due date | status | evidence | remediation ask |")
        L.append("|---|---|---|---|---|---|---|---|")
        for r in nc.to_dict(orient="records"):
            if str(r.get("status")).startswith(("not yet due", "unknown")) and not r.get("remediation_ask") and r.get("req_id") not in ("PUSH-01", "HAP-01"):
                continue
            L.append(f"| {r.get('req_id')} | {r.get('property_name')} | {r.get('statute_cite')} | {r.get('window_start') or ''}..{r.get('window_end') or ''} | {r.get('due_date')} | {r.get('status')} | {r.get('evidence')} | {r.get('remediation_ask')} |")
        L.append("")
        L.append(f"{len(nc)} checklist rows in notice_compliance_queue.csv; no demand or records letter is generated before the statutory trigger it cites.")
    else:
        L.append("No PuSH window or HAP opt-out clock open in this run.")
    L.append("")
    # ---- Mandate Fit
    L += ["## Mandate Fit", ""]
    if mandate:
        open_products = []
        for p in mandate.get("products", []):
            if str(p.get("status")) not in ("open", "rolling"):
                continue
            w = p.get("application_window") or {}
            o, c = parse_iso(w.get("opens")), parse_iso(w.get("closes"))
            if (o and as_of < o) or (c and as_of > c):
                continue
            open_products.append(p.get("product_id"))
        elig = sum(1 for r in rows if r.get("mandate_fit") == "eligible")
        inel = [r for r in rows if r.get("mandate_fit") == "ineligible"]
        reasons: Dict[str, int] = {}
        for r in inel:
            for part in str(r.get("mandate_ineligible_reason") or "").split(";"):
                if part.strip():
                    reasons[part.strip()] = reasons.get(part.strip(), 0) + 1
        top_reasons = sorted(reasons.items(), key=lambda kv: -kv[1])[:3]
        L.append(f"- Products open as of {as_of.isoformat()}: {', '.join(open_products) or 'none'}; eligible leads {elig}; ineligible {len(inel)}" + (f" (top reasons: {'; '.join(f'{k} x{v}' for k, v in top_reasons)})" if top_reasons else ""))
        L.append("- The mandate filter is route-level: an ineligible row loses nofa_offer only and keeps every other route (never an exclusion, never a multiplier).")
    else:
        L.append("- No mandate file: mandate_fit no_mandate_file for every row (signal mandate_unknown on nofa_offer rows)")
    L.append("")
    # ---- Status flips
    L += ["## Status Flips Since Last Run", ""]
    if flips is not None and len(flips):
        L.append("| property | flip_type | prior | new | evidence | basis |")
        L.append("|---|---|---|---|---|---|")
        for r in flips.to_dict(orient="records")[:60]:
            if r.get("flip_type"):
                L.append(f"| {r.get('property_name')} | {r.get('flip_type')} | {r.get('prior_value')} | {r.get('new_value')} | {str(r.get('evidence'))[:80]} | {r.get('basis')} |")
        kpi = uar.get("kpi") or {}
        counts = (kpi.get("flips") or flips["flip_type"].value_counts().to_dict())
        L.append("")
        L.append("KPI: " + " · ".join(f"{k} {counts.get(k, 0)}" for k in ("notice_filed", "tenant_notice_confirmed", "qc_requested", "qc_presented", "hap_renewed", "loan_extended", "loan_recast", "covenant_cured", "recap_closed"))
                 + f" · preserved {counts.get('preserved', 0)} ({kpi.get('units_preserved_since_prior', 0)} units) · lost {counts.get('lost', 0)} ({kpi.get('units_lost_since_prior', 0)} units, evidence-based)")
    else:
        L.append("No prior run supplied (prior_run); status flips need a prior leads_scored.csv.")
    L.append("")
    # ---- Pipeline not scored
    L += ["## Pipeline, not scored", ""]
    npns = len(pns) if pns is not None else int(cal.get("rows_excluded_in_development") or 0)
    L.append(f"- {npns} rows Status = In Development -> map-progress-monitor / map-troubled-project-escalator" + (": " + "; ".join(str(x) for x in pns["property_name"].head(8)) if pns is not None and len(pns) else ""))
    L.append("")
    # ---- Data gaps
    L += ["## Data Gaps and Verification Queue", ""]
    stale = sum(1 for r in rows if "hap_date_stale" in str(r.get("signals") or ""))
    L.append(f"- Stale contract dates: {stale} (request current HAP contract / TRACS; never OVERDUE, never lost)")
    L.append(f"- Notice log unknown after due date: {sum(1 for r in rows if 'Verify — Notice Log' in str(r.get('verify_flags') or ''))} (Verify — Notice Log)")
    L.append(f"- CA log unknown after opt-out notice deadline: {sum(1 for r in rows if 'Verify — CA Log' in str(r.get('verify_flags') or ''))} (Verify — CA Log)")
    L.append(f"- Book join gaps: {len(gaps) if gaps is not None else 0} (Verify — Book Join; suggested crosswalk rows in book_join_gaps.csv)" + (f"; book rows unmatched to the inventory: {len(unmatched)}" if unmatched is not None else ""))
    L.append(f"- Documents to request from our own file room: {len(docs) if docs is not None else 0} (feeds critical-dates-tracker)")
    L.append(f"- SOS worklist: {len(sos) if sos is not None else 0} organizations")
    L.append(f"- Rejected / conflicting dates: {cal.get('rejected', 0)} rejected; {cal.get('verify_flags', '')} verify flags on the OHCS adapter" if cal else "- Calendar summary absent")
    L.append("")
    # ---- Assumptions
    L += ["## Assumptions, Statutory Cites and Limits", ""]
    L.append("- Every statutory cite in this run is verified_live: false; confirm current text before sending any letter (ORS 456.265 reads 'sanctions against withdrawing owner prohibited' — PuSH enforcement is never a fine)")
    L.append("- UPB-at-risk rule: upb where any owner-cliff PRESSURE event <= 36 mo OR covenant_status in {watch, default} OR coterminous_senior_cliff; Board_Totals band on owner_cliff_band, the queue sorts on action_band = min(agency act-by, owner cliff)")
    eq = os.path.join(pack, "equity_overlays.yaml")
    L.append(f"- Equity overlay: {_equity_overlay_state(eq)} -> high_displacement_tract / underserved_district modifiers score 0 unless a tract / district list is supplied")
    L.append("- Board headline window: owner_cliff_months_out <= 36 (CRITICAL / URGENT / APPROACHING) plus OVERDUE rows whose restriction or contract date already passed with no termination evidence (verify cases); STALE_CONTRACT_DATE HAP rows are excluded and reported on their own Board_Totals row")
    L.append(f"- Market params as of {_params_as_of(params)}; cap_rate_affordable {param(params, 'cap_rate_affordable', 'n/a')} (verify); senior_dscr_floor {param(params, 'senior_dscr_floor', 1.15)}; recap_loan_rate {param(params, 'recap_loan_rate', 0.0)}")
    L.append("- Proxy-only leads capped at PLAN; no inferred maturities (PROXY mini-perm dates excluded unless include_proxies); the agency's own ledger is RECORDED")
    L.append("- A/B/C tiers never appear; queue bands are ESCALATE / ACT / PLAN / WATCH / EXCLUDED; `none` = monitoring, `excluded` names its exclusion_reason")
    L.append(f"- Sources not verified live: {', '.join(unverified) if unverified else 'none listed'}")
    L.append("")
    path = os.path.join(run_dir, "brief.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    return path


# --------------------------------------------------------------------------- result JSON
def write_result_json(run_dir: str, cfg: Dict[str, Any], as_of: date, prof: Dict[str, Any], sources_used, manifest: Dict[str, Any], pack: str) -> str:
    leads = _read(os.path.join(run_dir, "leads_scored.csv"))
    cal = json.load(open(os.path.join(run_dir, "calendar_summary.json"))) if os.path.exists(os.path.join(run_dir, "calendar_summary.json")) else {}
    uar = json.load(open(os.path.join(run_dir, "units_at_risk.json"))) if os.path.exists(os.path.join(run_dir, "units_at_risk.json")) else {}
    scope = cfg.get("pii_scope", "organization")
    params = load_market_params(pack)

    def recs(path):
        df = _read(path)
        return df.to_dict(orient="records") if df is not None else []

    lead_rows: List[Dict[str, Any]] = []
    if leads is not None and len(leads):
        leads, _ = apply_pii_scope(leads, scope)
        for r in leads.to_dict(orient="records"):
            fj = r.pop("factors_json", "")
            try:
                r["factors"] = json.loads(fj) if fj else {}
            except Exception:
                r["factors"] = {}
            lead_rows.append(r)
    degraded = cal.get("degraded_note") or ""
    res = {
        "run": {"skill": "preservation-loan-book", "version": PLB_VERSION, "as_of_date": as_of.isoformat(), "market_id": cfg.get("market_id"), "agency_profile": cfg.get("agency_profile", "hfa"),
                "agency_name": prof.get("agency_name"), "universe": cfg.get("universe", "all"), "mandate_file": cfg.get("mandate_file") or os.path.join(pack, "mandate.json"),
                "pii_scope": scope, "book_coverage": cfg.get("book_coverage", "partial"), "book_extract": cfg.get("servicing_extract"), "horizon_years": cfg.get("horizon_years", 10),
                "regulatory_horizon_years": cfg.get("regulatory_horizon_years") or cfg.get("horizon_years", 10), "noah_watch": bool(cfg.get("noah_watch")),
                "include_proxies": bool(cfg.get("include_proxies")), "degraded": bool(degraded.strip()), "degraded_reason": degraded.strip(),
                "records_classification": RECORDS_CLASSIFICATION, "header": cal.get("header", ""), "manifest_path": os.path.join(run_dir, "manifest.json")},
        "geography": {"mode": cfg.get("geography_mode", "metro_core"), "county_fips": cal.get("counties", []), "rows_in_geography": cal.get("rows_in_geography"),
                      "rows_excluded_in_development": cal.get("rows_excluded_in_development"), "resolution_order": ["county_field", "zip_crosswalk", "point_in_polygon", "city_name_weak"]},
        "sources": sources_used,
        "assumptions": {"market_params_as_of": params.get("as_of") if isinstance(params, dict) else None, "cap_rate_affordable": param(params, "cap_rate_affordable", None),
                        "senior_dscr_floor": param(params, "senior_dscr_floor", 1.15), "recap_loan_rate": param(params, "recap_loan_rate", 0.0),
                        "upb_at_risk_rule": "upb where any owner-cliff PRESSURE event <= 36 mo OR covenant_status in {watch, default} OR coterminous_senior_cliff",
                        "band_rules": "Board_Totals and Units_by_Year band on owner_cliff_band; the queue sorts on action_band = min(agency act-by, owner cliff); bands are months",
                        "equity_overlay": "present" if os.path.exists(os.path.join(pack, "equity_overlays.yaml")) else "absent; stacking_geography_equity modifiers scored 0",
                        "statutory_text_status": "every cite verified_live: false in this build; confirm current text before sending"},
        "calendar_summary": {k: v for k, v in cal.items() if k not in ("log", "pipeline_not_scored")},
        "summary": {"properties_in_geography": cal.get("rows_in_geography"), "leads": len(lead_rows),
                    "book_rows": cal.get("book_rows", 0), "book_rows_monitored": sum(1 for r in lead_rows if r.get("universe") == "our_book" and r.get("primary_route") == "none"),
                    "book_rows_on_watch": sum(1 for r in lead_rows if r.get("universe") == "our_book" and r.get("primary_route") != "none"),
                    "book_join_grades": cal.get("book_join_grades", {}), "book_match": cal.get("book_match_counts", {}),
                    "queue_counts": pd.Series([r.get("queue_band") for r in lead_rows]).value_counts().to_dict() if lead_rows else {},
                    "route_counts": pd.Series([r.get("primary_route") for r in lead_rows]).value_counts().to_dict() if lead_rows else {},
                    "units_at_risk": uar, "sponsor_exposure": recs(os.path.join(run_dir, "sponsor_exposure.csv")), "book_verdict": uar.get("book_verdict"),
                    "owner_type_unknown_share": round(sum(1 for r in lead_rows if r.get("owner_type") in ("unknown", "")) / len(lead_rows), 3) if lead_rows else 0.0,
                    "notice_log_unknown_share": cal.get("notice_log_unknown_share", 0.0),
                    "data_gaps": ([{"gap": "no agency servicing extract", "effect": "our_capital_at_risk 0 for every row; book_match book_absent",
                                    "fix": "run ingest_servicing_extract.py on the loan/grant system export"}] if not cal.get("book_present") else [])
                    + ([{"gap": "stale HAP contract dates", "effect": f"{cal.get('stale_contract_dates', 0)} rows flagged Verify — Stale Contract Date", "fix": "request current HAP contract / TRACS"}] if cal.get("stale_contract_dates") else [])},
        "leads": lead_rows,
        "book_watchlist": [r for r in lead_rows if r.get("universe") == "our_book"],
        "preservation_queue": [r for r in lead_rows if r.get("universe") == "universe_not_held"],
        "notice_compliance_queue": recs(os.path.join(run_dir, "notice_compliance_queue.csv")),
        "optout_qc_responses": recs(os.path.join(run_dir, "optout_qc_responses.csv")),
        "agency_calendar": recs(os.path.join(run_dir, "agency_calendar.csv")),
        "status_flips": recs(os.path.join(run_dir, "status_flips.csv")),
        "rejects": recs(os.path.join(run_dir, "rejects.csv")),
        "pipeline_not_scored": recs(os.path.join(run_dir, "pipeline_not_scored.csv")),
        "handoffs": {fn[:-5]: os.path.join("handoff", fn) for fn in sorted(os.listdir(os.path.join(run_dir, "handoff")))} if os.path.isdir(os.path.join(run_dir, "handoff")) else {},
    }
    path = os.path.join(run_dir, "result.json")
    json.dump(res, open(path, "w"), indent=1, default=str)
    return path


# --------------------------------------------------------------------------- main
def execute(argv, run_dir, run_id):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True)
    ap.add_argument("--from", dest="from_stage", default="discover", choices=STAGES)
    ap.add_argument("--prior-run", default=None)
    ap.add_argument("--explain", default=None)
    ap.add_argument("--as-of", default=None, help="overrides config as_of_date")
    a = ap.parse_args(argv)
    cfg = json.load(open(a.config))
    as_of = parse_as_of(a.as_of or cfg.get("as_of_date"))
    pack = cfg.get("pack") or os.path.normpath(os.path.join(HERE, "..", "references", "sources", "oregon-portland"))
    schemas = load_dataset_schemas(pack)
    directory = load_source_directory(pack)
    profile_name = cfg.get("agency_profile", "hfa")
    prof = agency_profile(profile_name, pack)
    scope = cfg.get("pii_scope", "organization")
    log: List[str] = []
    hz = str(cfg.get("horizon_years", 10))
    rhz = int(cfg.get("regulatory_horizon_years") or cfg.get("horizon_years", 10))   # int in the manifest; str() where it joins an argv
    mode = cfg.get("geography_mode", "metro_core")
    counties = cfg.get("counties")
    prior = a.prior_run or cfg.get("prior_run")
    manifest: Dict[str, Any] = {"as_of_date": as_of.isoformat(), "market_id": cfg.get("market_id"), "config": cfg, "pack": pack, "plb_version": PLB_VERSION,
                                "python": sys.version.split()[0], "run_id": run_id, "stages": {}, "inputs": [],
                                "flags": {"agency_profile": profile_name, "universe": cfg.get("universe", "all"), "mandate_file": cfg.get("mandate_file") or os.path.join(pack, "mandate.json"),
                                          "pii_scope": scope, "book_coverage": cfg.get("book_coverage", "partial"), "noah_watch": bool(cfg.get("noah_watch")),
                                          "horizon_years": cfg.get("horizon_years", 10), "regulatory_horizon_years": rhz, "include_proxies": bool(cfg.get("include_proxies")),
                                          "owner_types_include": cfg.get("owner_types_include"), "owner_types_exclude": cfg.get("owner_types_exclude"), "programs": cfg.get("programs"),
                                          "records_classification": RECORDS_CLASSIFICATION}}
    start = STAGES.index(a.from_stage)

    # ---- discover
    found = discover(cfg, schemas)
    manifest["inputs"] = found
    print("[discover] " + "; ".join(f"{os.path.basename(f['file'])} -> {f['schema']} (vintage {f['vintage']} from {f['vintage_source']})" for f in found) if found else "[discover] no input files found")
    by_schema: Dict[str, str] = {}
    for f in found:
        by_schema.setdefault(f["schema"], f["file"])
    zip_xw = by_schema.get("zip_county_crosswalk", cfg.get("zip_crosswalk"))
    for f in found:
        if f["schema"] is None:
            log.append(f"unprocessed input (schema not recognized): {f['file']}")

    # ---- universe (servicing -> adapters -> merge -> units -> agency calendar)
    if start <= STAGES.index("universe"):
        if "ohcs_affordable_housing_inventory" not in by_schema:
            print("[universe] no OHCS / HFA inventory file recognized; the inventory is the universe and is required", file=sys.stderr)
            raise ValueError("no recognized inventory; cannot produce a current run")
        else:
            cmd = [PY, os.path.join(HERE, "build_universe.py"), "--pack", pack, "--mode", mode, "--agency-profile", profile_name, "--ohcs", by_schema["ohcs_affordable_housing_inventory"],
                   "--out-dir", run_dir, "--as-of", as_of.isoformat(), "--horizon-years", hz, "--regulatory-horizon-years", str(rhz), "--book-coverage", cfg.get("book_coverage", "partial")]
            if counties:
                cmd += ["--counties", ",".join(counties)]
            if cfg.get("target_city"):
                cmd += ["--city", cfg["target_city"]]
            if "agency_servicing_extract" in by_schema:
                cmd += ["--book", by_schema["agency_servicing_extract"]]
            if cfg.get("book_crosswalk"):
                cmd += ["--crosswalk", cfg["book_crosswalk"]]
            if "hud_mf_assistance_sec8" in by_schema:
                cmd += ["--hud-sec8", by_schema["hud_mf_assistance_sec8"]]
            if "hud_fhasl_active" in by_schema:
                cmd += ["--hud-fhasl", by_schema["hud_fhasl_active"]]
                if "hud_fhasl_terminated" in by_schema:
                    cmd += ["--hud-fhasl-terminated", by_schema["hud_fhasl_terminated"]]
            if "ohcs_push_forecast" in by_schema:
                cmd += ["--forecast", by_schema["ohcs_push_forecast"]]
                if cfg.get("prior_forecast"):
                    cmd += ["--prior-forecast", cfg["prior_forecast"]]
            if "hud_reac_scores" in by_schema:
                cmd += ["--reac", by_schema["hud_reac_scores"]]
            if zip_xw:
                cmd += ["--zip-crosswalk", zip_xw]
            if cfg.get("include_proxies"):
                cmd += ["--include-proxies"]
            if cfg.get("noah_watch") and "noah_candidates" in by_schema:
                cmd += ["--noah-watch", "--noah", by_schema["noah_candidates"]]
            if scope == "internal":
                cmd += ["--internal"]
            rc = run_cmd(cmd, log)
            manifest["stages"]["universe"] = "ok" if rc == 0 else f"failed rc={rc}"
            if rc != 0:
                manifest["log"] = log
                json.dump(manifest, open(os.path.join(run_dir, "manifest.json"), "w"), indent=2, default=str)
                sys.exit(rc)

    for name in ("leads.csv", "events.csv", "calendar_summary.json"):
        if not os.path.isfile(os.path.join(run_dir, name)):
            raise ValueError(f"universe did not produce {name}")
    # ---- calendar (console view; header must equal the universe header)
    if start <= STAGES.index("calendar") and os.path.exists(os.path.join(run_dir, "events.csv")):
        qpath = os.path.join(run_dir, "calendar_query.json")
        run_cmd([PY, os.path.join(HERE, "query_calendar.py"), "--events", os.path.join(run_dir, "events.csv"), "--within-years", hz, "--regulatory-within-years", str(rhz),
                 "--as-of", as_of.isoformat(), "--json", qpath, "--limit", "15", "--show-agency"], log)
        try:
            q = json.load(open(qpath))
            c = json.load(open(os.path.join(run_dir, "calendar_summary.json")))
            manifest["stages"]["calendar"] = {"header": c.get("header"), "header_matches_query": q.get("header") == c.get("header")}
        except Exception as exc:
            raise RuntimeError(f"calendar verification failed: {exc}") from exc
        if not manifest["stages"]["calendar"]["header_matches_query"]:
            raise ValueError("calendar headers disagree; publication blocked")

    # ---- score
    if start <= STAGES.index("score") and os.path.exists(os.path.join(run_dir, "leads.csv")):
        cmd = [PY, os.path.join(HERE, "score_preservation.py"), "--leads", os.path.join(run_dir, "leads.csv"), "--events", os.path.join(run_dir, "events.csv"), "--pack", pack,
               "--agency-profile", profile_name, "--universe", cfg.get("universe", "all"), "--horizon-years", hz, "--as-of", as_of.isoformat(),
               "--out", os.path.join(run_dir, "leads_scored.csv")]
        for key in ("financial_observations", "readiness_observations"):
            if cfg.get(key):
                cmd += ["--" + key.replace("_", "-"), cfg[key]]
                manifest[key + "_input"] = {"file": cfg[key], "sha256": sha256(cfg[key])}
        if cfg.get("financial_policy"):
            policy_path = os.path.join(run_dir, "financial_policy.json")
            atomic_json(policy_path, cfg["financial_policy"])
            cmd += ["--financial-policy", policy_path]
        if cfg.get("mandate_file"):
            cmd += ["--mandate", cfg["mandate_file"]]
        if cfg.get("scoring_dir"):
            cmd += ["--scoring-dir", cfg["scoring_dir"]]
        for key, flag in (("owner_types_include", "--owner-types-include"), ("owner_types_exclude", "--owner-types-exclude")):
            if cfg.get(key):
                cmd += [flag, ",".join(cfg[key])]
        if cfg.get("noah_watch"):
            cmd += ["--noah-watch"]
        if scope == "internal":
            cmd += ["--internal"]
        if prior and os.path.exists(os.path.join(prior, "leads_scored.csv")):
            cmd += ["--prior", os.path.join(prior, "leads_scored.csv")]
        if a.explain:
            cmd += ["--explain", a.explain]
        rc = run_cmd(cmd, log)
        manifest["stages"]["score"] = "ok" if rc == 0 else f"failed rc={rc}"

    # ---- sources used: a file on disk proves the file, not the live portal
    sources_used = []
    for f in found:
        sid = ADAPTERS.get(f["schema"], (None, f["schema"] or os.path.basename(f["file"])))[1]
        entry = directory.get(sid, {})
        if sid == "agency_servicing_extract":
            verified = "true (the agency's own ledger; RECORDED)"
        else:
            verified = url_verified(entry) if entry else "false (not in sources.md)"
        sources_used.append({"source_id": sid, "file": os.path.basename(f["file"]), "sha256": f["sha256"], "vintage": f["vintage"], "vintage_source": f["vintage_source"],
                             "file_verified": "true (file opened; header matched schema)" if f["schema"] else "false (schema not recognized)",
                             "url_verified_live": verified, "verified_live": verified, "access": entry.get("access", "manual" if sid == "agency_servicing_extract" else ""),
                             "url": entry.get("url", ""), "note": "a file on disk proves the file, not the live portal"})
    json.dump(sources_used, open(os.path.join(run_dir, "sources_used.json"), "w"), indent=2)
    unverified = [sid for sid in AFFORDABLE_SOURCE_IDS if sid in directory and not url_verified(directory[sid]).startswith("true")]
    unverified += [s["source_id"] for s in sources_used if not str(s["url_verified_live"]).startswith("true") and s["source_id"] not in unverified]
    manifest["sources_verified_live_false"] = unverified

    # ---- diff before workbook / brief so KPI rows are available (the diff stage below is idempotent)
    prior_scored = os.path.join(prior, "leads_scored.csv") if prior else None
    if start <= STAGES.index("workbook") and prior_scored and os.path.exists(prior_scored) and os.path.exists(os.path.join(run_dir, "leads_scored.csv")):
        cmd = [PY, os.path.join(HERE, "diff_forecast.py"), "--current", os.path.join(run_dir, "leads_scored.csv"), "--prior", prior_scored, "--current-events", os.path.join(run_dir, "events.csv"),
               "--out", os.path.join(run_dir, "status_flips.csv"), "--summary", os.path.join(run_dir, "kpi_summary.json")]
        if os.path.exists(os.path.join(prior, "events.csv")):
            cmd += ["--prior-events", os.path.join(prior, "events.csv")]
        run_cmd(cmd, log)

    # ---- workbook (+ board packet)
    if start <= STAGES.index("workbook") and os.path.exists(os.path.join(run_dir, "leads_scored.csv")):
        wb = os.path.join(run_dir, cfg.get("workbook_name", "Preservation_LoanBook_10yr.xlsx"))
        cmd = [PY, os.path.join(HERE, "build_board_workbook.py"), "--leads-scored", os.path.join(run_dir, "leads_scored.csv"), "--events", os.path.join(run_dir, "events.csv"),
               "--calendar", os.path.join(run_dir, "calendar_summary.json"), "--rejects", os.path.join(run_dir, "rejects.csv"), "--pack", pack,
               "--sources", os.path.join(run_dir, "sources_used.json"), "--agency-profile", profile_name, "--out", wb, "--as-of", as_of.isoformat()]
        if cfg.get("board_packet", True):
            cmd += ["--board-packet"]
        if scope == "internal":
            cmd += ["--internal"]
        if prior_scored and os.path.exists(prior_scored):
            cmd += ["--prior", prior_scored]
            if os.path.exists(os.path.join(prior, "events.csv")):
                cmd += ["--prior-events", os.path.join(prior, "events.csv")]
        rc = run_cmd(cmd, log)
        manifest["stages"]["workbook"] = {"workbook": wb, "rc": rc}

    # ---- handoffs
    if start <= STAGES.index("handoffs") and os.path.exists(os.path.join(run_dir, "leads_scored.csv")):
        cmd = [PY, os.path.join(HERE, "make_handoffs.py"), "--leads-scored", os.path.join(run_dir, "leads_scored.csv"), "--out-dir", os.path.join(run_dir, "handoff"), "--pack", pack,
               "--max", str(cfg.get("max_results") or 200)]
        if cfg.get("handoff_routes"):
            cmd += ["--routes", *cfg["handoff_routes"]]
        rc = run_cmd(cmd, log)
        manifest["stages"]["handoffs"] = "ok" if rc == 0 else f"failed rc={rc}"

    # ---- brief
    if start <= STAGES.index("brief") and os.path.exists(os.path.join(run_dir, "leads_scored.csv")):
        bp = write_brief(run_dir, dict(cfg, counties=counties or [], geography_mode=mode), as_of, sources_used, unverified, prof, pack)
        print(f"[brief] wrote {bp}")
        manifest["stages"]["brief"] = bp

    # ---- diff (status flips; KPI)
    if start <= STAGES.index("diff") and prior_scored and os.path.exists(prior_scored) and os.path.exists(os.path.join(run_dir, "leads_scored.csv")):
        cmd = [PY, os.path.join(HERE, "diff_forecast.py"), "--current", os.path.join(run_dir, "leads_scored.csv"), "--prior", prior_scored, "--current-events", os.path.join(run_dir, "events.csv"),
               "--out", os.path.join(run_dir, "status_flips.csv"), "--summary", os.path.join(run_dir, "kpi_summary.json")]
        if os.path.exists(os.path.join(prior, "events.csv")):
            cmd += ["--prior-events", os.path.join(prior, "events.csv")]
        run_cmd(cmd, log)
        try:
            manifest["stages"]["diff"] = json.load(open(os.path.join(run_dir, "kpi_summary.json")))
        except Exception:
            manifest["stages"]["diff"] = "written"

    # ---- normalized positions and separate risk dimensions
    scored_frame = _read(os.path.join(run_dir, "leads_scored.csv"))
    if scored_frame is None:
        raise ValueError("scoring produced no readable current output")
    positions = []
    for row in scored_frame.to_dict(orient="records"):
        for position in parse_instruments(row.get("instruments_json")):
            exposure = grant_exposure([position], as_of)
            positions.append(dict(position, property_id=row["property_id"], recapture_exposure=exposure["exposure"], recapture_flag=exposure["flag"]))
    from plb.instruments import FIELDS
    pd.DataFrame(positions, columns=["property_id", "instrument_id", *FIELDS, "recapture_exposure", "recapture_flag"]).to_csv(os.path.join(run_dir, "instruments.csv"), index=False)
    from plb.book_model import build_model
    graph = build_model(scored_frame.to_dict(orient="records"), _read(os.path.join(run_dir, "events.csv")).to_dict(orient="records"),
                        _read(os.path.join(run_dir, "agency_calendar.csv")).to_dict(orient="records"), manifest)
    atomic_json(os.path.join(run_dir, "book_model.json"), graph)
    pd.DataFrame(graph["covenants"], columns=["covenant_id", "instrument_id", "property_id", "covenant_type", "effective_from", "effective_to", "status", "verification"]).to_csv(os.path.join(run_dir, "covenants.csv"), index=False)
    for entity in ("covenants", "events", "evidence", "event_evidence", "actions", "action_events", "linkage_issues"):
        rows = [{k: json.dumps(v, sort_keys=True) if isinstance(v, (dict, list)) else v for k, v in row.items()} for row in graph[entity]]
        pd.DataFrame(rows).to_csv(os.path.join(run_dir, f"model_{entity}.csv"), index=False)
    risk_rows = json.load(open(os.path.join(run_dir, "risk_dimensions.json"), encoding="utf-8"))
    # ---- result JSON, manifest, checkpoint
    if os.path.exists(os.path.join(run_dir, "leads_scored.csv")):
        rp = write_result_json(run_dir, cfg, as_of, prof, sources_used, manifest, pack)
        result = json.load(open(rp, encoding="utf-8"))
        result["instruments"] = positions
        result["book_model"] = graph
        result["risk_dimensions"] = risk_rows
        result["dimension_counts"] = json.load(open(os.path.join(run_dir, "dimension_counts.json"), encoding="utf-8"))
        result["legacy_score_notice"] = "intervention_score and queue_band are compatibility diagnostics; use separate dimensions and attention lists"
        atomic_json(rp, result)
        manifest["stages"]["result_json"] = rp
    required = ("leads_scored.csv", "result.json", "brief.md", cfg.get("workbook_name", "Preservation_LoanBook_10yr.xlsx"))
    for name in required:
        if not os.path.isfile(os.path.join(run_dir, name)):
            raise ValueError(f"required output missing: {name}")
    manifest["status"] = "COMPLETE"
    manifest["log"] = log
    manifest["outputs"] = {"run_dir_files": sorted(os.listdir(run_dir)),
                           "handoff_files": sorted(os.listdir(os.path.join(run_dir, "handoff"))) if os.path.isdir(os.path.join(run_dir, "handoff")) else [],
                           "worklists": [p for p in ("handoff/sos_worklist.csv", "handoff/documents_to_request.csv", "handoff/board_packet.csv", "notice_compliance_queue.csv",
                                                     "nofa_targets.csv", "servicing_unmatched.csv", "status_flips.csv") if os.path.exists(os.path.join(run_dir, p))]}
    json.dump(manifest, open(os.path.join(run_dir, "manifest.json"), "w"), indent=2, default=str)
    if cfg.get("pipeline_mode"):
        root = cfg.get("pipeline_root", os.getcwd())
        mid = cfg.get("market_id") or "market"
        sdir = os.path.join(root, "data", "status", mid, "asset_management")
        os.makedirs(sdir, exist_ok=True)
        uar = json.load(open(os.path.join(run_dir, "units_at_risk.json"))) if os.path.exists(os.path.join(run_dir, "units_at_risk.json")) else {}
        cal = json.load(open(os.path.join(run_dir, "calendar_summary.json"))) if os.path.exists(os.path.join(run_dir, "calendar_summary.json")) else {}
        scored = _read(os.path.join(run_dir, "leads_scored.csv"))
        status = "COMPLETE" if scored is not None else "FAILED"
        if status == "COMPLETE" and (cal.get("degraded_note") or "").strip():
            status = "PARTIAL"
        cp = {"agent": "preservation-loan-book", "phase": "asset_management", "market_id": mid, "status": status, "as_of": as_of.isoformat(),
              "payload": {"result_json": os.path.join(run_dir, "result.json"), "workbook": (manifest["stages"].get("workbook") or {}).get("workbook"),
                          "board_packet": os.path.join(run_dir, "board_packet.md") if os.path.exists(os.path.join(run_dir, "board_packet.md")) else None,
                          "brief": manifest["stages"].get("brief"), "queue_counts": scored["queue_band"].value_counts().to_dict() if scored is not None and len(scored) else {},
                          "units_at_risk_headline": uar.get("headline", {}), "book_verdict": uar.get("book_verdict"), "degraded": bool((cal.get("degraded_note") or "").strip()),
                          "handoffs": {fn[:-5]: os.path.join("handoff", fn) for fn in manifest["outputs"]["handoff_files"] if fn.endswith(".json")}}}
        cp["run_id"] = run_id
        atomic_json(os.path.join(sdir, "preservation-loan-book.json"), cp)
        ldir = os.path.join(root, "data", "logs", mid)
        os.makedirs(ldir, exist_ok=True)
        with open(os.path.join(ldir, "asset_management.log"), "a", encoding="utf-8") as fh:
            fh.write(f"{datetime.now().isoformat(timespec='seconds')} preservation-loan-book {status} as_of={as_of.isoformat()} header=\"{cal.get('header', '')}\"\n")
        print(f"[pipeline] checkpoint {os.path.join(sdir, 'preservation-loan-book.json')} ({status})")
    print(f"[pipeline] run dir {run_dir}; manifest.json written")


def atomic_json(path, data):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    temp = path + "." + uuid.uuid4().hex + ".tmp"
    try:
        with open(temp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, default=str)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.remove(temp)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--config", required=True)
    parser.add_argument("--as-of", default=None)
    parser.add_argument("--from", dest="from_stage", default="discover")
    if "--help" in argv or "-h" in argv:
        return execute(argv, "", "")
    args, _ = parser.parse_known_args(argv)
    with open(args.config, encoding="utf-8") as fh:
        cfg = json.load(fh)
    if args.from_stage not in ("discover", "universe"):
        raise ValueError("partial restarts are disabled: run from discover/universe to prevent stale artifact reuse")
    as_of = parse_as_of(args.as_of or cfg.get("as_of_date"))
    run_id = uuid.uuid4().hex
    date_dir = os.path.abspath(os.path.join(cfg.get("out_dir", "runs"), as_of.isoformat()))
    run_dir = os.path.join(date_dir, run_id)
    os.makedirs(run_dir, exist_ok=False)
    try:
        execute(argv, run_dir, run_id)
        if cfg.get("operations_db"):
            from plb.operations import connect, import_run
            db = connect(cfg["operations_db"])
            try:
                with open(os.path.join(run_dir, "manifest.json"), encoding="utf-8") as fh:
                    manifest = json.load(fh)
                def rows(name):
                    return pd.read_csv(os.path.join(run_dir, name), dtype=str, keep_default_na=False).to_dict(orient="records")
                import_run(db, manifest, rows("leads_scored.csv"), rows("events.csv"), rows("agency_calendar.csv"))
            finally:
                db.close()
        # Consumers discover only completely generated outputs via this atomic pointer.
        atomic_json(os.path.join(date_dir, "latest.json"), {"run_id": run_id, "run_dir": run_dir, "as_of": as_of.isoformat()})
    except (Exception, SystemExit) as exc:
        failure = {"run_id": run_id, "status": "FAILED", "as_of": as_of.isoformat(), "error": str(exc), "run_dir": run_dir}
        atomic_json(os.path.join(run_dir, "failure.json"), failure)
        atomic_json(os.path.join(date_dir, "last_attempt.json"), failure)
        if cfg.get("pipeline_mode"):
            path = os.path.join(cfg.get("pipeline_root", os.getcwd()), "data", "status", cfg.get("market_id") or "market", "asset_management", "preservation-loan-book.json")
            atomic_json(path, {"agent": "preservation-loan-book", "phase": "asset_management", **failure})
        raise
    atomic_json(os.path.join(date_dir, "last_attempt.json"), {"run_id": run_id, "status": "COMPLETE", "run_dir": run_dir})
    return run_dir


if __name__ == "__main__":
    main()
