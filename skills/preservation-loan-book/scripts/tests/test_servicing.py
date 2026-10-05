"""ingest_servicing_extract.py: the agency's own ledger is RECORDED; per-kind validation; exit 2 on a bad header or when every row
fails, naming the rule; owned_asset / administered_contract rows validate; am_officer stays, am_officer_email needs --internal."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _fixture_runs import FX, PACK, SCRIPTS, by_name, hfa_fixture_run  # noqa: E402

SCRIPT = os.path.join(SCRIPTS, "ingest_servicing_extract.py")


def _run(inp, *extra, profile="hfa"):
    out = tempfile.mkdtemp(prefix="plb_srv_")
    p = subprocess.run([sys.executable, SCRIPT, "--input", inp, "--pack", PACK, "--agency-profile", profile, "--out-dir", out, "--as-of", "2026-10-04", *extra], capture_output=True, text=True)
    return p, out


def test_fixture_emits_recorded_book_events():
    p, out = _run(os.path.join(FX, "agency_servicing_sample.csv"))
    assert p.returncode == 0, p.stderr
    leads = pd.read_csv(os.path.join(out, "leads.csv"), dtype=str, keep_default_na=False)
    ev = pd.read_csv(os.path.join(out, "events.csv"), dtype=str, keep_default_na=False)
    cal = json.load(open(os.path.join(out, "calendar_summary.json")))
    assert len(leads) == 14 and cal["rows_rejected"] == 0 and (leads["universe"] == "our_book").all() and (leads["in_inventory"].str.lower() == "false").all()
    ours = ev[(ev["event_family"] != "AGENCY_DEADLINE") & (ev["event_type"] != "LOAN_MATURITY")]
    assert (ours["basis"] == "RECORDED").all() and (ours["source"] == "agency_servicing").all()  # ledger rows RECORDED; helper deadlines DERIVED from them
    assert (ev["event_type"] == "AGENCY_LOAN_MATURITY").sum() == 13
    types = set(ev["event_type"])
    assert {"AFFORDABILITY_PERIOD_END", "GRANT_RECAPTURE_END", "COVENANT_DEFAULT", "QC_ELIGIBILITY", "QC_RESPONSE_DUE", "INSPECTION_DUE", "LOAN_MATURITY"} <= types
    sa = by_name(leads, "St Anthony Village")
    assert sa["covenant_status"] == "default" and (ev[(ev["property_id"] == sa["property_id"]) & (ev["event_type"] == "COVENANT_DEFAULT")]["event_date"] == "2026-10-04").all()
    cg = by_name(leads, "Cathedral Gardens")
    qc = ev[(ev["property_id"] == cg["property_id"]) & (ev["event_type"] == "QC_RESPONSE_DUE")]
    assert len(qc) == 1 and qc.iloc[0]["event_date"] == "2027-03-15" and cg["qc_status"] == "requested"
    rs = by_name(leads, "Rose Schnitzer Tower")
    assert rs["senior_lien_type"] == "hud_fha" and rs["senior_maturity"] == "2027-12-10" and float(rs["senior_upb"]) == 12_000_000
    senior = ev[(ev["property_id"] == rs["property_id"]) & (ev["event_type"] == "LOAN_MATURITY")]
    assert senior.iloc[0]["basis"] == "REPORTED" and "lender_type=hud_fha" in senior.iloc[0]["detail"]
    # every servicing event carries the ledger id in detail and in the event_id
    ours = ev[ev["event_type"] == "AGENCY_LOAN_MATURITY"]
    assert ours["detail"].str.contains("agency_loan_id=").all() and ours["event_id"].str.contains("L-OHCS-").all()
    g42 = by_name(leads, "GOING 42")
    assert g42["recapture_type"] == "home_rental_repayment" and g42["recapture_method"] == "full" and float(g42["recapture_amount"]) == 1_100_000  # rental HOME: 24 CFR 92.503(b), not 92.254
    assert (leads["am_officer"] != "").all() and "am_officer_email" not in leads.columns


def test_internal_flag_adds_am_officer_email():
    p, out = _run(os.path.join(FX, "agency_servicing_sample.csv"), "--internal")
    assert p.returncode == 0
    leads = pd.read_csv(os.path.join(out, "leads.csv"), dtype=str, keep_default_na=False)
    assert "am_officer_email" in leads.columns and leads["am_officer_email"].str.contains("@").all()


def test_bad_header_exits_2_naming_the_schema():
    p, _ = _run(os.path.join(FX, "agency_servicing_bad_schema.csv"))
    assert p.returncode == 2 and "agency_servicing_extract" in p.stderr and "book_kind" in p.stderr


def test_every_row_failing_exits_2_naming_the_rule():
    tmp = tempfile.mkdtemp()
    path = os.path.join(tmp, "bad_rows.csv")
    pd.DataFrame([{"book_kind": "loan", "program": "HOME", "agency_loan_id": "L-1", "maturity": "2030-01-01", "address": "1 Main St", "zip": "97205", "upb": ""},
                  {"book_kind": "grant", "program": "HOME", "grant_id": "", "affordability_end": "2030-01-01", "address": "2 Main St", "zip": "97205", "upb": ""}]).to_csv(path, index=False)
    p, _ = _run(path)
    assert p.returncode == 2 and "every row failed" in p.stderr and "loan requires upb" in p.stderr


def test_partial_failures_go_to_rejects_not_exit():
    tmp = tempfile.mkdtemp()
    path = os.path.join(tmp, "mixed.csv")
    pd.DataFrame([{"book_kind": "loan", "program": "HOME", "agency_loan_id": "L-1", "maturity": "2030-01-01", "address": "1 Main St", "zip": "97205", "upb": "100000"},
                  {"book_kind": "loan", "program": "HOME", "agency_loan_id": "L-2", "maturity": "2030-01-01", "address": "2 Main St", "zip": "97205", "upb": "100000", "covenant_status": "delinquent"}]).to_csv(path, index=False)
    p, out = _run(path)
    assert p.returncode == 0
    rej = pd.read_csv(os.path.join(out, "rejects.csv"), dtype=str, keep_default_na=False)
    assert len(rej) == 1 and "covenant_status" in rej.iloc[0]["reason"] and rej.iloc[0]["flag"] == "Rejected — Out of Range"


def test_pha_book_owned_assets_and_administered_contract_validate():
    p, out = _run(os.path.join(FX, "pha_book_sample.csv"), profile="pha_am")
    assert p.returncode == 0, p.stderr
    leads = pd.read_csv(os.path.join(out, "leads.csv"), dtype=str, keep_default_na=False)
    ev = pd.read_csv(os.path.join(out, "events.csv"), dtype=str, keep_default_na=False)
    assert set(leads["book_kind"]) == {"owned_asset", "administered_contract"} and (leads[leads["book_kind"] == "owned_asset"]["book_match"] == "self_owned").all()
    assert (leads[leads["book_kind"] == "owned_asset"]["owner_type"] == "self_owned").all()
    pbv = ev[(ev["event_type"] == "HAP_EXPIRATION")]
    assert len(pbv) == 1 and pbv.iloc[0]["program"] == "PBV" and float(pbv.iloc[0]["confidence"]) == 0.9
    assert "RAD_CHAP" in set(ev["event_type"])


def test_merged_fixture_keeps_book_columns_and_our_events():
    r = hfa_fixture_run()
    vg = by_name(r["leads"], "Village Garden Apartments")
    assert vg["universe"] == "our_book" and vg["book_kind"] == "loan" and float(vg["public_upb"]) == 1_200_000 and vg["payment_type"] == "residual_receipts"
    assert vg["our_maturity"] == "2031-06-30" and vg["our_maturity_basis"] == "RECORDED" and vg["affordability_end"] == "2029-06-01" and vg["am_officer"] == "J. Rivera"
    types = set(r["events"][r["events"]["property_id"] == vg["property_id"]]["event_type"])
    assert {"AGENCY_LOAN_MATURITY", "AFFORDABILITY_PERIOD_END", "PUSH_FIRST_NOTICE_DUE"} <= types and "RECORDS_REQUEST_DUE" not in types
