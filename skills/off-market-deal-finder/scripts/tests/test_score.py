"""Scoring engine contract tests against references/scoring/*.json (the only rubric; a missing dir raises)."""
from __future__ import annotations

import json
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from omdf.scoring import load_scoring, referenced_event_types, score_lead, weights_sum  # noqa: E402
from omdf.schema import EVENT_TAXONOMY  # noqa: E402

AS_OF = date(2026, 10, 4)
TABLES, SHARED, SRC = load_scoring()


def _lead(**kw):
    base = {"property_id": "t1", "property_name": "Test", "asset_class": "market_rate_mf", "owner_type": "single_asset_llc", "units": "40",
            "programs": "", "status": "Active", "signals": "", "compliance_gates": "", "rehab_year": "", "first_debt_months_out": "", "first_reg_months_out": ""}
    base.update(kw)
    return base


def _ev(etype, d, basis="RECORDED", **kw):
    e = {"event_id": f"{etype}:{d}", "property_id": "t1", "event_type": etype, "event_date": d, "basis": basis, "source": "test", "status": "FUTURE"}
    e.update(kw)
    return e


def test_weights_sum_to_100_per_class():
    for cls, t in TABLES.items():
        assert weights_sum(t) == 100, f"{cls} weights sum {weights_sum(t)}"


def test_every_band_event_type_in_taxonomy():
    for cls, t in TABLES.items():
        for et in referenced_event_types(t):
            assert et in EVENT_TAXONOMY, f"{cls}: {et} not in Section 2.2 taxonomy"


def test_proxy_only_never_exceeds_c():
    lead = _lead(asset_class="affordable_regulated", owner_type="lihtc_partnership_forprofit_gp", first_debt_months_out="8")
    evs = [_ev("LOAN_MATURITY", "2027-06-01", "PROXY")]
    r = score_lead(lead, evs, "affordable_regulated", TABLES, SHARED, AS_OF)
    assert r["tier"] in ("C", "WATCH") and "cap:proxy-only" in r["signals"]
    # even with the strongest owner profile and a huge fake score the cap holds
    assert all(ev.get("basis") == "PROXY" for f in r["factors"] for ev in f["evidence"] if ev.get("event_type"))


def test_housing_authority_partnership_route_and_minus_20():
    lead = _lead(asset_class="affordable_regulated", owner_type="housing_authority")
    evs = [_ev("LIHTC_EXTENDED_USE_END", "2028-01-01", "REPORTED")]
    r = score_lead(lead, evs, "affordable_regulated", TABLES, SHARED, AS_OF)
    assert r["route"] == "partnership_preservation"
    prof = next(f for f in r["factors"] if f["name"] == "owner_sponsor_profile")
    assert any(ev["points"] == -20 for ev in prof["evidence"]) and prof["points"] == 0  # -20 then floor 0
    assert r["tier"] in ("B", "C", "WATCH")


def test_suppress_until_zeroes_debt_factors_only():
    lead = _lead(first_debt_months_out="8", refi_gap_pct="0.30", noi_source="tape")
    evs = [_ev("LOAN_MATURITY", "2027-06-01"), _ev("SUPPRESS_UNTIL", "2031-08-15", "DERIVED"), _ev("TAX_DELINQUENT_YEARS", "2026-05-16", value=3)]
    r = score_lead(lead, evs, "market_rate_mf", TABLES, SHARED, AS_OF)
    f = {x["name"]: x for x in r["factors"]}
    assert f["capital_stack_timing"]["points"] == 0 and f["refinance_gap_coverage"]["points"] == 0
    assert f["operating_regulatory_pressure"]["points"] > 0  # non-debt factor untouched
    assert r["suppression"]["suppress_until"] == "2031-08-15"


def test_nonprofit_gp_year15_zero_points_and_partnership_route():
    lead = _lead(asset_class="affordable_regulated", owner_type="lihtc_partnership_nonprofit_gp", programs="LIHTC_9")
    evs = [_ev("LIHTC_COMPLIANCE_END", "2028-06-30", "DERIVED")]
    r = score_lead(lead, evs, "affordable_regulated", TABLES, SHARED, AS_OF)
    timing = next(f for f in r["factors"] if f["name"] == "regulatory_event_timing")
    assert timing["points"] == 0 and r["route"] == "partnership_preservation"
    lead2 = dict(lead, owner_type="lihtc_partnership_forprofit_gp")
    r2 = score_lead(lead2, evs, "affordable_regulated", TABLES, SHARED, AS_OF)
    timing2 = next(f for f in r2["factors"] if f["name"] == "regulatory_event_timing")
    assert timing2["points"] == 20 * 0.8 and r2["route"] in ("acquisition", "watch")  # 26 pts -> WATCH tier, never partnership


def test_recorded_maturity_9mo_with_refi_gap_has_no_cap():
    """Spec acceptance as written ("reaches Tier A") is arithmetically unreachable: capital_stack_timing (25) +
    refinance_gap_coverage (20) cap at 45 < 70. The contract we enforce is that a single-family RECORDED lead is
    scored on its merits with no tier cap applied: 17 + 14 = 31 -> Tier C, and tier equals the score-derived tier."""
    lead = _lead(first_debt_months_out="9", refi_gap_pct="0.30", noi_source="tape", est_dscr_refi="1.3")
    evs = [_ev("LOAN_MATURITY", "2027-07-04")]
    r = score_lead(lead, evs, "market_rate_mf", TABLES, SHARED, AS_OF)
    assert r["motivation_score"] == 31.0 and r["tier"] == "C" and r["tier_caps"] == [] and r["route"] == "acquisition"


def test_stacked_recorded_market_rate_lead_reaches_tier_a():
    lead = _lead(first_debt_months_out="9", refi_gap_pct="0.30", est_dscr_refi="0.95", noi_source="tape", sponsor_loans_maturing_36mo="3")
    evs = [_ev("LOAN_MATURITY", "2027-07-04"), _ev("SPECIAL_SERVICING", "2026-08-01"), _ev("TAX_DELINQUENT_YEARS", "2026-05-16", value=3),
           _ev("PROBATE_FILED", "2026-07-01")]
    r = score_lead(lead, evs, "market_rate_mf", TABLES, SHARED, AS_OF)
    assert r["motivation_score"] >= 70 and r["tier"] == "A"


def test_in_development_and_on_market_excluded():
    r = score_lead(_lead(status="In Development"), [_ev("LOAN_MATURITY", "2027-07-04")], "market_rate_mf", TABLES, SHARED, AS_OF)
    assert r["route"] == "excluded" and r["tier"] == "EXCLUDED"
    r = score_lead(_lead(on_market="true"), [_ev("LOAN_MATURITY", "2027-07-04")], "market_rate_mf", TABLES, SHARED, AS_OF)
    assert r["route"] == "excluded"


def test_rofr_routes_partnership_and_bankruptcy_gates_counsel():
    lead = _lead(asset_class="affordable_regulated", owner_type="lihtc_partnership_forprofit_gp")
    r = score_lead(lead, [_ev("ROFR_RECORDED", "2026-03-01"), _ev("LIHTC_EXTENDED_USE_END", "2028-01-01", "REPORTED"), _ev("BANKRUPTCY_FILED", "2026-06-01", detail="ch11")],
                   "affordable_regulated", TABLES, SHARED, AS_OF)
    assert r["route"] == "partnership_preservation" and "rofr_encumbered" in r["signals"] and "counsel_only" in r["compliance_gates"]


def test_deal_size_multiplier_and_strict_filter():
    lead = _lead(units="3", first_debt_months_out="9", refi_gap_pct="0.30", noi_source="tape")
    evs = [_ev("LOAN_MATURITY", "2027-07-04")]
    r = score_lead(lead, evs, "market_rate_mf", TABLES, SHARED, AS_OF, unit_range=[5, None])
    assert any(m["id"] == "deal_size_fit" and m["factor"] == 0.6 for m in r["multipliers"])
    r = score_lead(lead, evs, "market_rate_mf", TABLES, SHARED, AS_OF, unit_range=[5, None], strict_size_fit=True)
    assert r["route"] == "excluded"


def test_ambiguous_flag_forces_040_multiplier():
    lead = _lead(asset_class="affordable_regulated", owner_type="lihtc_partnership_forprofit_gp", first_reg_months_out="20")
    evs = [_ev("LIHTC_EXTENDED_USE_END", "2028-06-01", "REPORTED", verify_flag="Verify — Ambiguous")]
    r = score_lead(lead, evs, "affordable_regulated", TABLES, SHARED, AS_OF)
    timing = next(f for f in r["factors"] if f["name"] == "regulatory_event_timing")
    assert timing["basis_multiplier"] == 0.4 and timing["points"] == 10.0


def test_sfr_nod_stage_and_equity():
    lead = _lead(asset_class="sfr_small_res", owner_type="individual_absentee", units="1", equity_cushion_pct="0.55", balance_basis="RECORDED")
    evs = [_ev("NOD_RECORDED", "2026-08-01"), _ev("PROBATE_FILED", "2026-07-15"), _ev("ABSENTEE_TIER", "2026-01-01", value="out_of_state")]
    r = score_lead(lead, evs, "sfr_small_res", TABLES, SHARED, AS_OF)
    f = {x["name"]: x for x in r["factors"]}
    assert f["time_pressure"]["points"] == 22  # NOD 64 days old
    assert f["equity"]["points"] == 20 and f["owner_profile"]["points"] == 13
    assert f["signal_stacking"]["points"] >= 15  # 3 families (+5 nod+probate combo, capped 20)
    assert r["tier"] in ("A", "B")


def test_missing_scoring_dir_raises_instead_of_falling_back():
    import tempfile
    try:
        load_scoring(tempfile.mkdtemp())
    except FileNotFoundError as exc:
        assert "no embedded fallback" in str(exc)
    else:
        raise AssertionError("load_scoring must fail loudly when the JSON rubric is absent")


def test_every_json_band_has_reading_and_lever_and_signal_or_event():
    for cls, t in TABLES.items():
        for f in t["factors"]:
            for b in list(f.get("bands", [])) + list(f.get("modifiers", [])):
                assert b.get("id") and ("reading" in b) and ("lever" in b), f"{cls}:{f['name']}:{b.get('id')}"
                assert b.get("event_type") or b.get("signal") or "event_present" in json.dumps(b.get("match", {})), f"{cls}:{f['name']}:{b.get('id')} has neither event_type nor signal"


def test_owner_types_exclude_routes_excluded_with_reason():
    lead = _lead(asset_class="affordable_regulated", owner_type="housing_authority")
    evs = [_ev("LIHTC_EXTENDED_USE_END", "2028-01-01", "REPORTED")]
    r = score_lead(lead, evs, "affordable_regulated", TABLES, SHARED, AS_OF, owner_types_exclude=["housing_authority"])
    assert r["route"] == "excluded" and r["tier"] == "EXCLUDED" and any("owner_types_exclude" in x for x in r["route_reasons"])
    r2 = score_lead(lead, evs, "affordable_regulated", TABLES, SHARED, AS_OF, owner_types_include=["lihtc_partnership_forprofit_gp"])
    assert r2["route"] == "excluded"


def test_query_type_hit_flags():
    lead = _lead(asset_class="affordable_regulated", owner_type="lihtc_partnership_forprofit_gp")
    reg_only = [_ev("LIHTC_EXTENDED_USE_END", "2028-01-01", "REPORTED")]
    r = score_lead(lead, reg_only, "affordable_regulated", TABLES, SHARED, AS_OF, query_type="maturity")
    assert r["query_hit"] is False
    r = score_lead(lead, reg_only, "affordable_regulated", TABLES, SHARED, AS_OF, query_type="regulatory_expiry")
    assert r["query_hit"] is True
    r = score_lead(lead, reg_only + [_ev("LOAN_MATURITY", "2029-01-01", "PROXY")], "affordable_regulated", TABLES, SHARED, AS_OF, query_type="maturity")
    assert r["query_hit"] is True and r["query_type"] == "maturity"


def test_buyer_profile_gates_and_signals():
    r = score_lead(_lead(asset_class="sfr_small_res", owner_type="individual_absentee", units="1"), [_ev("NOD_RECORDED", "2026-08-01")],
                   "sfr_small_res", TABLES, SHARED, AS_OF, buyer_profile="wholesaler")
    assert "wholesaler_registration" in r["compliance_gates"]
    r = score_lead(_lead(asset_class="affordable_regulated", owner_type="lihtc_partnership_forprofit_gp"), [_ev("LIHTC_EXTENDED_USE_END", "2028-01-01", "REPORTED")],
                   "affordable_regulated", TABLES, SHARED, AS_OF, buyer_profile="qualified_purchaser")
    assert "designee_strategy" in r["signals"]


def test_push_window_open_modifier_and_signal():
    lead = _lead(asset_class="affordable_regulated", owner_type="lihtc_partnership_forprofit_gp", programs="LIHTC_9", units="35")
    base = [_ev("LIHTC_EXTENDED_USE_END", "2029-06-01", "REPORTED")]
    win = _ev("PRESERVATION_NOTICE_WINDOW", "2026-06-01", "DERIVED", window_start="2026-06-01", window_end="2026-12-01")
    r0 = score_lead(lead, base, "affordable_regulated", TABLES, SHARED, AS_OF)
    r1 = score_lead(lead, base + [win], "affordable_regulated", TABLES, SHARED, AS_OF)
    f1 = next(f for f in r1["factors"] if f["name"] == "declared_intent_and_notice")
    assert f1["points"] == 4 and "push_window_open" in r1["signals"] and r1["motivation_score"] > r0["motivation_score"]
    # window already closed -> nothing
    past = _ev("PRESERVATION_NOTICE_WINDOW", "2025-01-01", "DERIVED", window_start="2025-01-01", window_end="2025-07-01")
    r2 = score_lead(lead, base + [past], "affordable_regulated", TABLES, SHARED, AS_OF)
    assert "push_window_open" not in r2["signals"]


def test_recent_rehab_penalty_fires_on_comma_formatted_year():
    lead = _lead(asset_class="affordable_regulated", owner_type="lihtc_partnership_forprofit_gp", rehab_year="2,021")
    evs = [_ev("LIHTC_EXTENDED_USE_END", "2028-01-01", "REPORTED")]
    r = score_lead(lead, evs, "affordable_regulated", TABLES, SHARED, AS_OF)
    assert any(p["id"] == "recent_rehab" and p["points"] == -15 for p in r["penalties"])
    r_old = score_lead(dict(lead, rehab_year="2,016"), evs, "affordable_regulated", TABLES, SHARED, AS_OF)
    assert not any(p["id"] == "recent_rehab" for p in r_old["penalties"])
