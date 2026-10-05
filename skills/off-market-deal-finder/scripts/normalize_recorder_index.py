#!/usr/bin/env python3
"""File-drop adapter: a county recorder-index export -> leads/events for classes 1 and 2 (and recorded instruments on class 3).

TEMPLATE STATUS: no county recorder portal was fetched in this build (verified_live=false). The adapter reads the
canonical column names declared in dataset-schemas.yaml `recorder_index_export` (instrument_no, doc_type,
recording_date, grantor, grantee, plus optional parcel_id / address / zip / county_fips / state / stated_principal /
maturity_date / sale_date / sum_owing / units / reference_instrument_no). Rename an export's columns to these before
dropping it (date_profile.py proposes formats); unknown document types are listed, never guessed.

Document type -> event (schema `doc_type_map`, first match wins):
  NOD_RECORDED (+ DERIVED TRUSTEE_SALE_EARLIEST = NOD + 120 d and CURE_DEADLINE = sale - 5 d, ORS 86.764/.778)
  NOTS_RECORDED (+ DERIVED TRUSTEE_SALE_EARLIEST = NOTS + 90 d and CURE_DEADLINE = sale - 11 d, RCW 61.24.040/.090)
  SUCCESSOR_TRUSTEE_APPOINTED, OFAP_CERT_RECORDED, LIS_PENDENS, MECHANICS_LIEN, TRUSTEES_DEED, NOD_RESCISSION,
  LOAN_MODIFIED, ROFR_RECORDED, HECM_ON_RECORD, DOR_DEFERRAL_LIEN (all RECORDED)
  trust deed / deed of trust  -> LOAN_MATURITY RECORDED when `maturity_date` is given, else ESTIMATED from
                                 recording_date + lender-type term (assets/lender_type_dictionary.csv -> omdf.capital_stack.inferred_maturity)
                                 with window recording + min_term .. recording + max_term; lender_type stored on the lead
  reconveyance                -> REFINANCE_CLOSED + SUPPRESS_UNTIL when a new trust deed on the same property records within
                                 `refinance_window_days` (90); UNENCUMBERED otherwise
Validation: loan range orig < maturity < orig + 45y (else Rejected — Out of Range); sale_date >= NOD + 120 d (OR) or
NOTS + 90 d (WA) else Verify — Conflicting Sources. State from county_fips prefix (41 OR, 53 WA).

Usage:
  python scripts/normalize_recorder_index.py --input <recorder.csv> --pack references/sources/oregon-portland \
      [--counties 41051,41067,41005] [--asset-class auto|sfr_small_res|market_rate_mf] --out-dir runs/x/recorder [--as-of YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from omdf import adapters as A  # noqa: E402
from omdf import dates as D  # noqa: E402
from omdf import geo as G  # noqa: E402
from omdf.capital_stack import inferred_maturity  # noqa: E402
from omdf.entities import archetype, infer_owner_type  # noqa: E402
from omdf.schema import FLAG_ANCHOR, FLAG_CONFLICT, FLAG_REJECTED, clean_numeric, detect_schema, load_dataset_schemas, load_lender_terms  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
INSTRUMENT_CLASSES = {"TRUST_DEED", "RECONVEYANCE"}  # instrument classes converted into events; not event types themselves


def load_lender_dictionary(path: Optional[str]) -> List[Tuple[str, str, str]]:
    """[(token_upper, lender_type, match_type)] from assets/lender_type_dictionary.csv."""
    cands = [path] if path else []
    cands.append(os.path.normpath(os.path.join(HERE, "..", "assets", "lender_type_dictionary.csv")))
    for p in cands:
        if p and os.path.exists(p):
            with open(p, "r", encoding="utf-8") as fh:
                return [(r["token"].upper(), r["lender_type"], r.get("match_type", "contains")) for r in csv.DictReader(fh)]
    return []


def lender_type_for(grantee: str, dictionary: List[Tuple[str, str, str]]) -> str:
    g = (grantee or "").upper()
    for token, lt, mt in dictionary:
        if mt == "word":
            if re.search(r"(?<![A-Z0-9])" + re.escape(token) + r"(?![A-Z0-9])", g):
                return lt
        elif token in g:
            return lt
    return "unknown"


def classify_doc(doc_type: str, doc_map: List[Dict[str, str]]) -> Optional[str]:
    d = (doc_type or "").lower()
    for rule in doc_map:
        if rule.get("contains", "").lower() in d:
            return rule.get("event")
    return None


def run(a) -> Dict[str, Any]:
    as_of = D.parse_as_of(a.as_of)
    schemas = load_dataset_schemas(a.pack)
    spec = schemas.get("recorder_index_export") or {}
    df = A.read_table(a.input)
    sid = detect_schema(list(df.columns), schemas)
    if sid != "recorder_index_export":
        print(f"ERROR: input does not match recorder_index_export (detected {sid}); required columns: {spec.get('match_columns')}; file columns: {list(df.columns)}", file=sys.stderr)
        sys.exit(2)
    doc_map = spec.get("doc_type_map") or []
    dictionary = load_lender_dictionary(os.path.normpath(os.path.join(a.pack, spec.get("lender_dictionary", ""))) if a.pack and spec.get("lender_dictionary") else None)
    lender_terms = load_lender_terms(a.pack)
    refi_days = int(spec.get("refinance_window_days", 90))
    counties = set(c.strip() for c in a.counties.split(",")) if a.counties else None
    vintage = A.file_vintage(a.input)
    source = f"recorder index export {vintage}"
    fmt_rec = (spec.get("dates") or {}).get("recording_date", {}).get("format", "%Y-%m-%d")
    fmt_mat = (spec.get("dates") or {}).get("maturity_date", {}).get("format", "%Y-%m-%d")
    fmt_sale = (spec.get("dates") or {}).get("sale_date", {}).get("format", "%Y-%m-%d")

    # ---- group instruments by property
    rows_by_pid: Dict[str, List[Dict[str, Any]]] = {}
    meta: Dict[str, Dict[str, Any]] = {}
    unknown_types: Dict[str, int] = {}
    n_total = n_geo = 0
    rejects: List[Dict[str, Any]] = []
    for r in df.to_dict(orient="records"):
        n_total += 1
        fips = str(r.get("county_fips") or spec.get("default_county_fips") or "").strip()
        if not fips and r.get("county"):
            fips = G.county_fips_from_name(r.get("county")) or ""
        if counties and fips not in counties:
            continue
        n_geo += 1
        state = str(r.get("state") or G.STATE_BY_FIPS_PREFIX.get(fips[:2], "OR")).upper()
        pid = G.property_id(state, fips, r.get("parcel_id") or None, r.get("address"), r.get("zip"))
        rec = D.parse_value(r.get("recording_date"), fmt_rec)
        if rec.value is None:
            rejects.append({"property_key": pid, "property_id": pid, "column": "recording_date", "raw_value": r.get("recording_date"), "reason": rec.flag or "blank", "flag": rec.flag or FLAG_REJECTED, "alt_dates": ""})
            continue
        klass = classify_doc(str(r.get("doc_type")), doc_map)
        if klass is None:
            unknown_types[str(r.get("doc_type"))] = unknown_types.get(str(r.get("doc_type")), 0) + 1
            continue
        rows_by_pid.setdefault(pid, []).append(dict(r, _rec=rec.value, _klass=klass, _state=state, _fips=fips))
        m = meta.setdefault(pid, {"state": state, "fips": fips, "address": r.get("address") or "", "zip": G.zip5(r.get("zip")), "city": r.get("city") or "",
                                  "parcel_id": r.get("parcel_id") or "", "owner": "", "units": clean_numeric(r.get("units"), True)})
        if klass in ("TRUST_DEED", "NOD_RECORDED", "NOTS_RECORDED") and r.get("grantor"):
            m["owner"] = str(r.get("grantor"))  # the borrower / owner of record on the most recent lien-side instrument
        if m.get("units") is None and clean_numeric(r.get("units"), True) is not None:
            m["units"] = clean_numeric(r.get("units"), True)

    leads, events = [], []
    for pid, docs in rows_by_pid.items():
        docs.sort(key=lambda x: x["_rec"])
        m = meta[pid]
        state = m["state"]
        evs: List[Dict[str, Any]] = []
        tape_flags: List[str] = []
        lender_type = ""
        est_balance = ""
        trust_deeds = [d for d in docs if d["_klass"] == "TRUST_DEED"]
        for d in docs:
            k, rec = d["_klass"], d["_rec"]
            inst = str(d.get("instrument_no") or "")
            if k == "TRUST_DEED":
                lt = lender_type_for(str(d.get("grantee")), dictionary)
                lender_type = lt
                principal = clean_numeric(d.get("stated_principal"), False)
                if principal:
                    est_balance = principal
                mat = D.parse_value(d.get("maturity_date"), fmt_mat) if str(d.get("maturity_date") or "").strip() else None
                if mat and mat.value:
                    flag = "" if rec < mat.value < D.add_years(rec, 45) else FLAG_REJECTED
                    ev = A.make_event(pid, "LOAN_MATURITY", mat.value, "RECORDED", source, as_of, vintage, derivation=f"maturity printed in instrument {inst}",
                                      detail=f"grantee={d.get('grantee')}", verify_flag=flag, lender_type=lt)
                    if flag:
                        ev["status"] = "REJECTED"
                    evs.append(ev)
                elif lt in ("hud_fha", "fannie_dus", "freddie_k_sb", "cmbs", "usda_rd"):
                    # a tape exists for this lender type: never infer, ask for the tape instead (lead-level flag, no dated event)
                    tape_flags.append(f"{FLAG_ANCHOR}: {lt} trust deed {inst} recorded {rec}; pull the tape (FHASL / Ginnie / DUS Disclose / MSIA / EX-102 / USDA exit) for the maturity")
                else:
                    pt, ws, we, basis = inferred_maturity(rec, lt, lender_terms)
                    evs.append(A.make_event(pid, "LOAN_MATURITY", pt, basis, source, as_of, vintage,
                                            derivation=f"recording_date {rec} + typical term for lender_type {lt} (window min..max term; lender-term-assumptions.md)",
                                            window_start=ws.isoformat(), window_end=we.isoformat(), detail=f"grantee={d.get('grantee')}; instrument {inst}", lender_type=lt))
                    if lt == "debt_fund_bridge":
                        cap = D.add_years(rec, 3)
                        evs.append(A.make_event(pid, "RATE_CAP_EXPIRY", cap, "ESTIMATED", source, as_of, vintage, derivation="bridge origination + 3y initial term (+/-12 mo)",
                                                window_start=D.add_months(cap, -12).isoformat(), window_end=D.add_months(cap, 12).isoformat()))
            elif k == "RECONVEYANCE":
                newer = [t for t in trust_deeds if 0 <= (t["_rec"] - rec).days <= refi_days]
                if newer:
                    nlt = lender_type_for(str(newer[0].get("grantee")), dictionary)
                    terms = lender_terms.get(nlt) or lender_terms.get("unknown") or {"min_term": 5}
                    evs.append(A.make_event(pid, "REFINANCE_CLOSED", newer[0]["_rec"], "RECORDED", source, as_of, vintage,
                                            derivation=f"Reconveyance {inst} followed within {refi_days} d by trust deed {newer[0].get('instrument_no')}", detail=f"new lender_type={nlt}"))
                    evs.append(A.make_event(pid, "SUPPRESS_UNTIL", D.add_years(newer[0]["_rec"], int(terms.get("min_term", 5))), "DERIVED", source, as_of, vintage,
                                            derivation=f"new origination + min_term({nlt})"))
                else:
                    evs.append(A.make_event(pid, "UNENCUMBERED", rec, "RECORDED", source, as_of, vintage, derivation=f"Reconveyance {inst} with no new trust deed within {refi_days} d"))
            else:
                ev = A.make_event(pid, k, rec, "RECORDED", source, as_of, vintage, derivation=f"{d.get('doc_type')} instrument {inst}",
                                  detail=f"grantor={d.get('grantor')}; grantee={d.get('grantee')}",
                                  value=clean_numeric(d.get("sum_owing"), False) if d.get("sum_owing") else "")
                evs.append(ev)
                if k in ("NOD_RECORDED", "NOTS_RECORDED"):
                    is_wa = k == "NOTS_RECORDED" or state == "WA"
                    earliest = rec + timedelta(days=90 if is_wa else 120)
                    sale = D.parse_value(d.get("sale_date"), fmt_sale).value if str(d.get("sale_date") or "").strip() else None
                    flag = ""
                    if sale and sale < earliest:
                        flag = FLAG_CONFLICT
                    evs.append(A.make_event(pid, "TRUSTEE_SALE_EARLIEST", sale or earliest, "RECORDED" if sale else "DERIVED", source, as_of, vintage,
                                            derivation=("stated sale date" if sale else ("NOTS + 90 d (RCW 61.24.040; 120 d when a .031 letter applied)" if is_wa else "NOD + 120 d (ORS 86.764)")), verify_flag=flag))
                    cure_days = 11 if is_wa else 5
                    evs.append(A.make_event(pid, "CURE_DEADLINE", (sale or earliest) - timedelta(days=cure_days), "DERIVED", source, as_of, vintage,
                                            derivation=("sale - 11 d (RCW 61.24.090)" if is_wa else "sale - 5 d (ORS 86.778)")))
        evs = [e for e in evs if e]
        units = m.get("units")
        cls = a.asset_class if a.asset_class != "auto" else ("sfr_small_res" if (units or 0) <= 4 else "market_rate_mf")
        owner_type = infer_owner_type(m["owner"], None, None, cls)
        arch = archetype(owner_type)
        hard = [e for e in evs if e["event_family"] == "HARD_DISTRESS"]
        lead = A.blank_lead(property_id=pid, property_name=m["address"] or pid, address=m["address"], city=str(m["city"]).title(), zip=m["zip"], county_fips=m["fips"],
                            county_name=G.COUNTY_NAME_BY_FIPS.get(m["fips"], ""), jurisdiction=str(m["city"]).title(), geo_modes="|".join(G.modes_for_fips(m["fips"], m["city"])),
                            geo_grade="county_field" if m["fips"] else "", asset_class=cls, status="Active", units=units if units is not None else "",
                            owner_name=m["owner"], owner_type=owner_type, owner_archetype=arch["archetype"], decision_maker_name="not in public record",
                            decision_maker_role=arch["decision_maker_role"], dm_source="recorder grantor string; resolve via SOS worklist / trust-deed signatory", contact_grade="C",
                            est_loan_balance=est_balance, balance_basis="ESTIMATED (stated principal, not amortized)" if est_balance else "",
                            signals=";".join(["recorder_index"] + sorted({e["event_type"].lower() for e in hard})),
                            route=arch["route"], outreach_template=arch["template"], outreach_angle=arch["angle"],
                            source_vintages=f"recorder_index={vintage}", as_of_date=as_of.isoformat())
        lead.update({"lender_type": lender_type, "parcel_id": m["parcel_id"], "verify_flags": ";".join(tape_flags)})
        fd, fr, inh = A.first_events(evs, a.horizon_years * 12, a.horizon_years * 12)
        A.apply_first(lead, fd, fr, inh)
        leads.append(lead)
        events.extend(evs)
    summary = {"adapter": "recorder_index_export", "as_of_date": as_of.isoformat(), "input_sha256": A.sha256(a.input), "vintage": vintage,
               "rows_total": n_total, "rows_in_geography": n_geo, "leads": len(leads), "events": len(events), "by_basis": A.basis_breakdown(events),
               "unknown_doc_types": unknown_types, "verified_live": False,
               "note": "canonical column names; no county portal fetched in this build. ESTIMATED maturities carry a lender-type window; buy the image for every Tier A inferred maturity."}
    A.write_outputs(a.out_dir, leads, events, summary)
    import pandas as pd
    pd.DataFrame(rejects, columns=["property_key", "property_id", "column", "raw_value", "reason", "flag", "alt_dates"]).to_csv(os.path.join(a.out_dir, "rejects.csv"), index=False)
    print(f"[recorder] rows {n_total} in_geography {n_geo} leads {len(leads)} events {len(events)} unknown_doc_types {unknown_types}")
    print("[recorder] basis breakdown: " + " / ".join(f"{k} {v}" for k, v in summary["by_basis"].items()))
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", required=True)
    ap.add_argument("--pack", default=None)
    ap.add_argument("--counties", default=None, help="comma list of county FIPS")
    ap.add_argument("--asset-class", default="auto", choices=["auto", "sfr_small_res", "market_rate_mf", "affordable_regulated"])
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--horizon-years", type=float, default=5)
    ap.add_argument("--as-of", default=None)
    run(ap.parse_args(argv))


if __name__ == "__main__":
    main()
