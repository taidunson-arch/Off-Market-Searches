"""Independent agency-book acceptance evidence. Never certifies an agency or legal rule."""
import csv
import hashlib
import json
import math
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

AXES = ("preservation_urgency", "financial_risk", "data_confidence", "intervention_readiness")
RULES = ("preservation_calendar", "financial_thresholds", "readiness_gates", "recapture_terms", "intervention_mandate")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def money(value):
    if value in (None, ""):
        return None
    try:
        amount = Decimal(str(value)) * 100
        if not amount.is_finite() or amount < 0 or amount != amount.to_integral_value():
            raise ValueError("amount must be finite, nonnegative and exact to cents")
        return int(amount)
    except InvalidOperation as exc:
        raise ValueError("invalid amount") from exc


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def rule_inventory(run_dir, cfg):
    """Fingerprint actual engine/configuration inputs for explicit human review."""
    scripts = Path(__file__).resolve().parents[1]
    pack = Path(cfg["pack"])
    scoring = Path(cfg.get("scoring_dir") or scripts.parent/"references"/"scoring")
    mandate = Path(cfg["mandate_file"]) if cfg.get("mandate_file") and cfg["mandate_file"] != "none" else pack/"mandate.json"
    bundles = {
        "preservation_calendar": [scripts/"plb/agency_calendar.py", scripts/"plb/dates.py", scripts/"plb/schema.py", pack/"market-params.json", pack/"legal-timelines.md"],
        "financial_thresholds": [scripts/"plb/risk_dimensions.py", Path(run_dir)/"financial_policy.json"],
        "readiness_gates": [scripts/"plb/risk_dimensions.py"],
        "recapture_terms": [scripts/"plb/recap_math.py", scripts/"plb/instruments.py", pack/"agency-profiles.yaml"],
        "intervention_mandate": [scripts/"plb/mandate.py", scripts/"plb/scoring.py", mandate, *sorted(scoring.glob("*.json"))],
    }
    result = []
    for rule_id, paths in bundles.items():
        artifacts = [{"name": str(p.relative_to(scripts.parent)) if p.is_relative_to(scripts.parent) else p.name,
                      "sha256": sha(p) if p.is_file() else None} for p in paths]
        configured = all(r["sha256"] for r in artifacts)
        if rule_id == "intervention_mandate" and cfg.get("mandate_file") == "none":
            configured = False
        digest = hashlib.sha256(json.dumps(artifacts, sort_keys=True).encode()).hexdigest()
        result.append({"rule_id": rule_id, "bundle_sha256": digest, "configured": bool(configured),
                       "artifacts": artifacts, "review_status": "NOT_REVIEWED"})
    return result


def _index(rows, key):
    result = {}
    for row in rows:
        value = str(row.get(key) or "").strip()
        if not value or value in result:
            raise ValueError(f"blank or duplicate {key}: {value}")
        result[value] = row
    return result


def reconcile_positions(actual_rows, control_rows, tolerance_cents=0):
    if not isinstance(tolerance_cents, int) or isinstance(tolerance_cents, bool) or tolerance_cents < 0:
        raise ValueError("tolerance_cents must be a nonnegative integer")
    actual, expected = _index(actual_rows, "instrument_id"), _index(control_rows, "instrument_id")
    breaks, rolls = [], {}
    for iid in sorted(set(actual) | set(expected)):
        a, e = actual.get(iid), expected.get(iid)
        if not a or not e:
            breaks.append({"instrument_id": iid, "issue": "missing_from_run" if not a else "missing_from_controls"})
        if a and e:
            for field in ("property_id", "book_kind", "agency_programs"):
                if not str(e.get(field) or "").strip() or a.get(field) != e.get(field):
                    breaks.append({"instrument_id": iid, "field": field, "issue": "identity_or_program_mismatch", "actual": a.get(field), "expected": e.get(field)})
            kind = e.get("book_kind")
            if kind not in ("loan", "grant", "owned_asset", "administered_contract"):
                breaks.append({"instrument_id": iid, "issue": "unsupported_kind"})
            field = "public_upb" if kind == "loan" else "recapture_amount" if kind == "grant" else None
            if field:
                av, ev = money(a.get(field)), money(e.get(field))
                if av is None or ev is None or abs(av-ev) > tolerance_cents:
                    breaks.append({"instrument_id": iid, "field": field, "issue": "unknown_balance" if av is None or ev is None else "balance_mismatch",
                                   "actual_cents": av, "expected_cents": ev, "difference_cents": av-ev if av is not None and ev is not None else None})
        for side, row in (("actual", a), ("expected", e)):
            if row is None:
                continue
            kind, program = row.get("book_kind", ""), row.get("agency_programs", "")
            for dimension, group in (("kind", kind), ("program", program)):
                key = (dimension, group)
                roll = rolls.setdefault(key, {"dimension": dimension, "group": group, "actual_count": 0, "expected_count": 0,
                    "actual_loan_upb_cents": 0, "expected_loan_upb_cents": 0, "actual_grant_recapture_basis_cents": 0,
                    "expected_grant_recapture_basis_cents": 0, "actual_unknown_amounts": 0, "expected_unknown_amounts": 0})
                roll[side+"_count"] += 1
                field = "public_upb" if kind == "loan" else "recapture_amount" if kind == "grant" else None
                if field:
                    value = money(row.get(field))
                    if value is None:
                        roll[side+"_unknown_amounts"] += 1
                    else:
                        roll[side+("_loan_upb_cents" if kind == "loan" else "_grant_recapture_basis_cents")] += value
    # Unknowns remain null in rollups instead of presenting incomplete sums as totals.
    for roll in rolls.values():
        for side in ("actual", "expected"):
            if roll[side+"_unknown_amounts"]:
                roll[side+"_loan_upb_cents"] = roll[side+"_grant_recapture_basis_cents"] = None
    return {"passed": bool(expected) and not breaks, "control_instruments": len(expected), "run_instruments": len(actual),
            "control_properties": len({r.get("property_id") for r in expected.values()}), "breaks": breaks,
            "rollups": list(rolls.values()), "tolerance_cents": tolerance_cents}


def review_rules(inventory, reviews, as_of, jurisdiction):
    inv, rev = _index(inventory, "rule_id"), _index(reviews, "rule_id")
    checks = []
    for rule_id in RULES:
        item, review = inv.get(rule_id, {}), rev.get(rule_id, {})
        reasons = []
        if not item or not item.get("configured"):
            reasons.append("runtime rule not configured or inventory missing")
        if review.get("status") != "APPROVED":
            reasons.append("no agency approval attestation")
        if not item.get("bundle_sha256") or review.get("bundle_sha256") != item.get("bundle_sha256"):
            reasons.append("review does not match runtime rule fingerprint")
        for field in ("reviewer", "evidence_ref", "reviewed_on", "effective_from", "effective_to"):
            if not str(review.get(field) or "").strip():
                reasons.append("missing " + field)
        if review.get("jurisdiction") != jurisdiction or not jurisdiction:
            reasons.append("jurisdiction mismatch")
        try:
            if not date.fromisoformat(review["effective_from"]) <= as_of <= date.fromisoformat(review["effective_to"]):
                reasons.append("review outside effective period")
            if date.fromisoformat(review["reviewed_on"]) > date.today():
                reasons.append("review dated in the future")
        except (KeyError, ValueError):
            reasons.append("invalid review dates")
        checks.append({"rule_id": rule_id, "passed": not reasons, "reasons": reasons, "reviewer": review.get("reviewer"), "evidence_ref": review.get("evidence_ref")})
    return {"passed": all(c["passed"] for c in checks), "checks": checks,
            "scope": "Matches supplied human review attestations; does not authenticate reviewers or verify legal conclusions"}


def prediction(axis, value):
    if axis == "preservation_urgency":
        return True if value in ("OVERDUE", "CRITICAL", "URGENT", "APPROACHING") else False if value in ("MONITOR", "SCHEDULED", "BEYOND") else None
    if axis == "financial_risk":
        return True if value in ("WATCH", "DEFAULT") else False if value == "NO_CONFIGURED_BREACH" else None
    if axis == "data_confidence":
        return True if value == "VERIFY" else False if value == "SOURCE_AVAILABLE" else None
    if axis == "intervention_readiness":
        return False if value == "READY_FOR_REVIEW" else True if value in ("BLOCKED", "UNASSESSED", "NEEDS_INPUT", "REQUIRES_VERIFICATION") else None
    raise ValueError("unsupported assessment axis")


def _rate(n, d):
    return n/d if d else None


def _interval(n, d):
    if not d:
        return None
    z, p = 1.96, n/d
    denom = 1+z*z/d
    center = (p+z*z/(2*d))/denom
    radius = z*math.sqrt(p*(1-p)/d+z*z/(4*d*d))/denom
    return [max(0, center-radius), min(1, center+radius)]


def measure(risk_rows, labels, as_of):
    risks = _index(risk_rows, "property_id")
    counts = {axis: dict(tp=0, fp=0, tn=0, fn=0, abstained_positive=0, abstained_negative=0) for axis in AXES}
    seen, errors, cases = set(), [], []
    for row in labels:
        pid, axis = row.get("property_id"), row.get("axis")
        key = (pid, axis)
        if key in seen:
            raise ValueError(f"duplicate adjudication {key}")
        seen.add(key)
        if axis not in AXES:
            raise ValueError("unsupported adjudicated axis")
        if pid not in risks or row.get("as_of") != as_of.isoformat():
            errors.append({"property_id": pid, "axis": axis, "issue": "unmatched property or as-of date"})
            continue
        for field in ("reviewer", "reviewed_on", "decision_reason", "evidence_ref", "evidence_as_of"):
            if not str(row.get(field) or "").strip():
                errors.append({"property_id": pid, "axis": axis, "issue": "missing " + field})
        if date.fromisoformat(row.get("reviewed_on", "")) > date.today():
            errors.append({"property_id": pid, "axis": axis, "issue": "review dated in the future"})
        if not row.get("evidence_as_of") or date.fromisoformat(row["evidence_as_of"]) > as_of:
            errors.append({"property_id": pid, "axis": axis, "issue": "missing or future evidence cutoff"})
        truth = str(row.get("expected_attention", "")).lower()
        if truth not in ("true", "false"):
            raise ValueError("expected_attention must be true or false")
        positive = truth == "true"
        predicted = prediction(axis, risks[pid].get(axis))
        outcome = ("abstained_positive" if positive else "abstained_negative") if predicted is None else "tp" if predicted and positive else "fp" if predicted else "fn" if positive else "tn"
        counts[axis][outcome] += 1
        if outcome != "tn":
            cases.append({"property_id": pid, "axis": axis, "outcome": outcome, "prediction": risks[pid].get(axis),
                          "expected_attention": positive, "decision_reason": row.get("decision_reason"), "evidence_ref": row.get("evidence_ref")})
    metrics = {}
    for axis, c in counts.items():
        total = sum(c.values())
        positives, negatives = c["tp"]+c["fn"]+c["abstained_positive"], c["tn"]+c["fp"]+c["abstained_negative"]
        missed = c["fn"]+c["abstained_positive"]
        metrics[axis] = {**c, "reviewed": total, "positives": positives, "negatives": negatives, "missed_risks": missed,
            "precision": _rate(c["tp"], c["tp"]+c["fp"]), "recall": _rate(c["tp"], positives),
            "missed_risk_rate": _rate(missed, positives), "false_alarm_rate": _rate(c["fp"], c["tn"]+c["fp"]),
            "abstention_rate": _rate(c["abstained_positive"]+c["abstained_negative"], total),
            "missed_risk_rate_95_interval": _interval(missed, positives),
            "false_alarm_rate_95_interval": _interval(c["fp"], c["tn"]+c["fp"]),
            "review_coverage": _rate(total, len(risks)), "unreviewed_properties": len(risks)-total}
    return {"metrics": metrics, "label_errors": errors, "case_results": cases,
            "scope": "Adjudicated sample only; unknown predictions on true risks count as missed risks"}


def validate_package(run_dir, package_path):
    run, package_path = Path(run_dir), Path(package_path)
    package = json.loads(package_path.read_text(encoding="utf-8"))
    blockers, hashes = [], {"package": sha(package_path)}
    def load(name, is_json=False, generated=False):
        path = run/name if generated else package_path.parent/str(package.get(name) or "__missing__")
        if not path.is_file():
            blockers.append("missing input: " + name)
            return {} if is_json else []
        if not generated and path.resolve().is_relative_to(run.resolve()):
            blockers.append("independent evidence must not be taken from generated run outputs: " + name)
        hashes[name] = sha(path)
        return json.loads(path.read_text(encoding="utf-8")) if is_json else read_csv(path)
    manifest = load("manifest.json", True, True)
    actual = load("instruments.csv", generated=True)
    risks = load("risk_dimensions.csv", generated=True)
    inventory = load("rule_inventory.json", True, True)
    controls, labels, reviews = load("controls_csv"), load("decisions_csv"), load("rule_reviews_csv")
    as_of = date.fromisoformat(package["as_of"])
    if manifest.get("status") != "COMPLETE" or manifest.get("as_of_date") != as_of.isoformat():
        blockers.append("run must be COMPLETE and match package as_of")
    for field in ("agency", "jurisdiction", "control_source", "control_reviewer", "control_evidence_ref", "sampling_evidence_ref", "blind_review_evidence_ref"):
        if not str(package.get(field) or "").strip():
            blockers.append("missing attestation: " + field)
    if package.get("data_kind") != "real_agency":
        blockers.append("real agency data has not been supplied/attested")
    if package.get("evaluation_split") != "holdout" or package.get("blind_review") is not True:
        blockers.append("independent blinded holdout review required")
    if package.get("sampling_design") not in ("census", "random"):
        blockers.append("representative census/random sampling declaration required; targeted samples are diagnostic only")
    balance = reconcile_positions(actual, controls, package.get("tolerance_cents", 0))
    rules = review_rules(inventory or [], reviews, as_of, package.get("jurisdiction"))
    risk_index = _index(risks, "property_id")
    control_properties = {r.get("property_id") for r in controls}
    book_risks = []
    for pid in sorted(control_properties):
        risk = risk_index.get(pid)
        if not risk or risk.get("as_of") != as_of.isoformat():
            blockers.append("missing or out-of-date risk assessment: " + str(pid))
            risk = {"property_id": pid}
        book_risks.append(risk)
    performance = measure(book_risks, labels, as_of)
    if not balance["passed"]:
        blockers.append("instrument/control reconciliation failed")
    if not rules["passed"]:
        blockers.append("required rules lack matching effective human review attestations")
    if performance["label_errors"]:
        blockers.append("decision review records are incomplete or out of scope")
    criteria = package.get("acceptance_criteria") or {}
    for field in ("version", "reviewer", "evidence_ref", "frozen_on"):
        if not str(criteria.get(field) or "").strip():
            blockers.append("acceptance criteria missing " + field)
    try:
        if date.fromisoformat(criteria["frozen_on"]) > as_of:
            blockers.append("acceptance criteria must be fixed by the evaluation as-of date")
    except (KeyError, ValueError):
        blockers.append("invalid acceptance criteria frozen_on")
    checks = []
    for axis, metrics in performance["metrics"].items():
        limits = criteria.get(axis) or {}
        for key, observed in (("minimum_reviewed", metrics["reviewed"]), ("minimum_positive", metrics["positives"]),
                              ("minimum_negative", metrics["negatives"]), ("maximum_missed_risk_rate", metrics["missed_risk_rate"]),
                              ("maximum_false_alarm_rate", metrics["false_alarm_rate"]), ("maximum_abstention_rate", metrics["abstention_rate"])):
            limit = limits.get(key)
            valid = isinstance(limit, (int, float)) and not isinstance(limit, bool) and math.isfinite(limit)
            valid = valid and (limit >= 1 and int(limit) == limit if key.startswith("minimum") else 0 <= limit <= 1)
            passed = bool(valid and observed is not None and (observed >= limit if key.startswith("minimum") else observed <= limit))
            checks.append({"axis": axis, "criterion": key, "limit": limit, "observed": observed, "passed": passed})
        if package.get("sampling_design") == "census" and metrics["unreviewed_properties"]:
            blockers.append(axis + ": census has unreviewed properties")
    if not all(r["passed"] for r in checks):
        blockers.append("sample size or measured error/abstention criteria not met")
    return {"report_version": 1, "acceptance_status": "BLOCKED" if blockers else "READY_FOR_AGENCY_SIGNOFF", "blockers": blockers,
            "agency": package.get("agency"), "as_of": as_of.isoformat(), "data_kind": package.get("data_kind"), "input_sha256": hashes,
            "reconciliation": balance, "rule_review": rules, "performance": performance, "acceptance_checks": checks,
            "limitations": ["Source/reviewer independence and sampling design are supplied attestations, not authenticated identities.",
                "Rates describe reviewed records; representativeness and selection bias require agency review.",
                "Intervals are descriptive binomial Wilson intervals, not guarantees or calibrated credit predictions.",
                "READY_FOR_AGENCY_SIGNOFF is not agency approval, legal certification, or deployment authorization."]}
