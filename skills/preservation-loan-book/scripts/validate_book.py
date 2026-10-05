#!/usr/bin/env python3
"""Reconcile a generated HFA run against independent agency control totals and adjudicated cases."""
import argparse
import json
from pathlib import Path
import pandas as pd


def reconcile(run_dir, controls):
    run = Path(run_dir)
    positions = pd.read_csv(run/"instruments.csv", dtype=str, keep_default_na=False)
    leads = pd.read_csv(run/"leads_scored.csv", dtype=str, keep_default_na=False)
    risks = pd.read_csv(run/"risk_dimensions.csv", dtype=str, keep_default_na=False)
    book = leads[leads["universe"] == "our_book"]
    loans = positions[positions["book_kind"] == "loan"]
    unknown_upb = int(pd.to_numeric(loans["public_upb"], errors="coerce").isna().sum())
    actual = {"book_properties": int(book["property_id"].nunique()), "instruments": int(len(positions)),
              "public_upb": float(pd.to_numeric(loans["public_upb"], errors="coerce").sum()) if not unknown_upb else None,
              "unknown_loan_balances": unknown_upb}
    if not str(controls.get("source") or "").strip() or not str(controls.get("reviewer") or "").strip():
        raise ValueError("independent controls require a source and reviewer")
    expected = controls.get("totals") or {}
    if not expected:
        raise ValueError("at least one independent control total is required")
    checks=[]
    for key,value in expected.items():
        if key not in actual:
            raise ValueError(f"unsupported control: {key}")
        tolerance = float(controls.get("dollar_tolerance", 0.01)) if key == "public_upb" else 0
        if tolerance < 0:
            raise ValueError("tolerance cannot be negative")
        checks.append({"control":key,"expected":value,"actual":actual[key],"passed":actual[key] is not None and abs(actual[key]-float(value)) <= tolerance})
    by_pid = risks.set_index("property_id").to_dict(orient="index")
    for case in controls.get("adjudicated_cases", []):
        for axis,expected_value in case["expected"].items():
            observed=by_pid.get(case["property_id"],{}).get(axis)
            checks.append({"control":f"{case['property_id']}:{axis}","expected":expected_value,"actual":observed,"passed":observed==expected_value})
    return {"source":controls["source"],"reviewer":controls["reviewer"],"run_dir":str(run.resolve()),"passed":all(r["passed"] for r in checks),"checks":checks}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-dir",required=True)
    ap.add_argument("--controls",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    report=reconcile(a.run_dir,json.loads(Path(a.controls).read_text(encoding="utf-8")))
    Path(a.out).write_text(json.dumps(report,indent=2),encoding="utf-8")
    print("PASS" if report["passed"] else "FAIL")
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
