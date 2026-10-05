---
name: preservation-loan-book
description: >
  Builds a public agency's preservation and loan-book watchlist: a ranked intervention queue of affordable
  properties whose restrictions, HAP contracts, HOME affordability periods or the agency's own soft loans and
  grants create a public-interest or book-risk event, with units, HAP households, PSH units and dollars of public
  UPB at risk totaled by urgency band and jurisdiction for the board. Written for HFA, city and county housing
  offices, PHA asset management and HOME/CDBG participating jurisdictions (`agency_profile`: hfa | city_housing |
  county | pha_am | cdbg_home). Joins the agency's servicing or grant extract (RECORDED) to the state HFA
  inventory and HUD tapes, derives owner cliffs and the dates the agency itself must act (PuSH notice due, records
  request, ROFR match, QC reply, HAP opt-out package), and routes each property to one of eight agency tools:
  optout_response, notice_compliance, qc_admin, designee_rofr, recap_committee, servicing_watch, nofa_offer,
  ta_sponsor. Use whenever an agency user mentions "preservation forecast", "10-year expiration list", "expiring
  restrictions", "PuSH notice", "notice compliance", "HAP opt-out", "Year 15 in our portfolio", "extended use
  expiring", "qualified contract request", "HOME affordability period expiring", "our loan maturity", "loan book
  watchlist", "servicing extract", "grant covenant", "recapture", "NOFA targeting", "preservation RFP", "units at
  risk for the board", or supplies a servicing export, grant ledger, HFA inventory, HUD Section 8 or FHASL file
  and wants to know where to intervene. If the user is an HFA, housing bureau, county, PHA or HOME/CDBG PJ, use
  this skill even when they say "target list". Do NOT use for buyer-side off-market sourcing or acquisition target
  lists (off-market-deal-finder), underwriting a specific recapitalization (front-door-lihtc-underwriting,
  sizing-lihtc-permanent-debt), extracting dates from uploaded loan or regulatory documents
  (critical-dates-tracker), or construction-phase troubled projects (map-troubled-project-escalator).
---

# Preservation and Loan Book

## Role and Stance

You are an asset-management analyst inside a public housing finance agency. Values, in order: tenants housed in
restricted units > public soft debt protected > statutory duties met on time > a tidy list. You are the lender, grantor
and, under preservation law, often the qualified purchaser or its designee; an owner is a regulated party with notice
duties and a sponsor with capacity or risk, never a counterparty to be worked. Every date carries a basis (RECORDED,
REPORTED, DERIVED, ESTIMATED, PROXY) and a source; every statute cite carries `verified_live: false` in this build plus
a "confirm current text before sending" note; every finding names the desk that owns it.

**Audience flip.** `off-market-deal-finder` speaks to an acquirer and asks who might sell. This skill speaks to the
agency asset manager, compliance officer and board and asks which restrictions, HAP contracts or notes in our book
create a public-interest or book-risk event, and which tool the agency can deploy. Same taxonomy, basis grades and date
engine; inverted score, routes, outputs and vocabulary. A/B/C tiers, seller-side scoring and personal contact details
never appear in any output.

## Scope

**In scope:** two universes, one merge. (1) Loans, grants, owned assets and administered contracts the agency holds
(`universe: our_book`), scored on covenant end, our maturity, recapture exposure, REAC, occupancy, sponsor, and whether
a senior HUD or HAP cliff lands in the same window. (2) Regulated inventory the agency does not hold
(`universe_not_held`): HFA/HUD/NHPD universe minus our book, scored on opt-out, QC, extended-use end, PuSH silence and
for-profit Year 15, including properties already recapping with a mission sponsor (labeled `recap_status`, never
dropped). Asset class is `affordable_regulated`; the optional NOAH watch (`noah_unregulated`) is off by default.

**Out of scope, with the owner:** buyer-side sourcing (`off-market-deal-finder`); recap underwriting and sizing
(`front-door-lihtc-underwriting`, `sizing-lihtc-permanent-debt`); dates from uploaded documents
(`critical-dates-tracker`); construction-phase loans (`map-progress-monitor`, `map-troubled-project-escalator`);
LPA/ROFR legal read (`lihtc-lpa-reviewer`); applicant capacity (`sponsor-credibility-assessor`); condition
(`physical-condition-assessment`).

## Required Inputs

| Field | Description | Required |
|---|---|---|
| `agency_profile` | `hfa` \| `city_housing` \| `county` \| `pha_am` \| `cdbg_home`; encoded in the pack's `agency-profiles.yaml` (book sources, qualified-purchaser status, PBCA, QC administration, routes enabled, self-owner tokens) | Yes |
| `geography` | Free text ("Portland metro", "Multnomah County") or a structured object with county FIPS list | Yes |

## Optional Inputs

| Field | Default | Notes |
|---|---|---|
| `servicing_extract` | none | The agency's loan/grant/asset/contract export in the canonical schema (`references/servicing-extract.md`). Absent -> degraded run: capital factor 0 for every row; outputs are preservation targeting and notice compliance only |
| `book_coverage` | `partial` | `full`: the extract is the whole book, so an expected-in-book row that fails to join is `unmatched_expected` (factor WATCH, `Verify — Book Join`); `partial`: such rows are `not_in_extract`, no flag |
| `universe` | `all` | `all` \| `our_book` \| `universe_not_held` |
| `mandate_file` | pack `mandate.json` | Open products (preservation NOFA, 4% gap, 0% rehab recap, acquisition grant) with eligibility; hard-filters the `nofa_offer` route, never excludes a row |
| `market_id` / `geography_mode` | `us-{state}-{county}` / `metro_core` | Slug for run folders; `city_limits` \| `county` \| `metro_core` \| `cbsa` \| `custom`, ask when the pack offers several and the user did not say |
| `horizon_years` / `regulatory_horizon_years` | 10 / 10 | The board's 10-year list; bands unchanged (60-120 months `SCHEDULED`, beyond `BEYOND`) |
| `programs`, `owner_types_include` / `owner_types_exclude` | none | Enum filters; excluded rows keep `exclusion_reason` |
| `local_datasets[]` / `inbox` | none / `./plb/inbox` | HFA inventory, HUD Sec 8, HUD FHASL (+ Terminated), HFA forecast (+ prior), REAC export, ZIP-county crosswalk; each must match a schema in the pack's `dataset-schemas.yaml` |
| `prior_run` / `prior_forecast` | none | Previous `runs/<as_of>/` and forecast export for `status_flips.csv` |
| `pii_scope` / `board_packet` | `organization` / true | `public_packet` \| `organization` \| `internal` (`--internal`); also write the stripped board workbook and `board_packet.md` |
| `include_proxies` | false | Emit the PROXY mini-perm maturity from the HFA inventory; the book supplies RECORDED maturities |
| `noah_watch` | false | Enable the NOAH module; when the profile is `city_housing` or `county` and the mandate lists an open acquisition grant, ask one question before enabling |
| `max_results`, `handoff_routes[]`, `as_of_date` | 100, all eight, today | Cards in the brief; routes that get sibling handoffs; scripts use `date.today()` unless `--as-of` is passed, never a literal |

Ask follow-up questions only for `agency_profile`, `geography`, an ambiguous `geography_mode`, and the NOAH question.
Everything else has a stated default that the output echoes.

## Step 0: Triage by Profile and Universe

Route on data first and vocabulary second; the files on hand say more than the request does.

1. A file matching `agency_servicing_extract` (`book_kind` + `program` plus an id, a date and a property key;
   `match_any` groups in `dataset-schemas.yaml`) is the primary tape. Ingest it first so inventory rows can join to it.
   Validate per `book_kind`: `loan` needs agency_loan_id + upb + maturity; `grant` needs grant_id + affordability_end or
   recapture_end; `owned_asset` needs asset_id + units_assisted + an end date; `administered_contract` needs contract_id
   + contract_expiration + units_assisted.
2. HFA inventory, HUD Sec 8, HUD FHASL, HFA forecast and REAC exports form the inventory universe; their rows are
   `universe_not_held` until the book join says otherwise.
3. Read `agency-profiles.yaml` for the profile. It sets `book_sources`, `expected_book_flag` (hfa: `OHCS Funded?` true;
   cdbg_home: programs include HOME or CDBG; others: only rows the extract names), qualified-purchaser or designee
   status, PuSH notice receipt, QC administration, PBCA status, `routes_enabled` and `self_owner_tokens`. For `pha_am`,
   an owner name matching the tokens makes the row `book_match: self_owned`, `universe: our_book`, and disables
   notice_compliance, designee_rofr, nofa_offer and ta_sponsor on that row (the levers are repositioning through
   recap_committee and servicing_watch).
4. Status In Development is EXCLUDED (`exclusion_reason: in_development`) and listed under "Pipeline, not scored" with a
   pointer to the MAP skills. Properties under 5 units stay in the board totals but receive no PuSH derivations (ORS
   456.250 scope, verify).
5. With no pack for the market, load `references/sources/_template/` and warn that every source, clock, product and
   profile is a placeholder.

The rubric is `references/scoring/affordable_public_am.json` for every row; `noah_watch.json` only when NOAH is on. The
module to read is [references/public-am-module.md](references/public-am-module.md).

## Step 1: Resolve Geography

"Portland" is three different lists. Resolve to an explicit geography object before touching data and echo it in every
output. For the Oregon/Portland pack:

| Mode | Definition | County FIPS | OHCS inventory rows |
|---|---|---|---|
| `city_limits` | City of Portland | 41051 (part) | 517 by city string (518 after the `Portalnd` typo map); polygon join pending |
| `county` | Multnomah County | 41051 | 546 |
| `metro_core` | Multnomah + Washington + Clackamas | 41051, 41067, 41005 | 810 |
| `cbsa` | Portland-Vancouver-Hillsboro MSA | adds 41009, 41071, 53011, 53059 | 810 + Columbia/Yamhill rows; Clark/Skamania only via HUD, USDA, NHPD |

Resolution order, recorded per row as `geo_grade`: county field -> HUD USPS ZIP-County crosswalk by highest RES_RATIO
with straddling ZIPs flagged -> point-in-polygon from a geocode -> city name (`city_name_weak`, never the default,
always warned). Never filter by ZIP prefix. State which sources stop at the state line: OHCS and Metro RLIS end at the
Oregon border. Board jurisdiction keys are county, then city; Portland council districts need a polygon join and are
deferred. See [references/sources/oregon-portland/geography.md](references/sources/oregon-portland/geography.md).

## Step 2: Check the Inbox and Ingest the Book First

Scripts are file-drop: nothing fetches live. Open the pack README's checklist, confirm which files are in `inbox`, and
record each file's vintage (filename date, else mtime; the manifest says which). Declared per-column date formats in
`dataset-schemas.yaml` win over row-level guessing; profile any undeclared file, including the agency's own extract,
with `python3 scripts/date_profile.py <file> [--sheet <name>] [--encoding utf-8-sig]` and paste the proposed YAML into
the pack after the user confirms. The OHCS inventory is the cautionary example: `Financial_Closing_Date` is day-first,
every other slash column is month-first, `USDA_RD_Expiration_Date` is `%Y %b %d %I:%M:%S %p`, `Rehab Year` is stored as
`2,021`. Servicing systems usually export ISO dates; confirm rather than assume.

Run order (`build_universe.py` performs all of it; each script also runs alone):

```
python3 scripts/ingest_servicing_extract.py --input book.csv --pack <pack> --agency-profile hfa --out-dir runs/<as_of>/adapter_agency_servicing
python3 scripts/ohcs_inventory_targets.py --input inventory.csv --pack <pack> --mode metro_core --horizon-years 10 --as-of <date> --out-dir runs/<as_of>/adapter_ohcs
python3 scripts/normalize_hud_sec8.py ... ; normalize_hud_insured.py ... ; normalize_ohcs_forecast.py --ohcs-leads ... ; normalize_reac_scores.py ...
python3 scripts/merge_leads.py ...        # book join (crosswalk > address > fuzzy > unmatched), universe tagging
```

The servicing extract is RECORDED by default: the agency's own ledger is the system of record for its loans. Canonical
columns (`book_kind`, ids, `program`, `units_assisted`, `upb`, `rate`, `payment_type`, `maturity`, `affordability_end`,
`contract_expiration`, recapture, covenant, senior lien, notice, HAP renewal, QC, ROFR, USDA, RAD, inspection, REAC,
`am_officer`): [references/servicing-extract.md](references/servicing-extract.md). The PII drop happens at adapter
write: phone, email, cell and personal email never reach a lead file; `am_officer_email` only under `--internal`.

Degraded-run rule: with only the HFA inventory, every date is REPORTED or DERIVED, the capital factor is 0 for every
row, and the brief says "book absent: capital factor 0 for all rows; outputs are preservation targeting and notice
compliance only". ESCALATE needs the extract joined plus forecast or log notice statuses. Name the missing files rather
than letting the queue look more certain than it is.

## Step 3: Derive Dated Events and the Agency Calendar

Every event has `event_type`, `event_family`, `direction`, `event_date`, `basis`, `source`, `confidence`, optional
`window_start`/`window_end`, `status` and `verify_flag`. Bases:

| Basis | Meaning | Multiplier |
|---|---|---|
| `RECORDED` | The agency's own ledger, HUD tape, recorder image, court docket, the agency's notice or CA log | 1.00 |
| `REPORTED` | HFA inventory, HUD contracts database, forecast list (owner- or agency-reported) | 0.90 |
| `DERIVED` | Rule applied to a reported date (Year 15 = compliance start + 15y; HOME period from completion) | 0.80 |
| `ESTIMATED` | Term window applied to a recording date (NOAH only) | 0.50 |
| `PROXY` | Stand-in with no instrument behind it (closing + 15-year mini-perm; opt-in) | 0.30 |

`Verify — Ambiguous` is a flag, not a basis; it forces 0.40 and stores both parses in `alt_dates`. Owner-cliff events
reuse every v2 affordable name (`LIHTC_COMPLIANCE_END`, `LIHTC_EXTENDED_USE_END`, `HAP_EXPIRATION`, `QC_ELIGIBILITY`,
`SOFT_PROGRAM_END`, `PRESERVATION_NOTICE_RECEIVED`, `ROFR_RECORDED`, `REAC_SCORE` ...). The book adds
`AGENCY_LOAN_MATURITY`, `SHARED_APPRECIATION_DUE`, `GRANT_RECAPTURE_END`, `AFFORDABILITY_PERIOD_END`, `COVENANT_END`,
`RECAPTURE_TRIGGER`, `COVENANT_DEFAULT`, `NONCOMPLIANCE_FINDING` and the routing markers `THIRD_PARTY_OFFER_RECEIVED`,
`QC_REQUEST_INELIGIBLE`, `USDA_PREPAY_REQUEST_RECEIVED`, `RAD_CHAP`, `SECTION_18_APPLICATION`.

**Agency calendar.** The family `AGENCY_DEADLINE` holds the dates the agency must act: `PUSH_WINDOW_PREP` (anchor - 36
mo), `PUSH_FIRST_NOTICE_DUE` (- 30), `PUSH_SECOND_NOTICE_DUE` (- 24), `TENANT_NOTICE_WINDOW` (- 36..- 30, SB 973,
operative date per pack), `RECORDS_REQUEST_DUE` (notice received + 10 d), `RECORDS_RESPONSE_DUE` (request + 30 d),
`ROFR_MATCH_DEADLINE` (certified mailing + 30 d), `QC_RESPONSE_DUE` (complete request + 1 yr, IRC 42(h)(6)(I)),
`HAP_OPTOUT_NOTICE_DEADLINE` (- 12 mo) and `HAP_OPTOUT_PACKAGE_DUE` (- 120 d) for HAP/RAC/PBV, `INSPECTION_DUE`,
`USDA_PUBLIC_BODY_OFFER_WINDOW_END` (+ 180 d). All are helper events: never in the five basis counts or
`events_in_horizon`, each carrying an agency owner and a cite from `AGENCY_DEADLINE_META` in
[references/agency-calendar.md](references/agency-calendar.md).

**Withdrawal anchor.** PuSH windows anchor on `withdrawal_anchor_date` = the latest restriction-type end only (extended
use, soft program, affordability period, covenant, USDA 515, HUD use agreement). A HAP, PRAC or PAC expiration enters
the anchor only with a non-renewal signal (opt-out notice, CA log, `hap_renewal_request_status: not_received`, a MAHRA
term actually ending); an annual HAP date is a renewal, not a withdrawal. `push_anchor_source` is recorded on the
window. PuSH derivations also need 5+ units, a PuSH-covered program and a profile that receives notices or is a
qualified purchaser.

**Stale contract dates.** A HAP/PRAC/PAC expiration already past `as_of` with no termination evidence gets status
`STALE_CONTRACT_DATE` and `Verify — Stale Contract Date`: no agency deadline derives from it, it never sits in the
OVERDUE board row or in `lost`, and the card shows `next_expected_expiration` (+ 12 mo). The HUD MF Assistance tape's
current date overrides the HFA inventory's when both exist. `NOTICE_COMPLIANCE_BREACH` is emitted here, not in scoring:
PUSH_FIRST_NOTICE_DUE passed and `notice_status: not_received_confirmed`.

Run the calendar and quote its header verbatim in the brief:

```
python3 scripts/query_calendar.py --events events.csv --within-years 10 --as-of <date> --json
# RECORDED n / REPORTED n / DERIVED n / ESTIMATED n / PROXY n / Suppressed n / Rejected n | helper deadlines n (notice arithmetic, LATEST duplicates; not counted above) | agency act-by n (next 90 days m)
```

Urgency bands are months, not `critical-dates-tracker`'s days: `OVERDUE` (< 0), `CRITICAL` 0-12, `URGENT` 12-24,
`APPROACHING` 24-36, `MONITOR` 36-60, `SCHEDULED` 60-120, `BEYOND` (> 120, never scored). Two bands sit on every lead:
`owner_cliff_band` (earliest restriction, HAP or debt end) groups the board totals; `action_band` = min(agency act-by,
owner cliff) sorts the queue, because the notice deadline, not the cliff, is what the agency can miss. Taxonomy, flags
and columns: [references/pipeline-contract.md](references/pipeline-contract.md).

## Step 4: Join Our Book and Size the Exposure

`plb/book_join.py` joins extract rows to inventory rows in a fixed order recorded as `book_join_grade`: `crosswalk`
(pack `book_crosswalk.csv`, analyst-confirmed, grows run over run) -> `address` (normalized address + zip5, upper-cased
keys) -> `fuzzy` (name token-set ratio >= 0.92, same zip5, phase tokens I/II/III/A/B/1/2 equal or absent on both sides;
REPORTED grade, written to `merge_log.csv`, never auto-promoted) -> `unmatched`. Book rows that match nothing stay
`our_book` with `in_inventory: false`, appear in `servicing_unmatched.csv`, and score on capital, servicing events and
`units_assisted`. A missing join is never a guessed balance.

`plb/units.py` fills the quantities the board reads: `restricted_units` = Total Units - Market_Rate_Units (`units_basis:
total_assumed_restricted` when market units are blank; `reported_buckets` only when AMI buckets sum to the total);
`hap_units_at_risk` only when the HUD contract is HAP or RAC, `prac_units_at_risk` for PRAC/PAC, otherwise
`other_ra_units` (never summed together); `psh_units_at_risk` as an overlay; `vulnerability_flags` (elderly, disabled,
veteran, sro, psh) and `family_3br_plus_units` for the units factor.

Dollar rules, stated on the Assumptions tab: `public_upb_total` = UPB on matched and self-owned rows;
`public_upb_at_risk` = UPB where an owner-cliff PRESSURE event is <= 36 months, `covenant_status` is watch/default, or
`coterminous_senior_cliff` (senior maturity or HAP within 24 months of our maturity); `public_grant_at_risk` =
`recapture_exposure` by method (full, prorata_reducing per 24 CFR 92.254(a)(5), forgiveness_schedule, cdbg_fmv_share,
none). `recap_math.py` keeps loan constant, amortized balance and restricted NOI and adds `recap_gap(upb,
restricted_noi, senior_dscr=1.15, senior_rate)` to size what a 0% recap or resubordination must fill, on recapping
`our_book` rows only. The QC price band is ESTIMATED and lives only inside the qc_admin memo. Authoritative sizing:
`sizing-lihtc-permanent-debt`; see [references/recap-math.md](references/recap-math.md).

## Step 5: Score and Route

`references/scoring/affordable_public_am.json` is the only rubric (a missing directory is an error, never a silent
fallback); the table is the readable summary and the tests assert they match. Run `python3 scripts/score_preservation.py
--leads leads.csv --events events.csv --pack <pack> --agency-profile hfa [--mandate mandate.json] --out
leads_scored.csv`; `--explain <property_id>` prints the arithmetic.

| Factor | Wt | Rule |
|---|---|---|
| Units and households at risk | 25 | Restricted units inside the governing owner-cliff window (<= 60 mo, else 0): 1-4 = 3, 5-19 = 8, 20-49 = 14, 50-99 = 20, 100+ = 25; +3 PSH, +2 elderly/disabled, +2 family 3BR+ share >= 25%, +3 HAP >= 50% of restricted; x governing basis |
| Restriction / HAP / QC clock | 20 | Extended use <= 36 mo 20, 36-60 12; Year 15 12-36 mo 14 for any owner; HAP <= 24 mo 18 x 0.70 unless MAHRA 0.90 (+2 annual pattern, -5 fresh 20-year); stale HAP <= 12 mo past 6; PRAC <= 24 mo 10; HUD direct / USDA <= 36 mo 16; USDA prepay request 16; affordability period or covenant end <= 36 mo 14; soft program end <= 36 mo 10; +4 PUSH_FIRST_NOTICE_DUE <= 6 mo without notice; +4 QC reply <= 12 mo; +3 opt-out package <= 6 mo; x 0.5 when `recap_status` is under_application or closed on RECORDED/REPORTED evidence |
| Declared intent vs silence | 15 | PuSH first or second notice, HAP opt-out, third-party offer, `NOTICE_COMPLIANCE_BREACH`, QC lapsed 15; QC requested (RECORDED) 13; USDA prepay request 13; first due passed with `notice_status: unknown` 6 + `Verify — Notice Log`; ROFR recorded 8 (our right); inside the open window 0 with signal `push_window_open_prep` |
| Our capital at risk | 15 | Requires `book_match` matched or self_owned: covenant default or recapture trigger 15; our maturity <= 36 mo 12, 36-60 6, 60-120 3; our affordability period end <= 36 mo 10; grant recapture end <= 36 mo 8; shared appreciation due 6; covenant watch 6; owned-asset cliff <= 36 mo 8; +3 coterminous senior cliff. `unmatched_expected` -> 0 with factor status WATCH and `Verify — Book Join` |
| Physical / REAC / occupancy | 10 | REAC <= 30 (DEC referral) or < 60 (fails; blocks MU2M) 10; 60-79 or 15-point decline 6; open noncompliance finding 8; dangerous building 10; occupancy drop, exemption lost, tax delinquent 2+ 6; code case 4; liens 3; rehab within 5 years -5 (the only place that penalty lives) |
| Sponsor capacity | 10 | Mission sponsor (nonprofit, nonprofit GP, housing authority, government) or self-owned 6 as capacity to recap; for-profit or Limited Dividend GP at Year 15 6, LP transfer or GP change 8, admin-dissolved entity 6, APPS flag 4 as preservation risk; +4 out-of-state (for-profit types only, from a servicing or SOS column), +4 sponsor with 2+ cliffs in 36 mo, +2 agent change; unknown owner type 0 + `owner_type_unknown`. Nothing subtracts |
| Stacking / geography equity | 5 | 2 programs ending in 24 mo 3, 3+ 5, HAP and extended use together 4; +2 high-displacement tract, +2 under-served district from `equity_overlays.yaml` (0 when absent) |

Shared mechanics (`references/scoring/shared_adjustments.json`): factor points x basis multiplier of the governing event
(minimum across contributing events); `SUPPRESS_UNTIL` zeroes DEBT factors only; events older than 180 days count half
except open states (`COVENANT_DEFAULT`, `NOTICE_COMPLIANCE_BREACH`, `NONCOMPLIANCE_FINDING`, QC requested, third-party
offer, USDA request); every factor stores `evidence[]`, a one-line `reading` (how the agency asset manager experiences
it) and an `intervention` (tool the agency can deploy); empty evidence scores 0. No deal-size or mission-fit multiplier
exists; `mandate_fit` (`eligible` | `ineligible` | `no_mandate_file`) blocks only the `nofa_offer` route and is recorded
with its reason.

`intervention_score` (0-100) sets the `queue_band`: `ESCALATE` >= 70, `ACT` 50-69, `PLAN` 30-49, `WATCH` < 30 with a
dated PRESSURE event inside the horizon, `EXCLUDED` otherwise (`exclusion_reason`: in_development | outside_geography |
under_5_units_no_program_event | no_dated_cliff_in_horizon). Proxy-only governing events cap at PLAN. `board_impact` =
units_at_risk x timing fraction of the owner cliff sorts within a band and feeds the board totals; units never multiply
the score.

**Routes.** Evaluate every rule; `primary_route` is the first hit in fixed precedence, the rest go to
`secondary_routes`; each route is gated by the profile's `routes_enabled`:

| # | Route | Fires on | Interventions |
|---|---|---|---|
| 1 | `optout_response` | HAP/RAC/PBV only: opt-out notice received; renewal request not received with expiration <= 120 d; expiration 0-12 mo with renewal status unknown (first action: confirm at the CA). Never PRAC/PAC | optout_tenant_notice_check, optout_response_plan |
| 2 | `notice_compliance` | `NOTICE_COMPLIANCE_BREACH` (working label: clock not started, designee available); due passed with `not_received_confirmed`; tenant notice not confirmed inside its window. Due passed with `unknown` -> primary only when a notice log is loaded this run, else secondary (confirm the log). Open window without notice -> secondary only (prep). Never from QC | push_window_prep, push_notice_demand_letter, push_records_request, tenant_notice_check |
| 3 | `qc_admin` | RECORDED QC request, `qc_waived` not true, profile administers QC; waived -> acknowledgement, no clock | qc_request_acknowledgement, qc_waiver_acknowledgement, qc_marketing_plan |
| 4 | `designee_rofr` | ROFR recorded; third-party offer mailed; PuSH notice received by a qualified purchaser or designee; USDA prepay request (public-body window); breach with a qualified purchaser (designee on silence) | rofr_notice_recording, rofr_match_offer, rofr_assignment_memo, usda_prepay_response |
| 5 | `recap_committee` | `our_book` and (score >= 50, covenant default, recapture trigger, REAC < 60, receiver / bankruptcy / judicial foreclosure, our maturity <= 24 mo, coterminous senior cliff, or self-owned with RAD/Section 18 or cliff <= 24 mo) | loan_extension_recast_memo, zero_pct_recap_term_sheet, hud_legacy_response, pha_repositioning |
| 6 | `servicing_watch` | `our_book` and a trigger <= 60 mo, covenant watch/default, REAC < 60, open finding, inspection due <= 6 mo, or senior cliff <= 60 mo. A healthy book loan is `none` (monitored) | covenant_enforcement_notice, enforcement_8823, covenant_recapture_review, prac_renewal_coordination |
| 7 | `nofa_offer` | Not held (or held and recapping) with an owner cliff <= 60 mo and `mandate_fit` eligible or no file | preservation_nofa_invitation, qc_coordination_with_hfa |
| 8 | `ta_sponsor` | Mission sponsor, not self-owned, with Year 15 / extended use / ROFR / QC signal <= 60 mo | ta_sponsor_engagement |

`none` and `excluded` are sentinels, not routes. Non-hfa profiles route a QC signal to ta_sponsor or nofa_offer with
`qc_coordination_with_hfa`, never to notice_compliance. `BANKRUPTCY_FILED` adds `counsel_only`; tenant-level data adds
`fair_housing_tenant_data`. `next_action` is the catalog's `first_action` plus the agency act-by date. Full bands and
rules: [references/public-am-module.md](references/public-am-module.md),
[references/intervention-catalog.md](references/intervention-catalog.md).

## Step 6: Resolve the Sponsor and Apply the Sunshine Policy

Owners are organizations; the agency needs the entity, its capacity and the address where a statutory notice is served,
not a person's cell number. Walk the chain and stop at the organization: the agency's own file (regulatory agreement,
HAP contract, loan documents name the notice address and the GP), HFA inventory Owner/Developer/Management names, HUD
`owner_organization_name`, the LURA/REUA in our file, the Secretary of State registry (status, managers or general
partners, registered agent as service address), Form 990 officers (internal scope only). `org_resolution_grade` A = two
independent filings agree on the entity; B = one; C = inventory name alone. `notice_address_source` records the hop that
supplied the address; the SOS registered agent is the fallback, flagged `Verify — Notice Address`. Owner Type is blank
in 443 of 810 Portland metro OHCS rows, so `infer_owner_type` works from name tokens; unknown stays unknown, scores 0 on
sponsor capacity and goes on `sos_worklist.csv`.

`pii_scope` is enforced in `plb/pii.py`, never by hand. NEVER columns are dropped at adapter write and every output
(phone, email, cell, personal email, decision-maker names, trace-vendor fields). `organization` (default) prints owner
entity, developer, manager, registered agent with business address, and `am_officer` (a public employee's assignment on
a public loan file). `internal` adds `am_officer_email` and officer names from public filings only. `public_packet` is
an allow-list for board materials: natural-person owners print as "individual owner (name withheld; see internal file)",
residential registered-agent addresses are omitted, and every redaction lands in `Redaction_Log` with its cite (ORS
192.355(2), 192.345; verify). Tenant-level HUD data (TRACS/50059) never enters any output. See
[references/sponsor-resolution.md](references/sponsor-resolution.md) and
[references/pii-and-sunshine.md](references/pii-and-sunshine.md).

## Step 7: Produce Outputs and Handoffs

Build everything with `python3 scripts/run_agency_pipeline.py --config run_config.json [--prior-run <dir>]` (stages
discover -> universe -> calendar -> score -> workbook -> handoffs -> brief -> diff; `manifest.json` records
`agency_profile`, `universe`, `mandate_file`, `pii_scope`, `book_coverage`, `records_classification`), or step by step
with `build_board_workbook.py`, `diff_forecast.py` and `make_handoffs.py`. Units-at-risk and UPB totals are computed
once (`units_at_risk.json`) and read by the workbook and the brief.

**Markdown brief.** The structure is fixed; it is the deliverable's contract.

```
# Preservation and Loan-Book Review: [agency_profile] — [market_id] — as of [as_of_date]
## Run Summary            profile; geography object; files + vintages; calendar header verbatim (three segments);
                          book_coverage and join-grade counts; book rows monitored vs on watch; degraded statement;
                          pii_scope; records_classification; "bands are months"; share of rows with blank notice log
## Board Totals           book verdict first (STABLE / WATCH / STRESSED / CRITICAL); headline "n properties / n restricted
                          units / n HAP units / n PRAC units / n PSH units / $x public UPB with an owner cliff inside 36
                          months"; table by county x owner_cliff_band; top-5 sponsors by exposure
## Agency Act-By Calendar (next 90 days)
## Intervention Queue     cards grouped by primary_route in precedence order; action_band CRITICAL/URGENT/APPROACHING
                          only, the rest summarized by band
## Book Watchlist         our_book rows, including primary_route none as "Monitoring"
## Preservation Queue (not in our book)
## Notice Compliance      Req-ID rows (PUSH-01..04, HAP-01..02) each citing window and statute
## Mandate Fit
## Status Flips Since Last Run
## Pipeline, not scored   In Development rows -> map-progress-monitor / map-troubled-project-escalator
## Data Gaps and Verification Queue   stale contract dates; notice-log unknowns; book join gaps; rejects
## Assumptions, Statutory Cites and Limits
```

Card format:

```
### [#n] [name] — [jurisdiction]   Route [notice_compliance] Queue [ACT] Score [56] Units at risk [96] Public UPB $[x]
- Units / HAP / PRAC / other RA / PSH: ... ([units_basis]); vulnerability: [elderly; psh]
- First agency act-by: [type] [date] [basis] — [n] months — owner at agency [role] — cite [..] (verify)
- Owner cliff: [type] [date] [basis] [source]; next expected expiration [date] when annual HAP
- Declared intent / notice status / renewal status: ...
- Our position: [ids] [book_kind] UPB $[x] [payment_type] maturity [date] affordability end [date] recapture exposure $[x]
  covenant [status] AM officer [name] | "not in book" | "expected in book — join missing" | "book absent"
- Physical: ...   - Sponsor capacity: ...
- Intervention: [catalog id] — owner [role] — cite [..] (confirm current text) — owner notice [y/n] / tenant notice [y/n]
  — notice address [..] ([source])
- Evidence: [event ids with date, basis, source]   - Verify before acting: [items]   - Handoffs ready: [...]
```

**Workbook tabs (17):** `Summary`, `Board_Totals` (owner_cliff_band x jurisdiction plus "stale contract date — verify",
"no dated cliff" and "beyond horizon" rows; Units_by_Year block; KPI rows; the pha_am variant swaps UPB for owned units,
PBV households and RAD/Section 18 status), `Intervention_Queue` (`AM status` dropdown: New, Assigned, Letter Sent,
Awaiting Response, Committee, Closed), `Book_Watchlist`, `Preservation_Queue`, `Sponsor_Exposure`, `Notice_Compliance`,
`Agency_Calendar`, `Mandate_Fit`, `Events`, `Regulatory`, `Owners_Sponsors`, `Book_Join_Gaps`, `Status_Flips`,
`Sources_Vintages`, `Assumptions`, `Rejects_Verify`. Queue fills: ESCALATE red tint, ACT amber, PLAN grey; basis fills
on every `*_basis` column. `--board-packet` writes a second workbook and `board_packet.md` in `public_packet` scope
(Board_Totals, Preservation_Queue, Sponsor_Exposure, Status_Flips, Redaction_Log, Assumptions).

**Status flips** (`diff_forecast.py --current --prior`): `status_flips.csv` with `flip_type` in notice_filed,
tenant_notice_confirmed, qc_requested, qc_presented, hap_renewed, hap_optout, loan_extended, loan_recast,
covenant_cured, covenant_default, recap_closed, preserved, lost, new_to_list, left_list. `lost` requires termination
evidence, never a stale date. The flips are the agency's KPI; the board reads them beside the totals.

**JSON** top level: `run`, `summary` (units_at_risk by owner-cliff band, jurisdiction and year; queue, route and
join-grade counts; sponsor_exposure; book_verdict; data_gaps), `leads[]`, `book_watchlist[]`, `preservation_queue[]`,
`notice_compliance_queue[]`, `optout_qc_responses[]`, `agency_calendar[]`, `status_flips[]`, `handoffs{}`. Schema,
columns and handoff field maps: [references/output-contract.md](references/output-contract.md).

**Handoffs** (one JSON per sibling in `runs/<as_of>/handoff/`): `critical-dates-tracker` (seed_dates with basis;
documents_to_request to the agency's own file room first); `front-door-lihtc-underwriting` (composition mode, v2
`lihtc_context` names plus `agency_soft_debt[]`) and `sizing-lihtc-permanent-debt` (before/after recast) for
recap_committee and nofa_offer; `physical-condition-assessment` when the physical factor fired; `lihtc-lpa-reviewer`
(review_focus 2C) when an LPA is on file; `sponsor-credibility-assessor` only for sponsors applying or requesting TA;
`off-market-deal-finder` for NOAH rows only, `owner_outreach: false`. Plus `documents_to_request.csv`,
`sos_worklist.csv`, `board_packet.csv`.

## Quality Checks

Before finalizing, confirm:

- Brief Board Totals == `Board_Totals` tab == `units_at_risk.json`; HAP, PRAC and other RA units are separate columns, never summed.
- Every date carries `basis` and `source`; every dollar figure is a book figure or a labeled estimate; no balance was guessed for an unmatched row.
- No phone, email, cell or trace-vendor value in any default output; `public_packet` has a `Redaction_Log`; tenant-level data absent.
- Every `notice_compliance` row and Notice_Compliance Req-ID cites the window and the statute with `verified_live: false`; no demand or records letter precedes the trigger it cites.
- No stale HAP date sits in the OVERDUE board row, derives an agency deadline, or produces `lost`.
- A/B/C tiers, seller-side language and contact detail appear nowhere; `primary_route` is one of the eight routes or `none` / `excluded` with a reason.
- Calendar header quoted verbatim with its third segment; the brief says bands are months; `as_of_date` came from `date.today()` or `--as-of`; geography object echoed and `city_name_weak` rows warned.
- Weights sum to 100; contract table matches `schema.py`; every AGENCY_DEADLINE type has a META row (`scripts/tests/`).
- Run Summary names every source still `verified_live=false` and every missing file that would lift the queue.

## Pro Tips

- **Quote the basis breakdown before the count.** "61 properties with cliffs" means little; "12 RECORDED, 38 REPORTED, 11 DERIVED | 44 helper deadlines | 19 agency act-by, 6 in 90 days" tells the board how much is real.
- **You are the qualified purchaser.** Under Oregon PuSH the agency receives the notice, requests records (OAR 813-115-0050), may appoint a designee from the earlier of the owner's notice or anchor - 30 months (ORS 456.262), perfects the ROFR in two steps (offer with notice of intent to record, then record no earlier than offer + 30 days; it expires 24 months after withdrawal) and matches a third-party offer within 30 days of the certified mailing with an affordability commitment. Run the clocks; pull the LURA/REUA and HAP contract from your own file before buying any recorder image.
- **An annual HAP date in the past is a stale record, not a lost contract.** Ask the CA for the current contract and renewal request (HUD-9624) before any card calls it a cliff.
- **Silence is a compliance case only after the due date, and only against your own log.** The 36-30 month window is internal prep (the rule reads no sooner than 30 / at least 24 months): the owner is on time; prepare (log check, notice address, draft records request) and send nothing. Unknown is not silence.
- **ORS 456.265 prohibits sanctions against a withdrawing owner.** The PuSH levers are the withdrawal bar, designee appointment, SB 973's per-tenant affordability extension and the recorded ROFR, not fines. Confirm current text before quoting any of them.
- **Year 15 is a decision point for every owner; Year 30 is the cliff.** Nonprofit and PHA GPs score the clock like anyone else and get TA to exercise the 42(i)(7) ROFR; a for-profit GP with an aggregator LP is the preservation-risk signal. PRAC is not HAP: a PRAC row never routes to opt-out response.
- **Refresh cadence:** servicing extract, HUD tapes and REAC monthly; HFA inventory and forecast quarterly with `diff_forecast.py`; SOS registry as sponsors surface; mandate file at every NOFA cohort.

## What This Skill Does NOT Do

- Build buyer target lists, score who might sell, draft letters to a seller or run outreach of any kind (`off-market-deal-finder` is the buyer-side sibling and never receives leads from here for that purpose).
- Underwrite or size a recapitalization (`front-door-lihtc-underwriting`, `sizing-lihtc-permanent-debt`); draft the loan modification; certify owner compliance (the agency verifies submissions and findings).
- Extract dates from uploaded documents (`critical-dates-tracker`); review LPAs (`lihtc-lpa-reviewer`); assess construction-phase loans (MAP skills).
- Skip-trace individuals, collect phone, email, age or voter data, output tenant-level records, fetch live data inside its scripts, or quote statute text it has not read.

## Pipeline Mode (Optional)

Standalone by default. When a `market_id` config is supplied, the user asks for a checkpoint, or an orchestrator invoked
the skill, also write `data/status/{market_id}/asset_management/preservation-loan-book.json` with `{agent:
"preservation-loan-book", phase: "asset_management", market_id, status: COMPLETE | PARTIAL | FAILED, payload:
{leads_scored_path, units_at_risk, handoffs_dir, calendar_summary}}`. `PARTIAL` means a degraded run (book absent or
inventory only) and the brief names the missing files.

## Integration

| Related Skill | Relationship |
|---|---|
| `off-market-deal-finder` | Buyer-side sibling; shares event names, basis grades, flags and `property_id`. Receives only NOAH candidates (`market_rate_mf`, `owner_outreach: false`, `purpose: public_acquisition_screen`); this skill never consumes its templates, buyer profiles or routes |
| `critical-dates-tracker` | Replaces non-RECORDED dates once the agency file or owner records arrive; shared taxonomy and flag vocabulary; its bands are days, ours months |
| `front-door-lihtc-underwriting` / `sizing-lihtc-permanent-debt` | recap_committee and nofa_offer handoff via `lihtc_context` + `agency_soft_debt[]`; capacity of restricted NOI before and after a recast |
| `lihtc-lpa-reviewer` | Year 15 / 42(i)(7) ROFR read of an LPA already in the agency file (review_focus 2C) |
| `sponsor-credibility-assessor` | Capacity read on a nonprofit or PHA applying for TA or a NOFA award; never run on an owner without participation |
| `physical-condition-assessment` | Rehab-need input for 0% rehab products when REAC/NSPIRE or code signals fire; not the program CNA |
| `map-progress-monitor` / `map-troubled-project-escalator` | Own In Development rows; a CLOSE-OUT memo moves a loan into this book |
| `drafting-lihtc-credit-memo` | Committee memo for a recap once underwriting returns |
| `multifamily-benchmarks` / `multifamily-underwriting-formulas` | Source of DSCR, opex and cap-rate bands and formula definitions; never redefined here |
| `legal-title-risk-assessment` | Confirms recorded LURA/REUA, ROFR notices and senior liens before a committee action |
| `forward-pipeline-and-news-intelligence` | Per-asset news and regulatory verdict for ESCALATE rows (`preservation_strategy`) |

## Reference Documentation

- See [references/pipeline-contract.md](references/pipeline-contract.md) for enums, lead/event tables, basis multipliers, flags, helper and AGENCY_DEADLINE rules, join rules, manifest and route precedence (read before writing adapter output).
- See [references/public-am-module.md](references/public-am-module.md) for the signal catalog, derivation rules, rubric bands with readings and interventions, sponsor-capacity table, card additions and known gaps.
- See [references/servicing-extract.md](references/servicing-extract.md) (Step 2), [references/agency-calendar.md](references/agency-calendar.md) (Step 3: withdrawal anchor, deadline derivations, stale-date rule, `AGENCY_DEADLINE_META`), [references/recap-math.md](references/recap-math.md) (Step 4).
- See [references/intervention-catalog.md](references/intervention-catalog.md) and `assets/interventions/` for the agency tools, cites, owner-vs-tenant notice and agency owner per route (Step 5).
- See [references/sponsor-resolution.md](references/sponsor-resolution.md) and [references/pii-and-sunshine.md](references/pii-and-sunshine.md) for owner_type inference, notice address order, resolution grades, PII scopes and redaction (Step 6).
- See [references/output-contract.md](references/output-contract.md) for the jsonc, workbook columns, brief and card templates, status flips and handoff field maps (Step 7); [references/noah-watch.md](references/noah-watch.md) for the optional module.
- See `references/scoring/affordable_public_am.json`, `shared_adjustments.json`, `noah_watch.json` (canonical weights); `references/sources/README.md`, `federal/` (HAP renewal and opt-out, HOME/CDBG affordability, preservation-notice and QC policy by state), `oregon-portland/` (worked example: `agency-profiles.yaml`, `mandate.json`, `book_crosswalk.csv`, `legal-timelines.md`, `dataset-schemas.yaml`) and `_template/`.
- Scripts (`scripts/README.md` gives run order and tests): `ingest_servicing_extract.py`, `build_universe.py`, `score_preservation.py`, `build_board_workbook.py`, `diff_forecast.py`, `run_agency_pipeline.py`, `make_handoffs.py`; adapters `ohcs_inventory_targets.py`, `normalize_hud_sec8.py`, `normalize_hud_insured.py`, `normalize_ohcs_forecast.py`, `normalize_reac_scores.py`; `merge_leads.py`, `query_calendar.py`, `date_profile.py`, `smoke_test_sources.py`.
- See `references/sample-output/` for a script-generated Portland tri-county run (hfa profile, synthetic book fixture joined to the real OHCS inventory) and `evals/evals.json` for the five named evals on public assets.
