"""Shared helpers for file-drop adapters (HUD FHASL, HUD Section 8, recorder extracts).

Adapters never fetch: they read a file the analyst downloaded into the inbox, validate that the columns
match the schema declared in the pack's dataset-schemas.yaml (field names are confirmed only from the live
file, so every mismatch is reported by name), resolve county FIPS from a county column or a HUD USPS
ZIP-County crosswalk (never a ZIP prefix), and emit canonical leads/events rows.
"""
from __future__ import annotations

import hashlib
import os
import re
from datetime import date
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd

from . import geo as G
from .dates import months_between, urgency_band
from .schema import EVENT_COLUMNS, LEAD_COLUMNS, direction_of, family_of


class SchemaMismatch(Exception):
    pass


def read_table(path: str, sheet: Optional[str] = None) -> pd.DataFrame:
    if path.lower().endswith((".xlsx", ".xlsm", ".xls")):
        df = pd.read_excel(path, sheet_name=sheet or 0, dtype=str)
    else:
        df = pd.read_csv(path, dtype=str, encoding="utf-8-sig", keep_default_na=False)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def resolve_columns(df: pd.DataFrame, aliases: Dict[str, Sequence[str]], required: Sequence[str]) -> Dict[str, str]:
    """Map canonical field -> actual column using case/space-insensitive alias lists.

    Raises SchemaMismatch naming every missing required field and listing the file's columns, so the analyst
    can extend the alias table after confirming the live header (`verified_live=false` until then).
    """
    norm = {re.sub(r"[^a-z0-9]", "", c.lower()): c for c in df.columns}
    out: Dict[str, str] = {}
    for field, names in aliases.items():
        for n in names:
            k = re.sub(r"[^a-z0-9]", "", n.lower())
            if k in norm:
                out[field] = norm[k]
                break
    missing = [f for f in required if f not in out]
    if missing:
        raise SchemaMismatch(f"missing required fields {missing}; file columns: {list(df.columns)}")
    return out


def file_vintage(path: str) -> str:
    m = re.search(r"(20\d{2}[-_]?\d{2}[-_]?\d{2}|20\d{2}[-_]?\d{2})", os.path.basename(path))
    return m.group(1) if m else date.fromtimestamp(os.path.getmtime(path)).isoformat()


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def county_resolver(crosswalk_path: Optional[str]):
    """Return fn(zip, county_name, state) -> (county_fips, geo_grade, straddles)."""
    xw = G.load_zip_crosswalk(crosswalk_path) if crosswalk_path else {}

    def resolve(zip_code, county_name=None, state=None) -> Tuple[Optional[str], str, bool]:
        if county_name:
            f = G.county_fips_from_name(county_name)
            if f:
                return f, "county_field", False
        z = G.zip5(zip_code)
        if z and z in xw:
            fips, ratio, straddles = xw[z]
            return fips, "zip_crosswalk", straddles
        return None, "", False
    return resolve


def digits_only(s) -> str:
    return re.sub(r"\D", "", str(s or ""))


def blank_lead(**kw) -> Dict[str, Any]:
    lead = {c: "" for c in LEAD_COLUMNS}
    lead.update(kw)
    return lead


def make_event(pid: str, etype: str, d: Optional[date], basis: str, source: str, as_of: date, vintage: str, **kw) -> Optional[Dict[str, Any]]:
    if d is None:
        return None
    mo = months_between(as_of, d)
    ev = {c: "" for c in EVENT_COLUMNS}
    ev.update({"event_id": f"{pid}:{etype}:{d.isoformat()}", "property_id": pid, "event_type": etype, "event_family": family_of(etype),
               "direction": direction_of(etype), "event_date": d.isoformat(), "months_out": mo, "urgency_band": urgency_band(mo),
               "basis": basis, "confidence": kw.pop("confidence", 1.0), "source": source, "source_vintage": vintage,
               "status": "PAST" if mo < 0 else "FUTURE", "event_date_quality": "declared_format"})
    ev.update({k: ("" if v is None else v) for k, v in kw.items()})
    return ev


def first_events(events: List[Dict[str, Any]], horizon_m: float, reg_horizon_m: float, helper_types=("PRESERVATION_NOTICE_WINDOW", "HAP_OPTOUT_NOTICE_DEADLINE")):
    live = [e for e in events if e["status"] not in ("REJECTED", "SUPPRESSED") and e["direction"] == "PRESSURE"]
    debt = [e for e in live if e["event_family"] == "DEBT" and 0 <= e["months_out"] <= horizon_m]
    reg = [e for e in live if e["event_family"] == "REGULATORY" and e["event_type"] not in helper_types and 0 <= e["months_out"] <= reg_horizon_m]
    fd = min(debt, key=lambda e: e["event_date"]) if debt else None
    fr = min(reg, key=lambda e: e["event_date"]) if reg else None
    inh = sorted([e for e in live if 0 <= e["months_out"] <= max(horizon_m, reg_horizon_m)], key=lambda e: e["event_date"])
    return fd, fr, inh


def apply_first(lead: Dict[str, Any], fd, fr, inh) -> None:
    import json
    for prefix, e in (("first_debt", fd), ("first_reg", fr)):
        lead[f"{prefix}_event_type"] = e["event_type"] if e else ""
        lead[f"{prefix}_event_date"] = e["event_date"] if e else ""
        lead[f"{prefix}_months_out"] = e["months_out"] if e else ""
        lead[f"{prefix}_basis"] = e["basis"] if e else ""
        lead[f"{prefix}_source"] = e["source"] if e else ""
    lead["events_in_horizon"] = json.dumps([{k: e.get(k, "") for k in ("event_type", "event_date", "months_out", "basis", "confidence", "source",
                                                                        "verify_flag", "alt_dates", "window_start", "window_end", "direction")} for e in inh])


def write_outputs(out_dir: str, leads: List[Dict[str, Any]], events: List[Dict[str, Any]], summary: Dict[str, Any], prefix: str = "") -> None:
    import json
    os.makedirs(out_dir, exist_ok=True)
    extra = sorted({k for l in leads for k in l if k not in LEAD_COLUMNS})
    pd.DataFrame(leads, columns=LEAD_COLUMNS + extra).to_csv(os.path.join(out_dir, f"{prefix}leads.csv"), index=False)
    pd.DataFrame(events, columns=EVENT_COLUMNS).to_csv(os.path.join(out_dir, f"{prefix}events.csv"), index=False)
    with open(os.path.join(out_dir, f"{prefix}calendar_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, default=str)


def basis_breakdown(events: List[Dict[str, Any]]) -> Dict[str, int]:
    live = [e for e in events if e["status"] != "REJECTED"]
    return {b: sum(1 for e in live if e["basis"] == b) for b in ("RECORDED", "REPORTED", "DERIVED", "ESTIMATED", "PROXY")}
