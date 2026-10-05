"""Agency calendar derivations: withdrawal anchor (restriction ends only; annual HAP excluded), both PuSH windows and the PUSH_*_DUE
dates, records request only after notice, ROFR match from the mailing date, QC one-year clock, stale HAP dates emit no deadlines,
NOTICE_COMPLIANCE_BREACH only on not_received_confirmed, a META row for every AGENCY_DEADLINE type."""
from __future__ import annotations

import os
import sys
from datetime import date

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from plb import agency_calendar as AC  # noqa: E402
from plb.schema import AGENCY_ACTION_EVENTS, EVENT_COLUMNS, LEAD_COLUMNS, agency_profile, load_market_params  # noqa: E402
from query_calendar import summarize  # noqa: E402

AS_OF = date(2026, 10, 4)
PACK = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "references", "sources", "oregon-portland"))
PARAMS = load_market_params(PACK)
HFA = agency_profile("hfa", PACK)


def _lead(pid, **kw):
    base = {c: "" for c in LEAD_COLUMNS}
    base.update({"property_id": pid, "property_name": pid, "units": "35", "programs": "LIHTC_9", "notice_status": "unknown", "book_match": "not_in_book", "signals": "", "verify_flags": ""})
    base.update(kw)
    return base


def _ev(pid, et, d, basis="REPORTED", **kw):
    e = {c: "" for c in EVENT_COLUMNS}
    e.update({"event_id": f"{pid}:{et}:{d}", "property_id": pid, "event_type": et, "event_family": AC.derive.__globals__["family_of"](et) if "family_of" in AC.derive.__globals__ else "",
              "direction": "PRESSURE", "event_date": d, "basis": basis, "confidence": "1.0", "source": "test", "status": "FUTURE" if d >= AS_OF.isoformat() else "PAST"})
    e.update(kw)
    return e


def _derive(leads, events, profile=HFA):
    from plb.schema import family_of
    for e in events:
        e["event_family"] = e["event_family"] or family_of(e["event_type"])
    return AC.derive(pd.DataFrame(leads).astype(object), pd.DataFrame(events).astype(object), AS_OF, PARAMS, profile, 120)


def test_village_garden_windows_and_due_dates_no_records_request_before_notice():
    leads, events = _derive([_lead("vg", units="35", programs="OTHER_OHCS")], [_ev("vg", "SOFT_PROGRAM_END", "2029-06-01", program="OTHER_OHCS"), _ev("vg", "REGULATORY_LATEST_END", "2029-06-01")])
    r = leads.iloc[0]
    assert r["withdrawal_anchor_date"] == "2029-06-01" and r["push_anchor_source"] == "restriction_end" and r["notice_window_state"] == "open_first"
    by = {e["event_type"]: e for e in events.to_dict(orient="records")}
    assert by["PUSH_WINDOW_PREP"]["event_date"] == "2026-06-01" and by["PUSH_FIRST_NOTICE_DUE"]["event_date"] == "2026-12-01" and by["PUSH_SECOND_NOTICE_DUE"]["event_date"] == "2027-06-01"
    wins = events[events["event_type"] == "PRESERVATION_NOTICE_WINDOW"]
    assert len(wins) == 2 and set(wins["window_start"]) == {"2026-06-01", "2026-12-01"} and "window_open_now" in " ".join(wins["detail"])
    assert "RECORDS_REQUEST_DUE" not in by and "NOTICE_COMPLIANCE_BREACH" not in by
    assert "push_window_open_prep" in r["signals"] and r["agency_action_type"] == "PUSH_WINDOW_PREP" and r["owner_cliff_type"] == "SOFT_PROGRAM_END"
    assert r["action_band"] == "OVERDUE" and r["owner_cliff_band"] == "APPROACHING"


def test_annual_hap_does_not_anchor_windows_and_emits_optout_clocks_only():
    leads, events = _derive([_lead("hap", units="30", programs="HAP", hud_contract="Housing Assistance Payment")],
                            [_ev("hap", "HAP_EXPIRATION", "2027-06-04", program="HAP", detail="term_unknown_annual_assumed", confidence="0.7"), _ev("hap", "REGULATORY_LATEST_END", "2027-06-04")])
    types = set(events["event_type"])
    assert "PRESERVATION_NOTICE_WINDOW" not in types and "PUSH_FIRST_NOTICE_DUE" not in types and "NOTICE_COMPLIANCE_BREACH" not in types
    by = {e["event_type"]: e for e in events.to_dict(orient="records")}
    assert by["HAP_OPTOUT_NOTICE_DEADLINE"]["event_date"] == "2026-06-04" and by["HAP_OPTOUT_PACKAGE_DUE"]["event_date"] == "2027-02-04"
    assert leads.iloc[0]["withdrawal_anchor_date"] == "" and leads.iloc[0]["push_anchor_source"] == "none"
    # an opt-out notice turns the HAP date into a withdrawal anchor
    leads2, events2 = _derive([_lead("h2", units="30", programs="HAP")], [_ev("h2", "HAP_EXPIRATION", "2029-06-04", program="HAP"), _ev("h2", "PRESERVATION_NOTICE_RECEIVED", "2026-09-01", "RECORDED", detail="hap_optout")])
    assert leads2.iloc[0]["push_anchor_source"] == "hap_nonrenewal_signal" and "RECORDS_REQUEST_DUE" in set(events2["event_type"])
    assert events2[events2["event_type"] == "RECORDS_REQUEST_DUE"].iloc[0]["event_date"] == "2026-09-11"


def test_stale_hap_date_flagged_no_deadlines_not_overdue():
    leads, events = _derive([_lead("st", units="50", programs="HAP")], [_ev("st", "HAP_EXPIRATION", "2024-09-30", program="HAP", detail="term_unknown_annual_assumed"), _ev("st", "REGULATORY_LATEST_END", "2024-09-30")])
    hap = events[events["event_type"] == "HAP_EXPIRATION"].iloc[0]
    assert hap["status"] == "STALE_CONTRACT_DATE" and hap["verify_flag"] == "Verify — Stale Contract Date"
    assert not set(events["event_type"]) & AGENCY_ACTION_EVENTS
    r = leads.iloc[0]
    assert "hap_date_stale" in r["signals"] and r["next_expected_expiration"] == "2027-09-30" and r["owner_cliff_type"] == "" and r["owner_cliff_band"] == ""
    assert leads.attrs["stale_contract_dates"] == 1


def test_breach_only_when_not_received_confirmed_past_first_due():
    base = [_ev("b", "LIHTC_EXTENDED_USE_END", "2028-01-01", program="LIHTC_9")]
    unknown, ev_u = _derive([_lead("b", notice_status="unknown")], [dict(e) for e in base])
    assert unknown.iloc[0]["notice_window_state"] == "closed_first_due" and "NOTICE_COMPLIANCE_BREACH" not in set(ev_u["event_type"])
    confirmed, ev_c = _derive([_lead("b", notice_status="not_received_confirmed")], [dict(e) for e in base])
    br = ev_c[ev_c["event_type"] == "NOTICE_COMPLIANCE_BREACH"]
    assert len(br) == 1 and br.iloc[0]["event_date"] == "2025-07-01" and br.iloc[0]["basis"] == "DERIVED" and confirmed.attrs["notice_compliance_breaches"] == 1
    received, ev_r = _derive([_lead("b", notice_status="unknown")], [dict(e) for e in base] + [_ev("b", "PRESERVATION_NOTICE_RECEIVED", "2025-06-15", "RECORDED", detail="push_first")])
    assert received.iloc[0]["notice_status"] == "received" and "NOTICE_COMPLIANCE_BREACH" not in set(ev_r["event_type"])
    assert ev_r[ev_r["event_type"] == "RECORDS_REQUEST_DUE"].iloc[0]["event_date"] == "2025-06-25"


def test_push_gates_units_programs_and_profile():
    small, ev_s = _derive([_lead("s", units="4", programs="LIHTC_9")], [_ev("s", "LIHTC_EXTENDED_USE_END", "2029-06-01")])
    assert "PRESERVATION_NOTICE_WINDOW" not in set(ev_s["event_type"])
    pha = agency_profile("pha_am", PACK)
    np_, ev_p = _derive([_lead("p", units="40", programs="LIHTC_9")], [_ev("p", "LIHTC_EXTENDED_USE_END", "2029-06-01")], profile=pha)
    assert "PRESERVATION_NOTICE_WINDOW" not in set(ev_p["event_type"]) and np_.iloc[0]["notice_window_state"] == "not_tracked_by_profile"


def test_servicing_row_deadlines_qc_rofr_records_inspection_usda():
    row = {"qc_request_complete_date": "2026-03-15", "qc_waived": "false", "third_party_offer_mailed_date": "2026-09-20", "notice_log_status": "received", "notice_received_date": "2026-09-01",
           "records_request_date": "2026-09-05", "usda_prepay_request_date": "2026-08-01", "last_inspection_date": "2024-11-05", "program": "HOME", "units_assisted": "124"}
    out = {e["event_type"]: e for e in AC.deadlines_from_servicing_row("x", row, AS_OF, PARAMS, 124.0, ["HOME"])}
    assert out["QC_RESPONSE_DUE"]["event_date"] == "2027-03-15"
    assert out["ROFR_MATCH_DEADLINE"]["event_date"] == "2026-10-20" and out["ROFR_MATCH_DEADLINE"]["verify_flag"] == ""
    assert out["RECORDS_REQUEST_DUE"]["event_date"] == "2026-09-11" and out["RECORDS_RESPONSE_DUE"]["event_date"] == "2026-10-05"
    assert out["USDA_PUBLIC_BODY_OFFER_WINDOW_END"]["event_date"] == "2027-01-28"
    assert out["INSPECTION_DUE"]["event_date"] == "2025-11-05"  # 26+ HOME units: annual
    # ROFR two-step: the Notice of ROFR is recordable only 30 days after the qualified purchaser's offer (ORS 456.262, verify)
    qp = {e["event_type"]: e for e in AC.deadlines_from_servicing_row("q", {"qp_offer_delivered_date": "2026-09-10"}, AS_OF, PARAMS)}
    assert qp["ROFR_RECORDABLE_DATE"]["event_date"] == "2026-10-10" and "ROFR_RECORDABLE_DATE" in AC.AGENCY_DEADLINE_META
    rcv = {e["event_type"]: e for e in AC.deadlines_from_servicing_row("y", {"third_party_offer_received_date": "2026-09-20"}, AS_OF, PARAMS)}
    assert rcv["ROFR_MATCH_DEADLINE"]["verify_flag"] == "Verify — Mailing Date"
    assert "QC_RESPONSE_DUE" not in {e["event_type"] for e in AC.deadlines_from_servicing_row("z", {"qc_request_complete_date": "2026-03-15", "qc_waived": "true"}, AS_OF, PARAMS)}


def test_meta_row_for_every_agency_deadline_type_and_helper_exclusion():
    for et in AGENCY_ACTION_EVENTS:
        meta = AC.AGENCY_DEADLINE_META[et]
        assert meta["agency_owner"] and meta["statutory_cite"] and meta["verified_live"] is False and meta["derives_from"]
    leads, events = _derive([_lead("vg", units="35", programs="OTHER_OHCS")], [_ev("vg", "SOFT_PROGRAM_END", "2029-06-01", program="OTHER_OHCS")])
    _, s = summarize(events, AS_OF, 10, 10)
    assert s["by_basis"]["REPORTED"] == 1 and s["by_basis"]["DERIVED"] == 0 and s["agency_act_by"] >= 3 and "agency act-by" in s["header"]
