"""Separate preservation, financial condition, evidence quality and readiness.

Financial thresholds must be supplied by the agency; no calibrated rating is
invented from missing statements. Observations are property/period snapshots.
"""
from datetime import date
import math

METRICS = ("dscr", "days_past_due", "occupancy", "reserve_funded_ratio")
GATES = ("authority_confirmed", "owner_engaged", "funding_identified", "documents_complete", "staff_capacity_confirmed")
AXES = ("preservation_urgency", "financial_risk", "data_confidence", "intervention_readiness")
FRONT = ["property_id", "property_name", *AXES, "preservation_reasons", "financial_reasons", "data_confidence_reasons",
         "readiness_reasons", "financial_data_status", "financial_policy_version", "financial_period_end", "financial_source",
         "readiness_reviewed_on", "readiness_source", "attention_lanes", "assessment_version"]
URGENT = {"OVERDUE", "CRITICAL", "URGENT", "APPROACHING"}


def financial_observations(rows, as_of):
    latest, history = {}, {}
    for r in rows:
        pid = str(r.get("property_id") or "").strip()
        observed = date.fromisoformat(r["period_end"])
        if not pid or not str(r.get("source") or "").strip():
            raise ValueError("financial observation requires property_id and source")
        data = {"property_id": pid, "period_end": observed.isoformat(), "source": r["source"]}
        for metric in METRICS:
            raw = r.get(metric)
            value = float(raw) if raw not in (None, "") else None
            if value is not None and (not math.isfinite(value) or (metric != "dscr" and value < 0) or (metric == "occupancy" and value > 1)):
                raise ValueError(f"invalid {metric} for {pid}")
            data[metric] = value
        key = (pid, observed)
        if key in history and history[key] != data:
            raise ValueError(f"conflicting financial period: {pid} {observed}")
        history[key] = data
        if observed <= as_of and (pid not in latest or observed.isoformat() > latest[pid]["period_end"]):
            latest[pid] = data
    return latest, list(history.values())


def readiness_observations(rows, as_of):
    latest, history = {}, {}
    for row in rows:
        pid = str(row.get("property_id") or "").strip()
        reviewed = date.fromisoformat(row["reviewed_on"])
        if not pid or not str(row.get("source") or "").strip():
            raise ValueError("readiness requires property_id, reviewed_on and source")
        r = {"property_id": pid, "reviewed_on": reviewed.isoformat(), "source": row["source"]}
        for key in GATES:
            raw = str(row[key] if row.get(key) is not None else "").strip().lower()
            if raw not in ("", "unknown", "true", "false", "yes", "no"):
                raise ValueError(f"invalid readiness gate {key}")
            r[key] = True if raw in ("true", "yes") else False if raw in ("false", "no") else None
        key = (pid, reviewed)
        if key in history and history[key] != r:
            raise ValueError(f"conflicting readiness review: {pid} {reviewed}")
        history[key] = r
        if reviewed <= as_of and (pid not in latest or r["reviewed_on"] > latest[pid]["reviewed_on"]):
            latest[pid] = r
    return latest, list(history.values())


def assess(lead, observation, as_of, policy=None, readiness=None):
    """Independent assessments; no arithmetic combines axes into an overall rating."""
    import json
    from .dates import parse_iso, months_between, urgency_band
    policy = policy or {}
    if policy and not str(policy.get("version") or "").strip():
        raise ValueError("financial policy requires a version")
    for key in ("max_age_days", "min_dscr", "max_days_past_due", "min_occupancy", "min_reserve_funded_ratio"):
        if key in policy and (not math.isfinite(float(policy[key])) or float(policy[key]) < 0):
            raise ValueError(f"invalid financial policy threshold: {key}")
    if float(policy.get("min_occupancy", 0)) > 1:
        raise ValueError("min_occupancy must be a fraction")
    cliff = parse_iso(lead.get("owner_cliff_date"))
    urgency = urgency_band(months_between(as_of, cliff)) if cliff else lead.get("owner_cliff_band") or "UNKNOWN"
    if urgency not in {"OVERDUE", "CRITICAL", "URGENT", "APPROACHING", "MONITOR", "SCHEDULED", "BEYOND"}:
        urgency = "UNKNOWN"
    preservation_reasons = [f"{lead.get('owner_cliff_type') or 'owner cliff'}: {cliff.isoformat()}" if cliff else "No dated owner cliff available"]
    if not cliff and urgency != "UNKNOWN":
        preservation_reasons.append("Existing calendar band retained; date requires verification")
    financial, freshness, reasons, breaches, missing = "UNKNOWN", "MISSING", [], [], []
    checks = (("dscr", "min_dscr", "below"), ("days_past_due", "max_days_past_due", "above"),
              ("occupancy", "min_occupancy", "below"), ("reserve_funded_ratio", "min_reserve_funded_ratio", "below"))
    if observation:
        age = (as_of-date.fromisoformat(observation["period_end"])).days
        freshness = "FUTURE" if age < 0 else "STALE" if age > float(policy.get("max_age_days", 365)) else "CURRENT"
        for metric, threshold, direction in checks:
            if observation.get(metric) is None:
                missing.append(metric)
            elif threshold in policy:
                v, t = float(observation[metric]), float(policy[threshold])
                if not math.isfinite(v):
                    raise ValueError(f"invalid {metric}")
                if (v < t if direction == "below" else v > t):
                    breaches.append({"metric": metric, "value": v, "threshold": t, "rule": threshold})
        if freshness == "CURRENT":
            if breaches:
                financial = "WATCH"
            elif not missing and all(t in policy for _, t, _ in checks):
                financial = "NO_CONFIGURED_BREACH"
        reasons.extend(f"{b['metric']}={b['value']} breaches {b['rule']}={b['threshold']}" for b in breaches)
        if missing:
            reasons.append("Missing metrics: " + ", ".join(missing))
        if freshness != "CURRENT":
            reasons.append(f"{freshness.lower()} observation; current financial risk remains UNKNOWN")
    else:
        missing = list(METRICS)
        reasons.append("No financial observation on or before the assessment date")
    absent_rules = [t for _, t, _ in checks if t not in policy]
    if absent_rules:
        reasons.append("Unconfigured thresholds: " + ", ".join(absent_rules))
    if financial == "NO_CONFIGURED_BREACH":
        reasons.append("All four configured thresholds evaluated on current data; no breach detected")
    # Legal/physical covenant status is context, not proof of payment default.
    cov = str(lead.get("covenant_status") or "unknown")
    confidence_reasons = []
    flags = str(lead.get("verify_flags") or "").strip()
    if flags:
        confidence_reasons.append("Source verification flags: " + flags)
    if not cliff:
        confidence_reasons.append("Preservation date missing")
    if freshness != "CURRENT" or missing:
        confidence_reasons.append("Financial evidence is missing, stale, future-dated or incomplete")
    if absent_rules:
        confidence_reasons.append("Financial assessment policy incomplete")
    preservation_basis = str(lead.get("first_reg_basis") or lead.get("our_maturity_basis") or lead.get("first_debt_basis") or "UNKNOWN")
    if preservation_basis in ("PROXY", "ESTIMATED", "UNKNOWN"):
        confidence_reasons.append("Preservation source basis: " + preservation_basis)
    confidence = "VERIFY" if confidence_reasons else "SOURCE_AVAILABLE"
    readiness_reasons, blocked, unknown = [], [], list(GATES)
    readiness_status = "UNASSESSED"
    if readiness:
        age = (as_of-date.fromisoformat(readiness["reviewed_on"])).days
        blocked = [k for k in GATES if readiness.get(k) is False]
        unknown = [k for k in GATES if readiness.get(k) is None]
        if age < 0 or age > 180:
            readiness_status = "REQUIRES_VERIFICATION"
            readiness_reasons.append("Readiness review is future-dated or older than 180 days")
        elif blocked:
            readiness_status = "BLOCKED"
        elif unknown:
            readiness_status = "NEEDS_INPUT"
        else:
            readiness_status = "READY_FOR_REVIEW"
        if blocked:
            readiness_reasons.append("Unmet gates: " + ", ".join(blocked))
        if unknown:
            readiness_reasons.append("Unknown gates: " + ", ".join(unknown))
    else:
        readiness_reasons.append("No dated staff readiness review supplied")
    verification = str(lead.get("verify_before_action") or "").strip()
    if flags or verification:
        readiness_reasons.append("Verify before action: " + (verification or flags))
        if readiness_status == "READY_FOR_REVIEW":
            readiness_status = "REQUIRES_VERIFICATION"
    if lead.get("mandate_fit") == "ineligible":
        readiness_status = "BLOCKED"
        readiness_reasons.append("Proposed intervention is ineligible under the supplied mandate")
    if not readiness_reasons:
        readiness_reasons.append("All five staff-reported gates met; independent action approval still required")
    lanes = []
    if urgency in URGENT:
        lanes.append("PRESERVATION")
    if financial == "WATCH":
        lanes.append("FINANCIAL")
    if confidence == "VERIFY":
        lanes.append("DATA_GAPS")
    if readiness_status != "READY_FOR_REVIEW":
        lanes.append("READINESS_GAPS")
    explanation = {
        "preservation": {"status": urgency, "reasons": preservation_reasons, "date": cliff.isoformat() if cliff else None},
        "financial": {"status": financial, "reasons": reasons, "breaches": breaches, "missing_metrics": missing,
                      "source": observation.get("source", "") if observation else "", "policy": policy},
        "confidence": {"status": confidence, "reasons": confidence_reasons, "source_basis": preservation_basis},
        "readiness": {"status": readiness_status, "reasons": readiness_reasons, "blocked_gates": blocked, "unknown_gates": unknown}}
    return {"property_id": lead["property_id"], "assessment_version": "four-dimensions-v1", "as_of": as_of.isoformat(),
            "preservation_urgency": urgency, "preservation_reasons": "; ".join(preservation_reasons),
            "financial_risk": financial, "financial_reasons": "; ".join(reasons), "financial_data_status": freshness,
            "financial_period_end": observation.get("period_end", "") if observation else "", "financial_source": observation.get("source", "") if observation else "",
            "financial_policy_version": policy.get("version") or "NOT_CONFIGURED", "covenant_status_context": cov,
            "data_confidence": confidence, "data_confidence_reasons": "; ".join(confidence_reasons),
            "intervention_readiness": readiness_status, "readiness_reasons": "; ".join(readiness_reasons),
            "readiness_reviewed_on": readiness.get("reviewed_on", "") if readiness else "", "readiness_source": readiness.get("source", "") if readiness else "",
            "attention_lanes": ";".join(lanes), "dimension_explanations_json": json.dumps(explanation, sort_keys=True)}


def apply_dimensions(frame, as_of, financial=None, policy=None, readiness=None):
    import pandas as pd
    rows = [dict(r, **assess(r, (financial or {}).get(str(r["property_id"])), as_of, policy,
                           (readiness or {}).get(str(r["property_id"])))) for r in frame.to_dict(orient="records")]
    if not rows:
        return frame.copy()
    out = pd.DataFrame(rows)
    order = {s: i for i, s in enumerate(("OVERDUE", "CRITICAL", "URGENT", "APPROACHING", "MONITOR", "SCHEDULED", "BEYOND", "UNKNOWN"))}
    out["_preservation_order"] = out["preservation_urgency"].map(order)
    out = out.sort_values(["_preservation_order", "property_id"]).drop(columns="_preservation_order").reset_index(drop=True)
    return out[[c for c in FRONT if c in out] + [c for c in out if c not in FRONT]]


def dimension_counts(rows):
    from collections import Counter
    return {axis: dict(Counter(r.get(axis) or "UNKNOWN" for r in rows)) for axis in AXES}
