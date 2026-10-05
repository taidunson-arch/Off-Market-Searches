"""Fixture tests for the recorder-index, assessor-taxlot and OHCS forecast adapters (synthetic data, canonical field names)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
PACK = os.path.normpath(os.path.join(SCRIPTS, "..", "references", "sources", "oregon-portland"))
FX = os.path.join(HERE, "fixtures")


def _run(script, *args):
    out = tempfile.mkdtemp(prefix="omdf_adp_")
    p = subprocess.run([sys.executable, os.path.join(SCRIPTS, script), "--out-dir", out, "--as-of", "2026-10-04", "--pack", PACK, *args], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    return {"dir": out, "leads": pd.read_csv(os.path.join(out, "leads.csv"), dtype=str, keep_default_na=False),
            "events": pd.read_csv(os.path.join(out, "events.csv"), dtype=str, keep_default_na=False),
            "cal": json.load(open(os.path.join(out, "calendar_summary.json"))), "stdout": p.stdout}


def test_recorder_index_events_and_estimated_maturities():
    r = _run("normalize_recorder_index.py", "--input", os.path.join(FX, "recorder_index_sample.csv"))
    ev, leads = r["events"], r["leads"].set_index("property_id")
    # bank trust deed with no printed maturity -> ESTIMATED point = recording + typical (7y), window min..max (5..10y)
    e = ev[(ev["property_id"] == "OR-41051-R123456") & (ev["event_type"] == "LOAN_MATURITY")].iloc[0]
    assert e["basis"] == "ESTIMATED" and e["event_date"] == "2025-06-15" and e["window_start"] == "2023-06-15" and e["window_end"] == "2028-06-15"
    assert leads.loc["OR-41051-R123456", "lender_type"] == "bank_cu" and leads.loc["OR-41051-R123456", "asset_class"] == "market_rate_mf"
    # bridge lender -> debt_fund_bridge with RATE_CAP_EXPIRY
    assert leads.loc["OR-41051-R222333", "lender_type"] == "debt_fund_bridge"
    assert (ev[ev["property_id"] == "OR-41051-R222333"]["event_type"] == "RATE_CAP_EXPIRY").any()
    # Oregon NOD: pre-NOD trustee appointment, NOD, stated sale date (RECORDED), cure = sale - 5 d; class 1 from units
    sub = ev[ev["property_id"] == "OR-41051-R555666"].set_index("event_type")
    assert {"SUCCESSOR_TRUSTEE_APPOINTED", "NOD_RECORDED", "TRUSTEE_SALE_EARLIEST", "CURE_DEADLINE"} <= set(sub.index)
    assert sub.loc["TRUSTEE_SALE_EARLIEST", "event_date"] == "2026-12-10" and sub.loc["CURE_DEADLINE", "event_date"] == "2026-12-05"
    assert float(sub.loc["NOD_RECORDED", "value"]) == 287450.0 and leads.loc["OR-41051-R555666", "asset_class"] == "sfr_small_res"
    # printed maturity -> RECORDED; reconveyance followed by new trust deed within 90 d -> REFINANCE_CLOSED + SUPPRESS_UNTIL (+5y bank min term)
    sub = ev[ev["property_id"] == "OR-41051-R777888"]
    assert (sub[sub["event_date"] == "2024-03-01"]["basis"] == "RECORDED").all()
    assert "REFINANCE_CLOSED" in set(sub["event_type"]) and sub[sub["event_type"] == "SUPPRESS_UNTIL"].iloc[0]["event_date"] == "2029-03-20"
    # reconveyance with no new lien -> UNENCUMBERED
    assert "UNENCUMBERED" in set(ev[ev["property_id"] == "OR-41051-R999000"]["event_type"])
    # Washington NOTS: cure = sale - 11 d; trust owner
    sub = ev[ev["property_id"] == "WA-53011-123456789"].set_index("event_type")
    assert sub.loc["CURE_DEADLINE", "event_date"] == "2026-12-08" and leads.loc["WA-53011-123456789", "owner_type"] == "trust_estate"
    assert r["cal"]["unknown_doc_types"] == {"Certificate of Mystery Filing": 1}
    assert r["cal"]["verified_live"] is False


def test_assessor_taxlots_absentee_hold_and_rmv():
    r = _run("normalize_assessor_taxlots.py", "--input", os.path.join(FX, "assessor_taxlots_sample.csv"))
    leads = r["leads"].set_index("property_id")
    ev = r["events"]
    assert leads.loc["OR-41051-R123456", "signals"].endswith("absentee:far") and leads.loc["OR-41051-R123456", "mailing_address"].startswith("PO BOX 4411")
    assert leads.loc["OR-41051-R555666", "owner_type"] == "individual_occupant" and float(leads.loc["OR-41051-R555666", "hold_years"]) > 30
    assert "DEPRECIATION_EXHAUSTED" in set(ev[ev["property_id"] == "OR-41051-R555666"]["event_type"])
    assert "RECENT_1031_ACQUISITION" in set(ev[ev["property_id"] == "OR-41051-R777888"]["event_type"])  # hold 2.5 y
    assert (ev[ev["property_id"] == "OR-41051-R555666"]["event_type"] == "TAX_DELINQUENT_YEARS").any()
    # est_value = RMV x sales ratio (1.0 default); AV never used; av_rmv_ratio is a tenure signal
    assert float(leads.loc["OR-41051-R123456", "est_value"]) == 8_400_000 and leads.loc["OR-41051-R123456", "value_source"].startswith("rmv_calibrated")
    assert abs(float(leads.loc["OR-41051-R555666", "av_rmv_ratio"]) - 0.41) < 1e-6
    assert set(ev["basis"]) == {"RECORDED"} and leads.loc["OR-41051-R333444", "asset_class"] == "sfr_small_res" and leads.loc["OR-41051-R222333", "asset_class"] == "market_rate_mf"


def test_ohcs_forecast_notices_and_status_flips():
    r = _run("normalize_ohcs_forecast.py", "--input", os.path.join(FX, "ohcs_forecast_sample.csv"), "--prior", os.path.join(FX, "ohcs_forecast_prior_sample.csv"),
             "--counties", "41051,41067,41005")
    ev, leads = r["events"], r["leads"]
    assert r["cal"]["rows_in_geography"] == 4  # Lincoln County row dropped
    assert (leads["on_state_expiring_list"].astype(str).str.lower() == "true").all()
    notices = ev[ev["event_type"] == "PRESERVATION_NOTICE_RECEIVED"]
    assert len(notices) == 2 and set(notices["basis"]) == {"RECORDED"}
    vg = notices[notices["detail"] == "push_first"].iloc[0]
    assert vg["event_date"] == "2026-03-15" and vg["verify_flag"] == ""
    oo = notices[notices["detail"] == "hap_optout"].iloc[0]
    assert oo["verify_flag"] == "Needs Anchor Date"  # no notice date in the file
    assert "STABILIZATION_AWARD" in set(ev["event_type"])
    flips = pd.read_csv(os.path.join(r["dir"], "status_flips.csv"), dtype=str, keep_default_na=False)
    assert len(flips) == 3 and (flips["flip_into_notice"].str.lower() == "true").sum() == 2


def test_forecast_reuses_ohcs_property_ids_when_leads_supplied():
    # build a tiny OHCS-style leads file whose name+address matches a forecast row
    out = tempfile.mkdtemp()
    pd.DataFrame([{"property_id": "addr:deadbeef0001", "property_name": "Village Garden Apartments", "address": "15230 NE Sandy Boulevard", "zip": "97230"}]).to_csv(os.path.join(out, "leads.csv"), index=False)
    r = _run("normalize_ohcs_forecast.py", "--input", os.path.join(FX, "ohcs_forecast_sample.csv"), "--ohcs-leads", os.path.join(out, "leads.csv"))
    assert "addr:deadbeef0001" in set(r["leads"]["property_id"]) and r["cal"]["matched_to_ohcs_leads"] == 1


def test_pipeline_discover_recognizes_new_schemas():
    sys.path.insert(0, SCRIPTS)
    from omdf.schema import detect_schema, load_dataset_schemas
    from run_pipeline import file_vintage
    schemas = load_dataset_schemas(PACK)
    assert detect_schema(list(pd.read_csv(os.path.join(FX, "recorder_index_sample.csv"), nrows=0).columns), schemas) == "recorder_index_export"
    assert detect_schema(list(pd.read_csv(os.path.join(FX, "assessor_taxlots_sample.csv"), nrows=0).columns), schemas) == "assessor_taxlots"
    assert detect_schema(list(pd.read_csv(os.path.join(FX, "ohcs_forecast_sample.csv"), nrows=0).columns), schemas) == "ohcs_push_forecast"
    assert file_vintage("/x/Oregon_Affordable_Housing_Inventory_20261002.csv") == ("2026-10-02", "filename")
    assert file_vintage(os.path.join(FX, "ohcs_sample.csv"))[1] == "mtime"
