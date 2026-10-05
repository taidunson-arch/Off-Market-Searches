# Capital-Stack Math

Screening-grade value, balance and refinance arithmetic used by `scripts/omdf/capital_stack.py` and quoted in the `Capital_Stack` workbook tab. This is a screen, not an underwrite: every output is labeled with its `basis`, and Tier A leads hand off to `underwriting-market-rate-multifamily`, `front-door-lihtc-underwriting` or `residential-deal-underwriter` for the real thing. Formula definitions follow `multifamily-underwriting-formulas`; do not redefine them elsewhere.

## Contents

1. Value proxies (three, by class)
2. NOI proxies
3. Loan constant and amortized balance
4. Inferred maturity from lender type
5. Refinance test
6. Interpretation bands
7. Lender-term table (summary)
8. Recorded-instrument image extraction schema
9. Worked example
10. What this math never does

---

## 1. Value proxies

Pick one per property, record it in `value_source`, and never silently mix them.

| class | proxy | formula | value_source label | notes |
|---|---|---|---|---|
| sfr_small_res | RMV-calibrated | `est_value = RMV x neighborhood_sales_ratio` where `RMV = ROLLLAND + ROLLIMP` and `sales_ratio = median(arm's-length SALE_PRICE / prior-year RMV)` over the ZIP or neighborhood, trailing 12-24 months | `rmv_calibrated` | In Measure-50 states (Oregon) Assessed Value is capped and commonly 50-55% of market; never scale AV. AVM (PropStream, ATTOM, HouseCanary) replaces this when available: label `avm:<vendor>`. |
| market_rate_mf | income proxy | `est_value = est_noi / cap_rate` with cap rate from pack `market-params.json` (class-specific when year_built/class known, else market average) | `income_proxy` | RMV is only a +/-25% sanity band. Hand off to `comp-analyzer` / `cap-rate-comp-selector` to replace. |
| affordable_regulated | restricted income proxy | `est_value = restricted_noi / cap_rate_affordable` (pack: Class C cap + 100 bp) | `restricted_income_proxy` | Value as-restricted, not as-converted. Report conversion value separately only when extended use ends inside the horizon, labeled `conversion_scenario`. |
| any | price-per-unit band | `est_value = units x price_per_unit` (pack `price_per_unit_avg`) | `ppu_band` | Fallback when units known but rent/opex unknown. Lowest quality; flag `Missing Source — Request Document` for rent roll. `ohcs_inventory_targets.py` applies it to every OHCS lead until `rent-limits.json` is populated (then `restricted_income_proxy`); `normalize_assessor_taxlots.py` writes `rmv_calibrated` from the roll. |

Sanity rule: if `est_value` falls outside 0.6x-1.6x of RMV (where RMV exists), set `Verify — Conflicting Sources` on the value and show both.

## 2. NOI proxies

```
noi_proxy(units, rent, vacancy, opex_ratio)
  GPR   = units x rent x 12
  EGI   = GPR x (1 - vacancy)
  NOI   = EGI x (1 - opex_ratio)

restricted_noi(ami_units, max_rents, hap_rent, vacancy, opex_ratio = 0.50)
  GPR   = sum over AMI buckets (units_b x max_rent_b x 12) + hap_units x hap_contract_rent x 12 + market_units x market_rent x 12
  EGI   = GPR x (1 - vacancy)              # vacancy for HAP units may be set to 0.03
  NOI   = EGI x (1 - opex_ratio)           # regulated opex ratio 0.50 or pack opex_per_unit_regulated x units, whichever is higher
```

Inputs by preference (record in `noi_source`): reported NOI from a tape (`tape_reported`, weighs 1.0 in scoring) > rent roll / T-12 supplied by user (`user_supplied`) > benchmark rent x units (`benchmark_estimate`, weighs 0.7). Rents: ZIP-level median by bedroom (Apartment List / Zumper / RentCafe three-source median) with a 3-8% haircut for Class C in-place; HUD SAFMR as the conservative floor; LIHTC max rents by AMI from the HFA rent-limit table; HAP contract rent when known. Opex: pack `opex_per_unit_market` / `opex_per_unit_regulated` inflated to the as-of year, or the opex ratio; replace the tax line with actual taxes billed when the assessor record is on hand. Benchmarks come from `multifamily-benchmarks` Quick Reference (surface its date in Assumptions).

## 3. Loan constant and amortized balance

```
i = annual_rate / 12
loan_constant(rate, am = 360) = 12 x i / (1 - (1 + i)^-am)
   check: loan_constant(0.0615, 360) ~= 0.0731

amortized_balance(P0, annual_rate, n_months = 360, k_months, io_months = 0)
   if k_months <= io_months:          balance = P0
   else: k' = k_months - io_months;   balance = P0 x ((1+i)^n - (1+i)^k') / ((1+i)^n - 1)
   check: k = 0 -> P0 ; full IO -> P0
```

Inputs for a recorded trust deed with no tape: `P0` = stated principal; `annual_rate` = note rate if printed, else proxy = 10-year UST at origination month + lender spread (pack `lender-term-assumptions.md`); `k_months` = months from first payment (recording + 1-2 months) to as-of. HELOC / line-of-credit trust deeds: use the stated maximum principal (Oregon ORS 86.155 prints it on page one) as the balance ceiling, flagged `balance_basis = ESTIMATED`. Add junior trust deeds, HECM (balance grows; use original principal limit x 1.0 as a floor), DOR deferral liens and recorded judgments to total liens. When a Notice of Default / Notice of Sale states the sum owing, it overrides the estimate (`balance_basis = RECORDED`).

`balance_basis`: tape UPB -> REPORTED (HUD FHASL UPB -> RECORDED); amortized from recorded principal -> ESTIMATED; from a proxy (e.g. OHCS closing date with no principal) -> PROXY, and usually `not in public record`.

## 4. Inferred maturity from lender type

```
inferred_maturity(orig_date, lender_type, pack)
   terms = pack.lender_terms[lender_type]      # min_term, typical, max_term (years)
   point        = orig_date + typical
   window_start = orig_date + min_term
   window_end   = orig_date + max_term
   basis        = ESTIMATED
```

Agency (`fannie_dus`, `freddie_k_sb`), `hud_fha`, `usda_rd` and `cmbs` are never inferred when a tape exists; the adapter pulls the actual date. A recorded Modification/Extension Agreement replaces the point with its stated new maturity (RECORDED). A Reconveyance followed within 90 days by a new trust deed is a refinance: emit `REFINANCE_CLOSED` and `SUPPRESS_UNTIL = new_orig + min_term`.

## 5. Refinance test

```
refi_rate       = ust10 + refi_spread_bp / 10000          # pack values; UST10 flagged verify
constant_refi   = loan_constant(refi_rate, 360)

max_loan        = min( noi / (dscr_floor x constant_refi),
                       noi / debt_yield_floor,
                       ltv_max x est_value )
refi_gap        = upb - max_loan
refi_gap_pct    = refi_gap / upb
dscr_refi       = noi / (upb x constant_refi)
ltv             = upb / est_value
debt_yield      = noi / upb
equity_cushion_pct = (est_value - total_liens) / est_value
rate_spread_bp  = (refi_rate - note_rate) x 10000           # when note_rate known
refi_proceeds_ratio = loan_constant(note_rate) / loan_constant(refi_rate)
```

Floors by class (pack `market-params.json`): market-rate agency/CMBS `dscr_floor 1.25`, bank `1.20`, affordable `1.15` (hard-debt sizing per `sizing-lihtc-permanent-debt`, which also handles mandatory soft debt vs residual receipts); `debt_yield_floor 0.08`; `ltv_max` 0.70 market / 0.80 affordable. For regulated assets run the test on restricted NOI and treat recorded soft loans as subordinate: they are not part of `upb` for the first-mortgage test but are listed in the capital stack line and in `SOFT_LOAN_MATURITY` events when a date is actually recorded.

Floating-rate / bridge extension test (class 2): `dscr_at_current = noi / (upb x (sofr + margin))` (IO), `debt_yield = noi / upb`; extension passes when `dscr_at_current >= 1.10-1.20` and `debt_yield >= 0.07-0.08` (use pack values); fail -> modifier in scoring.

IO roll test: `dscr_amortizing = noi / (upb x loan_constant(note_rate, 360))`; flag when IO ends within 12 months and `dscr_amortizing < 1.35`; score when < 1.20.

## 6. Interpretation bands

| metric | reading |
|---|---|
| `refi_gap_pct > 0.25` | owner must bring 25%+ of the balance in new equity or sell; strongest maturity-driven seller |
| `0.10-0.25` | recap or partial paydown; sale is one of two realistic paths |
| `0-0.10` | refinanceable with friction; motivation depends on rate shock and hold period |
| `<= 0` | refinanceable; maturity alone is not a seller signal (assumption/low-coupon tag may still apply) |
| `equity_cushion_pct 0.10-0.35` | owner can sell but not refinance: best conversion band |
| `equity_cushion_pct <= 0` | lender is the real counterparty; route `lender_counterparty` |
| `rate_spread_bp > 200` with maturity < 36 mo | proceeds shrink sharply at refi; also a buyer edge if debt is assumable (HUD/agency) |

Reported DSCR/NOI (tape) weigh 1.0 in scoring; estimates 0.7. Tape NOI is borrower-reported, often annualized from trailing quarters and lags 1-2 quarters; benchmark NOI carries roughly +/-15% error. Show the basis in the workbook.

## 7. Lender-term table (summary)

Full table with rate proxies and notes: `sources/<pack>/lender-term-assumptions.md`. Defaults when a pack has none:

| lender_type | min_term | typical | max_term | amort | note |
|---|---|---|---|---|---|
| bank_cu | 5 | 7 | 10 | 30 (25 for small balance) | balloon; 5/7/10 candidates |
| life_co | 10 | 10 | 15 | 30 | |
| debt_fund_bridge | 2 | 3 | 5 | IO | floating; cap expiry at initial term |
| fannie_dus / freddie_k_sb | 7 | 10 | 12 | 30 / IO period | pull tape first |
| hud_fha | 35 | 35 | 40 | fully amortizing | pull FHASL; 223(f) 35y, 221(d)(4) 40y |
| cmbs | 5 | 10 | 10 | 30 / IO | pull EX-102 or trustee IRP |
| usda_rd | 30 | 50 | 50 | | pull exit data |
| state_soft / local_soft | coterminous with regulatory agreement | | | deferred | affordability period end is not a note maturity |
| hecm | n/a | due on death or move-out | | negative amortization | class 1 only |
| seller_private | 1 | 5 | 10 | IO or short am | read the instrument |

Lender name -> `lender_type` mapping lives in `assets/lender_type_dictionary.csv`.

## 8. Recorded-instrument image extraction schema

When a trust-deed image (Multnomah $3.75/document per county snippet, unverified, `market-params.json`; Clark WA free, unverified) is read by OCR + LLM, extract to this JSON and store with `basis = RECORDED` only for fields literally present in the instrument:

```jsonc
{
  "instrument_number": "string",
  "recording_date": "YYYY-MM-DD",
  "document_type": "Trust Deed | Line of Credit Trust Deed | Modification | Extension | Assignment of Rents | Reconveyance | UCC Fixture | Notice of Default | Notice of Sale",
  "grantor": "string",                 // borrower entity exactly as printed
  "grantee": "string",                 // lender / beneficiary
  "trustee": "string | null",
  "stated_principal": "number | null",
  "maximum_principal": "number | null",  // ORS 86.155 line-of-credit legend
  "maturity_date": "YYYY-MM-DD | null",
  "maturity_date_location": "page 1 legend | definitions | note reference | not stated",
  "note_rate": "number | null",
  "rate_type": "fixed | floating | not stated",
  "amortizing": "true | false | not stated",
  "uniform_instrument": "Fannie 6025.OR | Freddie | HUD-94000M | bank form | none",
  "cross_default_or_portfolio": "true | false",
  "signatory_name": "string | null",
  "signatory_title": "string | null",   // the decision-maker evidence item
  "signatory_entity_chain": ["string"], // e.g. ["XYZ Apartments LLC", "by ABC Manager LLC, its manager", "by Jane Doe, Managing Member"]
  "sum_owing": "number | null",         // NOD / Notice of Sale only
  "sale_date": "YYYY-MM-DD | null",
  "legal_description_snippet": "string",
  "confidence": "high | medium | low",
  "page_count": "int",
  "source_file": "string"
}
```

Oregon notes: the maturity date is mandatory on page one only for line-of-credit trust deeds (ORS 86.155); Fannie Mae Form 6025.OR, Freddie Mac and HUD-94000M security instruments recite it in the definitions; conventional bank trust deeds often omit it (use Section 4). Construction-loan trust deeds show short maturities that convert to mini-perms: label `ESTIMATED` with a note. Washington deeds of trust (RCW 61.24) rarely print maturity on page one; read the body.

## 9. Worked example

`python scripts/omdf/capital_stack.py --selftest` prints this case.

```
48-unit 1972 Class C, Multnomah County, bank trust deed recorded 2018-06-15, stated principal $4,200,000, no maturity printed.
lender_type = bank_cu -> inferred maturity point 2025-06 (typical 7y), window 2023-06..2028-06, basis ESTIMATED.
Note rate proxy: UST10 at 2018-06 (2.90%) + 200 bp = 4.90%.
k = 99 months (first payment 2018-08 to 2026-10). balance ~= $3,618,000 (ESTIMATED).

NOI proxy: 48 x $1,450 x 12 = $835,200 GPR; x (1 - 0.071) = $775,900 EGI; x (1 - 0.42) = $450,000 NOI (benchmark_estimate).
Value: $450,000 / 0.056 (Class C) = $8,036,000 (income_proxy).
refi_rate = 0.0415 + 0.0175 = 0.059; constant = 0.0712.
max_loan = min(450,000/(1.20 x 0.0712) = $5,266,000 ; 450,000/0.08 = $5,625,000 ; 0.70 x 8,036,000 = $5,625,000) = $5,266,000.
refi_gap = 3,618,000 - 5,266,000 = -$1,648,000 -> refinanceable; refi_gap_pct -0.46.
dscr_refi = 450,000 / (3,618,000 x 0.0712) = 1.75 ; ltv 0.45 ; debt yield 12.4% ; equity cushion 55%.
Reading: maturity alone is not a seller signal here; the 2018-vintage bank loan is past its typical term, so check the recorder for a Modification or a new trust deed (REFINANCE_CLOSED) before scoring timing points.
```

## 10. What this math never does

- Produce a value opinion (that is `comp-analyzer`), a credit verdict (`underwriting-market-rate-multifamily`, `front-door-lihtc-underwriting`) or debt sizing for a term sheet (`sizing-conventional-multifamily-debt`, `sizing-lihtc-permanent-debt`).
- Use Assessed Value as market value in Measure-50 states.
- Report a balance, rate or maturity without a `basis`; when there is no anchor at all, the field reads `not in public record`.
