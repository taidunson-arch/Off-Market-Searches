"""Acceptance tests for ohcs_inventory_targets.py on the real OHCS inventory (skipped when the file is absent)
plus hermetic checks on the small fixture."""
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
REAL = os.environ.get("OHCS_CSV", "/tmp/claude-0/-home-user/7bb5c89e-a260-588a-815c-3462cdc087de/scratchpad/d/Oregon_Affordable_Housing_Inventory_20261002.csv")
FIXTURE = os.path.join(HERE, "fixtures", "ohcs_sample.csv")
_CACHE = {}


def _run(inp, *extra):
    key = (inp, extra)
    if key in _CACHE:
        return _CACHE[key]
    out = tempfile.mkdtemp(prefix="omdf_ohcs_")
    cmd = [sys.executable, SCRIPT, "--input", inp, "--out-dir", out, "--as-of", "2026-10-04", "--horizon-years", "5", *extra]
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


def test_real_metro_core_counts():
    _need_real()
    r = _run(REAL, "--mode", "metro_core")
    assert r["cal"]["rows_total"] == 1819
    assert r["cal"]["rows_in_geography"] == 810  # Multnomah 546 + Washington 163 + Clackamas 101, before status filter
    assert r["cal"]["rows_excluded_in_development"] > 0
    assert (r["leads"]["status"] == "In Development").sum() == 0
    assert set(r["leads"]["geo_grade"]) == {"county_field"}


def test_real_city_limits_counts_and_grade():
    _need_real()
    r = _run(REAL, "--mode", "city_limits", "--city", "Portland")
    # 517 rows spell the city Portland plus one `Portalnd` typo corrected by the schema typo_map
    assert r["cal"]["rows_in_geography"] == 518
    assert set(r["leads"]["geo_grade"]) == {"city_name_weak"}
    assert "city_name_weak" in r["stderr"]


def test_real_declared_day_first_closing_date_no_ambiguity():
    _need_real()
    # the raw file carries 26/01/2022 (Veteran's Village, Baker) - that row has no expiration dates and is never a
    # lead, so verify the declared day-first parse on every metro lead whose raw closing date has a first field > 12
    r = _run(REAL, "--mode", "metro_core", "--horizon-years", "60", "--regulatory-horizon-years", "60")
    amb = r["rejects"][(r["rejects"]["column"] == "Financial_Closing_Date") & (r["rejects"]["flag"] == "Verify — Ambiguous")]
    assert len(amb) == 0
    raw = pd.read_csv(REAL, dtype=str, encoding="utf-8-sig", keep_default_na=False)
    raw = raw[raw["Financial_Closing_Date"].str.match(r"^(1[3-9]|2\d|3[01])/\d{1,2}/\d{4}$", na=False)]
    assert len(raw) > 0
    leads = r["leads"].set_index(["property_name", "address"])
    ev = r["events"][r["events"]["event_type"] == "LOAN_MATURITY"].set_index("property_id")
    checked = 0
    for _, row in raw.iterrows():
        key = (row["Property Name"], row["Address"])
        if key in leads.index:
            pid = leads.loc[key]["property_id"]
            pid = pid.iloc[0] if hasattr(pid, "iloc") else pid
            if pid in ev.index:
                e = ev.loc[pid]
                e = e.iloc[0] if hasattr(e, "iloc") and not isinstance(e, pd.Series) else e
                d, m, y = row["Financial_Closing_Date"].split("/")
                assert e["event_date"] == f"{int(y) + 15:04d}-{int(m):02d}-{int(d):02d}" or e["event_date"] == f"{int(y) + 17:04d}-{int(m):02d}-{int(d):02d}", (row["Financial_Closing_Date"], e["event_date"])
                assert e["basis"] == "PROXY"
                checked += 1
    assert checked >= 5
    ws = pd.to_datetime(ev["window_start"]); we = pd.to_datetime(ev["window_end"]); d = pd.to_datetime(ev["event_date"])
    assert ((d - ws).dt.days.between(1090, 1100)).all() and ((we - d).dt.days.between(1090, 1100)).all()  # +/- 36 months


def test_real_usda_format_and_proxy_windows():
    _need_real()
    r = _run(REAL, "--mode", "cbsa", "--regulatory-horizon-years", "60")
    ev = r["events"]
    usda = ev[ev["event_type"] == "USDA_515_MATURITY"]
    assert len(usda) > 0 and all(len(d) == 10 for d in usda["event_date"])
    lm = ev[ev["event_type"] == "LOAN_MATURITY"]
    assert len(lm) > 0 and set(lm["basis"]) == {"PROXY"}
    ws = pd.to_datetime(lm["window_start"]); we = pd.to_datetime(lm["window_end"]); d = pd.to_datetime(lm["event_date"])
    assert ((d - ws).dt.days.between(1090, 1100)).all() and ((we - d).dt.days.between(1090, 1100)).all()  # +/- 36 months


def test_real_known_latest_exceptions_flagged_not_rejected():
    _need_real()
    # Casa Sonada 4 (Jefferson) and Riverside Terrace (Yamhill): LATEST != max(components)
    r = _run(REAL, "--county", "41031,41071", "--regulatory-horizon-years", "60")
    for name in ("Casa Sonada 4", "Riverside Terrace"):
        rows = r["leads"][r["leads"]["property_name"] == name]
        assert len(rows) == 1, name
        assert "Verify — Conflicting Sources" in rows.iloc[0]["verify_flags"] and "LATEST" in rows.iloc[0]["verify_flags"]
        assert "known exception" in rows.iloc[0]["verify_flags"]
    assert r["cal"]["rejected"] == 0


def test_real_no_expiration_before_compliance_start_without_flag():
    _need_real()
    r = _run(REAL, "--mode", "metro_core")
    ev = r["events"]
    raw = pd.read_csv(REAL, dtype=str, encoding="utf-8-sig", keep_default_na=False)
    comp = {}
    for _, row in raw.iterrows():
        comp[(row["Property Name"], row["Address"])] = row["Compliance_Start_Date"]
    leads = r["leads"].set_index("property_id")
    bad = 0
    for _, e in ev[ev["event_family"] == "REGULATORY"].iterrows():
        l = leads.loc[e["property_id"]]
        cs = comp.get((l["property_name"], l["address"]), "")
        if cs:
            csd = pd.to_datetime(cs, format="%m/%d/%Y")
            if pd.to_datetime(e["event_date"]) < csd and not e["verify_flag"]:
                bad += 1
    assert bad == 0


def test_real_year15_only_with_lihtc_program():
    _need_real()
    r = _run(REAL, "--mode", "metro_core")
    progs = r["leads"].set_index("property_id")["programs"]
    y15 = r["events"][r["events"]["event_type"] == "LIHTC_COMPLIANCE_END"]
    assert len(y15) > 0 and all("LIHTC" in progs.get(p, "") for p in y15["property_id"])


def test_fixture_schema_and_events():
    r = _run(FIXTURE, "--mode", "metro_core")
    assert len(r["leads"]) >= 3
    ev = r["events"]
    assert set(ev["basis"]) <= {"REPORTED", "DERIVED", "PROXY"}
    hap = ev[ev["event_type"] == "HAP_EXPIRATION"]
    assert len(hap) >= 1 and float(hap.iloc[0]["confidence"]) == 0.70
    assert (r["leads"]["decision_maker_name"] == "not in public record").all()
    assert "lihtc_partnership_nonprofit_gp" in set(r["leads"]["owner_type"]) and "housing_authority" in set(r["leads"]["owner_type"])
    bad = r["rejects"][r["rejects"]["flag"] == "Rejected — Out of Range"]
    assert len(bad) == 1 and bad.iloc[0]["column"] == "LIHTC_9_Expiration_Date"  # 13/31/2031 cannot parse month-first


def test_fixture_auto_detect_flags_ambiguous():
    r = _run(FIXTURE, "--mode", "metro_core", "--auto-detect-dates")
    amb = r["rejects"][r["rejects"]["flag"] == "Verify — Ambiguous"]
    assert len(amb) >= 1 and all(";" in a for a in amb["alt_dates"])
    assert (r["events"]["event_date_quality"] == "ambiguous").any()


def test_fixture_wrong_schema_exit_2():
    out = tempfile.mkdtemp()
    p = subprocess.run([sys.executable, SCRIPT, "--input", os.path.join(HERE, "fixtures", "hud_sec8_sample.csv"), "--out-dir", out], capture_output=True, text=True)
    assert p.returncode == 2 and "schema" in p.stderr


def test_real_numeric_clean_and_rehab_penalty():
    _need_real()
    r = _run(REAL, "--mode", "metro_core")
    leads = r["leads"]
    assert not leads["rehab_year"].str.contains(",").any() and not leads["year_built"].str.contains(",").any()
    assert not leads["units"].str.contains(r"\.").any() and leads["units"].str.match(r"^\d+$").all()
    raw = pd.read_csv(REAL, dtype=str, encoding="utf-8-sig", keep_default_na=False)
    assert (raw["Rehab Year"].str.contains(",")).sum() >= 90  # the source really does store '2,021'
    # a 2020-2022 rehab in the lead table must receive the shared -15 penalty when scored
    recent = leads[leads["rehab_year"].isin(["2020", "2021", "2022"])]
    if len(recent):
        sys.path.insert(0, SCRIPTS)
        from omdf.scoring import load_scoring, score_lead
        from datetime import date
        tables, shared, _ = load_scoring()
        ev = r["events"]
        lead = recent.iloc[0].to_dict()
        res = score_lead(lead, ev[ev["property_id"] == lead["property_id"]].to_dict(orient="records"), "affordable_regulated", tables, shared, date(2026, 10, 4))
        assert any(p["id"] == "recent_rehab" and p["points"] == -15 for p in res["penalties"])


def test_real_push_window_gating_and_value_proxy():
    _need_real()
    r = _run(REAL, "--mode", "metro_core")
    ev, leads = r["events"], r["leads"]
    win = ev[ev["event_type"] == "PRESERVATION_NOTICE_WINDOW"].set_index("property_id")
    units = leads.set_index("property_id")["units"].astype(int)
    progs = leads.set_index("property_id")["programs"]
    for pid in set(win.index):
        assert units[pid] >= 5 and progs[pid] != ""  # ORS 456.250 gate: 5+ units and a covered program
    assert r["cal"]["push_window_open_count"] == int(leads["signals"].str.contains("push_window_open").sum()) >= 1
    with_units = leads[leads["units"].astype(int) > 0]
    assert len(with_units) > 100 and (with_units["value_source"].str.startswith("ppu_band")).all() and (with_units["est_value"].astype(float) > 0).all()
    assert with_units["verify_flags"].str.contains("Missing Source").all()
    # the adapter's basis header excludes helper deadlines
    assert r["cal"]["helper_events"] > 0 and "helper deadlines" in r["cal"]["header"]
    assert r["cal"]["vintage"] == "20261002" and r["cal"]["vintage_source"] == "filename"
