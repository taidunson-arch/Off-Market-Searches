# Market Pack: <State>, <Metro> (`<st>-<metro>`)

Copy this folder to `references/sources/<st>-<metro>/` and replace every `<placeholder>`. Delete this paragraph when done. Follow `references/sources/README.md` for the full procedure and `references/sources/oregon-portland/` for a completed example. Scripts load the pack with `--pack references/sources/<st>-<metro>`.

## Files

| file | purpose | status |
|---|---|---|
| `geography.md` | modes, county FIPS, jurisdictions, resolution order, boundary layers, sources that stop at a state line | <todo> |
| `sources.md` | source directory with access tier, fee, cadence, key fields, verified_live | <todo> |
| `dataset-schemas.yaml` | declared date formats, basis, event mapping, validations, normalizations, filters for every file-drop dataset | <todo> |
| `market-params.json` | cap rates, vacancy, rents, opex, rates, floors, local rules; each with value / as_of / source | <todo> |
| `legal-timelines.md` | foreclosure, receivership, lien, tax-foreclosure, preservation-notice, solicitation and assessment rules | <todo> |
| `lender-term-assumptions.md` | lender-type terms and rate proxies for inferred maturities | <todo> (defaults in `references/capital-stack-math.md` Section 7 apply until edited) |

## Coverage matrix (source x county)

| source | <County A FIPS> | <County B FIPS> | <County C FIPS> |
|---|---|---|---|
| State HFA inventory | | | |
| State preservation-notice registry | | | |
| HUD FHASL, HUD Sec 8, HUD LIHTC, REAC, eGIS | yes | yes | yes |
| USDA MFH exit | | | |
| NHPD | yes | yes | yes |
| Ginnie Mae, DUS Disclose, MSIA, EDGAR EX-102 | yes | yes | yes |
| Recorder index / images | | | |
| Assessor | | | |
| Courts | | | |
| SOS registry / UCC | | | |
| City code enforcement / liens | | | |
| Rent regulation | | | |
| Market params | | | |

## Verify-before-first-run checklist

1. Every URL in `sources.md` resolves (`scripts/smoke_test_sources.py --pack <this folder>`); flip `verified_live` only after reading `sources_status.json`.
2. Recorder index URL, online image availability and fee for each county.
3. Foreclosure regime: judicial or non-judicial; which instrument is recorded first and its statutory clock; whether a lis pendens exists.
4. Assessment regime: does assessed value track market value? If not (Oregon Measure 50, California Prop 13), set `av_is_market: false` in `market-params.json`.
5. State preservation-notice law current text (`federal/preservation-notice-laws-by-state.md` row) and any public notices registry.
6. State LIHTC qualified-contract policy and adoption year (`federal/qc-policy-by-state.md` row); current QAP.
7. State HFA inventory date formats: run `scripts/date_profile.py` on the file and paste the YAML into `dataset-schemas.yaml`.
8. HUD field names from live headers; ArcGIS layer `/0?f=pjson`.
9. `market-params.json` values flagged `verify` (UST10, SOFR, opex inflation, cap rates).
10. Telephone-solicitation / DNC law, wholesaler registration, equity-purchaser statutes with counsel.
11. Vendor pricing and filters for any paid source the user plans to use.
12. Rent regulation (caps, relocation ordinances, just-cause rules) that drives motivation and underwriting.
