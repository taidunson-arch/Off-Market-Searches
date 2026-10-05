# scripts/ — off-market-deal-finder v2

File-drop pipeline that turns public inventories, government loan/subsidy tapes, recorder-index and assessor exports into
an evidence-graded target list. No script makes a network call; the analyst downloads files into an inbox and the scripts
read them. Every dated event carries a `basis` (RECORDED / REPORTED / DERIVED / ESTIMATED / PROXY) and a `source`, and
today's date is always `date.today()` unless `--as-of YYYY-MM-DD` is passed.

Requirements: Python 3.10+, `pip install -r scripts/requirements.txt` (pandas, openpyxl, pyyaml).
Run every command from the skill root (`/home/user/off-market-deal-finder-v2` or wherever the skill is installed).

## Run order (one command)

```bash
cp references/sample-output/run_config.example.json run_config.json   # edit paths, geography_mode, horizon, query_type, owner_types_exclude
python scripts/run_pipeline.py --config run_config.json [--prior-run runs/2026-07-01] [--explain <property_id>]
#   stages: discover -> adapters -> merge -> calendar -> score -> workbook -> handoffs -> brief -> diff
#   --from <stage> restarts at a stage using artifacts already in runs/<as_of>/
```

Every documented run-config input reaches the scripts: `query_type`, `owner_types_include` / `owner_types_exclude`,
`lender_types`, `price_or_value_band`, `buyer_profile`, `unit_range`, `programs`, `strict_size_fit` are passed to
`score_leads.py` and recorded in `manifest.json` under `flags`.

Outputs land in `runs/<as_of>/`: `leads.csv`, `events.csv`, `rejects.csv`, `calendar_summary.json`,
`leads_scored.csv`, `<workbook>.xlsx` (11 tabs), `handoff/<sibling-skill>.json`, `handoff/sos_worklist.csv`,
`handoff/documents_to_request.csv`, `brief.md`, `diff.csv`, `sources_used.json`, `manifest.json` (config snapshot,
input sha256 + vintage + vintage_source, flags, sources still verified_live=false, stage log).

## Adapters (file-drop; one per dataset schema in the pack's `dataset-schemas.yaml`)

| schema id | script | classes | emits | status |
|---|---|---|---|---|
| `ohcs_affordable_housing_inventory` | `ohcs_inventory_targets.py` | 3 | REPORTED program ends, HAP (0.70), USDA; DERIVED Year 15; PROXY mini-perm; PuSH window (gated, DERIVED) with `push_window_open`; `ppu_band` value proxy | verified against the real file |
| `hud_fhasl_active` (+ terminated) | `normalize_hud_insured.py` | 2, 3 | LOAN_MATURITY / HUD_DIRECT_LOAN_MATURITY RECORDED; PREPAY_WINDOW_OPEN DERIVED; REFINANCE_CLOSED + SUPPRESS_UNTIL | template: field names via alias table, `verified_live=false` |
| `hud_mf_assistance_sec8` | `normalize_hud_sec8.py` | 3 | HAP_EXPIRATION REPORTED 0.70, HAP_OPTOUT_NOTICE_DEADLINE DERIVED; owner / agent names | template, `verified_live=false` |
| `ohcs_push_forecast` | `normalize_ohcs_forecast.py` | 3 | `on_state_expiring_list`; PRESERVATION_NOTICE_RECEIVED RECORDED on notice statuses; STABILIZATION_AWARD; `--prior` status-flip diff | template: field names and status vocabulary are guesses, `verified_live=false` |
| `recorder_index_export` | `normalize_recorder_index.py` | 1, 2 (3 for recorded instruments) | NOD / NOTS with derived sale and cure clocks, pre-NOD instruments, lis pendens, liens, trustee's deed, rescission, modification, ROFR; LOAN_MATURITY RECORDED when printed else ESTIMATED from recording + lender term; REFINANCE_CLOSED / SUPPRESS_UNTIL / UNENCUMBERED | canonical column names; rename the county export first |
| `assessor_taxlots` | `normalize_assessor_taxlots.py` | 1, 2 | ABSENTEE_TIER, HOLD_YEARS, DEPRECIATION_EXHAUSTED, RECENT_1031_ACQUISITION, TAX_DELINQUENT_YEARS; `mailing_address`, `av_rmv_ratio`, `est_value` rmv_calibrated | SAIL / RLIS field names from a third-party tool, `verified_live=false` |

Still specified but not shipped (`sources.md` marks them `future`): HUD LIHTC DB, HUD REAC, USDA MFH exit, Ginnie Mae, DUS Disclose, MSIA, EDGAR EX-102 adapters.

## Run order (step by step)

| step | command | notes |
|---|---|---|
| 0 profile dates | `python scripts/date_profile.py <file>` | prints first-field>12 / second-field>12 per column and a YAML snippet; run on any file not yet in the pack's dataset-schemas.yaml |
| 1a HFA inventory | `python scripts/ohcs_inventory_targets.py --input <ohcs.csv> --pack references/sources/oregon-portland --mode metro_core --horizon-years 5 --out-dir runs/x/ohcs [--xlsx]` | aliases `--metro`, `--city Portland` (city_limits, graded `city_name_weak`), `--county 41051,41067`; `--auto-detect-dates` opts into per-value day/month detection with `Verify — Ambiguous` flags; numeric columns are comma-cleaned (`2,021` -> 2021) |
| 1b HUD insured | `python scripts/normalize_hud_insured.py --input <FHASL_Active.xlsx> --terminated <FHASL_Terminated.xlsx> --counties 41051,41067,41005 --zip-crosswalk <crosswalk.csv> --out-dir runs/x/hud_fhasl` | TEMPLATE: names missing fields instead of guessing |
| 1c HUD Sec 8 | `python scripts/normalize_hud_sec8.py --input <MF_Assistance_Sec8_Contracts.xlsx> [--properties <MF_Properties.xlsx>] --counties ... --zip-crosswalk ... --out-dir runs/x/hud_sec8` | TEMPLATE as above; HAP_EXPIRATION at confidence 0.70 |
| 1d OHCS forecast | `python scripts/normalize_ohcs_forecast.py --input <forecast.csv> --ohcs-leads runs/x/ohcs/leads.csv [--prior <older forecast.csv>] --counties ... --out-dir runs/x/forecast` | TEMPLATE; reuses OAHI property_ids by name + address; `status_flips.csv` |
| 1e recorder index | `python scripts/normalize_recorder_index.py --input <recorder.csv> --pack references/sources/oregon-portland --counties 41051 --out-dir runs/x/recorder` | canonical columns `instrument_no, doc_type, recording_date, grantor, grantee` (+ optional parcel/address/zip/stated_principal/maturity_date/sale_date/sum_owing/units); lender tokens from `assets/lender_type_dictionary.csv` |
| 1f assessor roll | `python scripts/normalize_assessor_taxlots.py --input <taxlots.csv> --pack references/sources/oregon-portland --out-dir runs/x/assessor` | SAIL / RLIS field names; `rmv_sales_ratio` from market-params (1.0 placeholder, verify) |
| 2 merge | `python scripts/merge_leads.py --inputs a/leads.csv b/leads.csv --events a/events.csv b/events.csv --out-dir runs/x` | unions on `property_id`; fuzzy name+zip >= 0.92 across sources only, never across phases; applies SUPPRESS_UNTIL; carries adapter extra columns (mailing_address, lender_type, on_state_expiring_list) |
| 3 calendar | `python scripts/query_calendar.py --events runs/x/events.csv --within-years 5 [--regulatory-within-years 5] [--json runs/x/calendar_summary.json] [--show-helpers]` | prints the header the brief must quote: `RECORDED n / REPORTED n / DERIVED n / ESTIMATED n / PROXY n / Suppressed n / Rejected n \| helper deadlines n`; helper deadlines (notice arithmetic, LATEST duplicates) and SUPPRESSION/ROUTING rows are never inside the five basis counts |
| 4 score | `python scripts/score_leads.py --leads runs/x/leads.csv --events runs/x/events.csv --out runs/x/leads_scored.csv [--class auto] [--query-type maturity] [--owner-types-exclude housing_authority] [--lender-types bank_cu] [--buyer-profile principal] [--unit-range 20,120] [--price-band 2000000,15000000] [--strict-size-fit] [--programs LIHTC_9,HAP] [--xlsx runs/x/targets.xlsx] [--explain <property_id>]` | reads `references/scoring/*.json` only (a missing directory is an error, there is no embedded fallback); writes `query_hit`; `--explain` prints the arithmetic |
| 5 workbook | `python scripts/build_workbook.py --leads runs/x/leads_scored.csv --events runs/x/events.csv --calendar runs/x/calendar_summary.json --rejects runs/x/rejects.csv [--prior prior/leads_scored.csv] --out runs/x/targets.xlsx [--recalc]` | cells are literals, so recalc is off by default; `--recalc` runs `/mnt/skills/public/xlsx/scripts/recalc.py` when it exists |
| 6 handoffs | `python scripts/make_handoffs.py --leads runs/x/leads_scored.csv --tier A [--tier B] --out-dir runs/x/handoff --pack references/sources/oregon-portland` | one JSON per sibling skill plus `sos_worklist.csv` and `documents_to_request.csv` |
| 7 sources | `python scripts/smoke_test_sources.py --pack references/sources/oregon-portland [--live]` | dry run by default (no network); `--live` probes URLs and flips `verified_live` in `sources_status.json` only on success; never edits the .md; `run_pipeline.py` reads live results |
| worked example | `cd scripts && python -m omdf.capital_stack --selftest` | amortization / refi-gap arithmetic on a 60-unit example |

## Tests

```bash
python scripts/tests/run_tests.py [-k substring]      # 56 tests; pytest also works if installed
OHCS_CSV=/path/to/Oregon_Affordable_Housing_Inventory_YYYYMMDD.csv python scripts/tests/run_tests.py
```

`test_ohcs.py` runs the real inventory when it is present (default path is the session scratchpad; set `OHCS_CSV`) and
skips those cases otherwise; the fixture cases always run. `test_contract.py` parses `references/pipeline-contract.md`
and fails when the event table or the events.csv column list drifts from `omdf/schema.py`. `test_calendar.py` asserts
helper deadlines never appear in the basis counts. `test_adapters.py` covers the recorder, assessor and forecast
fixtures. Fixtures in `tests/fixtures/` are synthetic: HUD and forecast rows carry the layout's field names but invented
values; recorder and assessor rows use the canonical column names.

## Library (`omdf/`)

| module | what it holds |
|---|---|
| `schema.py` | every enum string (asset_class, basis, verify_flag, event taxonomy with family/direction, HELPER_EVENTS, PUSH_COVERED_PROGRAMS, owner_type, route, tier, program, lender_type), canonical lead/event/reject columns, `clean_numeric` / `apply_numeric_block`, loaders that prefer the pack files (default pack: `references/sources/oregon-portland`) |
| `calendar.py` | `split_helper_rows`, `basis_counts`, `header_line`: the one place the quoted header is computed |
| `dates.py` | `parse_value` / `parse_column` with declared formats (`%d/%m/%Y`, `%m/%d/%Y`, `%Y %b %d %I:%M:%S %p`, `excel_date`, `auto`), `profile_series`, months_out, urgency bands, `parse_as_of` (the only clock read) |
| `geo.py` | county FIPS maps, Portland geography modes, address normalization, `property_id`, WKT parsing, ZIP-county crosswalk loader |
| `capital_stack.py` | `loan_constant`, `amortized_balance`, `noi_proxy`, `restricted_noi`, `refi_test`, `inferred_maturity`, `value_proxy` |
| `scoring.py` | JSON-driven engine: match DSL, factor/band/modifier evaluation, basis multipliers, penalties, deal-size and price-band multipliers, owner_type / lender_type filters, buyer_profile gating, query_hit, routes, caps, tiers, `explain` |
| `entities.py` | `infer_owner_type` from Owner Type + name tokens, archetype table (decision maker, template, angle, default route), SOS worklist rows, contact grades |
| `adapters.py` | header alias resolution with named mismatches, county resolver, event/lead builders shared by the adapters |
| `workbook.py` | openpyxl renderer for the 11-tab workbook with tier/basis fills, freeze panes, autofilter, Analyst-status dropdown, file-verified vs URL-verified source columns |

## Conventions the scripts enforce

- Geography is a county-FIPS set; a city string is only used in `city_limits` mode and is graded `city_name_weak`.
- A column verified day-first is never re-tested row by row; `auto` is opt-in and flags every ambiguous value.
- A loan maturity inferred from `Financial_Closing_Date + 15y` is `PROXY` with a +/-36-month window and, alone, caps a lead at Tier C; one inferred from a recording date and a lender-type term is `ESTIMATED` with a min..max-term window.
- Status `In Development` is excluded; `SUPPRESS_UNTIL` in the future zeroes DEBT factors only.
- No lender, balance, maturity, GP name or contact is ever invented: the field says `not in public record`; tape-lender trust deeds get a `Needs Anchor Date: pull the tape` flag instead of an inferred date.
- Housing authorities, governments, nonprofits and any property with a recorded ROFR route to `partnership_preservation`; `owner_types_exclude` removes a class of owner from the ranked list with the reason recorded.
- A file opened on disk is `file_verified`; it never makes a source `verified_live`.

## Deviation from the build spec (documented)

Spec Section 5.5 asks a test that a lone RECORDED `LOAN_MATURITY` at 9 months with `refi_gap_pct 0.30` "reaches Tier A".
With the canonical weights (capital_stack_timing 25 + refinance_gap_coverage 20) that lead scores 17 + 14 = 31, so
Tier A is arithmetically unreachable from two factors. `tests/test_score.py::test_recorded_maturity_9mo_with_refi_gap_has_no_cap`
asserts the enforceable contract instead: the lead is scored on its merits with no tier cap (Tier C at 31), and a
companion test shows a stacked RECORDED lead reaching Tier A.
