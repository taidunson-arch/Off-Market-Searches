"""Servicing extract <-> inventory join (pipeline-contract.md Section 10; servicing-extract.md Section 5).

Order, recorded per book row as `book_join_grade`:
  1. crosswalk : references/sources/<pack>/book_crosswalk.csv (agency_loan_id | grant_id | asset_id | contract_id -> property_id)
  2. address   : the v2 property_id (addr: + sha1 of normalized address + '|' + zip5) computed for every servicing row
                 regardless of parcel_id; `ohcs_property_key` compared after upper() + normalize_address()
  3. fuzzy     : upper(name) token-set ratio >= 0.92 AND same zip5 AND phase tokens equal (or absent on both sides);
                 REPORTED-grade, written to merge_log, never auto-promoted
  4. unmatched : servicing_unmatched.csv with candidate matches

Phase tokens {I, II, III, IV, A, B, C, 1, 2, 3, Phase n} are hard discriminators: "Powell Plaza I" never joins
"Powell Plaza II" (ratio 0.966).
"""
from __future__ import annotations

import difflib
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from . import geo as G

_PHASE_RE = re.compile(r"\b(\d+|[IVX]+|PHASE\s*\w+|[A-D])\b")
FUZZY_MIN = 0.92


def phase_tokens(name: str) -> frozenset:
    """Digits, roman numerals, single letters A-D and 'Phase n' that distinguish sibling phases."""
    return frozenset(m.group(0).replace(" ", "") for m in _PHASE_RE.finditer(str(name or "").upper()))


def _name_core(name: str) -> str:
    s = re.sub(r"[^A-Z0-9 ]", " ", str(name or "").upper())
    return re.sub(r"\s+", " ", s).strip()


def token_set_ratio(a: str, b: str) -> float:
    """difflib ratio on sorted token sets (order-insensitive)."""
    ta, tb = " ".join(sorted(_name_core(a).split())), " ".join(sorted(_name_core(b).split()))
    if not ta or not tb:
        return 0.0
    return max(difflib.SequenceMatcher(None, ta, tb).ratio(), difflib.SequenceMatcher(None, _name_core(a), _name_core(b)).ratio())


def ohcs_key(name: str, addr: str) -> str:
    return f"{_name_core(name)}|{G.normalize_address(addr)}"


def load_crosswalk(path: Optional[str]) -> Dict[str, str]:
    """book id (any of agency_loan_id / grant_id / asset_id / contract_id) -> property_id."""
    out: Dict[str, str] = {}
    if not path or not os.path.exists(path):
        return out
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    idcol = next((c for c in ("book_id", "agency_loan_id", "grant_id", "asset_id", "contract_id") if c in df.columns), None)
    if idcol is None or "property_id" not in df.columns:
        return out
    for c in ("book_id", "agency_loan_id", "grant_id", "asset_id", "contract_id"):
        if c in df.columns:
            for k, v in zip(df[c], df["property_id"]):
                if str(k).strip() and str(v).strip():
                    out[str(k).strip()] = str(v).strip()
    return out


def join_book(book: pd.DataFrame, inventory: pd.DataFrame, crosswalk: Optional[Dict[str, str]] = None) -> Tuple[Dict[str, Dict[str, Any]], List[Dict[str, Any]]]:
    """Return (decisions by book property_id, merge_log rows).

    decision = {inventory_pid, grade, ratio, book_pids[]} ; grade in crosswalk | address | fuzzy | unmatched.
    `book` rows carry property_id (addr hash), property_name, address, zip, agency_loan_id, grant_id, asset_id, contract_id,
    ohcs_property_key, site_type; `inventory` rows carry property_id, property_name, address, zip.
    """
    crosswalk = crosswalk or {}
    inv_by_pid = {str(r["property_id"]): r for r in inventory.to_dict(orient="records")} if len(inventory) else {}
    inv_by_key: Dict[str, str] = {}
    inv_by_zip: Dict[str, List[Dict[str, Any]]] = {}
    for r in inv_by_pid.values():
        inv_by_key[ohcs_key(r.get("property_name", ""), r.get("address", ""))] = str(r["property_id"])
        inv_by_zip.setdefault(G.zip5(r.get("zip")), []).append(r)
    decisions: Dict[str, Dict[str, Any]] = {}
    log: List[Dict[str, Any]] = []
    for r in (book.to_dict(orient="records") if len(book) else []):
        bpid = str(r.get("property_id"))
        ids: List[str] = []
        for c in ("agency_loan_id", "grant_id", "asset_id", "contract_id", "agency_loan_ids", "grant_ids", "asset_ids", "contract_ids"):
            for part in str(r.get(c) or "").split(";"):
                if part.strip() and part.strip() not in ids:
                    ids.append(part.strip())
        target, grade, ratio, note = None, "unmatched", None, ""
        # 1 crosswalk
        for i in ids:
            if i and i in crosswalk and crosswalk[i] in inv_by_pid:
                target, grade = crosswalk[i], "crosswalk"
                break
        # 2 address (addr-hash id or OHCS Name|Address key)
        if target is None:
            if bpid in inv_by_pid:
                target, grade = bpid, "address"
            else:
                key = str(r.get("ohcs_property_key") or "").strip()
                if key:
                    parts = key.split("|", 1)
                    k = ohcs_key(parts[0], parts[1] if len(parts) > 1 else "")
                    if k in inv_by_key:
                        target, grade = inv_by_key[k], "address"
                if target is None and r.get("address"):
                    k2 = G.property_id("OR", r.get("county_fips") or None, None, r.get("address"), r.get("zip"))
                    if k2 in inv_by_pid:
                        target, grade = k2, "address"
        # 3 fuzzy
        if target is None:
            z = G.zip5(r.get("zip"))
            toks = phase_tokens(r.get("property_name"))
            best, best_pid = 0.0, None
            for cand in inv_by_zip.get(z, []):
                ct = phase_tokens(cand.get("property_name"))
                if ct != toks:
                    continue
                ratio_c = token_set_ratio(r.get("property_name"), cand.get("property_name"))
                if ratio_c > best:
                    best, best_pid = ratio_c, str(cand["property_id"])
            if best_pid and best >= FUZZY_MIN:
                target, grade, ratio = best_pid, "fuzzy", round(best, 3)
                note = "REPORTED-grade name match; confirm and add to book_crosswalk.csv"
            elif best_pid:
                note = f"best candidate {best_pid} ratio {best:.3f} below {FUZZY_MIN}"
        if str(r.get("site_type") or "").lower().startswith("scatter"):
            note = (note + "; " if note else "") + "scattered_site_join"
        decisions[bpid] = {"inventory_pid": target, "grade": grade, "ratio": ratio, "note": note,
                           "book_ids": [i for i in ids if i], "property_name": r.get("property_name")}
        log.append({"property_id": bpid, "merged_into": target or "", "name": r.get("property_name"), "ratio": ratio if ratio is not None else "",
                    "grade": grade, "note": note})
    return decisions, log
