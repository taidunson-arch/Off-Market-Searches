import json
from datetime import date
import pandas as pd
from plb.risk_dimensions import assess, financial_observations, readiness_observations, apply_dimensions, GATES

AS_OF = date(2026, 10, 4)
POLICY = {"version": "agency-test-v1", "min_dscr": 1.1, "max_days_past_due": 30, "min_occupancy": 0.9, "min_reserve_funded_ratio": 1}
LEAD = {"property_id": "p", "owner_cliff_date": "2027-01-01", "first_reg_basis": "RECORDED"}
FIN = {"property_id": "p", "source": "financial statement", "period_end": "2026-09-30", "dscr": 1.5, "days_past_due": 0, "occupancy": 0.98, "reserve_funded_ratio": 1}
READY = {"property_id": "p", "reviewed_on": "2026-10-01", "source": "staff review", **{gate: True for gate in GATES}}


def rejects(fn):
    try:
        fn()
    except ValueError:
        return
    raise AssertionError("invalid observation accepted")


def test_dimensions_urgent_preservation_survives_missing_financial_data_and_blocked_readiness():
    r = assess(LEAD, None, AS_OF, POLICY, dict(READY, funding_identified=False))
    assert r["preservation_urgency"] == "CRITICAL" and r["financial_risk"] == "UNKNOWN"
    assert r["intervention_readiness"] == "BLOCKED" and r["data_confidence"] == "VERIFY"
    assert {"PRESERVATION", "DATA_GAPS", "READINESS_GAPS"} <= set(r["attention_lanes"].split(";"))


def test_dimensions_financial_breach_survives_long_restriction_and_legacy_exclusion():
    r = assess(dict(LEAD, owner_cliff_date="2040-01-01", queue_band="EXCLUDED", intervention_score=0), dict(FIN, dscr=0.6), AS_OF, POLICY, READY)
    assert r["preservation_urgency"] == "BEYOND" and r["financial_risk"] == "WATCH"
    assert "FINANCIAL" in r["attention_lanes"] and "dscr" in r["financial_reasons"]


def test_dimensions_axes_do_not_offset_each_other_or_use_blended_scores():
    a = assess(LEAD, FIN, AS_OF, POLICY, READY)
    b = assess(dict(LEAD, intervention_score=100, queue_band="ESCALATE", units_at_risk=1000), dict(FIN, dscr=0.5), AS_OF, POLICY, READY)
    for key in ("preservation_urgency", "intervention_readiness", "data_confidence"):
        assert a[key] == b[key]
    assert a["financial_risk"] != b["financial_risk"]
    assert a["intervention_readiness"] == "READY_FOR_REVIEW"


def test_dimensions_missing_partial_stale_future_and_no_policy_never_healthy():
    for observation, policy in ((None, POLICY), (dict(FIN, dscr=None), POLICY), (dict(FIN, period_end="2020-01-01"), POLICY),
                                (dict(FIN, period_end="2027-01-01"), POLICY), (FIN, {})):
        assert assess(LEAD, observation, AS_OF, policy)["financial_risk"] == "UNKNOWN"
    stale = assess(LEAD, dict(FIN, period_end="2020-01-01", dscr=0.5), AS_OF, POLICY)
    assert stale["financial_risk"] == "UNKNOWN" and "dscr" in stale["financial_reasons"]
    assert assess(dict(LEAD, covenant_status="default"), None, AS_OF)["financial_risk"] == "UNKNOWN"


def test_dimensions_readiness_requires_explicit_fresh_gates_and_verification():
    assert assess(LEAD, FIN, AS_OF, POLICY)["intervention_readiness"] == "UNASSESSED"
    assert assess(LEAD, FIN, AS_OF, POLICY, dict(READY, documents_complete=None))["intervention_readiness"] == "NEEDS_INPUT"
    assert assess(LEAD, FIN, AS_OF, POLICY, dict(READY, reviewed_on="2025-01-01"))["intervention_readiness"] == "REQUIRES_VERIFICATION"
    assert assess(dict(LEAD, verify_flags="Confirm source"), FIN, AS_OF, POLICY, READY)["intervention_readiness"] == "REQUIRES_VERIFICATION"
    assert assess(dict(LEAD, mandate_fit="ineligible"), FIN, AS_OF, POLICY, READY)["intervention_readiness"] == "BLOCKED"


def test_dimensions_observation_selection_conflicts_and_boolean_gates():
    latest, history = readiness_observations([dict(READY, funding_identified=False), dict(READY, reviewed_on="2027-01-01")], AS_OF)
    assert latest["p"]["funding_identified"] is False and len(history) == 2
    rejects(lambda: readiness_observations([READY, dict(READY, funding_identified=False)], AS_OF))
    rejects(lambda: readiness_observations([dict(READY, authority_confirmed="maybe")], AS_OF))
    latest, _ = financial_observations([FIN, dict(FIN, period_end="2027-01-01", dscr=0.1)], AS_OF)
    assert latest["p"]["dscr"] == 1.5


def test_dimensions_explanations_and_sort_order_are_not_blended():
    frame = pd.DataFrame([dict(LEAD, property_id="later", owner_cliff_date="2035-01-01", intervention_score=100), dict(LEAD, property_id="soon", intervention_score=0)])
    out = apply_dimensions(frame, AS_OF)
    assert list(out["property_id"]) == ["soon", "later"]
    explanation = json.loads(out.iloc[0]["dimension_explanations_json"])
    assert set(explanation) == {"preservation", "financial", "confidence", "readiness"}
    assert all(explanation[axis]["reasons"] for axis in explanation)


def test_dimensions_monitor_band_and_policy_validation():
    assert assess(dict(LEAD, owner_cliff_date="2030-10-04"), FIN, AS_OF, POLICY)["preservation_urgency"] == "MONITOR"
    for policy in ({"min_dscr": 1}, {"version": "bad", "min_occupancy": 90}, {"version": "bad", "min_dscr": float("nan")}):
        rejects(lambda: assess(LEAD, FIN, AS_OF, policy))


def test_dimensions_scoring_cli_uses_financial_and_readiness_inputs():
    import tempfile
    from pathlib import Path
    from plb.adapters import blank_lead
    from plb.schema import EVENT_COLUMNS
    from score_preservation import main
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        lead = blank_lead(property_id="p", property_name="Fixture", asset_class="affordable_regulated", universe="our_book",
                          book_match="matched", owner_cliff_date="2040-01-01", owner_cliff_band="BEYOND", units=10)
        pd.DataFrame([lead]).to_csv(root/"leads.csv", index=False)
        pd.DataFrame(columns=EVENT_COLUMNS).to_csv(root/"events.csv", index=False)
        pd.DataFrame([dict(FIN, dscr=0.5)]).to_csv(root/"financial.csv", index=False)
        pd.DataFrame([READY]).to_csv(root/"readiness.csv", index=False)
        (root/"policy.json").write_text(json.dumps(POLICY), encoding="utf-8")
        main(["--leads", str(root/"leads.csv"), "--events", str(root/"events.csv"), "--as-of", "2026-10-04", "--mandate", "none",
              "--out", str(root/"leads_scored.csv"), "--financial-observations", str(root/"financial.csv"),
              "--financial-policy", str(root/"policy.json"), "--readiness-observations", str(root/"readiness.csv")])
        out = pd.read_csv(root/"leads_scored.csv").iloc[0]
        assert out["financial_risk"] == "WATCH" and out["financial_policy_version"] == POLICY["version"]
        assert out["readiness_source"] == READY["source"]
        attention = pd.read_csv(root/"financial_attention.csv")
        assert attention.iloc[0]["property_id"] == "p"


def test_dimensions_public_packet_keeps_axes_without_staff_source_notes():
    from plb.pii import apply_pii_scope
    row = assess(LEAD, FIN, AS_OF, POLICY, READY)
    row.update(financial_source="private-statement-reference", readiness_source="private-review-reference",
               financial_reasons="private-financial-note", readiness_reasons="private-staff-note")
    public, log = apply_pii_scope(pd.DataFrame([row]), "public_packet")
    assert {"preservation_urgency", "financial_risk", "data_confidence", "intervention_readiness", "attention_lanes"} <= set(public.columns)
    assert "private-" not in public.to_json()
    assert any(r["field"] == "financial_reasons" for r in log)
    assert row["financial_reasons"] == "private-financial-note"
