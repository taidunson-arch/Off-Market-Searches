"""Executes evals/evals.json against the sample run in references/sample-output/ (hfa, metro_core, 10-year horizon, as-of
2026-10-04, synthetic servicing fixture joined to the real OHCS inventory).

* `common_assertions` and each eval's `assertions` run against the committed sample files (leads_scored.csv,
  units_at_risk.json, calendar_summary.json, brief.md, board_packet.md, servicing_unmatched.csv, the two workbooks).
* `variant_assertions` run against a run regenerated under the eval's `run_variant` (agency_profile / book / coverage)
  with the real OHCS CSV (env OHCS_CSV or the authoring-session path); skipped when the CSV is absent.
* `test_eval_properties_exist_in_real_inventory` re-verifies that every named OHCS property is a real row.

The assertion mini-DSL (see evals.json): {"file", "where" {column: value}, "column", "op", "value", "path", "factor",
"all_rows"} with ops eq / ne / eq_ci / eq_num / in / not_in / contains / not_contains / contains_all / not_contains_any /
between / gte / lte / empty / not_empty / factor_points_between / no_caps / count_where / columns_absent /
columns_present / column_values_subset / no_pii / contains_text / contains_text_ci / regex / contains_header_verbatim /
board_totals_agree. Skipped (not failed) when the sample files are missing.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from typing import Any, Dict, List
from unittest import SkipTest

import openpyxl
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
ROOT = os.path.dirname(SCRIPTS)
sys.path.insert(0, SCRIPTS)
from _fixture_runs import FX, PACK, REAL, AS_OF  # noqa: E402
from plb.pii import assert_no_pii  # noqa: E402

EVALS_PATH = os.path.join(ROOT, "evals", "evals.json")
SAMPLE = os.path.join(ROOT, "references", "sample-output")
WORKBOOK = "Portland_TriCounty_Preservation_LoanBook_10yr.xlsx"
PACKET = "Portland_TriCounty_Board_Packet.xlsx"
BAND_LABELS = {"BEYOND": "beyond horizon", "stale_contract_date_verify": "stale contract date — verify", "no_dated_cliff": "no dated cliff"}
_CACHE: Dict[str, Any] = {}


def _evals() -> Dict[str, Any]:
    if "evals" not in _CACHE:
        _CACHE["evals"] = json.load(open(EVALS_PATH, encoding="utf-8"))
    return _CACHE["evals"]


def _sample_ctx() -> Dict[str, Any]:
    if "sample" in _CACHE:
        return _CACHE["sample"]
    if not os.path.exists(os.path.join(SAMPLE, "leads_scored.csv")):
        raise SkipTest("references/sample-output/leads_scored.csv absent; regenerate with run_agency_pipeline.py")
    _CACHE["sample"] = _load_ctx(SAMPLE, WORKBOOK, PACKET)
    return _CACHE["sample"]


def _load_ctx(d: str, workbook: str = "", packet: str = "") -> Dict[str, Any]:
    def csv(name):
        p = os.path.join(d, name)
        return pd.read_csv(p, dtype=str, keep_default_na=False) if os.path.exists(p) else None

    def js(name):
        p = os.path.join(d, name)
        return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None

    def txt(name):
        p = os.path.join(d, name)
        return open(p, encoding="utf-8").read() if os.path.exists(p) else None

    return {"dir": d, "leads_scored.csv": csv("leads_scored.csv"), "servicing_unmatched.csv": csv("servicing_unmatched.csv"),
            "units_at_risk.json": js("units_at_risk.json"), "calendar_summary.json": js("calendar_summary.json"),
            "brief.md": txt("brief.md"), "board_packet.md": txt("board_packet.md"),
            "workbook": os.path.join(d, workbook) if workbook and os.path.exists(os.path.join(d, workbook)) else "",
            "packet": os.path.join(d, packet) if packet and os.path.exists(os.path.join(d, packet)) else ""}


def _variant_ctx(variant: Dict[str, Any]) -> Dict[str, Any]:
    key = "variant|" + json.dumps(variant, sort_keys=True)
    if key in _CACHE:
        return _CACHE[key]
    if not os.path.exists(REAL):
        raise SkipTest(f"real OHCS CSV absent ({REAL}); set OHCS_CSV to run the {variant['agency_profile']} variant")
    out = tempfile.mkdtemp(prefix=f"plb_eval_{variant['agency_profile']}_")
    prof = variant["agency_profile"]
    cmd = [sys.executable, os.path.join(SCRIPTS, "build_universe.py"), "--pack", PACK, "--mode", "metro_core", "--agency-profile", prof, "--ohcs", REAL,
           "--book", os.path.join(FX, variant["book"]), "--book-coverage", variant.get("book_coverage", "partial"), "--horizon-years", "10", "--as-of", AS_OF, "--out-dir", out]
    if variant.get("crosswalk", True) and prof != "pha_am":
        cmd += ["--crosswalk", os.path.join(FX, "book_crosswalk_sample.csv")]
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=SCRIPTS)
    assert p.returncode == 0, p.stderr[-4000:]
    p = subprocess.run([sys.executable, os.path.join(SCRIPTS, "score_preservation.py"), "--leads", os.path.join(out, "leads.csv"), "--events", os.path.join(out, "events.csv"),
                        "--pack", PACK, "--agency-profile", prof, "--horizon-years", "10", "--as-of", AS_OF, "--out", os.path.join(out, "leads_scored.csv")],
                       capture_output=True, text=True, cwd=SCRIPTS)
    assert p.returncode == 0, p.stderr[-4000:]
    _CACHE[key] = _load_ctx(out)
    return _CACHE[key]


# ---------------------------------------------------------------- assertion DSL
def _num(v) -> float:
    return float(str(v).replace(",", "").replace("$", ""))


def _rows(ctx, a) -> pd.DataFrame:
    df = ctx.get(a["file"])
    assert df is not None, f"{a['file']} missing in {ctx['dir']}"
    sub = df
    for col, val in (a.get("where") or {}).items():
        assert col in sub.columns, f"{a['file']} lacks column {col}"
        sub = sub[sub[col].astype(str).str.upper() == str(val).upper()]
    assert len(sub) >= 1, f"no row where {a.get('where')} in {a['file']}"
    return sub


def _path(obj, path: str):
    for part in path.split("."):
        assert isinstance(obj, dict) and part in obj, f"path {path} missing at {part}"
        obj = obj[part]
    return obj


def _list_items(cell: str) -> List[str]:
    return [x for x in re.split(r"[;,]", str(cell)) if x]


def _check_value(op: str, got, exp, label: str):
    s = "" if got is None else str(got)
    if op == "eq":
        assert s == str(exp), f"{label}: {s!r} != {exp!r}"
    elif op == "ne":
        assert s != str(exp), f"{label}: {s!r} should differ from {exp!r}"
    elif op == "eq_ci":
        assert s.lower() == str(exp).lower(), f"{label}: {s!r} != {exp!r}"
    elif op == "eq_num":
        assert abs(_num(s) - float(exp)) < 1e-6, f"{label}: {s} != {exp}"
    elif op == "in":
        assert s in [str(x) for x in exp], f"{label}: {s!r} not in {exp}"
    elif op == "not_in":
        assert s not in [str(x) for x in exp], f"{label}: {s!r} in {exp}"
    elif op == "contains":
        assert str(exp) in s, f"{label}: {exp!r} not in {s!r}"
    elif op == "not_contains":
        assert str(exp) not in s, f"{label}: {exp!r} unexpectedly in {s!r}"
    elif op == "contains_all":
        missing = [x for x in exp if str(x) not in s]
        assert not missing, f"{label}: missing {missing} in {s!r}"
    elif op == "not_contains_any":
        found = [x for x in exp if str(x) in s]
        assert not found, f"{label}: found {found} in {s!r}"
    elif op == "between":
        lo, hi = exp
        assert lo <= _num(s) <= hi, f"{label}: {s} not in [{lo}, {hi}]"
    elif op == "gte":
        assert _num(s) >= float(exp), f"{label}: {s} < {exp}"
    elif op == "lte":
        assert _num(s) <= float(exp), f"{label}: {s} > {exp}"
    elif op == "empty":
        assert s.strip() == "", f"{label}: expected empty, got {s!r}"
    elif op == "not_empty":
        assert s.strip() != "", f"{label}: expected a value"
    else:
        raise AssertionError(f"unknown op {op}")


def _board_rows_from_xlsx(path: str) -> Dict[str, Any]:
    ws = openpyxl.load_workbook(path, read_only=True)["Board_Totals"]
    rows = list(ws.iter_rows(values_only=True))
    out, in_all = {}, False
    for row in rows:
        if row[0] == "ALL":
            in_all = True
            continue
        if in_all and row[0] not in (None, ""):
            break
        if in_all and row[1] not in (None, "", "TOTAL"):
            out[str(row[1])] = row[2:]
    return out


def _board_totals_agree(ctx):
    uar = ctx["units_at_risk.json"]
    brief, packet = ctx["brief.md"], ctx["board_packet.md"]
    assert uar and brief, "units_at_risk.json / brief.md missing"
    h = uar["headline"]
    head = f"{h['properties']} properties / {h['units_at_risk']} restricted units / {h['hap_units_at_risk']} HAP units / {h['prac_units_at_risk']} PRAC units / {h['psh_units_at_risk']} PSH units"
    assert head in brief, f"brief headline differs from units_at_risk.json: {head}"
    if packet:
        assert head in packet, "board packet headline differs from units_at_risk.json"
    xl = _board_rows_from_xlsx(ctx["workbook"]) if ctx.get("workbook") else {}
    xp = _board_rows_from_xlsx(ctx["packet"]) if ctx.get("packet") else {}
    for band, vals in uar["by_owner_cliff_band"].items():
        label = BAND_LABELS.get(band, band)
        m = re.search(rf"^\| {re.escape(label)} \| (\d+) \| ([\d.]+) \| ([\d.]+) \|", brief, re.M)
        assert m, f"brief Board Totals lacks band {label}"
        assert int(m.group(1)) == vals["properties"] and float(m.group(2)) == float(vals["units_at_risk"]) and float(m.group(3)) == float(vals["hap_units_at_risk"]), band
        if packet:
            mp = re.search(rf"^\| ALL \| {re.escape(label)} \| (\d+) \| ([\d.]+) \|", packet, re.M)
            assert mp and int(mp.group(1)) == vals["properties"] and float(mp.group(2)) == float(vals["units_at_risk"]), f"board packet {band}"
        for name, tab in (("workbook", xl), ("packet", xp)):
            if tab:
                assert label in tab, f"{name} Board_Totals lacks {label}"
                assert int(tab[label][0]) == vals["properties"] and float(tab[label][1]) == float(vals["units_at_risk"]), f"{name} {band}"


def run_assertion(ctx: Dict[str, Any], a: Dict[str, Any], label: str = ""):
    op = a["op"]
    f = a.get("file", "")
    label = f"{label} {f} {a.get('where', '')} {a.get('column', '')} {op}".strip()
    if op == "board_totals_agree":
        return _board_totals_agree(ctx)
    if f in ("brief.md", "board_packet.md"):
        text = ctx.get(f)
        assert text, f"{f} missing"
        if op == "contains_text":
            assert a["value"] in text, f"{label}: {a['value']!r} not in {f}"
        elif op == "contains_text_ci":
            assert a["value"].lower() in text.lower(), f"{label}: {a['value']!r} not in {f}"
        elif op == "not_contains_any":
            found = [x for x in a["value"] if x in text]
            assert not found, f"{label}: {found} found in {f}"
        elif op == "regex":
            assert re.search(a["value"], text), f"{label}: /{a['value']}/ not found in {f}"
        elif op == "contains_header_verbatim":
            cal = ctx.get("calendar_summary.json") or {}
            header = cal.get("header")
            assert header and header in text, f"{label}: calendar header not quoted verbatim ({header!r})"
        else:
            raise AssertionError(f"unknown text op {op}")
        return
    if f == "units_at_risk.json":
        got = _path(ctx[f], a["path"])
        if op == "contains_all":
            assert all(x in got for x in a["value"]), f"{label}: {a['value']} not all in {got}"
        else:
            _check_value(op, got, a.get("value"), label)
        return
    df = ctx.get(f)
    assert df is not None, f"{f} missing"
    if op == "columns_absent":
        bad = [c for c in a["value"] if c in df.columns]
        assert not bad, f"{label}: forbidden columns present {bad}"
        return
    if op == "columns_present":
        missing = [c for c in a["value"] if c not in df.columns]
        assert not missing, f"{label}: columns missing {missing}"
        return
    if op == "column_values_subset":
        extra = set(df[a["column"]].astype(str)) - set(a["value"])
        assert not extra, f"{label}: unexpected values {sorted(extra)}"
        return
    if op == "no_pii":
        assert assert_no_pii(df) == [], f"{label}: PII columns present"
        return
    if op == "count_where":
        sub = df
        for col, val in a["where"].items():
            sub = sub[sub[col].astype(str) == str(val)]
        assert len(sub) == a["value"], f"{label}: count {len(sub)} != {a['value']}"
        return
    rows = _rows(ctx, a)
    targets = rows if a.get("all_rows") else rows.iloc[:1]
    for _, r in targets.iterrows():
        col = a["column"]
        assert col in rows.columns, f"{label}: column {col} missing"
        cell = r[col]
        if op == "factor_points_between":
            fj = json.loads(cell)
            pts = {x["name"]: float(x["points"]) for x in fj["factors"]}
            assert a["factor"] in pts, f"{label}: factor {a['factor']} missing"
            lo, hi = a["value"]
            assert lo - 1e-6 <= pts[a["factor"]] <= hi + 1e-6, f"{label}: {a['factor']} = {pts[a['factor']]} not in [{lo}, {hi}]"
        elif op == "no_caps":
            fj = json.loads(cell)
            assert not fj.get("caps"), f"{label}: caps present {fj.get('caps')}"
        else:
            _check_value(op, cell, a.get("value"), label)


def _run_eval(eval_id: str):
    ev = next(e for e in _evals()["evals"] if e["id"] == eval_id)
    ctx = _sample_ctx()
    for a in ev["assertions"]:
        run_assertion(ctx, a, eval_id)
    return ev


def _run_variant(eval_id: str):
    ev = next(e for e in _evals()["evals"] if e["id"] == eval_id)
    ctx = _variant_ctx(ev["run_variant"])
    for a in ev.get("variant_assertions", []):
        run_assertion(ctx, a, f"{eval_id}[{ev['run_variant']['agency_profile']}]")


# ---------------------------------------------------------------- tests
def test_evals_file_shape():
    ev = _evals()
    assert ev["skill_name"] == "preservation-loan-book" and len(ev["evals"]) == 5
    ids = [e["id"] for e in ev["evals"]]
    assert ids == ["E1_push_window_open_village_garden", "E2_hap_annual_vs_mahra_powell_plaza", "E3_home_only_cdbg_pj", "E4_pha_yards_union_station", "E5_our_loan_not_in_ohcs"]
    for e in ev["evals"]:
        for k in ("prompt", "agency_profile", "expected", "expected_output", "expectations", "assertions"):
            assert k in e and e[k], f"{e['id']} lacks {k}"
        assert e["agency_profile"] in ("hfa", "city_housing", "county", "pha_am", "cdbg_home")
        text = json.dumps(e)
        for banned in ("Tier A", "Tier B", "motivated seller", "approach angle", "skip trace", "IOI", "we buy"):
            assert banned not in text, f"{e['id']} carries buyer vocabulary {banned!r}"


def test_eval_properties_exist_in_real_inventory():
    if not os.path.exists(REAL):
        raise SkipTest("real OHCS CSV absent")
    df = pd.read_csv(REAL, encoding="utf-8-sig", dtype=str)
    names = set(df["Property Name"].astype(str).str.strip().str.upper())
    present = ["Village Garden Apartments", "Powell Plaza I", "Garden Grove Apartments", "Silvercrest Residence", "Yards at Union Station A", "Dawson Park Plaza",
               "Going 42", "Corey Hill", "Quartz Avenue Apts", "West Main Apartments 1", "Viewfinder, The", "Mary Ann, The"]
    for n in present:
        assert n.upper() in names, f"{n} not in the OHCS export"
    for n in ("Hollow Oak Commons", "Sumner Street Flats"):
        assert n.upper() not in names, f"{n} must be absent from the inventory (our-loan-not-in-OHCS eval)"
    vg = df[df["Property Name"] == "Village Garden Apartments"].iloc[0]
    assert vg["LATEST_Expiration_Date"] == "06/01/2029" and vg["Owner Type"] == "For-Profit" and vg["OHCS Funded?"] == "true"
    pp = df[df["Property Name"] == "Powell Plaza I"].iloc[0]
    assert pp["HUD Contract"] == "Housing Assistance Payment" and pp["HUD_MF_Expiration_Date"] == "03/31/2027" and pp["Rental_Assistance_Count"] == "47"
    ya = df[df["Property Name"] == "Yards at Union Station A"].iloc[0]
    assert ya["Owner Name"] == "Home Forward" and ya["LATEST_Expiration_Date"] == "01/01/2028" and ya["Total Units"] == "158"
    metro = df[df["County"].str.strip().str.title().isin(["Multnomah", "Washington", "Clackamas"]) & (df["Status"] == "Active")]
    prog = [c for c in df.columns if c.endswith("_Expiration_Date") and c not in ("LATEST_Expiration_Date", "HOME_Expiration_Date")]
    assert int((metro["HOME_Expiration_Date"].notna() & metro[prog].isna().all(axis=1)).sum()) == 0, "metro HOME-only rows expected to be 0"


def test_common_assertions_on_sample_run():
    ctx = _sample_ctx()
    for a in _evals()["common_assertions"]:
        run_assertion(ctx, a, "common")
    assert "## Run Summary" in ctx["brief.md"] and "## Board Totals" in ctx["brief.md"] and "## Intervention Queue" in ctx["brief.md"]
    cal = ctx["calendar_summary.json"]
    assert re.match(r"^RECORDED \d+ / REPORTED \d+ / DERIVED \d+ / ESTIMATED \d+ / PROXY \d+ / Suppressed \d+ / Rejected \d+ \| helper deadlines \d+ \(.*\) \| agency act-by \d+ \(next 90 days \d+\)$", cal["header"]), cal["header"]


def test_eval_E1_push_window_open_village_garden():
    _run_eval("E1_push_window_open_village_garden")


def test_eval_E2_hap_annual_vs_mahra_powell_plaza():
    _run_eval("E2_hap_annual_vs_mahra_powell_plaza")


def test_eval_E3_home_only_cdbg_pj():
    _run_eval("E3_home_only_cdbg_pj")


def test_eval_E3_variant_cdbg_home_profile():
    _run_variant("E3_home_only_cdbg_pj")


def test_eval_E4_pha_yards_union_station():
    _run_eval("E4_pha_yards_union_station")


def test_eval_E4_variant_pha_am_profile():
    _run_variant("E4_pha_yards_union_station")


def test_eval_E5_our_loan_not_in_ohcs():
    _run_eval("E5_our_loan_not_in_ohcs")


if __name__ == "__main__":
    sys.exit(subprocess.call([sys.executable, os.path.join(HERE, "run_tests.py"), "-k", "test_evals"]))
