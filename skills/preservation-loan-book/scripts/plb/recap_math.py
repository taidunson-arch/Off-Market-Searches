"""Recapitalization and recapture math (screening grade only).

Formulas follow `multifamily-underwriting-formulas`; constants come from the jurisdiction pack's market-params.json.
This module never produces an underwriting verdict: it sizes the gap an agency would have to fill when a restricted
asset is recapitalized, and the dollars of grant exposure a recapture clause protects. Authoritative sizing belongs to
`sizing-lihtc-permanent-debt` and `front-door-lihtc-underwriting`.

Run `python -m plb.recap_math --selftest` (from scripts/) for a worked example.
"""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, Optional

from .schema import param


def loan_constant(rate: float, am: int = 360) -> float:
    """Annual loan constant for a fully amortizing loan: 12 * r / (1 - (1+r)^-n), r monthly."""
    if am <= 0:
        return rate  # interest-only
    r = rate / 12.0
    if r == 0:
        return 12.0 / am
    return 12.0 * r / (1.0 - (1.0 + r) ** (-am))


def amortized_balance(P0: float, annual_rate: float, n_months: int = 360, k_months: int = 0, io_months: int = 0) -> float:
    """Outstanding balance after k payments on a level-payment loan with an optional IO period."""
    if k_months <= io_months:
        return float(P0)
    k = k_months - io_months
    if n_months <= 0:
        return float(P0)
    i = annual_rate / 12.0
    if i == 0:
        return max(0.0, P0 * (1 - k / n_months))
    if k >= n_months:
        return 0.0
    return P0 * (((1 + i) ** n_months - (1 + i) ** k) / ((1 + i) ** n_months - 1))


def noi_proxy(units: float, rent: float, vacancy: float, opex_ratio: float) -> float:
    return float(units) * float(rent) * 12.0 * (1.0 - vacancy) * (1.0 - opex_ratio)


def restricted_noi(ami_units: Dict[str, float], max_rents: Dict[str, float], hap_rent: Optional[float] = None,
                   vacancy: float = 0.05, opex_ratio: float = 0.50, hap_units: float = 0.0) -> float:
    """Restricted NOI for a regulated asset: sum(units_at_band * max_rent_band) + HAP units at contract rent."""
    gpr = 0.0
    for band, n in ami_units.items():
        gpr += float(n or 0) * float(max_rents.get(band, 0.0)) * 12.0
    if hap_rent and hap_units:
        gpr += float(hap_units) * float(hap_rent) * 12.0
    return gpr * (1.0 - vacancy) * (1.0 - opex_ratio)


def value_proxy(noi: Optional[float], cap_rate: Optional[float]) -> Optional[float]:
    if noi is None or not cap_rate:
        return None
    return round(noi / cap_rate, 0)


def recap_gap(upb: Optional[float], restricted_noi_value: Optional[float], senior_dscr: float = 1.15, senior_rate: float = 0.059,
              am: int = 360, rehab_need: float = 0.0) -> Dict[str, Optional[float]]:
    """Supportable senior debt on restricted NOI and the gap the agency must fill (our_book / recap rows only).

    supportable_senior = NOI / (DSCR * constant(senior_rate))
    gap = max(0, upb + rehab_need - supportable_senior)   (our note resubordinated or recast counts as a use)
    Returns None metrics when inputs are missing; never fabricates.
    """
    out: Dict[str, Optional[float]] = {"senior_rate": round(senior_rate, 5), "constant": round(loan_constant(senior_rate, am), 5),
                                       "supportable_senior": None, "gap": None, "dscr_on_upb": None}
    if restricted_noi_value is None or restricted_noi_value <= 0:
        return out
    const = loan_constant(senior_rate, am)
    out["supportable_senior"] = round(restricted_noi_value / (senior_dscr * const), 0)
    if upb is not None:
        out["gap"] = round(max(0.0, float(upb) + float(rehab_need or 0) - out["supportable_senior"]), 0)
        if upb > 0:
            out["dscr_on_upb"] = round(restricted_noi_value / (float(upb) * const), 3)
    return out


def qc_price_band(outstanding_debt: Optional[float], investor_equity: Optional[float], other_capital: float = 0.0,
                  cash_distributed: float = 0.0, equity_cola_factor: float = 1.0) -> Dict[str, Any]:
    """ESTIMATED qualified-contract price order of magnitude per IRC 42(h)(6)(F): debt + adjusted investor equity + other
    capital - cash distributed (plus FMV of market units, not modeled). Used only inside the qc_admin memo as a budget
    figure superseded by the owner's certification; never on cards or Board_Totals."""
    if outstanding_debt is None and investor_equity is None:
        return {"qc_price_estimate": None, "basis": "ESTIMATED", "note": "inputs missing; request the owner's QC price certification"}
    est = float(outstanding_debt or 0) + float(investor_equity or 0) * float(equity_cola_factor) + float(other_capital or 0) - float(cash_distributed or 0)
    return {"qc_price_estimate": round(max(0.0, est), 0), "basis": "ESTIMATED",
            "note": "IRC 42(h)(6)(F) formula without FMV of market units; superseded by the owner's certification (Treas. Reg. 1.42-18, verify)"}


def recapture_exposure(amount: Optional[float], start: Optional[date], end: Optional[date], as_of: date, method: str = "full",
                       fmv: Optional[float] = None, fmv_share: Optional[float] = None) -> Dict[str, Any]:
    """Dollars of grant the agency can still recapture as of `as_of`.

    full                : amount until end, 0 after
    prorata_reducing    : amount x (years remaining / total years), straight-line. HOMEBUYER assistance only (24 CFR 92.254(a)(5)(ii)
                          recapture); RENTAL HOME uses `full` because 24 CFR 92.503(b) requires repayment of all HOME funds invested when
                          the 92.252 affordability period is not met, unless the RECORDED written agreement states a schedule
    forgiveness_schedule: same arithmetic as prorata_reducing (annual forgiveness)
    cdbg_fmv_share      : fmv x fmv_share until end (24 CFR 570.505); flag when fmv is missing
    none                : 0
    """
    out: Dict[str, Any] = {"exposure": None, "method": method or "none", "flag": ""}
    m = (method or "none").lower()
    if m == "none":
        out["exposure"] = 0.0
        return out
    if end is not None and as_of > end:
        out["exposure"] = 0.0
        return out
    if m == "cdbg_fmv_share":
        if fmv is None or fmv_share is None:
            out["flag"] = "Missing Source — Request Document: current FMV for CDBG change-of-use share"
            return out
        out["exposure"] = round(float(fmv) * float(fmv_share), 0)
        return out
    if amount is None:
        out["flag"] = "Missing Source — Request Document: recapture amount"
        return out
    if m == "full":
        out["exposure"] = round(float(amount), 0)
        return out
    if m in ("prorata_reducing", "forgiveness_schedule"):
        if start is None or end is None or end <= start:
            out["exposure"] = round(float(amount), 0)
            out["flag"] = "Needs Anchor Date: recapture_start / recapture_end for prorata reduction"
            return out
        total = (end - start).days
        remaining = max(0, (end - as_of).days)
        out["exposure"] = round(float(amount) * remaining / total, 0)
        return out
    out["flag"] = f"unknown recapture_method {method}"
    return out


def _selftest() -> None:
    from .schema import DEFAULT_MARKET_PARAMS as P
    print("Worked example A: 60-unit restricted asset, our 0% residual-receipts note UPB $1.2M, restricted NOI $310,000")
    noi = 310_000.0
    r = recap_gap(1_200_000, noi, senior_dscr=float(param(P, "senior_dscr_floor", 1.15)), senior_rate=float(param(P, "senior_rate_default", 0.059)))
    for k, v in r.items():
        print(f"  {k:<20}{v}")
    print("  reading: supportable senior debt at 1.15x covers NOI; the gap is what a 4% recap or 0% recast must fill.")
    print("Worked example B: rental HOME loan $1,100,000, affordability 2018-09-08 .. 2058-09-08, as of 2026-10-04")
    e = recapture_exposure(1_100_000, date(2018, 9, 8), date(2058, 9, 8), date(2026, 10, 4), "full")
    print(f"  exposure {e['exposure']:,.0f}  ({e['method']}; 24 CFR 92.503(b): all HOME funds repayable while the 92.252 period runs, verify)")
    h = recapture_exposure(60_000, date(2022, 1, 1), date(2032, 1, 1), date(2026, 10, 4), "prorata_reducing")
    print(f"  homebuyer contrast: $60,000 HOME homebuyer subsidy, 10-year prorata_reducing -> exposure {h['exposure']:,.0f} (24 CFR 92.254(a)(5)(ii), verify)")
    print(f"  constant(5.90%)    {loan_constant(0.059):.5f}")


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        _selftest()
    else:
        print(__doc__)
