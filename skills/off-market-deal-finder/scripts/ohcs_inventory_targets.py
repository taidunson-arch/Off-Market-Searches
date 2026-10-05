#!/usr/bin/env python3
"""Hardened rewrite of the improvised OHCS target-list script (b.py).

Reads a state HFA affordable-housing inventory (worked example: Oregon OHCS OAHI, Socrata p9yn-ftai),
resolves geography by county FIPS, parses every date column with its DECLARED format, derives dated
events with an explicit basis (REPORTED program ends, DERIVED Year 15, PROXY 15-year mini-perm), and
writes the canonical lead table, the companion events table, rejects, a calendar summary and an
optional unscored workbook. Scoring is a separate step (score_leads.py).

What changed versus b.py and why
--------------------------------
* b.py filtered on `City == 'Portland'` (a string) -- here geography is a county-FIPS mode
  (`county`, `metro_core`, `cbsa`) and `city_limits` is explicitly graded `city_name_weak`.
* b.py guessed day-first only when the first field exceeded 12 -- here each column carries a
  declared format (Financial_Closing_Date is %d/%m/%Y, every other slash column %m/%d/%Y, USDA
  `%Y %b %d %I:%M:%S %p`). `--auto-detect-dates` opts into per-value detection, where
  ambiguous values are flagged `Verify — Ambiguous` and both parses are kept in alt_dates.
* b.py treated program expirations and the mini-perm estimate as one "loan event" -- here every
  event has an event_type, family, basis and confidence, and the mini-perm is labelled PROXY.
* b.py scored with ad-hoc weights -- here no scoring happens; score_leads.py reads references/scoring.

Usage
-----
python scripts/ohcs_inventory_targets.py --input <ohcs.csv> --pack references/sources/oregon-portland \
    --mode metro_core --horizon-years 5 --out-dir runs/ohcs [--as-of 2026-10-04] [--xlsx]

Aliases: --metro == --mode metro_core; --city Portland == --mode city_limits; --county 41051,41067 overrides
the mode's county list. Exit 0 on success, 2 on schema mismatch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import date
from typing import Any, Dict, List, Optional

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from omdf import dates as D  # noqa: E402
from omdf import geo as G  # noqa: E402
from omdf.calendar import basis_counts, header_line, split_helper_rows  # noqa: E402
from omdf.capital_stack import restricted_noi, value_proxy  # noqa: E402
from omdf.entities import archetype, infer_owner_type, normalize_owner_type_field  # noqa: E402
from omdf.schema import (EVENT_COLUMNS, FLAG_CONFLICT, FLAG_MISSING_SOURCE, HELPER_EVENTS, HUD_CONTRACT_TO_PROGRAM,  # noqa: E402
                         LEAD_COLUMNS, PUSH_COVERED_PROGRAMS, REJECT_COLUMNS, apply_numeric_block, clean_numeric,
                         detect_schema, direction_of, family_of, load_dataset_schemas, load_market_params, param)


def _s(v) -> str:
    if v is None:
        return ""
    s = str(v)
    return "" if s.strip().lower() in ("nan", "none", "nat") else s.strip()


def _num(v) -> Optional[float]:
    """Comma- and blank-safe numeric ('2,021' -> 2021.0, '35.0' -> 35.0, '' -> None)."""
    x = clean_numeric(v, as_int=False)
    return None if x is None else float(x)


def _int_or_blank(v):
    x = clean_numeric(v, as_int=True)
    return "" if x is None else x


def _vintage(path: str):
    """(vintage, vintage_source): the YYYYMMDD in the filename when present, else the file mtime."""
    m = re.search(r"(20\d{6})", os.path.basename(path))
    if m:
        return m.group(1), "filename"
    return date.fromtimestamp(os.path.getmtime(path)).isoformat(), "mtime"


def load_rent_limits(pack: Optional[str], spec: Dict[str, Any]) -> Dict[str, Any]:
    """rent-limits.json beside the pack (placeholder ships with nulls; populated by the user from HUD/OHCS limits)."""
    fn = ((spec.get("value_proxy") or {}).get("rent_limits_file")) or "rent-limits.json"
    for d in [pack, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "sources", "oregon-portland"))]:
        if d and os.path.exists(os.path.join(d, fn)):
            with open(os.path.join(d, fn), "r", encoding="utf-8") as fh:
                return json.load(fh)
    return {}


def value_screen(units, ami_units: Dict[str, float], hap_units: float, params: Dict[str, Any], rent_limits: Dict[str, Any]):
    """Return (est_value, value_source, est_noi, noi_source, flag). Restricted income proxy when rent limits are
    populated, else units x pack price_per_unit_avg labelled ppu_band (flag: request the rent roll)."""
    if not units:
        return "", "not computed (units unknown)", "", "not computed", ""
    limits = (rent_limits.get("max_rents_by_ami") or {})
    usable = {k: v for k, v in limits.items() if isinstance(v, (int, float)) and v > 0}
    cap_aff = param(params, "cap_rate_affordable", 0.0675)
    if usable and sum(ami_units.values()) > 0:
        hap_rent = rent_limits.get("hap_contract_rent_default")
        noi = restricted_noi(ami_units, usable, hap_rent if isinstance(hap_rent, (int, float)) else None,
                             vacancy=float(param(params, "vacancy", 0.071)), opex_ratio=float(param(params, "opex_ratio_affordable", 0.50)), hap_units=hap_units)
        val = value_proxy(noi, cap_aff)
        return val, "restricted_income_proxy", round(noi, 0), "benchmark_estimate (HFA rent limits x AMI buckets)", FLAG_MISSING_SOURCE + ": rent roll / T-12"
    ppu = param(params, "price_per_unit_avg", None)
    if not ppu:
        return "", "not computed (no price_per_unit_avg in market-params)", "", "not computed", FLAG_MISSING_SOURCE + ": rent roll"
    return round(float(units) * float(ppu), 0), "ppu_band (market avg $/unit; as-restricted value is usually lower)", "", "not computed (populate rent-limits.json for restricted_income_proxy)", FLAG_MISSING_SOURCE + ": rent roll / HFA rent limits"


def _sha(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_frame(df: pd.DataFrame, spec: Dict[str, Any]) -> pd.DataFrame:
    df = df.copy()
    norm = spec.get("normalize", {}) or {}
    for col, rule in norm.items():
        if col not in df.columns:
            continue
        if rule == "title_case":
            df[col] = df[col].map(lambda v: _s(v).title())
        elif isinstance(rule, dict):
            if rule.get("title_case"):
                df[col] = df[col].map(lambda v: _s(v).title())
            typo = rule.get("typo_map") or {}
            if typo:
                df[col] = df[col].map(lambda v: typo.get(v, v))
            mp = rule.get("map") or {}
            if mp:
                df[col] = df[col].map(lambda v: mp.get(v, v))
            drop = rule.get("drop_values") or []
            if drop:
                df[col] = df[col].map(lambda v: "" if _s(v) in drop else v)
    if "Owner Type" in df.columns:
        df["Owner Type"] = df["Owner Type"].map(normalize_owner_type_field)
    apply_numeric_block(df, spec)
    return df


def run(args) -> Dict[str, Any]:
    as_of = D.parse_as_of(args.as_of)
    schemas = load_dataset_schemas(args.pack)
    raw = pd.read_csv(args.input, dtype=str, encoding="utf-8-sig", keep_default_na=False)
    raw = raw.rename(columns=lambda c: c.strip())
    sid = detect_schema(list(raw.columns), schemas)
    if sid != "ohcs_affordable_housing_inventory":
        print(f"ERROR: input does not match the ohcs_affordable_housing_inventory schema (detected: {sid}). "
              f"Run date_profile.py and add a schema to the pack's dataset-schemas.yaml.", file=sys.stderr)
        sys.exit(2)
    spec = schemas[sid]
    vintage, vintage_source = _vintage(args.input)
    source_tag = f"OHCS OAHI p9yn-ftai {vintage}"
    params = load_market_params(args.pack)
    rent_limits = load_rent_limits(args.pack, spec)
    push_cfg = (spec.get("derived_events") or {}).get("PRESERVATION_NOTICE_WINDOW") or {}
    df = normalize_frame(raw, spec)

    # ---------------------------------------------------------------- geography
    county_map = spec.get("county_fips") or {}
    df["county_fips"] = df["County"].map(lambda c: G.county_fips_from_name(c, county_map))
    mode = args.mode
    counties = [c.strip() for c in args.counties.split(",")] if args.counties else None
    target_city = args.city or "Portland"
    modes = dict(G.PORTLAND_MODES)
    modes["city_limits"] = {"fips": modes["city_limits"]["fips"], "city": target_city, "grade": "city_name_weak"}
    keep_mask, grades = [], []
    for _, r in df.iterrows():
        ok, grade = G.in_mode(r["county_fips"], r["City"], mode, counties, modes)
        keep_mask.append(ok)
        grades.append(grade if ok else "")
    df["geo_grade"] = grades
    geo = df[pd.Series(keep_mask, index=df.index)].copy()
    rows_in_geo = len(geo)
    if mode == "city_limits":
        print(f"WARNING: city_limits mode filters on the normalized City string == '{target_city}'; point-in-polygon "
              f"is not implemented in v2, so every row is graded geo_grade=city_name_weak.", file=sys.stderr)

    excl = (spec.get("filters") or {}).get("exclude") or {}
    n_dev = 0
    for col, vals in excl.items():
        if col in geo.columns:
            m = geo[col].isin(vals)
            n_dev += int(m.sum())
            geo = geo[~m].copy()

    # ---------------------------------------------------------------- dates
    date_specs: Dict[str, Dict[str, Any]] = spec.get("dates", {})
    parsed: Dict[str, pd.Series] = {}
    quality: Dict[str, Dict[Any, str]] = {}
    rejects: List[Dict[str, Any]] = []
    key_cols = spec.get("key") or ["Property Name", "Address"]

    def pkey(r) -> str:
        return " | ".join(_s(r[c]) for c in key_cols if c in r)

    for col, ds in date_specs.items():
        if col not in geo.columns:
            continue
        fmt = ds.get("format")
        if args.auto_detect_dates and isinstance(fmt, str) and fmt.startswith("%") and "/" in fmt:
            fmt = "auto"
        series, rej = D.parse_column(geo[col].replace("", None), fmt, args.date_order)
        parsed[col] = series
        q: Dict[Any, str] = {}
        for _, rr in rej.iterrows():
            idx = rr["index"]
            q[idx] = rr["quality"]
            rejects.append({"property_key": pkey(geo.loc[idx]), "property_id": "", "column": col, "raw_value": rr["raw_value"],
                            "reason": f"{rr['flag']} under declared format {fmt}", "flag": rr["flag"], "alt_dates": rr["alt_dates"]})
        quality[col] = q

    component_cols = [c for c, ds in date_specs.items() if ds.get("event") and c != "LATEST_Expiration_Date" and c in parsed]
    whitelist = set()
    for v in spec.get("validations", []) or []:
        if v.get("rule") == "latest_equals_max_components":
            whitelist = set(v.get("whitelist") or [])

    # ---------------------------------------------------------------- build leads + events
    leads: List[Dict[str, Any]] = []
    events: List[Dict[str, Any]] = []
    horizon_m = int(args.horizon_years * 12)
    reg_horizon_m = int((args.regulatory_horizon_years or args.horizon_years) * 12)
    ev_counter = 0
    seen_pids: Dict[str, int] = {}

    for idx, r in geo.iterrows():
        name = _s(r["Property Name"])
        addr = _s(r["Address"])
        zipc = G.zip5(r.get("Zip Code"))
        state = "OR"
        pid = G.property_id(state, r["county_fips"], None, addr, zipc)
        verify_flags: List[str] = []
        dup_signal = ""
        if pid in seen_pids:  # phases listed at one address (Forest Manor I / II): the inventory key is Name + Address
            seen_pids[pid] += 1
            pid = f"{pid}-{seen_pids[pid]}"
            dup_signal = "duplicate_address_in_inventory"
        else:
            seen_pids[pid] = 1
        lead_events: List[Dict[str, Any]] = []

        def dt(col) -> Optional[date]:
            return parsed[col].loc[idx] if col in parsed else None

        closing = dt("Financial_Closing_Date")
        comp_start = dt("Compliance_Start_Date")
        if closing and comp_start:
            diff_m = D.months_between(closing, comp_start)
            if not (0 <= diff_m <= 36):
                verify_flags.append(f"{FLAG_CONFLICT}: Compliance_Start_Date {comp_start} is {diff_m:+.0f} months from Financial_Closing_Date {closing}")

        programs: List[str] = []
        hud_contract = _s(r.get("HUD Contract"))
        if hud_contract in HUD_CONTRACT_TO_PROGRAM:
            programs.append(HUD_CONTRACT_TO_PROGRAM[hud_contract])

        latest_reported = dt("LATEST_Expiration_Date")
        comps = [dt(c) for c in component_cols]
        latest_max = D.max_date(comps)
        latest_recomputed = False
        if latest_reported is None and latest_max is not None:
            latest_reported = latest_max
            latest_recomputed = True
        elif latest_reported is not None and latest_max is not None and latest_reported != latest_max:
            tag = " (known exception)" if name in whitelist else ""
            verify_flags.append(f"{FLAG_CONFLICT}: LATEST_Expiration_Date {latest_reported} != max(components) {latest_max}{tag}")

        def add_event(etype, d, basis, source, program=None, confidence=None, derivation=None, window_months=0,
                      detail=None, value=None, alt_dates=None, q="declared_format", flag=None):
            nonlocal ev_counter
            if d is None:
                return None
            ev_counter += 1
            mo = D.months_between(as_of, d)
            fam = family_of(etype)
            if fam == "DEBT" and closing and etype == "LOAN_MATURITY" and not (closing < d < D.add_years(closing, 45)):
                flag = "Rejected — Out of Range"
            if fam == "REGULATORY" and comp_start and d < comp_start and flag is None:
                flag = FLAG_CONFLICT
                verify_flags.append(f"{FLAG_CONFLICT}: {etype} {d} precedes Compliance_Start_Date {comp_start}")
            ev = {
                "event_id": f"{pid}:{ev_counter}", "property_id": pid, "event_type": etype, "event_family": fam,
                "direction": direction_of(etype), "event_date": d.isoformat(), "months_out": mo, "urgency_band": D.urgency_band(mo),
                "basis": basis, "confidence": confidence if confidence is not None else 1.0, "source": source, "source_vintage": vintage,
                "derivation": derivation or "", "program": program or "", "detail": detail or "", "value": value if value is not None else "",
                "verify_flag": flag or "", "alt_dates": ";".join(alt_dates or []),
                "window_start": D.add_months(d, -window_months).isoformat() if window_months else "",
                "window_end": D.add_months(d, window_months).isoformat() if window_months else "",
                "status": "REJECTED" if flag == "Rejected — Out of Range" else ("PAST" if mo < 0 else "FUTURE"),
                "event_date_quality": q,
            }
            lead_events.append(ev)
            return ev

        # REPORTED program-end events straight from the inventory columns
        for col, ds in date_specs.items():
            et = ds.get("event")
            if not et or col not in parsed:
                continue
            d = dt(col)
            if col == "LATEST_Expiration_Date":
                if latest_reported is None:
                    continue
                add_event(et, latest_reported, ds.get("basis", "REPORTED"), source_tag,
                          derivation="max of component expiration dates (LATEST blank)" if latest_recomputed else f"{col}",
                          q=quality.get(col, {}).get(idx, "declared_format"), detail="recomputed" if latest_recomputed else "")
                continue
            if d is None:
                continue
            prog = ds.get("program")
            if prog and prog not in programs:
                programs.append(prog)
            if et == "USDA_515_MATURITY" and "USDA_515" not in programs:
                programs.append("USDA_515")
            q = quality.get(col, {}).get(idx, "declared_format")
            flag = "Verify — Ambiguous" if q == "ambiguous" else None
            add_event(et, d, ds.get("basis", "REPORTED"), source_tag, program=prog, confidence=ds.get("confidence"),
                      derivation=col, q=q, flag=flag)
            if et == "HAP_EXPIRATION":
                add_event("HAP_OPTOUT_NOTICE_DEADLINE", D.add_months(d, -12), "DERIVED", source_tag,
                          derivation="HAP_EXPIRATION - 12 months (federal one-year opt-out notice)", detail="federal_1yr_notice")

        # DERIVED and PROXY events
        units_int = clean_numeric(r.get("Total Units"), as_int=True)
        for et, ds in (spec.get("derived_events") or {}).items():
            if et == "PRESERVATION_NOTICE_WINDOW":
                continue  # handled below with its own gating
            src_col = ds.get("from")
            d0 = dt(src_col)
            if d0 is None:
                continue
            years = int(ds.get("add_years", 0))
            for prog, alt_years in (ds.get("add_years_if_program") or {}).items():
                if prog in programs:
                    years = int(alt_years)
            d = D.add_years(d0, years)
            derivation = ds.get("derivation") or f"{src_col} + {years}y"
            if et == "LIHTC_COMPLIANCE_END":
                if not any(p.startswith("LIHTC") for p in programs):
                    # Compliance_Start_Date is populated for non-LIHTC OHCS programs too; a Year-15 event there would be fiction
                    continue
                derivation = f"{src_col} + 15y (Year 15; owner may have elected +15 -> +1y election possible)"
            add_event(et, d, ds.get("basis", "DERIVED"), source_tag, derivation=derivation, window_months=int(ds.get("window_months", 0)),
                      detail="+15_election_possible" if et == "LIHTC_COMPLIANCE_END" else "")

        # Oregon PuSH first-notice window on the latest regulatory end. Gated on ORS 456.250 coverage: 5+ units and a
        # HUD/USDA rent-assistance or OHCS-administered restriction. Windows from OAR 813-115 snippets (statute text
        # not read in this build): first notice expiration - 36..30 months.
        push_window_open = False
        push_ok = (latest_reported is not None and (units_int or 0) >= int(push_cfg.get("min_units", 5))
                   and bool(set(programs) & PUSH_COVERED_PROGRAMS))
        if push_ok:
            w0, w1 = (push_cfg.get("window_months_before") or [36, 30])
            ws, we = D.add_months(latest_reported, -int(w0)), D.add_months(latest_reported, -int(w1))
            add_event("PRESERVATION_NOTICE_WINDOW", ws, "DERIVED", source_tag,
                      derivation=push_cfg.get("derivation") or "REGULATORY_LATEST_END - 36..30 months (OAR 813-115 first notice; statute text unverified)",
                      detail="oregon_push_first_notice" + ("; window_open_now" if ws <= as_of <= we else ""), window_months=0)
            lead_events[-1]["window_start"] = ws.isoformat()
            lead_events[-1]["window_end"] = we.isoformat()
            push_window_open = ws <= as_of <= we

        active = [e for e in lead_events if e["status"] != "REJECTED"]
        debt = [e for e in active if e["event_family"] == "DEBT" and e["direction"] == "PRESSURE" and 0 <= e["months_out"] <= horizon_m
                and (args.include_proxies or e["basis"] != "PROXY")]
        reg = [e for e in active if e["event_family"] == "REGULATORY" and e["direction"] == "PRESSURE" and e["event_type"] not in HELPER_EVENTS
               and 0 <= e["months_out"] <= reg_horizon_m]
        if not debt and not reg:
            continue
        first_debt = min(debt, key=lambda e: e["event_date"]) if debt else None
        first_reg = min(reg, key=lambda e: e["event_date"]) if reg else None
        in_h = sorted([e for e in active if e["direction"] == "PRESSURE" and 0 <= e["months_out"] <= max(horizon_m, reg_horizon_m)], key=lambda e: e["event_date"])

        owner_name = _s(r.get("Owner Name"))
        owner_type = infer_owner_type(owner_name, r.get("Owner Type"), r.get("Developer Name"), "affordable_regulated")
        arch = archetype(owner_type)
        ami_buckets = {b: (_num(r.get(f"Total_{b}_AMI_Units")) or 0) for b in ("30", "40", "50", "60", "80")}
        ami_30_60 = sum(ami_buckets[b] for b in ("30", "40", "50", "60"))
        ra_units = _num(r.get("Rental_Assistance_Count")) or 0
        est_value, value_source, est_noi, noi_source, value_flag = value_screen(units_int, ami_buckets, ra_units, params, rent_limits)
        if value_flag and value_flag not in verify_flags:
            verify_flags.append(value_flag)
        lat, lon = G.parse_wkt_point(r.get("Geocode"))
        signals = ["hfa_inventory"] + ([dup_signal] if dup_signal else [])
        if push_window_open:
            signals.append("push_window_open")
        if hud_contract:
            signals.append("hud_contract:" + HUD_CONTRACT_TO_PROGRAM.get(hud_contract, hud_contract))
        if latest_recomputed:
            signals.append("latest_recomputed")
        for e in in_h:
            if e["verify_flag"] and e["verify_flag"] not in verify_flags:
                verify_flags.append(f"{e['verify_flag']} on {e['event_type']} {e['event_date']}")

        lead = {c: "" for c in LEAD_COLUMNS}
        lead.update({
            "property_id": pid, "property_name": name, "address": addr, "city": _s(r.get("City")), "zip": zipc,
            "county_fips": r["county_fips"] or "", "county_name": _s(r.get("County")), "jurisdiction": _s(r.get("City")),
            "geo_modes": "|".join(G.modes_for_fips(r["county_fips"], r.get("City"), modes)), "geo_grade": r["geo_grade"],
            "lat": lat if lat is not None else "", "lon": lon if lon is not None else "", "asset_class": "affordable_regulated",
            "status": _s(r.get("Status")), "units": units_int if units_int is not None else "", "year_built": _int_or_blank(r.get("Year Built")),
            "rehab_year": _int_or_blank(r.get("Rehab Year")), "property_type": _s(r.get("Property Type")), "programs": ";".join(programs),
            "hud_contract": hud_contract, "ami_30_60_units": int(ami_30_60), "ami_80_units": int(ami_buckets["80"]),
            "market_rate_units": int(_num(r.get("Market_Rate_Units")) or 0), "rental_assistance_units": int(ra_units),
            "owner_name": owner_name, "owner_type": owner_type, "owner_archetype": arch["archetype"],
            "developer_name": _s(r.get("Developer Name")), "manager_name": _s(r.get("Management Name")),
            "decision_maker_name": "not in public record", "decision_maker_role": arch["decision_maker_role"],
            "dm_source": "pending SOS registry resolution", "contact_grade": "C",
            "first_debt_event_type": first_debt["event_type"] if first_debt else "", "first_debt_event_date": first_debt["event_date"] if first_debt else "",
            "first_debt_months_out": first_debt["months_out"] if first_debt else "", "first_debt_basis": first_debt["basis"] if first_debt else "",
            "first_debt_source": first_debt["source"] if first_debt else "",
            "first_reg_event_type": first_reg["event_type"] if first_reg else "", "first_reg_event_date": first_reg["event_date"] if first_reg else "",
            "first_reg_months_out": first_reg["months_out"] if first_reg else "", "first_reg_basis": first_reg["basis"] if first_reg else "",
            "first_reg_source": first_reg["source"] if first_reg else "",
            "events_in_horizon": json.dumps([{k: e[k] for k in ("event_type", "event_date", "months_out", "basis", "confidence", "source",
                                                                  "verify_flag", "alt_dates", "window_start", "window_end", "direction")} for e in in_h]),
            "est_value": est_value, "value_source": value_source, "est_noi": est_noi, "noi_source": noi_source,
            "est_loan_balance": "", "balance_basis": "", "assumable_debt": "", "signals": ";".join(signals), "verify_flags": ";".join(verify_flags),
            "route": arch["route"], "outreach_template": arch["template"], "outreach_angle": arch["angle"],
            "source_vintages": f"ohcs_oahi={vintage}", "as_of_date": as_of.isoformat(),
        })
        leads.append(lead)
        for e in lead_events:
            events.append(e)
        for vf in [v for v in verify_flags if v.startswith(FLAG_CONFLICT)]:  # lead-level conflicts are visible in Rejects_Verify but never drop the lead
            rejects.append({"property_key": pkey(r), "property_id": pid, "column": "LATEST_Expiration_Date" if "LATEST" in vf else "Compliance_Start_Date",
                            "raw_value": "", "reason": vf, "flag": FLAG_CONFLICT, "alt_dates": ""})
        for rj in rejects:
            if rj["property_key"] == pkey(r) and not rj["property_id"]:
                rj["property_id"] = pid

    leads_df = pd.DataFrame(leads, columns=LEAD_COLUMNS)
    events_df = pd.DataFrame(events, columns=EVENT_COLUMNS)
    rejects_df = pd.DataFrame(rejects, columns=REJECT_COLUMNS)

    # ---------------------------------------------------------------- calendar summary
    active = events_df[events_df["status"] != "REJECTED"] if len(events_df) else events_df
    core, helper = split_helper_rows(active) if len(active) else (active, active)
    by_basis = basis_counts(core)
    by_family = {f: int((core["event_family"] == f).sum()) for f in sorted(core["event_family"].unique())} if len(core) else {}
    by_type = active.groupby("event_type").size().to_dict() if len(active) else {}
    calendar = {
        "as_of_date": as_of.isoformat(), "source": source_tag, "input_sha256": _sha(args.input), "vintage": vintage, "vintage_source": vintage_source,
        "geography_mode": mode,
        "counties": counties or list(modes[mode]["fips"]), "target_city": target_city if mode == "city_limits" else "",
        "horizon_years": args.horizon_years, "regulatory_horizon_years": args.regulatory_horizon_years or args.horizon_years,
        "rows_total": int(len(raw)), "rows_in_geography": rows_in_geo, "rows_excluded_in_development": n_dev,
        "leads": int(len(leads_df)), "events": int(len(core)), "events_all": int(len(active)), "helper_events": int(len(helper)),
        "helper_by_type": {k: int(v) for k, v in (helper.groupby("event_type").size().to_dict().items() if len(helper) else [])},
        "push_window_open_count": int(leads_df["signals"].str.contains("push_window_open").sum()) if len(leads_df) else 0,
        "by_basis": by_basis, "by_family": by_family,
        "by_event_type": {k: int(v) for k, v in by_type.items()}, "suppressed": 0,
        "rejected": int((events_df["status"] == "REJECTED").sum()) + int((rejects_df["flag"] == "Rejected — Out of Range").sum()) if len(events_df) else len(rejects_df),
        "verify_flags": int(leads_df["verify_flags"].astype(bool).sum()) if len(leads_df) else 0,
        "date_mode": "auto-detect" if args.auto_detect_dates else "declared formats",
        "degraded_note": "Inventory-only run: every date is REPORTED (program ends), DERIVED (Year 15) or PROXY (mini-perm); no RECORDED debt. "
                         "Tier A needs RECORDED or declared-intent families: HUD FHASL Active, HUD MF Assistance & Sec 8, the OHCS 10-Year Forecast "
                         "(normalize_ohcs_forecast.py, field names unverified) or recorder images in the inbox.",
    }
    calendar["header"] = header_line(calendar)

    os.makedirs(args.out_dir, exist_ok=True)
    leads_df.to_csv(os.path.join(args.out_dir, "leads.csv"), index=False)
    events_df.to_csv(os.path.join(args.out_dir, "events.csv"), index=False)
    rejects_df.to_csv(os.path.join(args.out_dir, "rejects.csv"), index=False)
    with open(os.path.join(args.out_dir, "calendar_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(calendar, fh, indent=2)
    with open(os.path.join(args.out_dir, "leads.json"), "w", encoding="utf-8") as fh:
        recs = leads_df.to_dict(orient="records")
        for rec in recs:
            try:
                rec["events_in_horizon"] = json.loads(rec["events_in_horizon"]) if rec.get("events_in_horizon") else []
            except Exception:
                pass
        json.dump({"run": calendar, "leads": recs}, fh, indent=2, default=str)
    if args.xlsx:
        from omdf.workbook import build_workbook
        params = load_market_params(args.pack)
        build_workbook(os.path.join(args.out_dir, "ohcs_targets_unscored.xlsx"), leads_df, active, calendar, rejects_df, params,
                       [{"source_id": "ohcs_oahi_p9yn-ftai", "file": os.path.basename(args.input), "sha256": calendar["input_sha256"],
                         "vintage": vintage, "vintage_source": vintage_source, "file_verified": "true (file opened and profiled)",
                         "url_verified_live": "false (data.oregon.gov not fetched in this build)", "verified_live": "false", "access": "free-public",
                         "url": "https://data.oregon.gov/d/p9yn-ftai"}],
                       run_meta={"as_of_date": as_of.isoformat(), "geography_mode": mode, "counties": calendar["counties"],
                                 "asset_class": "affordable_regulated", "horizon_years": args.horizon_years,
                                 "regulatory_horizon_years": calendar["regulatory_horizon_years"], "degraded_note": calendar["degraded_note"]})

    print(f"[ohcs] mode={mode} counties={calendar['counties']} rows_total={len(raw)} rows_in_geography={rows_in_geo} "
          f"in_development_excluded={n_dev} leads={len(leads_df)} events={len(core)} (+{len(helper)} helper deadlines) vintage={vintage} ({vintage_source})")
    print(f"[ohcs] basis breakdown: {calendar['header']}")
    print(f"[ohcs] push_window_open now: {calendar['push_window_open_count']} properties; value proxy: ppu_band unless rent-limits.json is populated")
    print(f"[ohcs] wrote {args.out_dir}/leads.csv, events.csv, rejects.csv, calendar_summary.json, leads.json" + (", ohcs_targets_unscored.xlsx" if args.xlsx else ""))
    return calendar


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", required=True, help="state HFA inventory CSV (OHCS OAHI)")
    ap.add_argument("--pack", default=None, help="jurisdiction pack dir with dataset-schemas.yaml (default: embedded Oregon schema)")
    ap.add_argument("--mode", default="metro_core", choices=["city_limits", "county", "metro_core", "cbsa"], help="geography_mode")
    ap.add_argument("--metro", action="store_true", help="alias for --mode metro_core")
    ap.add_argument("--city", default=None, help="target city for city_limits mode (sets --mode city_limits); default Portland")
    ap.add_argument("--county", "--counties", dest="counties", default=None, help="comma list of county FIPS overriding the mode")
    ap.add_argument("--horizon-years", type=float, default=5, help="debt-event horizon in years (default 5)")
    ap.add_argument("--regulatory-horizon-years", type=float, default=None, help="regulatory-event horizon (default = --horizon-years)")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--as-of", default=None, help="YYYY-MM-DD (default: today)")
    ap.add_argument("--include-proxies", default="true", choices=["true", "false"], help="let PROXY mini-perm maturities qualify a lead")
    ap.add_argument("--xlsx", action="store_true", help="also write an unscored workbook")
    ap.add_argument("--auto-detect-dates", action="store_true", help="per-value day/month detection instead of declared formats (flags ambiguous values)")
    ap.add_argument("--date-order", default="month_first", choices=["month_first", "day_first"], help="point estimate for ambiguous values under --auto-detect-dates")
    a = ap.parse_args(argv)
    if a.metro:
        a.mode = "metro_core"
    if a.city:
        a.mode = "city_limits"
    a.include_proxies = a.include_proxies == "true"
    run(a)


if __name__ == "__main__":
    main()
