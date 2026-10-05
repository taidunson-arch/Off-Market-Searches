# Market Pack: Portland, Oregon (`oregon-portland`)

The worked example for `off-market-deal-finder`. A market pack is everything that is specific to one place: geography modes, the source directory, dataset schemas with declared date formats, market parameters, legal clocks and lender-term conventions. Scripts load it with `--pack references/sources/oregon-portland`. To build another market, copy `references/sources/_template/` and follow `references/sources/README.md`.

## Files

| file | purpose | read by |
|---|---|---|
| `geography.md` | modes (`city_limits`, `county`, `metro_core`, `cbsa`), FIPS, jurisdictions, resolution order, boundary sources, OHCS row counts per mode | SKILL.md Step 1; `omdf/geo.py` |
| `sources.md` | every source with adapter, class, publisher, URL, access tier, fee, cadence, key fields, `verified_live`, caveats | Step 2 download checklist; `smoke_test_sources.py` |
| `dataset-schemas.yaml` | declared per-column date formats, basis, event mapping, validations, normalizations, filters, county FIPS map for OHCS, HUD FHASL and HUD Sec 8 files | `omdf/schema.py`, every adapter |
| `market-params.json` | cap rates, vacancy, rents, opex, UST10, spreads, DSCR/LTV/debt-yield floors, rent cap, relocation amounts, fees; each with value / as_of / source | `omdf/capital_stack.py`; Assumptions tab |
| `legal-timelines.md` | ORS 86 / 88 / 37 / 87 / 312, RCW 61.24 / 84.64, ORS 456 + OAR 813-115 + SB 973, IRC 42, ORS 646, HB 4058, ORS 646A.702, RCW 61.34, Measure 50 | event derivation; compliance gates |
| `lender-term-assumptions.md` | min / typical / max terms, amortization, rate proxies by lender type; suppression terms | `inferred_maturity()`, `SUPPRESS_UNTIL` |
| `rent-limits.json` | LIHTC max rents by AMI band for the restricted-income value proxy (placeholder: nulls until the user pastes current MTSP limits) | `ohcs_inventory_targets.py` value screen |
| `sources_status.json` | output of `smoke_test_sources.py` (dry run by default); `run_pipeline.py` reads live results to label sources | brief Run Summary, Sources_Vintages tab |

## Coverage matrix (source x county)

| source | Multnomah 41051 | Washington 41067 | Clackamas 41005 | Clark WA 53011 | Columbia / Yamhill / Skamania |
|---|---|---|---|---|---|
| OHCS OAHI (class 3 spine) | yes | yes | yes | no | OR counties yes |
| OHCS 10-Year Forecast / PuSH | yes | yes | yes | no | yes |
| HUD FHASL, HUD Sec 8, HUD LIHTC, REAC, eGIS | yes | yes | yes | yes | yes |
| USDA MFH exit | few | few | few | some | yes |
| NHPD | yes | yes | yes | yes (WA extract) | yes |
| Ginnie Mae, DUS Disclose, MSIA, EDGAR EX-102 | yes | yes | yes | yes | yes |
| Recorder index | MultcoRecords (free index, $3.75 image) | Washington Co. Recording (URL/fee unverified) | Clackamas Clerk (partial online) | Clark Auditor + Digital Archives (free images) | county-specific; not in pack |
| Assessor | MultcoPropTax, SAIL, RLIS | A&T Public Access, InterMap, RLIS | AscendWeb, CMAP, RLIS | Property Information Center, GIS | not in pack |
| Courts | OJD Smart Search / OJCIN | OJD | OJD | WA Odyssey portal (not verified) | OJD |
| SOS registry / UCC | Oregon SOS | Oregon SOS | Oregon SOS | WA SOS CCFS / WA DOL (not verified) | Oregon SOS |
| City code / liens | Portland BDS, PortlandMaps, Conduits; Gresham rental program | none verified | none verified | Clark County code enforcement (not verified) | none |
| Rent cap / relocation rules | ORS 90.324; Portland PCC 30.01.085/.086/.087 | ORS 90.324 | ORS 90.324 | WA 2025 law (verify) | ORS 90.324 |
| Market params | Kidder, MFNW, Zumper, RentCafe, Apartment List, IREM, OHCS financial report | same | same | partial (Zumper/Apartment List ZIP data) | thin |

## Verify-before-first-run checklist

Run `python scripts/smoke_test_sources.py --pack references/sources/oregon-portland` and then confirm by hand:

1. Every URL in `sources.md` resolves and the file sources return the expected header tokens (`dataset-schemas.yaml` `match_columns`). Flip `verified_live` only on success and only in `sources_status.json`. As of 2026-10-04 no non-GitHub URL in `sources.md` has been fetched (every government, county, court and vendor host was egress-blocked); run `python scripts/smoke_test_sources.py --pack references/sources/oregon-portland --live` from an unrestricted machine before the first run.
2. Washington County (OR) and Clackamas County online recorded-document search URLs, image availability and per-page fees (503-846-8752; 503-655-8698). Several search hits for "Washington County recorded documents" belong to Idaho, Arkansas and Minnesota counties of the same name.
3. ORS 456.262 / 456.263 ROFR duration (24 vs 36 months) and current owner-notice timing after SB 973 (2025); read the statute text, not summaries.
4. 2025 Oregon QAP: whether a qualified-contract waiver is now required of new allocations; status of the OHCS Qualified Contract Procedure (draft PDF).
5. Oregon PBCA identity under HUD's FY2025 PBCA NOFO before filing opt-out records requests.
6. Vendor pricing and filters (CoStar, Yardi Matrix, Reonomy, CRED iQ, Crexi, PropStream maturity filter, skip-trace per-record costs).
7. HUD field names from the live FHASL and Sec 8 Excel headers and from the ArcGIS layer `/0?f=pjson`; Ginnie Mae layout version.
8. `market-params.json` values flagged `verify`: UST10, SOFR, opex inflation, cap_rate_affordable, extension-test thresholds; refresh Kidder/MFNW/Zumper/RentCafe quarterly.
9. HB 4058 registration fee and cancellation period; ORS 646A.702 and RCW 61.34 with counsel before any pre-foreclosure outreach template is used.
10. OHCS OAHI release: re-run `scripts/date_profile.py` on the new file; if any declared format no longer fits (first-field > 12 appears in a month-first column), update `dataset-schemas.yaml` before running.
11. Clark County WA: Auditor online search URL, WA SOS and DOL UCC portals, Washington 2025 rent-cap terms.
12. OJCIN base monthly fee for the chosen account type; OJD terms of use regarding automated Smart Search queries.

## What a degraded run looks like here

With only the OHCS CSV in the inbox every affordable target is REPORTED (regulatory dates), DERIVED (Year 15) or PROXY (mini-perm maturity); there is no RECORDED debt and no declared-intent signal, so in the 2026-10-04 sample nothing rose above Tier C (that is empirical, not a designed cap: the proxy-only cap applies to PROXY-governed leads only). Lifting it means adding the families that are absent: HUD FHASL Active (RECORDED maturities), HUD MF Assistance & Sec 8 (HAP dates and owner/agent names), the OHCS 10-Year Forecast through `normalize_ohcs_forecast.py` (preservation status; adapter field names unverified until the export is profiled), and recorder images for individual leads. The brief must say which of these were absent.
