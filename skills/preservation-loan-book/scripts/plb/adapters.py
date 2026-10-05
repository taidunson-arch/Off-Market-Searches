"""Shared helpers for file-drop adapters (agency servicing extract, OHCS inventory, HUD tapes, OHCS forecast, REAC).

Adapters never fetch: they read a file the analyst downloaded into the inbox, validate that the columns match the
schema declared in the pack's dataset-schemas.yaml (every mismatch is reported by name), resolve county FIPS from a
county column or a HUD USPS ZIP-County crosswalk (never a ZIP prefix), and emit canonical leads/events rows.
Default outputs are organization scope: `plb.pii.NEVER_COLUMNS` are dropped at write time.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import date
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd

from . import geo as G
from .dates import months_between, urgency_band
from .schema import EVENT_COLUMNS, HELPER_EVENTS, LEAD_COLUMNS, direction_of, family_of


class SchemaMismatch(Exception):
    pass


def read_table(path: str, sheet: Optional[str] = None) -> pd.DataFrame:
    if path.lower().endswith((".xlsx", ".xlsm", ".xls")):
        df = pd.read_excel(path, sheet_name=sheet or 0, dtype=str)
        df = df.fillna("")
    else:
        df = pd.read_csv(path, dtype=str, encoding="utf-8-sig", keep_default_na=False)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def resolve_columns(df: pd.DataFrame, aliases: Dict[str, Sequence[str]], required: Sequence[str]) -> Dict[str, str]:
    """Map canonical field -> actual column using case/space-insensitive alias lists; raise SchemaMismatch naming misses."""
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
    """Build one canonical event row. `event_id` defaults to {pid}:{etype}:{date}; pass event_id= to override."""
    if d is None:
        return None
    mo = months_between(as_of, d)
    ev = {c: "" for c in EVENT_COLUMNS}
    eid = kw.pop("event_id", None) or f"{pid}:{etype}:{d.isoformat()}"
    ev.update({"event_id": eid, "property_id": pid, "event_type": etype, "event_family": family_of(etype),
               "direction": direction_of(etype), "event_date": d.isoformat(), "months_out": mo, "urgency_band": urgency_band(mo),
               "basis": basis, "confidence": kw.pop("confidence", 1.0), "source": source, "source_vintage": vintage,
               "status": "PAST" if mo < 0 else "FUTURE", "event_date_quality": "declared_format"})
    ev.update({k: ("" if v is None else v) for k, v in kw.items()})
    return ev


def first_events(events: List[Dict[str, Any]], horizon_m: float, reg_horizon_m: float, helper_types=None):
    """(first_debt, first_reg, events_in_horizon). Helper deadlines (AGENCY_DEADLINE family, PRESERVATION_NOTICE_WINDOW)
    are never a property's first event and never enter events_in_horizon; STALE_CONTRACT_DATE rows are not first events."""
    helper = set(helper_types) if helper_types is not None else set(HELPER_EVENTS)
    live = [e for e in events if e["status"] not in ("REJECTED", "SUPPRESSED") and e["direction"] == "PRESSURE"
            and e["event_type"] not in helper and e.get("event_family") != "AGENCY_DEADLINE"]
    fresh = [e for e in live if e["status"] != "STALE_CONTRACT_DATE" and e.get("months_out") not in ("", None)]
    debt = [e for e in fresh if e["event_family"] == "DEBT" and 0 <= float(e["months_out"]) <= horizon_m]
    reg = [e for e in fresh if e["event_family"] == "REGULATORY" and 0 <= float(e["months_out"]) <= reg_horizon_m]
    fd = min(debt, key=lambda e: e["event_date"]) if debt else None
    fr = min(reg, key=lambda e: e["event_date"]) if reg else None
    inh = sorted([e for e in live if e.get("months_out") not in ("", None) and -12 <= float(e["months_out"]) <= max(horizon_m, reg_horizon_m)], key=lambda e: e["event_date"])
    return fd, fr, inh


EIH_KEYS = ("event_type", "event_date", "months_out", "basis", "confidence", "source", "verify_flag", "alt_dates", "window_start", "window_end", "direction", "status", "program", "detail")


def apply_first(lead: Dict[str, Any], fd, fr, inh) -> None:
    for prefix, e in (("first_debt", fd), ("first_reg", fr)):
        lead[f"{prefix}_event_type"] = e["event_type"] if e else ""
        lead[f"{prefix}_event_date"] = e["event_date"] if e else ""
        lead[f"{prefix}_months_out"] = e["months_out"] if e else ""
        lead[f"{prefix}_basis"] = e["basis"] if e else ""
        lead[f"{prefix}_source"] = e["source"] if e else ""
    lead["events_in_horizon"] = json.dumps([{k: e.get(k, "") for k in EIH_KEYS} for e in inh])


def write_outputs(out_dir: str, leads: List[Dict[str, Any]], events: List[Dict[str, Any]], summary: Dict[str, Any], prefix: str = "",
                  pii_scope: str = "organization") -> None:
    from .pii import apply_pii_scope
    os.makedirs(out_dir, exist_ok=True)
    extra = sorted({k for l in leads for k in l if k not in LEAD_COLUMNS})
    df = pd.DataFrame(leads, columns=LEAD_COLUMNS + extra)
    df, _log = apply_pii_scope(df, pii_scope)
    df.to_csv(os.path.join(out_dir, f"{prefix}leads.csv"), index=False)
    pd.DataFrame(events, columns=EVENT_COLUMNS).to_csv(os.path.join(out_dir, f"{prefix}events.csv"), index=False)
    with open(os.path.join(out_dir, f"{prefix}calendar_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, default=str)


def basis_breakdown(events: List[Dict[str, Any]]) -> Dict[str, int]:
    live = [e for e in events if e["status"] != "REJECTED" and e["event_type"] not in HELPER_EVENTS]
    return {b: sum(1 for e in live if e["basis"] == b) for b in ("RECORDED", "REPORTED", "DERIVED", "ESTIMATED", "PROXY")}
