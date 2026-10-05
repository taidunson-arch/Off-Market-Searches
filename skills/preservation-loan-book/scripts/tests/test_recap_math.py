"""Recap math: loan constant, amortization, restricted NOI, recap gap, recapture exposure; the buyer refinance test is gone."""
from __future__ import annotations

import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from plb import recap_math as R  # noqa: E402


def test_loan_constant_and_amortization():
    assert abs(R.loan_constant(0.0615) - 0.07313) < 1e-4
    assert R.loan_constant(0.05, 0) == 0.05
    assert R.amortized_balance(1_000_000, 0.05, 360, 0) == 1_000_000
    assert R.amortized_balance(1_000_000, 0.05, 360, 36, io_months=36) == 1_000_000
    assert 900_000 < R.amortized_balance(1_000_000, 0.05, 360, 60) < 930_000
    assert R.amortized_balance(1_000_000, 0.05, 360, 360) == 0.0


def test_restricted_noi_and_value_proxy():
    noi = R.noi_proxy(60, 1656, 0.071, 0.42)
    assert 640_000 < noi < 645_000
    assert R.value_proxy(noi, 0.064) == round(noi / 0.064, 0)
    assert R.restricted_noi({"60": 40, "50": 10}, {"60": 1200, "50": 1000}, hap_rent=1500, hap_units=10) > 0


def test_recap_gap_recast_example():
    r = R.recap_gap(1_200_000, 310_000, senior_dscr=1.15, senior_rate=0.059)
    assert r["supportable_senior"] is not None and r["supportable_senior"] > 3_000_000
    assert r["gap"] == 0.0 and r["dscr_on_upb"] > 3
    tight = R.recap_gap(6_000_000, 310_000, senior_dscr=1.15, senior_rate=0.059, rehab_need=500_000)
    assert tight["gap"] > 0
    assert R.recap_gap(1_000_000, None)["supportable_senior"] is None  # never fabricated


def test_recapture_exposure_methods():
    as_of = date(2026, 10, 4)
    # rental HOME: `full` while the 92.252 period runs (24 CFR 92.503(b)); the homebuyer prorata rule (92.254(a)(5)(ii)) stays available by name
    rental = R.recapture_exposure(1_100_000, date(2018, 9, 8), date(2058, 9, 8), as_of, "full")
    assert rental["exposure"] == 1_100_000 and rental["flag"] == ""
    pro = R.recapture_exposure(60_000, date(2022, 1, 1), date(2032, 1, 1), as_of, "prorata_reducing")
    assert 30_000 < pro["exposure"] < 32_500 and pro["flag"] == ""
    assert R.recapture_exposure(480_000, date(2019, 6, 30), date(2029, 6, 30), as_of, "prorata_reducing")["exposure"] < 480_000
    assert R.recapture_exposure(100_000, None, None, as_of, "full")["exposure"] == 100_000
    assert R.recapture_exposure(100_000, None, date(2020, 1, 1), as_of, "full")["exposure"] == 0.0
    assert R.recapture_exposure(None, None, None, as_of, "none")["exposure"] == 0.0
    cdbg = R.recapture_exposure(None, None, None, as_of, "cdbg_fmv_share")
    assert cdbg["exposure"] is None and cdbg["flag"].startswith("Missing Source")
    assert R.recapture_exposure(None, None, None, as_of, "cdbg_fmv_share", fmv=2_000_000, fmv_share=0.25)["exposure"] == 500_000


def test_qc_price_band_is_estimated_and_no_refi_test_survives():
    q = R.qc_price_band(5_000_000, 2_000_000, cash_distributed=250_000)
    assert q["basis"] == "ESTIMATED" and q["qc_price_estimate"] == 6_750_000
    assert R.qc_price_band(None, None)["qc_price_estimate"] is None
    assert not hasattr(R, "refi_test") and not hasattr(R, "inferred_maturity")
