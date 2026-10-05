# Source Directory and Market Packs

`references/sources/` holds everything that depends on where the user is prospecting. The skill's logic (modules, scoring, math, contracts) is market-neutral; a market pack supplies the geography, the local source directory, declared dataset schemas, market parameters, legal clocks and lender conventions. `oregon-portland` is the worked example; `_template` is the starting point for any other US market; `federal/` holds the national tapes and per-state policy tables every pack can reference.

## Layout

```
sources/
  README.md                      this file
  federal/
    README.md                    national tapes directory (HUD, USDA, NHPD, Ginnie, DUS, MSIA, EDGAR, vendors)
    qc-policy-by-state.md        LIHTC qualified-contract policy by state
    preservation-notice-laws-by-state.md   state preservation-notice / ROFR laws
  _template/                     copy to sources/<state>-<metro>/ and fill in
  oregon-portland/               worked example
```

## How to add a market pack

1. Copy `_template/` to `sources/<state>-<metro>/` (slug: two-letter state, hyphen, lowercase metro or county, e.g. `wa-seattle`, `tx-harris`). `market_id` defaults to `us-<state>-<first county name>`.
2. `geography.md`: define the modes the market actually supports (at minimum `county` and `metro_core`), list county FIPS and jurisdictions, name the boundary layers and the ZIP-County crosswalk, and state which sources stop at a state line. Never define a mode by ZIP prefix or city string alone.
3. `sources.md`: one row per source with the standard columns (`source_id | adapter | class | publisher | URL | access | fee | cadence | key fields | verified_live | caveats`). Start from `federal/README.md` for the national rows, then add the state HFA inventory, state preservation program, recorder and assessor per county, courts, SOS registry and UCC, city code enforcement, and market-parameter sources. Every row carries an access tier and `verified_live`.
4. `dataset-schemas.yaml`: for every file-drop dataset declare `match_columns`, `key`, every date column's `format` and `basis`, event mappings, derived events, validations, normalizations and filters. Run `scripts/date_profile.py <file>` to propose formats; paste its YAML snippet. A column with date-like values and no declared format stops the adapter.
5. `market-params.json`: fill each value with `value`, `as_of`, `source`; mark anything you have not pulled this quarter `verify: true`. Cite `multifamily-benchmarks` for bands.
6. `legal-timelines.md`: the state's foreclosure statute (judicial vs non-judicial, recorded instruments and their timing), receivership, mechanics liens, tax foreclosure, preservation-notice law (from `federal/preservation-notice-laws-by-state.md`), telephone-solicitation / DNC rules, wholesaler or equity-purchaser statutes, and the assessment regime (is assessed value market value?).
7. `lender-term-assumptions.md`: adjust terms and rate proxies if local lending differs; keep the `lender_type` enum.
8. `README.md`: the pack index, a coverage matrix (source x county) and the verify-before-first-run checklist.
9. Run `python scripts/smoke_test_sources.py --pack sources/<slug>`; fix dead URLs; keep `verified_live=false` for anything the test could not confirm.

## Access tiers

| tier | meaning | examples |
|---|---|---|
| `free-public` | downloadable or searchable without an account | HUD FHASL, OHCS OAHI, recorder indexes, SOS registry, statutes |
| `free-registration` | free account, terms of use, sometimes a CAPTCHA or API token | NHPD, DUS Disclose, MSIA, CTSLink (public deals), OJD Smart Search, HUD crosswalk API, MultcoPropTax guest login |
| `paid` | subscription or per-record fee | recorder images, Conduits lien search, OJCIN, PACER, CoStar, Yardi Matrix, Reonomy, CRED iQ, Trepp, PropStream, skip-trace vendors |
| `manual` | public-records request, phone call or in-person retrieval | OHCS PuSH notices, PBCA opt-out logs, DART foreclosure list, Enhanced Inspections enrollment, Gresham inspection records |

Record the fee when known; write `quote-based (unverified)` otherwise. Never present an unverified price as fact.

## verified_live policy

- `verified_live` is a statement about this build, not about the source's existence. It is `true` only when a researcher or `smoke_test_sources.py` fetched the URL (or the file) directly and confirmed the expected content or header tokens.
- Search-engine snippets, third-party catalogs and prior knowledge leave it `false` with an evidence note in `caveats` (e.g. "snippet-confirmed", "GitHub repo corroboration", "knowledge").
- `smoke_test_sources.py` writes results to `sources_status.json` next to the pack; it never edits `sources.md`. A human flips the column after reading the status file.
- The brief's Run Summary lists every source still `false`; the Sources_Vintages tab shows it in amber.

## Verify-before-first-run checklist pattern

Every pack README ends with a numbered checklist. Required items for any market: all URLs resolve; recorder index URL, image availability and fee per county; whether the state records a pre-sale instrument (NOD vs notice of sale) and its statutory clock; whether assessed value equals market value; the state preservation-notice law's current text; the state QC policy and adoption year; the state HFA inventory's date formats (re-profile on every release); vendor pricing; HUD field names from live headers; current UST10 and other `verify` market params; telephone-solicitation / DNC and wholesaler statutes with counsel.

## Conventions

- URLs are copied from a source the researcher saw; when the exact page is unknown, describe how to find it ("from the county recorder's home page, Recorded Documents Search") instead of guessing a path.
- Dates in a pack are ISO (`YYYY-MM-DD`) except where a dataset's native format is being declared.
- No vendor is endorsed; list alternatives with their access tier and let the user choose.
- Keep the `lender_type`, `program`, `event_type` and other enums from `references/pipeline-contract.md` unchanged across packs; extend them there, not in a pack.
