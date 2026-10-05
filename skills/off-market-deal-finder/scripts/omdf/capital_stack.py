"""Capital-stack screening math (screening grade only).

Formulas follow `multifamily-underwriting-formulas`; constants come from the jurisdiction pack's
market-params.json and `multifamily-benchmarks`. This module never produces an underwriting
verdict: it sizes the refinance gap so a lead can be ranked, and every output carries the
basis of its inputs. Authoritative sizing belongs to `sizing-conventional-multifamily-debt`
and `sizing-lihtc-permanent-debt`.

Run `python -m omdf.capital_stack --selftest` (from scripts/) for a worked example.
"""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, Optional, Tuple

from .dates import add_years
from .schema import DEFAULT_LENDER_TERMS, param


def loan_constant(rate: float, am: int = 360) -> float:
    """Annual loan constant for a fully amortizing loan: 12 * r / (1 - (1+r)^-n), r monthly."""
    if am <= 0:
        return rate  # interest-only
    r = rate / 12.0
    if r == 0:
        return 12.0 / am
    return 12.0 * r / (1.0 - (1.0 + r) ** (-am))


def amortized_balance(P0: float, annual_rate: float, n_months: int = 360, k_months: int = 0, io_months: int = 0) -> float:
    """Outstanding balance after k payments on a level-payment loan with an optional IO period.

    balance_k = P0 * ((1+i)^n - (1+i)^k) / ((1+i)^n - 1), i monthly, counting only amortizing months.
    """
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
    """NOI = units * rent * 12 * (1 - vacancy) * (1 - opex_ratio)."""
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


def refi_test(noi: Optional[float], upb: Optional[float], value: Optional[float], params: Dict[str, Any],
              note_rate: Optional[float] = None, affordable: bool = False) -> Dict[str, Optional[float]]:
    """Refinance-gap screen.

    max_loan  = min(noi / (dscr_floor * constant(refi_rate)), noi / debt_yield_floor, ltv_max * value)
    refi_gap  = upb - max_loan ; refi_gap_pct = refi_gap / upb
    dscr_refi = noi / (upb * constant(refi_rate)) ; ltv = upb / value ; debt_yield = noi / upb
    equity_cushion_pct = (value - upb) / value ; rate_spread_bp = (refi_rate - note_rate) * 1e4
    Returns None for any metric whose inputs are missing; never fabricates.
    """
    ust10 = param(params, "ust10", 0.0415)
    spread_bp = param(params, "refi_spread_bp", 175)
    refi_rate = float(ust10) + float(spread_bp) / 1e4
    dscr_floor = param(params, "dscr_floor_affordable" if affordable else "dscr_floor_market", 1.15 if affordable else 1.25)
    dy_floor = param(params, "debt_yield_floor", 0.08)
    ltv_max = param(params, "ltv_max_affordable" if affordable else "ltv_max_market", 0.80 if affordable else 0.70)
    const = loan_constant(refi_rate, 360)
    out: Dict[str, Optional[float]] = {
        "refi_rate": round(refi_rate, 5), "constant": round(const, 5), "max_loan": None, "refi_gap": None,
        "refi_gap_pct": None, "dscr_refi": None, "ltv": None, "debt_yield": None, "equity_cushion_pct": None,
        "rate_spread_bp": None,
    }
    if noi is not None and noi > 0:
        caps = [noi / (dscr_floor * const), noi / dy_floor]
        if value:
            caps.append(ltv_max * value)
        out["max_loan"] = round(min(caps), 0)
    if upb is not None and upb > 0:
        if out["max_loan"] is not None:
            out["refi_gap"] = round(upb - out["max_loan"], 0)
            out["refi_gap_pct"] = round((upb - out["max_loan"]) / upb, 4)
        if noi is not None:
            out["dscr_refi"] = round(noi / (upb * const), 3)
            out["debt_yield"] = round(noi / upb, 4)
        if value:
            out["ltv"] = round(upb / value, 4)
            out["equity_cushion_pct"] = round((value - upb) / value, 4)
    if note_rate is not None:
        out["rate_spread_bp"] = round((refi_rate - float(note_rate)) * 1e4, 0)
    return out


def inferred_maturity(orig_date: date, lender_type: str, lender_terms: Optional[Dict[str, Dict[str, Any]]] = None
                      ) -> Tuple[date, date, date, str]:
    """(point, window_start, window_end, basis=ESTIMATED) from recording date + lender-type term table."""
    terms = (lender_terms or DEFAULT_LENDER_TERMS).get(lender_type) or DEFAULT_LENDER_TERMS["unknown"]
    point = add_years(orig_date, int(terms["typical"]))
    return point, add_years(orig_date, int(terms["min_term"])), add_years(orig_date, int(terms["max_term"])), "ESTIMATED"


def value_proxy(noi: Optional[float], cap_rate: Optional[float]) -> Optional[float]:
    if noi is None or not cap_rate:
        return None
    return round(noi / cap_rate, 0)


def _selftest() -> None:
    from .schema import DEFAULT_MARKET_PARAMS as P
    print("Worked example: 60-unit Class C Portland asset, bank loan recorded 2019-06-15 for $6.2M at 4.25%")
    noi = noi_proxy(60, param(P, "asking_rent_per_unit"), param(P, "vacancy"), param(P, "opex_ratio_market"))
    value = value_proxy(noi, param(P, "cap_rate_class_c"))
    bal = amortized_balance(6_200_000, 0.0425, 360, k_months=87)
    print(f"  NOI proxy          {noi:,.0f}  (units*rent*12*(1-vac)*(1-opex))")
    print(f"  Value proxy        {value:,.0f}  (NOI / class C cap {param(P, 'cap_rate_class_c')})")
    print(f"  Balance @87 mo     {bal:,.0f}  (amortized from $6.2M at 4.25%/30y)")
    r = refi_test(noi, bal, value, P, note_rate=0.0425)
    for k, v in r.items():
        print(f"  {k:<20}{v}")
    pt, ws, we, basis = inferred_maturity(date(2019, 6, 15), "bank_cu")
    print(f"  inferred maturity  {pt} window {ws}..{we} basis {basis}")
    print(f"  constant(6.15%)    {loan_constant(0.0615):.5f}  (expected ~0.07313)")


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        _selftest()
    else:
        print(__doc__)
