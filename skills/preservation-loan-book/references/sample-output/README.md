# Sample output — Portland tri-county, hfa profile, 10-year board horizon

A script-generated run of `scripts/run_agency_pipeline.py` as of **2026-10-04** (`agency_profile hfa` = Oregon Housing and
Community Services, `geography_mode metro_core` = Multnomah 41051 / Washington 41067 / Clackamas 41005, `horizon_years 10`
for both the debt and regulatory families, `pii_scope organization`, `book_coverage partial`, `include_proxies false`,
`noah_watch false`). `run_config.example.json` is the config with paths rewritten relative to the skill root; replace the
`local_datasets` placeholder with the OHCS inventory export and `servicing_extract` with the agency's own ledger, then run
`python3 scripts/run_agency_pipeline.py --config references/sample-output/run_config.example.json` from the skill root.

## What is real and what is synthetic

| input | real / synthetic | what it contributes |
|---|---|---|
| OHCS Affordable Housing Inventory (`Oregon_Affordable_Housing_Inventory_20261002.csv`, 1,819 rows x 53 columns, vintage 2026-10-02 from the filename) | **real** (public OHCS export) | every inventory property, unit count, program end date (REPORTED), Year 15 (DERIVED), HAP/PRAC expiration (REPORTED, annual term assumed), PuSH windows and agency deadlines (DERIVED), owner organizations, PSH / RA counts |
| `scripts/tests/fixtures/agency_servicing_sample.csv` (14 rows) | **synthetic** | the agency's "book": 8 rows whose names and addresses are copied byte-for-byte from real tri-county inventory rows (Village Garden Apartments, Powell Plaza I, Yards at Union Station A, Cathedral Gardens, GOING 42, Town Center Courtyards, St Anthony Village, Rose Schnitzer Tower), one fuzzy-join row ("Village Gardens Apartments"), two crosswalk / same-day-maturity fixture rows, and two our-loan-not-in-OHCS rows (Hollow Oak Commons, Sumner Street Flats). **Every public UPB, maturity, covenant status, am_officer and recapture figure is illustrative**; the real OHCS book is not public. |
| `scripts/tests/fixtures/book_crosswalk_sample.csv` | synthetic | analyst crosswalk for one fixture row |
| `references/sources/oregon-portland/mandate.json` | placeholder products, `verified_live: false` | the route-level `nofa_offer` filter |
| HUD MF Assistance / Sec 8 tape, HUD FHASL, OHCS 10-year forecast, REAC export | **absent** in this run | so `notice_status` is `unknown` for every inventory row (silence is never inferred), HAP terms are `term_unknown_annual_assumed`, and the run is reported as degraded in the brief |

## Files

| file | content |
|---|---|
| `brief.md` | the fixed-structure brief: Run Summary (calendar header quoted verbatim, incl. the agency act-by segment), Board Totals, Agency Act-By Calendar (next 90 days), Intervention Queue cards grouped by route precedence, Book Watchlist, Preservation Queue, Notice Compliance, Mandate Fit, Status Flips (no prior run), Pipeline not scored, Data Gaps, Assumptions |
| `board_packet.md` | the public-packet variant (organization + registered agent only; natural-person owners withheld with a Redaction Log citing ORS 192.355(2), verify) |
| `Portland_TriCounty_Preservation_LoanBook_10yr.xlsx` | the 17-tab working file: Summary, Board_Totals, Intervention_Queue, Book_Watchlist, Preservation_Queue, Sponsor_Exposure, Notice_Compliance, Agency_Calendar, Mandate_Fit, Events, Regulatory, Owners_Sponsors, Book_Join_Gaps, Status_Flips, Sources_Vintages, Assumptions, Rejects_Verify |
| `Portland_TriCounty_Board_Packet.xlsx` | the stripped board workbook: Board_Totals, Preservation_Queue, Sponsor_Exposure, Status_Flips, Redaction_Log, Assumptions |
| `leads_scored.csv` | one row per property (768) with every lead column, `factors_json` and the queue / route outputs; `scripts/tests/test_evals.py` runs `evals/evals.json` against it |
| `units_at_risk.json` | the single source for Board_Totals (by owner_cliff_band, by jurisdiction, by year, headline, book verdict, KPI rows) |
| `calendar_summary.json` | the calendar summary whose `header` the brief quotes (input paths replaced with `<data-dir>` / `<out-dir>` placeholders) |
| `servicing_unmatched.csv` | the four book rows the inventory does not hold |
| `run_config.example.json` | the run configuration |

Not copied (regenerate by running the pipeline): `leads.csv`, `events.csv` (4,414 rows), `rejects.csv`, `merge_log.csv`,
`book_join_gaps.csv`, `agency_calendar.csv`, `notice_compliance_queue.csv`, `nofa_targets.csv`, `sponsor_exposure.csv`,
`optout_qc_responses.csv`, `pipeline_not_scored.csv`, `result.json` (16 MB), `manifest.json`, `sources_used.json`, `handoff/`.

## Headline numbers of this run

* Discover: 1,819 rows -> 810 in metro_core -> 46 `In Development` excluded (listed under "Pipeline, not scored") -> 764
  inventory leads + 4 book-only rows (`book_match book_only`) = **768 leads**, 4,407 events.
* Header: `RECORDED 20 / REPORTED 217 / DERIVED 83 / ESTIMATED 0 / PROXY 0 / Suppressed 0 / Rejected 0 | helper deadlines 595
  (notice arithmetic, LATEST duplicates; not counted above) | agency act-by 384 (next 90 days 20)`. The 20 RECORDED events
  are all from the synthetic book; with the inventory alone the run has no RECORDED date.
* Book join: crosswalk 0 / address 8 / fuzzy 1 / unmatched 4; `book_match` matched 12 / not_in_extract 756 (coverage
  `partial`, so no `unmatched_expected`); universe our_book 12 / universe_not_held 756; book rows monitored 1 vs on watch 11.
* Queue: ESCALATE 1 / ACT 3 / PLAN 55 / WATCH 207 / EXCLUDED 502. Primary routes: excluded 502 (no dated cliff inside
  10 years, 5+ unit gate, geography), none 141 (monitoring), nofa_offer 97, ta_sponsor 14, optout_response 5,
  servicing_watch 5, recap_committee 3, qc_admin 1, notice_compliance 0 as a primary: no notice log is loaded in this run,
  so the 18 "first due passed, notice_status unknown" rows carry notice_compliance as a SECONDARY confirm-the-log route
  with `Verify — Notice Log` (it becomes primary when `notice_log_status` is populated or a PuSH forecast is loaded).
* Board headline (owner cliff inside 36 months, or OVERDUE without termination evidence — 15 of the 87 are OVERDUE verify cases): **87 properties / 5,690 restricted units / 771 HAP units / 567 PRAC
  units / 14 PSH units / $11,330,000 public UPB**; by county Multnomah 63 / 4,404 units, Washington 13 / 850, Clackamas
  11 / 436. Book verdict CRITICAL on the fixture book ($12,830,000 of $15,480,000 UPB on watch) — a property of the
  synthetic extract, not of OHCS's real book.
* Board_Totals by owner_cliff_band (properties / units at risk / HAP / PRAC / PSH / $UPB at risk): OVERDUE 15 / 778 / 0 /
  19 / 0 / 0; CRITICAL 22 / 1,136 / 95 / 0 / 0 / 850,000; URGENT 20 / 1,579 / 291 / 375 / 0 / 5,600,000; APPROACHING
  30 / 2,197 / 385 / 173 / 14 / 4,880,000 (public_grant_at_risk 480,000: Sumner Street Flats, rental HOME `full`); MONITOR 39 / 2,307 / 534 / 15 / 17 / 0; SCHEDULED 75 / 5,533 / 1,867 / 19 /
  98 / 1,500,000; beyond horizon 275 / 19,767 / 1,312 / 148 / 808 / 0 (public_grant_at_risk 1,100,000: GOING 42, rental HOME `full` under 24 CFR 92.503(b)); stale contract date — verify 14 / 269 / 30 /
  229 / 0 / 0; no dated cliff 278 / 8,655 / 0 / 0 / 22 / 0.
* Data gaps: 33 stale HUD contract dates (request the current HAP contract / TRACS; never OVERDUE, never `lost`), 18
  notice-log unknowns after the first-notice due date (Verify — Notice Log), 5 CA-log unknowns after the opt-out notice
  deadline (Verify — CA Log), 112 documents to request from the agency's own file room, 54 organizations on the SOS
  worklist, owner type unknown on 224 of 768 rows (OHCS leaves Owner Type blank on 443 of 810 metro rows).
* The 5-year horizon run (not shipped) yields the identical Board headline because Board_Totals band on owner_cliff_band
  and the 36-month window sits inside both horizons; only WATCH / EXCLUDED counts move (WATCH 104 / EXCLUDED 604).

## The five named evals in this run

| eval | property (real OHCS row unless noted) | result in this run |
|---|---|---|
| E1 PuSH window open | Village Garden Apartments, Portland, 35 units, Village Garden, LLC, restriction end 2029-06-01 | our_book (L-OHCS-0001, address join); window `open_first`; PUSH_WINDOW_PREP 2026-06-01 (passed), PUSH_FIRST_NOTICE_DUE 2026-12-01, PUSH_SECOND_NOTICE_DUE 2027-06-01, no RECORDS_REQUEST_DUE; declared intent 0 (`push_window_open_prep`); primary servicing_watch, secondary notice_compliance; PLAN 45.6 |
| E2 HAP annual vs long-dated | Powell Plaza I, Portland, 47 units, HAP 2027-03-31, 47 RA units; contrasts Garden Grove Apartments (HAP 2040) and Silvercrest Residence (PRAC 2029) | optout_response / optout_tenant_notice_check / pbca_liaison; act-by HAP_OPTOUT_PACKAGE_DUE 2026-12-01 (CRITICAL); passed one-year notice deadline -> `Verify — CA Log`; hap_units_at_risk 47; clock 15.3; PLAN 36.6. Garden Grove: no opt-out route, owner cliff is its OAHTC end 2028-12-01 (nofa_offer). Silvercrest: prac_units_at_risk 75, never optout_response |
| E3 HOME-only PJ | metro has 0 HOME-only rows (statewide 3); GOING 42 (HOME 2058 with LIHTC); Sumner Street Flats (synthetic PJ-only row) | GOING 42: our_book, BEYOND, WATCH, `none`, recapture exposure the full $1,100,000 (rental HOME, 24 CFR 92.503(b); never pro-rated as homebuyer assistance); Sumner Street Flats: servicing_unmatched (book_only), AFFORDABILITY_PERIOD_END 2029-06-30 APPROACHING, recapture exposure the full $480,000, PuSH window flagged Verify — PuSH Coverage (HOME-only), servicing_watch / covenant_recapture_review / cpd_program_manager, recapture exposure $131,399, PLAN 36.0 (32.0 under the cdbg_home profile with INSPECTION_DUE 2027-01-15) |
| E4 PHA-owned | Yards at Union Station A, Portland, 158 units, Home Forward, restriction end 2028-01-01 | hfa (this run): our_book (L-OHCS-0003), ESCALATE 74.0, primary recap_committee / loan_extension_recast_memo (our RECORDED maturity 2028-01-01 inside 24 months), secondary notice_compliance / push_window_prep (first- and second-notice due dates passed, notice log unknown and no log loaded -> Verify — Notice Log), servicing_watch / ta_sponsor, sponsor capacity 10, no cap. pha_am variant (regenerated by `test_evals.py`): self_owned, recap_committee / pha_repositioning, ACT 66.0, URGENT |
| E5 our loan not in OHCS | Hollow Oak Commons (synthetic), $1,850,000, matures 2029-06-30, covenant watch, 30 assisted units | servicing_unmatched; our_book, book_match book_only, in_inventory false; no PuSH clock (the book row has no restriction end; nothing inferred from the inventory); AGENCY_LOAN_MATURITY 2029-06-30 APPROACHING; capital 12 + units 14 = 26.0, WATCH, servicing_watch / covenant_enforcement_notice; $1,850,000 inside the APPROACHING public UPB at risk |

## Checks that pass on these files (`python3 scripts/tests/run_tests.py -k test_evals`)

No `tier` / `motivation_score` / outreach column; no phone, email, cell or skip-trace column (`am_officer` present,
`am_officer_email` absent); queue bands only ESCALATE / ACT / PLAN / WATCH / EXCLUDED; the brief quotes the calendar header
verbatim; brief Board Totals == `units_at_risk.json` == both workbooks' Board_Totals == the board packet; the OVERDUE row
carries 0 HAP units (stale HAP dates sit in their own row); no buyer vocabulary ("Tier A", "motivated seller", "approach
angle", "skip trace", "IOI") in the brief or packet.

## Known presentation nits (not fixed in this build)

* Village Garden Apartments joins both a loan (L-OHCS-0001) and a fuzzy-matched grant row (G-OHCS-0012); its card and
  Book_Watchlist row print `book_kind loan;grant` (BOOK_KINDS order, loan first) with `payment_type` from the loan row.
* The `[universe]` log line prints `stale HUD dates 0` although 33 stale contract dates are counted in Board_Totals and
  the Data Gaps section (the log counter reads a column the adapter fills later); the outputs are right.
