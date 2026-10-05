# Class Module: Affordable and Regulated Apartments (`affordable_regulated`)

Read this module only when Step 0 routes to `affordable_regulated`. Shared vocabulary is in `pipeline-contract.md`; shared math in `capital-stack-math.md`; the canonical weights are `scoring/affordable_regulated.json` (Section 5 reproduces them and must match). Oregon is the worked example; the per-state tables in `sources/federal/` generalize it.

## Contents

1. Scope and routing rules
2. Signal catalog
3. Event derivation rules
4. Valuation and capital-stack proxy
5. Scoring rubric
6. Owner archetypes and outreach angles
7. Lead-card additions
8. Pro tips and timing
9. Refresh cadence
10. Known gaps

---

## 1. Scope and routing rules

In scope: any rental property with an active affordability restriction or subsidy: LIHTC (9%/4%) in the compliance or extended-use period, project-based Section 8 (HAP, PRAC, RAC, PAC), HUD-insured or HUD-held debt with a use agreement (221(d)(3) BMIR, 236, 202/811, 223(f) with LIHTC), USDA 514/515, HOME, state soft-loan programs (Oregon: OAHTC, GHAP, HDGP, LIFT, HTF, Other OHCS), local regulatory agreements (PHB loans, TIF/URA covenants). Query types: `regulatory_expiry` (Year 15/30, HAP, program ends), `maturity` (HUD/USDA/agency/recorded first-mortgage dates), `distress`, or `all`.

Routing in: a supplied file matching a housing-inventory or HUD schema (OHCS OAHI, HUD FHASL, HUD MF Assistance & Sec 8, HUD LIHTC, USDA MFH, NHPD) routes here before any keyword; regulated vocabulary (affordable, LIHTC, Year 15, HAP, Section 8, 236, 202, USDA, 515, preservation, regulatory agreement, extended use) routes here.

Routing out: all restrictions expired -> `market_rate_mf` with `ex_regulated` tag; Portland Inclusionary Housing buildings -> `market_rate_mf` with `IH_SET_ASIDE` (99-year covenant on a small set-aside; no public unit registry); `Status == In Development` -> excluded; housing authority / government owners stay in class but route `partnership_preservation` with tier cap B.

Two horizons: `horizon_years` governs DEBT events; `regulatory_horizon_years` governs REGULATORY events. "Loans coming due within 5 years" sets the first; the user's unstated interest in Year 15/30 and HAP cliffs is served by the second. Keep `first_debt_event` and `first_reg_event` as separate columns.

## 2. Signal catalog

Actual loan maturities exist publicly for two slices only: HUD/FHA-insured or HUD-held loans (FHASL) and USDA 514/515 (MFH exit data). Everything else (bank, agency, bond, state soft loans) is proxied from regulatory expirations, recorded trust deeds, or `Financial_Closing_Date + 15y`, and labeled accordingly. `verified_live` is true only for the OHCS CSV on disk (every date column pattern-tested) and the edgartools guide.

| signal | event_type | family | source (adapter) | fields | access | URL | verified_live | window | basis | points rule |
|---|---|---|---|---|---|---|---|---|---|---|
| State HFA inventory regulatory expirations (Oregon OAHI) | LIHTC_EXTENDED_USE_END, SOFT_PROGRAM_END, HAP_EXPIRATION (0.70), USDA_515_MATURITY, REGULATORY_LATEST_END; DERIVED LIHTC_COMPLIANCE_END; PROXY LOAN_MATURITY | REGULATORY / DEBT | OHCS Oregon Affordable Housing Inventory CSV, Socrata p9yn-ftai (`ohcs_inventory_targets.py`) | Property Name, Address, City, Zip, County, Status, Property Type, Year Built, Rehab Year, Management/Developer/Owner Name, Owner Type, Total Units, AMI buckets, Rental_Assistance_Count, Financial_Closing_Date (DD/MM/YYYY), Compliance_Start_Date and all `*_Expiration_Date` (MM/DD/YYYY), USDA_RD_Expiration_Date (`%Y %b %d %I:%M:%S %p`), LATEST_Expiration_Date, HUD Contract, OHCS Funded?, Geocode WKT | free-public | https://data.oregon.gov/d/p9yn-ftai | true (file on disk; live page not fetched) | 0-60 mo | REPORTED (dates); DERIVED (Year 15); PROXY (mini-perm) | regulatory_event_timing bands; PROXY maturity scores x0.30; LATEST blank in 554 rows -> recompute |
| LIHTC Year 15 (compliance period end) | LIHTC_COMPLIANCE_END | REGULATORY | HUD LIHTC Database LIHTCPUB (`normalize_hud_lihtc.py`, future; not shipped in v2); OHCS Compliance_Start_Date fallback (shipped) | HUD_ID, PROJECT, address, YR_ALLOC, YR_PIS, N_UNITS, LI_UNITS, CREDIT (4%/9%), NON_PROF, TYPE, QCT/DDA, FMHA_515, HOME, NLM_REASON | free-public | https://www.huduser.gov/portal/datasets/lihtc.html | false | 36 mo before to 24 mo after | DERIVED (0.80) | 12-36 mo out and for-profit GP 20; nonprofit GP / PHA 0 (route partnership); > 24 mo past with no transfer 10 |
| LIHTC Year 30 / extended-use end | LIHTC_EXTENDED_USE_END | REGULATORY | OHCS LIHTC_4/9_Expiration_Date; recorded Declaration of Land Use Restrictive Covenants / REUA (recorder); fallback YR_PIS + 29 | REUA end date, QC waiver clause, owner LP/GP names | free-public (OHCS); recorder image fee | https://data.oregon.gov/d/p9yn-ftai ; https://multcorecords.com/ | true / false | <= 36 mo 25; 36-60 mo 15 | REPORTED (OHCS/LURA); DERIVED (fallback) | regulatory_event_timing |
| Qualified contract eligibility / request / lapse | QC_ELIGIBILITY (status eligible / requested / lapsed_decontrol) | REGULATORY | the property's recorded REUA / Declaration (waiver clause) first, then `sources/federal/qc-policy-by-state.md` (Oregon: unknown / likely waiver_required for recent allocations); OHCS Asset Management QC-request list (records request) | YR_ALLOC, waiver flag, request date | free-public / manual | https://www.oregon.gov/ohcs/development/Documents/LIHTC/QAP/draft-qualified-contract-procedure.pdf | false | year >= 15; QC period 1 y; 3-y decontrol | DERIVED / RECORDED | declared_intent: eligible 8; requested 17; lapsed/decontrol 20 |
| HAP / PRAC / PAC contract expiration and renewal pattern | HAP_EXPIRATION, HAP_OPTOUT_NOTICE_DEADLINE | REGULATORY | HUD Multifamily Assistance & Section 8 Contracts DB, two Excel tables joined on property_id (`normalize_hud_sec8.py`) | property_id, property_name_text, address, owner_organization_name, owner_main_phone_number_text, mgmt_agent_org_name, contract_number, program_type_name, tracs_effective_date, tracs_overall_expiration_date, tracs_current_expiration_date, assisted_units_count, rent_to_FMR_ratio, primary_fha_number, is_hud_administered | free-public | https://www.hud.gov/hud-partners/multifamily-assist-section8-database | false | <= 24 mo; opt-out notice >= 12 mo before | REPORTED, confidence 0.70 (annual renewal) / 0.90 (20-y MAHRA) | 15 (<= 24 mo); +5 short-renewal pattern with for-profit owner; -5 fresh 20-y renewal |
| Section 8 opt-out / renewal-intent notice | PRESERVATION_NOTICE_RECEIVED (detail hap_optout) | REGULATORY | PBCA / OHCS HUD Contract Administration records request (no national dataset; Minnesota opt-out log is the model) | property, notice date, intended termination date, stated intent | manual | https://www.oregon.gov/ohcs/Pages/hca-hud-contract-administration.aspx ; model https://www.mnhousing.gov/rental-housing/federal-opt-out-log.html | false | 12 mo before expiration | RECORDED | 20 |
| Oregon PuSH-CP owner notices, 10-Year Expiration Forecast, Preservation Dashboard | PRESERVATION_NOTICE_WINDOW (DERIVED, statute text unverified), PRESERVATION_NOTICE_RECEIVED (push_first / push_second / hap_optout), signals on_state_expiring_list and push_window_open | REGULATORY | OHCS PuSH page; data.oregon.gov "Affordable Housing 10-Year Expiration Forecast" (`normalize_ohcs_forecast.py`: template adapter, alias-matched field names and status vocabulary, `--prior` writes the quarterly status-flip diff); records request to PuSH-CP Program Manager | property, affordable units, assistance type, AMI, expiration/termination date, preservation status, notice date when published | free-public / manual | https://www.oregon.gov/ohcs/compliance-monitoring/pages/push.aspx | false | first notice 36-30 mo, second 30-24 mo before expiration (OAR 813-115 snippets) | DERIVED / RECORDED | notice received 20; window open as of run date +4 (`push_window_open`, modifier) and a Pipeline Action to request the notice; on list within 5 y without notice 6 |
| Recorded Notice of Right of First Refusal / OHCS designee agreement | ROFR_RECORDED | REGULATORY (ROUTING) | recorder index by parcel/owner ("Notice of Right of First Refusal") | grantee (OHCS / local government / designee), recording date | free-public | https://multcorecords.com/ | false | from first notice through 24-36 mo after termination (duration unresolved) | RECORDED | 15 and `rofr_encumbered` -> partnership_preservation |
| HUD-insured / HUD-held loan maturity and prepayment window | LOAN_MATURITY (HUD_INSURED), HUD_DIRECT_LOAN_MATURITY (SOA 236 / 221(d)(3) / 202), PREPAY_WINDOW_OPEN, REFINANCE_CLOSED | DEBT | HUD FHASL Active + Terminated (`normalize_hud_insured.py`); HUD eGIS Section 202 layer | HUD Project Number, name, address, units, endorsement dates, original amount, first payment, Maturity Date, term, rate, UPB, holder, servicer, SOA code | free-public | https://www.hud.gov/hud-partners/multifamily-fhasl-active | false | <= 36 mo 20 (regulatory leg) / 12 (debt leg); 36-60 10 / 6 | RECORDED | +5 236 IRP/decoupling; +5 no HAP overlay; prepay window +3 |
| Mark-to-Market portfolio membership | signal m2m_portfolio | OWNERSHIP (attribute) | HUD OAHP quarterly M2M Transactions Report (PDF) | property, FHA/REMS id, owner, milestones, HUD-held MRN/CRN notes, 30-y use agreement | free-public | https://www.hud.gov/hud-partners/multifamily-mark-to-market-program | false | ongoing | RECORDED | owner_sponsor +3 |
| USDA 514/515 maturity, prepayment eligibility, projected exit | USDA_515_MATURITY, USDA_515_PREPAY_ELIGIBLE, USDA_EXIT_PROJECTED | DEBT | USDA RD MFH Program Exit Data (`normalize_usda_mfh.py`, future); OHCS USDA_RD_Expiration_Date; CARH / Affordable Housing Online as sanity check | borrower, project id, name, address, units, RA units, loan amount, loan date, term, remaining term, maturity, estimated exit year, prepay eligible flag/date, borrower type | free-public | https://www.sc.egov.usda.gov/data/MFH.html | false | <= 36 mo 20; 36-60 10; prepay-eligible +5 | RECORDED / REPORTED (exit year, +/-12 mo) | mostly metro-fringe (Columbia, Yamhill, Clark exurbs) |
| NHPD deduplicated subsidy end dates | REGULATORY_LATEST_END cross-check; LOAN_MATURITY for HUD/USDA | REGULATORY / DEBT | NHPD property + subsidy extracts (free registration) | property, address, owner name/type, subsidy program, start/end dates, assisted units, REAC score, inactive extract | free-registration | https://preservationdatabase.org/ | false | quarterly; lags state data | REPORTED | conflict resolution: take most recent vintage per field; inactive extract = recent conversions (comps) |
| State soft-program affordability period ends (HOME, OAHTC, GHAP, HDGP, LIFT, HTF, Other OHCS) | SOFT_PROGRAM_END | REGULATORY | OHCS OAHI `*_Expiration_Date` columns | per-program dates | free-public | https://data.oregon.gov/d/p9yn-ftai | true | <= 36 mo | REPORTED | timing 8; regulatory_stacking 2 programs 6 / 3+ 10; +4 HAP + extended use same 24 mo |
| Soft-loan note maturity (only when recorded) | SOFT_LOAN_MATURITY | DEBT | recorder trust deed (PHB, OHCS, HOME loans); PHB portfolio data; loan docs via `critical-dates-tracker` | stated maturity, coterminous language | free-public (index) / fee (image) | https://www.portland.gov/phb/data-and-reports | false | coterminous with first mortgage or regulatory agreement | RECORDED | capital_stack +3 when coterminous with first |
| REAC / NSPIRE inspection scores | REAC_SCORE | OPERATING | HUD Multifamily Physical Inspection Scores Excel | property_id, inspection_date, inspection_score, inspection_protocol | free-public | https://www.hud.gov/stat/mfh/inspection-scores | false | strongest within 12 mo of a failing score | REPORTED | <= 30 = 10; < 60 = 7; >= 15-pt decline 5 |
| Property-tax exemption lost / tax delinquency / ORS 312 list on a regulated asset | TAX_EXEMPTION_LOST / TAX_DELINQUENT_YEARS / TAX_FORECLOSURE_LIST | OPERATING / TAX_LIEN | assessor roll exemption code diff (ORS 307.540 etc.); MultcoPropTax; DART list | exemption code by year; delinquent years | free-public / free-registration / manual | https://www.multco.us/assessment-taxation/reports-and-data | false | annual | RECORDED | exemption lost 6; delinquent 1-2 y 7; list 10 |
| OHCS stabilization / preservation award or dashboard at-risk status | STABILIZATION_AWARD | OPERATING | OHCS award lists; dashboard preservation-status values | property, award, status | free-public | https://www.oregon.gov/ohcs/compliance-monitoring/pages/push.aspx | false | rolling | RECORDED | 6 |
| HUD assisted-properties owner and management agent (contact spine) | owner/agent names; join to LIHTC NON_PROF | OWNERSHIP | HUD eGIS Multifamily Properties - Assisted layer; HUD MF Assistance DB | OWNER_ORGANIZATION_NAME, MGMT_AGENT_ORG_NAME, program flags, lat/long | free-public | https://egis.hud.gov/arcgis/rest/services/cpdmaps/HudMfProps/MapServer/2 | false | monthly | RECORDED | decision-maker chain hop 1 |
| Ownership structure: for-profit GP, LP transfer to aggregator, GP/agent change, sponsor portfolio Year 15/30 load | owner_type; MANAGER_CHANGE / REGISTERED_AGENT_CHANGE; signals lp_transferred_recent, sponsor_other_properties_hitting_y15_30_36mo | OWNERSHIP | Oregon SOS registry (LP lists every GP); LURA; OHCS Developer Name; court dockets for Year-15 litigation (SunAmerica v. Pathway of Pontiac pattern) | GP, managers, officers, status, filings | free-public / free-registration | https://egov.sos.state.or.us/br/ | false | Year 15 +/- 3 y | RECORDED | for-profit GP 10; LP/GP change +8; sponsor 2+ Y15/30 +6; out-of-state +4; nonprofit 0 (partnership); PHA/government -20 |
| Local regulatory layers (Metro RLIS affordable inventory; PHB portfolio) | LOCAL_REG program tag; SOFT_LOAN_MATURITY candidates | REGULATORY | Metro RLIS Affordable Housing file geodatabase; PHB Affordable Rental Housing Portfolio map | property, taxlot, regulated units by AMI, funding sources, expiration where known; PHB loan / regulatory agreement presence | free-registration / free-public | https://rlisdiscovery.oregonmetro.gov/maps/drcMetro::affordable-housing ; https://www.portland.gov/phb/data-and-reports | false | annual (RLIS layer may be stale; 2020 metadata) | REPORTED | adds City consent / notice parties; PHB soft loan as a debt-stack layer |
| First-mortgage debt from agency / CMBS tapes on regulated assets | LOAN_MATURITY, IO_EXPIRATION, PREPAY_WINDOW_OPEN | DEBT | DUS Disclose (MAH indicator), MSIA, EX-102 | as in `market-rate-multifamily.md` | free-registration / free-public | https://mfdusdisclose.fanniemae.com/#/home ; https://mf.freddiemac.com/investors/data | false | <= 36 mo 12; 36-60 6 | REPORTED | capital_stack_pressure |
| Quality / negative signals | status, rehab_year, LIFT 60-year REUA | n/a | OHCS fields | Status, Rehab Year, LIFT_Expiration_Date, LIHTC_9 end > 30 y | free-public | — | true | n/a | — | exclude In Development; rehab <= 5 y -15; LIFT/60-y SCHEDULED, no timing points; proxy-only cap C |

## 3. Event derivation rules

```
OHCS OAHI (declared formats; see sources/oregon-portland/dataset-schemas.yaml):
  Financial_Closing_Date        '%d/%m/%Y'  (day-first: 222 of 298 values have first field > 12, zero have second > 12)
  Compliance_Start_Date, every *_Expiration_Date, LATEST_Expiration_Date   '%m/%d/%Y'
  USDA_RD_Expiration_Date       '%Y %b %d %I:%M:%S %p'   e.g. '2038 Nov 17 12:00:00 AM'
  LATEST_Expiration_Date        recompute = max(components) when blank (554 rows); equals max in 1,263 of 1,265 populated rows;
                                exceptions Casa Sonada 4, Riverside Terrace -> 'Verify — Conflicting Sources', not rejected

  LIHTC_EXTENDED_USE_END        = LIHTC_9_Expiration_Date / LIHTC_4_Expiration_Date (REPORTED; program tag per column)
  SOFT_PROGRAM_END              = each HOME/OAHTC/GHAP/HDGP/LIFT/HTF/Other_OHCS date (REPORTED; program per column) -- affordability period end, not a note maturity
  HAP_EXPIRATION                = HUD_MF_Expiration_Date (REPORTED, confidence 0.70) ; replaced by HUD Sec 8 tracs_overall_expiration_date when present
  USDA_515_MATURITY             = USDA_RD_Expiration_Date (REPORTED) ; replaced by USDA exit data when present
  REGULATORY_LATEST_END         = LATEST_Expiration_Date (REPORTED)
  LIHTC_COMPLIANCE_END          = Compliance_Start_Date + 15 y (DERIVED, window +12 mo; flag '+15 election possible')
  LOAN_MATURITY (PROXY)         = Financial_Closing_Date + 15 y (17 y when LIHTC_4), window +/-36 mo, derivation text stored

HUD LIHTC DB:
  LIHTC_COMPLIANCE_END          = Dec 31 of (YR_PIS + 14)            (DERIVED)
  LIHTC_EXTENDED_USE_END fallback = Dec 31 of (YR_PIS + 29)          (DERIVED) when no REUA/OHCS date
  QC_ELIGIBILITY.status         = eligible when year >= 15, YR_ALLOC < state waiver adoption year, state policy != prohibited, no waiver clause in REUA

HUD Sec 8:
  HAP_EXPIRATION                = tracs_overall_expiration_date ; detail short_renewal_pattern when (overall - effective) <= 5 y repeatedly ; mahra_20yr_recent when a 20-y term started within 24 mo
  HAP_OPTOUT_NOTICE_DEADLINE    = HAP_EXPIRATION - 12 mo (DERIVED)
  rent_gap                      = rent_to_FMR_ratio ; < 0.85 in a strong submarket -> opt-out risk ; > 1.0 -> renewal incentive

HUD FHASL:
  LOAN_MATURITY                 = Maturity Date (RECORDED) ; HUD_DIRECT_LOAN_MATURITY when SOA in {236, 221(d)(3), 202} ; detail 236_irp when SOA 236 ; no_hap_overlay when no Sec 8 contract joins
  PREPAY_WINDOW_OPEN            = Final Endorsement Date + 10 y (DERIVED, +/-6 mo)
  REFINANCE_CLOSED / SUPPRESS_UNTIL from Terminated rows matched on digits-only HUD Project Number

USDA:
  USDA_515_MATURITY             = loan maturity (RECORDED) ; USDA_515_PREPAY_ELIGIBLE = prepay eligible date (RECORDED) ; USDA_EXIT_PROJECTED = Dec 31 of estimated exit year (REPORTED, +/-12 mo)

Oregon PuSH (ORS 456.250-.265; OAR 813-115 -- windows from OAR snippets, statute text NOT read in this build):
  PRESERVATION_NOTICE_WINDOW    = [expiration - 36 mo, expiration - 30 mo] first notice ; [expiration - 30 mo, expiration - 24 mo] second notice
                                  basis DERIVED (statute text unverified); emitted only when units >= 5 and programs intersect the PuSH-covered set
                                  (HAP/PRAC/RAC/PAC, LIHTC, HUD 236/202, USDA 515, OHCS programs) per ORS 456.250; never scored as a date, never a first_* event
  push_window_open              = window_start <= as_of <= window_end  (signal; +4 in declared_intent_and_notice; Pipeline Action: request the notice)
  PRESERVATION_NOTICE_RECEIVED  = notice date from records request or forecast-list status flip (RECORDED; Needs Anchor Date when the file has no notice date)
  ROFR_RECORDED                 = recording date
  QC_ELIGIBILITY.status         = eligible for an Oregon property ONLY after reading its recorded REUA / Declaration (no waiver clause) and the QAP for its
                                  allocation year; OHCS is believed to require a QC waiver of current allocations (sources/federal/qc-policy-by-state.md)
```

Validation: every REGULATORY event >= Compliance_Start_Date when present (else `Verify — Conflicting Sources`); Compliance_Start_Date within 36 months after Financial_Closing_Date when both present; month <= 12 after parsing; year 1960-2100; exclude In Development.

## 4. Valuation and capital-stack proxy

`est_value = restricted_noi / cap_rate_affordable` (pack: Class C cap + 100 bp = 6.75%), `value_source = restricted_income_proxy`, computed by `ohcs_inventory_targets.py` once the pack's `rent-limits.json` holds the current MTSP max rents by AMI band (it ships with nulls); until then the adapter writes `units x price_per_unit_avg` with `value_source = ppu_band` and flags `Missing Source — Request Document` for the rent roll, and the Capital_Stack tab shows that basis. `restricted_noi` from AMI unit buckets x LIHTC max rents (HFA rent-limit table) + HAP units x contract rent + market units x ZIP rent, vacancy 0.071 (0.03 on HAP units), opex ratio 0.50 or pack `opex_per_unit_regulated` (OHCS FY24 $8,198 inflated), whichever is higher. Report a `conversion_scenario` value (market rents, market cap) only when LIHTC_EXTENDED_USE_END or REGULATORY_LATEST_END falls inside the horizon and no ROFR/PuSH encumbrance is recorded.

Debt: first mortgage from HUD/USDA/agency/CMBS tape or recorded trust deed; soft loans listed as layers with their own basis (`SOFT_LOAN_MATURITY` only when recorded). Refi test on restricted NOI with `dscr_floor 1.15`, LTV 0.80, debt yield 0.08 (hard-debt sizing conventions from `sizing-lihtc-permanent-debt`, which also handles mandatory soft debt vs residual receipts). PROXY mini-perm maturities (Financial_Closing_Date + 15y) carry no balance; `est_loan_balance` reads `not in public record` and the lead is capped at Tier C unless another source supplies the debt.

## 5. Scoring rubric

Canonical: `scoring/affordable_regulated.json`.

| factor | weight | rule |
|---|---|---|
| Regulatory event timing | 25 | nearest of: extended-use end <= 36 mo 25, 36-60 mo 15; Year 15 12-36 mo out 20 when owner_type `lihtc_partnership_forprofit_gp`, 0 (route partnership) when nonprofit GP / PHA / government; > 24 mo past Year 15 with no transfer 10; HAP <= 24 mo 15 (+5 short-renewal pattern with for-profit owner; -5 fresh 20-y MAHRA; x0.70 confidence when annually renewing); HUD direct-loan maturity <= 36 mo 20 (+5 236 IRP; +5 no HAP overlay); USDA 515 maturity/exit <= 36 mo 20, 36-60 10, prepay-eligible +5; soft program end <= 36 mo 8; latest end <= 36 mo 12; take max; cap 25; x basis multiplier |
| Declared intent and notice | 20 | PuSH notice received 20; Section 8 opt-out notice confirmed 20; QC request confirmed 17; QC period lapsed / decontrol running 20; ROFR recorded 15 with `rofr_encumbered` routing; QC eligible (pre-waiver vintage, no waiver in the REUA) 8; on state 10-year list within 5 y without notice 6; take max; modifier +4 when the PuSH first-notice window is open as of the run date (`push_window_open`); cap 20 |
| Capital-stack pressure | 15 | HUD/USDA/agency/CMBS/recorded LOAN_MATURITY <= 36 mo 12, 36-60 mo 6; PROXY mini-perm scores through the same bands x0.30, no extra rule; refi gap under restricted NOI > 25% +5, 10-25% +3; recorded soft loan coterminous with first +3; prepay window (endorsement + 10 y) <= 12 mo +3; cap 15 |
| Regulatory stacking | 10 | 2 regulatory programs ending within the same 24 mo 6; 3+ = 10; HAP and extended-use within the same 24 mo +4; cap 10 |
| Owner / sponsor profile | 15 | for-profit or Limited Dividend GP 10; LP transferred to aggregator / recent GP or agent change +8; sponsor with 2+ other properties hitting Year 15/30 within 36 mo +6; out-of-state sponsor +4; nonprofit GP 0 (route partnership_preservation; +5 motivation on that track only); housing authority / government -20 and partnership route; M2M +3; cap 15, floor 0 |
| Operating distress | 10 | REAC <= 30 = 10; < 60 = 7; >= 15-pt decline 5; tax exemption lost 6; tax delinquent 1-2 y 7, foreclosure list 10; stabilization award 6; occupancy < 85% or down 10 pts 4; take max |
| Signal stacking | 5 | 2 families 3; 3+ = 5 |

Quality rules: exclude In Development; rehab within 5 y -15; LIFT / 60-year REUA with extended use > 30 y out -> SCHEDULED, no timing points; proxy-only -> cap C; nonprofit with ROFR or PRAC and all housing-authority / government owners -> `partnership_preservation`; ROFR_RECORDED -> `rofr_encumbered`.

## 6. Owner archetypes and outreach angles

| owner_type | decision maker | angle | template | gates |
|---|---|---|---|---|
| lihtc_partnership_forprofit_gp | GP managing member (SOS LP record lists every GP) + syndicator asset manager | Year 15: buyout / resyndication / fund the LP exit; Year 30: preservation purchase or conversion partner | `lihtc_gp_year15` | preservation_law; lihtc_tenant_protections; dnc_scrub |
| lihtc_partnership_nonprofit_gp / nonprofit | ED / CFO / board | recap or JV; preservation capital; ROFR support (§42(i)(7) minimum price = debt + exit taxes) | `nonprofit_partnership` | preservation_law |
| housing_authority / government | development director | RAD / conversion / mixed-finance partner | `housing_authority_partnership` | none (partnership only) |
| HUD / USDA-assisted owner (overlay) | owner org + management agent; HUD/HFA/RD AE as process contact | HAP renewal vs opt-out economics (Mark-Up-to-Market), 236 decoupling, 515 transfer with RA, M2M note treatment | `hud_usda_assisted_owner` | preservation_law; lihtc_tenant_protections; assumption_approval |
| institutional (funds holding LP or fee interests) | asset manager | formal IOI; assumption of HUD debt | `institutional` | assumption_approval |
| lender_reo_receiver | receiver / special servicer / HUD (for HUD-held notes) | register as qualified buyer | `receiver_lender` | counsel_only when bankruptcy |

`buyer_profile` matters most here: `nonprofit_preservation` and `qualified_purchaser` turn the PuSH ROFR from a constraint into a right (`outreach-and-compliance.md` Section 3).

## 7. Lead-card additions

`Programs` with each program's end date and basis; `Year 15` and `Year 30` dates with basis and `+15 election possible` flag; `HAP`: contract type, expiration, renewal pattern, rent_to_FMR; `PuSH`: notice window start/end, whether the window is open now (`push_window_open` -> Pipeline Action: file the records request), notice status, ROFR recorded; `QC`: eligibility status and waiver note; `HUD/USDA loan`: SOA, maturity, UPB, rate, prepay window, assumable; `Soft debt layers` with basis (or `not in public record`); `REAC` latest score / protocol / trend; `Sponsor`: GP, LP/syndicator, nonprofit flag, other Year 15/30 events in portfolio; `Restricted value` and, when applicable, `conversion_scenario` value; `Track` (acquisition / partnership_preservation).

## 8. Pro tips and timing

- **Year 15 is a negotiation window; Year 30 is the cliff.** At Year 15 the LP exits and the GP decides between buyout, resyndication and sale; at Year 30 (or after a lapsed qualified contract) restrictions can end. Oregon PuSH notices start 36 months before the cliff, so the realistic outreach window is 36-24 months out.
- **Who holds the ROFR decides the deal.** A nonprofit GP with a §42(i)(7) ROFR buys at minimum price; approach as recap/JV partner. A for-profit GP with an institutional or aggregator LP is the strongest off-market acquisition signal. Check whether LP interests have traded (MANAGER_CHANGE, litigation dockets).
- **HAP dates roll annually.** An expiration 12 months out under annual renewal is not a departure; weigh it at 0.70 until a PBCA opt-out notice or a PuSH notice confirms intent. A fresh 20-year MAHRA renewal is a suppression.
- **Parse OHCS dates with declared formats, never a heuristic.** Financial_Closing_Date is day-first; every other slash column is month-first; USDA is `YYYY Mon DD hh:mm:ss AM`. A single-format guess mis-parses roughly 75% of closing dates.
- **LATEST is blank 30% of the time.** Recompute it as the max of components and flag the two known exceptions rather than rejecting them.
- **A mini-perm proxy is a hypothesis.** `Financial_Closing_Date + 15y` has a 0.30 multiplier and a +/-36 month window; it earns Tier C at most until a recorder image, HUD row or loan document replaces it. Say so in the brief.
- **Preservation law gives qualified purchasers rights; position as a designee.** OHCS, the affected local government or an OHCS-appointed designee can record a ROFR and match any third-party offer within 30 days (statutory windows from OAR 813-115 snippets; confirm against current ORS 456.260-.265 text post-SB 973 before quoting to a counterparty). If the user is a nonprofit or works with one, that is the lane.
- **236 maturities end the use agreement.** 1970s-80s 40-year loans are at or past maturity; decoupling, RAD and Section 8 preservation tools shape the recap. Nonprofit owners here get the mission-partnership script, never a distress script.
- **USDA 515 is a fringe play.** Mostly outside Portland city limits (Columbia, Yamhill, Clark exurbs); prepayment requires RD approval, advance tenant notice (period per 7 CFR part 3560 subpart N; verify) and restrictive-use provisions.
- **Score certain, dated events over "distress".** A recorded LURA end date beats a failed REAC score for predicting a transaction.

## 9. Refresh cadence

| feed | cadence |
|---|---|
| OHCS OAHI | each release (key on Property Name + Address, not row order) |
| OHCS 10-Year Forecast / dashboard | quarterly diff |
| HUD FHASL Active + Terminated | monthly |
| HUD MF Assistance & Sec 8 | monthly |
| HUD LIHTC DB | annual |
| REAC/NSPIRE scores | per release (semiannual) |
| USDA MFH exit data | semiannual |
| NHPD | quarterly (three updates a year) |
| recorder (LURA, ROFR notices, trust deeds, modifications) | weekly |
| SOS (GP / manager / status) | on worklist; quarterly for the sponsor map |
| assessor exemption codes / tax status | annual roll; semiannual tax |
| PBCA / OHCS records requests (opt-out, PuSH notices, QC requests) | quarterly |
| rent limits and HAP rents | annual (HUD income limits release) |

## 10. Known gaps

- No public source gives actual loan maturities for non-FHA, non-USDA affordable debt (bank, agency, bond, state soft loans); the proxy tier must stay labeled and Tier C-capped.
- OHCS data quality: Owner Type blank in 1,039 rows and mixed case; County mixed case (normalize to Multnomah 546 / Washington 163 / Clackamas 101 = 810 tri-county); City typo `Portalnd`; Property Type `0` (25) and `ERROR: #N/A` (8); Financial_Closing_Date in only 298 rows; Compliance_Start_Date in 890; expiration dates are regulatory, not loan maturities.
- OHCS publishes no discrete log of PuSH owner notices or Section 8 opt-out notices; the 10-Year Forecast dataset with preservation status is the public proxy; raw notices need records requests. The PBCA identity may change under HUD's FY2025 PBCA NOFO.
- ORS 456.262/.263 ROFR duration appears as 24 months (designee agreement) and 36 months (after termination) in different snippets; owner-notice timing cited as "2 years" in the 2017 statute vs 36-30 / 30-24 month dual notices in OAR 813-115. Confirm current text (post-SB 973) before publishing timing.
- Oregon qualified-contract policy unconfirmed and likely restrictive: OHCS REUAs and QAPs are widely understood to require a QC waiver of current allocations, so post-adoption vintages are probably ineligible; absence from 2017-2019 waiver lists is weak negative evidence. Score QC_ELIGIBILITY `eligible` only after reading the property's recorded REUA and the QAP for its allocation year.
- HUD LIHTC DB lacks extended-use end dates, REUA/QC-waiver terms, owner names and parcel IDs; Year 15 is computed from YR_PIS (+14 assumption; owners may elect +15); for non-Oregon states the recorded LURA is required.
- NHPD requires registration; terms of use for commercial prospecting unconfirmed; no API.
- NSPIRE and legacy UPCS scores are not comparable; LIHTC-only properties are inspected by OHCS and those scores are not public.
- Portland Inclusionary Housing units have 99-year covenants and no public registry; they belong in `market_rate_mf` with the `IH_SET_ASIDE` tag.
- Metro RLIS affordable layer may be stale (2020 metadata); Clark County WA is absent from OHCS and RLIS (use NHPD WA, HUD, USDA, WSHFC inventories; WSHFC not verified).
- Every external source `verified_live=false` except the OHCS file on disk and the edgartools guide; re-verify URLs, field names and vintages before hard-coding them.
