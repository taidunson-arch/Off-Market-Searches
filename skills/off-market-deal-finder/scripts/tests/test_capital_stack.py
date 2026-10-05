"""Capital-stack math: loan constant, amortization, refi test, inferred maturity windows."""
from __future__ import annotations

import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from omdf import capital_stack as C  # noqa: E402
from omdf.schema import DEFAULT_MARKET_PARAMS  # noqa: E402


def test_loan_constant():
    assert abs(C.loan_constant(0.0615) - 0.07313) < 1e-4
    assert C.loan_constant(0.05, 0) == 0.05  # interest-only


def test_amortized_balance_edges():
    assert C.amortized_balance(1_000_000, 0.05, 360, 0) == 1_000_000
    assert C.amortized_balance(1_000_000, 0.05, 360, 36, io_months=36) == 1_000_000  # still in IO
    b = C.amortized_balance(1_000_000, 0.05, 360, 60)
    assert 900_000 < b < 930_000
    assert C.amortized_balance(1_000_000, 0.05, 360, 360) == 0.0


def test_refi_test_gap():
    noi = 600_000
    r = C.refi_test(noi, 9_000_000, 10_000_000, DEFAULT_MARKET_PARAMS, note_rate=0.035)
    assert r["max_loan"] is not None and r["refi_gap"] > 0 and 0 < r["refi_gap_pct"] < 1
    assert r["ltv"] == 0.9 and abs(r["debt_yield"] - 0.0667) < 1e-3 and r["rate_spread_bp"] > 150
    assert r["dscr_refi"] < 1.0
    r2 = C.refi_test(None, 9_000_000, None, DEFAULT_MARKET_PARAMS)
    assert r2["max_loan"] is None and r2["refi_gap_pct"] is None  # never fabricated


def test_noi_proxy_and_value():
    noi = C.noi_proxy(60, 1656, 0.071, 0.42)
    assert 640_000 < noi < 645_000
    assert C.value_proxy(noi, 0.064) == round(noi / 0.064, 0)
    rn = C.restricted_noi({"60": 40, "50": 10}, {"60": 1200, "50": 1000}, hap_rent=1500, hap_units=10)
    assert rn > 0


def test_inferred_maturity_window():
    pt, ws, we, basis = C.inferred_maturity(date(2019, 6, 15), "bank_cu")
    assert (pt, ws, we, basis) == (date(2026, 6, 15), date(2024, 6, 15), date(2029, 6, 15), "ESTIMATED")
    pt, ws, we, _ = C.inferred_maturity(date(2021, 9, 1), "debt_fund_bridge")
    assert pt == date(2024, 9, 1) and we == date(2026, 9, 1)
