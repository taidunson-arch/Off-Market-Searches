import csv
import json
import tempfile
from datetime import date
from pathlib import Path
from plb.validation import AXES, RULES, measure, reconcile_positions, review_rules, rule_inventory, validate_package

AS_OF = date(2026, 10, 4)


def positions():
    return [{"instrument_id": "loan:1", "property_id": "p1", "book_kind": "loan", "agency_programs": "HOME", "public_upb": "100.01"},
            {"instrument_id": "loan:2", "property_id": "p2", "book_kind": "loan", "agency_programs": "HOME", "public_upb": "200.02"}]


def risks():
    return [dict(property_id="p1", as_of=AS_OF.isoformat(), preservation_urgency="CRITICAL", financial_risk="WATCH", data_confidence="VERIFY", intervention_readiness="BLOCKED"),
            dict(property_id="p2", as_of=AS_OF.isoformat(), preservation_urgency="BEYOND", financial_risk="NO_CONFIGURED_BREACH", data_confidence="SOURCE_AVAILABLE", intervention_readiness="READY_FOR_REVIEW")]


def labels():
    return [dict(property_id=pid, axis=axis, as_of=AS_OF.isoformat(), expected_attention=truth, reviewer="independent-reviewer",
                 reviewed_on=AS_OF.isoformat(), evidence_as_of=AS_OF.isoformat(), decision_reason="synthetic fixture decision", evidence_ref="fixture:decision")
            for pid, truth in (("p1", "true"), ("p2", "false")) for axis in AXES]


def reviews():
    return [dict(rule_id=key, bundle_sha256=key+"-fixture-hash", status="APPROVED", jurisdiction="fixture-jurisdiction",
                 effective_from="2026-01-01", effective_to="2026-12-31", reviewed_on=AS_OF.isoformat(), reviewer="fixture-reviewer", evidence_ref="fixture:policy") for key in RULES]


def rejects(fn):
    try:
        fn()
    except ValueError:
        return
    raise AssertionError("invalid data accepted")


def test_agency_validation_offsetting_balance_errors_do_not_reconcile():
    expected = positions()
    actual = [dict(expected[0], public_upb="110.01"), dict(expected[1], public_upb="190.02")]
    result = reconcile_positions(actual, expected)
    assert not result["passed"] and len(result["breaks"]) == 2
    assert result["rollups"][0]["actual_loan_upb_cents"] == result["rollups"][0]["expected_loan_upb_cents"]
    assert reconcile_positions(expected, expected)["passed"]


def test_agency_validation_unknown_duplicate_missing_and_invalid_balances():
    rows = positions()
    unknown = reconcile_positions([dict(rows[0], public_upb=""), rows[1]], rows)
    assert not unknown["passed"] and unknown["rollups"][0]["actual_loan_upb_cents"] is None
    assert not reconcile_positions(rows[:1], rows)["passed"]
    assert not reconcile_positions(rows, rows[:1])["passed"]
    rejects(lambda: reconcile_positions(rows + rows[:1], rows))
    rejects(lambda: reconcile_positions(rows, rows, float("inf")))
    for value in ("NaN", "Infinity", "-1", "1.001"):
        rejects(lambda: reconcile_positions([dict(rows[0], public_upb=value)], rows[:1]))


def test_agency_validation_grant_basis_and_program_are_separate_controls():
    rows = [{"instrument_id": "grant:1", "property_id": "p", "book_kind": "grant", "agency_programs": "HOME", "recapture_amount": "1000.25"}]
    r = reconcile_positions(rows, rows)
    assert r["passed"] and r["rollups"][0]["actual_grant_recapture_basis_cents"] == 100025
    assert not reconcile_positions([dict(rows[0], agency_programs="CDBG")], rows)["passed"]
    assert not reconcile_positions([dict(rows[0], recapture_amount="")], rows)["passed"]


def test_agency_validation_counts_unknown_positive_as_missed_risk():
    rows = risks()
    rows[0]["financial_risk"] = "UNKNOWN"
    rows[1]["financial_risk"] = "WATCH"
    r = measure(rows, labels(), AS_OF)["metrics"]["financial_risk"]
    assert r["abstained_positive"] == r["missed_risks"] == r["fp"] == 1
    assert r["recall"] == 0 and r["missed_risk_rate"] == r["false_alarm_rate"] == 1
    assert r["abstention_rate"] == 0.5 and r["review_coverage"] == 1
    assert r["missed_risk_rate_95_interval"][1] == 1


def test_agency_validation_unreviewed_records_and_undefined_rates_are_visible():
    r = measure(risks(), [], AS_OF)["metrics"]["financial_risk"]
    assert r["unreviewed_properties"] == 2 and r["reviewed"] == 0
    assert r["precision"] is r["recall"] is r["false_alarm_rate"] is None
    rejects(lambda: measure(risks(), labels() + labels()[:1], AS_OF))
    wrong = [dict(labels()[0], as_of="2025-10-04")]
    assert measure(risks(), wrong, AS_OF)["label_errors"]
    future = [dict(labels()[0], evidence_as_of="2027-10-04")]
    assert measure(risks(), future, AS_OF)["label_errors"]


def test_agency_validation_rule_hash_expiry_and_review_coverage():
    inv = [{"rule_id": key, "bundle_sha256": key+"-fixture-hash", "configured": True} for key in RULES]
    assert review_rules(inv, reviews(), AS_OF, "fixture-jurisdiction")["passed"]
    bad = reviews()
    bad[0]["bundle_sha256"] = "different"
    assert not review_rules(inv, bad, AS_OF, "fixture-jurisdiction")["passed"]
    bad[0] = dict(reviews()[0], effective_to="2025-01-01")
    assert not review_rules(inv, bad, AS_OF, "fixture-jurisdiction")["passed"]
    assert not review_rules(inv, reviews()[:-1], AS_OF, "fixture-jurisdiction")["passed"]


def write_csv(path, rows):
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def package_fixture(root):
    run = root/"run"
    run.mkdir()
    (run/"manifest.json").write_text(json.dumps({"status": "COMPLETE", "as_of_date": AS_OF.isoformat()}))
    write_csv(run/"instruments.csv", positions())
    write_csv(run/"risk_dimensions.csv", risks())
    (run/"rule_inventory.json").write_text(json.dumps([{"rule_id": k, "configured": True, "bundle_sha256": k+"-fixture-hash"} for k in RULES]))
    write_csv(root/"controls.csv", positions())
    write_csv(root/"decisions.csv", labels())
    write_csv(root/"reviews.csv", reviews())
    criterion = dict(minimum_reviewed=2, minimum_positive=1, minimum_negative=1, maximum_missed_risk_rate=0,
                     maximum_false_alarm_rate=0, maximum_abstention_rate=0)
    package = dict(agency="SYNTHETIC TEST ONLY", jurisdiction="fixture-jurisdiction", as_of=AS_OF.isoformat(), data_kind="synthetic",
        controls_csv="controls.csv", decisions_csv="decisions.csv", rule_reviews_csv="reviews.csv", control_source="fixture independent tape",
        control_reviewer="fixture-controller", control_evidence_ref="fixture:control", sampling_design="census", sampling_evidence_ref="fixture:sample",
        blind_review=True, blind_review_evidence_ref="fixture:blind-review", evaluation_split="holdout", tolerance_cents=0,
        acceptance_criteria={"version": "fixture-only", "reviewer": "fixture-policy", "evidence_ref": "fixture:criteria", "frozen_on": AS_OF.isoformat(),
                             **{axis: criterion for axis in AXES}})
    path = root/"package.json"
    path.write_text(json.dumps(package))
    return run, path, package


def test_agency_validation_synthetic_success_never_becomes_agency_acceptance():
    with tempfile.TemporaryDirectory() as tmp:
        run, path, _ = package_fixture(Path(tmp))
        report = validate_package(run, path)
        assert report["reconciliation"]["passed"] and report["rule_review"]["passed"]
        assert all(check["passed"] for check in report["acceptance_checks"])
        assert report["acceptance_status"] == "BLOCKED" and "real agency" in report["blockers"][0]
        assert len(report["input_sha256"]) == 8


def test_agency_validation_missing_assessments_and_targeted_samples_block_signoff():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        run, path, package = package_fixture(root)
        package.update(data_kind="real_agency", sampling_design="targeted")  # Tests the attestation gate, not a real book.
        path.write_text(json.dumps(package))
        write_csv(run/"risk_dimensions.csv", risks()[1:])
        report = validate_package(run, path)
        assert report["acceptance_status"] == "BLOCKED"
        assert any("missing or out-of-date risk" in b for b in report["blockers"])
        assert report["performance"]["metrics"]["financial_risk"]["missed_risks"] == 1


def test_agency_validation_rule_inventory_pins_runtime_configuration():
    scripts = Path(__file__).resolve().parents[1]
    pack = scripts.parent/"references/sources/oregon-portland"
    with tempfile.TemporaryDirectory() as tmp:
        before = rule_inventory(tmp, {"pack": str(pack)})
        financial = next(r for r in before if r["rule_id"] == "financial_thresholds")
        assert not financial["configured"]
        (Path(tmp)/"financial_policy.json").write_text('{"version":"fixture-v1"}')
        after = rule_inventory(tmp, {"pack": str(pack)})
        financial2 = next(r for r in after if r["rule_id"] == "financial_thresholds")
        assert financial2["configured"] and financial2["bundle_sha256"] != financial["bundle_sha256"]


def test_agency_validation_attestation_gate_and_missing_criteria_unit_test_only():
    # Deliberately exercise the declaration gate with synthetic files. This is not real-book validation.
    with tempfile.TemporaryDirectory() as tmp:
        run, path, package = package_fixture(Path(tmp))
        package["data_kind"] = "real_agency"
        path.write_text(json.dumps(package))
        report = validate_package(run, path)
        assert report["acceptance_status"] == "READY_FOR_AGENCY_SIGNOFF"
        assert "not agency approval" in report["limitations"][-1]
        package["acceptance_criteria"]["financial_risk"] = {}
        path.write_text(json.dumps(package))
        assert validate_package(run, path)["acceptance_status"] == "BLOCKED"


def test_agency_validation_copied_output_control_and_cli_cannot_claim_acceptance():
    import subprocess
    import sys
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        run, path, package = package_fixture(root)
        package.update(data_kind="real_agency", controls_csv="run/instruments.csv")
        path.write_text(json.dumps(package))
        report = validate_package(run, path)
        assert report["acceptance_status"] == "BLOCKED" and any("independent evidence" in b for b in report["blockers"])
        cli = Path(__file__).resolve().parents[1]/"validate_book.py"
        out = root/"report.json"
        result = subprocess.run([sys.executable, str(cli), "--run-dir", str(run), "--package", str(path), "--out", str(out)], capture_output=True, text=True)
        assert result.returncode == 1 and "BLOCKED" in result.stdout
        assert json.loads(out.read_text())["acceptance_status"] == "BLOCKED"


def test_agency_validation_invalid_attempt_replaces_prior_success_report():
    import subprocess
    import sys
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        run, path, package = package_fixture(root)
        output = root/"report.json"
        cli = Path(__file__).resolve().parents[1]/"validate_book.py"
        package["acceptance_criteria"]["financial_risk"]["maximum_false_alarm_rate"] = float("nan")
        for malformed in ('{"invalid"', '[]', json.dumps(package)):
            path.write_text(malformed)
            output.write_text('{"acceptance_status":"READY_FOR_AGENCY_SIGNOFF"}')
            result = subprocess.run([sys.executable, str(cli), "--run-dir", str(run), "--package", str(path), "--out", str(output)], capture_output=True, text=True)
            assert result.returncode == 2 and "INVALID_INPUT" in result.stdout
            assert json.loads(output.read_text())["acceptance_status"] == "INVALID_INPUT"
