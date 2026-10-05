"""Preserve individual agency positions before making property-level summaries.

Only financial and identity fields are serialized; no contact or free-text fields.
"""
import json
from .dates import parse_iso
from .recap_math import recapture_exposure

FIELDS = ("book_kind", "agency_loan_ids", "grant_ids", "asset_ids", "contract_ids", "agency_programs",
          "public_upb", "our_rate", "payment_type", "our_maturity", "our_maturity_basis", "affordability_end",
          "recapture_type", "recapture_method", "recapture_amount", "recapture_start", "recapture_end",
          "covenant_status", "senior_maturity", "senior_upb", "units_assisted", "source_vintages", "as_of_date")
ID_FIELD = {"loan": "agency_loan_ids", "grant": "grant_ids", "owned_asset": "asset_ids", "administered_contract": "contract_ids"}


def parse_instruments(value):
    if value is None or str(value).strip() in ("", "nan"):
        return []
    records = json.loads(value) if isinstance(value, str) else value
    if not isinstance(records, list) or any(not isinstance(r, dict) for r in records):
        raise ValueError("instruments_json must be an array of instrument records")
    return records


def collect_instruments(rows):
    result = {}
    for row in rows:
        records = parse_instruments(row.get("instruments_json")) or [{k: row.get(k, "") for k in FIELDS}]
        for record in records:
            r = {k: record.get(k, "") for k in FIELDS}
            kind = str(r["book_kind"])
            identifier = str(r.get(ID_FIELD.get(kind, "")) or "").strip()
            if not identifier or ";" in identifier:
                raise ValueError(f"individual {kind} instrument requires one stable identifier")
            key = f"{kind}:{identifier}"
            r["instrument_id"] = key
            if key in result and result[key] != r:
                raise ValueError(f"conflicting rows for instrument {key}; reconcile the extract")
            result[key] = r
    return [result[k] for k in sorted(result)]


def grant_exposure(records, as_of):
    total, flags, unknown = 0.0, [], False
    for r in records:
        raw = r.get("recapture_amount")
        amount = float(raw) if raw not in (None, "") else None
        method = r.get("recapture_method") or ("full" if amount is not None else "none")
        if method == "none" and r.get("recapture_type") not in (None, "", "none"):
            unknown = True
            flags.append(f"Missing recapture terms: {r.get('instrument_id')}")
            continue
        calc = recapture_exposure(amount, parse_iso(r.get("recapture_start")), parse_iso(r.get("recapture_end")), as_of, method)
        if calc["exposure"] is None:
            unknown = True
        else:
            total += calc["exposure"]
        if calc["flag"]:
            flags.append(f"{r.get('instrument_id')}: {calc['flag']}")
    return {"exposure": None if unknown else total, "flag": "; ".join(flags)}
