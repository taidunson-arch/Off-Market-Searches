# Lender-Term Assumptions: Portland market pack

Used by `inferred_maturity()` when a recorded trust deed gives a lender and a recording date but no maturity, and by `REFINANCE_CLOSED -> SUPPRESS_UNTIL` (new origination + `min_term`). Every inferred date is `basis = ESTIMATED` with a window from `min_term` to `max_term`; an image read or a tape replaces it. Lender name tokens map to `lender_type` through `assets/lender_type_dictionary.csv`; an unmatched grantee defaults to `unknown` and is scored with the `bank_cu` prior (Yardi Matrix mix: 56% agency, 16% bank, 10% HUD, 6% debt fund, 6% life co, 2% CMBS) only when the user opts in via `--assume-unknown-lender bank_cu`.

| lender_type | min_term (y) | typical (y) | max_term (y) | amortization | rate proxy at origination | notes |
|---|---|---|---|---|---|---|
| bank_cu | 5 | 7 | 10 | 25-30 y (25 common for small balance) | UST (matching term) + 200 bp | Balloon; 5/7/10-year candidates; Oregon community banks and credit unions dominate the 5-49 unit stock; a 2016-2021 recording is likely maturing 2026-2031 |
| life_co | 10 | 10 | 15 | 25-30 y | UST10 + 150 bp | Larger, newer assets; often prepay-restricted (YM) until near maturity |
| debt_fund_bridge | 2 | 3 | 5 (with extensions) | interest-only | SOFR + 350 bp (300-450) | Floating; rate cap purchased for the initial term; extension tests (DSCR 1.10-1.20, debt yield 7-8%); 2021-22 vintages mature 2026-27; UCC often lists the rate-cap agreement as collateral |
| fannie_dus | 7 | 10 | 12 | 30 y with 0-10 y IO | pull tape (DUS Disclose) | Never infer when the tape is available; yield maintenance typically ends ~6 months before maturity (open window); assumable with approval |
| freddie_k_sb | 5 | 10 | 10 | 30 y with IO; SB hybrid ARMs reset after year 5/7/10 | pull tape (MSIA) | SB program concentrates Portland's 5-50 unit agency loans; defeasance/YM/declining premium per deal |
| cmbs | 5 | 10 | 10 | 30 y; many full IO | pull EX-102 / IRP | Defeasance; open period last 3-6 months; special servicing and watchlist from IRP |
| hud_fha | 35 | 35 | 40 | fully amortizing | pull tape (FHASL) | 223(f) 35 y, 221(d)(4) 40 y, 223(a)(7) remaining term; 223(f)/221(d)(4) prepayment restrictions are negotiated within HUD limits (commonly a 2-year lockout then a declining premium, with restrictions typically ending by year 10; no statute imposes a lockout; verify from the note or the Ginnie Mae prepayment-penalty file). The `PREPAY_WINDOW_OPEN` proxy of final endorsement + 10 years is a convention, not a statute; assumable with HUD approval |
| usda_rd | 30 | 50 | 50 | per note | pull exit data | 515 interest credit; prepayment requires RD approval, advance tenant notice (period per 7 CFR part 3560 subpart N; verify, usda.gov not fetched) and restrictive-use provisions |
| state_soft | coterminous with regulatory agreement | — | — | deferred / residual receipts | 0-3% | OHCS HOME/OAHTC/GHAP/HDGP/HTF loans; the OHCS `*_Expiration_Date` is the affordability period, not the note maturity; a recorded trust deed or loan doc is required for `SOFT_LOAN_MATURITY` |
| local_soft | coterminous with regulatory agreement (30-60 y) | — | — | deferred | 0-3% | PHB and other city/county loans; PHB trust deeds recorded in Multnomah |
| hecm | n/a | due on death, sale or move-out | n/a | negative amortization | pull instrument | Class 1 only; second trust deed to Secretary of HUD identifies it |
| seller_private | 1 | 5 | 10 | IO or short amortization | read the instrument | Seller carrybacks and private money; no OFAP certificate with an NOD implies a small beneficiary |
| unknown | — | — | — | — | — | Do not infer unless the user opts into the bank_cu prior |

## Rate proxies by origination year (for amortized-balance estimates)

Use the 10-year UST monthly average for the recording month plus the spread above; when no series is at hand the following rounded anchors are acceptable with `verify`:

| year | UST10 (approx.) |
|---|---|
| 2015 | 2.1% |
| 2016 | 1.8% |
| 2017 | 2.3% |
| 2018 | 2.9% |
| 2019 | 2.1% |
| 2020 | 0.9% |
| 2021 | 1.4% |
| 2022 | 3.0% |
| 2023 | 4.0% |
| 2024 | 4.2% |
| 2025 | 4.3% |

These are approximate annual averages from memory; pull FRED DGS10 before relying on any single month.

## Construction-to-perm notes

A construction-loan trust deed shows a 2-3 year maturity that converts to a mini-perm or is refinanced at completion; label the inferred maturity ESTIMATED with `derivation = construction loan; conversion expected` and look for the perm trust deed or the HUD 221(d)(4) final endorsement (Ginnie CLC -> PLC) before scoring.

## Suppression terms

`SUPPRESS_UNTIL = new_origination + min_term(lender_type)`: bank 5 y; life co 10 y; bridge 2 y; agency 7 y; CMBS 5 y; HUD 35 y (practically permanent for maturity scoring; prepay window still scored); unknown 5 y.
