"""Separate preservation, financial condition, evidence quality and readiness.

Financial thresholds must be supplied by the agency; no calibrated rating is
invented from missing statements. Observations are property/period snapshots.
"""
from datetime import date
import math

METRICS = ("dscr", "days_past_due", "occupancy", "reserve_funded_ratio")


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


def assess(lead, observation, as_of, policy=None):
    policy = policy or {}
    if policy:
        if not str(policy.get("version") or "").strip():
            raise ValueError("financial policy requires a version")
        for key in ("max_age_days", "min_dscr", "max_days_past_due", "min_occupancy", "min_reserve_funded_ratio"):
            if key in policy and (not math.isfinite(float(policy[key])) or float(policy[key]) < 0):
                raise ValueError(f"invalid financial policy threshold: {key}")
        if float(policy.get("min_occupancy", 0)) > 1:
            raise ValueError("min_occupancy must be a fraction")
    reasons = []
    cov = str(lead.get("covenant_status") or "")
    financial = "DEFAULT" if cov == "default" else "WATCH" if cov == "watch" else "UNKNOWN"
    if cov in ("watch", "default"):
        reasons.append("agency covenant status: " + cov)
    freshness = "MISSING"
    if observation:
        age = (as_of-date.fromisoformat(observation["period_end"])).days
        freshness = "CURRENT" if age <= int(policy.get("max_age_days", 365)) else "STALE"
        checks = (("dscr", "min_dscr", lambda v,t: v < t), ("days_past_due", "max_days_past_due", lambda v,t: v > t),
                  ("occupancy", "min_occupancy", lambda v,t: v < t), ("reserve_funded_ratio", "min_reserve_funded_ratio", lambda v,t: v < t))
        evaluated = 0
        for metric, threshold, breach in checks:
            if observation.get(metric) is not None and threshold in policy:
                evaluated += 1
                if breach(observation[metric], float(policy[threshold])):
                    reasons.append(f"{metric}={observation[metric]} breaches {threshold}={policy[threshold]}")
        if len(reasons) > (1 if cov in ("watch", "default") else 0) and financial != "DEFAULT":
            financial = "WATCH"
        elif evaluated == len(METRICS) and freshness == "CURRENT" and financial == "UNKNOWN":
            financial = "NO_CONFIGURED_BREACH"
    flags = str(lead.get("verify_flags") or "").strip()
    confidence = "VERIFY" if flags or freshness != "CURRENT" else "SOURCE_AVAILABLE"
    readiness = "REQUIRES_VERIFICATION" if str(lead.get("verify_before_action") or "").strip() or flags else "STAFF_REVIEW"
    return {"property_id": lead["property_id"], "preservation_urgency": lead.get("owner_cliff_band") or "UNKNOWN",
            "financial_risk": financial, "financial_reasons": "; ".join(reasons), "financial_data_status": freshness,
            "financial_policy_version": policy.get("version") or "NOT_CONFIGURED", "data_confidence": confidence,
            "intervention_readiness": readiness, "as_of": as_of.isoformat()}
