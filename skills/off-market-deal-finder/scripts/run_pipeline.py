#!/usr/bin/env python3
"""Orchestrate the off-market-deal-finder v2 pipeline from a run_config.json.

Stages (in order; `--from <stage>` restarts at one of them using the artifacts already in the run dir):
  discover  -> scan `inbox` and `local_datasets[]`, detect each file's schema from its header, date it from the
               filename (YYYYMMDD / YYYY-MM-DD) and fall back to mtime (vintage_source recorded)
  adapters  -> ohcs_inventory_targets / normalize_hud_insured / normalize_hud_sec8 / normalize_ohcs_forecast /
               normalize_recorder_index / normalize_assessor_taxlots for every recognized file
  merge     -> merge_leads
  calendar  -> query_calendar (writes calendar_summary.json; the basis header is quoted in the brief)
  score     -> score_leads with every run-config input that affects ranking (query_type, owner_types_include/exclude,
               lender_types, price_or_value_band, buyer_profile, unit_range, programs, strict_size_fit)
  workbook  -> build_workbook (+ Diff_vs_Prior when --prior-run / prior_run is set); no recalc (literal cells)
  handoffs  -> make_handoffs for Tier A (and more when `handoff_tiers` says so): sibling JSON + sos_worklist.csv + documents_to_request.csv
  brief     -> markdown brief (Run Summary with basis breakdown and query hits, event horizon, cards, tracks, actions, gaps)
  diff      -> diff.csv against the prior run

Writes runs/<as_of>/manifest.json: config snapshot, every input file's sha256 / vintage / vintage_source, stage outputs,
sources still verified_live=false, scripts version. No network calls. `--explain <property_id>` prints the scoring
arithmetic for one lead.

Usage:
  python scripts/run_pipeline.py --config run_config.json [--from score] [--prior-run runs/2026-07-01] [--explain addr:...]
Config keys mirror the SKILL.md inputs; see references/sample-output/run_config.example.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import date
from typing import Any, Dict, List, Optional

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from omdf import __version__ as OMDF_VERSION  # noqa: E402
from omdf.calendar import header_line  # noqa: E402
from omdf.dates import parse_as_of  # noqa: E402
from omdf.schema import detect_schema, load_dataset_schemas  # noqa: E402
from smoke_test_sources import parse_tables  # noqa: E402

STAGES = ["discover", "adapters", "merge", "calendar", "score", "workbook", "handoffs", "brief", "diff"]
PY = sys.executable
FILENAME_DATE_RE = re.compile(r"(20\d{2})[-_]?(\d{2})[-_]?(\d{2})")
# schema id -> (adapter script, sources.md source_id used to look up URL / access / verified_live)
ADAPTERS = {
    "ohcs_affordable_housing_inventory": ("ohcs_inventory_targets.py", "ohcs_oahi"),
    "hud_fhasl_active": ("normalize_hud_insured.py", "hud_fhasl_active / hud_fhasl_terminated"),
    "hud_mf_assistance_sec8": ("normalize_hud_sec8.py", "hud_mf_assist_sec8"),
    "ohcs_push_forecast": ("normalize_ohcs_forecast.py", "ohcs_push_forecast"),
    "recorder_index_export": ("normalize_recorder_index.py", "multco_records"),
    "assessor_taxlots": ("normalize_assessor_taxlots.py", "multco_sail"),
}
CLASS_SOURCE_IDS = {  # sources the brief lists as still unverified for each class (from sources.md source_id column)
    "affordable_regulated": ["ohcs_oahi", "ohcs_push_forecast", "ohcs_hca_optout", "hud_fhasl_active / hud_fhasl_terminated", "hud_mf_assist_sec8",
                             "hud_lihtc_db", "hud_reac", "usda_mfh_exit", "nhpd", "multco_records", "oregon_sos_registry"],
    "market_rate_mf": ["hud_fhasl_active / hud_fhasl_terminated", "fannie_dus_disclose", "freddie_msia", "sec_edgar_ex102", "multco_records",
                       "multco_sail", "ojd_smart_search", "oregon_sos_registry", "oregon_sos_ucc", "portland_bds_cases"],
    "sfr_small_res": ["multco_records", "multco_proptax", "multco_sail", "ojd_smart_search", "pacer_orb", "portland_bds_cases", "clark_wa_auditor", "public_notice_oregon"],
}


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
    if p.stderr.strip():
        print(p.stderr.strip(), file=sys.stderr)
    return p.returncode


def header_columns(path: str) -> List[str]:
    try:
        if path.lower().endswith((".xlsx", ".xls", ".xlsm")):
            return [str(c).strip() for c in pd.read_excel(path, nrows=0).columns]
        return [str(c).strip() for c in pd.read_csv(path, nrows=0, dtype=str, encoding="utf-8-sig").columns]
    except Exception:
        return []


def load_source_directory(pack: str) -> Dict[str, Dict[str, str]]:
    """source_id -> {url, access, verified_live (declared in sources.md), live_status (from sources_status.json)}."""
    out: Dict[str, Dict[str, str]] = {}
    sp = os.path.join(pack, "sources.md")
    if os.path.exists(sp):
        with open(sp, "r", encoding="utf-8") as fh:
            for row in parse_tables(fh.read()):
                sid = row.get("source_id")
                if sid:
                    out[sid] = {"url": row.get("url", ""), "access": row.get("access", ""), "verified_live_declared": row.get("verified_live", ""),
                                "adapter": row.get("adapter", ""), "class": row.get("class", "")}
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
    if "mirror" in low:
        return "false (statute mirror read; official site not fetched)"
    return f"false ({decl or 'not fetched in this build'})"


def discover(cfg: Dict[str, Any], schemas: Dict[str, Any]) -> List[Dict[str, Any]]:
    files: List[str] = []
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
        v, vs = file_vintage(f)
        out.append({"file": f, "schema": sid, "sha256": sha256(f), "columns": cols[:12], "vintage": v, "vintage_source": vs})
    return out


def _render_event(r: Dict[str, Any], prefix: str) -> str:
    et = r.get(f"{prefix}_event_type")
    if not et:
        return ""
    return f"{et} {r.get(f'{prefix}_event_date')} [{r.get(f'{prefix}_basis')}] — {r.get(f'{prefix}_months_out')} mo"


def _any_first_event(r: Dict[str, Any]) -> str:
    """Whichever of first_debt / first_reg exists (partnership and counterparty rows used to print an empty event)."""
    parts = [x for x in (_render_event(r, "first_debt"), _render_event(r, "first_reg")) if x]
    return "; ".join(parts) if parts else "no dated DEBT/REGULATORY event inside horizon (other-family signals only)"


def write_brief(run_dir: str, cfg: Dict[str, Any], as_of: date, sources_used: List[Dict[str, Any]], class_unverified: List[str]) -> str:
    leads = pd.read_csv(os.path.join(run_dir, "leads_scored.csv"), dtype=str, keep_default_na=False)
    cal = json.load(open(os.path.join(run_dir, "calendar_summary.json")))
    hdr = cal.get("header") or header_line(cal)
    qt = cfg.get("query_type") or "all"
    hits = leads["query_hit"].astype(str).str.lower().isin(["true", "1"]) if "query_hit" in leads else pd.Series([True] * len(leads))
    L = []
    L.append(f"# Off-Market Targets — {cfg.get('market_id', 'market')} — {cfg.get('asset_class', 'auto')} — {qt} — as of {as_of.isoformat()}\n")
    L.append("## Run Summary\n")
    L.append(f"- as_of_date: {as_of.isoformat()}  |  geography_mode: {cfg.get('geography_mode')}  |  counties: {', '.join(cfg.get('counties') or [])}  |  buyer_profile: {cfg.get('buyer_profile', 'principal')}")
    L.append(f"- horizon_years (debt): {cfg.get('horizon_years', 5)}  |  regulatory_horizon_years: {cfg.get('regulatory_horizon_years') or cfg.get('horizon_years', 5)}  |  query_type: {qt}")
    L.append(f"- files ingested: " + "; ".join(f"{s['file']} (vintage {s['vintage']} from {s['vintage_source']})" for s in sources_used) if sources_used else "- files ingested: none")
    L.append(f"- dated events inside horizon: {cal.get('events', '')} on {cal.get('properties', '')} properties (+{cal.get('helper_events', 0)} helper deadlines not counted)")
    L.append(f"- **Basis breakdown (read this before the count): {hdr}**")
    tiers = leads["tier"].value_counts().to_dict() if len(leads) else {}
    routes = leads["route"].value_counts().to_dict() if len(leads) else {}
    L.append(f"- leads: {len(leads)}  |  tiers: {tiers}  |  routes: {routes}")
    if qt != "all":
        L.append(f"- **{qt} hits: {int(hits.sum())} leads carry a dated {qt.replace('_', ' ')} event; {int((~hits).sum())} regulatory-/other-family-only leads are shown as secondary.** "
                 f"A `{qt}` query is not the same list as `all`; the secondary leads are kept because their owners face a dated event of another kind.")
    b = cal.get("by_basis", {})
    if b.get("RECORDED", 0) == 0:
        L.append("- Degraded run: no RECORDED dates. Every maturity is REPORTED/DERIVED/PROXY, so Tier A is out of reach until a RECORDED or declared-intent "
                 "family arrives: HUD FHASL Active, HUD MF Assistance & Sec 8, the OHCS 10-Year Forecast (normalize_ohcs_forecast.py; field names unverified) or recorder images.")
    L.append(f"- Sources still verified_live=false (URL not fetched in this build; file-on-disk checks do not count): {', '.join(class_unverified) if class_unverified else 'none'}")
    L.append("")
    L.append("## Event Horizon\n")
    L.append("| family | RECORDED | REPORTED | DERIVED | ESTIMATED | PROXY |")
    L.append("|---|---|---|---|---|---|")
    for fam, bb in (cal.get("by_family") or {}).items():
        if isinstance(bb, dict):
            L.append(f"| {fam} | {bb.get('RECORDED', 0)} | {bb.get('REPORTED', 0)} | {bb.get('DERIVED', 0)} | {bb.get('ESTIMATED', 0)} | {bb.get('PROXY', 0)} |")
    L.append(f"\nUrgency: {cal.get('by_urgency', {})}  |  helper deadlines by type: {cal.get('helper_by_type', {})}\n")
    L.append("## Top Targets\n")
    ranked = leads[~leads["tier"].isin(["EXCLUDED", "WATCH"]) & ~leads["route"].isin(["partnership_preservation", "lender_counterparty"])] if len(leads) else leads
    n = 0
    secondary_started = False
    for r in ranked.head(int(cfg.get("max_results", 100))).to_dict(orient="records"):
        is_hit = str(r.get("query_hit", "True")).lower() in ("true", "1")
        if qt != "all" and not is_hit and not secondary_started:
            L.append(f"\n### Secondary: no dated {qt.replace('_', ' ')} event, ranked on other families\n")
            secondary_started = True
        n += 1
        L.append(f"### [#{n}] {r['property_name']} — {r['address']}, {r['jurisdiction']}  Tier [{r['tier']}] Score [{r['motivation_score']}] Route [{r['route']}]")
        L.append(f"- Class / Units / Built / Rehab / Owner type: {r['asset_class']} / {r['units']} / {r['year_built'] or '-'} / {r['rehab_year'] or '-'} / {r['owner_type']}")
        L.append(f"- First debt event: {_render_event(r, 'first_debt') or 'none in horizon'}" + (f" ({r['first_debt_source']})" if r.get('first_debt_source') else ""))
        L.append(f"- First regulatory event: {_render_event(r, 'first_reg') or 'none in horizon'}" + (f" ({r['first_reg_source']})" if r.get('first_reg_source') else ""))
        val = f"${float(r['est_value']):,.0f} ({r['value_source']})" if r.get("est_value") not in ("", None) else (r.get("value_source") or "not computed")
        L.append(f"- Capital stack: {r.get('lender_type') or 'lender_type not in public record'}; balance {r['est_loan_balance'] or 'not in public record'} [{r['balance_basis'] or '-'}]; value {val}")
        L.append(f"- Refi screen: LTV {r['est_ltv'] or 'n/a'}; dscr_refi {r['est_dscr_refi'] or 'n/a'}; gap {r['refi_gap_pct'] or 'n/a'}; cushion {r['equity_cushion_pct'] or 'n/a'}")
        L.append(f"- Signals: {r['signals']}")
        L.append(f"- Decision maker: {r['decision_maker_name']}, {r['decision_maker_role']}, grade {r['contact_grade']} — evidence: {r['dm_source'] or 'none yet'}")
        L.append(f"- Outreach: {r['outreach_angle']} via template {r['outreach_template']}; gates: {r['compliance_gates'] or 'dnc_scrub'}")
        L.append(f"- Verify before outreach: {r['verify_before_outreach'] or 'none (all governing dates RECORDED)'}" + (f"; {r['verify_flags']}" if r.get('verify_flags') else ""))
        L.append(f"- Handoffs ready: see handoff/*.json\n")
    L.append("## Partnership Track\n")
    for r in leads[leads["route"] == "partnership_preservation"].head(40).to_dict(orient="records"):
        L.append(f"- {r['property_name']} ({r['owner_type']}; {_any_first_event(r)}) — template {r['outreach_template']}; signals {r['signals']}")
    L.append("\n## Lender-Counterparty Track\n")
    lc = leads[leads["route"] == "lender_counterparty"]
    L.extend([f"- {r['property_name']} ({_any_first_event(r)}) — {r['signals']}" for r in lc.head(40).to_dict(orient="records")] or ["- none"])
    L.append("\n## Pipeline Actions\n")
    L.append("| priority | action | channel | compliance gate | count |\n|---|---|---|---|---|")
    push_open = leads[leads["signals"].str.contains("push_window_open", na=False)] if len(leads) else leads
    if len(push_open):
        L.append(f"| 1 | PuSH first-notice window open now ({', '.join(push_open['property_name'].head(8))}{'...' if len(push_open) > 8 else ''}): file a records request with the OHCS PuSH-CP Program Manager and the affected city for any owner notice; a confirmed notice becomes PRESERVATION_NOTICE_RECEIVED (20 pts) | records request | preservation_law | {len(push_open)} |")
    for t, act in (("A", "Verify governing dates, resolve decision maker to grade A/B, first touch this month"), ("B", "Resolve decision maker; buy recorder images; schedule outreach within 60 days"),
                   ("C", "Monitor; add tapes / images that upgrade PROXY or ESTIMATED dates"), ("WATCH", "Quarterly re-check")):
        sub = leads[leads["tier"] == t]
        if len(sub):
            L.append(f"| {('2' if t == 'A' else '3' if t == 'B' else '4' if t == 'C' else '5')} | Tier {t}: {act} | letter / business line | per card | {len(sub)} |")
    L.append("\n## Data Gaps and Verification Queue\n")
    rej = os.path.join(run_dir, "rejects.csv")
    nrej = len(pd.read_csv(rej)) if os.path.exists(rej) else 0
    L.append(f"- Rejects_Verify rows: {nrej} = rejected {cal.get('rejected', 0)} + verify-flag rows {max(0, nrej - int(cal.get('rejected', 0) or 0))}")
    vf = leads["verify_flags"] if len(leads) else pd.Series(dtype=str)
    L.append(f"- Leads with a conflict / ambiguity flag: {int(vf.str.contains('Verify —', na=False).sum())}; leads with a document request "
             f"(Missing Source — Request Document, e.g. rent roll for the value proxy): {int(vf.str.contains('Missing Source', na=False).sum())}")
    L.append(f"- Sources still verified_live=false: {', '.join(class_unverified) if class_unverified else 'none'}")
    wl = os.path.join(run_dir, "handoff", "sos_worklist.csv")
    dq = os.path.join(run_dir, "handoff", "documents_to_request.csv")
    L.append(f"- SOS worklist: {len(pd.read_csv(wl)) if os.path.exists(wl) else 0} owner entities to resolve (handoff/sos_worklist.csv); documents to request: "
             f"{len(pd.read_csv(dq)) if os.path.exists(dq) else 0} rows (handoff/documents_to_request.csv; recorder image fee from market-params, verify: true)")
    L.append("- Decision makers: every entity owner is `not in public record` until the SOS worklist is resolved (two independent filings for grade A).")
    L.append("\n## Assumptions and Limits\n")
    L.append("- Scoring tables: references/scoring/*.json; basis multipliers RECORDED 1.00 / REPORTED 0.90 / DERIVED 0.80 / ESTIMATED 0.50 / PROXY 0.30.")
    L.append("- Mini-perm maturities derived from Financial_Closing_Date + 15y (17y for 4% bond deals) are PROXY (0.30) and alone cap a lead at Tier C.")
    L.append("- HAP expirations under annual renewal roll forward (confidence 0.70); Year 15 assumes the credit period began in the Compliance_Start year (+1y election possible).")
    L.append("- PuSH notice windows come from OAR 813-115 snippets (ORS 456.260-.265 text not read in this build); confirm before quoting to a counterparty.")
    L.append("- Assessed Value is never used as market value (Oregon Measure 50). Value proxies: ppu_band (units x market $/unit) until rent-limits.json is populated; every market parameter marked verify must be re-pulled before a run that depends on it.")
    path = os.path.join(run_dir, "brief.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    return path


def main(argv=None):
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
    run_dir = os.path.join(cfg.get("out_dir", "runs"), as_of.isoformat())
    os.makedirs(run_dir, exist_ok=True)
    schemas = load_dataset_schemas(pack)
    directory = load_source_directory(pack)
    log: List[str] = []
    manifest: Dict[str, Any] = {"as_of_date": as_of.isoformat(), "market_id": cfg.get("market_id"), "config": cfg, "pack": pack, "omdf_version": OMDF_VERSION,
                                "python": sys.version.split()[0], "stages": {}, "inputs": [],
                                "flags": {"query_type": cfg.get("query_type", "all"), "buyer_profile": cfg.get("buyer_profile", "principal"),
                                          "owner_types_include": cfg.get("owner_types_include"), "owner_types_exclude": cfg.get("owner_types_exclude"),
                                          "lender_types": cfg.get("lender_types"), "price_or_value_band": cfg.get("price_or_value_band"),
                                          "strict_size_fit": bool(cfg.get("strict_size_fit")), "unit_range": cfg.get("unit_range"), "programs": cfg.get("programs")}}
    start = STAGES.index(a.from_stage)
    mode = cfg.get("geography_mode", "metro_core")
    counties = cfg.get("counties")
    hz = str(cfg.get("horizon_years", 5))
    rhz = str(cfg.get("regulatory_horizon_years") or cfg.get("horizon_years", 5))
    prior = a.prior_run or cfg.get("prior_run")
    asset_class = cfg.get("asset_class", "auto")

    # ---- discover
    found = discover(cfg, schemas)
    manifest["inputs"] = found
    print("[discover] " + "; ".join(f"{os.path.basename(f['file'])} -> {f['schema']} (vintage {f['vintage']} from {f['vintage_source']})" for f in found) if found else "[discover] no input files found")
    crosswalk = next((f["file"] for f in found if f["schema"] == "zip_county_crosswalk"), cfg.get("zip_crosswalk"))
    terminated = next((f["file"] for f in found if f["schema"] == "hud_fhasl_terminated"), None)

    adapter_dirs: List[str] = []
    ohcs_leads_path: Optional[str] = None
    if start <= STAGES.index("adapters"):
        ordered = sorted(found, key=lambda f: 0 if f["schema"] == "ohcs_affordable_housing_inventory" else 1)  # OHCS first so the forecast can reuse its ids
        for f in ordered:
            sid = f["schema"]
            if sid not in ADAPTERS:
                if sid not in ("zip_county_crosswalk", "hud_fhasl_terminated"):
                    log.append(f"unprocessed input (no adapter): {f['file']} schema={sid}")
                continue
            script, _src = ADAPTERS[sid]
            od = os.path.join(run_dir, f"adapter_{sid}"); adapter_dirs.append(od)
            cmd = [PY, os.path.join(HERE, script), "--input", f["file"], "--pack", pack, "--out-dir", od, "--as-of", as_of.isoformat(), "--horizon-years", hz]
            if sid == "ohcs_affordable_housing_inventory":
                cmd += ["--mode", mode, "--regulatory-horizon-years", rhz]
                if counties:
                    cmd += ["--counties", ",".join(counties)]
                if cfg.get("target_city"):
                    cmd += ["--city", cfg["target_city"]]
                ohcs_leads_path = os.path.join(od, "leads.csv")
            elif sid in ("hud_fhasl_active", "hud_mf_assistance_sec8"):
                if counties:
                    cmd += ["--counties", ",".join(counties)]
                if crosswalk:
                    cmd += ["--zip-crosswalk", crosswalk]
                if sid == "hud_fhasl_active" and terminated:
                    cmd += ["--terminated", terminated]
            elif sid == "ohcs_push_forecast":
                if counties:
                    cmd += ["--counties", ",".join(counties)]
                if ohcs_leads_path and os.path.exists(ohcs_leads_path):
                    cmd += ["--ohcs-leads", ohcs_leads_path]
                if cfg.get("prior_forecast"):
                    cmd += ["--prior", cfg["prior_forecast"]]
            elif sid == "recorder_index_export":
                if counties:
                    cmd += ["--counties", ",".join(counties)]
                if asset_class in ("sfr_small_res", "market_rate_mf"):
                    cmd += ["--asset-class", asset_class]
            elif sid == "assessor_taxlots":
                if counties and len(counties) == 1:
                    cmd += ["--county-fips", counties[0]]
                if asset_class in ("sfr_small_res", "market_rate_mf"):
                    cmd += ["--asset-class", asset_class]
            run_cmd(cmd, log)
        manifest["stages"]["adapters"] = adapter_dirs
    else:
        adapter_dirs = [os.path.join(run_dir, d) for d in os.listdir(run_dir) if d.startswith("adapter_")]

    if start <= STAGES.index("merge"):
        li = [os.path.join(d, "leads.csv") for d in adapter_dirs if os.path.exists(os.path.join(d, "leads.csv"))]
        ei = [os.path.join(d, "events.csv") for d in adapter_dirs if os.path.exists(os.path.join(d, "events.csv"))]
        if not li:
            print("[merge] nothing to merge: no adapter produced leads (check the inbox and schemas)")
            manifest["stages"]["merge"] = "no inputs"
        else:
            run_cmd([PY, os.path.join(HERE, "merge_leads.py"), "--inputs", *li, "--events", *ei, "--out-dir", run_dir, "--horizon-years", hz,
                     "--regulatory-horizon-years", rhz, "--as-of", as_of.isoformat()], log)
            rej = [pd.read_csv(os.path.join(d, "rejects.csv"), dtype=str, keep_default_na=False) for d in adapter_dirs if os.path.exists(os.path.join(d, "rejects.csv"))]
            pd.concat(rej, ignore_index=True).to_csv(os.path.join(run_dir, "rejects.csv"), index=False) if rej else None
            notes = []
            for d in adapter_dirs:
                p = os.path.join(d, "calendar_summary.json")
                if os.path.exists(p):
                    notes.append(json.load(open(p)).get("degraded_note", ""))
            manifest["stages"]["merge"] = {"adapters": adapter_dirs, "notes": [n for n in notes if n]}

    if start <= STAGES.index("calendar") and os.path.exists(os.path.join(run_dir, "events.csv")):
        run_cmd([PY, os.path.join(HERE, "query_calendar.py"), "--events", os.path.join(run_dir, "events.csv"), "--within-years", hz, "--regulatory-within-years", rhz,
                 "--as-of", as_of.isoformat(), "--json", os.path.join(run_dir, "calendar_summary.json"), "--limit", "15"], log)
        cp = os.path.join(run_dir, "calendar_summary.json")
        cal = json.load(open(cp))
        cal.update({"geography_mode": mode, "counties": counties or [], "horizon_years": cfg.get("horizon_years", 5), "regulatory_horizon_years": rhz,
                    "degraded_note": " ".join((manifest["stages"].get("merge") or {}).get("notes", [])) if isinstance(manifest["stages"].get("merge"), dict) else ""})
        for d in adapter_dirs:
            p = os.path.join(d, "calendar_summary.json")
            if os.path.exists(p):
                sub = json.load(open(p))
                for k in ("rows_in_geography", "rows_excluded_in_development"):
                    if k in sub:
                        cal[k] = cal.get(k, 0) + sub[k]
        json.dump(cal, open(cp, "w"), indent=2)

    if start <= STAGES.index("score") and os.path.exists(os.path.join(run_dir, "leads.csv")):
        cmd = [PY, os.path.join(HERE, "score_leads.py"), "--leads", os.path.join(run_dir, "leads.csv"), "--events", os.path.join(run_dir, "events.csv"),
               "--class", asset_class if asset_class != "all" else "auto", "--horizon-years", hz, "--as-of", as_of.isoformat(),
               "--out", os.path.join(run_dir, "leads_scored.csv"), "--query-type", cfg.get("query_type", "all") or "all",
               "--buyer-profile", cfg.get("buyer_profile", "principal") or "principal"]
        if cfg.get("scoring_dir"):
            cmd += ["--scoring-dir", cfg["scoring_dir"]]
        if cfg.get("unit_range"):
            cmd += ["--unit-range", ",".join(str(x) if x is not None else "" for x in cfg["unit_range"])]
        if cfg.get("price_or_value_band"):
            cmd += ["--price-band", ",".join(str(x) if x is not None else "" for x in cfg["price_or_value_band"])]
        if cfg.get("strict_size_fit"):
            cmd += ["--strict-size-fit"]
        for key, flag in (("programs", "--programs"), ("owner_types_include", "--owner-types-include"), ("owner_types_exclude", "--owner-types-exclude"), ("lender_types", "--lender-types")):
            if cfg.get(key):
                cmd += [flag, ",".join(cfg[key])]
        if a.explain:
            cmd += ["--explain", a.explain]
        run_cmd(cmd, log)

    # ---- sources used: file verified on disk is NOT url verified live
    sources_used = []
    for f in found:
        sid = ADAPTERS.get(f["schema"], (None, f["schema"] or os.path.basename(f["file"])))[1]
        entry = directory.get(sid, {})
        sources_used.append({"source_id": sid, "file": os.path.basename(f["file"]), "sha256": f["sha256"], "vintage": f["vintage"], "vintage_source": f["vintage_source"],
                             "file_verified": "true (file opened; header matched schema)" if f["schema"] else "false (schema not recognized)",
                             "url_verified_live": url_verified(entry) if entry else "false (not in sources.md)",
                             "verified_live": url_verified(entry) if entry else "false (not in sources.md)",
                             "access": entry.get("access", ""), "url": entry.get("url", ""), "note": "a file on disk proves the file, not the live portal"})
    json.dump(sources_used, open(os.path.join(run_dir, "sources_used.json"), "w"), indent=2)
    classes = [asset_class] if asset_class in CLASS_SOURCE_IDS else list(CLASS_SOURCE_IDS)
    class_ids = []
    for c in classes:
        class_ids += [s for s in CLASS_SOURCE_IDS[c] if s not in class_ids]
    class_unverified = [sid for sid in class_ids if sid in directory and not url_verified(directory[sid]).startswith("true")]
    class_unverified += [s["source_id"] for s in sources_used if not str(s["url_verified_live"]).startswith("true") and s["source_id"] not in class_unverified]
    manifest["sources_verified_live_false"] = class_unverified

    if start <= STAGES.index("workbook") and os.path.exists(os.path.join(run_dir, "leads_scored.csv")):
        cmd = [PY, os.path.join(HERE, "build_workbook.py"), "--leads", os.path.join(run_dir, "leads_scored.csv"), "--events", os.path.join(run_dir, "events.csv"),
               "--calendar", os.path.join(run_dir, "calendar_summary.json"), "--rejects", os.path.join(run_dir, "rejects.csv"), "--pack", pack,
               "--sources", os.path.join(run_dir, "sources_used.json"), "--out", os.path.join(run_dir, cfg.get("workbook_name", "targets.xlsx")),
               "--geography-mode", mode, "--as-of", as_of.isoformat(), "--query-type", cfg.get("query_type", "all") or "all", "--buyer-profile", cfg.get("buyer_profile", "principal") or "principal"]
        if prior and os.path.exists(os.path.join(prior, "leads_scored.csv")):
            cmd += ["--prior", os.path.join(prior, "leads_scored.csv")]
        run_cmd(cmd, log)

    if start <= STAGES.index("handoffs") and os.path.exists(os.path.join(run_dir, "leads_scored.csv")):
        cmd = [PY, os.path.join(HERE, "make_handoffs.py"), "--leads", os.path.join(run_dir, "leads_scored.csv"), "--out-dir", os.path.join(run_dir, "handoff"), "--pack", pack]
        for t in cfg.get("handoff_tiers", ["A"]):
            cmd += ["--tier", t]
        run_cmd(cmd, log)

    if start <= STAGES.index("brief") and os.path.exists(os.path.join(run_dir, "leads_scored.csv")):
        bp = write_brief(run_dir, dict(cfg, counties=counties or [], geography_mode=mode), as_of, sources_used, class_unverified)
        print(f"[brief] wrote {bp}")

    if start <= STAGES.index("diff") and prior and os.path.exists(os.path.join(prior, "leads_scored.csv")) and os.path.exists(os.path.join(run_dir, "leads_scored.csv")):
        from build_workbook import diff_frames
        d = diff_frames(pd.read_csv(os.path.join(run_dir, "leads_scored.csv"), dtype=str, keep_default_na=False),
                        pd.read_csv(os.path.join(prior, "leads_scored.csv"), dtype=str, keep_default_na=False))
        d.to_csv(os.path.join(run_dir, "diff.csv"), index=False)
        print(f"[diff] {d['change'].value_counts().to_dict() if len(d) else 'no changes'} -> diff.csv")
        manifest["stages"]["diff"] = d["change"].value_counts().to_dict() if len(d) else {}

    manifest["log"] = log
    manifest["outputs"] = {"run_dir_files": sorted(os.listdir(run_dir)),
                           "handoff_files": sorted(os.listdir(os.path.join(run_dir, "handoff"))) if os.path.isdir(os.path.join(run_dir, "handoff")) else [],
                           "worklists": [p for p in ("handoff/sos_worklist.csv", "handoff/documents_to_request.csv") if os.path.exists(os.path.join(run_dir, p))]}
    json.dump(manifest, open(os.path.join(run_dir, "manifest.json"), "w"), indent=2, default=str)
    print(f"[pipeline] run dir {run_dir}; manifest.json written")


if __name__ == "__main__":
    main()
