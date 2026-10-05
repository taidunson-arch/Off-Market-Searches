# Class Module: SFR and 2-4 Unit Distress (`sfr_small_res`)

Read this module only when Step 0 routes to `sfr_small_res`. Shared vocabulary is in `pipeline-contract.md`; shared math in `capital-stack-math.md`; the canonical weights are `scoring/sfr_small_res.json` (Section 5 below reproduces them for readability and must match).

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

In scope: 1-4 unit residential (SFR, condo, duplex, triplex, fourplex) and small investor portfolios financed with residential trust deeds. 2-4 units belong here, not in `market_rate_mf`, because they carry residential financing and the same owner profile; they add landlord-fatigue signals (Section 2).

Route out when: `units >= 5` (-> `market_rate_mf`); the parcel carries a regulatory agreement, HAP contract or LIHTC allocation (-> `affordable_regulated`, even at 1-4 units); the owner is a lender/REO vesting or a trustee's deed has recorded (-> `lender_counterparty` track); an active listing exists (-> `excluded`, `on_market=true`).

Trigger vocabulary (whole words): SFR, single-family, house, duplex, triplex, fourplex, condo, probate, pre-foreclosure, NOD, absentee, tired landlord, wholesale, fix and flip, BRRRR.

Jurisdiction split that matters: Oregon counties (Multnomah, Washington, Clackamas) run the ORS 86 non-judicial clock with a recorded NOD; Clark County WA runs RCW 61.24 where the first recorded instrument is the Notice of Trustee's Sale. Never assume an Oregon-style NOD feed in Vancouver.

## 2. Signal catalog

Access tiers: free-public / free-registration / paid / manual. `verified_live` is false for every source except the ORS 86, ORS 646, RCW 61.24 and RCW 84.64 statute mirrors that were read in full; `smoke_test_sources.py` flips it when a URL and its headers are confirmed.

| signal | event_type | family | source (adapter) | fields | access | URL | verified_live | window | basis | points rule |
|---|---|---|---|---|---|---|---|---|---|---|
| Oregon Notice of Default and Election to Sell recorded | NOD_RECORDED | HARD_DISTRESS | MultcoRecords index export (`normalize_recorder_index.py`, canonical columns); Washington Co. Recording; Clackamas Clerk | doc type, recording date, instrument no., grantor (owner), beneficiary, trustee, referenced trust deed | free-public index; images $3.75/doc Multnomah (fee per county snippet; unverified; stored in market-params.json `multco_recorder_image_fee` with verify: true) | https://multcorecords.com/ | false | day 0 = recording; sale >= day 120; cure = sale - 5 d; postponements up to 180 d | RECORDED | time_pressure: 0-30 d 15; 31-90 d 22; 91 d to cure 25; postponed 18 |
| Appointment of Successor Trustee (pre-NOD) | SUCCESSOR_TRUSTEE_APPOINTED | HARD_DISTRESS | recorder index | doc type, grantor, new trustee (Clear Recon, Quality Loan Service, Aztec, ZBS) | free-public | https://multcorecords.com/ | false | 0-45 d before NOD | RECORDED | time_pressure 11; +5 stacking when both pre-NOD instruments present |
| OFAP Certificate of Compliance / exemption affidavit (pre-NOD) | OFAP_CERT_RECORDED | HARD_DISTRESS | recorder index | doc type, grantor, beneficiary; absence with NOD implies <= 30 foreclosures/yr beneficiary (ORS 86.726(1)(b)) | free-public | https://multcorecords.com/ | false | 0-45 d before NOD | RECORDED | time_pressure 11 |
| Washington Notice of Trustee's Sale recorded | NOTS_RECORDED | HARD_DISTRESS | Clark County Auditor records; WA Digital Archives (`recorder_wa`) | grantor, trustee, sale date, arrears | free-public (images free) | https://clark.wa.gov/auditor/recording ; https://digitalarchives.wa.gov | false | sale >= 90 d (120 if RCW 61.24.031 letter); cure = sale - 11 d; continuances up to 120 d | RECORDED | time_pressure 24 |
| Trustee's sale publication / postponement | NOD_RECORDED (detail publication_running / postponed) | HARD_DISTRESS | PublicNoticeOregon; trustee sites (QLS, Clear Recon, Aztec, auction.com) | sale date, sum owing (ORS 86.771(5)), trustee contact | free-public | https://www.publicnoticeoregon.com/ | false | 4 weekly runs ending > 20 d before sale | RECORDED | time_pressure 25 during publication |
| Trustee's Deed / Notice of Rescission (exit) | TRUSTEES_DEED / NOD_RESCISSION | HARD_DISTRESS (ROUTING / SUPPRESSION) | recorder index | doc type, grantee | free-public | https://multcorecords.com/ | false | n/a | RECORDED | Trustee's Deed -> route lender_counterparty, score 0; Rescission -> remove NOD |
| Probate filing / small-estate affidavit | PROBATE_FILED | OWNERSHIP | OJD Smart Search (`court_or`); OJCIN daily case index (paid) | case no., county, decedent, PR, attorney, filing date | free-registration (reCAPTCHA); OJCIN $170 setup + $27/mo report pack (fee snippets; unverified) | https://webportal.courts.oregon.gov/portal/Home/Dashboard/29 | false | soft outreach 60-120 d after filing; heirs sell 6-18 mo | RECORDED | owner_profile 13; time_pressure 7 alone; +5 stacking with NOD |
| HECM reverse mortgage on record | HECM_ON_RECORD | OWNERSHIP | recorder index (2nd trust deed to Secretary of HUD; "Home Equity Conversion") | beneficiary, recording date, principal limit | free-public | https://multcorecords.com/ | false | ongoing; urgent on probate or HECM NOD | RECORDED | owner_profile 10; equity caution (balance grows) |
| Oregon DOR senior/disabled deferral lien | DOR_DEFERRAL_LIEN | OWNERSHIP | recorder index; tax statement | DOR lien, deferral status | free-public | https://www.oregon.gov/dor/programs/property/Pages/deferral.aspx | false | ongoing; urgent on probate | RECORDED | owner_profile 10; add deferred balance to payoff |
| Property-tax delinquency (1-2 years) | TAX_DELINQUENT_YEARS | TAX_LIEN | MultcoPropTax (guest login, per account); WashCo A&T; Clackamas AscendWeb; DART delinquency extract (fee) | delinquent roll years, balance, payment history | free-registration (per account); paid bulk | https://multcoproptax.com/ | false | delinquent May 16 after tax year | RECORDED | time_pressure 1 yr 6 / 2 yr 12; stacking input |
| ORS 312 foreclosure list (3+ years) / redemption | TAX_FORECLOSURE_LIST / TAX_REDEMPTION_END | TAX_LIEN | DART foreclosure list (records request); Daily Journal of Commerce August publication; Clark Treasurer RCW 84.64 | owner, account, years, amount, judgment date | manual / free-public publication | https://multco.us/dart/property-tax-foreclosure | false | list July, publication August, judgment, 2-year redemption | RECORDED / DERIVED | time_pressure list 20; redemption period 25 |
| Absentee ownership with distance tiers | ABSENTEE_TIER | OWNERSHIP | SAIL taxlots export (`normalize_assessor_taxlots.py`); Metro RLIS taxlots; Clark GIS | NAME, NAME2, ADDR1, CITY, STATE, ZIP vs SITUSADDR; DEED_DATE | free-public | https://services5.arcgis.com/x7DNZL1YqNQVNykA/ArcGIS/rest/services/Multnomah_County_Taxlot_Parcels/FeatureServer/0 ; https://rlisdiscovery.oregonmetro.gov/ | false | refresh quarterly | RECORDED | owner_profile out-of-state 10 / in-state 7 / local 4 / occupant 2; never standalone |
| Long tenure and Measure 50 basis lock | HOLD_YEARS | OWNERSHIP | SAIL / RLIS taxlots | DEED_DATE, SALE_DATE, ROLLM50, ROLLLAND, ROLLIMP | free-public | as above | false | ongoing | RECORDED | tenure_basis_lock > 20 y or AV/RMV < 0.45 = 10; 10-20 y 7; 5-10 y 4; < 5 y 1 |
| Code enforcement: dangerous building, housing, derelict, empty-home | DANGEROUS_BUILDING / CODE_CASE_OPEN | PHYSICAL | Portland BDS open-case lists (`code_portland`); PortlandMaps case history (API key free); Gresham rental inspection records (public records) | case type, address, status, open date | free-public / manual | https://www.portland.gov/bds/property-compliance-services-and-inspections/open-code-enforcement-cases ; https://www.portlandmaps.com/ | false | open 0-6 mo active; > 6 mo escalating fees | REPORTED | condition_vacancy dangerous 10; housing 7; nuisance 4 |
| Vacancy (USPS vacant / no-stat via licensed vendor; returned mail) | (signal `usps_vacant`, `returned_mail_or_no_stat`) | PHYSICAL | PropStream / BatchData / PropertyRadar DSF2 flags; own returned mail; HUD USPS tract data for prioritization only | vacant flag, no-stat flag, duration | paid (vendor); HUD tract file restricted to governments/nonprofits | https://www.huduser.gov/portal/datasets/usps.html | false | monthly/quarterly | REPORTED | condition_vacancy USPS vacant 8; no-stat/returned 5 |
| Judgment, mechanics, HOA, IRS/state tax liens | JUDGMENT_LIEN / MECHANICS_LIEN | TAX_LIEN | recorder index by owner name; OJCIN judgment index; OJD civil (HOA plaintiff) | doc type, claimant, amount, date | free-public / paid | https://multcorecords.com/ | false | HOA judicial foreclosure 6-12 mo to sheriff sale; 180-d redemption | RECORDED | stacking input (+1 family, cap 2); subtract from equity; judicial complaint -> time_pressure 15 |
| HOA / private-lender judicial foreclosure complaint | JUDICIAL_FORECLOSURE_FILED | HARD_DISTRESS | OJD Smart Search civil | plaintiff, defendant, filing date | free-registration | https://webportal.courts.oregon.gov/portal/Home/Dashboard/29 | false | 6-12 mo to judgment | RECORDED | time_pressure 15 |
| Divorce (dissolution) filing | DISSOLUTION_FILED (detail domestic_relations) | OWNERSHIP | OJD Smart Search domestic relations | parties, filing date | free-registration | as above | false | 3-12 mo after filing | RECORDED | owner_profile 6 |
| Bankruptcy filed / Chapter 13 dismissed | BANKRUPTCY_FILED / CH13_DISMISSED | HARD_DISTRESS (ROUTING) | PACER District of Oregon; CourtListener RECAP (free tier) | debtor, chapter, status, schedules | paid ($0.10/page) / free | https://www.orb.uscourts.gov/ ; https://www.courtlistener.com/recap/ | false | dismissal -> foreclosure resumes | RECORDED | active -> counsel_only gate; dismissed Ch.13 with prior NOD -> time_pressure 22 |
| FED (eviction) filing cluster on 2-4 units | (signal `fed_filings_12mo`) | OWNERSHIP | OJD Smart Search landlord/tenant, plaintiff = owner/LLC | plaintiff, case count, dates | free-registration | as above | false | 2+ in 12 months | RECORDED | owner_profile 10 |
| Residential Infill Project upzoning eligibility (upside tag) | n/a (tag `rip_eligible`) | n/a | PortlandMaps zoning (R2.5/R5/R7), lot size | zoning, lot sqft | free-public | https://www.portlandmaps.com/ | false | static | REPORTED | no score; `upside` tag on card |
| Owner-entity status for LLC-held 2-4 units | ENTITY_ADMIN_DISSOLVED | OWNERSHIP | Oregon SOS Business Registry | status, managers/members, registered agent | free-public | https://sos.oregon.gov/business/pages/find.aspx | false | 45 d after missed annual report | RECORDED | stacking input; decision-maker chain |
| Trustee sale postings (confirm live) | NOD_RECORDED detail | HARD_DISTRESS | Quality Loan Service, Clear Recon Corp, Aztec, auction.com | TS number, address, sale date, postponements, opening bid | free-public | https://www.qualityloan.com/ ; https://www.clearreconcorp.com/ | false | weekly | REPORTED | confirms lead still live |

Vendor turnkey alternative for the whole class: PropStream (~$99/mo, unverified) or PropertyRadar (OR/WA recorder-based NOD/NOTS tracking) when the user does not want to run recorder pulls; PropertyRadar shows Oregon only as auction records because the NOD and notice of sale are one instrument.

## 3. Event derivation rules

```
Oregon (ORS 86, post-2013 numbering):
  NOD_RECORDED.event_date      = recording date
  TRUSTEE_SALE_EARLIEST        = NOD + 120 d                     (DERIVED; 86.764)
  publication window           = sale - ~48 d .. sale - 20 d     (86.774)
  CURE_DEADLINE                = sale_date - 5 d                 (DERIVED; 86.778) ; use stated sale date from Notice of Sale when known
  postponement                 = up to 180 d total               (86.782) ; detail = postponed
  NOD_RESCISSION               -> retire NOD_RECORDED (status RETIRED)
  TRUSTEES_DEED                -> route lender_counterparty; owner outreach ends

Washington (RCW 61.24):
  NOTS_RECORDED.event_date     = recording date
  TRUSTEE_SALE_EARLIEST        = NOTS + 90 d (120 d when a 61.24.031 pre-NOD letter applied, i.e. owner-occupied)
  CURE_DEADLINE                = sale_date - 11 d                (61.24.090)
  continuance                  = up to 120 d                     (61.24.040(10); the 2025 RCW mirror places the 120-day continuance rule in subsection (10))

Tax:
  TAX_DELINQUENT_YEARS.value   = count of distinct delinquent roll years (delinquent May 16 after the tax year)
  TAX_FORECLOSURE_LIST         = appears on the July/August ORS 312 list (3 full years)      ; WA: RCW 84.64 certificate of delinquency after 3 years
  TAX_REDEMPTION_END           = judgment date + 2 y             (DERIVED)

Ownership:
  HOLD_YEARS.value             = (as_of - DEED_DATE) / 365.25 ; DEPRECIATION_EXHAUSTED when >= 27.5
  ABSENTEE_TIER.value          = occupant (mailing == situs after USPS normalization) | local (same CBSA) | in_state | out_of_state | far (> 500 mi)
  av_rmv_ratio                 = ROLLM50 / (ROLLLAND + ROLLIMP)
  PROBATE_FILED                = filing date; detail = PR name when on docket
  HECM_ON_RECORD               = recording date of HUD second trust deed
```

Validation: NOD date must be >= trust-deed recording date; sale dates must be >= NOD + 120 d (OR) or NOTS + 90 d (WA), otherwise `Verify — Conflicting Sources`.

## 4. Valuation and capital-stack proxy

Value: `RMV x neighborhood_sales_ratio` (`value_source = rmv_calibrated`) or an AVM (`avm:<vendor>`). Never Assessed Value in Oregon (Measure 50: AV is the lesser of MAV, growing max 3%/yr from a 1995-96 base, and RMV; AV is commonly 50-55% of market). A low AV/RMV ratio is a tenure signal, not a value input.

Liens: amortize each recorded trust deed from stated principal at the PMMS rate for its month (`balance_basis = ESTIMATED`); HELOC at stated maximum; HECM at principal limit (grows); add DOR deferral balance, judgments, HOA/mechanics liens. A stated sum owing in a Notice of Sale (ORS 86.771(5)) overrides (`RECORDED`).

`equity_cushion_pct = (est_value - total_liens) / est_value`. Equity bands in Section 5. For 2-4 units the income proxy (`noi_proxy` with ZIP rents) is a cross-check only.

## 5. Scoring rubric

Canonical: `scoring/sfr_small_res.json`. Factor points x basis multiplier of the governing event (time_pressure and equity only), then shared multipliers, caps and tiers (`shared_adjustments.json`).

| factor | weight | bands (take max unless noted) |
|---|---|---|
| Time pressure | 25 | OR NOD 0-30 d 15; 31-90 d 22; 91 d to cure deadline or publication running 25; postponed 18; WA NOTS 24; pre-NOD instruments 11; tax foreclosure list 20; redemption period 25; judicial complaint 15; dismissed Ch.13 with prior NOD 22; probate alone 7 |
| Signal stacking | 20 | 2 independent families 10; 3 = 15; 4+ = 20; +5 NOD + probate; +5 both pre-NOD instruments; assessor facts count once; cap 20 |
| Equity | 20 | cushion > 50% 20; 35-50 15; 20-35 10; 10-20 5; < 10 0 (RMV x sales ratio minus liens; sum owing overrides) |
| Owner profile | 15 | estate/PR 13; HECM 10; DOR deferral 10; out-of-state 10; in-state non-metro 7; local absentee 4; trust 6; 2+ FEDs/12 mo on 2-4 units 10; dissolution 6; occupant 2 |
| Condition / vacancy | 10 | dangerous building 10; USPS vacant 8; housing case 7; no-stat/returned mail 5; nuisance 4 |
| Tenure / basis lock | 10 | > 20 y or AV/RMV < 0.45 = 10; 10-20 y 7; 5-10 y 4; < 5 y 1 |

Hard filters: active listing; rescission/reconveyance; institutional or REO owner; DNC/litigator flags (phone channel); active bankruptcy (counsel only). Tiers: A >= 70, B 50-69, C 30-49, WATCH < 30 with a dated event. Absentee, tenure and equity never make a lead on their own.

## 6. Owner archetypes and outreach angles

| owner_type | angle | template | gates |
|---|---|---|---|
| individual_occupant / individual_absentee | convenience, certainty, as-is; tax strategy for long holds | `individual_or_trust` | dnc_scrub; equity_purchaser_rules if in foreclosure; wholesaler_registration if buyer_profile wholesaler |
| trust_estate (probate) | one buyer, one closing; stepped-up basis | `estate` | probate_cooling |
| single_asset_llc (2-4 unit landlord) | regulatory fatigue (rent cap, relocation, FAIR), buy with tenants in place | `single_asset_llc` | dnc_scrub; fair_housing_tenant_data |
| lender_reo_receiver (post trustee's deed) | REO track | `receiver_lender` | none for owner; owner_outreach false |

Full archetype table and resolution chain: `decision-maker-enrichment.md`.

## 7. Lead-card additions

Add to the standard card: `Stage` (pre-NOD watch / NOD day n / publication / postponed / redemption), `Sale date` and `Cure deadline` with basis, `Trustee` and trustee site, `Liens` list with basis per lien, `AV/RMV ratio`, `Hold years`, `Absentee tier`, `RIP upside` tag, `Vendor flags` (DNC, litigator, vacant) verbatim.

## 8. Pro tips and timing

- **The NOD is the last recorded step, not the first.** Appointment of Successor Trustee and the OFAP Certificate of Compliance land days to weeks before it; watching those two document types is how you reach the owner before everyone keyed on NODs.
- **Oregon leads have a 120-day floor; Washington leads do not.** Clark County surfaces at the Notice of Trustee's Sale, 90-120 days before sale, with cure ending 11 days out. Treat every WA lead as late-stage.
- **Publication is a confirmation, not a discovery tool.** By the time a trustee's notice runs, the cure deadline is 3-5 weeks away. Use PublicNoticeOregon to read the stated sum owing and to catch NODs you missed.
- **Private-lender NODs look different.** No OFAP certificate means the beneficiary does 30 or fewer foreclosures a year; expect faster, less flexible behavior.
- **Probate is a letter campaign, not a call campaign.** First touch 60-120 days after filing, addressed to the PR or counsel, never price-first. Combined with an NOD or HECM it is the highest-converting SFR pattern.
- **Measure 50 makes AV useless as value and useful as tenure.** A ROLLM50 / RMV ratio under 0.45 means the owner has held since before 1997 or has had no exception events: older owner, little debt, basis lock.
- **Tax delinquency is slow and loud.** Year 2 is the best window: stress is visible, the county is not yet involved. The ORS 312 list in July/August and the 2-year redemption period are the last windows.
- **2-4 unit landlords sell on regulation, not on price.** Rent cap (9.5% in 2026; `market-params.json`, verify), Portland relocation assistance ($2,900-$4,500/unit on a 10%+ increase or no-cause termination; amounts per PHB snippet, verify), FAIR screening and deposit rules, Schedule R registration. Two or more FED filings in a year is the tell.
- **Portland RIP upzoning is upside, not motivation.** Tag it; do not score it.

## 9. Refresh cadence

| feed | cadence | why |
|---|---|---|
| recorder document types (NOD, Successor Trustee, OFAP cert, Trustee's Deed, Rescission, NOTS) | daily or weekly (PRAS alerts are daily in Multnomah) | 120-day clock |
| OJD probate, FED, dissolution, civil | weekly | filing volume |
| PACER / CourtListener | weekly | stay and dismissal status |
| assessor roll (SAIL / RLIS) | quarterly (Multnomah updates weekly; Washington/Clackamas quarterly) | absentee, tenure, RMV |
| tax payment history | semiannual (after May 16 and Nov 15) plus July/August list | delinquency years |
| BDS open cases | monthly | escalating fees |
| vendor vacancy flags | monthly/quarterly | USPS DSF2 cycle |
| trustee sites / PublicNoticeOregon | weekly | postponements |

## 10. Known gaps

- Every source except the four statute mirrors is `verified_live=false`; county recorder index URLs for Washington County (OR) and Clackamas were not confirmed; Clark County Auditor search URL unconfirmed.
- Portland code-enforcement bulk layer: none found in the PortlandMaps service catalog; cases are address-level lookups or the BDS open-case lists; Enhanced Rental Inspections enrollment requires a public-records request. Suburban code portals (Gresham, Beaverton, Hillsboro, Vancouver) not verified.
- USPS vacancy: HUD's tract file is licensed only to governments and nonprofits; address-level flags require a licensed vendor. Portland Water Bureau shutoffs are not public.
- AVM access: Zillow/Redfin have no open API; default to RMV x sales ratio and record the AVM vendor when one is used.
- OJD Smart Search has a reCAPTCHA and terms that may restrict automation; OJCIN base monthly fee varies by account type (only the $170 setup and $27/month report package were visible).
- Skip-trace pricing unverified (BatchData ~$0.01/record API per one integration vs ~$0.15-0.25 retail; REISkip ~$0.15; PropStream ~$99/month).
- Legal overlays not fully verified: HB 4058 fee and cancellation period; ORS 646A.702 and RCW 61.34 (equity-purchaser / distressed-property rules) must be reviewed by counsel before pre-foreclosure outreach language is finalized; TCPA one-to-one consent status.
- Whether a buy-side offer is a "telephone solicitation" is unsettled; scrub DNC regardless.
