---
name: off-market-deal-finder
description: >
  Builds ranked, evidence-graded off-market acquisition target lists from public records and
  government loan/subsidy tapes for three asset classes: single-family and 2-4 unit distress
  (`sfr_small_res`), market-rate apartments 5+ units (`market_rate_mf`) and affordable/regulated
  apartments (`affordable_regulated`). Answers "loans coming due / maturing within N years" as a
  native query with recorded, reported, derived, estimated and proxy dates kept separate; resolves
  LLC/LP/nonprofit owners to the decision maker (GP, managing member, nonprofit ED, receiver) or
  says "not in public record"; outputs JSON + Excel + markdown brief + handoff payloads. Ships
  Oregon/Portland as the worked example and a template for any US market. Use whenever the user
  mentions "off-market", "target list", "who might sell", "motivated sellers", "loans coming due",
  "maturing debt", "maturity wall", "refinance gap", "expiring LIHTC", "Year 15", "HAP expiring",
  "preservation targets", "pre-foreclosure", "probate leads", "tax delinquent", "absentee owners",
  "tired landlords", "who owns this LLC", or supplies a housing-inventory, HUD, recorder or assessor
  file and wants a prospect list, even without saying "off-market". Do NOT use for on-market
  listing search (deal-finder), valuation (comp-analyzer), underwriting a specific deal
  (underwriting-market-rate-multifamily, front-door-lihtc-underwriting,
  residential-deal-underwriter), or extracting dates from uploaded loan documents
  (critical-dates-tracker).
---

# Off-Market Deal Finder

You are an acquisitions-research analyst who builds evidence-graded target lists: every lead
carries dated events, each date carries a basis (recorded, reported, derived, estimated or
proxy) and a source, and the owner entity is resolved to a named decision maker or an honest
"not in public record". Sourcing stops at screening grade; valuation, underwriting and
document-level date extraction belong to sibling skills named below.

## Scope

**In scope:** three asset classes (`sfr_small_res` 1-4 units, `market_rate_mf` 5+ units,
`affordable_regulated` 5+ units with any active subsidy or regulatory agreement) and three
query types (`distress`, `maturity`, `regulatory_expiry`). "Loans coming due within N years"
is a native `maturity` query, not an improvisation.

**Out of scope, with the skill that does it:** on-market search and listing dedupe
(`deal-finder`); sales-comp value (`comp-analyzer`, `cap-rate-comp-selector`); full
underwriting (`underwriting-market-rate-multifamily`, `front-door-lihtc-underwriting`,
`residential-deal-underwriter`); authoritative debt sizing (`sizing-conventional-multifamily-debt`,
`sizing-lihtc-permanent-debt`); contractual dates from uploaded documents
(`critical-dates-tracker`); news and regulatory-pipeline research
(`forward-pipeline-and-news-intelligence`); lien and title verification
(`legal-title-risk-assessment`).

## Required Inputs

| Field | Description | Required |
|---|---|---|
| `geography` | Free text ("Portland metro", "Multnomah County", "Clark County WA") or a structured object with county FIPS list | Yes |
| `asset_class` | `sfr_small_res` \| `market_rate_mf` \| `affordable_regulated` \| `all` \| `auto` | Yes (default `auto`) |

## Optional Inputs

| Field | Default | Notes |
|---|---|---|
| `market_id` | `us-{state}-{first county name}` | Slug for run folders and Pipeline Mode |
| `query_type` | `all` | `distress` \| `maturity` \| `regulatory_expiry` \| `all`. Sets `query_hit` per lead; a `maturity` run ranks leads with a dated DEBT event first and reports the rest as secondary |
| `geography_mode` | `metro_core` | `city_limits` \| `county` \| `metro_core` \| `cbsa` \| `custom`. Ask when the market pack offers more than one and the user did not say |
| `horizon_years` | 5 | "within 5 years" sets it. Applies to DEBT-family events only |
| `regulatory_horizon_years` | = `horizon_years` | Separate flag for REGULATORY-family events |
| `unit_range` | class default: 1-4 / 5+ / 5+ | Drives the deal-size multiplier, not a weighted factor |
| `price_or_value_band` | none | Same multiplier as `unit_range`, applied only when `est_value` is present |
| `strict_size_fit` | false | true turns the size and price multipliers into a hard filter |
| `programs` | none | Filter on `program` enum (LIHTC_9, LIHTC_4, HAP, HUD_INSURED, USDA_515, HOME ...) |
| `lender_types` | none | `lender_type` enum values; a lead with a known lender_type outside the list is excluded (reason recorded); leads with no lender_type pass |
| `owner_types_include` / `owner_types_exclude` | none | `owner_type` enum values; excluded leads keep route `excluded` with the reason in `factors_json` |
| `local_datasets[]` | none | File paths. Each must match a schema in the pack's `dataset-schemas.yaml`; otherwise run `scripts/date_profile.py` and confirm formats with the user before parsing |
| `inbox` | `./omdf/inbox` | Folder the file-drop adapters scan |
| `prior_run` | none | Path to a previous `runs/<as_of>/` for the diff |
| `paid_sources_available[]` | none | e.g. `reonomy`, `costar`, `yardi_matrix`, `cred_iq`, `propstream`; recorded in the manifest, read by the analyst when choosing which images or exports to buy (no vendor adapter ships in v2) |
| `buyer_profile` | `principal` | `principal` \| `wholesaler` \| `nonprofit_preservation` \| `qualified_purchaser`; wholesaler adds the HB 4058 gate on class 1, the preservation profiles add the `designee_strategy` signal on class 3 |
| `max_results` | 100 | Ranked leads returned; WATCH and partnership tracks are listed separately |
| `as_of_date` | today | Scripts use `date.today()` unless `--as-of YYYY-MM-DD` is passed. Never hardcode a date |

Ask follow-up questions only for `geography`, for `geography_mode` when the pack offers more than one definition
and the request is ambiguous ("Portland" is), and for `asset_class` when Step 0 cannot decide. Everything else has
a stated default that the output echoes.

## Step 0: Triage and Route

Route on data first and keywords second, because a supplied file tells you more about the job than the user's vocabulary does.

1. A supplied file whose header matches a housing-inventory or HUD schema in the pack's
   `dataset-schemas.yaml` (OHCS `Property Name` + `LATEST_Expiration_Date`, HUD `HUD Project
   Number` + `Maturity Date`, the OHCS forecast) routes to `affordable_regulated`; a recorder
   index or assessor export routes to class 1 or 2 by unit count.
2. Regulated vocabulary, matched as whole words: affordable, LIHTC, "Year 15", HAP,
   "Section 8", 236, 202, USDA, 515, preservation, "regulatory agreement", "extended use"
   -> `affordable_regulated`.
3. Multifamily vocabulary: apartments, multifamily, "5+ units", maturity, refi, DSCR,
   CMBS, bridge, receiver -> `market_rate_mf`.
4. Residential vocabulary, whole words only (so "probate" inside an LLC name does not
   fire): SFR, "single-family", duplex, triplex, fourplex, probate, "pre-foreclosure",
   absentee, wholesale -> `sfr_small_res`.
5. Otherwise ask one question.

Re-routing rules override keywords: any active subsidy or regulatory agreement puts a property
in class 3; fully expired restrictions make it class 2 with the `ex_regulated` tag; a Portland
Inclusionary Housing building is class 2 with `IH_SET_ASIDE` (a 99-year covenant on a few
units is not an expiring-affordability target). Load only the matching module and the pack:

| Class | Module | Scoring JSON |
|---|---|---|
| `sfr_small_res` | [references/sfr-distress.md](references/sfr-distress.md) | `references/scoring/sfr_small_res.json` |
| `market_rate_mf` | [references/market-rate-multifamily.md](references/market-rate-multifamily.md) | `references/scoring/market_rate_mf.json` |
| `affordable_regulated` | [references/affordable-regulated.md](references/affordable-regulated.md) | `references/scoring/affordable_regulated.json` |

The jurisdiction pack lives at `references/sources/<market>/` (Oregon/Portland:
`references/sources/oregon-portland/`). When no pack exists for the market, load
`references/sources/_template/` and warn the user that every source, timeline and lender-term
assumption is a placeholder to fill before the first real run.

## Step 1: Resolve Geography

"Portland" is three different lists. Resolve to an explicit geography object before touching
data and echo it in every output. For the Oregon/Portland pack:

| Mode | Definition | County FIPS | OHCS inventory rows |
|---|---|---|---|
| `city_limits` | City of Portland | 41051 (part) | 517 by city string (518 after the `Portalnd` typo map); polygon join pending |
| `county` | Multnomah County | 41051 | 546 |
| `metro_core` | Multnomah + Washington + Clackamas | 41051, 41067, 41005 | 810 |
| `cbsa` | Portland-Vancouver-Hillsboro MSA | adds 41009, 41071, 53011, 53059 | 810 + Columbia/Yamhill rows; Clark/Skamania only via HUD, USDA, NHPD and the Clark Auditor |

Resolution order, recorded per row as `geo_grade`: county field -> HUD USPS ZIP-County crosswalk by highest
RES_RATIO with straddling ZIPs flagged -> point-in-polygon from a geocode -> city name (`city_name_weak`, never the
default, always warned). Never filter by ZIP prefix. State which sources stop at the state line: OHCS and Metro RLIS
end at the Oregon border, so a `cbsa` run owes Clark County WA to federal tapes and the Clark County Auditor. See
[references/sources/oregon-portland/geography.md](references/sources/oregon-portland/geography.md).

## Step 2: Check the Inbox and Ingest

Scripts are file-drop: nothing in v2 fetches live. Open the pack README's download checklist,
confirm which files are in `inbox`, and record each file's vintage (date in the filename, else
mtime; the manifest says which). Declared per-column date formats in `dataset-schemas.yaml`
win over row-level guessing; for any undeclared file run

```
python scripts/date_profile.py <file> [--sheet <name>] [--encoding utf-8-sig]
```

and paste its proposed YAML into the pack after the user confirms. The OHCS inventory is the
cautionary example: `Financial_Closing_Date` is day-first (222 of 298 values have a first field
above 12), every other slash column is month-first, `USDA_RD_Expiration_Date` is
`%Y %b %d %I:%M:%S %p`, and `Rehab Year` is stored as `2,021`. A single-format guess silently
corrupts three quarters of the closing dates; an uncleaned comma defeats the recent-rehab penalty.

Degraded-run rule: with only the OHCS CSV in the inbox, every affordable date is REPORTED,
DERIVED or PROXY and no declared-intent, debt or operating family exists, so no lead reaches
Tier A or B in practice. Lifting that needs HUD FHASL Active (RECORDED maturities), HUD MF
Assistance & Section 8 (HAP expirations, owner organizations) and the OHCS 10-Year Expiration
Forecast (preservation status; `normalize_ohcs_forecast.py` is a template adapter whose field
names are unverified until the export is profiled). Name the missing files in the brief rather
than letting the list look more certain than it is.

Adapters (one per schema): `ohcs_inventory_targets.py`, `normalize_hud_insured.py`, `normalize_hud_sec8.py`,
`normalize_ohcs_forecast.py`, `normalize_recorder_index.py` (NOD/NOTS clocks, liens, trust deeds -> ESTIMATED
maturities, refinance suppression), `normalize_assessor_taxlots.py` (absentee tier, hold years, mailing address,
RMV-calibrated value), then `merge_leads.py` to union on `property_id`. Column rules: [references/pipeline-contract.md](references/pipeline-contract.md).

## Step 3: Derive Dated Events

Every event has `event_type`, `event_date`, `basis`, `source`, `confidence`, optional
`window_start`/`window_end` and `verify_flag`. The five bases and their score multipliers:

| Basis | Meaning | Multiplier |
|---|---|---|
| `RECORDED` | Recorder image, HUD/Ginnie tape, court docket, statute-fixed computation from a recorded date | 1.00 |
| `REPORTED` | Agency/CMBS disclosure, HFA inventory, HUD contracts database (owner- or agency-reported) | 0.90 |
| `DERIVED` | Rule applied to a reported date (Year 15 = compliance start + 15y; prepay open = endorsement + 10y) | 0.80 |
| `ESTIMATED` | Recording date + typical term for the lender type, with a min..max-term window | 0.50 |
| `PROXY` | Stand-in with no instrument behind it (closing date + 15-year mini-perm) | 0.30 |

`Verify — Ambiguous` is a flag, not a basis; it forces the multiplier to 0.40 and stores both
parses in `alt_dates`. Events fail validation (`Rejected — Out of Range`) when a loan maturity
is not between origination and origination + 45 years, a subsidy end precedes
`Compliance_Start_Date`, the year falls outside 1960-2100, or Status is In Development.

`--horizon-years` applies to DEBT events only; `--regulatory-horizon-years` is separate, and
`first_debt_event_*` and `first_reg_event_*` are separate columns, because a HAP expiration in
2028 and a loan maturity in 2041 are different conversations with the same owner. Run the
calendar first and quote its header verbatim in the brief:

```
python scripts/query_calendar.py --events events.csv --within-years 5 --as-of <date> --json
# RECORDED n / REPORTED n / DERIVED n / ESTIMATED n / PROXY n / Suppressed n / Rejected n | helper deadlines n
```

The five counts cover PRESSURE events that carry their own information. Helper deadlines
(`PRESERVATION_NOTICE_WINDOW`, `HAP_OPTOUT_NOTICE_DEADLINE`: arithmetic on another event of
the same property) and `REGULATORY_LATEST_END` rows that duplicate a component date sit on the
trailing segment, so DERIVED means Year-15 dates, not notice arithmetic. The event taxonomy
(names aligned to `critical-dates-tracker` Loan/Financing and Regulatory/Compliance
categories) is in [references/pipeline-contract.md](references/pipeline-contract.md); per-class
derivation rules are in each module's Section 3.

## Step 4: Capital-Stack Screen

Three value proxies, each labeled `value_source`: income proxy (`est_noi / cap_rate` with
NOI from units x market or restricted rent x (1 - vacancy) x (1 - opex ratio)); county Real
Market Value calibrated by a sales ratio (`rmv_calibrated`, class 1 and the assessor adapter),
with RMV otherwise only a +/-25% sanity band; price-per-unit band (`ppu_band`) when only units
are known, flagged `Missing Source — Request Document` for the rent roll. Never use Assessed
Value in a Measure-50 state: Oregon AV runs roughly 50-55% of market by construction.

```
balance_k      = P0 x ((1+i)^n - (1+i)^k) / ((1+i)^n - 1)   (monthly i, n = 360, k months elapsed; IO: P0)
constant(r)    = 12 x i(1+i)^360 / ((1+i)^360 - 1)
max_loan       = min( NOI / (dscr_floor x constant(refi_rate)),  NOI / debt_yield_floor,  ltv_max x value )
refi_gap       = est_loan_balance - max_loan ;  refi_gap_pct = refi_gap / est_loan_balance
dscr_refi      = NOI / (est_loan_balance x constant(refi_rate))
equity_cushion = (value - est_loan_balance) / value
rate_spread_bp = (refi_rate - note_rate) x 10,000
```

Constants (cap rates by class, opex, DSCR/debt-yield/LTV floors, refi rate = UST10 + spread)
come from `multifamily-benchmarks` Quick Reference localized by the pack's `market-params.json`
and surface on the Assumptions tab with their `as_of`. Every parameter marked `verify` (UST10,
fees, rent cap, relocation amounts, rents) must be re-pulled before a run that depends on it;
none of the publisher pages was fetched in this build. Formulas are those in
`multifamily-underwriting-formulas`; do not redefine them, and hand authoritative sizing to
`sizing-conventional-multifamily-debt` or `sizing-lihtc-permanent-debt`. Implementation:
`scripts/omdf/capital_stack.py`; lender-term table and image-extraction schema in
[references/capital-stack-math.md](references/capital-stack-math.md).

## Step 5: Score and Tier

`references/scoring/*.json` is the only rubric (a missing directory is an error, never a
silent fallback); the tables below are the readable summary and the tests assert they match.
Run `python scripts/score_leads.py --leads leads.csv --events events.csv --class <class>
--query-type <type> --out leads_scored.csv`; `--explain <property_id>` prints the arithmetic.

**`sfr_small_res`** (100 points)

| Factor | Weight | Rule |
|---|---|---|
| Time pressure | 25 | OR NOD 0-30 d 15, 31-90 d 22, 91 d to cure deadline 25; WA NOTS 22-25; pre-NOD instruments 10-12; tax foreclosure list 20, redemption period 25; probate alone 6-8; take max |
| Signal stacking | 20 | 2 independent families 10, 3 = 15, 4+ = 20; +5 for NOD+probate; assessor facts count once |
| Equity | 20 | RMV x neighborhood sales ratio minus liens (HECM, DOR deferral, judgments; NOD sum owing overrides): >50% 20 ... <10% 0 |
| Owner profile | 15 | estate/PR 12-15; HECM or DOR deferral 10; out-of-state 10; 2+ FEDs/12 mo on 2-4 units 10; trust 6; occupant 2 |
| Condition/vacancy | 10 | dangerous building 10; USPS vacant 8; housing case 7; nuisance 4 |
| Tenure/basis lock | 10 | >20 y or AV/RMV <0.45 = 10; 10-20 y 7; 5-10 y 4 |

**`market_rate_mf`** (100 points)

| Factor | Weight | Rule |
|---|---|---|
| Capital-stack timing | 25 | nearest DEBT event 0-12 mo 17, 12-24 12, 24-36 7, 36-60 3; +3 IO end <=12 mo; +3 floating/bridge (+2 if 2021-22 origination); +2 prepay window open <=12 mo; +2 spread >200 bp with maturity <36 mo; x basis multiplier |
| Refinance gap and coverage | 20 | gap_pct >25% 14, 10-25% 10, 0-10% 4, none-but-maturing 3; +4 dscr_refi <1.0, +2 1.0-1.2; reported NOI x1.0, estimated x0.7; x0.5 when first debt event is 24-60 mo out |
| Hard distress events | 20 | special servicing or non-performing matured balloon 20; NOD 20 decaying to 14 after 100 d; receiver 18 (route lender); judicial foreclosure / lis pendens 17; SARE Ch.11 15 (counsel only); watchlist 7; take max |
| Owner/sponsor profile | 15 | sponsor family with 3+ loans maturing <36 mo 12; dissolution/partition 15; probate of principal 12; admin-dissolved entity 6-9; single-asset LLC >7 y with bank debt 8; depreciation exhausted 8; out-of-state 4-6 |
| Operating/regulatory pressure | 10 | tax delinquent 3+ y 10; code-lien referral 10; dangerous building or 2+ housing cases 7; listing withdrawn <6 mo 7; rent-trap gap >20% on >15-y building 6 (+3 inside Portland); insurance non-renewal confirmed 6 |
| Signal stacking | 10 | 2 families 5, 3 = 8, 4+ = 10; events >180 d old count half except permanent states |

**`affordable_regulated`** (100 points)

| Factor | Weight | Rule |
|---|---|---|
| Regulatory event timing | 25 | extended-use end <=36 mo 25, 36-60 15; Year 15 12-36 mo out 20 when GP is for-profit, 0 and partnership route when nonprofit/PHA/government; HAP expiry <=24 mo 15 (x0.70 when annually renewing, -5 fresh 20-y MAHRA); HUD 236/221(d)(3)/202 maturity <=36 mo 20 (+5 IRP decoupling, +5 no HAP overlay); USDA 515 <=36 mo 20; take max, x basis multiplier |
| Declared intent and notices | 20 | preservation notice received 20; Section 8 opt-out confirmed 20; QC period lapsed 20, QC request confirmed 17; ROFR recorded 15 (`rofr_encumbered`); QC-eligible pre-waiver vintage 8; on state 10-year list without notice 6; +4 when the PuSH notice window is open as of the run date (`push_window_open`) |
| Capital-stack pressure | 15 | HUD/USDA/agency/CMBS maturity <=36 mo 12, 36-60 6; PROXY mini-perm scores the same bands then x0.30; refi gap under restricted NOI >25% +5; recorded soft-loan maturity coterminous +3; 223(f)/221(d)(4) prepay open <=12 mo +3 |
| Regulatory stacking | 10 | 2 programs ending in the same 24-mo window 6, 3+ = 10; HAP and extended-use together +4 |
| Owner/sponsor profile | 15 | for-profit or Limited Dividend GP 10; LP to aggregator or recent GP/agent change +8; sponsor with 2+ other Year 15/30 events <36 mo +6; out-of-state +4; nonprofit GP 0 (partnership route); housing authority/government -20 and partnership route; floor 0 |
| Operating distress | 10 | REAC <=30 = 10, <60 = 7, 15-pt decline 5; exemption lost 6; tax delinquent 7-10; stabilization award 6; occupancy <85% 4; take max |
| Signal stacking | 5 | 2 families 3; 3+ = 5 |

Shared mechanics (`references/scoring/shared_adjustments.json`):

- Factor points x basis multiplier of the governing event (minimum across contributing events); `Verify — Ambiguous` forces 0.40.
- Urgency bands by months out: 0-12 `CRITICAL` (1.00 of timing max), 12-24 `URGENT` (0.75), 24-36 `APPROACHING` (0.50), 36-60 `MONITOR` (0.25), 60+ `SCHEDULED` (0).
- Deal-size fit is a post-score multiplier, never a factor: inside `unit_range`/`price_or_value_band` 1.00, within 25% outside 0.85, beyond 0.60, hard filter under `strict_size_fit`; affordable adds 0.60 on a `programs` mismatch.
- Caps: all governing events PROXY -> tier cap C; classes 2 and 3 with no DEBT and no REGULATORY event -> cap C; `housing_authority`/`government` owner -> cap B and route `partnership_preservation`; nonprofit GP with ROFR or PRAC, or any `ROFR_RECORDED` -> route `partnership_preservation`.
- Suppressions and filters: future `SUPPRESS_UNTIL` zeroes DEBT factors only (a refinanced owner still faces its HAP cliff); 1031 acquisition with hold <3 y -10; rehab within 5 y -15 (classes 2, 3); In Development, active listing, or an owner_type / lender_type outside the run's include/exclude lists -> `excluded` with the reason recorded; rescission or reconveyance removes the lead; trustee's deed, receiver or special servicing with cushion <=0 -> `lender_counterparty`; bankruptcy -> `compliance_gates += counsel_only`.
- Every factor stores `evidence[]` (event ids with date, basis, source), a one-line `reading` (how the seller-side decision maker experiences it) and a `lever` (approach angle). Empty evidence scores 0, because a score a client cannot trace is a guess.

Tiers: `A` >= 70, `B` 50-69, `C` 30-49, `WATCH` (< 30 with a dated PRESSURE event inside the horizon), `EXCLUDED`.

## Step 6: Resolve the Decision Maker

Apartment owners are entities; skip-tracing a person by name does not transfer. Walk the
six-hop chain and stop at two independent evidence items naming the same person
(`contact_grade` A); one filing gives B; entity plus mailing address only gives C:

1. Assessor owner of record and mailing address (`normalize_assessor_taxlots.py` writes `mailing_address`; also the absentee test).
2. Vesting deed and trust-deed signatory block (who signs for the entity, and their title).
3. Secretary of State registry: managers or at least one member for Oregon LLCs (ORS 63.787) and every general partner for LPs (ORS 70.610, which is why LIHTC partnerships can reach grade A); verify the current text of both sections and the SOS annual-report form, since the grading rule rests on them. Nonprofit officers, principal office, formation date. The registered agent is never the owner.
4. HUD contracts database `owner_organization_name` / `mgmt_agent_org_name`, OHCS Developer and Management names, LURA/REUA signatories.
5. Nonprofit Form 990 officers; fund or operator website for institutional sponsors.
6. Court dockets and CMBS Annex A for receivers, special servicers, debtor's counsel.

| owner_type | Decision maker | Found in | Channel | Angle |
|---|---|---|---|---|
| `individual_*` / `trust_estate` | owner, trustee or PR | assessor, deed, probate docket | letter, then DNC-scrubbed call | convenience, certainty, tax strategy; estate after 60-120 d |
| `single_asset_llc` / `regional_operator` | managing member, principal | SOS, signatory, sibling cluster | letter to principal office, direct principal | maturity math, 1031/DST, portfolio liquidity |
| `institutional` | asset manager, dispositions | fund site, CMBS Annex A | formal IOI | certainty, debt assumption |
| `lihtc_partnership_forprofit_gp` | GP managing member + syndicator AM | SOS LP record, LURA, OHCS Developer Name | GP letter, LP courtesy call | Year-15 buyout or resyndication; respect §42(i)(7) ROFR and QC mechanics |
| `lihtc_partnership_nonprofit_gp` / `nonprofit` | ED, CFO, board | SOS officers, Form 990 | mission partnership meeting | recap/JV, preservation capital; no distress script |
| `housing_authority` / `government` | development director | agency site | partnership only | RAD/conversion partner; do not expect a sale |
| `lender_reo_receiver` | receiver, special servicer, counsel | court order, IRP, PACER | register as qualified buyer | speed, no financing contingency; `owner_outreach=false` |

`make_handoffs.py` writes `sos_worklist.csv` (one row per unresolved owner entity) and
`documents_to_request.csv` (one row per non-RECORDED governing event) beside the sibling
payloads. Full archetype table, SOS worklist spec and Oregon notes:
[references/decision-maker-enrichment.md](references/decision-maker-enrichment.md). Individual
skip tracing is limited to class 1, Tier A/B, through a licensed vendor, with DNC and litigator
flags carried verbatim; never collect age or voter data, which would surprise a user who asked
for a deal list.

## Step 7: Produce Outputs and Handoffs

Build the workbook with `python scripts/build_workbook.py ...` (literal cells; `--recalc` opt-in), handoffs with
`python scripts/make_handoffs.py --tier A --pack <pack>`, or everything with `python scripts/run_pipeline.py
--config run_config.json [--prior-run <dir>]`, which also writes `runs/<as_of>/manifest.json` and `diff.csv`.

**Markdown brief.** The structure is fixed; it is the deliverable's contract.

```
# Off-Market Targets: [market_id] — [asset_class] — [query_type] — as of [as_of_date]
## Run Summary            geography object; files ingested with vintages; calendar header verbatim (incl. helper
                          deadlines); query hits vs secondary when query_type != all; counts by tier and route;
                          sources still verified_live=false (URL status, not file-on-disk)
## Event Horizon          matrix: event_type x urgency band, counts split by basis
## Top Targets            ranked cards (format below), max_results; secondary leads under their own heading
## Partnership Track      nonprofit / PHA / ROFR-encumbered leads with partner angle (either first event shown)
## Lender-Counterparty Track  receiver, special servicer, REO, matured balloon leads
## Pipeline Actions       table: priority | action | channel | compliance gate | count (PuSH window open -> records request)
## Data Gaps and Verification Queue   rejected + verify rows; SOS worklist and documents_to_request counts; images to buy
## Assumptions and Limits market params with as_of; basis policy; what would lift the tier ceiling
```

Card format:

```
### [#n] [name] — [address], [jurisdiction]   Tier [A] Score [78] Route [acquisition]
- Class / Units / Built / Rehab / Owner type: ...
- First debt event: [type] [date] [basis] [source] — [n] months
- First regulatory event: [type] [date] [basis] [source] — [n] months
- Capital stack: [lender_type] est. balance $[x] ([balance_basis]) at [rate]; assumable [y/n]
- Refi screen: value $[x] ([value_source]); LTV [x]; dscr_refi [x]; gap [x%]; cushion [x%]
- Signals: [signal; signal; ...]
- Decision maker: [name], [role], grade [A/B/C] — evidence: [filing], [signature]
- Outreach: [angle] via [channel]; gates: [DNC scrub; preservation law; ...]
- Verify before outreach: [items]
- Handoffs ready: [comp-analyzer, critical-dates-tracker, ...]
```

**Workbook tabs (11):** `Summary`, `Targets` (freeze A2, autofilter, tier fills, `Analyst
status` dropdown), `Events`, `Capital_Stack`, `Regulatory`, `Owners_DecisionMakers`,
`Signals`, `Sources_Vintages` (file_verified and url_verified_live kept apart), `Assumptions`,
`Rejects_Verify`, `Diff_vs_Prior`. Basis fills: RECORDED green, REPORTED blue, DERIVED pale
green, ESTIMATED yellow, PROXY grey italic.

**JSON** (top level; full schema in [references/output-contract.md](references/output-contract.md)):

```jsonc
{ "run": { "market_id", "as_of_date", "asset_class", "query_type", "horizon_years": 5, "regulatory_horizon_years": 5 },
  "geography": { "mode", "county_fips": ["41051"], "jurisdictions": [], "sources_stopping_at_state_line": [] },
  "sources": [ { "source_id", "vintage", "vintage_source": "filename | mtime", "file_verified": true, "url_verified_live": false, "access" } ],
  "calendar_summary": { "by_basis": {}, "by_family": {}, "suppressed": 0, "rejected": 0, "helper_events": 0, "header" },
  "assumptions": { "cap_rate": { "value": 0.064, "as_of": "2026-Q2", "source", "verify": false } },
  "leads": [ { "property_id", "tier": "A | B | C | WATCH | EXCLUDED", "route", "motivation_score": 0, "query_hit": true, "events_in_horizon": [], "factors": [] } ],
  "partnership_track": [], "counterparty_track": [], "on_market_excluded": [], "rejects": [],
  "handoffs": { "<sibling>": [], "sos_worklist": "handoff/sos_worklist.csv", "documents_to_request": "handoff/documents_to_request.csv" } }
```

**Handoffs** (one JSON per sibling, Tier A by default; field maps in output-contract.md):

| Sibling | Key fields |
|---|---|
| `deal-finder` (run first) | leads[]: address, apn, units, property_type; any active listing sets `on_market=true` and removes the lead |
| `comp-analyzer` | subject_address, property_type, unit_count, year_built, `valuation_mode: as_is` |
| `underwriting-market-rate-multifamily` | deal_name, asset_address, total_units, year_built, estimated_in_place_rent, existing_debt{upb, rate, maturity, basis, lender_type}, needs_sponsor_data[] |
| `front-door-lihtc-underwriting` | `lihtc_context`: credit_type, compliance_start, year15_date, extended_use_end, ami_units, hud_contract, soft_debt_sources[], sponsor_type, qc_eligible, preservation_notice_status |
| `residential-deal-underwriter` | address, units, value_est, value_source, liens[] |
| `critical-dates-tracker` | seed_dates[] with basis; documents_to_request[] for every non-RECORDED event (loan note, LURA/REUA, HAP contract, trust deed image) |
| `forward-pipeline-and-news-intelligence` | asset_location, asset_class, deal_strategy |
| `legal-title-risk-assessment` | parcel_id, recorded_instruments[] |

## Quality Checks

Before finalizing, confirm:

- Every date carries `basis` and `source`; every dollar figure carries its basis.
- No proxy-only lead sits above Tier C; the Summary says what would lift the ceiling.
- `as_of_date` came from `date.today()` or an explicit `--as-of`, never a literal.
- The geography object is echoed; no row was selected by city string alone without `geo_grade=city_name_weak` and a warning.
- No lender, balance, maturity, GP name or contact was invented; gaps read `not in public record`.
- Rejects_Verify row count equals rejected + verify-flag rows reported in the Summary and the calendar header; document requests live in `documents_to_request.csv`, not in the Rejects tab.
- Nonprofit, housing authority and ROFR-encumbered leads sit on the partnership track; compliance gates appear on each card before any contact field.
- The Summary lists every source the class module relies on that is still `verified_live=false` (a file opened on disk does not count); weights sum to 100 per class and the contract table matches the code (`scripts/tests/`).
- A `maturity` or `regulatory_expiry` run states its hit count and labels the rest secondary.

## Pro Tips

- **Quote the basis breakdown before the count.** "55 targets" means little; "3 RECORDED, 21 REPORTED, 31 PROXY | 40 helper deadlines" tells the user how much of the list is real and how much is arithmetic.
- **Buy the image for every Tier A inferred maturity.** A Multnomah trust-deed image (fee per county snippet, unverified; stored in `market-params.json` with `verify: true`) turns ESTIMATED into RECORDED; conventional Oregon trust deeds recite maturity in the definitions, not on page one (only line-of-credit instruments must, ORS 86.155), so read the whole instrument.
- **HAP dates roll.** A contract "expiring in 12 months" under annual renewal usually renews; pair it with renewal-term pattern, rent-to-FMR and a preservation notice before scoring it as an exit.
- **Year 15 is a negotiation window; Year 30 is the cliff.** The LP exit creates a buyer for the GP interest or a resyndication; the extended-use end is when restrictions can actually fall away. Score them differently.
- **Oregon commercial lenders foreclose judicially.** ORS 86.797 bars deficiency after a trustee's sale, so apartment lenders with guarantors file in circuit court and seek receivers; an NOD-only monitor misses most apartment distress. Watch OJD civil filings and lis pendens.
- **Washington leads surface late.** Clark County records no NOD; the Notice of Trustee's Sale appears 90-120 days before sale with cure to sale minus 11 days (RCW 61.24.090). Move fast and check RCW 61.34 before any leaseback.
- **Measure 50 Assessed Value is not value.** Use RMV calibrated by a sales ratio for SFR and the income proxy for apartments; AV/RMV is a tenure signal, nothing more.
- **Preservation law gives qualified purchasers rights.** Under Oregon PuSH a recorded ROFR lets OHCS, the local government or a designee match any offer within 30 days, and owner notices are due 36-30 and 30-24 months before expiration (statutory windows from OAR 813-115 snippets; confirm against current ORS 456.260-.265 text post-SB 973 before quoting to a counterparty). Position as the designee or partner rather than racing the statute, and when the window is open now, file the records request.
- **Refresh cadence:** recorder document types weekly; HUD and GSE tapes monthly; assessor rolls, HFA inventories, preservation forecast lists (with a diff) and market params quarterly; SOS registry on the worklist as leads surface.

## What This Skill Does NOT Do

- Search listings or confirm on-market status (`deal-finder`); value a property (`comp-analyzer`, `cap-rate-comp-selector`); underwrite, size debt or compute credits (`underwriting-market-rate-multifamily`, `front-door-lihtc-underwriting`, `residential-deal-underwriter`, `sizing-conventional-multifamily-debt`, `sizing-lihtc-permanent-debt`).
- Extract contractual dates from documents (`critical-dates-tracker`); research news (`forward-pipeline-and-news-intelligence`); verify title (`legal-title-risk-assessment`).
- Fetch live data inside its scripts, skip-trace individuals outside class 1 Tier A/B, or collect age and voter data at all.

## Pipeline Mode (Optional)

Standalone by default. When a `market_id` config is supplied, the user asks for an agent
checkpoint, or an orchestrator invoked the skill, also write `data/status/{market_id}/sourcing/off-market-targets.json`
with `{agent: "off-market-deal-finder", phase: "sourcing", market_id, status: COMPLETE | PARTIAL | FAILED,
payload: {leads_path, handoffs_dir, calendar_summary}}`. `PARTIAL` means the run completed on a
degraded inbox (for example OHCS only) and the brief names the missing files.

## Integration

| Related Skill | Relationship |
|---|---|
| `deal-finder` | On-market dedupe of Tier A leads; this skill is the sole off-market authority |
| `comp-analyzer` / `cap-rate-comp-selector` | Replace `value_source: proxy` with comp-based value or cap rate |
| `multifamily-benchmarks` | Source of DSCR/LTV/debt-yield/cap-rate/opex bands; benchmark date surfaced on Assumptions |
| `multifamily-underwriting-formulas` / `sizing-conventional-multifamily-debt` / `sizing-lihtc-permanent-debt` | Formula source of truth; authoritative sizing after screening |
| `underwriting-market-rate-multifamily` | Class 2 Tier A handoff |
| `front-door-lihtc-underwriting` | Class 3 Tier A handoff via `lihtc_context` (Composition mode) |
| `residential-deal-underwriter` | Class 1 Tier A handoff |
| `critical-dates-tracker` | Replaces non-RECORDED dates once documents arrive; shared event taxonomy and flag vocabulary |
| `forward-pipeline-and-news-intelligence` | Per-asset news and regulatory verdict for Tier A |
| `legal-title-risk-assessment` | Confirms trust deeds, balances and junior liens before outreach |
| `sponsor-credibility-assessor` / `new-state-entry-diagnostic` | Buyer-side assessment when the user is a nonprofit or out-of-state sponsor |
| `market-research-assistant` | Metro context and CBSA definition behind `geography_mode` |

## Reference Documentation

- See [references/pipeline-contract.md](references/pipeline-contract.md) for lead/event tables, enums, basis multipliers, flags, helper-deadline rule, run manifest and diff semantics (read before writing adapter output).
- See [references/capital-stack-math.md](references/capital-stack-math.md) for value proxies, amortization, refi test, lender-term inference and the image-extraction schema (Step 4).
- See [references/decision-maker-enrichment.md](references/decision-maker-enrichment.md) for owner_type rules, full archetype table, resolution chain, contact grades, SOS worklist (Step 6).
- See [references/outreach-and-compliance.md](references/outreach-and-compliance.md) for angle/channel/do-not per archetype, compliance gates and `buyer_profile` gating (before any contact).
- See [references/output-contract.md](references/output-contract.md) for the full jsonc, workbook column spec, brief template and handoff field maps (Step 7).
- See [references/sfr-distress.md](references/sfr-distress.md), [references/market-rate-multifamily.md](references/market-rate-multifamily.md), [references/affordable-regulated.md](references/affordable-regulated.md) for the class modules (load only the routed one); `references/scoring/*.json` and `shared_adjustments.json` are the canonical weights.
- See [references/sources/README.md](references/sources/README.md) (adding a pack, `verified_live` policy, access tiers), [references/sources/federal/README.md](references/sources/federal/README.md) (national tapes, QC policy and preservation-notice laws by state) and [references/sources/oregon-portland/README.md](references/sources/oregon-portland/README.md) (worked example, coverage matrix, verify-before-first-run checklist; `rent-limits.json` placeholder for the restricted-income value proxy).
- See `assets/outreach-templates/` (ten archetype templates) and `assets/lender_type_dictionary.csv` (grantee token -> lender_type).
- Scripts (`scripts/README.md` gives the run order): `date_profile.py`, `ohcs_inventory_targets.py`, `normalize_hud_insured.py`, `normalize_hud_sec8.py`, `normalize_ohcs_forecast.py`, `normalize_recorder_index.py`, `normalize_assessor_taxlots.py`, `merge_leads.py`, `query_calendar.py`, `score_leads.py`, `build_workbook.py`, `make_handoffs.py`, `smoke_test_sources.py` (flips `verified_live` only on a confirmed fetch), `run_pipeline.py` (orchestrates, manifests, diffs).
- See `references/sample-output/` for a script-generated Portland tri-county affordable run (REPORTED/DERIVED-only, no RECORDED dates, no Tier A by design) and `evals/evals.json` for the three test prompts.
