# off-market-deal-finder v2 — Design Notes

How we would rebuild the single-family distress skill so that it is a first-class fit for
single-family distress, market-rate apartments and affordable/regulated apartments, with
Oregon/Portland as the worked example and a template for any US market.

Contents: 1 The answer in one paragraph · 2 Current vs v2 · 3 The six problems and their
fixes · 4 Recorded, reported, derived, estimated, proxy · 5 Free, registration and paid data ·
6 Oregon/Portland specifics · 7 Chaining to sibling skills · 8 Scoring rationale and
calibration · 9 What we could not verify · 10 Follow-ups outside this folder · 11 Tradeoffs

## 1. The answer in one paragraph

Keep one skill, but stop treating "distress" as the only reason an owner sells. The v2 spine
is a triage router (data first, keywords second) that picks one of three asset-class modules,
a shared pipeline contract (one lead table, one dated-event taxonomy, one five-level basis
vocabulary from RECORDED down to PROXY, one geography object keyed on county FIPS), a
capital-stack screen that replaces "equity % of assessed value" with a refinance-gap test
against benchmark NOI, three scoring rubrics stored as JSON with evidence attached to every
factor, an entity-resolution step that walks assessor -> deed signatory -> Secretary of State
-> HUD/HFA owner records -> Form 990 -> court dockets to name a decision maker, and a
jurisdiction pack (sources, legal clocks, lender-term assumptions, market parameters, dataset
schemas with declared date formats) that is the only place Oregon appears. "Loans coming due
within five years" becomes a native `maturity` query whose answer is honest about how many of
the dates are recorded (HUD/Ginnie/recorder/CMBS tapes), reported (agency disclosure, HFA
inventory), derived (Year 15 from compliance start), estimated (recording date plus a typical
term) or proxied (closing date plus a 15-year mini-perm), and whose scripts refuse to guess a
date format row by row.

## 2. Current vs v2

| Dimension | Current (v1, NextAutomation pack) | v2 |
|---|---|---|
| Asset scope | SFR, duplex-fourplex, condo; one pipeline | Three classes with their own modules: `sfr_small_res`, `market_rate_mf`, `affordable_regulated`; router in Step 0; re-routing on active subsidy |
| Signal model | Six SFR distress signals (lis pendens, probate, tax, absentee, code, vacant) | ~60 typed events in seven families (DEBT, REGULATORY, HARD_DISTRESS, TAX_LIEN, PHYSICAL, OWNERSHIP, OPERATING) with direction PRESSURE / SUPPRESSION / ROUTING; names shared with `critical-dates-tracker` |
| Date model | None; "auction < 30 days" | Every event dated with `basis`, `source`, `confidence`, optional window and `verify_flag`; debt and regulatory horizons are separate flags and separate columns; validation ranges; declared per-column formats |
| Equity / value formula | `Assessed value x assessment ratio`, equity % | RMV x neighborhood sales ratio for SFR; income proxy `NOI / cap` for apartments with RMV as a sanity band only; refi test `max_loan = min(DSCR, debt-yield, LTV constraints)`, `refi_gap_pct`, `dscr_refi`, `equity_cushion`; never Assessed Value in a Measure-50 state |
| Scoring weights | Stacking 25, Equity 20, Time 20, Ownership duration 15, Condition 10, Owner profile 10 | Per-class JSON rubrics (Section 8), basis multipliers, urgency bands, deal-size post-multiplier, caps (proxy-only never above C), suppressions, `evidence[]` / `reading` / `lever` on every factor |
| Owner model | Skip trace a person: phone, email, estimated age, voter registration | 13 `owner_type` values and 11 archetypes; six-hop entity resolution; `contact_grade` A/B/C by independent evidence; routes (`acquisition`, `partnership_preservation`, `lender_counterparty`, `assumption_play`); individual skip trace limited to class 1 Tier A/B via licensed vendor, no age or voter data |
| Geography | `target_market` string plus ZIP list | `geography_mode` enum (`city_limits`, `county`, `metro_core`, `cbsa`, `custom`) resolved to county FIPS with `geo_grade` per row; city-string matches flagged `city_name_weak`; no ZIP prefixes |
| Outputs | Markdown lead list with offer range as % of EMV | Fixed-structure markdown brief with basis breakdown header; 11-tab workbook; jsonc with `calendar_summary`, `rejects`, partnership and counterparty tracks; per-sibling handoff JSON; run manifest and diff vs prior run |
| Scripts | None (the Portland run improvised `b.py`) | `scripts/omdf/` library plus six file-drop adapters (OHCS inventory, OHCS forecast, HUD FHASL, HUD Sec 8, recorder index, assessor taxlots), calendar, scorer, workbook builder, handoff writer (sibling JSON + SOS worklist + documents_to_request), smoke test and orchestrator, with 56 tests and fixtures |
| Compliance | None | Gates table: DNC/TCPA with ORS 646 texts, Oregon HB 4058 wholesaler registration, ORS 646A.702 / RCW 61.34 foreclosure-rescue rules, probate cooling period, PuSH ROFR and tenant notices, bankruptcy stay, LIHTC decontrol; `buyer_profile` gating |
| Integration names | "Skill 03 / 04 / 06 / 08" from a numbered pack that does not exist here | Exact backticked folder names: `deal-finder`, `comp-analyzer`, `critical-dates-tracker`, `front-door-lihtc-underwriting`, `underwriting-market-rate-multifamily`, `residential-deal-underwriter`, `legal-title-risk-assessment`, and others |
| Frontmatter | One-sentence description, `version`, `metadata.author` | Pushy multi-line description with trigger phrases and negative routes; `name` unchanged; no `version`/`metadata`/`license` |

## 3. The six problems and the fix for each

### 3.1 No concept of loan maturity, debt stack, DSCR/refi gap or regulatory expirations

The SFR skill scored "time pressure" from an auction date. Apartments rarely go to auction;
they refinance, recapitalize or sell when a date arrives. v2 makes dated events the unit of
analysis. `references/pipeline-contract.md` defines the taxonomy: `LOAN_MATURITY`,
`IO_EXPIRATION`, `PREPAY_WINDOW_OPEN`, `RATE_CAP_EXPIRY`, `LOAN_MODIFIED`,
`SPECIAL_SERVICING`, `MATURED_BALLOON`, `LIHTC_COMPLIANCE_END`, `LIHTC_EXTENDED_USE_END`,
`QC_ELIGIBILITY`, `HAP_EXPIRATION`, `HAP_OPTOUT_NOTICE_DEADLINE`,
`PRESERVATION_NOTICE_WINDOW`, `HUD_DIRECT_LOAN_MATURITY`, `USDA_515_*`, `SOFT_PROGRAM_END`
versus `SOFT_LOAN_MATURITY`, and the suppression event `REFINANCE_CLOSED` ->
`SUPPRESS_UNTIL`. `scripts/omdf/capital_stack.py` carries the amortization, loan constant and
refi test; `references/capital-stack-math.md` documents them and the lender-term inference
table. Class 2 scores "Capital-stack timing" (25) and "Refinance gap and coverage" (20);
class 3 scores "Regulatory event timing" (25), "Declared intent and notices" (20) and
"Capital-stack pressure" (15). The SFR module keeps its equity factor because for a house the
mortgage balance against RMV is still the right question.

### 3.2 No source of actual maturity dates, only proxies

There is no single source, but there are four tapes that together cover a large share of US
apartment debt (unverified; on the order of half to two-thirds, mostly agency MBS and FHA):
HUD FHASL Active/Terminated plus Ginnie Mae loan-level files (FHA-insured), Fannie Mae DUS
Disclose and Freddie Mac MSIA (securitized agency loans; the often-quoted ~56% agency share is
a Yardi Matrix origination mix, not outstanding balance, and is marked `verify`), SEC EDGAR
ABS-EE EX-102 (registered conduit CMBS, parsed by `edgartools`), and county recorders for
everything else (trust-deed images recite maturity; Oregon line-of-credit
instruments must print it on page one under ORS 86.155). Affordable assets add HUD MF
Assistance & Section 8 (HAP dates), USDA MFH exit data (515 maturity and prepay eligibility),
NHPD and the OHCS 10-Year Forecast. The fix is architectural: adapters per tape
(`normalize_hud_insured.py`, `normalize_hud_sec8.py`, `ohcs_inventory_targets.py`,
`normalize_ohcs_forecast.py` for the OHCS 10-Year Forecast, `normalize_recorder_index.py` for
recorder-index exports and `normalize_assessor_taxlots.py` for the assessor roll, with the
GSE/CMBS/LIHTC-DB/USDA adapters specified in `references/sources/federal/README.md` for a later
build), `merge_leads.py` to union them on `property_id` preferring the higher basis, and the
degraded-run rule that says plainly: with only the OHCS CSV, every date is REPORTED, DERIVED or
PROXY and no lead reaches Tier A. The remaining gap, bank/credit-union/life-company/debt-fund
loans with no public tape (most of Portland's 5-49 unit stock), is handled by `ESTIMATED`
events from recording date plus a lender-type term window (the recorder adapter emits them,
and refuses to infer when a tape exists for the lender type) and an image purchase for
anything that reaches Tier A (Multnomah fee per county snippet, unverified; `market-params.json`).

### 3.3 Mixed day-first / month-first dates

The improvised script swapped fields only when the first field exceeded 12, so every
ambiguous value (both fields <= 12) was a guess. We profiled the file column by column:
`Financial_Closing_Date` is day-first (222 of 298 values have a first field above 12, none
have a second field above 12); `Compliance_Start_Date` and every other slash column are
month-first (0 versus 532 for compliance start, 0 versus 764 for `LATEST_Expiration_Date`);
`USDA_RD_Expiration_Date` is a third format, `%Y %b %d %I:%M:%S %p`. The fix: formats are
declared per column in `references/sources/oregon-portland/dataset-schemas.yaml`, declared
formats win (a column proven day-first is never re-tested row by row), `format: auto` is the
only path that produces `Verify — Ambiguous` with both parses stored in `alt_dates`,
undeclared files are run through `scripts/date_profile.py` and confirmed with the user, and
validations (`month_le_12`, `latest_equals_max_components` with the two known exceptions
`Casa Sonada 4` and `Riverside Terrace`, `expiration_ge_compliance_start`) write to a
Rejects tab instead of silently coercing.

### 3.4 Owners are entities; skip trace does not find the decision maker

v1 treated the owner as a person with an age. v2 classifies `owner_type` (13 values) and maps
each to an archetype with a decision maker, where to find them, a channel, an angle, a do-not
list and a template (`references/decision-maker-enrichment.md`, `assets/outreach-templates/`).
The six-hop chain in SKILL.md Step 6 ends in a `contact_grade`: A requires two independent
filings naming the same person. Oregon makes LIHTC partnerships tractable because an LP's
annual report is understood to list every general partner (ORS 70.610), while an LLC may list
one member (ORS 63.787); both sections should be verified against current text and the SOS
form, since the grade-A rule rests on them. Single-asset LLCs usually stop at grade B until a
trust-deed signatory block corroborates. `make_handoffs.py` writes the SOS worklist and the
documents-to-request list so the manual step is bounded and visible. Nonprofits, housing authorities and anything with a recorded ROFR are routed to
`partnership_preservation` with a different template, because a distress script sent to a
mission-driven ED is both ineffective and reputationally costly. Receivers, special servicers
and debtors' counsel are a separate `lender_counterparty` route with `owner_outreach=false`.

### 3.5 "Portland" city versus metro

Every primary dataset is county-scoped, so v2 resolves geography to county FIPS before touching
data. The Oregon pack defines four modes and reports what each means in the OHCS inventory:
`city_limits` 517 rows by city string (518 after the `Portalnd` typo map), `county` 546, `metro_core` 810 (Multnomah
546 + Washington 163 + Clackamas 101 after `.strip().title()` on County, which matters because
case-sensitive matching gives 325), `cbsa` adds Columbia, Yamhill, Clark WA and Skamania WA, the
last two reachable only through federal tapes and the Clark County Auditor. Each row records a
`geo_grade`; a city-string match is `city_name_weak` and triggers a warning. The skill asks for
`geography_mode` when a pack offers several and the user did not specify.

### 3.6 SFR-centric scoring weights

Equity percentage, ownership duration and owner-occupancy carry no information about whether
a syndicator's LP wants out at Year 15 or whether a 2021 bridge loan fails its extension test.
v2 ships three rubrics (`references/scoring/*.json`) and a shared adjustments file. Class 2
replaces equity with the refinance gap and treats equity cushion as a routing input (cushion
<= 0 means the lender is the counterparty); class 3 weights regulatory timing and declared
intent above capital stack because the subsidy calendar is more certain than any proxied
maturity; class 1 keeps a six-factor model close to v1 but re-bands time pressure on the
Oregon statutory clock and swaps assessed value for RMV. Deal-size fit became a post-score
multiplier so a 400-unit asset does not outrank a 40-unit one for a buyer who cannot close it.

## 4. Recorded, reported, derived, estimated, proxy

The basis vocabulary is the honesty mechanism. Multipliers: RECORDED 1.00, REPORTED 0.90,
DERIVED 0.80, ESTIMATED 0.50, PROXY 0.30; `Verify — Ambiguous` forces 0.40. A lead whose
governing events are all PROXY cannot exceed Tier C.

| Event | Typical basis today | What upgrades it |
|---|---|---|
| LOAN_MATURITY (FHA) | RECORDED (HUD FHASL, Ginnie) | Already top grade; diff against Terminated file for suppression |
| LOAN_MATURITY (agency, CMBS) | REPORTED (DUS Disclose, MSIA, EX-102) | Loan agreement via `critical-dates-tracker` |
| LOAN_MATURITY (bank/CU/life co) | ESTIMATED (recording date + term window) | Buy the trust-deed image (Multnomah fee and free Clark WA images per county snippets, unverified) and read the maturity recital |
| LOAN_MATURITY (OHCS mini-perm) | PROXY (Financial_Closing_Date + 15y, 17y for 4% bond) | Any of the above; the proxy is retired the moment a real instrument appears |
| IO_EXPIRATION, PREPAY_WINDOW_OPEN | REPORTED (tape) / DERIVED (HUD endorsement + 10y) | Loan documents |
| LIHTC_COMPLIANCE_END | DERIVED (compliance start + 15y; `+15 election possible` flag) | 8609 / LURA confirms the credit-period start |
| LIHTC_EXTENDED_USE_END | REPORTED (OHCS LIHTC_4/9 expiration) | Recorded Declaration/REUA image |
| HAP_EXPIRATION | REPORTED, confidence 0.70 under annual renewal, 0.90 after a 20-year MAHRA renewal | HAP contract and renewal history; PBCA opt-out log |
| SOFT_PROGRAM_END | REPORTED (OHCS program expiration dates) | Recorded trust deed or PHB loan record to become SOFT_LOAN_MATURITY |
| PRESERVATION_NOTICE_WINDOW | DERIVED (statute text unverified; OAR 813-115 snippets); gated on 5+ units and a PuSH-covered program; reported as a helper deadline, not in the basis counts | PRESERVATION_NOTICE_RECEIVED via records request or forecast-list status flip (RECORDED; `normalize_ohcs_forecast.py`) |
| NOD, NOTS, lis pendens, receiver, probate, SOS status | RECORDED | Already top grade |
| TAX_DELINQUENT_YEARS, CODE_CASE_OPEN, REAC_SCORE | RECORDED / REPORTED | Per-account lookup; inspection report |

The policy has a cost: honesty shrinks the list. The Portland affordable run that produced 55
tiered targets under the old script produces, under v2 with only the OHCS CSV (2026-10-04),
141 leads of which 17 are Tier C and the rest WATCH or partnership-track; nothing is above
Tier C because the debt, declared-intent and operating families are absent, not because of the
proxy-only cap (only 1 of 152 in-horizon events is PROXY; 114 are REPORTED and 37 DERIVED),
and the brief says exactly which files would add those families. That is the intended behavior.

## 5. Free, registration and paid data

| Source | Tier | Cost | Classes | Portland coverage | Verified live |
|---|---|---|---|---|---|
| HUD FHASL Active / Terminated | free-public | none | 2, 3 | all FHA-insured OR/WA loans | no |
| HUD eGIS ArcGIS layers | free-public | none | 2, 3 | geocoded join spine | no |
| Ginnie Mae mfplmon / mfpldaily | free-public | none | 2, 3 | securitized FHA loans | no |
| HUD MF Assistance & Section 8 | free-public | none | 3 | HAP/PRAC contracts, owner orgs | no |
| HUD LIHTC database | free-public | none | 3 | YR_PIS, NON_PROF; no extended-use end | no |
| HUD REAC/NSPIRE scores | free-public | none | 3 | HUD-assisted only | no |
| USDA MFH exit data | free-public | none | 3 | mostly metro fringe | no |
| OHCS Affordable Housing Inventory | free-public | none | 3 | 810 tri-county rows | file verified on disk; portal not fetched |
| OHCS 10-Year Forecast / PuSH dashboard | free-public | none | 3 | preservation status statewide | no |
| NHPD | free-registration | none | 3 | deduplicated subsidy ends, OR and WA | no |
| Fannie Mae DUS Disclose | free-registration | none | 2, 3 | agency loans | no |
| Freddie Mac MSIA | free-registration | none | 2, 3 | K/SB/ML collateral | no |
| SEC EDGAR EX-102 via edgartools | free-public | none | 2 | registered conduit CMBS only (~2% of apartment debt) | yes (edgartools guide) |
| CMBS trustee portals (CTSLink) | free-registration / NDA | none | 2 | watchlist and special-servicer files | no |
| MultcoRecords | free index; $3.75 per image (fee per county snippet; unverified) | small | all | documents since Feb 2002 (snippet; unverified) | no |
| Washington County OR Recording | free-public | unverified | all | Beaverton, Hillsboro, Tigard | no; URL and fee unconfirmed |
| Clackamas County Clerk | free-public | unverified | all | partial online coverage | no |
| Clark County WA Auditor / Digital Archives | free-public | free images | all | Vancouver, Camas | no |
| Oregon SOS Business Registry / UCC | free-public | none | all | entity resolution, mezz pledges | no |
| MultcoPropTax, PortlandMaps, RLIS, SAIL | free-public / free-registration | none | all | parcel backbone, tax status, code cases | no |
| OJD Smart Search / OJCIN | free / $170 setup + $27/mo report pack (fee snippets; unverified) | low | all | probate, FED, civil, receivership | no |
| PACER | per page | low | all | SARE Ch.11, Ch.13 | no |
| Conduits city lien search | paid | $33 per search (snippet; unverified) | 1, 2 | Portland code liens | no |
| PropStream / BatchData / REISkip / PropertyRadar | paid | ~$99/mo; per-record | 1 | SFR distress lists, USPS vacancy, skip trace | no; pricing unverified |
| Yardi Matrix | paid | quote | 2 | 50+ units only | no |
| Reonomy, CoStar, Crexi Intelligence | paid | quote; CoStar reportedly $300-500+/user/mo | 2, 3 | recorder-sourced maturities, true owner | no |
| CRED iQ, Trepp, Morningstar | paid | quote | 2 | securitized loan distress | no |

The honest coverage gap: bank, credit-union, life-company, debt-fund and unsecuritized agency
balance-sheet loans have no public tape. They are a third or more of apartment debt
nationally (unverified; the lender-mix figures in this skill are origination shares) and the
majority of Portland's 5-49 unit buildings. For them v2 produces ESTIMATED maturities from the recorder index and
lender-type term windows, and tells the user which images to buy.

## 6. Oregon/Portland specifics

- **Measure 50.** Assessed Value is the lesser of Maximum Assessed Value (1995-96 base growing
  at most 3% a year) and Real Market Value, commonly 50-55% of market. v1's `AV x ratio`
  formula is wrong here. v2 uses RMV calibrated by a neighborhood sales ratio for SFR, the
  income proxy for apartments, and AV/RMV only as a tenure signal.
- **ORS 86 and the judicial preference.** Oregon records a combined Notice of Default and
  Election to Sell (ORS 86.752); sale no sooner than 120 days after notice (86.764);
  publication four weeks ending 20+ days before sale (86.774); cure until five days before
  sale (86.778); postponements up to 180 days (86.782). Leading indicators are the
  Appointment of Successor Trustee and the OFAP Certificate of Compliance. Because ORS 86.797
  bars deficiency only for residential trust deeds, apartment lenders with guarantors
  typically foreclose judicially (ORS 88) and seek receivers (ORS ch. 37), so class 2 watches
  OJD civil filings and lis pendens, not NODs alone.
- **PuSH (ORS 456.250-.265, OAR 813-115).** Owners of publicly supported housing give a first
  notice 36-30 months and a second 30-24 months before an affordability expiration; qualified
  purchasers may record a Notice of Right of First Refusal and match a third-party offer
  within 30 days. SB 973 (2025) lengthens tenant notice to 30 months for restrictions ending
  on or after 1 July 2028. (Statutory windows from OAR 813-115 snippets; the ORS 456.260-.265
  text post-SB 973 was not readable in this build and the ROFR duration is unresolved, so
  `PRESERVATION_NOTICE_WINDOW` is DERIVED with statute text unverified; confirm before quoting
  a window to a counterparty.) v2 scores a received notice as the strongest affordable signal,
  routes ROFR-encumbered properties to the partnership track, and lets a
  `qualified_purchaser` or `nonprofit_preservation` buyer profile use designee language.
- **OHCS date formats.** Verified counts: `Financial_Closing_Date` day-first (222/0 of 298),
  all other slash columns month-first (LATEST 0/764 of 1,265; HUD_MF 0/297 of 301;
  Compliance_Start 0/532 of 890), USDA `%Y %b %d %I:%M:%S %p`, LATEST blank in 554 rows and
  equal to the maximum of its components in 1,263 of 1,265 populated rows.
- **Three (four) geography modes.** Section 3.5; `city_limits` is 517 rows by string, 518 after the `Portalnd` typo map. The `cbsa` mode is the only one that reaches
  Vancouver WA, and it does so without OHCS or Metro RLIS.
- **Clark County WA differences.** No recorded NOD; the Notice of Trustee's Sale records 90
  (120 if an RCW 61.24.031 letter applied) days before sale and cure runs to the eleventh day
  before sale; tax foreclosure follows RCW 84.64 after three years; Washington is outside the
  Oregon rent cap and Portland's relocation and FAIR ordinances; the Distressed Property
  Conveyances Act (RCW 61.34) governs pre-foreclosure purchases.
- **Regulatory motivation.** The 2026 Oregon rent cap is 9.5%; Portland relocation assistance
  runs $2,900-$4,500 per unit on any 10%+ increase. Class 2 scores a "rent trap" for
  under-rented buildings older than 15 years, higher inside city limits.

## 7. Chaining to sibling skills

Run order for a Tier A lead:

```
off-market-deal-finder  ->  deal-finder (on-market dedupe; on_market=true removes the lead)
                        ->  legal-title-risk-assessment (confirm trust deeds, balances, junior liens)
                        ->  comp-analyzer / cap-rate-comp-selector (replace value proxy)
                        ->  forward-pipeline-and-news-intelligence (asset news and regulatory verdict)
                        ->  engage owner; obtain loan docs, LURA/REUA, HAP contract
                        ->  critical-dates-tracker (non-RECORDED dates replaced by contractual ones)
                        ->  class 1: residential-deal-underwriter
                            class 2: sizing-conventional-multifamily-debt -> underwriting-market-rate-multifamily
                            class 3: sizing-lihtc-permanent-debt -> front-door-lihtc-underwriting (Composition mode)
```

| Sibling | What v2 sends | What comes back |
|---|---|---|
| `deal-finder` | leads[] with address, apn, units | active-listing flags |
| `comp-analyzer` | subject_address, property_type, unit_count, year_built, valuation_mode | comp-based value replacing `value_source: proxy` |
| `multifamily-benchmarks` | (read) | DSCR/LTV/debt-yield/cap-rate/opex bands with their date |
| `multifamily-underwriting-formulas`, `sizing-*` | NOI proxy, balance, constants | authoritative sizing; v2 never redefines the formulas |
| `underwriting-market-rate-multifamily` | pre-populated required inputs plus `needs_sponsor_data[]` | Go / Conditional / No-Go |
| `front-door-lihtc-underwriting` | `lihtc_context` block | LIHTC verdict in Composition mode |
| `residential-deal-underwriter` | address, units, value_est, liens[] | 1-4 unit underwrite |
| `critical-dates-tracker` | seed_dates[] with basis; documents_to_request[] | contractual dates; shared flag vocabulary |
| `forward-pipeline-and-news-intelligence` | asset_location, asset_class, deal_strategy | TAILWIND / HEADWIND verdict |
| `legal-title-risk-assessment` | parcel_id, recorded_instruments[] | lien and title confirmation |
| `sponsor-credibility-assessor`, `new-state-entry-diagnostic` | (buyer side, optional) | how a nonprofit or out-of-state buyer will be received |
| `market-research-assistant` | geography | metro definition and context |

## 8. Scoring rationale and calibration plan

The weights are expert heuristics, not back-tested. They encode four judgments: a dated event
with a public instrument behind it outranks any inference (basis multipliers); a certain
regulatory date outranks a proxied maturity (class 3 weights); the owner's structure decides
who can say yes and therefore which route applies before any score matters (routing before
tiering); and independent public records agreeing with each other are worth more than any
single feed (stacking factors that count only distinct families and halve stale events).

Calibration plan: keep every run's `leads_scored.csv` and `manifest.json`; after two to three
quarters, tag each Tier A/B lead with its outcome (responded, engaged, under contract, closed,
dead, never reached) and fit the weights that best separate closed from dead by editing the
JSON only, so the SKILL.md tables and the test that asserts weights sum to 100 are the only
things that change. Until then, read the `factors_json` evidence on every Tier A card rather
than the score.

## 9. What we could not verify

The research session's egress proxy returned 403 on every government, county and vendor host.
Only GitHub raw content was reachable. Consequences:

- Every source in `references/sources/oregon-portland/sources.md` is `verified_live=false`
  except the edgartools CMBS guide. URLs, field names, cadences and fees come from search
  snippets and should be smoke-tested (`scripts/smoke_test_sources.py`) from an unrestricted
  machine before the first real run. HUD ArcGIS field names should be confirmed from each
  layer's `/0?f=pjson`.
- Washington County (OR) and Clackamas County online recorded-document index URLs and image
  fees are unconfirmed (phone: 503-846-8752 and 503-655-8698).
- ORS 456.262/.263 ROFR duration appears as 24 months in one snippet and 36 months in
  another; owner-notice timing cited as 36-30 / 30-24 months comes from OAR 813-115 snippets.
  Confirm against the current statute text post-SB 973.
- Whether Oregon's 2025 QAP requires a qualified-contract waiver was not readable. OHCS REUAs
  and QAPs are widely understood to require a waiver of current allocations, so the Oregon row
  in `qc-policy-by-state.md` reads unknown / likely waiver_required; `QC_ELIGIBILITY` is scored
  only from a property's recorded REUA, never from the table.
- Oregon's Section 8 PBCA identity may change under HUD's FY2025 PBCA NOFO; confirm before
  filing opt-out log requests.
- Vendor pricing (CoStar, Yardi Matrix, Reonomy, CRED iQ, Crexi, Trepp, PropStream skip trace
  rates, BatchData) is unverified; PropStream's maturity-date filter was not confirmed.
- OJCIN base monthly fee was not visible; only the $170 setup and $27/month report package.
- The 10-year Treasury value in `market-params.json` is a placeholder flagged `verify`.
- Statute text for ORS 86, ORS 646, ORS 87, ORS 90.324, ORS 100.450 and ORS 18.964 was read
  from a GitHub mirror whose file header reads "2025 EDITION", and RCW 61.24 / 84.64 from the
  wa-law.org mirror. Confirmed there: ORS 86.705; 86.726(1)(b) (exemption for beneficiaries
  that commenced 30 or fewer residential foreclosures in the prior year); 86.752(3)-(4); 86.764
  (120 days); 86.771(5) (sum owing); 86.774 (four successive weeks, last publication more than 20
  days before sale); 86.778 (cure until five days before sale, $1,000 residential fee cap);
  86.782(2)(a) (postponements totalling not more than 180 days); 86.797(2); 86.155(1)(b)
  (line-of-credit legend with maximum principal and maturity); 646.561(4)(a)(B) (text messages,
  2025 c.580); 646.569; 646.572(1)(b); 646.642 ($25,000 per violation); 87.035 / .055 / .057;
  100.450; 18.964; 90.324 (lesser of 10% or 7% + CPI; 6% for parks with more than 30 spaces);
  RCW 61.24.031, 61.24.040(1)(a), 61.24.040(10) (120-day continuance), 61.24.090 (eleventh day),
  84.64.050. Not readable and therefore unverified: ORS 312 (tax foreclosure sections cited as
  312.010 / 312.040-.050 / 312.120), ORS 456 and OAR 813-115 (PuSH), ORS 63.787 / 70.610 (SOS
  annual-report contents), ORS 432 (death records), ORS 646A.702, 7 CFR 3560 (USDA notice
  period), the Treasury QC page, and every county, court and vendor fee figure.
- HB 4058 wholesaler registration fee ($300), cancellation period and phase-in come from a
  third-party summary; the registration requirement and penalties are confirmed in the bill
  digest.
- Portland Inclusionary Housing has no public unit registry; the IH flag depends on PHB data
  obtained by request.

## 10. Follow-ups outside this folder

- Replace `deal-finder/SKILL.md` lines 81-208 (the off-market mode, a verbatim copy of v1)
  with the exact line: `For off-market sourcing (pre-foreclosure, probate, tax delinquency, loan maturity, LIHTC/HAP expirations) use \`off-market-deal-finder\`; this skill covers on-market listing search and batch DCF only.`
- Correct `deal-finder`'s Integration names: `legal-title-review` -> `legal-title-risk-assessment`,
  `opex-analyzer` -> `operating-expense-analysis`.
- Package with `python -m scripts.package_skill /home/user/off-market-deal-finder-v2` from
  the `skill-creator` tooling; the output stays named `off-market-deal-finder` (the `-v2`
  suffix is a staging-folder name only).
- Run the description-optimization loop from `skill-creator` with near-miss negatives
  ("underwrite this LIHTC deal", "search LoopNet for Portland apartments", "extract the
  maturity date from this loan agreement", "run comps on this fourplex").
- Import the user's existing `off-market-sourcing-system.zip` contracts (vendor-agnostic data
  source map, skip-trace evidence chain, human verification checklist) into
  `references/decision-maker-enrichment.md` and `references/outreach-and-compliance.md`
  rather than re-inventing them.
- Build the GSE, CMBS, HUD LIHTC DB, REAC and USDA adapters specified in
  `references/sources/federal/README.md` once the file formats have been confirmed live; profile
  the real OHCS forecast export and replace the guessed field names in `normalize_ohcs_forecast.py`.
- Replace the `ppu_band` value proxy on affordable leads by pasting current MTSP max rents into
  `references/sources/oregon-portland/rent-limits.json` (restricted-income proxy switches on automatically).

## 11. Tradeoffs

- **One skill with modules versus three skills.** One skill keeps a single pipeline contract,
  one lead table and one scoring engine, and lets a mixed Portland inventory route row by row;
  the cost is a longer SKILL.md and a router that must be right. Progressive disclosure
  (modules loaded per class) keeps the context cost close to a single-class skill.
- **Pipeline maintenance.** Fourteen scripts and a market pack are more to maintain than a prose
  skill. The alternative was every run re-deriving `b.py`. The recorder and assessor adapters
  take canonical column names, so each new county export costs a rename step, not code.
- **Honesty shrinks the list.** A proxy-only run produces no Tier A. Users who want a longer
  list can see what to download to get one, which is better than acting on dates that do not exist.
- **Semi-manual entity resolution.** SOS lookups, Form 990s and trust-deed images are not
  automated in v2 (no live fetch). The SOS worklist CSV and image-purchase queue make the
  manual step explicit and bounded to Tier A/B.
- **File-drop over live fetch.** Deterministic, reproducible, auditable, and immune to the
  proxy problems that blocked the research; slower on the first run.
- **Oregon as example, not as logic.** Statutory clocks, lender terms and market params live
  in the pack. A new market needs a pack filled from `_template/`, which is a day of work
  rather than a rewrite, but a pack filled carelessly will produce confident wrong dates.
- **Preservation-law posture.** Treating PuSH rights as something to join rather than
  outrun forgoes some speed for a Portland acquirer; it also keeps the skill usable by
  nonprofit and qualified-purchaser users and out of avoidable disputes.
