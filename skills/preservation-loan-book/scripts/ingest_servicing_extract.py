#!/usr/bin/env python3
"""Adapter for the agency's own servicing / grant / owned-asset ledger (schema id `agency_servicing_extract`).

The agency's ledger is the primary tape and the only RECORDED source for its own maturities, affordability periods, recapture
terms, covenant status, notice log and QC log (references/servicing-extract.md). Every book row becomes a lead with
universe = our_book and in_inventory = false until build_universe.py joins it to the inventory.

Schema detection honors `match_columns` + `match_any` groups; per-row validation by `book_kind`:
  loan -> agency_loan_id + upb + maturity;  grant -> grant_id + (affordability_end | recapture_end)
  owned_asset -> asset_id + units_assisted + (affordability_end | contract_expiration);  administered_contract -> contract_id + contract_expiration + units_assisted
Exit 2 names the failing rule when the header does not match or every row fails; failing rows otherwise go to rejects.csv.

Events (basis from the `basis` column, default RECORDED, source `agency_servicing`, detail `<id_kind>=<id>`, event_id includes the id):
  maturity -> AGENCY_LOAN_MATURITY; affordability_end -> AFFORDABILITY_PERIOD_END (program carried); contract_expiration -> HAP_EXPIRATION (PBV/HAP, 0.90);
  recapture_end -> GRANT_RECAPTURE_END; covenant_status=default -> COVENANT_DEFAULT; shared_appreciation_pct>0 & maturity -> SHARED_APPRECIATION_DUE;
  qc_request_(complete_)date & qc_waived!=true -> QC_ELIGIBILITY requested + QC_RESPONSE_DUE; qc_waived=true -> QC_REQUEST_INELIGIBLE;
  third_party_offer_mailed_date -> THIRD_PARTY_OFFER_RECEIVED + ROFR_MATCH_DEADLINE; notice_log_status=received -> PRESERVATION_NOTICE_RECEIVED + RECORDS_REQUEST_DUE;
  usda_prepay_request_date -> USDA_PREPAY_REQUEST_RECEIVED + USDA_PUBLIC_BODY_OFFER_WINDOW_END; rad_chap_date -> RAD_CHAP; section_18_application_date -> SECTION_18_APPLICATION;
  open_findings_count>0 | last_8823_date -> NONCOMPLIANCE_FINDING; last_reac_score -> REAC_SCORE (RECORDED); last_inspection_date -> INSPECTION_DUE; senior_maturity -> LOAN_MATURITY (REPORTED)

Usage:
  python scripts/ingest_servicing_extract.py --input <csv|xlsx> [--sheet S] --pack <dir> --agency-profile hfa [--crosswalk book_crosswalk.csv]
      [--zip-crosswalk <csv>] --out-dir <dir> [--horizon-years 10] [--as-of YYYY-MM-DD] [--internal]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plb import adapters as A  # noqa: E402
from plb import dates as D  # noqa: E402
from plb import geo as G  # noqa: E402
from plb.agency_calendar import deadlines_from_servicing_row  # noqa: E402
from plb.entities import archetype, infer_owner_type, is_self_owned  # noqa: E402
from plb.schema import (BOOK_KINDS, FLAG_ANCHOR, FLAG_MAILING_DATE, FLAG_REJECTED, REJECT_COLUMNS, SERVICING_ENUMS, SERVICING_NUMERIC_COLUMNS,  # noqa: E402
                        SERVICING_REQUIRED_BY_KIND, agency_profile, clean_numeric, detect_schema, load_dataset_schemas, load_market_params)

SOURCE = "agency_servicing"


def _s(v) -> str:
    if v is None:
        return ""
    s = str(v)
    return "" if s.strip().lower() in ("nan", "none", "nat") else s.strip()


def _num(v) -> Optional[float]:
    x = clean_numeric(v, as_int=False)
    return None if x is None else float(x)


def validate_row(r: Dict[str, Any], dates: Dict[str, Optional[D.date]]) -> Optional[str]:
    """Return the failing rule for a row, else None."""
    kind = _s(r.get("book_kind")).lower()
    if kind not in BOOK_KINDS:
        return f"book_kind '{kind}' not in {BOOK_KINDS}"
    for req in SERVICING_REQUIRED_BY_KIND[kind]:
        if isinstance(req, tuple):
            if not any(dates.get(c) if c in dates else _s(r.get(c)) for c in req):
                return f"{kind} requires one of {list(req)}"
        else:
            val = dates.get(req) if req in dates else (_num(r.get(req)) if req in ("upb", "units_assisted") else _s(r.get(req)))
            if val in (None, ""):
                return f"{kind} requires {req}"
    for col, allowed in SERVICING_ENUMS.items():
        v = _s(r.get(col))
        if v and v.lower() not in [str(a).lower() for a in allowed]:
            return f"{col} value '{v}' not in enum"
    return None


def run(a) -> Dict[str, Any]:
    as_of = D.parse_as_of(a.as_of)
    schemas = load_dataset_schemas(a.pack)
    params = load_market_params(a.pack)
    prof = agency_profile(a.agency_profile, a.pack)
    df = A.read_table(a.input, a.sheet)
    sid = detect_schema(list(df.columns), schemas)
    if sid != "agency_servicing_extract":
        spec = schemas.get("agency_servicing_extract", {})
        print(f"ERROR agency_servicing_extract: header does not match (detected: {sid}). Required columns {spec.get('match_columns')} plus one of each group "
              f"{spec.get('match_any')}; file columns: {list(df.columns)}", file=sys.stderr)
        sys.exit(2)
    spec = schemas[sid]
    date_specs = spec.get("dates") or {}
    vintage = A.file_vintage(a.input)
    resolve = A.county_resolver(a.zip_crosswalk)
    hz = a.horizon_years * 12
    leads: List[Dict[str, Any]] = []
    events: List[Dict[str, Any]] = []
    rejects: List[Dict[str, Any]] = []
    n_total = n_ok = 0
    for r in df.to_dict(orient="records"):
        n_total += 1
        dates: Dict[str, Optional[D.date]] = {}
        row_rejects = []
        for col, ds in date_specs.items():
            if col in r and _s(r.get(col)):
                p = D.parse_value(r[col], ds.get("format", "iso"))
                dates[col] = p.value
                if p.flag:
                    row_rejects.append({"column": col, "raw_value": r[col], "reason": f"{p.flag} under declared format {ds.get('format', 'iso')}", "flag": p.flag})
            else:
                dates[col] = None
        why = validate_row(r, dates)
        key = " | ".join(_s(r.get(c)) for c in ("book_kind", "agency_loan_id", "grant_id", "asset_id", "contract_id", "property_name") if _s(r.get(c)))
        if why:
            rejects.append({"property_key": key, "property_id": "", "column": "row", "raw_value": "", "reason": why, "flag": FLAG_REJECTED, "alt_dates": ""})
            continue
        n_ok += 1
        kind = _s(r.get("book_kind")).lower()
        name, addr, city, zipc = _s(r.get("property_name")), _s(r.get("address")), _s(r.get("city")), G.zip5(r.get("zip"))
        fips = _s(r.get("county_fips"))
        grade = "county_field" if fips else ""
        if not fips:
            fips, grade, _ = resolve(zipc, None, "OR")
            fips = fips or ""
        pid = _s(r.get("property_id")) or G.property_id("OR", fips or None, None, addr, zipc)
        if not addr and not _s(r.get("property_id")):
            pid = G.property_id("OR", None, None, f"{name} {city}", zipc)
        ids = {k: _s(r.get(k)) for k in ("agency_loan_id", "grant_id", "asset_id", "contract_id")}
        id_kind = {"loan": "agency_loan_id", "grant": "grant_id", "owned_asset": "asset_id", "administered_contract": "contract_id"}[kind]
        idtag = f"{id_kind}={ids[id_kind]}"
        basis = _s(r.get("basis")).upper() or "RECORDED"
        program = _s(r.get("program"))
        for rj in row_rejects:
            rejects.append({"property_key": key, "property_id": pid, **rj, "alt_dates": ""})
        units_assisted = _num(r.get("units_assisted"))
        evs: List[Dict[str, Any]] = []

        def mk(et, d, b=None, **kw):
            if d is None:
                return None
            e = A.make_event(pid, et, d, b or basis, SOURCE, as_of, vintage, event_id=f"{pid}:{et}:{ids[id_kind] or kind}:{d.isoformat()}", **kw)
            if e:
                e["detail"] = (kw.get("detail") + "; " if kw.get("detail") else "") + idtag if "detail" in kw else idtag
                evs.append(e)
            return e

        if kind == "loan":
            mk("AGENCY_LOAN_MATURITY", dates.get("maturity"), derivation="servicing extract maturity (our note)", program=program)
            if (_num(r.get("shared_appreciation_pct")) or 0) > 0:
                mk("SHARED_APPRECIATION_DUE", dates.get("maturity"), derivation="shared appreciation due at our maturity", program=program)
        if dates.get("affordability_end"):
            mk("AFFORDABILITY_PERIOD_END", dates["affordability_end"], derivation=f"servicing extract affordability_end ({program or 'program unknown'})", program=program)
        if kind == "administered_contract" and dates.get("contract_expiration"):
            mk("HAP_EXPIRATION", dates["contract_expiration"], confidence=0.90, program=program if program in ("PBV", "HAP", "RAC", "PRAC", "PAC") else "PBV",
               derivation="administered contract expiration (agency PBV / HAP contract)", detail="agency_contract")
        if kind == "owned_asset" and dates.get("contract_expiration"):
            mk("HAP_EXPIRATION", dates["contract_expiration"], confidence=0.90, program=program if program in ("PBV", "HAP", "RAC", "PRAC", "PAC") else "PBV",
               derivation="owned asset contract expiration", detail="owned_asset_contract")
        if dates.get("recapture_end"):
            mk("GRANT_RECAPTURE_END", dates["recapture_end"], derivation="servicing extract recapture_end", program=program)
        cov = _s(r.get("covenant_status")).lower()
        if cov == "default":
            mk("COVENANT_DEFAULT", as_of, derivation="covenant_status = default (dated as of run; non-decaying while open)", program=program)
        qc_waived = _s(r.get("qc_waived")).lower()
        qd = dates.get("qc_request_complete_date") or dates.get("qc_request_date")
        if qd:
            if qc_waived == "true":
                mk("QC_REQUEST_INELIGIBLE", qd, derivation="QC request on an allocation that waived the qualified contract", detail="qc_waived")
            else:
                e = mk("QC_ELIGIBILITY", qd, derivation="qualified-contract request logged by the agency", detail="requested", status="requested")
                if e and not dates.get("qc_request_complete_date"):
                    e["verify_flag"] = FLAG_ANCHOR
        md, rd = dates.get("third_party_offer_mailed_date"), dates.get("third_party_offer_received_date")
        if md or rd:
            e = mk("THIRD_PARTY_OFFER_RECEIVED", md or rd, derivation="owner mailed a third-party offer (ORS 456.263 match clock)", detail="mailed" if md else "received_only")
            if e and not md:
                e["verify_flag"] = FLAG_MAILING_DATE
        if _s(r.get("notice_log_status")).lower() == "received":
            nd = dates.get("notice_received_date")
            e = mk("PRESERVATION_NOTICE_RECEIVED", nd or as_of, derivation="agency notice log (PuSH-CP / received-notice file)", detail=_s(r.get("notice_detail")) or "push_first")
            if e and not nd:
                e["verify_flag"] = FLAG_ANCHOR
        if dates.get("usda_prepay_request_date"):
            mk("USDA_PREPAY_REQUEST_RECEIVED", dates["usda_prepay_request_date"], derivation="RD prepayment request (7 CFR 3560.653)")
        if dates.get("rad_chap_date"):
            mk("RAD_CHAP", dates["rad_chap_date"], derivation="RAD CHAP issued")
        if dates.get("section_18_application_date"):
            mk("SECTION_18_APPLICATION", dates["section_18_application_date"], derivation="Section 18 application (24 CFR 970)")
        findings = _num(r.get("open_findings_count")) or 0
        if findings > 0 or dates.get("last_8823_date"):
            mk("NONCOMPLIANCE_FINDING", dates.get("last_8823_date") or as_of, derivation="agency compliance file", detail="8823_filed" if dates.get("last_8823_date") else "open_finding",
               value=int(findings) if findings else "")
        if _num(r.get("last_reac_score")) is not None:
            mk("REAC_SCORE", dates.get("last_reac_date") or as_of, derivation="agency file REAC / NSPIRE score", value=int(_num(r.get("last_reac_score"))), detail="agency_file")
        if dates.get("senior_maturity"):
            mk("LOAN_MATURITY", dates["senior_maturity"], "REPORTED", derivation="senior lien maturity from the servicing extract", detail=f"lender_type={_s(r.get('senior_lien_type')) or 'unknown'}",
               program="HUD_INSURED" if _s(r.get("senior_lien_type")) == "hud_fha" else "")
        # agency deadlines from ledger columns
        evs.extend(deadlines_from_servicing_row(pid, r, as_of, params, units_assisted, [program] if program else []))
        for event in evs:
            event["instrument_id"] = f"{kind}:{ids[id_kind]}"
            event["event_id"] = f"{kind}:{ids[id_kind]}:{event['event_id']}"

        owner = _s(r.get("owner_name"))
        self_owned = kind == "owned_asset" or is_self_owned(owner, prof.get("self_owner_tokens"), None)
        owner_type = "self_owned" if self_owned else (infer_owner_type(owner, None, None) if owner else "unknown")
        arch = archetype(owner_type)
        lead = A.blank_lead(
            property_id=pid, property_name=name, address=addr, city=city.title() if city else "", zip=zipc, county_fips=fips, county_name=G.COUNTY_NAME_BY_FIPS.get(fips, ""),
            jurisdiction=city.title() if city else "", geo_modes="|".join(G.modes_for_fips(fips, city)) if fips else "", geo_grade=grade,
            asset_class="affordable_regulated", status="Active", units=int(units_assisted) if units_assisted is not None and kind in ("owned_asset", "administered_contract") else "",
            programs=program, owner_name=owner, owner_type=owner_type, owner_archetype=arch["archetype"], sponsor_contact_role=arch["decision_maker_role"],
            org_resolution_grade="B" if owner else "C", universe="our_book", in_inventory=False, book_match="self_owned" if self_owned else "matched", book_join_grade="",
            book_kind=kind, agency_loan_ids=ids["agency_loan_id"], grant_ids=ids["grant_id"], asset_ids=ids["asset_id"], contract_ids=ids["contract_id"], agency_programs=program,
            public_upb=_num(r.get("upb")) if _num(r.get("upb")) is not None else "", our_rate=_num(r.get("rate")) if _num(r.get("rate")) is not None else "",
            payment_type=_s(r.get("payment_type")), our_maturity=D.iso(dates.get("maturity")), our_maturity_basis=basis if dates.get("maturity") else "",
            affordability_end=D.iso(dates.get("affordability_end")), recapture_type=_s(r.get("recapture_type")),
            recapture_method=_s(r.get("recapture_method")) or (prof.get("recapture_methods") or {}).get(program, (prof.get("recapture_methods") or {}).get("default", "")) if _s(r.get("recapture_type")) not in ("", "none") else _s(r.get("recapture_method")),
            recapture_amount=_num(r.get("recapture_amount")) if _num(r.get("recapture_amount")) is not None else "", covenant_status=cov,
            senior_lien_type=_s(r.get("senior_lien_type")), senior_maturity=D.iso(dates.get("senior_maturity")), senior_maturity_basis="REPORTED" if dates.get("senior_maturity") else "",
            senior_upb=_num(r.get("senior_upb")) if _num(r.get("senior_upb")) is not None else "", am_officer=_s(r.get("am_officer")),
            notice_status=_s(r.get("notice_log_status")).lower() or "unknown", tenant_notice_status=_s(r.get("tenant_notice_status")).lower(),
            hap_renewal_request_status=_s(r.get("hap_renewal_request_status")).lower() or "", hap_renewal_option=_s(r.get("hap_renewal_option")).lower(),
            recap_status=_s(r.get("recap_status")).lower() or "none", qc_status="requested" if qd and qc_waived != "true" else ("ineligible_waived" if qd else ""),
            qc_waived=qc_waived, rofr_recorded=_s(r.get("rofr_recorded")).lower() or "", apps_flag=_s(r.get("apps_flag")).lower() or "",
            notice_address=_s(r.get("notice_address")), notice_address_source=_s(r.get("notice_address_source")) or ("loan_docs" if _s(r.get("notice_address")) else "unknown"),
            signals=";".join([s for s in ["agency_servicing", f"book_kind:{kind}", "covenant_watch" if cov == "watch" else "", "self_owned" if self_owned else ""] if s]),
            source_vintages=f"agency_servicing_extract={vintage}", as_of_date=as_of.isoformat(), pii_scope="internal" if a.internal else "organization",
        )
        lead.update({"units_assisted": int(units_assisted) if units_assisted is not None else "", "ohcs_property_key": _s(r.get("ohcs_property_key")),
                     "parcel_id": _s(r.get("parcel_id")), "recapture_start": D.iso(dates.get("recapture_start")), "recapture_end": D.iso(dates.get("recapture_end")),
                     "records_request_date": D.iso(dates.get("records_request_date")) if "records_request_date" in dates else "",
                     "last_inspection_date": D.iso(dates.get("last_inspection_date")), "qc_request_complete_date": D.iso(dates.get("qc_request_complete_date")),
                     "qc_request_date": D.iso(dates.get("qc_request_date")), "third_party_offer_mailed_date": D.iso(dates.get("third_party_offer_mailed_date")),
                     "third_party_offer_received_date": D.iso(dates.get("third_party_offer_received_date")), "usda_prepay_request_date": D.iso(dates.get("usda_prepay_request_date")),
                     "notice_received_date": D.iso(dates.get("notice_received_date")), "notice_log_status": _s(r.get("notice_log_status")).lower(),
                     "recap_evidence_basis": "RECORDED" if _s(r.get("recap_status")) else "", "coterminous_with": _s(r.get("coterminous_with"))})
        if a.internal:
            lead["am_officer_email"] = _s(r.get("am_officer_email"))
        for field in ("origination_date", "contract_expiration", "lien_position", "rate_type", "accrued_interest"):
            lead[field] = D.iso(dates.get(field)) if field in ("origination_date", "contract_expiration") else _s(r.get(field))
        fd, fr, inh = A.first_events(evs, hz, hz)
        A.apply_first(lead, fd, fr, inh)
        leads.append(lead)
        events.extend(evs)
    if n_total and n_ok == 0:
        print(f"ERROR agency_servicing_extract: every row failed validation. First failing rule: {rejects[0]['reason'] if rejects else 'unknown'}", file=sys.stderr)
        sys.exit(2)
    summary = {"adapter": "agency_servicing_extract", "as_of_date": as_of.isoformat(), "input_sha256": A.sha256(a.input), "vintage": vintage, "agency_profile": a.agency_profile,
               "rows_total": n_total, "rows_valid": n_ok, "rows_rejected": n_total - n_ok, "leads": len(leads), "events": len(events), "by_basis": A.basis_breakdown(events),
               "by_book_kind": pd.Series([l["book_kind"] for l in leads]).value_counts().to_dict() if leads else {},
               "notice_log_blank_share": round(sum(1 for l in leads if l.get("notice_log_status") in ("", "unknown")) / len(leads), 3) if leads else 0.0,
               "verified_live": True, "note": "the agency's own ledger is RECORDED for its loans; notice_log_status blank -> unknown"}
    A.write_outputs(a.out_dir, leads, events, summary, pii_scope="internal" if a.internal else "organization")
    pd.DataFrame(rejects, columns=REJECT_COLUMNS).to_csv(os.path.join(a.out_dir, "rejects.csv"), index=False)
    print(f"[servicing] rows {n_total} valid {n_ok} rejected {n_total - n_ok} leads {len(leads)} events {len(events)} by_kind {summary['by_book_kind']}")
    print("[servicing] basis breakdown: " + " / ".join(f"{k} {v}" for k, v in summary["by_basis"].items()))
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", required=True)
    ap.add_argument("--sheet", default=None)
    ap.add_argument("--pack", default=None)
    ap.add_argument("--agency-profile", default="hfa", choices=["hfa", "city_housing", "county", "pha_am", "cdbg_home"])
    ap.add_argument("--crosswalk", default=None, help="book_crosswalk.csv (used by build_universe.py; accepted here for symmetry)")
    ap.add_argument("--zip-crosswalk", default=None)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--horizon-years", type=float, default=10)
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--internal", action="store_true", help="write am_officer_email (internal scope)")
    run(ap.parse_args(argv))


if __name__ == "__main__":
    main()
