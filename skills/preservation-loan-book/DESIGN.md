# preservation-loan-book — Design Notes

How the buyer's off-market sourcing tool (`off-market-deal-finder` v2) was recast into a public-agency
preservation and loan-book tool for HFA, city and county housing offices, PHA asset management and HOME/CDBG
participating jurisdictions, with Oregon/Portland (OHCS, Portland Housing Bureau, Home Forward, the tri-county
housing offices, the Portland Consortium PJ) as the worked example and a template for any US jurisdiction.

Contents: 1 Why the inversion · 2 Reused verbatim from v2 · 3 Design · 4 Basis table · 5 Oregon worked example
· 6 Chaining and the one-directional cross-reference · 7 Calibration · 8 What we could not verify · 9 Tradeoffs
· 10 Future work

## 1. Why the inversion

v2's affordable module (`affordable_regulated`) has the right spine for an agency: dated events with five basis
grades, declared per-column date formats, the PuSH notice arithmetic, HAP annual-renewal haircuts, Year 15 versus
Year 30, a geography object keyed on county FIPS. Its job-to-be-done is wrong for an agency. It asks who might
sell and ranks an acquisition list. An HFA asset manager, a city housing bureau or a PHA does not want a list of
sellers; it wants to know which restrictions, HAP contracts or notes in its own book create a public-interest or
book-risk event, and which tool it can deploy before the clock runs out.

The user's specification (authoritative) sets the inversion:

| Piece | As designed (acquirer) | Agency AM |
|---|---|---|
| Job | Who might sell; ranked acquisition list | Which restrictions, HAP, or our notes create a public-interest or book-risk event; ranked intervention queue |
| User | buyer_profile: principal / wholesaler / qualified_purchaser | agency_profile: hfa \| city_housing \| county \| pha_am \| cdbg_home — lender/grantor, often the ROFR/designee |
| Score | Seller motivation (for-profit GP +10, PHA -20) | Preservation urgency x units at risk x our UPB/covenants. PHA/nonprofit are high-priority partners, not low-score non-sellers |
| Route | acquisition / partnership / lender_counterparty / IOI | notice_compliance, nofa_offer, designee_rofr, servicing_watch, recap_committee, ta_sponsor, optout_response, qc_admin |
| Unit of loss | Deal we might miss | Restricted units, HAP households, and dollars of public soft debt that can walk or default |
| Class 1-2 | SFR NOD + market-rate maturity hunt | Off by default. Optional NOAH watch (unregulated 5+, rent vs FMR, long-hold) for acquisition/rehab grant targeting |
| Primary tape | OHCS/HUD/recorder inbox | Agency servicing + grant covenant extract first, then HUD/HFA inventory as the universe |
| Card "lever" | Approach angle to a seller | Tool the agency can actually deploy (notice letter, NOFA, ROFR assign, recast, 0% recap, enforcement) |

**Why `qualified_purchaser` as a skin failed.** v2 already had a `buyer_profile: qualified_purchaser` that let an
agency use designee language. It did not change what the rubric rewarded. A for-profit GP with an aggregator LP
still scored +10 as an attractive seller and routed to `acquisition`; a housing authority still scored -20 with a
tier cap at B and a template that said "do not expect a sale"; a nonprofit GP at Year 15 scored 0 as "not for
sale". For an agency those readings are backwards: the PHA and nonprofit recaps are the work, the aggregator
Year 15 and the HAP opt-out are the risk, and the agency's own UPB is the exposure. The deal-size multiplier
penalized a 400-unit property the agency can never "close" but must absolutely watch. Changing labels on a
seller-motivation score produces a confidently wrong agency list. The rubric, routes, outputs and templates had
to be rewritten; the spine could stay.

## 2. Reused verbatim from v2

Copied into `scripts/plb/` (renamed from `omdf`; nothing imports from the v2 folder at runtime): the geography
module (county FIPS maps, Portland modes, `property_id` construction, ZIP crosswalk), the date profiler, the test
runner and its date tests, the seven adapter fixtures, `geography.md` for both packs and `rent-limits.json`.
Copied with one change: `adapters.py` (helper types now come from `schema.HELPER_EVENTS` and the new
AGENCY_DEADLINE family is excluded from `events_in_horizon`) and `smoke_test_sources.py` (User-Agent string).
Copied and modified: the date engine (new bands), calendar and `query_calendar` (third header segment), schema,
scoring engine, entities, capital-stack math (now `recap_math.py`), workbook, the four affordable adapters, merge,
scorer, workbook builder, handoff writer, orchestrator, and every affordable reference file.

Kept exactly because two packs must join without translation: every v2 affordable `event_type` name, the five
basis levels and multipliers (1.00 / 0.90 / 0.80 / 0.50 / 0.30; ambiguous 0.40), the verify-flag vocabulary
(literal em-dash), `property_id` construction, `EVENT_COLUMNS`, the governing-event minimum-basis rule, the HAP
0.70 confidence rule, the helper-deadline rule (notice arithmetic never enters the five basis counts), the
declared-format rule and the `lihtc_context` field names handed to `front-door-lihtc-underwriting`.

Dropped: both buyer classes and their modules, rubrics, recorder and assessor adapters and fixtures; the refinance
gap test and lender-term inference; the ten outreach templates and the outreach/compliance reference; the lender
dictionary; the buyer sample outputs. Nothing from those files survives except the LIFT 60-year note, the HAP
mechanics paragraph that seeded the opt-out response entry, and the counsel-only and fair-housing gate definitions.

## 3. Design

### 3.1 The servicing extract is the RECORDED primary tape

The agency's own ledger is the system of record for its loans, so a servicing or grant extract enters as basis
RECORDED by default and is ingested first (`ingest_servicing_extract.py`), before the inventory, so inventory rows
can join to it. The canonical schema (`references/servicing-extract.md`) carries `book_kind` because an agency
book is not only loans: `loan`, `grant`, `owned_asset` (a PHA's own stock) and `administered_contract` (PBV or
HAP contracts a PHA or PBCA administers) have different required columns and different events. The spec's ten
columns became agency_loan_id / grant_id / asset_id / contract_id, `program`, `upb`, `rate`, `payment_type`
(hard_pay, residual_receipts, deferred, forgivable), `maturity`, `affordability_end`, `recapture_type` /
`recapture_method` / `recapture_amount` / `recapture_start` / `recapture_end`, `covenant_status`, `am_officer`,
plus notice-log, HAP-renewal, QC, ROFR, USDA, RAD, inspection and REAC columns, because those are the RECORDED
facts only the agency holds. Every servicing event stamps `detail` with the loan or grant id so two HOME loans on
one property survive merge as two events, and the OHCS PROXY mini-perm maturity is dropped when a RECORDED
agency maturity exists on the property.

No real extract existed in this build, so the pack ships the schema, a 14-row synthetic fixture keyed byte-for-
byte to real OHCS metro property names and addresses (so the join is exercised against the real inventory), a
PHA owned-asset fixture, and a bad-schema fixture. `--book` is optional; without it the run is universe-only and
says so.

### 3.2 Two universes, one merge

Every property lands in one of two universes: `our_book` (the agency holds a loan, grant, asset or contract on
it, or, for `pha_am`, owns it) or `universe_not_held`. A property in both the inventory and the book is `our_book`
with `in_inventory: true`; a book row absent from the inventory is `our_book` with `in_inventory: false` and a
line in `servicing_unmatched.csv` (the "our loan is not in OHCS" case, which the real OHCS file cannot produce
because every row in it is by definition in OHCS). `book_match` records why a row is or is not in the book:
`matched`, `self_owned`, `unmatched_expected`, `not_in_extract`, `not_in_book`, `book_absent`.

The spec's rule "missing join -> WATCH, not a guessed balance" was scoped to the factor, not the lead. Demoting
a whole lead would hide a HAP opt-out on a property the agency never financed. So `unmatched_expected` (the
profile expects the row in book, for example OHCS Funded = true under the hfa profile with `book_coverage:
full`, and the join failed) zeroes the capital factor with factor status WATCH and `Verify — Book Join`, lists
the row in `Book_Join_Gaps`, and leaves the queue band uncapped. Under `book_coverage: partial` the same row is
`not_in_extract` with no flag, because the agency said the extract is incomplete. The join order is recorded
per row (`crosswalk` > `address` > `fuzzy` > `unmatched`), fuzzy matches are REPORTED-grade and never
auto-promoted, and phase tokens are hard discriminators because "Powell Plaza I" and "Powell Plaza II" score 0.966
on a token-set ratio and are different properties with different owners.

### 3.3 The rubric inversion, and why nothing subtracts in sponsor capacity

The user's seven factors (25 / 20 / 15 / 15 / 10 / 10 / 5) keep v2's JSON shape, match DSL, basis multipliers,
decay and evidence rule, so the scoring engine and its tests port. What changed is what the points mean:

- **Units and households at risk (25)** replaces "regulatory event timing" as the biggest factor and is banded
  on absolute restricted units inside the governing owner-cliff window, because a board counts units and an
  absolute band is auditable from the source row. It scores only when the cliff is within 60 months; units beyond
  that still appear in Board_Totals and Units_by_Year. Units never multiply the score (a 300-unit property would
  swamp everything); `board_impact = units_at_risk x timing_fraction` carries the multiplicative idea as a sort key.
- **Restriction / HAP / QC clock (20)** keeps the Year 15 versus Year 30 split and the HAP 0.70 haircut, and
  scores Year 15 for any owner. The for-profit-only condition was the acquirer's view (a nonprofit GP will not
  sell); for the agency Year 15 is a decision point for every owner: LP exit, 42(i)(7) ROFR, QC request.
- **Declared intent vs silence (15)**: a received notice, a confirmed opt-out and a filed QC stay on top. Silence
  is a compliance case only after PUSH_FIRST_NOTICE_DUE, and only when the agency's own log confirms no notice;
  inside the window the owner is on time (0 points, prep signal), and an unknown log state scores 6 with a verify
  flag rather than 15. Absence in our data is not owner silence.
- **Our capital at risk (15)** exists only for matched or self-owned rows. Dollars of public soft debt, grant
  recapture exposure and shared appreciation are the agency's exposure; a coterminous senior HUD cliff adds 3.
- **Physical / REAC / occupancy (10)** keeps v2's REAC, tax, exemption and code bands with troubled-asset readings
  instead of bid discounts; REAC < 60 also matters because it blocks a Mark-Up-To-Market renewal. The recent-rehab
  penalty lives here and nowhere else.
- **Sponsor capacity (10)** adds points in both directions and never subtracts: a nonprofit, PHA or government
  sponsor scores +6 as capacity to recapitalize (TA, NOFA, ROFR exercise); an aggregator LP transfer or GP change
  scores +8 and a for-profit GP at Year 15 +6 as preservation risk. v2's -20 for housing authorities encoded "will
  not sell to me", which is not information an agency needs; for `pha_am` the housing authority is the user.
- **Stacking / geography equity (5)** keeps the two-cliffs-in-24-months rule and adds an optional overlay (high-
  displacement tract, under-served district) that scores 0 when the pack file is absent.

Removed from the engine: deal-size and mission-fit multipliers, buyer_profile gating, the designee_strategy
signal, lender_counterparty and assumption_play routing, the housing-authority tier cap, the forced nonprofit
partnership route, on_market and 1031 suppressions. The mission-fit 0.60 multiplier became a route-level hard
filter: a property eligible for no open product in `mandate.json` cannot receive `nofa_offer`, but it still scores
and still routes to notice compliance, opt-out response or servicing watch. `mandate_fit` is never an exclusion.

### 3.4 Queue bands, urgency bands, owner_cliff_band, action_band, board_impact

A/B/C tiers never appear. The 70 / 50 / 30 thresholds survive as `queue_band` ESCALATE / ACT / PLAN / WATCH /
EXCLUDED so v2's scoring tests port, but the labels say what the agency does, not how good a deal is. Urgency
bands stay in months (critical-dates-tracker's identically named bands are in days; the brief says so) and gain
OVERDUE (< 0) and BEYOND (> 120, outside the 10-year horizon, never scored). Two bands sit on every lead because
two different questions are asked of it: `owner_cliff_band` (earliest restriction, HAP or debt end) answers the
board's "how many units have a cliff in the next 12 months" and groups Board_Totals; `action_band` = min(agency
act-by, owner cliff) answers the AM's "what do I do this quarter" and sorts the Intervention Queue. The horizon
defaults to 10 years for both families because the board reads a 10-year list and OHCS publishes one.

### 3.5 The AGENCY_DEADLINE family, the withdrawal anchor, stale contract dates, the notice-deadline trap

v2 derived one PuSH window and reported it as a helper deadline so notice arithmetic would not inflate the basis
counts. The agency needs the other side of that arithmetic: the date the agency must act. A new event family
`AGENCY_DEADLINE` holds PUSH_WINDOW_PREP, PUSH_FIRST_NOTICE_DUE, PUSH_SECOND_NOTICE_DUE, TENANT_NOTICE_WINDOW,
RECORDS_REQUEST_DUE, RECORDS_RESPONSE_DUE, ROFR_MATCH_DEADLINE, QC_RESPONSE_DUE, HAP_OPTOUT_NOTICE_DEADLINE,
HAP_OPTOUT_PACKAGE_DUE, INSPECTION_DUE and USDA_PUBLIC_BODY_OFFER_WINDOW_END. All are helper events (never in the
five basis counts, never in `events_in_horizon`), each maps to an agency role and a cite through
`AGENCY_DEADLINE_META`, and the calendar header gains a third segment: `agency act-by n (next 90 days m)`.

Three rules came out of profiling the real inventory and reading the statute summaries:

- **Withdrawal anchor.** OHCS's `LATEST_Expiration_Date` is the maximum of every program date, and in 27 of the
  61 metro rows whose LATEST falls between the past and 36 months out that maximum is a HUD contract date. An
  annual HAP date is a renewal event, not a withdrawal, so anchoring the PuSH window on it would open notice
  windows on properties whose restrictions run to 2035. PuSH windows therefore anchor on
  `withdrawal_anchor_date` = the latest restriction-type end only; a HAP/PRAC/PAC date enters the anchor only
  with a non-renewal signal, and `push_anchor_source` is recorded.
- **Stale contract dates.** 33 metro rows carry a HUD_MF expiration already in the past (Park Terrace,
  2024-09-30, is typical). These are rolled annual contracts, not lost contracts. They get status
  STALE_CONTRACT_DATE, a verify flag, no agency deadlines, their own Board_Totals row, and never produce `lost`
  in the status-flip diff.
- **Records request follows notice.** The qualified purchaser's records right in OAR 813-115 follows the owner's
  notice. At window open the agency prepares (PUSH_WINDOW_PREP, internal); RECORDS_REQUEST_DUE is emitted only
  on PRESERVATION_NOTICE_RECEIVED + 10 days. No demand letter or records request is generated before the trigger
  it cites.

The notice-deadline trap from `critical-dates-tracker` applies on the agency side: the 30-day ROFR match runs
from the owner's certified mailing (`third_party_offer_mailed_date`, with a fallback flag), the QC one-year period
from the complete request, the HAP opt-out package from expiration minus 120 days. `action_band` runs off those
dates, not the owner's cliff.

### 3.6 Mandate hard filter versus multiplier

v2 multiplied an affordable lead by 0.60 on a `programs` mismatch, which quietly buried properties the buyer
could not finance. An agency's eligibility is binary and lives in its NOFA: a product is open or closed, a
program and owner type are eligible or not, a unit minimum is met or not. `mandate.json` lists open products
with those predicates (`plb/mandate.py`), `mandate_fit` is computed per row and recorded with the first failing
test, and the only effect is on the `nofa_offer` route. A property no product fits is still in the queue for the
routes that do not need money.

### 3.7 Sunshine and PII posture

v2 walked a six-hop chain to a named decision maker and allowed licensed skip tracing on class 1. An agency's
outputs are public records the moment they exist (ORS 192.311 ff.), its board packets are published, and it
serves statutory notices on organizations at a notice address, not on a person's cell phone. The default scope is
therefore `organization`: owner entity, developer, manager, registered agent with business address, and the
agency's own `am_officer`, whose assignment to a loan file is a public record and without whom the watchlist is
useless. `internal` adds `am_officer_email` and officer names from public filings only. `public_packet` is an
allow-list with redaction: natural-person owners (OHCS lists a few, such as "Bell, David" on Yards at Union
Station B) print as "individual owner (name withheld; see internal file)", residential registered-agent addresses
are omitted, and every redaction is logged with its ORS 192.355(2) / 192.345 cite for the records officer. Phone,
email, cell, personal email and any trace-vendor field are dropped at adapter write and never reach a lead file;
tenant-level HUD data (TRACS/50059) is excluded by design. `records_classification` is recorded in the manifest.

## 4. Basis table

Multipliers: RECORDED 1.00, REPORTED 0.90, DERIVED 0.80, ESTIMATED 0.50, PROXY 0.30; `Verify — Ambiguous` 0.40.
Proxy-only governing events cap the queue band at PLAN.

| Event | Typical basis today | What upgrades it |
|---|---|---|
| AGENCY_LOAN_MATURITY, AFFORDABILITY_PERIOD_END, GRANT_RECAPTURE_END, COVENANT_DEFAULT | RECORDED (the agency's own ledger) | Already top grade; the note, written agreement or grant agreement in our file confirms |
| LOAN_MATURITY (senior HUD/FHA) | RECORDED (HUD FHASL) or REPORTED (servicing `senior_maturity`) | FHASL Active; diff against Terminated for suppression |
| LOAN_MATURITY (OHCS mini-perm) | PROXY (closing + 15y); opt-in only | Retired the moment the book supplies the real maturity |
| LIHTC_COMPLIANCE_END | DERIVED (compliance start + 15y) | 8609 / LURA in our file |
| LIHTC_EXTENDED_USE_END | REPORTED (OHCS LIHTC_4/9 expiration) | Recorded Declaration / REUA image |
| HAP_EXPIRATION | REPORTED, confidence 0.70 annual, 0.90 MAHRA 20-year or administered contract | HUD MF Assistance tape (overrides OHCS); HAP contract and HUD-9624 renewal request from the CA |
| SOFT_PROGRAM_END | REPORTED (OHCS program expiration) | Our servicing extract replaces it with AFFORDABILITY_PERIOD_END or AGENCY_LOAN_MATURITY |
| PRESERVATION_NOTICE_RECEIVED | RECORDED (agency PuSH-CP log, forecast status flip, CA opt-out log) | Already top grade; date needed, else `Needs Anchor Date` |
| PRESERVATION_NOTICE_WINDOW, every AGENCY_DEADLINE | DERIVED helper (statute text unverified); never in the basis counts | A RECORDED log date anchors RECORDS_REQUEST_DUE, ROFR_MATCH_DEADLINE, QC_RESPONSE_DUE |
| NOTICE_COMPLIANCE_BREACH | DERIVED (due date passed, log says not received) | The owner's late notice or the designee appointment closes it |
| QC_ELIGIBILITY (requested) | RECORDED (agency QC intake) | Price certification; presentment of a contract |
| REAC_SCORE, NONCOMPLIANCE_FINDING, INSPECTION_DUE | RECORDED from the agency compliance file; REPORTED from a REAC export | Inspection report; 8823 filing |
| TAX_DELINQUENT_YEARS, CODE_CASE_OPEN | RECORDED / REPORTED | Per-account lookup |

Honesty still shrinks the list. With only the OHCS CSV every owner cliff is REPORTED or DERIVED, the capital
factor is 0 for every row and nothing reaches ESCALATE; the Run Summary says "book absent" and names the extract
and the notice log as the files that would change that. That is the intended behavior.

## 5. Oregon worked example

- **Agency profiles.** `hfa` = Oregon Housing and Community Services (receives PuSH notices, administers
  qualified contracts, qualified purchaser under ORS 456.250, PBCA status to verify); `city_housing` = Portland
  Housing Bureau (affected local government and qualified purchaser; preservation RFP, Section 108, TIF, PCEF);
  `county` = Multnomah / Washington / Clackamas housing offices (qualified purchasers; Metro bond allocations);
  `pha_am` = Home Forward (owned assets and PBV contracts; levers are RAD, Section 18 and recap, not notices to
  itself; `self_owner_tokens` fold its LPs into `our_book`); `cdbg_home` = the Portland Consortium PJ (HOME
  affordability periods, recapture, 24 CFR 92.504(d) inspections in place of PuSH enforcement).
- **The inventory.** 1,819 rows, 53 columns, read with `utf-8-sig`; 810 tri-county rows after `.strip().title()`
  on County (Multnomah 546, Washington 163, Clackamas 101; a case-sensitive match gives 325); `city_limits` 518
  by string. `OHCS Funded?` is true on 420 metro rows and is the hfa profile's expected-book flag. Owner Type is
  blank on 443 metro rows; 236 of those also have a blank Owner Name (HUD-contract-only rows whose owner must
  come from the HUD Sec 8 tape). Date formats as v2 found them: `Financial_Closing_Date` day-first, all other
  slash columns month-first, USDA `%Y %b %d %I:%M:%S %p`, LATEST blank in 554 rows statewide.
- **Units at risk headline (metro, Active, as of 2026-10-04, by LATEST band).** CRITICAL 10 properties / 733
  units / 20 RA units; URGENT 8 / 609 / 197; APPROACHING 14 / 1,326 / 191; MONITOR 25 / 1,579 / 330; SCHEDULED
  400 / 28,195 / 6,891 RA / 937 PSH; 29 rows already past; 278 rows with no LATEST date (HUD-contract-only and
  PHA-owned). HAP, PRAC and other RA are separated before any of this reaches a board: Rental_Assistance_Count is
  populated on 257 metro rows but only 130 carry a HUD contract (96 HAP, 32 PRAC, 2 PAC), so the remainder is
  PBV or unknown.
- **Why R25 exists.** 27 of the 61 metro LATEST dates between the past and 36 months out are HUD contract dates,
  and 33 HUD_MF expirations are already past. Anchoring PuSH on LATEST, as v2 did, opens notice windows on
  annual renewals; the withdrawal anchor and the stale-date status are the fix.
- **Named evals.** Village Garden Apartments (35 units, for-profit, OHCS Funded, restriction end 2029-06-01 at
  about 32 months): first-notice window open, PUSH_WINDOW_PREP already due, PUSH_FIRST_NOTICE_DUE 2026-12-01, no
  records request yet, declared intent 0 with a prep signal, servicing_watch primary on the book fixture. Powell
  Plaza I (47 units, Limited Dividend LP, HAP 2027-03-31 at about 6 months, LIHTC to 2035): annual HAP haircut,
  opt-out notice deadline passed unconfirmed, HAP_OPTOUT_PACKAGE_DUE 2026-12-01 as the agency act-by,
  optout_response primary, no PuSH window because the anchor is 2035; Garden Grove Apartments (HAP 2040) is
  BEYOND and EXCLUDED with no dated cliff; Silvercrest Residence (PRAC) never routes to opt-out response. Going 42
  (HOME 2058 paired with LIHTC 2058) sits in the Book_Watchlist with urgency BEYOND and route `none`; the metro
  has no HOME-only OHCS rows at all, which is why a PJ must supply its own extract (Sumner Street Flats, a
  fixture row absent from OHCS, demonstrates the unmatched path). Yards at Union Station A (158 units, Home
  Forward, LATEST 2028-01-01): under `pha_am` it is self-owned and routes recap_committee with repositioning
  levers; under `hfa` it is a matched GHAP loan maturing 2028-01-01 with sponsor capacity +6 and no cap. Hollow
  Oak Commons (fixture, maturity 2029-06-30, covenant watch, 30 assisted units) is the our-loan-not-in-OHCS case:
  `servicing_unmatched.csv`, universe our_book, roughly 26 points, WATCH, servicing_watch.
- **PuSH posture.** The agency is the qualified purchaser. Levers in the catalog: the withdrawal bar (ORS
  456.262), designee appointment including on owner silence (HB 2095), the recorded Notice of ROFR and 30-day
  match from the certified mailing (ORS 456.263, OAR 813-115-0060/-0070), the records right after notice, SB 973's
  per-tenant affordability extension and 30-36 month tenant notice, HB 3042's three-year post-withdrawal tail.
  ORS 456.265 is titled "Sanctions against withdrawing property owner prohibited" and is never described as a
  penalty; v2's legal-timelines row that called it one is corrected here.

## 6. Chaining and the one-directional cross-reference

```
ingest_servicing_extract (RECORDED book)  ->  ohcs_inventory_targets / normalize_hud_* / normalize_ohcs_forecast / normalize_reac_scores
   ->  merge_leads + book_join (two universes, one merge)  ->  units + agency_calendar  ->  score_preservation
   ->  route: optout_response -> CA letter review, MU2M / 20-year counteroffer, nonprofit transfer plan
             notice_compliance -> prep, demand letter, records request, tenant-notice check
             qc_admin -> acknowledgement, one-year marketing plan, present a contract
             designee_rofr -> record ROFR, match within 30 days, assign to a mission sponsor
             recap_committee -> sizing-lihtc-permanent-debt (before/after recast) -> front-door-lihtc-underwriting (composition) -> drafting-lihtc-credit-memo
             servicing_watch -> covenant notice, 8823, recapture review, PRAC renewal coordination
             nofa_offer -> mandate.json product -> preservation NOFA invitation
             ta_sponsor -> sponsor-credibility-assessor (applicants only) -> TA engagement
   ->  critical-dates-tracker (agency file first) replaces non-RECORDED dates  ->  diff_forecast (status flips, the KPI)
```

`off-market-deal-finder` cannot be edited from here and does not name this skill. The cross-reference is carried
one way: this pack's Integration table names it as the buyer-side sibling, hands it only NOAH candidates
(`asset_class: market_rate_mf`, `owner_outreach: false`, `purpose: public_acquisition_screen`), never consumes its
templates, buyer profiles or routes, and keeps event names, basis grades, flags, `property_id` and
`lihtc_context` identical so the two packs' outputs join without translation. Recommended future v2 patch: add
`preservation-loan-book` to v2's Integration table and route `buyer_profile: qualified_purchaser` users here.

Other siblings and what crosses the boundary: `map-progress-monitor` / `map-troubled-project-escalator` own In
Development rows and a CLOSE-OUT memo is the RECORDED event that moves a construction loan into this book;
`lihtc-lpa-reviewer` returns the 42(i)(7) ROFR read (`rofr_42i7_compliant`) on an LPA already in the agency
file; `physical-condition-assessment` returns a condition score and five-year CapEx as the rehab-need input, not
the program CNA; `portfolio-performance-analyzer` lent its maturity roll-up and concentration pattern to
Board_Totals and Sponsor_Exposure but never receives book loans (its lens is owner equity).

## 7. Calibration

The weights are expert heuristics, not back-tested. They encode four judgments: a dated event with a public
instrument or our own ledger behind it outranks any inference (basis multipliers); units and households are the
unit of loss and therefore the largest factor; statutory clocks decide which tool applies before any score
matters (routing precedence: opt-out, notice, QC and ROFR clocks first, then money, then programs); and mission
sponsors are partners whose capacity is a plus, not non-sellers to be penalized.

The KPI is status flips, not closed deals. Keep every run's `leads_scored.csv` and `manifest.json`; each quarter
`diff_forecast.py` reports notice_filed, tenant_notice_confirmed, qc_requested, qc_presented, hap_renewed,
hap_optout, loan_extended, loan_recast, covenant_cured, covenant_default, recap_closed, preserved, lost,
new_to_list and left_list. After two or three quarters, fit the factor weights that best separate preserved
from lost and the route rules that produced flips in time, by editing the JSON only, so the SKILL.md table and
the weights-sum-to-100 test are the only things that change. A `lost` flip requires termination evidence (HUD
tape status, CA log, extended use passed with QC lapsed); a stale date is never a loss. The book verdict
(STABLE / WATCH / STRESSED / CRITICAL) is a reporting convenience derived from the share of book UPB on watch or
in default and units with cliffs inside 24 months, not a scored output.

## 8. What we could not verify

Every government, legal-publisher and vendor host was egress-blocked during research; findings rest on search
snippets of official documents and every cite in this pack carries `verified_live: false`. Confirm before any
letter goes out:

- ORS 456.260 exact notice language after SB 973 (the only rule text surfaced reads "no sooner than 30 and at
  least 24 months" before withdrawal; no source supports a 36-month owner-notice start, so the 36-30 row is an
  internal prep window and NOTICE_COMPLIANCE_BREACH is a working label for "clock not started, designee available"); the enrolled SB 973 text and its operative-date nuance (staff summary says 1 January
  2026; v2 noted a 2028-07-01 phase-in for restrictions ending on or after that date, unconfirmed).
- ORS 456.265's title ("Sanctions against withdrawing property owner prohibited"); the ORS 456.262 two-step
  offer-then-record ROFR sequence (recording after 30 days from the qualified purchaser's offer) and the 24-month
  duration after withdrawal (snippets and the OHCS designee page; no source supports 36); the ORS 456.263 match
  content (affordability commitment; earnest-money and 240-day closing variations).
- The OAR 813-115 section map (0010 definitions and covered programs, 0030 notice, 0035 designee, 0050 qualified
  purchaser access to property, records and documents, 0060 ROFR recording, 0070 third-party offer); the 30-day
  records-response figure was not found in any snippet and is a working target. Whether HOME-only (PJ) and
  LIHTC-only rows are covered depends on 0010 (`push_program_coverage_verified`, `Verify — PuSH Coverage`).
- Whether a LIHTC extended-use agreement alone, with no OHCS loan or grant contract, makes a property "publicly
  supported housing" under ORS 456.250; this bounds the Oregon class-3 universe.
- The first Oregon QAP year that conditions allocations on a qualified-contract waiver (2016 is reported).
- Treas. Reg. 1.42-18 details for the QC price; the QC price band stays ESTIMATED and off every card.
- Section 8 Renewal Guide chapter and section cites for the 120-day opt-out package, Option 1B criteria and the
  nonprofit exception; Oregon's current PBCA identity under the 2024-2025 re-solicitation.
- HOME 2025 final rule dollar thresholds for 24 CFR 92.252(e) periods and the current paragraph numbering of the
  foreclosure-termination and PJ purchase provisions; HTF 93.302 and CDBG 570.505 read from snippets.
- 7 CFR 3560 subpart N figures (30-day tenant notice, 180-day offer window, 10-year restrictive-use extension);
  Section 250 notice timing (150-270 days) and Notice H 2013-25 / H 2013-17 details; PRAC five-year renewal under
  Notice H 2022-05.
- NSPIRE / DEC referral thresholds (<= 30 automatic, 31-59 elective) come from the pre-NSPIRE procedure.
- Agency soft-debt servicing conventions: no OHCS, PHB or Home Forward asset-management, recast or
  subordination policy was located, so the canonical servicing columns are a design proposal.
- ORS 192 application to owner personal contact information and tenant-level HUD data in board packets rests on
  DOJ exemption summaries; agency counsel should review the sunshine text.
- Home Forward's RAD and Section 18 status and the county acquisition program guidelines; the county and pha_am
  mandate examples are illustrative.

## 9. Tradeoffs

- **One rubric, not one per profile.** `agency_profile` changes book sources, expected-book flag, routes enabled,
  qualified-purchaser status and self-owner handling, but every profile scores on the same seven factors. A
  per-profile rubric would be tuned to data no one has yet; the profile file is where the behavioral differences
  live and can grow.
- **Factor-scoped, not lead-scoped, book join.** More columns (`book_match`, `book_coverage`, `book_join_grade`)
  in exchange for never hiding an opt-out on a property outside the book.
- **Additive score with a separate board_impact.** Keeps the engine and tests; costs the user two numbers to read
  instead of one. The alternative, multiplying units into the score, made every large property an emergency.
- **Six AGENCY_DEADLINE derivations rest on unverified statute text.** They are DERIVED helpers with verify
  notes and never enter the basis counts; the alternative was no agency calendar at all.
- **Organization-level outputs by default.** Slower for an AM who wants a phone number; correct for records that
  are public the moment they exist. `--internal` is one flag away and still excludes trace data.
- **File-drop over live fetch.** Deterministic, auditable and immune to the proxy problems that blocked
  research; the first run needs the agency to export its own book.
- **Oregon as example, not logic.** Clocks, products, profiles and formats live in the pack. A new jurisdiction
  fills `_template/` in a day; a pack filled carelessly will produce confident wrong act-by dates.
- **Honesty shrinks the queue.** An inventory-only run produces no ESCALATE. The Run Summary says which two files
  (the servicing extract, the notice log) would change that.

## 10. Future work

- Portland council districts by point-in-polygon on the OHCS geocode, so Board_Totals can report by council
  district and the equity overlay can score under-served districts.
- Grow `book_crosswalk.csv` from confirmed fuzzy matches run over run; a confirmed match should become an
  analyst-approved `crosswalk` row, not stay REPORTED.
- Ingest the HUD MF Assistance & Section 8 tape's renewal-option fields to fill `hap_renewal_option` and lift the
  0.70 haircut to 0.90 on confirmed 20-year terms without a CA log.
- Reconcile the pack's five-year statewide units-at-risk total against OHCS's published figure (about 3,641
  rent-restricted units expiring by June 2029, scope differences allowed) as a named eval once statewide runs
  are routine.
- Profile a real agency servicing export and replace the synthetic fixture; confirm ISO date formats with
  `date_profile.py` before the first production run.
- Re-fetch every statute and notice cited in `legal-timelines.md` from an unrestricted machine, flip
  `verified_live` with `smoke_test_sources.py`, and fix any window or section number the read contradicts.
- Patch v2's Integration table to name this skill and route `qualified_purchaser` users here.
