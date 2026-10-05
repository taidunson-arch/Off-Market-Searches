# Lender-Term Assumptions: <Metro> market pack

Used by `inferred_maturity()` when a recorded instrument gives a lender and a recording date but no maturity, and by `REFINANCE_CLOSED -> SUPPRESS_UNTIL` (new origination + `min_term`). Every inferred date is `basis = ESTIMATED` with a window from `min_term` to `max_term`. Lender name tokens map to `lender_type` through `assets/lender_type_dictionary.csv` (add local bank and credit-union names there, not here). Edit the table only where local lending differs from the defaults in `references/capital-stack-math.md` Section 7; keep the `lender_type` enum.

| lender_type | min_term (y) | typical (y) | max_term (y) | amortization | rate proxy at origination | notes |
|---|---|---|---|---|---|---|
| bank_cu | 5 | 7 | 10 | 25-30 y | UST (matching term) + 200 bp | balloon; adjust if local banks favor 5-year resets |
| life_co | 10 | 10 | 15 | 25-30 y | UST10 + 150 bp | |
| debt_fund_bridge | 2 | 3 | 5 (with extensions) | interest-only | SOFR + 350 bp | floating; cap expiry at initial term; extension tests |
| fannie_dus | 7 | 10 | 12 | 30 y with IO | pull tape | never infer when the tape is available |
| freddie_k_sb | 5 | 10 | 10 | 30 y with IO; SB hybrid ARMs | pull tape | |
| cmbs | 5 | 10 | 10 | 30 y; often IO | pull EX-102 / IRP | |
| hud_fha | 35 | 35 | 40 | fully amortizing | pull FHASL | 223(f) 35 y; 221(d)(4) 40 y; prepay step-down to year 10 |
| usda_rd | 30 | 50 | 50 | per note | pull exit data | |
| state_soft | coterminous with regulatory agreement | — | — | deferred | 0-3% | affordability-period end is not a note maturity |
| local_soft | coterminous with regulatory agreement | — | — | deferred | 0-3% | |
| hecm | n/a | due on death, sale or move-out | n/a | negative amortization | pull instrument | class 1 only |
| seller_private | 1 | 5 | 10 | IO or short am | read instrument | |
| unknown | — | — | — | — | — | infer only with `--assume-unknown-lender bank_cu` |

## Rate proxies by origination year

Pull FRED DGS10 monthly averages for the recording month; the Oregon pack lists rounded annual anchors as an example. Record the series and pull date here.

## Construction-to-perm notes

<Local practice for construction loans converting to mini-perms; HUD 221(d)(4) final endorsement as the conversion signal.>

## Suppression terms

`SUPPRESS_UNTIL = new_origination + min_term(lender_type)`: bank 5 y; life co 10 y; bridge 2 y; agency 7 y; CMBS 5 y; HUD 35 y; unknown 5 y.
