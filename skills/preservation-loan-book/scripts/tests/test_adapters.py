"""Fixture tests for the HUD Sec 8, HUD FHASL, OHCS forecast and REAC adapters (synthetic data, canonical field names, no PII) and
schema discovery in run_agency_pipeline.py."""
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
sys.path.insert(0, SCRIPTS)


def _run(script, *args):
    out = tempfile.mkdtemp(prefix="plb_adp_")
    p = subprocess.run([sys.executable, os.path.join(SCRIPTS, script), "--out-dir", out, "--as-of", "2026-10-04", "--pack", PACK, *args], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    return {"dir": out, "leads": pd.read_csv(os.path.join(out, "leads.csv"), dtype=str, keep_default_na=False),
            "events": pd.read_csv(os.path.join(out, "events.csv"), dtype=str, keep_default_na=False),
            "cal": json.load(open(os.path.join(out, "calendar_summary.json"))), "stdout": p.stdout}


def test_hud_sec8_hap_units_no_phone_and_renewal_details():
    r = _run("normalize_hud_sec8.py", "--input", os.path.join(FX, "hud_sec8_sample.csv"), "--zip-crosswalk", os.path.join(FX, "zip_county_crosswalk_sample.csv"), "--counties", "41051,41067,41005")
    leads, ev = r["leads"], r["events"]
    assert "owner_phone" not in leads.columns and "owner_email" not in leads.columns and "outreach_template" not in leads.columns
    hap = ev[ev["event_type"] == "HAP_EXPIRATION"]
    assert len(hap) == len(ev) and set(hap["basis"]) == {"REPORTED"} and (hap["confidence"].astype(float) == 0.7).all()
    assert set(hap["program"]) <= {"HAP", "PRAC", "RAC", "PAC"} and (hap["detail"].isin(["short_renewal_pattern", "annual_renewal", ""])).all()
    lents = leads[leads["property_name"] == "Sample Lents Senior Housing"].iloc[0]
    assert lents["hap_units_at_risk"] == "60" and lents["programs"] == "HAP"
    prac = leads[leads["programs"] == "PRAC"]
    assert len(prac) == 1 and prac.iloc[0]["hap_units_at_risk"] in ("", "0")
    stale = ev[ev["status"] == "STALE_CONTRACT_DATE"]
    assert len(stale) == 1 and stale.iloc[0]["verify_flag"] == "Verify — Stale Contract Date"


def test_hud_insured_senior_lien_without_refi_screen():
    r = _run("normalize_hud_insured.py", "--input", os.path.join(FX, "hud_fhasl_sample.csv"), "--terminated", os.path.join(FX, "hud_fhasl_terminated_sample.csv"),
             "--zip-crosswalk", os.path.join(FX, "zip_county_crosswalk_sample.csv"), "--counties", "41051,41067,41005")
    leads, ev = r["leads"], r["events"]
    for gone in ("est_ltv", "est_dscr_refi", "refi_gap_pct", "assumable_debt", "rate_spread_bp", "outreach_template"):
        assert gone not in leads.columns
    assert (leads["senior_lien_type"] == "hud_fha").all() and (leads["senior_maturity"] != "").all() and leads["senior_upb"].astype(float).gt(0).all()
    mats = ev[ev["event_type"].isin(["LOAN_MATURITY", "HUD_DIRECT_LOAN_MATURITY"])]
    assert set(mats["basis"]) == {"RECORDED"} and (mats["program"] == "HUD_INSURED").all()
    assert "REFINANCE_CLOSED" in set(ev["event_type"]) and ev[ev["event_type"] == "SUPPRESS_UNTIL"].iloc[0]["event_date"] == "2031-08-15"
    assert r["cal"]["terminated_matched"] == 1


def test_ohcs_forecast_notices_status_flips_and_kpi_flags():
    r = _run("normalize_ohcs_forecast.py", "--input", os.path.join(FX, "ohcs_forecast_sample.csv"), "--prior", os.path.join(FX, "ohcs_forecast_prior_sample.csv"), "--counties", "41051,41067,41005")
    ev, leads = r["events"], r["leads"]
    assert r["cal"]["rows_in_geography"] == 4
    notices = ev[ev["event_type"] == "PRESERVATION_NOTICE_RECEIVED"]
    assert len(notices) == 2 and set(notices["basis"]) == {"RECORDED"}
    assert notices[notices["detail"] == "push_first"].iloc[0]["event_date"] == "2026-03-15"
    assert notices[notices["detail"] == "hap_optout"].iloc[0]["verify_flag"] == "Needs Anchor Date"
    assert "STABILIZATION_AWARD" in set(ev["event_type"])
    assert set(leads[leads["notice_status"] == "received"]["property_name"]) == {"Village Garden Apartments", "Sample Opt-Out Place"}
    assert "preserved" in set(leads["kpi_flags"]) and "notice_filed" in " ".join(leads["kpi_flags"])
    assert "outreach_template" not in leads.columns and "outreach_angle" not in leads.columns
    flips = pd.read_csv(os.path.join(r["dir"], "status_flips.csv"), dtype=str, keep_default_na=False)
    assert len(flips) == 3


def test_forecast_reuses_ohcs_property_ids_when_leads_supplied():
    out = tempfile.mkdtemp()
    pd.DataFrame([{"property_id": "addr:deadbeef0001", "property_name": "Village Garden Apartments", "address": "15230 NE Sandy Boulevard", "zip": "97230"}]).to_csv(os.path.join(out, "leads.csv"), index=False)
    r = _run("normalize_ohcs_forecast.py", "--input", os.path.join(FX, "ohcs_forecast_sample.csv"), "--ohcs-leads", os.path.join(out, "leads.csv"))
    assert "addr:deadbeef0001" in set(r["leads"]["property_id"]) and r["cal"]["matched_to_ohcs_leads"] == 1


def test_reac_scores_reported_with_decline_detail():
    r = _run("normalize_reac_scores.py", "--input", os.path.join(FX, "reac_scores_sample.csv"), "--counties", "41051,41067,41005")
    ev = r["events"]
    assert set(ev["event_type"]) == {"REAC_SCORE"} and set(ev["basis"]) == {"REPORTED"}
    low = ev[ev["value"].astype(float) < 60]
    assert len(low) == 1 and "decline_ge_15" in low.iloc[0]["detail"] and r["cal"]["below_60"] == 1


def test_pipeline_discover_recognizes_schemas_including_servicing_match_any():
    from plb.schema import detect_schema, load_dataset_schemas
    from run_agency_pipeline import discover, file_vintage
    schemas = load_dataset_schemas(PACK)
    cols = lambda f: list(pd.read_csv(os.path.join(FX, f), nrows=0, encoding="utf-8-sig").columns)  # noqa: E731
    assert detect_schema(cols("agency_servicing_sample.csv"), schemas) == "agency_servicing_extract"
    assert detect_schema(cols("pha_book_sample.csv"), schemas) == "agency_servicing_extract"
    assert detect_schema(cols("agency_servicing_bad_schema.csv"), schemas) is None
    assert detect_schema(cols("ohcs_sample.csv"), schemas) == "ohcs_affordable_housing_inventory"
    assert detect_schema(cols("ohcs_forecast_sample.csv"), schemas) == "ohcs_push_forecast"
    assert detect_schema(cols("reac_scores_sample.csv"), schemas) == "hud_reac_scores"
    found = discover({"servicing_extract": os.path.join(FX, "agency_servicing_sample.csv"), "local_datasets": [os.path.join(FX, "ohcs_sample.csv"), os.path.join(FX, "zip_county_crosswalk_sample.csv")]}, schemas)
    assert [f["schema"] for f in found] == ["agency_servicing_extract", "ohcs_affordable_housing_inventory", "zip_county_crosswalk"]  # servicing first
    assert file_vintage("/x/Oregon_Affordable_Housing_Inventory_20261002.csv") == ("2026-10-02", "filename")
    assert file_vintage(os.path.join(FX, "ohcs_sample.csv"))[1] == "mtime"
