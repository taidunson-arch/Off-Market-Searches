#!/usr/bin/env python3
"""Union adapter outputs (agency servicing extract, OHCS inventory, HUD tapes, OHCS forecast, REAC) into one lead table + one event table.

Join key is `property_id`. The servicing extract is joined first through plb/book_join.py (crosswalk > address > fuzzy > unmatched) and
the decisions are passed in as `id_map`; non-book sources still reconcile by fuzzy name + zip5 >= 0.92 across sources (never within
one source, never across phases). For each lead field the value from the higher-basis source wins; book columns come only from the
servicing adapter; owner_name blank in OHCS -> HUD Sec 8 owner_organization_name -> servicing owner.

Universe tagging (pipeline-contract.md Section 10): book + inventory -> our_book / matched (or self_owned) / in_inventory true; book-only ->
our_book / book_only, in_inventory false, servicing_unmatched.csv; inventory-only -> universe_not_held with book_match per profile and coverage
(unmatched_expected under `full` when the profile expects the row in book; not_in_extract under `partial`; not_in_book otherwise;
book_absent when no extract was supplied). Owner names matching the profile's self_owner_tokens are self_owned / our_book.

Event dedupe key = (property_id, event_type, program, detail); AGENCY_DEADLINE rows, PRESERVATION_NOTICE_WINDOW and agency_servicing rows
are exempt from the conflict-flag path. The OHCS PROXY LOAN_MATURITY is dropped when a RECORDED AGENCY_LOAN_MATURITY exists; a HUD Sec 8
HAP_EXPIRATION overrides the OHCS HUD_MF date. SUPPRESS_UNTIL in the future marks DEBT events SUPPRESSED.

Usage:
  python scripts/merge_leads.py --inputs a/leads.csv b/leads.csv --events a/events.csv b/events.csv --out-dir runs/merged
      [--book-leads adapter_agency_servicing/leads.csv] [--agency-profile hfa] [--book-coverage partial] [--pack <dir>]
      [--horizon-years 10] [--regulatory-horizon-years 10] [--as-of YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plb import adapters as A  # noqa: E402
from plb.book_join import join_book, load_crosswalk, phase_tokens  # noqa: E402
from plb.dates import months_between, parse_as_of, parse_iso, urgency_band  # noqa: E402
from plb.entities import is_self_owned  # noqa: E402
from plb.geo import zip5  # noqa: E402
from plb.schema import BOOK_KINDS, EVENT_COLUMNS, FLAG_CONFLICT, LEAD_COLUMNS, agency_profile  # noqa: E402

BASIS_RANK = {b: i for i, b in enumerate(["RECORDED", "REPORTED", "DERIVED", "ESTIMATED", "PROXY"])}
BOOK_ONLY_COLUMNS = {"agency_loan_ids", "grant_ids", "agency_programs", "public_upb", "our_rate", "payment_type", "our_maturity", "our_maturity_basis", "affordability_end",
                     "recapture_type", "recapture_method", "recapture_amount", "covenant_status", "am_officer", "book_kind", "units_assisted", "recapture_start", "recapture_end"}


def _rank(b: str) -> int:
    return BASIS_RANK.get(str(b or "").upper(), 9)


def fuzzy_key(name: str, z: str) -> str:
    return f"{str(name or '').upper().strip()}|{zip5(z)}"


def _blank(v) -> bool:
    return v is None or (isinstance(v, float) and pd.isna(v)) or str(v).strip() == ""


LEAD_COLUMN_FOR_SOURCE = {"OHCS Funded?": "ohcs_funded", "programs": "programs"}


UNION_COLUMNS = ("signals", "verify_flags", "programs", "source_vintages", "compliance_gates", "kpi_flags", "agency_loan_ids", "grant_ids", "agency_programs")


def expected_in_book(lead: Dict[str, Any], profile: Dict[str, Any]) -> bool:
    """Does the profile expect this inventory row in its book? (agency-profiles.yaml expected_book_flag; R3)."""
    flag = profile.get("expected_book_flag")
    if not flag:
        return False
    if flag == "ohcs_funded":
        return str(lead.get("ohcs_funded") or "").lower() == "true"
    if flag == "home_cdbg_programs":
        return bool({"HOME", "CDBG"} & set(str(lead.get("programs") or "").split(";")))
    if isinstance(flag, dict):
        col = LEAD_COLUMN_FOR_SOURCE.get(str(flag.get("column")), str(flag.get("column") or "").strip().lower().replace(" ", "_").replace("?", ""))
        val = str(lead.get(col) or "")
        if "equals" in flag:
            return val.strip().lower() == str(flag["equals"]).strip().lower()
        if "intersects" in flag:
            return bool(set(str(x) for x in flag["intersects"]) & set(v for v in val.split(";") if v))
    return False


def merge(lead_frames: List[pd.DataFrame], event_frames: List[pd.DataFrame], as_of, horizon_years: float, reg_horizon_years: float,
          book_index: Optional[int] = None, id_map: Optional[Dict[str, str]] = None, join_grades: Optional[Dict[str, str]] = None,
          profile: Optional[Dict[str, Any]] = None, coverage: str = "partial"):
    profile = profile or {}
    id_map = id_map or {}
    join_grades = join_grades or {}
    book_present = book_index is not None
    for i, f in enumerate(lead_frames):
        f["_src"] = i
        f["_is_book"] = (i == book_index)
        if i == book_index and id_map:
            f["_book_pid"] = f["property_id"].astype(str)
            f["property_id"] = f["property_id"].astype(str).map(lambda p: id_map.get(p) or p)
    for i, f in enumerate(event_frames):
        if i == book_index and id_map and len(f):
            f["property_id"] = f["property_id"].astype(str).map(lambda p: id_map.get(p) or p)
    leads = pd.concat(lead_frames, ignore_index=True) if lead_frames else pd.DataFrame(columns=LEAD_COLUMNS + ["_src", "_is_book"])
    events = pd.concat(event_frames, ignore_index=True) if event_frames else pd.DataFrame(columns=EVENT_COLUMNS)
    for c in LEAD_COLUMNS:
        if c not in leads.columns:
            leads[c] = ""
    if "_book_pid" not in leads.columns:
        leads["_book_pid"] = ""
    leads["_book_pid"] = leads["_book_pid"].fillna("").astype(str).replace({"nan": "", "None": ""})
    log: List[Dict[str, Any]] = []
    # ---- fuzzy id reconciliation across non-book sources
    canon: Dict[str, str] = {}
    by_key: Dict[str, tuple] = {}
    for _, r in leads.iterrows():
        pid = str(r["property_id"])
        if bool(r.get("_is_book")):
            canon.setdefault(pid, pid)
            continue
        k = fuzzy_key(r["property_name"], r["zip"])
        src = r.get("_src")
        toks = phase_tokens(r["property_name"])
        matched = None
        if pid not in canon and k.split("|")[1]:
            for other_k, (other_pid, other_src, other_toks) in by_key.items():
                if other_src == src or other_pid == pid or other_k.split("|")[1] != k.split("|")[1]:
                    continue
                if other_toks != toks:
                    continue
                ratio = difflib.SequenceMatcher(None, other_k.split("|")[0], k.split("|")[0]).ratio()
                if ratio >= 0.92:
                    matched = other_pid
                    log.append({"property_id": pid, "merged_into": other_pid, "name": r["property_name"], "ratio": round(ratio, 3), "grade": "fuzzy", "note": "cross-source name match"})
                    break
        canon[pid] = matched or canon.get(pid, pid)
        by_key.setdefault(k, (canon[pid], src, toks))
    leads["property_id"] = leads["property_id"].map(lambda p: canon.get(str(p), str(p)))
    if len(events):
        events["property_id"] = events["property_id"].map(lambda p: canon.get(str(p), str(p)))

    # ---- field-level merge preferring higher basis; inventory row is the geographic base
    def row_rank(r):
        return min(_rank(r.get("first_debt_basis")), _rank(r.get("first_reg_basis")))

    merged_rows: List[Dict[str, Any]] = []
    unmatched_book: List[Dict[str, Any]] = []
    for pid, grp in leads.groupby("property_id", sort=False):
        grp = grp.copy()
        grp["_rank"] = grp.apply(row_rank, axis=1)
        grp["_inv"] = grp["_is_book"].map(lambda b: 1 if b else 0)
        grp = grp.sort_values(["_inv", "_rank"])  # inventory rows first (identity / geography), then by evidence quality
        base = grp.iloc[0].to_dict()
        has_book = bool(grp["_is_book"].any())
        has_inv = bool((~grp["_is_book"].astype(bool)).any())
        fill_cols = [c for c in grp.columns if not str(c).startswith("_")]
        for _, other in grp.iloc[1:].iterrows():
            for c in fill_cols:
                if c in BOOK_ONLY_COLUMNS and not bool(other.get("_is_book")):
                    continue
                if _blank(base.get(c)) and not _blank(other.get(c)):
                    base[c] = other[c]
            # book columns always come from the book row even when the inventory row is the base
            if bool(other.get("_is_book")):
                for c in BOOK_ONLY_COLUMNS | {"notice_status", "tenant_notice_status", "hap_renewal_request_status", "hap_renewal_option", "recap_status", "qc_status", "qc_waived",
                                              "notice_address", "notice_address_source", "senior_lien_type", "senior_maturity", "senior_maturity_basis", "senior_upb", "apps_flag", "rofr_recorded"}:
                    if c in UNION_COLUMNS:
                        continue  # ';'-lists (agency_loan_ids, grant_ids, agency_programs, signals ...) are unioned below, never overwritten
                    if c in other and not _blank(other.get(c)) and (c in BOOK_ONLY_COLUMNS or _blank(base.get(c)) or str(base.get(c)) in ("unknown", "none")):
                        base[c] = other[c]
                if str(other.get("book_match")) == "self_owned":
                    base["book_match"] = "self_owned"
            for c in UNION_COLUMNS:
                a_, b_ = str(base.get(c) or ""), str(other.get(c) or "")
                items = [x for x in (a_ + ";" + b_).split(";") if x.strip()]
                base[c] = ";".join(dict.fromkeys(items))
            if c == "public_upb" or True:
                # two loans on one property: sum the UPB of book rows
                pass
        book_rows = grp[grp["_is_book"].astype(bool)]
        if len(book_rows) > 1:
            # several instruments on one property: book_kind is a ';'-list in BOOK_KINDS order (loan first); scalar loan terms
            # (payment_type, our_rate) come from the first loan row, recapture_* from the row that carries a recapture position
            kinds = [k for k in BOOK_KINDS if k in set(str(x) for x in book_rows["book_kind"] if str(x).strip())]
            base["book_kind"] = ";".join(kinds)
            loan_rows = book_rows[book_rows["book_kind"].astype(str) == "loan"]
            if len(loan_rows):
                for c in ("payment_type", "our_rate", "our_maturity_basis"):
                    v = loan_rows.iloc[0].get(c)
                    if not _blank(v):
                        base[c] = v
            rec_rows = book_rows[book_rows["recapture_type"].astype(str).str.strip().isin(["", "none", "nan"]) == False] if "recapture_type" in book_rows.columns else book_rows.iloc[0:0]
            if len(rec_rows):
                for c in ("recapture_type", "recapture_method", "recapture_start", "recapture_end"):
                    v = rec_rows.iloc[0].get(c)
                    if not _blank(v):
                        base[c] = v
            base["public_upb"] = float(pd.to_numeric(book_rows["public_upb"], errors="coerce").fillna(0).sum())
            mats = [parse_iso(x) for x in book_rows["our_maturity"] if parse_iso(x)]
            if mats:
                base["our_maturity"] = min(mats).isoformat()
            amts = pd.to_numeric(book_rows["recapture_amount"], errors="coerce")
            if amts.notna().any():
                base["recapture_amount"] = float(amts.fillna(0).sum())
        # universe / book_match
        self_owned = str(base.get("book_match")) == "self_owned" or is_self_owned(base.get("owner_name"), profile.get("self_owner_tokens"), base.get("developer_name"))
        if self_owned and str(base.get("owner_type")) != "self_owned":
            base["signals"] = ";".join(dict.fromkeys([s for s in str(base.get("signals") or "").split(";") if s] + ["self_owned"]))
        if has_book and has_inv:
            base["universe"], base["in_inventory"] = "our_book", True
            base["book_match"] = "self_owned" if self_owned else "matched"
            bpid = next((str(x) for x in grp["_book_pid"] if str(x) not in ("", "nan", "None")), "")
            base["book_join_grade"] = join_grades.get(bpid, join_grades.get(pid, "address"))
        elif has_book:
            base["universe"], base["in_inventory"] = "our_book", False
            base["book_match"] = "self_owned" if self_owned else "book_only"   # in our book, not in the inventory (R3 / pipeline-contract Section 10)
            base["book_join_grade"] = "unmatched"
            unmatched_book.append({"property_id": pid, "property_name": base.get("property_name"), "address": base.get("address"), "zip": base.get("zip"),
                                   "book_kind": base.get("book_kind"), "agency_loan_ids": base.get("agency_loan_ids"), "grant_ids": base.get("grant_ids"),
                                   "note": "book row not found in the inventory (crosswalk > address > fuzzy all missed); scored on capital, servicing events and units_assisted"})
        else:
            base["in_inventory"] = True
            if self_owned:
                base["universe"], base["book_match"] = "our_book", "self_owned"
            elif not book_present:
                base["universe"], base["book_match"] = "universe_not_held", "book_absent"
            elif coverage == "full" and expected_in_book(base, profile):
                base["universe"], base["book_match"] = "universe_not_held", "unmatched_expected"
            elif coverage == "partial":
                base["universe"], base["book_match"] = "universe_not_held", "not_in_extract"
            else:
                base["universe"], base["book_match"] = "universe_not_held", "not_in_book"
            base["book_join_grade"] = ""
        if str(base.get("book_match")) == "self_owned":
            base["owner_type"] = "self_owned"
        for k in list(base):
            if str(k).startswith("_"):
                base.pop(k)
        merged_rows.append(base)
    extra_cols = [c for c in leads.columns if c not in LEAD_COLUMNS and not str(c).startswith("_")]
    out = pd.DataFrame(merged_rows, columns=LEAD_COLUMNS + extra_cols).astype(object)

    # ---- events: dedupe same (property, type, program, detail); keep best basis, record alternates; drop PROXY when RECORDED ours exists
    if len(events):
        events = events.astype(object)
        for c in ("program", "detail", "source", "event_family"):
            if c not in events.columns:
                events[c] = ""
            events[c] = events[c].fillna("")
        recorded_ours = set(events[(events["event_type"] == "AGENCY_LOAN_MATURITY") & (events["basis"] == "RECORDED")]["property_id"])
        drop = (events["event_type"] == "LOAN_MATURITY") & (events["basis"] == "PROXY") & (events["property_id"].isin(recorded_ours))
        for pid in set(events[drop]["property_id"]):
            log.append({"property_id": pid, "merged_into": pid, "name": "PROXY LOAN_MATURITY dropped: RECORDED AGENCY_LOAN_MATURITY on file", "ratio": "", "grade": "", "note": ""})
        events = events[~drop]
        hud_hap = set(events[(events["event_type"] == "HAP_EXPIRATION") & (events["source"].astype(str).str.contains("HUD MF Assistance", na=False))]["property_id"])
        drop2 = (events["event_type"] == "HAP_EXPIRATION") & (events["source"].astype(str).str.startswith("OHCS OAHI")) & (events["property_id"].isin(hud_hap))
        events = events[~drop2]
        events["_rank"] = events["basis"].map(_rank)
        events = events.sort_values(["property_id", "event_type", "_rank", "event_date"])
        exempt = (events["event_family"] == "AGENCY_DEADLINE") | (events["event_type"] == "PRESERVATION_NOTICE_WINDOW") | (events["source"].astype(str) == "agency_servicing")
        keep = [r for r in events[exempt].to_dict(orient="records")]
        conflicts: List[Dict[str, Any]] = []
        for (pid, et, prog, det), grp in events[~exempt].groupby(["property_id", "event_type", "program", "detail"], sort=False):
            best = grp.iloc[0].to_dict()
            others = grp.iloc[1:]
            alts = sorted({str(d) for d in grp["event_date"].tolist() if str(d) and str(d) != str(best["event_date"])})
            if alts:
                prev = [x for x in str(best.get("alt_dates") or "").split(";") if x]
                best["alt_dates"] = ";".join(dict.fromkeys(prev + alts))
                b1, b2 = parse_iso(best["event_date"]), parse_iso(alts[0])
                strong = all(_rank(b) <= 1 for b in grp["basis"])
                if strong and b1 and b2 and abs((b1 - b2).days) > 31:
                    if not best.get("verify_flag"):
                        best["verify_flag"] = FLAG_CONFLICT
                    conflicts.append({"property_key": "", "property_id": pid, "column": et, "raw_value": ";".join(alts), "reason": f"{FLAG_CONFLICT}: {et} {best['event_date']} vs {alts}", "flag": FLAG_CONFLICT, "alt_dates": ";".join(alts)})
                    for _, o in others.iterrows():
                        oo = o.to_dict()
                        oo["verify_flag"] = oo.get("verify_flag") or FLAG_CONFLICT
                        keep.append(oo)
            keep.append(best)
        events = pd.DataFrame(keep).astype(object)
        events = events.drop(columns=[c for c in ["_rank"] if c in events.columns])
        d = pd.to_datetime(events["event_date"], errors="coerce")
        events["months_out"] = [months_between(as_of, x.date()) if pd.notna(x) else "" for x in d]
        events["urgency_band"] = events["months_out"].map(lambda m: urgency_band(m) if m != "" else "")
        sup = events[(events["event_type"] == "SUPPRESS_UNTIL") & (d > pd.Timestamp(as_of))]
        for pid in set(sup["property_id"]):
            m = (events["property_id"] == pid) & (events["event_family"] == "DEBT") & (events["event_type"] != "SUPPRESS_UNTIL")
            events.loc[m, "status"] = "SUPPRESSED"
            log.append({"property_id": pid, "merged_into": pid, "name": "SUPPRESS_UNTIL applied", "ratio": "", "grade": "", "note": ""})
        events = events[EVENT_COLUMNS + [c for c in events.columns if c not in EVENT_COLUMNS]]
        # recompute first_debt / first_reg / events_in_horizon
        hz, rz = horizon_years * 12, reg_horizon_years * 12
        ev_by_pid: Dict[str, List[Dict[str, Any]]] = {}
        for rec in events.to_dict(orient="records"):
            if rec.get("months_out") in ("", None):
                continue
            ev_by_pid.setdefault(str(rec["property_id"]), []).append(rec)
        for i, r in out.iterrows():
            fd, fr, inh = A.first_events(ev_by_pid.get(str(r["property_id"]), []), hz, rz)
            lead = {}
            A.apply_first(lead, fd, fr, inh)
            for k, v in lead.items():
                out.at[i, k] = v
        out["as_of_date"] = as_of.isoformat()
        rejects = pd.DataFrame(conflicts, columns=["property_key", "property_id", "column", "raw_value", "reason", "flag", "alt_dates"])
    else:
        rejects = pd.DataFrame(columns=["property_key", "property_id", "column", "raw_value", "reason", "flag", "alt_dates"])
    out["units"] = [u if not _blank(u) else (ua if not _blank(ua) else "") for u, ua in zip(out["units"], out.get("units_assisted", pd.Series([""] * len(out))))]
    return out, events, pd.DataFrame(log, columns=["property_id", "merged_into", "name", "ratio", "grade", "note"]), pd.DataFrame(unmatched_book), rejects


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--inputs", nargs="+", required=True, help="leads.csv files (the book leads file may be among them; name it with --book-leads)")
    ap.add_argument("--events", nargs="+", required=True)
    ap.add_argument("--book-leads", default=None, help="which of --inputs is the agency servicing adapter output")
    ap.add_argument("--crosswalk", default=None, help="book_crosswalk.csv")
    ap.add_argument("--agency-profile", default="hfa")
    ap.add_argument("--book-coverage", default="partial", choices=["full", "partial"])
    ap.add_argument("--pack", default=None)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--horizon-years", type=float, default=10)
    ap.add_argument("--regulatory-horizon-years", type=float, default=None)
    ap.add_argument("--as-of", default=None)
    a = ap.parse_args(argv)
    as_of = parse_as_of(a.as_of)
    paths = [p for p in a.inputs if os.path.exists(p)]
    lf = [pd.read_csv(p, dtype=str, keep_default_na=False) for p in paths]
    ef = [pd.read_csv(p, dtype=str, keep_default_na=False) for p in a.events if os.path.exists(p)]
    prof = agency_profile(a.agency_profile, a.pack)
    book_index = None
    id_map, grades = {}, {}
    if a.book_leads and os.path.abspath(a.book_leads) in [os.path.abspath(p) for p in paths]:
        book_index = [os.path.abspath(p) for p in paths].index(os.path.abspath(a.book_leads))
        inv = pd.concat([f for i, f in enumerate(lf) if i != book_index], ignore_index=True) if len(lf) > 1 else pd.DataFrame(columns=LEAD_COLUMNS)
        xw = load_crosswalk(a.crosswalk or (os.path.join(a.pack, "book_crosswalk.csv") if a.pack else None))
        decisions, jlog = join_book(lf[book_index], inv, xw)
        id_map = {k: v["inventory_pid"] for k, v in decisions.items() if v["inventory_pid"]}
        grades = {k: v["grade"] for k, v in decisions.items()}
    out, events, log, unmatched, rejects = merge(lf, ef, as_of, a.horizon_years, a.regulatory_horizon_years or a.horizon_years, book_index, id_map, grades, prof, a.book_coverage)
    os.makedirs(a.out_dir, exist_ok=True)
    out.to_csv(os.path.join(a.out_dir, "leads.csv"), index=False)
    events.to_csv(os.path.join(a.out_dir, "events.csv"), index=False)
    log.to_csv(os.path.join(a.out_dir, "merge_log.csv"), index=False)
    unmatched.to_csv(os.path.join(a.out_dir, "servicing_unmatched.csv"), index=False)
    print(f"[merge] inputs {len(lf)} lead files / {len(ef)} event files -> {len(out)} leads, {len(events)} events; log rows {len(log)}; servicing unmatched {len(unmatched)}")


if __name__ == "__main__":
    main()
