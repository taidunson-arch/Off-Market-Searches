# Source Directory and Jurisdiction Packs

`references/sources/` holds everything that depends on where the agency sits and what it holds. The skill's logic (module, scoring, calendar, contracts) is jurisdiction-neutral; a pack supplies the geography, the local source directory with the agency's own records first, declared dataset schemas (including the agency servicing extract), the agency profiles, the mandate / product file, market and statutory parameters, legal clocks, the book crosswalk and an optional equity overlay. `oregon-portland` is the worked example; `_template` is the starting point for any other US jurisdiction; `federal/` holds the national tapes and per-state policy tables every pack can reference.

## Layout

```
sources/
  README.md                      this file
  federal/
    README.md                    national tapes and federal rules directory (HUD, USDA, NHPD, IRS; statutes and notices)
    qc-policy-by-state.md        LIHTC qualified-contract policy by state (HFA clock linkage)
    preservation-notice-laws-by-state.md   state preservation-notice / purchase-right laws (agency encoding)
    home-cdbg-affordability.md   HOME / HTF / CDBG affordability periods, recapture, inspections
    hap-renewal-and-optout.md    MAHRA opt-out notice, Renewal Guide options, 120-day package, PBCA, PRAC
  _template/                     copy to sources/<state>-<metro>/ and fill in
  oregon-portland/               worked example (OHCS, PHB, counties, Home Forward, Portland Consortium PJ)
```

## How to add a jurisdiction pack

1. Copy `_template/` to `sources/<state>-<metro>/` (slug: two-letter state, hyphen, lowercase metro or county, e.g. `wa-seattle`, `tx-harris`). `market_id` defaults to `us-<state>-<first county name>`.
2. `geography.md`: define the modes the jurisdiction supports (at minimum `county` and `metro_core`; `city_limits` for a city housing bureau), list county FIPS and jurisdictions, name the boundary layers and the ZIP-County crosswalk, and state which sources stop at a state line. Never define a mode by ZIP prefix or city string alone.
3. `agency-profiles.yaml`: one entry per profile the agency will run (`hfa`, `city_housing`, `county`, `pha_am`, `cdbg_home`) with book sources, expected-book flag, qualified-purchaser / designee / PBCA / QC-administrator status, routes enabled, self-owner tokens, recapture methods, PII level and mandate defaults. Every institutional fact starts `verify`.
4. `sources.md`: one row per source with the standard columns (`source_id | adapter | profile | publisher | URL | access | fee | cadence | key fields | verified_live | caveats`). Agency records first (servicing extract, notice log, QC log, CA opt-out log, PJ HOME / CDBG records, PHA assets), then the state HFA inventory and preservation registry, HUD / USDA / NHPD from `federal/README.md`, then organization resolution (SOS, 990s, recorder for LURA / ROFR images, assessor exemption codes, courts for the book-risk stub).
5. `dataset-schemas.yaml`: copy the `agency_servicing_extract` block verbatim and profile its date formats with `scripts/date_profile.py`; for every other file-drop dataset declare `match_columns`, `key`, every date column's `format` and `basis`, event mappings, derived events, validations, normalizations, lead-column maps and filters. A column with date-like values and no declared format stops the adapter.
6. `mandate.json`: the agency's open products with eligibility (programs, owner types, min units, application window, new covenant years); route-level hard filter on `nofa_offer`; mark `verified_live: false` until the NOFA is read.
7. `market-params.json`: fill each value with `value`, `as_of`, `source`; the statutory day / month counts (owner notice months, tenant notice, records response, ROFR match, QC 12 months, HAP opt-out 12 months / 120 days, inspection cadences, USDA 180 days, Section 250) come from the state law row and the federal rules and stay `verify: true` until the text is read.
8. `legal-timelines.md`: the state preservation-notice and purchase-right law (from `federal/preservation-notice-laws-by-state.md`), IRC 42 and the HFA's clocks, HOME / HTF / CDBG, MAHRA opt-out and renewal, HUD legacy, USDA 515, RAD / Section 18, NSPIRE / 8823, the state public records law for packet redaction, a two-row book-risk stub, the assessment regime. No foreclosure-clock, telephone-solicitation, wholesaler or equity-purchaser sections.
9. `README.md`: the pack index, a coverage matrix (source x county) and the verify-before-first-run checklist.
10. Run `python3 scripts/smoke_test_sources.py --pack sources/<slug>`; fix dead URLs; keep `verified_live=false` for anything the test could not confirm.

## Access tiers

| tier | meaning | examples |
|---|---|---|
| `free-public` | downloadable or searchable without an account | HUD FHASL, OHCS OAHI, SOS registry, statutes, recorder indexes |
| `free-registration` | free account, terms of use, sometimes a CAPTCHA or API token | NHPD, OJD Smart Search, HUD crosswalk API, MultcoPropTax guest login, HUD IDIS (PJ) |
| `paid` | subscription or per-record fee | recorder images, PACER |
| `manual` | internal system export, public-records request, phone call or in-person retrieval | the agency's own servicing extract, notice and QC logs, CA opt-out log, PHA board records, RD prepayment request status |

Record the fee when known; write `quote-based (unverified)` otherwise. Never present an unverified price as fact. No skip-trace or data-broker vendor appears in any pack.

## verified_live policy

- `verified_live` is a statement about this build, not about the source's existence. It is `true` only when a researcher or `smoke_test_sources.py` fetched the URL (or the file) directly and confirmed the expected content or header tokens. The agency's own extract is `true` when supplied and header-matched.
- Search-engine snippets, third-party catalogs and prior knowledge leave it `false` with an evidence note in `caveats` (e.g. "snippet-confirmed", "knowledge").
- `smoke_test_sources.py` writes results to `sources_status.json` next to the pack; it never edits `sources.md`. A human flips the column after reading the status file.
- The brief's Run Summary lists every source still `false`; the Sources_Vintages tab shows it in amber. Every statutory cite in intervention letters carries `verified_live: false` until the pack's legal-timelines are read from official text.

## Verify-before-first-run checklist pattern

Every pack README ends with a numbered checklist. Required items for any jurisdiction: all URLs resolve; the agency servicing extract's date formats and vocabularies; the state preservation-notice law's current text (notice months, withdrawal bar, designee, purchase right, records duty, tenant notice, registry, sanctions language); the state QC policy and first waiver year; the PBCA identity; HOME affordability rules per written agreement; the state HFA inventory's date formats (re-profile on every release) and HAP date freshness; HUD field names from live headers; current `verify` market and statutory params; mandate product windows; the state public records law treatment of personal contact information, with counsel.

## Conventions

- URLs are copied from a source the researcher saw; when the exact page is unknown, describe how to find it instead of guessing a path.
- Dates in a pack are ISO (`YYYY-MM-DD`) except where a dataset's native format is being declared.
- No vendor is endorsed; external partners (bridge lenders, TA providers) are listed in `mandate.json` as `external: true`.
- Keep the `program`, `event_type`, `agency_profile`, `book_kind`, route and other enums from `references/pipeline-contract.md` unchanged across packs; extend them there, not in a pack.
- Default outputs are organization level; a pack never adds a personal-contact source.
