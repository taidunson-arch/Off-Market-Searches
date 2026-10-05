# Legal Timelines: Oregon and Clark County, Washington

Statutory clocks the event-derivation rules encode. Section numbers for ORS 86 use the post-2013 renumbering (the older 86.735-86.797 range should not be cited). Verification: ORS 86, ORS 646, ORS 87, ORS 90.324, ORS 100.450, ORS 18.964, RCW 61.24 and RCW 84.64 were read from statute mirrors whose file header reads "2025 EDITION" (ORS) or the current RCW (wa-law.org mirror); spot-check against the official sites, which were egress-blocked in this build. Confirmed from those mirrors: ORS 86.705 (residential trust deed), 86.726(1)(b) (beneficiaries that commenced more than 30 residential foreclosures in the prior year must hold the OFAP conference; 30 or fewer are exempt), 86.752(3)-(4), 86.764 (120 days), 86.771(5) (sum owing), 86.774 (four successive weeks, last publication more than 20 days before sale), 86.778 (cure until five days before sale; $1,000 residential fee cap), 86.782(2)(a) (postponements totalling not more than 180 days), 86.797(2), 86.155(1)(b) (line-of-credit legend with maximum principal and term or maturity date), 646.561(4)(a)(B) (text messages, 2025 c.580), 646.569, 646.572(1)(b), 646.642 ($25,000 per violation), 87.035 (75 days), 87.055 (120 days / two years), 87.057 (10 days), 100.450 (90-day lender notice), 18.964 (180-day redemption), 90.324 (lesser of 10% or 7% + CPI; 6% for manufactured-dwelling parks with more than 30 spaces), RCW 61.24.031 (30/90 days), 61.24.040(1)(a) (90/120 days), 61.24.040(10) (120-day continuance), 61.24.090 (eleventh day), 84.64.050 (three years). NOT readable in this build and therefore unverified: ORS 312, 456, 63, 70, 432, 646A, OAR 813-115, 7 CFR 3560, and every fee figure; those rows say so. Nothing here is legal advice; the equity-purchaser and preservation-law items in particular need counsel before outreach language is finalized.

## Contents

1. Oregon trust-deed foreclosure (ORS 86) — non-judicial
2. Oregon judicial foreclosure, receivership, liens
3. Oregon property-tax foreclosure (ORS 312)
4. Washington deeds of trust and tax foreclosure (RCW 61.24, 84.64)
5. Oregon publicly supported housing preservation (ORS 456.250-.265, OAR 813-115, SB 973)
6. LIHTC federal mechanics (IRC 42)
7. Outreach compliance (ORS 646, HB 4058, ORS 646A.702, RCW 61.34)
8. Oregon Measure 50
9. Rent and tenant regulation that drives motivation

---

## 1. Oregon trust-deed foreclosure (ORS 86) — non-judicial

| step | section | rule | event mapping |
|---|---|---|---|
| Resolution conference | 86.726 | Oregon Foreclosure Avoidance Program conference before NOD for residential trust deeds; beneficiaries doing 30 or fewer residential foreclosures a year are exempt (86.726(1)(b)) and file an exemption affidavit | OFAP_CERT_RECORDED (certificate or exemption affidavit) |
| Certificate of Compliance | 86.736; 86.752(4) | certificate (or exemption affidavit) must be recorded with or before the NOD | pre-NOD leading indicator |
| Appointment of Successor Trustee | practice | lender substitutes a foreclosure trustee shortly before the NOD | SUCCESSOR_TRUSTEE_APPOINTED |
| Notice of Default and Election to Sell recorded | 86.752(3) | combined instrument recorded in the county clerk's office; there is no separate earlier pre-foreclosure recording and no lis pendens in non-judicial practice | NOD_RECORDED (day 0) |
| Notice of sale served / mailed | 86.764 | at least 120 days before the sale | TRUSTEE_SALE_EARLIEST = NOD + 120 d |
| Contents of notice | 86.771 | includes the sum owing (86.771(5)) and the sale date, time, place | sum owing overrides balance estimate |
| Publication | 86.774 | once a week for four successive weeks; last publication more than 20 days before sale | publication window ~ sale - 48 d .. sale - 20 d |
| Cure / reinstatement | 86.778 | until 5 days before the sale (residential reinstatement fee cap $1,000) | CURE_DEADLINE = sale - 5 d |
| Sale and postponement | 86.782 | sale between 9am and 4pm in the county; postponements up to 180 days total | detail postponed |
| Deficiency | 86.797 | no deficiency after a trustee's sale; no deficiency after judicial foreclosure of a residential trust deed; commercial lenders may still pursue deficiency/guarantors through judicial foreclosure | explains why apartment lenders file under ORS 88 |
| Line-of-credit trust deed legend | 86.155 | maximum principal and maturity date printed on page one | RECORDED maturity for LOC instruments |

Whether an apartment loan is a "residential trust deed" turns on ORS 86.705 definitions (owner occupancy); treat multifamily investor loans as commercial for deficiency analysis and confirm with counsel.

## 2. Oregon judicial foreclosure, receivership, liens

| instrument | section | timing | event mapping |
|---|---|---|---|
| Judicial foreclosure complaint | ORS ch. 88 | filing to judgment 6-12 months; sheriff's sale 4+ weeks after writ; 180-day redemption after sale for judicial foreclosures | JUDICIAL_FORECLOSURE_FILED |
| Lis pendens / notice of pendency | ORS 93.740 | recorded when a suit affects title | LIS_PENDENS |
| Receivership | ORS ch. 37 (effective 2018-01-01; UCRERA-modeled): 37.060 grounds incl. real property in default; 37.110/.120 receiver powers to operate, lease, sell with court approval | receivers stabilize 3-9 months before marketing | RECEIVER_APPOINTED (route lender_counterparty) |
| Construction lien | ORS 87.035 (record within 75 days of last labor/materials); 87.055 (suit within 120 days); 87.057 (10-day notice of intent); lien cannot continue beyond 2 years | outreach days 15-120 after recording | MECHANICS_LIEN |
| Condominium assessment lien | ORS 100.450 | association lien; may prime first mortgage if lender fails to act within 90 days after formal notice | JUDGMENT_LIEN (detail hoa) |
| Partition | ORS 105 | 12-24 months | PARTITION_FILED |
| Entity status | ORS 63.787 (LLC annual report lists managers or at least one member) and ORS 70.610 (LP annual report lists every general partner) per prior knowledge; verify current ORS 63.787 / 70.610 text and the SOS annual-report form, since contact grade A for LIHTC partnerships rests on the LP rule; administrative dissolution ~45 days after a missed annual report; reinstatement within 5 years (verify) | | ENTITY_ADMIN_DISSOLVED, MANAGER_CHANGE |
| Death records | ORS chapter 432 (ORS 432.350 is believed to be the operative section: death records become public 50 years after the date of death; verify section number, no ORS 432 mirror was readable) | death certificates restricted 50 years | principal death via probate, obituaries, SOS changes |

## 3. Oregon property-tax foreclosure (ORS 312)

| step | rule | event mapping |
|---|---|---|
| Delinquency | taxes delinquent May 16 after the tax year (installments Nov 15 / Feb 15 / May 15) | TAX_DELINQUENT_YEARS |
| Foreclosure list | property becomes subject to foreclosure once 3 full years have elapsed from the earliest delinquency (ORS 312.010; consistent with prior knowledge, text not read); county compiles list in July, publishes in a general-circulation newspaper (Multnomah: Daily Journal of Commerce) in August with the application for judgment (ORS 312.040-312.050; verify, no ORS 312 mirror readable); one omnibus circuit-court case | TAX_FORECLOSURE_LIST |
| Redemption | 2 years after judgment (ORS 312.120; verify); redemption-expiration notices published in January | TAX_REDEMPTION_END = judgment + 2 y |
| Tax Title | foreclosed properties pass to the county Tax Title program | REO track |
| Deferral | Oregon DOR senior/disabled deferral lien (ORS 311.666 et seq.); counties pay deferred taxes to DOR on foreclosure (ORS 311.694) | DOR_DEFERRAL_LIEN |
| Utility certification | delinquent sewer/stormwater certified to the tax roll (ORS 454.225; owner notice ORS 91.255) | UTILITY_LIEN_CERTIFIED |

## 4. Washington deeds of trust and tax foreclosure (RCW 61.24, 84.64) — Clark County

| step | section | rule | event mapping |
|---|---|---|---|
| Pre-foreclosure contact letter | 61.24.031 | owner-occupied: NOD not before 30 days after the letter (90 if the borrower responds); mediation referral under the Foreclosure Fairness Act (61.24.163) | not recorded |
| Notice of Default | 61.24.030 | mailed/posted, not recorded | not recorded |
| Notice of Trustee's Sale recorded | 61.24.040(1)(a) | recorded with the county auditor at least 90 days before the sale (120 if a .031 letter was required); mailed to borrower, successors and occupants of < 5 unit buildings | NOTS_RECORDED (day 0); TRUSTEE_SALE_EARLIEST = NOTS + 90/120 d |
| Cure | 61.24.090 | until the 11th day before the sale | CURE_DEADLINE = sale - 11 d |
| Continuance | 61.24.040(10) | sale may be continued for a period or periods not exceeding a total of 120 days (the current RCW places this in subsection (10), not (6)) | detail continued |
| Tax foreclosure | 84.64.050 (certificate of delinquency after 3 years); 84.64.080 (judicial judgment and sale, electronic auction allowed) | | TAX_FORECLOSURE_LIST |
| Distressed Property Conveyances Act | RCW 61.34 | duties and contract rules for distressed-home consultants and purchasers; leasebacks | compliance gate equity_purchaser_rules |

Washington leads therefore surface 90-120 days before sale with no earlier public NOD; Clark County is also outside Oregon's rent cap and Portland's relocation/FAIR rules (Washington enacted a 2025 rent-cap law with different terms; verify).

## 5. Oregon publicly supported housing preservation (PuSH)

| element | source | rule | status |
|---|---|---|---|
| Definition | ORS 456.250 | publicly supported housing = multifamily rental of 5+ units with a HUD/USDA/OHCS rent-assistance contract containing an affordability restriction, or other government assistance with an affordability restriction identified by OHCS rule (OAR 813-115); qualified purchaser = affected local government, OHCS, or an OHCS designee | snippets; verify |
| Owner notices | ORS 456.260; OAR 813-115-0030/-0035 | first notice of intent to OHCS and each local government by certified mail 36-30 months before expiration/termination/withdrawal; second notice 30-24 months; withdrawal not sooner than 30 months after notices | OAR 813-115 snippets only; the 2017 statute cited "2 years"; ORS 456.260 text (post-SB 973) not read in this build. `PRESERVATION_NOTICE_WINDOW` is therefore DERIVED (statute text unverified); confirm before quoting a window to a counterparty |
| Tenant notice | ORS 456.259; SB 973 (2025) | 12-14 months before withdrawal, plain language, posted; SB 973 raises tenant notice to 30 months minimum in Oregon's five most common languages and adds applicant/new-tenant disclosure, operative 2026-01-01 for restrictions ending on/after 2028-07-01 | snippets; verify |
| Designee and recorded ROFR | ORS 456.262 | OHCS may appoint a designee as purchaser after consulting the local government; qualified purchaser may record a Notice of Right of First Refusal in county real-property records | ROFR_RECORDED |
| Matching right | ORS 456.263 | before selling to a non-qualified third party the owner mails the third-party offer (or its terms); qualified purchasers have 30 days to deliver a matching offer; the owner must accept the first matching offer | compliance gate preservation_law |
| ROFR duration | 456.262 / 456.263 | appears as 24 months after withdrawal (designee agreement) and 36 months after termination date in different snippets | unresolved; verify |
| Records | OAR 813-115-0060 | owner must provide property records within 30 days of a written request | |
| Sanctions | ORS 456.265 | local-government penalties for failure to give notice; mandatory affordability extension for non-compliance | snippets |
| History | 2017 HB 2002 (original); 2019 HB 2002 (all PSH, 24-30 month notice, recorded ROFR); 2021 HB 2095; 2023 HB 3042; 2025 SB 973 | | |
| Public artifacts | OHCS 10-Year Expiration Forecast dataset with preservation status; PuSH dashboard; no discrete notices log (records request to PuSH-CP Program Manager) | | |

Model: 30 months is the floor between notice and withdrawal, so conversion value cannot be realized sooner. Position as a designee or local-government partner to convert the ROFR from a threat into an advantage.

## 6. LIHTC federal mechanics (IRC 42)

| element | section | rule | event mapping |
|---|---|---|---|
| Compliance period | 42(i)(1) | 15 years from the first year of the credit period; Year 15 = Dec 31 of (YR_PIS + 14), or +15 if the owner elected to begin the credit period the year after placed in service | LIHTC_COMPLIANCE_END (flag +15 election possible) |
| Extended use | 42(h)(6) | agreement required for 1990+ allocations; minimum 15 years beyond the compliance period (30 total); Oregon REUAs require >= 15 years beyond compliance; LIFT-paired 9% deals 60 years | LIHTC_EXTENDED_USE_END |
| Qualified contract | 42(h)(6)(E)(i)(II), (F) | owner may request after the 14th year unless waived; agency has 1 year to present a QC; failure ends extended use | QC_ELIGIBILITY |
| Decontrol | 42(h)(6)(E)(ii) | 3 years: no eviction without good cause and no non-§42 rent increases for existing tenants | compliance gate lihtc_tenant_protections |
| ROFR | 42(i)(7) | qualified nonprofit, tenants/cooperative or government agency may hold a ROFR exercisable after the compliance period at minimum purchase price = outstanding debt (excluding debt incurred within 5 years) + exit taxes; SunAmerica Housing Fund 1050 v. Pathway of Pontiac (6th Cir. 2022): triggered by a third-party offer without investor consent; aggregator LPs contesting exits is an active litigation trend | routing partnership_preservation for nonprofit GP |
| QC policy by state | Treasury Dec 2024 (page not fetched; figures unverified): 14 agencies reportedly prohibit QC requests as an allocation condition; most others require or incentivize waivers (NCSHA 2017); ~115,000 units lost nationally. SunAmerica Housing Fund 1050 v. Pathway of Pontiac, Inc., 33 F.4th 872 (6th Cir. 2022) | see `sources/federal/qc-policy-by-state.md` | |

## 7. Outreach compliance

| law | rule | status |
|---|---|---|
| ORS 646.561-.574 (telephone solicitation) | 646.561 "telephone solicitation" covers calls and text messages encouraging purchase of real estate (amended 2025 c.580); 646.569 prohibits soliciting numbers on the designated federal registry; 646.572 designates the National DNC Registry as Oregon's list; violation is an unlawful practice under 646.608 (penalties under 646.642 up to $25,000 per willful violation, from knowledge) | mirror read; penalty amount verify |
| TCPA (47 U.S.C. 227) | prior express written consent for autodialed/prerecorded/AI-voice calls and texts to cells; 8am-9pm; $500-$1,500 per violation; FCC one-to-one consent rule vacated Jan 2025, consent requirement stands | knowledge; verify |
| HB 4058 (2024) residential property wholesaling | wholesalers register with the Oregon Real Estate Agency from 2025-01-01; written disclosures; seller cancellation right; up to 364 days / $6,250 plus civil penalties; principals exempt | chaptered (digest via mirror); fee (~$300/yr), 3-business-day cancellation and July 2025 phase-in from a third-party summary; verify |
| ORS 646A.702 et seq. (Mortgage Rescue Fraud Protection Act) | equity-purchaser contract contents, cancellation rights, leaseback restrictions for owners in foreclosure | not re-read; counsel |
| RCW 61.34 (Distressed Property Conveyances Act) | Washington analogue; distressed-home consultant duties | not re-read; counsel |
| Fair housing (FHA; ORS 659A) | tenant-related records used only for owner-motivation assessment | knowledge |
| 11 U.S.C. 362 | automatic stay; contact through counsel/trustee | knowledge |

## 8. Oregon Measure 50

Real Market Value (ORS 308.205) is the assessor's January 1 estimate; Maximum Assessed Value started at 1995-96 RMV x 0.90 and grows at most 3% a year (exception events reset it); Assessed Value is the lesser of MAV and RMV and is commonly ~50-55% of market in Multnomah. Consequences for this skill: never use AV for value, equity or LTV; use RMV only as a +/-25% sanity band; use the AV/RMV ratio as a tenure/basis-lock signal (ratio < 0.45 implies pre-1997 ownership or no exception events). Studies show wide horizontal inequity in Oregon assessed-to-market ratios.

## 9. Rent and tenant regulation that drives motivation

| rule | source | 2026 value | use |
|---|---|---|---|
| Statewide rent cap | ORS 90.324 (SB 608 2019, SB 611 2023); OEA publishes by Sept 30 | 9.5% (lesser of 10% or 7% + CPI); 6% for manufactured-dwelling parks > 30 spaces (HB 3054 2025); buildings < 15 years from first CO exempt | rent-trap metric; years_to_market = ln(market/inplace)/ln(1+cap) |
| Portland relocation assistance | PCC 30.01.085 (amounts per PHB snippet; verify, portland.gov not fetched) | studio/SRO $2,900; 1BR $3,300; 2BR $4,200; 3BR+ $4,500; triggered by no-cause termination, non-renewal, qualifying landlord reason, or a rent increase of 10%+ within 12 months when the tenant elects to move; payment within 31 days; penalty 3x plus fees | relocation_exposure in underwriting and motivation |
| Portland FAIR ordinances | PCC 30.01.086 (screening; $250/violation) and 30.01.087 (deposits; double deposit + fees) | effective 2020-03-01, amended 2022 | regulatory-fatigue angle |
| Portland rental registration | PCC 7.02.890 Schedule R; LIC-5.09 | $70/unit TY2025 (fee snippet; unverified; `market-params.json` verify: true); filer data confidential (ORS 314.835) | cost line only |
| Gresham rental housing program | city code | licensing + mandatory random inspections | records request signal |
| PHB enforcement | Q1 2025: 2,878 units investigated, 106 violations | | context only |
