# Recap Math

Screening-grade arithmetic used by `scripts/plb/recap_math.py` for the agency's own recapitalization decisions: restricted NOI, loan constant and amortized balance, the recast / recap gap, a qualified-contract price band, and recapture exposure. This is a screen, not an underwrite: every output carries a basis label, and `recap_committee` / `nofa_offer` leads hand off to `sizing-lihtc-permanent-debt` (capacity) and `front-door-lihtc-underwriting` (the recap itself). Formula definitions follow `multifamily-underwriting-formulas`; do not redefine them elsewhere. The buyer-side refinance test and inferred maturity from lender type are gone: the agency's own notes are RECORDED and the question is what the restricted NOI can carry after a recast, not whether an owner can refinance.

## Contents

1. Scope and when each function runs
2. Restricted NOI
3. Loan constant and amortized balance
4. Recap gap (recast sizing)
5. Qualified-contract price band (memo only)
6. Recapture exposure
7. Worked examples
8. What this math never does

---

## 1. Scope and when each function runs

| function | runs for | output column | basis |
|---|---|---|---|
| `restricted_noi` | any lead when `rent-limits.json` is populated; blank otherwise with `Missing Source — Request Document` (rent roll / operating statement from the agency file) | `est_restricted_noi`, `noi_source` | `benchmark_estimate` unless an agency-held operating statement supplies it (`agency_file`) |
| `recap_gap` | **our_book rows only**, with `recap_status` in {announced, under_application}; never universe_not_held | `recap_gap_estimate` | ESTIMATED |
| `qc_price_band` | inside the `qc_admin` memo only (qc_marketing_plan); never on cards, tabs or Board_Totals | memo text | ESTIMATED, "budget order of magnitude, superseded by the owner's certification" |
| `recapture_exposure` | every book row with `recapture_type != none` | `recapture_exposure`, feeds `public_grant_at_risk` | RECORDED inputs, DERIVED output |
| `loan_constant`, `amortized_balance`, `noi_proxy`, `value_proxy` | helpers | | |

There is no `est_value` on the lead. A restricted value (`value_proxy(restricted_noi, cap_rate_affordable)`) appears only inside the recap memo as the as-restricted collateral context for a resubordination.

## 2. Restricted NOI

```
restricted_noi(ami_units, max_rents, hap_rent = None, vacancy = 0.05, opex_ratio = 0.50, hap_units = 0.0)
  GPR = sum over AMI buckets (units_b x max_rent_b x 12) + hap_units x hap_contract_rent x 12
  EGI = GPR x (1 - vacancy)              # vacancy_hap_units (0.03) on HAP units
  NOI = EGI x (1 - opex_ratio)           # opex_ratio_affordable 0.50 or units x opex_per_unit_regulated, whichever is higher
```

Inputs: AMI buckets from the inventory (descriptive; when they do not reconcile to Total Units use restricted_units x the 60% rent as the single band and record `noi_source = benchmark_estimate_single_band`); max rents from the pack `rent-limits.json` (MTSP, net of utility allowance); HAP contract rent when the agency file has it. Opex from `opex_per_unit_regulated` (OHCS FY24 $8,198 inflated; verify). Benchmarks date surfaces in the Assumptions tab.

## 3. Loan constant and amortized balance

```
i = annual_rate / 12
loan_constant(rate, am = 360) = 12 x i / (1 - (1 + i)^-am)      # check: loan_constant(0.0615, 360) ~= 0.0731; 0% rate -> 12 / am
amortized_balance(P0, annual_rate, n_months = 360, k_months, io_months = 0)
   k <= io_months: P0 ; else k' = k - io_months; P0 x ((1+i)^n - (1+i)^k') / ((1+i)^n - 1)   # 0% rate: P0 x (1 - k'/n)
```

Used to check a reported `upb` against origination terms (flag `Verify — Conflicting Sources` when they differ by more than 15%) and to project the balance at a proposed extension date. For deferred / residual-receipts notes the balance is `upb + accrued_interest` as the ledger states it; never recompute accruals from a rate.

## 4. Recap gap (recast sizing)

```
recap_gap(upb, restricted_noi, senior_dscr = 1.15, senior_rate, am = 360, existing_senior_upb = 0, rehab_need = 0)
  supportable_senior_ds   = restricted_noi / senior_dscr
  supportable_senior_debt = supportable_senior_ds / loan_constant(senior_rate, am)
  uses                    = existing_senior_upb + upb_to_be_retired_or_resubordinated + rehab_need
  gap                     = max(0, uses - supportable_senior_debt)
```

`senior_dscr` from pack `senior_dscr_floor` 1.15 (`sizing-lihtc-permanent-debt` convention; mandatory soft debt vs residual receipts handled there); `senior_rate` from the pack or the proposed senior lender. The scenario pair handed to `sizing-lihtc-permanent-debt` is: before recast (our note hard-pay, `mandatory_soft_debt_annual` = our current debt service) and after recast (our note residual receipts / 0% / extended, `residual_receipts_soft_debt`). The agency decides the recast; the sibling measures the capacity; this function only frames the order of magnitude for the committee memo. Output is ESTIMATED and printed as a range (+/- 15%).

## 5. Qualified-contract price band (memo only)

```
qc_price_band(outstanding_debt, adjusted_investor_equity, other_capital_contributions, cash_distributed, fmv_market_units = 0)
  qc_price = outstanding_debt + adjusted_investor_equity + other_capital_contributions - cash_distributed + fmv_market_units
```

Per IRC 42(h)(6)(F) and Treas. Reg. 1.42-18 (verify; COLA adjustment of investor equity and the "low-income portion" definition were not read in this build). Inputs come from the agency's own soft-debt UPB plus reported equity; the owner's QC price certification is the document to request and supersedes this band. ESTIMATED; appears only inside the `qc_marketing_plan` memo as the budget order of magnitude for presenting a bona fide contract.

## 6. Recapture exposure

```
recapture_exposure(amount, start, end, as_of, method, fmv = None)
  full                -> amount                                   (while as_of < end)
  prorata_reducing    -> amount x (years_remaining / total_years)  (HOMEBUYER assistance only: 24 CFR 92.254(a)(5)(ii) straight-line; verify)
  forgiveness_schedule-> amount x (1 - share_forgiven_to_date)     (schedule from the loan documents; else flag)
  cdbg_fmv_share      -> fmv x (cdbg_share)                        (24 CFR 570.505; requires fmv input, else flag Missing Source)
  none                -> 0
```

`public_grant_at_risk` = sum of `recapture_exposure` on matched / self_owned book rows. Default method per program comes from `agency-profiles.yaml` `recapture_methods` (HOME **full**, HOME_HOMEBUYER prorata_reducing, CDBG cdbg_fmv_share, HTF full, default full); the extract's `recapture_method` column overrides. Rental HOME is `full` because 24 CFR 92.503(b) requires the PJ to repay ALL HOME funds invested in a project that does not meet its 92.252 affordability requirements for the full period; 92.254 recapture / resale (and its pro-rata reduction) applies only to homebuyer assistance. Use `forgiveness_schedule` only when the PJ's RECORDED written agreement states one (the agreement may provide otherwise and then governs). A RECAPTURE_TRIGGER event (sale, payoff, foreclosure inside the period) makes the current exposure the demand amount in `covenant_recapture_review`.

## 7. Worked examples

**Recast (the `_selftest`).** Our note: $1,200,000 residual receipts, matures 2031-06-30 (RECORDED). Restricted NOI $486,000 (benchmark_estimate). Senior refinance at 6.15%, 30-year amortization, DSCR 1.15: supportable debt service $422,609; loan constant 0.0731; supportable senior $5.78M. Uses: existing senior $5.9M payoff + $900k rehab = $6.8M. Gap ~$1.0M, ESTIMATED (+/- 15%). Lever: resubordinate our $1.2M, extend coterminous with the new senior, fund the gap from a 0% recap or a 4% gap award (`zero_pct_recap_term_sheet`, `loan_extension_recast_memo`).

**Rental HOME repayment.** GOING 42, Portland: rental HOME loan $1,100,000, affordability period 2018-09-08 to 2058-09-08 (40 years, RECORDED), `recapture_type` home_rental_repayment, method `full`. As of 2026-10-04 the exposure is the full $1,100,000 -> `public_grant_at_risk` (24 CFR 92.503(b): all HOME funds invested are repayable when the 92.252 period is not met; verify). A pro-rata figure (~$878,000 at 31.9 of 40 years) would understate the PJ's exposure by $222,000: that arithmetic belongs to homebuyer recapture only.

**Homebuyer prorata (contrast).** A $60,000 HOME homebuyer subsidy with a 10-year recapture period 2022-01-01 to 2032-01-01, method prorata_reducing: as of 2026-10-04, 5.24 years remain -> exposure ~$31,400 (24 CFR 92.254(a)(5)(ii); verify).

**Sumner Street Flats** (PJ-only fixture): rental HOME $480,000, `full` (92.503(b)); AFFORDABILITY_PERIOD_END 2029-06-30 RECORDED (32.9 months) -> clock 14 x 1.0, capital 10 x 1.0, units 8 x 1.0 (12 units_assisted) ~ 32 PLAN; `recapture_exposure` $480,000; `INSPECTION_DUE` if `last_inspection_date` is given (5-25 units -> +24 months per 24 CFR 92.504(d), verify).

## 8. What this math never does

- No market value, price per unit, LTV, refinance gap or equity cushion on any lead (buyer-side screens removed).
- No inferred maturities from lender type; the agency's own notes are RECORDED and a senior maturity is REPORTED from the extract or RECORDED from HUD FHASL.
- No QC price on a card or in Board_Totals.
- No recap gap for a property the agency does not hold.
