# scripts/ — preservation-loan-book

Deterministic, offline pipeline for a public-agency preservation and loan-book review (HFA, city or county housing office,
PHA asset management, HOME/CDBG PJ). Python 3, `pandas` + `openpyxl` + `pyyaml` only (`requirements.txt`). Nothing fetches
the network; the clock is read only through `--as-of` (default `date.today()`); every statutory figure is a pack parameter
marked `verified_live: false` in this build. The library package is `plb/` (a self-contained copy of the affordable spine of
off-market-deal-finder v2, recast for the agency: no code imports from that folder).

## Run order (one command)

```bash
python3 scripts/run_agency_pipeline.py --config run_config.json [--from <stage>] [--prior-run runs/2026-07-01] [--explain <property_id>] [--as-of 2026-10-04]
```

Stages: `discover -> universe -> calendar -> score -> workbook -> handoffs -> brief -> diff`. The run dir is
`<out_dir>/<as_of>/` and holds `leads.csv`, `events.csv`, `rejects.csv`, `merge_log.csv`, `servicing_unmatched.csv`,
`book_join_gaps.csv`, `pipeline_not_scored.csv`, `calendar_summary.json`, `leads_scored.csv`, `units_at_risk.json`,
`notice_compliance_queue.csv`, `nofa_targets.csv`, `agency_calendar.csv`, `sponsor_exposure.csv`, `optout_qc_responses.csv`,
`<workbook_name>.xlsx`, `<market>_Board_Packet.xlsx` + `board_packet.md`, `handoff/*.json` + `documents_to_request.csv` +
`sos_worklist.csv` + `board_packet.csv`, `brief.md`, `status_flips.csv` + `kpi_summary.json` (with a prior run), `result.json`,
`sources_used.json`, `manifest.json`. With `pipeline_mode: true` it also writes
`data/status/{market_id}/asset_management/preservation-loan-book.json`.

### run_config.json keys

| key | default | meaning |
|---|---|---|
| `market_id`, `pack` | — | run label; jurisdiction pack dir (`references/sources/oregon-portland`) |
| `agency_profile` | `hfa` | `hfa` / `city_housing` / `county` / `pha_am` / `cdbg_home` (`agency-profiles.yaml` changes routes, book sources, PuSH / QC / PBCA roles, self-owner tokens) |
| `universe` | `all` | `all` / `our_book` / `universe_not_held` |
| `mandate_file` | `<pack>/mandate.json` | open products for the route-level `nofa_offer` filter (`"none"` disables) |
| `geography_mode`, `counties[]`, `target_city` | `metro_core` | OHCS geography modes (`city_limits`, `county`, `metro_core`, `cbsa`) |
| `horizon_years`, `regulatory_horizon_years` | 10 | both families; bands are months (OVERDUE / CRITICAL 0-12 / URGENT 12-24 / APPROACHING 24-36 / MONITOR 36-60 / SCHEDULED 60-120 / BEYOND) |
| `servicing_extract` | — | the agency's own loan / grant / owned-asset ledger (schema `agency_servicing_extract`; see `references/servicing-extract.md`). Absent = degraded run (capital factor 0, `book_match book_absent`) |
| `book_coverage` | `partial` | `full` marks inventory rows the profile expects in book but could not join as `unmatched_expected` (Verify — Book Join) |
| `book_crosswalk` | `<pack>/book_crosswalk.csv` | analyst-confirmed `agency_loan_id / grant_id -> property_id` |
| `local_datasets[]`, `inbox` | — | OHCS inventory (required), HUD FHASL / Sec 8 tapes, OHCS forecast, REAC export, ZIP crosswalk, NOAH candidates; schemas detected from headers |
| `prior_run`, `prior_forecast` | — | prior run dir for status flips (the agency KPI) and the forecast diff |
| `noah_watch` | false | optional unregulated 5+ watch (`noah_watch.py`, route `nofa_offer` only); ask before enabling |
| `pii_scope` | `organization` | `public_packet` / `organization` / `internal` (`am_officer_email` needs `internal`; phones and skip-trace columns never exist) |
| `board_packet` | true | also write the stripped public-packet workbook and `board_packet.md` |
| `include_proxies` | false | emit the OHCS PROXY mini-perm maturities (the book supplies RECORDED maturities) |
| `handoff_routes[]`, `max_results`, `workbook_name`, `out_dir`, `as_of_date`, `scoring_dir`, `pipeline_mode`, `pipeline_root` | — | as named |

## Stage by stage (each script runs standalone)

| step | script | what it does |
|---|---|---|
| 1 | `ingest_servicing_extract.py --input <csv|xlsx> --pack <dir> --agency-profile hfa --out-dir <dir> [--internal]` | the agency's ledger -> RECORDED `AGENCY_LOAN_MATURITY`, `AFFORDABILITY_PERIOD_END`, `GRANT_RECAPTURE_END`, `COVENANT_DEFAULT`, `SHARED_APPRECIATION_DUE`, `QC_ELIGIBILITY` + `QC_RESPONSE_DUE`, `THIRD_PARTY_OFFER_RECEIVED` + `ROFR_MATCH_DEADLINE`, `PRESERVATION_NOTICE_RECEIVED` + `RECORDS_REQUEST_DUE`, `NONCOMPLIANCE_FINDING`, `REAC_SCORE`, `INSPECTION_DUE`, senior `LOAN_MATURITY` (REPORTED). Validates per `book_kind` (loan / grant / owned_asset / administered_contract); exit 2 names the failing rule |
| 2 | `ohcs_inventory_targets.py --input <csv> --pack <dir> --mode metro_core --out-dir <dir> [--include-proxies] [--xlsx]` | OHCS inventory -> REPORTED program ends, DERIVED Year 15, HAP expirations stamped with program + `term_unknown_annual_assumed`, past HUD dates -> `STALE_CONTRACT_DATE`, units columns (restricted / HAP / PRAC / other RA / PSH / 3BR+ / vulnerability flags), `ohcs_funded`, `site_type` |
| 3 | `normalize_hud_sec8.py`, `normalize_hud_insured.py`, `normalize_ohcs_forecast.py --ohcs-leads <leads.csv> [--prior]`, `normalize_reac_scores.py` | optional file-drop adapters (HAP contract tape with `hap_units_at_risk`, no owner phone; HUD-insured senior liens `senior_lien_type` / `senior_maturity` / `senior_upb`; forecast notice statuses + `status_flips.csv`; REAC/NSPIRE scores) |
| 4 | `merge_leads.py --inputs ... --events ... --book-leads <book leads.csv> --crosswalk <csv> --agency-profile hfa --book-coverage partial --out-dir <dir>` | one lead per property; book ⨝ inventory via `plb/book_join.py` (crosswalk > address > fuzzy >= 0.92 with phase tokens > unmatched); universe `our_book` / `universe_not_held`; `book_match`; dedupe key (property, type, program, detail); PROXY maturity dropped when a RECORDED ours exists |
| 2-6 | `build_universe.py --pack <dir> --mode metro_core --agency-profile hfa --ohcs <csv> [--book <csv>] [--book-coverage full] [--crosswalk] [--hud-sec8] [--hud-fhasl [--hud-fhasl-terminated]] [--forecast [--prior-forecast]] [--reac] [--zip-crosswalk] [--include-proxies] [--noah-watch --noah <csv>] --horizon-years 10 --out-dir <dir>` | runs steps 1-4, then `plb/units.py` (units / HAP / PRAC / PSH / UPB at risk, recapture exposure) and `plb/agency_calendar.py` (withdrawal anchor, both PuSH windows, every AGENCY_DEADLINE, `NOTICE_COMPLIANCE_BREACH`, stale HAP dates, owner cliff / agency act-by / action band) |
| 7 | `query_calendar.py --events <csv> --within-years 10 [--json out.json] [--show-helpers] [--show-agency]` | the header quoted in the brief: `RECORDED n / REPORTED n / DERIVED n / ESTIMATED n / PROXY n / Suppressed n / Rejected n \| helper deadlines n (...) \| agency act-by n (next 90 days m)` |
| 8 | `score_preservation.py --leads <csv> --events <csv> --pack <dir> --agency-profile hfa [--mandate <json>\|none] [--universe all] --out leads_scored.csv [--xlsx] [--explain pid] [--prior <leads_scored.csv>] [--internal]` | `references/scoring/affordable_public_am.json` (units 25 / clock 20 / declared intent 15 / our capital 15 / physical 10 / sponsor 10 / stacking 5) + `shared_adjustments.json`; queue bands ESCALATE >= 70 / ACT 50 / PLAN 30 / WATCH / EXCLUDED; eight routes by precedence `optout_response > notice_compliance > qc_admin > designee_rofr > recap_committee > servicing_watch > nofa_offer > ta_sponsor` under the profile's `routes_enabled`; sentinels `none` / `excluded`; mandate hard filter on `nofa_offer`; writes `units_at_risk.json` (the single source for Board_Totals) and the queue CSVs |
| 9 | `build_board_workbook.py --leads-scored <csv> --events <csv> --calendar <json> --rejects <csv> --pack <dir> --agency-profile hfa --out <xlsx> [--board-packet] [--prior <csv>] [--internal]` | 17-tab working file (Summary, Board_Totals, Intervention_Queue, Book_Watchlist, Preservation_Queue, Sponsor_Exposure, Notice_Compliance, Agency_Calendar, Mandate_Fit, Events, Regulatory, Owners_Sponsors, Book_Join_Gaps, Status_Flips, Sources_Vintages, Assumptions, Rejects_Verify) and the public-packet workbook + markdown with a Redaction_Log |
| 10 | `make_handoffs.py --leads-scored <csv> --out-dir <dir>/handoff --pack <dir> [--routes ...] [--queue ESCALATE ACT PLAN]` | sibling payloads (critical-dates-tracker, front-door-lihtc-underwriting composition mode + `agency_soft_debt[]`, sizing-lihtc-permanent-debt before/after recast, physical-condition-assessment, lihtc-lpa-reviewer 2C, sponsor-credibility-assessor only for applicants, off-market-deal-finder NOAH only), `documents_to_request.csv` (our own file room first), `sos_worklist.csv`, `board_packet.csv` |
| 11 | `diff_forecast.py --current <leads_scored.csv> --prior <prior leads_scored.csv> [--current-events] [--prior-events] --out status_flips.csv [--summary kpi_summary.json]` | KPI flips: notice_filed, tenant_notice_confirmed, qc_requested, qc_presented, hap_renewed, hap_optout, loan_extended, loan_recast, covenant_cured, covenant_default, recap_closed, preserved, lost (evidence only; a stale HAP date is never `lost`), new_to_list, left_list |
| — | `date_profile.py <csv> <column>` | proposes a declared date format for a new extract (day-first vs month-first) before an adapter sees it |
| — | `smoke_test_sources.py --pack <dir> [--live]` | checks `sources.md` URLs (offline by default) |
| — | `noah_watch.py --input noah_candidates.csv --pack <dir> --out-dir <dir>` | optional NOAH stub (off by default; route `nofa_offer` only; no outreach) |

Exit codes: 2 on a schema mismatch (the header does not match any `dataset-schemas.yaml` block, or every servicing row fails validation), 1 on any other error.

## Library (`plb/`)

| module | role |
|---|---|
| `schema.py` | every enum, the event taxonomy (asserted against `references/pipeline-contract.md` Section 3), `LEAD_COLUMNS`, `EVENT_COLUMNS`, servicing columns, embedded pack defaults and loaders (`load_dataset_schemas`, `load_market_params`, `load_agency_profiles`, `load_mandate`, `detect_schema` with `match_any`) |
| `dates.py` | declared-format parsing (day-first / month-first / USDA / Excel serial / auto with Verify — Ambiguous), month arithmetic, urgency bands (months) |
| `geo.py` | county-FIPS geography modes, address normalization, `property_id` |
| `calendar.py` / `query_calendar.py` | the three-segment basis header |
| `adapters.py` | shared adapter helpers (`read_table`, `resolve_columns`, `make_event`, `first_events`, `write_outputs`) |
| `entities.py` | owner_type inference, self-owned detection, natural-person check, sponsor archetypes (intervention owner, never an approach angle) |
| `book_join.py` | servicing extract <-> inventory join grades |
| `units.py` | units / HAP / PRAC / other RA / PSH / UPB / grant at risk; `units_at_risk_json` Board_Totals pivot and book verdict |
| `agency_calendar.py` | withdrawal anchor, PuSH windows, AGENCY_DEADLINE events, `AGENCY_DEADLINE_META` (owner role + cite per type), stale contract dates |
| `scoring.py` | JSON-driven engine (match DSL incl. `absent` / `contains`, factor `requires`, basis multipliers, recap_status multiplier, caps), routing by precedence, `explain()` |
| `mandate.py` | NOFA product predicate (route-level hard filter) |
| `recap_math.py` | loan constant, amortization, restricted NOI, recap gap, recapture exposure, ESTIMATED QC price band (no refinance test) |
| `pii.py` | sunshine scopes (`public_packet` / `organization` / `internal`), NEVER columns, redaction log, `RECORDS_CLASSIFICATION` |
| `interventions.py` | catalog metadata mirrored from `assets/interventions/*.md` (first action, agency owner, cite, owner / tenant notice) |
| `workbook.py` | openpyxl renderer for the working file and the board packet |

## Tests

```bash
python3 scripts/tests/run_tests.py          # pytest-compatible (run_tests.py sets PYTHONDONTWRITEBYTECODE; no __pycache__ is shipped)
OHCS_CSV=/path/to/Oregon_Affordable_Housing_Inventory_YYYYMMDD.csv python3 scripts/tests/run_tests.py
```

Real-file tests (`test_ohcs.py`, `test_book_join.py::test_real_inventory_joins_at_least_eight_fixture_rows`) skip when the OHCS
inventory is absent. Fixtures in `tests/fixtures/`: the synthetic servicing extract (`agency_servicing_sample.csv`, 14 rows whose
names and addresses are copied byte-for-byte from the real inventory plus two our-loan-not-in-OHCS rows), `pha_book_sample.csv`,
`agency_servicing_bad_schema.csv`, `book_crosswalk_sample.csv`, `reac_scores_sample.csv`, `mandate_sample.json`,
`prior_leads_scored_sample.csv`, the extended `ohcs_sample.csv` (past annual HAP, HAP-only 8 months out, an individual owner) and
the v2 HUD / forecast / crosswalk fixtures. `test_contract.py` fails when the markdown taxonomy and `schema.py` drift.

## Conventions

* The agency's own ledger is RECORDED; nothing infers a maturity (PROXY mini-perm dates are opt-in and capped at PLAN).
* A/B/C tiers never appear. `queue_band` is ESCALATE / ACT / PLAN / WATCH / EXCLUDED; `primary_route` is one of the eight
  agency routes or the sentinels `none` (monitoring) / `excluded` (with `exclusion_reason`). A book row with no dated cliff
  inside the horizon stays on the Book_Watchlist as `none`; only inventory rows are EXCLUDED for `no_dated_cliff_in_horizon`.
* PHA / nonprofit sponsors score sponsor-capacity plus and route `ta_sponsor` / `recap_committee` with no cap; a for-profit or
  aggregator GP at Year 15 is a preservation-risk plus. Nothing subtracts in the sponsor factor.
* Missing book join is factor-scoped: `unmatched_expected` zeroes our_capital_at_risk with factor status WATCH and
  `Verify — Book Join`; the queue band is never capped and no balance is guessed.
* Silence inside the first-notice window is not late (`push_window_open_prep`, notice_compliance secondary only); after
  `PUSH_FIRST_NOTICE_DUE` only `not_received_confirmed` is a `NOTICE_COMPLIANCE_BREACH`; `unknown` scores 6 with
  `Verify — Notice Log`. No demand or records letter is generated before the statutory trigger it cites.
* A past HAP / PRAC date with no termination evidence is `STALE_CONTRACT_DATE` (own Board_Totals row, never OVERDUE, never `lost`).
* Default outputs are organization level: `am_officer` yes, `am_officer_email` only with `--internal`, never a phone, email,
  cell or skip-trace column; the board packet withholds natural-person owners and residential registered-agent addresses.
* Every statutory cite carries verify text; ORS 456.265 is "sanctions against withdrawing owner prohibited", never a fine.
