# Jurisdiction Pack: <State>, <Metro> (`<st>-<metro>`)

Copy this folder to `references/sources/<st>-<metro>/` and replace every `<placeholder>`. Delete this paragraph when done. Follow `references/sources/README.md` for the full procedure and `references/sources/oregon-portland/` for a completed example. Scripts load the pack with `--pack references/sources/<st>-<metro>`.

Agency profiles to fill in `agency-profiles.yaml`: `hfa` = <state housing finance agency>; `city_housing` = <city housing bureau>; `county` = <county housing office>; `pha_am` = <public housing authority>; `cdbg_home` = <HOME / CDBG participating jurisdiction>. Delete profiles the agency will not run.

## Files

| file | purpose | status |
|---|---|---|
| `geography.md` | modes, county FIPS, jurisdictions, resolution order, boundary layers, sources that stop at a state line | <todo> |
| `sources.md` | source directory: agency records first, then state / federal inventories, organization resolution; access tier, fee, cadence, key fields, verified_live | <todo> |
| `dataset-schemas.yaml` | declared date formats, basis, event mapping, validations, normalizations, lead-column maps for the agency servicing extract and every file-drop dataset | <todo> |
| `agency-profiles.yaml` | per-profile behaviour (book sources, expected-book flag, purchaser / designee / PBCA / QC status, routes enabled, self-owner tokens, recapture methods, PII level, mandate defaults, Board_Totals variant) | <todo> |
| `mandate.json` | open products and eligibility (route-level hard filter on nofa_offer) | <todo> |
| `market-params.json` | affordable NOI inputs, senior DSCR floor, product rates, every statutory day / month count; each with value / as_of / source / verify | <todo> |
| `legal-timelines.md` | state preservation-notice law, IRC 42, HOME / HTF / CDBG, MAHRA, HUD legacy, USDA 515, RAD / Section 18, NSPIRE / 8823, state public records law, book-risk stub, assessment regime | <todo> |
| `rent-limits.json` | MTSP max rents by AMI band for restricted NOI (recap sizing, our_book only) | <todo> |
| `book_crosswalk.csv` | agency ids -> property_id confirmed by an analyst (starts empty) | header only |
| `equity_overlays.yaml` | optional displacement-risk tracts and under-served districts | optional |

## Coverage matrix (source x county)

| source | <County A FIPS> | <County B FIPS> | <County C FIPS> |
|---|---|---|---|
| Agency servicing system (book spine) | | | |
| State HFA inventory | | | |
| State preservation registry / notice log | | | |
| PBCA opt-out / renewal log | | | |
| HOME / CDBG PJ records | | | |
| PHA assets / PBV contracts | | | |
| HUD FHASL, HUD Sec 8, HUD LIHTC, REAC, eGIS | yes | yes | yes |
| USDA MFH exit | | | |
| NHPD | yes | yes | yes |
| SOS registry / UCC | | | |
| Recorder (LURA / ROFR images only) | | | |
| Assessor exemption / delinquency | | | |
| Courts (book-risk stub) | | | |
| City code enforcement | | | |

## Verify-before-first-run checklist

1. Every URL in `sources.md` resolves (`scripts/smoke_test_sources.py --pack <this folder>`); flip `verified_live` only after reading `sources_status.json`.
2. The agency servicing extract: run `scripts/date_profile.py` on it, paste the formats, confirm the `book_kind` / `program` / `payment_type` / `covenant_status` / `recapture_method` vocabularies and whether notice and QC log columns exist.
3. State preservation-notice law current text (`federal/preservation-notice-laws-by-state.md` row): unit threshold and program set, owner notice months, withdrawal bar, designee / appointment-on-silence, purchase right and its duration, records duty, tenant notice and its remedy, public registry, sanctions language. Fill `market-params.json` push / tenant / records / ROFR parameters from the text, not summaries.
4. State LIHTC qualified-contract policy and first waiver year (`federal/qc-policy-by-state.md`); current QAP; the HFA's QC procedure.
5. The state's PBCA identity (`agency-profiles.yaml` `is_pbca`) and whether the CA log is available as RECORDED.
6. HOME affordability-period rules per written agreement (pre / post 2025 final rule) and the PJ's recapture method per program.
7. State HFA inventory date formats: run `scripts/date_profile.py` on the file and paste the YAML into `dataset-schemas.yaml`; check HAP date freshness (stale annual dates).
8. HUD field names from live headers; ArcGIS layer `/0?f=pjson`.
9. `market-params.json` values flagged `verify`; `mandate.json` product windows and eligibility against the current NOFA / RFP.
10. Whether a LIHTC extended-use agreement alone qualifies a property under the state preservation law.
11. PHA repositioning status and local acquisition program guidelines if `pha_am` / `county` profiles will run.
12. State public records law treatment of personal contact information for the board packet (`pii-and-sunshine.md`); agency counsel review before the first packet.

## What a degraded run looks like

Without the agency servicing extract every lead is `universe_not_held` with `book_match = book_absent`: our_capital_at_risk is 0 for every row and the brief says "book absent: capital factor 0 for all rows; outputs are preservation targeting and notice compliance only". Without the agency notice log every PuSH-covered row is `notice_status unknown` (no breach, 6 points after the due date with Verify — Notice Log). Name the absent files in the brief.
