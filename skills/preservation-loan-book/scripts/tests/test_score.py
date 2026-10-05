"""Scoring engine contract tests against references/scoring/affordable_public_am.json + shared_adjustments.json (the only rubric;
a missing directory raises). Agency posture: nothing subtracts for a mission sponsor, housing authorities are partners, the eight
routes are the only intervention routes, A/B/C never appear."""
from __future__ import annotations

import json
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from plb.schema import EVENT_TAXONOMY, FLAG_BOOK_JOIN, FLAG_NOTICE_LOG, QUEUE_BANDS, ROUTES, agency_profile  # noqa: E402
from plb.scoring import load_scoring, referenced_event_types, score_lead, weights_sum  # noqa: E402

AS_OF = date(2026, 10, 4)
PACK = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "references", "sources", "oregon-portland"))
TABLES, SHARED, SRC = load_scoring()
HFA = agency_profile("hfa", PACK)
PHA = agency_profile("pha_am", PACK)
CITY = agency_profile("city_housing", PACK)


def _lead(**kw):
    base = {"property_id": "t1", "property_name": "Test", "asset_class": "affordable_regulated", "owner_type": "lihtc_partnership_forprofit_gp", "units": "40",
            "units_at_risk": "40", "restricted_units": "40", "programs": "LIHTC_9", "status": "Active", "signals": "", "compliance_gates": "", "rehab_year": "",
            "universe": "universe_not_held", "book_match": "not_in_book", "notice_status": "unknown", "hap_units_at_risk": "0", "psh_units_at_risk": "0"}
    base.update(kw)
    return base


def _ev(etype, d, basis="RECORDED", **kw):
    e = {"event_id": f"t1:{etype}:{d}", "property_id": "t1", "event_type": etype, "event_date": d, "basis": basis, "source": "test", "status": "FUTURE"}
    e.update(kw)
    return e


def _score(lead, evs, profile=HFA, **kw):
    return score_lead(lead, evs, "affordable_regulated", TABLES, SHARED, AS_OF, profile=profile, **kw)


def _factor(r, name):
    return next(f for f in r["factors"] if f["name"] == name)


def test_weights_sum_to_100_per_class():
    for cls, t in TABLES.items():
        assert weights_sum(t) == 100, f"{cls} weights sum {weights_sum(t)}"
    assert "affordable_public_am" in TABLES or "affordable_regulated" in TABLES


def test_every_band_event_type_in_taxonomy():
    for cls, t in TABLES.items():
        for et in referenced_event_types(t):
            assert et in EVENT_TAXONOMY, f"{cls}: {et} not in the taxonomy"


def test_every_band_has_reading_intervention_and_signal_or_event():
    for cls, t in TABLES.items():
        for f in t["factors"]:
            for b in list(f.get("bands", [])) + list(f.get("modifiers", [])):
                assert b.get("id") and "reading" in b and "intervention" in b and "lever" not in b, f"{cls}:{f['name']}:{b.get('id')}"
                assert b.get("event_type") or b.get("signal") or "event_present" in json.dumps(b.get("match", {})), f"{cls}:{f['name']}:{b.get('id')}"


def test_missing_scoring_dir_raises_instead_of_falling_back():
    import tempfile
    try:
        load_scoring(tempfile.mkdtemp())
    except FileNotFoundError as exc:
        assert "no embedded fallback" in str(exc)
    else:
        raise AssertionError("load_scoring must fail loudly when the JSON rubric is absent")


def test_abc_tiers_never_appear():
    r = _score(_lead(), [_ev("LIHTC_EXTENDED_USE_END", "2028-01-01", "REPORTED")])
    assert r["queue_band"] in QUEUE_BANDS and "tier" not in r and "motivation_score" not in r
    assert r["primary_route"] in ROUTES + ["none", "excluded"]


def test_proxy_only_capped_at_plan():
    lead = _lead(first_debt_months_out="8")
    r = _score(lead, [_ev("LOAN_MATURITY", "2027-06-01", "PROXY")])
    assert r["queue_band"] in ("PLAN", "WATCH", "EXCLUDED") and "cap:proxy-only" in r["signals"]
    assert all(ev.get("basis") == "PROXY" for f in r["factors"] for ev in f["evidence"] if ev.get("event_type"))


def test_suppress_until_zeroes_debt_factor_only():
    lead = _lead(universe="our_book", book_match="matched", public_upb="1000000")
    evs = [_ev("AGENCY_LOAN_MATURITY", "2027-06-01", source="agency_servicing"), _ev("SUPPRESS_UNTIL", "2031-08-15", "DERIVED"), _ev("REAC_SCORE", "2026-05-16", value=50)]
    r = _score(lead, evs)
    assert _factor(r, "our_capital_at_risk")["points"] == 0 and _factor(r, "physical_reac_occupancy")["points"] == 10
    assert r["suppression"]["suppress_until"] == "2031-08-15"


def test_ambiguous_flag_forces_040_multiplier():
    evs = [_ev("LIHTC_EXTENDED_USE_END", "2028-06-01", "REPORTED", verify_flag="Verify — Ambiguous")]
    f = _factor(_score(_lead(), evs), "restriction_hap_qc_clock")
    assert f["basis_multiplier"] == 0.4 and f["points"] == 8.0


def test_housing_authority_is_a_partner_sponsor_plus_and_no_cap():
    evs = [_ev("LIHTC_EXTENDED_USE_END", "2028-01-01", "REPORTED")]
    pha = _score(_lead(owner_type="housing_authority"), evs)
    fp = _score(_lead(owner_type="lihtc_partnership_forprofit_gp"), evs)
    assert _factor(pha, "sponsor_capacity")["points"] == 6 >= _factor(fp, "sponsor_capacity")["points"]
    assert pha["intervention_score"] >= fp["intervention_score"]
    routes = {pha["primary_route"]} | set(pha["secondary_routes"].split(";"))
    assert "ta_sponsor" in routes and pha["caps"] == [] and pha["queue_band"] != "EXCLUDED"
    assert not any(ev["points"] < 0 for f in pha["factors"] for ev in f["evidence"])


def test_nonprofit_year15_scores_clock_like_any_owner():
    evs = [_ev("LIHTC_COMPLIANCE_END", "2028-06-30", "DERIVED")]
    np_ = _score(_lead(owner_type="lihtc_partnership_nonprofit_gp"), evs)
    fp = _score(_lead(owner_type="lihtc_partnership_forprofit_gp"), evs)
    assert _factor(np_, "restriction_hap_qc_clock")["points"] == _factor(fp, "restriction_hap_qc_clock")["points"] == round(14 * 0.8, 1)
    assert "ta_sponsor" in ({np_["primary_route"]} | set(np_["secondary_routes"].split(";")))
    # for-profit GP at Year 15 is a preservation-risk plus, not a buy-side plus
    assert _factor(fp, "sponsor_capacity")["points"] == 6


def test_aggregator_gp_change_is_preservation_risk_plus_8():
    evs = [_ev("LIHTC_EXTENDED_USE_END", "2028-01-01", "REPORTED"), _ev("MANAGER_CHANGE", "2026-03-01", detail="aggregator")]
    r = _score(_lead(), evs)
    assert _factor(r, "sponsor_capacity")["points"] == 8


def test_window_open_scores_zero_prep_signal_secondary_route():
    base = [_ev("LIHTC_EXTENDED_USE_END", "2029-06-01", "REPORTED")]
    win = _ev("PRESERVATION_NOTICE_WINDOW", "2026-06-01", "DERIVED", window_start="2026-06-01", window_end="2026-12-01", detail="push_first_window; window_open_now")
    r = _score(_lead(units="35", units_at_risk="35", restricted_units="35"), base + [win])
    assert _factor(r, "declared_intent_vs_silence")["points"] == 0 and "push_window_open_prep" in r["signals"]
    assert r["primary_route"] != "notice_compliance" and "notice_compliance" in r["secondary_routes"].split(";")
    assert r["route_hits"].get("notice_compliance") == "push_window_prep"


def test_first_due_passed_unknown_scores_6_and_flags_notice_log():
    evs = [_ev("LIHTC_EXTENDED_USE_END", "2028-01-01", "REPORTED"),
           _ev("PRESERVATION_NOTICE_WINDOW", "2025-01-01", "DERIVED", window_start="2025-01-01", window_end="2025-07-01", detail="push_first_window"),
           _ev("PRESERVATION_NOTICE_WINDOW", "2025-07-01", "DERIVED", window_start="2025-07-01", window_end="2026-01-01", detail="push_second_window"),
           _ev("PUSH_FIRST_NOTICE_DUE", "2025-07-01", "DERIVED")]
    r = _score(_lead(notice_status="unknown"), evs)
    assert _factor(r, "declared_intent_vs_silence")["points"] == 6 and FLAG_NOTICE_LOG in r["verify_flags_added"]
    # no notice log loaded this run: confirm-the-log is a SECONDARY route (critic finding 25); the intent band and flag still fire
    assert r["primary_route"] != "notice_compliance" and "notice_compliance" in r["secondary_routes"].split(";")
    assert r["route_hits"].get("notice_compliance") == "push_window_prep"
    # with a notice log loaded (hfa with notice_log_status populated) the same silence becomes the primary compliance case
    prof = dict(HFA); prof["notice_log_loaded"] = True
    r2 = _score(_lead(notice_status="unknown"), evs, profile=prof)
    assert r2["primary_route"] == "notice_compliance" and r2["intervention"] == "push_window_prep" and "confirm" in r2["next_action"].lower()
    # a first-notice due date ten months past with notice_status unknown earns only the 6-point intent band: push_first_due_le_6 is bounded to [-1, 6]
    old = [_ev("LIHTC_EXTENDED_USE_END", "2028-06-01", "REPORTED"),
           _ev("PRESERVATION_NOTICE_WINDOW", "2025-06-01", "DERIVED", window_start="2025-06-01", window_end="2025-12-01", detail="push_first_window"),
           _ev("PRESERVATION_NOTICE_WINDOW", "2025-12-01", "DERIVED", window_start="2025-12-01", window_end="2026-06-01", detail="push_second_window"),
           _ev("PUSH_FIRST_NOTICE_DUE", "2025-12-01", "DERIVED")]
    r3 = _score(_lead(notice_status="unknown"), old)
    assert "push_first_due_le_6" not in _factor(r3, "restriction_hap_qc_clock")["matched_bands"]


def test_not_received_confirmed_past_due_is_a_breach_with_demand_letter():
    evs = [_ev("LIHTC_EXTENDED_USE_END", "2028-01-01", "REPORTED"),
           _ev("PRESERVATION_NOTICE_WINDOW", "2025-01-01", "DERIVED", window_start="2025-01-01", window_end="2025-07-01", detail="push_first_window"),
           _ev("NOTICE_COMPLIANCE_BREACH", "2025-07-01", "DERIVED", detail="push_first_due_passed; notice_status=not_received_confirmed")]
    r = _score(_lead(notice_status="not_received_confirmed"), evs)
    assert _factor(r, "declared_intent_vs_silence")["points"] == 12.0  # 15 x DERIVED 0.8
    assert r["primary_route"] == "notice_compliance" and r["intervention"] == "push_notice_demand_letter"
    assert "designee_rofr" in r["secondary_routes"].split(";")  # qualified purchaser: designee appointment on silence
    assert "ORS 456" in r["statutory_cite"] and "verify" in r["statutory_cite"].lower()


def test_hap_optout_notice_routes_optout_response_over_notice_compliance():
    evs = [_ev("HAP_EXPIRATION", "2027-06-01", "REPORTED", program="HAP", confidence=0.7, detail="term_unknown_annual_assumed"),
           _ev("PRESERVATION_NOTICE_RECEIVED", "2026-06-01", detail="hap_optout"),
           _ev("NOTICE_COMPLIANCE_BREACH", "2025-07-01", "DERIVED")]
    r = _score(_lead(programs="HAP;LIHTC_9", hap_units_at_risk="40", notice_status="received"), evs)
    assert r["primary_route"] == "optout_response" and "notice_compliance" in r["secondary_routes"].split(";")
    assert r["intervention"] == "optout_response_plan" and _factor(r, "declared_intent_vs_silence")["points"] == 15


def test_prac_row_never_routes_optout_response():
    evs = [_ev("HAP_EXPIRATION", "2027-03-01", "REPORTED", program="PRAC", confidence=0.7, detail="term_unknown_annual_assumed")]
    r = _score(_lead(programs="PRAC;HUD_202_811", owner_type="nonprofit", prac_units_at_risk="40"), evs)
    assert "optout_response" not in {r["primary_route"]} | set(r["secondary_routes"].split(";"))
    assert _factor(r, "restriction_hap_qc_clock")["matched_bands"] and "prac_le_24" in r["signals"]


def test_hap_inside_12_months_unknown_renewal_routes_optout_check():
    evs = [_ev("HAP_EXPIRATION", "2027-03-31", "REPORTED", program="HAP", confidence=0.7, detail="term_unknown_annual_assumed"),
           _ev("HAP_OPTOUT_NOTICE_DEADLINE", "2026-03-31", "DERIVED"), _ev("HAP_OPTOUT_PACKAGE_DUE", "2026-12-01", "DERIVED")]
    r = _score(_lead(programs="HAP;LIHTC_4", units="47", units_at_risk="47", restricted_units="47", hap_units_at_risk="47", owner_type="lihtc_partnership_forprofit_gp"), evs)
    assert r["primary_route"] == "optout_response" and r["intervention"] == "optout_tenant_notice_check"
    assert "optout_notice_deadline_passed_unconfirmed" in r["signals"] and "Verify — CA Log" in r["verify_flags_added"]
    assert r["agency_action_date_override"] == "2026-12-01"
    clock = _factor(r, "restriction_hap_qc_clock")
    assert abs(clock["points"] - (18 * 0.7 + 2 * 0.7 + 3) * 0.9) < 0.11  # (hap_le_24 + annual-renewal modifier, both x0.70 confidence, + package-due modifier) x REPORTED 0.90


def test_units_factor_scales_with_units_at_risk_and_governing_basis():
    def pts(units, when):
        lead = _lead(units=str(units), units_at_risk=str(units), restricted_units=str(units))
        return _factor(_score(lead, [_ev("LIHTC_EXTENDED_USE_END", when, "REPORTED")]), "units_households_at_risk")["points"]
    assert pts(8, "2029-04-01") == round(8 * 0.9, 1)
    assert pts(120, "2029-04-01") == 22.5          # 25 x REPORTED 0.90; 30 months out
    assert pts(120, "2034-04-01") == 0             # 90 months out: beyond the 60-month window, units stay in Board_Totals only


def test_unmatched_expected_book_join_scores_zero_capital_with_watch_and_flag():
    lead = _lead(universe="universe_not_held", book_match="unmatched_expected", ohcs_funded="true")
    r = _score(lead, [_ev("LIHTC_EXTENDED_USE_END", "2028-01-01", "REPORTED"), _ev("AGENCY_LOAN_MATURITY", "2027-06-01", source="agency_servicing")])
    cap = _factor(r, "our_capital_at_risk")
    assert cap["points"] == 0 and cap["factor_status"] == "WATCH" and FLAG_BOOK_JOIN in r["verify_flags_added"]
    assert r["queue_band"] != "EXCLUDED" and r["caps"] == []
    absent = _score(_lead(book_match="book_absent"), [_ev("LIHTC_EXTENDED_USE_END", "2028-01-01", "REPORTED")])
    assert absent["verify_flags_added"] == [] and _factor(absent, "our_capital_at_risk")["factor_status"] != "WATCH"


def test_mandate_ineligible_blocks_nofa_offer_only():
    mandate = {"products": [{"product_id": "hap_only", "status": "open", "eligible_programs": ["HAP"], "min_units": 5}]}
    r = _score(_lead(), [_ev("LIHTC_EXTENDED_USE_END", "2028-01-01", "REPORTED")], mandate=mandate)
    assert r["mandate_fit"] == "ineligible" and r["mandate_ineligible_reason"] and "nofa_offer" not in {r["primary_route"]} | set(r["secondary_routes"].split(";"))
    assert r["queue_band"] != "EXCLUDED" and r["exclusion_reason"] == ""
    assert all(m.get("id") != "mission_fit_affordable" for f in r["factors"] for m in f["post_multipliers"])
    ok = _score(_lead(programs="HAP;LIHTC_9"), [_ev("LIHTC_EXTENDED_USE_END", "2028-01-01", "REPORTED")], mandate=mandate)
    assert ok["mandate_fit"] == "eligible" and "nofa_offer" in {ok["primary_route"]} | set(ok["secondary_routes"].split(";"))


def test_no_rule_hit_is_none_not_excluded_and_no_cliff_is_excluded():
    quiet = _score(_lead(universe="our_book", book_match="matched", public_upb="900000"), [_ev("AGENCY_LOAN_MATURITY", "2033-06-01", source="agency_servicing")])
    assert quiet["primary_route"] == "none" and quiet["queue_band"] == "WATCH" and quiet["exclusion_reason"] == ""
    far = _score(_lead(), [_ev("LIHTC_EXTENDED_USE_END", "2040-01-01", "REPORTED")])
    assert far["queue_band"] == "EXCLUDED" and far["primary_route"] == "excluded" and far["exclusion_reason"] == "no_dated_cliff_in_horizon"
    dev = _score(_lead(status="In Development"), [_ev("LIHTC_EXTENDED_USE_END", "2028-01-01", "REPORTED")])
    assert dev["exclusion_reason"] == "in_development"


def test_recap_status_closed_halves_clock_and_intent_only():
    evs = [_ev("LIHTC_EXTENDED_USE_END", "2028-01-01", "REPORTED")]
    r = _score(_lead(recap_status="closed", recap_evidence_basis="RECORDED"), evs)
    assert _factor(r, "restriction_hap_qc_clock")["points"] == 9.0  # 20 x 0.9 x 0.5
    assert _factor(r, "units_households_at_risk")["points"] == round(14 * 0.9, 1)  # units untouched


def test_covenant_default_does_not_decay_and_recent_rehab_applied_once():
    lead = _lead(universe="our_book", book_match="matched", public_upb="700000", rehab_year="2,021")
    r = _score(lead, [_ev("COVENANT_DEFAULT", "2025-08-30", source="agency_servicing"), _ev("REAC_SCORE", "2026-04-12", "REPORTED", value=54)])
    assert _factor(r, "our_capital_at_risk")["points"] == 15
    assert _factor(r, "physical_reac_occupancy")["points"] == 5 and "penalties" not in r  # 10 - 5, only in the physical factor
    assert r["primary_route"] == "recap_committee"


def test_self_owned_pha_routes_repositioning_never_notice_compliance():
    lead = _lead(owner_type="self_owned", universe="our_book", book_match="self_owned", owner_name="Home Forward", units="158", units_at_risk="158", restricted_units="158",
                 notice_status="unknown", book_kind="owned_asset")
    evs = [_ev("AFFORDABILITY_PERIOD_END", "2028-01-01", source="agency_servicing"),
           _ev("PRESERVATION_NOTICE_WINDOW", "2025-01-01", "DERIVED", window_start="2025-01-01", window_end="2025-07-01", detail="push_first_window")]
    r = _score(lead, evs, profile=PHA)
    assert r["primary_route"] == "recap_committee" and r["intervention"] == "pha_repositioning"
    assert "notice_compliance" not in r["secondary_routes"] and "designee_rofr" not in r["secondary_routes"]
    assert _factor(r, "sponsor_capacity")["points"] == 6 and r["caps"] == []


def test_qc_admin_only_for_recorded_request_and_only_when_profile_administers_qc():
    evs = [_ev("QC_ELIGIBILITY", "2026-03-15", detail="requested; agency_loan_id=L-1", status="requested"), _ev("QC_RESPONSE_DUE", "2027-03-15", "DERIVED"),
           _ev("LIHTC_EXTENDED_USE_END", "2045-01-01", "REPORTED")]
    lead = _lead(universe="our_book", book_match="matched", public_upb="1500000", qc_status="requested", qc_waived="false")
    r = _score(lead, evs)
    assert r["primary_route"] == "qc_admin" and _factor(r, "declared_intent_vs_silence")["points"] == 13
    assert "IRC 42" in r["statutory_cite"]
    city = _score(dict(lead, owner_type="nonprofit"), evs, profile=CITY)
    assert city["primary_route"] != "qc_admin" and city["route_hits"].get("ta_sponsor") == "qc_coordination_with_hfa"
    waived = _score(dict(lead, qc_waived="true"), [_ev("QC_REQUEST_INELIGIBLE", "2026-03-15", detail="qc_waived"), _ev("LIHTC_EXTENDED_USE_END", "2045-01-01", "REPORTED")])
    assert waived["route_hits"].get("qc_admin") == "qc_waiver_acknowledgement"


def test_precedence_order_and_sentinels():
    assert ROUTES == ["optout_response", "notice_compliance", "qc_admin", "designee_rofr", "recap_committee", "servicing_watch", "nofa_offer", "ta_sponsor"]
    table = TABLES.get("affordable_public_am") or TABLES["affordable_regulated"]
    assert table["routes"]["precedence"] == ROUTES and table["routes"]["sentinels"] == ["none", "excluded"]


def test_out_of_state_modifier_ignored_for_mission_sponsor():
    evs = [_ev("LIHTC_EXTENDED_USE_END", "2028-01-01", "REPORTED")]
    np_ = _score(_lead(owner_type="nonprofit", out_of_state_sponsor="true"), evs)
    fp = _score(_lead(owner_type="lihtc_partnership_forprofit_gp", out_of_state_sponsor="true"), evs + [_ev("LIHTC_COMPLIANCE_END", "2027-06-01", "DERIVED")])
    assert _factor(np_, "sponsor_capacity")["points"] == 6 and _factor(fp, "sponsor_capacity")["points"] == 10


def test_owner_types_exclude_and_rofr_gates():
    evs = [_ev("ROFR_RECORDED", "2026-03-01"), _ev("LIHTC_EXTENDED_USE_END", "2028-01-01", "REPORTED"), _ev("BANKRUPTCY_FILED", "2026-06-01", detail="ch11")]
    r = _score(_lead(), evs)
    assert "designee_rofr" in {r["primary_route"]} | set(r["secondary_routes"].split(";")) and "counsel_only" in r["compliance_gates"]
    assert _factor(r, "declared_intent_vs_silence")["points"] == 8
    ex = _score(_lead(owner_type="institutional"), evs, owner_types_exclude=["institutional"])
    assert ex["primary_route"] == "excluded" and ex["queue_band"] == "EXCLUDED"


def test_basis_arithmetic_powell_style_hap_clock():
    """One rule (pipeline-contract Section 11): base-band take + modifiers, event confidence scales every band or modifier the event
    matched, then the min BASE-band basis multiplier. Powell Plaza I: (18 x 0.70 + 2 x 0.70 + 3) x 0.90 = 15.3 of 20."""
    evs = [_ev("HAP_EXPIRATION", "2027-03-31", "REPORTED", program="HAP", detail="term_unknown_annual_assumed", confidence="0.7"),
           _ev("HAP_OPTOUT_PACKAGE_DUE", "2026-12-01", "DERIVED", program="HAP"),
           _ev("LIHTC_EXTENDED_USE_END", "2035-01-01", "REPORTED")]
    r = _score(_lead(programs="LIHTC_9;HAP", units="47", units_at_risk="47", restricted_units="47", hap_units_at_risk="47"), evs)
    f = _factor(r, "restriction_hap_qc_clock")
    assert f["basis_multiplier"] == 0.9 and abs(f["points_raw"] - 17.0) < 0.01 and abs(f["points"] - 15.3) < 0.01
    assert {"hap_le_24", "hap_annual_renewal", "hap_optout_package_due_le_6"} <= set(f["matched_bands"])
