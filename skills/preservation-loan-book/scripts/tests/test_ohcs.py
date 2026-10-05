"""Acceptance tests for ohcs_inventory_targets.py on the real OHCS inventory (skipped when the file is absent) plus hermetic checks
on the fixture: declared date formats, geography modes, stale HUD dates, units columns, no buyer value proxy, no PuSH windows here
(they are derived from the withdrawal anchor in plb/agency_calendar.py)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from unittest import SkipTest

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
SCRIPT = os.path.join(SCRIPTS, "ohcs_inventory_targets.py")
PACK = os.path.normpath(os.path.join(SCRIPTS, "..", "references", "sources", "oregon-portland"))
REAL = os.environ.get("OHCS_CSV", "/tmp/claude-0/-home-user/7bb5c89e-a260-588a-815c-3462cdc087de/scratchpad/d/Oregon_Affordable_Housing_Inventory_20261002.csv")
FIXTURE = os.path.join(HERE, "fixtures", "ohcs_sample.csv")
_CACHE = {}


def _run(inp, *extra):
    key = (inp, extra)
    if key in _CACHE:
        return _CACHE[key]
    out = tempfile.mkdtemp(prefix="plb_ohcs_")
    cmd = [sys.executable, SCRIPT, "--input", inp, "--pack", PACK, "--out-dir", out, "--as-of", "2026-10-04", "--horizon-years", "10", *extra]
    p = subprocess.run(cmd, capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    res = {"dir": out, "leads": pd.read_csv(os.path.join(out, "leads.csv"), dtype=str, keep_default_na=False),
           "events": pd.read_csv(os.path.join(out, "events.csv"), dtype=str, keep_default_na=False),
           "rejects": pd.read_csv(os.path.join(out, "rejects.csv"), dtype=str, keep_default_na=False),
           "cal": json.load(open(os.path.join(out, "calendar_summary.json"))), "stdout": p.stdout, "stderr": p.stderr}
    _CACHE[key] = res
    return res


def _need_real():
    if not os.path.exists(REAL):
        raise SkipTest(f"real OHCS CSV not found at {REAL} (set OHCS_CSV)")


def test_real_metro_core_counts_and_stale_dates():
    _need_real()
    r = _run(REAL, "--mode", "metro_core")
    assert r["cal"]["rows_total"] == 1819 and r["cal"]["rows_in_geography"] == 810 and r["cal"]["rows_excluded_in_development"] == 46
    assert len(r["leads"]) == 764 and (r["leads"]["status"] == "In Development").sum() == 0 and set(r["leads"]["geo_grade"]) == {"county_field"}
    assert r["cal"]["stale_contract_dates"] == 33 and (r["events"]["status"] == "STALE_CONTRACT_DATE").sum() == 33
    assert r["cal"]["vintage"] == "20261002" and r["cal"]["vintage_source"] == "filename"
    assert "agency act-by" in r["cal"]["header"] and "helper deadlines" in r["cal"]["header"]
    assert len(r["cal"]["pipeline_not_scored"]) == 46


def test_real_city_limits_counts_and_grade():
    _need_real()
    r = _run(REAL, "--mode", "city_limits", "--city", "Portland")
    assert r["cal"]["rows_in_geography"] == 518 and set(r["leads"]["geo_grade"]) == {"city_name_weak"}


def test_real_proxy_maturities_are_opt_in_and_day_first():
    _need_real()
    default = _run(REAL, "--mode", "metro_core")
    assert (default["events"]["basis"] == "PROXY").sum() == 0 and default["cal"]["include_proxies"] is False
    r = _run(REAL, "--mode", "metro_core", "--include-proxies", "true", "--regulatory-horizon-years", "60", "--horizon-years", "60")
    lm = r["events"][r["events"]["event_type"] == "LOAN_MATURITY"]
    assert len(lm) >= 90 and set(lm["basis"]) == {"PROXY"}  # 96 metro Active rows carry Financial_Closing_Date
    assert len(r["rejects"][(r["rejects"]["column"] == "Financial_Closing_Date") & (r["rejects"]["flag"] == "Verify — Ambiguous")]) == 0
    raw = pd.read_csv(REAL, dtype=str, encoding="utf-8-sig", keep_default_na=False)
    raw = raw[raw["Financial_Closing_Date"].str.match(r"^(1[3-9]|2\d|3[01])/\d{1,2}/\d{4}$", na=False)]
    leads = r["leads"].set_index(["property_name", "address"])
    ev = lm.set_index("property_id")
    checked = 0
    for _, row in raw.iterrows():
        key = (row["Property Name"], row["Address"])
        if key in leads.index:
            pid = leads.loc[key]["property_id"]
            pid = pid.iloc[0] if hasattr(pid, "iloc") else pid
            if pid in ev.index:
                e = ev.loc[pid]
                e = e.iloc[0] if isinstance(e, pd.DataFrame) else e
                d, m, y = row["Financial_Closing_Date"].split("/")
                assert e["event_date"] in (f"{int(y) + 15:04d}-{int(m):02d}-{int(d):02d}", f"{int(y) + 17:04d}-{int(m):02d}-{int(d):02d}")
                checked += 1
    assert checked >= 5


def test_real_usda_format_and_known_latest_exceptions():
    _need_real()
    r = _run(REAL, "--mode", "cbsa", "--regulatory-horizon-years", "60")
    usda = r["events"][r["events"]["event_type"] == "USDA_515_MATURITY"]
    assert len(usda) > 0 and all(len(d) == 10 for d in usda["event_date"])
    r2 = _run(REAL, "--county", "41031,41071", "--regulatory-horizon-years", "60")
    for name in ("Casa Sonada 4", "Riverside Terrace"):
        rows = r2["leads"][r2["leads"]["property_name"] == name]
        assert len(rows) == 1 and "Verify — Conflicting Sources" in rows.iloc[0]["verify_flags"] and "LATEST" in rows.iloc[0]["verify_flags"]
    assert r2["cal"]["rejected"] == 0


def test_real_year15_only_with_lihtc_and_hap_program_stamp():
    _need_real()
    r = _run(REAL, "--mode", "metro_core")
    progs = r["leads"].set_index("property_id")["programs"]
    y15 = r["events"][r["events"]["event_type"] == "LIHTC_COMPLIANCE_END"]
    assert len(y15) > 0 and all("LIHTC" in progs.get(p, "") for p in y15["property_id"])
    hap = r["events"][r["events"]["event_type"] == "HAP_EXPIRATION"]
    assert len(hap) == 130 and set(hap["program"]) == {"HAP", "PRAC", "PAC"} and (hap["detail"] == "term_unknown_annual_assumed").all()
    assert (hap["confidence"].astype(float) == 0.7).all()
    # no PuSH window or agency deadline comes out of the adapter; agency_calendar.py derives them from the withdrawal anchor
    assert not set(r["events"]["event_type"]) & {"PRESERVATION_NOTICE_WINDOW", "PUSH_FIRST_NOTICE_DUE", "HAP_OPTOUT_NOTICE_DEADLINE"}


def test_real_units_columns_and_no_value_proxy():
    _need_real()
    r = _run(REAL, "--mode", "metro_core")
    leads = r["leads"]
    for gone in ("est_value", "value_source", "decision_maker_name", "outreach_template", "motivation_score", "tier", "route"):
        assert gone not in leads.columns, gone
    assert (leads["est_restricted_noi"] == "").all() and leads["noi_source"].str.contains("rent-limits").all()
    assert leads["ohcs_funded"].str.lower().isin(["true", "false", ""]).all() and (leads["ohcs_funded"].str.lower() == "true").sum() == 374
    ua = pd.to_numeric(leads["units_at_risk"], errors="coerce")
    assert ua.notna().sum() > 700 and (ua <= pd.to_numeric(leads["units"], errors="coerce")).all()
    assert pd.to_numeric(leads["psh_units_at_risk"], errors="coerce").sum() == 959  # metro Active PSH_Units (In Development excluded)
    assert pd.to_numeric(leads["hap_units_at_risk"], errors="coerce").sum() > 3000 and pd.to_numeric(leads["prac_units_at_risk"], errors="coerce").sum() > 500
    assert not leads["rehab_year"].str.contains(",").any() and leads["units"].str.match(r"^\d+$").all()
    assert set(leads["units_basis"]) - {""} <= {"reported_buckets", "total_assumed_restricted", "proxy"}


def test_fixture_schema_events_and_stale_row():
    r = _run(FIXTURE, "--mode", "metro_core")
    assert len(r["leads"]) == 7 and r["cal"]["rows_excluded_in_development"] == 1
    ev = r["events"]
    assert set(ev["basis"]) <= {"REPORTED", "DERIVED"}
    hap = ev[ev["event_type"] == "HAP_EXPIRATION"]
    assert len(hap) == 3 and (hap["confidence"].astype(float) == 0.7).all() and (hap["program"] == "HAP").all()
    stale = hap[hap["status"] == "STALE_CONTRACT_DATE"]
    assert len(stale) == 1 and stale.iloc[0]["event_date"] == "2024-09-30"
    assert {"lihtc_partnership_nonprofit_gp", "housing_authority", "individual_owner_of_record"} <= set(r["leads"]["owner_type"])
    bad = r["rejects"][r["rejects"]["flag"] == "Rejected — Out of Range"]
    assert len(bad) == 1 and bad.iloc[0]["column"] == "LIHTC_9_Expiration_Date"
    park = r["leads"][r["leads"]["property_name"] == "Fixture Park Terrace"].iloc[0]
    assert "hap_date_stale" in park["signals"] and park["vulnerability_flags"] == "elderly" and park["hap_units_at_risk"] == "50"
    assert "decision_maker_name" not in r["leads"].columns and "owner_phone" not in r["leads"].columns


def test_fixture_auto_detect_flags_ambiguous():
    r = _run(FIXTURE, "--mode", "metro_core", "--auto-detect-dates")
    amb = r["rejects"][r["rejects"]["flag"] == "Verify — Ambiguous"]
    assert len(amb) >= 1 and all(";" in a for a in amb["alt_dates"])


def test_fixture_wrong_schema_exit_2():
    out = tempfile.mkdtemp()
    p = subprocess.run([sys.executable, SCRIPT, "--input", os.path.join(HERE, "fixtures", "hud_sec8_sample.csv"), "--out-dir", out], capture_output=True, text=True)
    assert p.returncode == 2 and "schema" in p.stderr.lower()
