# Class Module: Market-Rate Apartments 5+ Units (`market_rate_mf`)

Read this module only when Step 0 routes to `market_rate_mf`. Shared vocabulary is in `pipeline-contract.md`; shared math in `capital-stack-math.md`; the canonical weights are `scoring/market_rate_mf.json` (Section 5 reproduces them and must match).

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

In scope: 5+ unit apartments with no active affordability restriction, including ex-regulated assets whose restrictions have all expired (`ex_regulated` tag) and Portland Inclusionary Housing buildings (99-year covenant on a small set-aside; `IH_SET_ASIDE` program tag, scored as market-rate). Query types: `maturity` (the "loans coming due within N years" question), `distress`, or `all`.

Route out when: any active LIHTC, HAP/PRAC, HUD 236/202, USDA 515, HOME or state soft-loan regulatory agreement is present (-> `affordable_regulated`); `units <= 4` (-> `sfr_small_res`); a trustee's deed, receiver or special servicer controls the asset with no owner equity (-> `lender_counterparty` track within this class, owner outreach off); active listing (-> `excluded`).

Trigger vocabulary: apartments, multifamily, 5+ units, maturity, maturing debt, maturity wall, refi, refinance gap, DSCR, CMBS, bridge, floating, receiver, special servicing, syndicator, sponsor.

## 2. Signal catalog

A large share of US apartment debt (unverified; on the order of half to two-thirds, mostly agency MBS and FHA) carries an actual maturity date in a public or free-registration tape (HUD/FHA, Fannie DUS, Freddie K/SB, SEC-registered CMBS); the remainder (bank, credit-union, life-company, debt-fund and unsecuritized agency balance-sheet loans, which include the majority of Portland's 5-49 unit stock) has none, and the recorded trust deed is the only primary source, often without the maturity. The lender-mix percentages quoted in this file (Yardi Matrix: agency ~56%, bank 16%, HUD 10%, debt fund 6%, life co 6%, CMBS 2%) are an origination mix, not a share of outstanding balance, and are marked `verify` until an MBA debt-outstanding table is cited. All sources below are `verified_live=false` except the edgartools CMBS parser guide (fetched live).

| signal | event_type | family | source (adapter) | fields | access | URL | verified_live | window | basis | points rule |
|---|---|---|---|---|---|---|---|---|---|---|
| HUD/FHA-insured loan maturity | LOAN_MATURITY (and REFINANCE_CLOSED from Terminated) | DEBT | HUD Insured Multifamily Mortgages Active + Terminated Excel (`normalize_hud_insured.py`) | HUD Project Number, Property Name/Street/City/State/Zip, Units, Initial/Final Endorsement Date, Original Amount, First Payment Date, Maturity Date, Term, Interest Rate, UPB, Holder, Servicer, SOA code; Terminated adds Termination Date/Type | free-public | https://www.hud.gov/hud-partners/multifamily-fhasl-active | false | monthly, 1-2 month lag | RECORDED | capital_stack_timing 0-12 mo 17; 12-24 12; 24-36 7; 36-60 3; +2 prepay window (endorsement + 10y); assumable tag |
| HUD eGIS insured / assisted layers (geocoded join key) | LOAN_MATURITY (same loan), owner/agent names | DEBT | HUD ArcGIS FeatureServer (GeoJSON) | HUD_PROJECT_NUMBER, address, UNITS, SOA, ORIGINAL_MORTGAGE_AMOUNT, MATURITY_DATE, UPB, HOLDER, SERVICER, lat/long | free-public | https://services.arcgis.com/VTyQ9soqVukalItT/ArcGIS/rest/services/HUD_Insured_Multifamily_Properties/FeatureServer/0 | false | monthly | RECORDED | geography join; confirm field names from `/0?f=pjson` |
| Ginnie Mae multifamily loan-level disclosure | LOAN_MATURITY (reconcile UPB; catch new endorsements) | DEBT | bulk.ginniemae.gov mfplmon / mfpldaily (`normalize_ginnie.py`, future) | Pool ID, FHA case number, issuer, loan type, UPB, rate, Maturity Date (YYYYMMDD), property name/address (L30-L34), prepayment penalty file | free-public | https://bulk.ginniemae.gov/layout_sample.aspx | false | monthly / daily | RECORDED | join on digits-only case number; CLC->PLC = construction complete |
| Fannie Mae DUS Disclose loan/property data | LOAN_MATURITY, IO_EXPIRATION, PREPAY_WINDOW_OPEN, OCCUPANCY_DROP | DEBT / OPERATING | DUS Disclose Advanced Search export (`normalize_dus.py`, file-drop) | Loan Number, property address, units, year built, UPB, note rate, rate type, Maturity Date, amortization, IO end, prepayment provision / YM end, UW and current DSCR, LTV, occupancy, DUS lender, operating statements, affordability indicators | free-registration (search free, downloads need account) | https://mfdusdisclose.fanniemae.com/#/home | false | monthly | REPORTED | as HUD; +3 IO expiry <= 12 mo; +2 prepay open; DSCR trend feeds refi factor at x1.0 |
| Freddie Mac MSIA (K / SB / ML deals) | LOAN_MATURITY, IO_EXPIRATION, PREPAY_WINDOW_OPEN, WATCHLIST, SPECIAL_SERVICING | DEBT / OPERATING / HARD_DISTRESS | MSIA property search/download (CREFC IRP) (`normalize_msia.py`, file-drop) | Deal, Loan ID, address, units, UPB, rate, rate type (fixed / floating SOFR), index + margin, maturity, IO period, prepayment provision, open period, UW and current NOI/DSCR/debt yield, occupancy, watchlist code, special servicing status, delinquency, modifications | free-registration | https://mf.freddiemac.com/investors/data | false | monthly | REPORTED | SB-Deal hybrid ARMs: +3 floating; watchlist 7; special servicing 20 |
| SEC EDGAR 10-D / ABS-EE EX-102 (conduit CMBS) | LOAN_MATURITY, IO_EXPIRATION, PREPAY_WINDOW_OPEN, LOAN_MODIFIED, SPECIAL_SERVICING, MATURED_BALLOON, OCCUPANCY_DROP | DEBT / HARD_DISTRESS | edgartools `Filing(form='10-D').obj()` properties x loans (`cmbs_edgar_pull.py`, future) | maturityDate, interestOnlyIndicator, yieldMaintenanceEndDate, prepaymentPremiumsEndDate, paymentStatusLoanCode (4/5 matured balloon), modifiedIndicator, mostRecentSpecialServicerTransferDate, DSCR/NOI/occupancy at securitization and current, propertyCity/State/Type MF | free-public | https://www.sec.gov/info/edgar/edgarabsxml.htm ; parser guide https://raw.githubusercontent.com/dgunning/edgartools/main/docs/guides/tend-data-object-guide.md | false (parser guide true) | monthly | REPORTED (payment status / SS transfer treated RECORDED) | special servicing 20; NP matured balloon 20; performing 14; modified 10 |
| CMBS trustee IRP (CTSLink etc.) incl. watchlist file | WATCHLIST, SPECIAL_SERVICING, LOAN_MODIFIED | OPERATING / HARD_DISTRESS | Computershare CTSLink and other certificate administrators | Loan Periodic Update, Property File, Watchlist codes, Special Servicer file, modification history | free-registration (144A needs investor certification) | https://ctslink.computershare.com/ | false | monthly | REPORTED | watchlist 7 (the only free route to CREFC codes) |
| Paid consolidators (CRED iQ, Trepp, Yardi Matrix 50+ units, Reonomy, CoStar, Crexi Intelligence, ATTOM/DataTree) | LOAN_MATURITY, owner contacts, LISTING_WITHDRAWN | DEBT / OPERATING | vendor exports (file-drop) | maturity, lender, UPB, rate, DSCR, status, true owner contacts, listing history | paid (quote-based; unverified pricing) | https://cred-iq.com/ ; https://www.trepp.com/ ; https://www.yardimatrix.com/multifamily ; https://www.reonomy.com/ ; https://www.costar.com/ ; https://www.crexi.com/intelligence ; https://www.attomdata.com/ | false | monthly | REPORTED | as tape; label `vendor:<name>`; Yardi Matrix lender mix (56% agency / 16% bank / 10% HUD / 6% debt fund / 6% life co / 2% CMBS; origination mix, verify) is the prior for inferring lender type |
| Recorded trust deed (bank / CU / life co / debt fund) | LOAN_MATURITY (ESTIMATED from recording + lender term; RECORDED when image states it), LOAN_MODIFIED, REFINANCE_CLOSED -> SUPPRESS_UNTIL, UNENCUMBERED, RATE_CAP_EXPIRY | DEBT | recorder index export renamed to canonical columns (`normalize_recorder_index.py`; lender tokens via `assets/lender_type_dictionary.csv`); Washington Co. Recording; Clackamas Clerk; Clark WA Auditor / Digital Archives | doc type, recording date, grantor, grantee (lender), stated principal, maximum principal (ORS 86.155 legend), maturity when printed, signatory block | free-public index; Multnomah images $3.75/doc (county snippet; unverified; `market-params.json` verify: true); Clark images free (unverified); Washington/Clackamas fees unverified | https://multco.us/recording/research-online ; https://www.washingtoncountyor.gov/at/recording ; https://www.clackamas.us/recording ; https://clark.wa.gov/auditor/recording | false | re-check when a Modification or Reconveyance records | ESTIMATED (0.50) -> RECORDED on image read | timing bands at 0.50 multiplier; buy the image for every Tier A inferred maturity |
| Interest-only roll (amortization shock) | IO_EXPIRATION | DEBT | tapes above | first_payment_date, io_term | per tape | — | false | 6-12 mo before IO end | REPORTED | +3 if <= 12 mo; refi factor +4/+2 when amortizing DSCR < 1.20 / 1.0-1.2 |
| Floating-rate / bridge debt, rate-cap expiry, extension test | RATE_CAP_EXPIRY; signal lender_type debt_fund_bridge, rate_type floating | DEBT | tapes (rate type); recorder (lender name -> debt fund); SOS UCC (rate-cap agreement as collateral) | rate type, index + margin, origination date, lender | per source | https://sos.oregon.gov/business/Pages/ucc-search-help.aspx | false | 3-9 mo before initial maturity / cap expiry | ESTIMATED | +3 floating; +2 if 2021-22 origination; +2 extension test fail |
| Prepayment window opening (lockout / YM / HUD step-down end) | PREPAY_WINDOW_OPEN | DEBT | tapes; HUD final endorsement + 10y | lockout_end, ym_end, premium_end | per tape | — | false | contact 3-6 mo before open | REPORTED / DERIVED | +2 if opens within 12 mo; `assumption_play` tag for low-coupon HUD/agency |
| DSCR below 1.20x at refi rates / refinance gap | signals est_dscr_refi, refi_gap_pct | DEBT (attribute) | `capital_stack.py` from tape NOI or benchmark NOI | NOI, UPB, value, refi constant | — | — | — | evaluate for every maturity inside horizon | reported x1.0 / estimated x0.7 | refinance_gap_coverage: gap > 25% 14; 10-25% 10; 0-10% 4; <= 0 but maturity <= 12 mo 3; DSCR < 1.0 +4, 1.0-1.2 +2; extension fail +2 |
| Rate-shock spread (coupon far below market) | signal rate_spread_bp | DEBT (attribute) | tapes (note rate) vs pack refi rate | note_rate | — | — | — | pairs with maturity | per tape | +2 when > 200 bp and maturity < 36 mo; `assumption_play` when assumable |
| Judicial foreclosure complaint / lis pendens | JUDICIAL_FORECLOSURE_FILED / LIS_PENDENS | HARD_DISTRESS | OJD Smart Search civil (`court_or`); MultcoRecords Notice of Pendency; OJCIN for complaint text | plaintiff (lender), defendant (owner), filing date; complaint: balance, default date, guarantors | free-registration / paid | https://webportal.courts.oregon.gov/portal/ ; https://www.courts.oregon.gov/services/online/Pages/ojcin.aspx | false | 6-12 mo to judgment; sheriff sale 4+ weeks after writ; 180-d redemption | RECORDED | hard_distress 17; +2 individual guarantor |
| Receiver appointed (ORS ch. 37) | RECEIVER_APPOINTED | HARD_DISTRESS (ROUTING) | OJD civil orders | receiver firm, lender counsel, appointment date | free-registration | https://www.oregonlegislature.gov/bills_laws/ors/ors037.html | false | register within 30 d; receivers stabilize 3-9 mo before marketing | RECORDED | 18; route lender_counterparty |
| Oregon NOD on an apartment trust deed | NOD_RECORDED | HARD_DISTRESS | MultcoRecords index; PublicNoticeOregon publication; MCSO sales (judicial) | grantor, beneficiary, trustee, default amount, sale date | free-public | https://multcorecords.com/ ; https://www.publicnoticeoregon.com/ ; https://www.mcso.us/how-do-i/civil-enforcement | false | sale >= 120 d; 4 weekly publications | RECORDED | 20 fresh; 14 after 100 d without rescission; Trustee's Deed -> lender_counterparty |
| Chapter 11 single-asset real estate bankruptcy | BANKRUPTCY_FILED (detail ch11_sare) | HARD_DISTRESS (ROUTING) | PACER District of Oregon; inforuptcy / bondoro trackers | debtor, chapter, SARE flag, schedules A/B/D (value, liens, lender), sale motions | paid ($0.10/page) / free trackers | https://www.orb.uscourts.gov | false | plan or payments within 90 d of petition; sales 60-180 d | RECORDED | 15; counsel_only gate; schedules replace estimated balance |
| UCC-1 pledge of membership interests / Article 9 sale notice | UCC_MEZZ_PLEDGE / UCC_ART9_SALE | HARD_DISTRESS | Oregon SOS UCC search (free uncertified); WA DOL UCC; Delaware UCC for DE parents | debtor, secured party, filing/lapse dates, collateral text | free-public | https://sos.oregon.gov/business/Pages/ucc-search-help.aspx | false | lapse 5 y; Article 9 sale ~10 d notice, 30-60 d close | RECORDED | mezz pledge +3 (raise est_ltv 10-20 pts); Article 9 sale 14 |
| Property-tax delinquency / ORS 312 list | TAX_DELINQUENT_YEARS / TAX_FORECLOSURE_LIST | TAX_LIEN / HARD_DISTRESS | MultcoPropTax per account; DART delinquency extract (fee); July/August list and DJC publication | years delinquent, balance, list status | free-registration / paid / manual | https://multcoproptax.com/ ; https://multco.us/dart/property-tax-foreclosure | false | May 16 delinquency; list July; 2-y redemption | RECORDED | operating 1 y 4 / 2 y 7 / 3+ y 10; list 12 in hard_distress |
| Construction (mechanic's) lien | MECHANICS_LIEN | TAX_LIEN / HARD_DISTRESS | recorder Claim of Lien (ORS 87.035); OJD suit (87.055) | claimant (GC vs sub), amount, recording date, suit filed | free-public | https://oregon.public.law/statutes/ors_87.035 | false | 75 d to record; 120 d to sue; dies at 2 y | RECORDED | 8 when suit filed; stacking input; require age > 30 d or > $50k |
| City code-lien foreclosure referral / open code cases | CODE_LIEN_REFERRAL / CODE_CASE_OPEN / DANGEROUS_BUILDING | TAX_LIEN / PHYSICAL | Council ordinance exhibits and press (Hoodline, Willamette Week); BDS open-case lists; PortlandMaps; Conduits lien search ($33) | addresses, lien counts and balances; case type, status | free-public / paid | https://www.portland.gov/revenue/assessments-finance/request-access-search-city-liens ; https://www.portland.gov/bds/property-compliance-services-and-inspections/open-code-enforcement-cases | false | referral -> ordinance -> auction over months | RECORDED / REPORTED | referral 10; dangerous or 2+ housing 7; one case 3 |
| Delinquent sewer/stormwater certified to tax roll | UTILITY_LIEN_CERTIFIED | TAX_LIEN | annual BES certification ordinance exhibits | accounts, amounts | free-public | https://www.portland.gov/council/documents/ordinance/passed/191340 | false | annual | RECORDED | stacking input (+3 equivalent); low weight |
| Sponsor / portfolio-level distress | signal sponsor_loans_maturing_36mo | OWNERSHIP (attribute) | SOS + OpenCorporates sibling cluster run through recorder, OJD, PACER, news | shared registered agent / office / managers; sibling events | free-public / free-registration | https://opencorporates.com/companies/us_or | false | 3-9 mo after first visible default | RECORDED (events) | owner_sponsor 12 when >= 3 loans maturing < 36 mo (needs >= 2 independent indicators); applied to every sibling asset |
| Owner entity administratively dissolved / inactive | ENTITY_ADMIN_DISSOLVED | OWNERSHIP | Oregon SOS Business Registry | status, last annual report, registered agent | free-public | https://sos.oregon.gov/business/pages/find.aspx | false | 45 d after missed annual report; reinstatement within 5 y | RECORDED | 9 if > 1 y; 6 if < 1 y |
| Probate of principal / trust succession | PROBATE_FILED | OWNERSHIP | OJD probate (PR cases); obituaries; recorder Affidavit of Death / PR deeds; SOS manager change | decedent, PR, counsel | free-registration | https://webportal.courts.oregon.gov/portal/ | false | 60-120 d cooling; estates sell 6-18 mo | RECORDED | 12 |
| Voluntary / judicial dissolution, partition, partner dispute | DISSOLUTION_FILED / PARTITION_FILED | OWNERSHIP | SOS Articles of Dissolution; OJD civil (ORS 105 partition, accounting, breach of operating agreement); lis pendens | parties, filing date, counsel | free-public / free-registration | as above | false | winding up 6-24 mo | RECORDED | 15; counterparty = liquidity-seeking partner's counsel |
| Out-of-state / distant owner | ABSENTEE_TIER | OWNERSHIP | assessor mailing address (`normalize_assessor_taxlots.py`, also writes `mailing_address`, HOLD_YEARS, DEPRECIATION_EXHAUSTED, av_rmv_ratio, est_value rmv_calibrated); SOS principal office / foreign registration | state, distance | free-public | https://www.portlandmaps.com/ | false | annual | RECORDED | out-of-state 4; far or non-Pacific foreign LLC 6 |
| Management company change / self-management of 20+ units | MGMT_CHANGE | OPERATING | assessor mailing address diff; listing manager names (Apartments.com, Zumper, Craigslist); signage | PM name over time | free-public (observed) | — | false | detect within 90 d | REPORTED | 3; PM is the gatekeeper |
| Listing expired / withdrawn in last 12 months | LISTING_WITHDRAWN | OPERATING | CoStar / LoopNet status history (paid); Crexi | list date, withdrawn date, last ask, broker | paid | https://www.costar.com/ | false | 0-90 d after withdrawal is best | REPORTED | 7 (< 6 mo); 4 (6-12 mo); last ask = offer ceiling; broker_exclusive gate |
| Long hold / depreciation exhausted (>= 27.5 y) | HOLD_YEARS / DEPRECIATION_EXHAUSTED | OWNERSHIP | RLIS / SAIL sale date; recorder (no recent trust deed; deeds into trusts) | SALE_DATE, DEED_DATE | free-public | https://oregonmetro.gov/rlis-live | false | permanent; quarterly nurture | RECORDED | 8 (exhausted); trust/estate 6 |
| Rent-cap and relocation "rent trap" | signal rent_gap_pct, inside_portland_city_limits | OPERATING (attribute) | OEA annual cap (ORS 90.324); PHB relocation (PCC 30.01.085); ZIP rents (Apartment List / Zumper / RentCafe); building age | cap (2026: 9.5%), relocation amounts (studio $2,900 / 1BR $3,300 / 2BR $4,200 / 3BR+ $4,500), market vs est. in-place rent | free-public | https://www.oregon.gov/das/OEA/Pages/rent-stabilization.aspx ; https://www.portland.gov/phb/rental-services/renter-relocation-assistance | false | cap published by Sept 30; Q4 outreach | ESTIMATED (in-place rent) | gap > 20% on > 15-y building 6; +3 inside Portland |
| Tenant litigation / PHB enforcement | signal tenant_cases_24mo | OPERATING (attribute) | OJD civil / landlord-tenant with owner as defendant; PHB enforcement records (public records) | case count, determinations | free-registration / manual | https://webportal.courts.oregon.gov/portal/ | false | trailing 24 mo | RECORDED | 4 when 2+ |
| Insurance non-renewal / premium shock (confirmed only) | INSURANCE_NONRENEWAL_CONFIRMED | OPERATING | owner/broker confirmation; NOD or complaint text citing insurance covenant | confirmation | manual | https://www.realpage.com/analytics/soaring-insurance-premiums-hitting-apartment-owners/ | false | annual renewals | REPORTED | 6 only when confirmed; never inferred |
| Recent refinance / payoff (suppression) | REFINANCE_CLOSED -> SUPPRESS_UNTIL; UNENCUMBERED | DEBT (SUPPRESSION) / OWNERSHIP | FHASL Terminated; recorder Reconveyance followed <= 90 d by new trust deed | termination type, new lender, new recording date | free-public | as HUD / recorder | false | re-evaluate at suppress_until | RECORDED | DEBT factors 0 until suppress_until; UNENCUMBERED -> route watch |
| Recent 1031 acquisition (negative) / sibling-asset sale (positive) | RECENT_1031_ACQUISITION; signal sibling_asset_sold_12mo | OWNERSHIP | RLIS sale date + deed language; sponsor map | hold < 3 y; sibling sale date | free-public | — | false | 36 mo negative; 12 mo positive | RECORDED | -10 total; +3 owner_sponsor |

Market parameters (cap rates, vacancy, rents, opex) come from the pack `market-params.json`; benchmark bands from `multifamily-benchmarks`.

## 3. Event derivation rules

```
Tapes (HUD / DUS / MSIA / EX-102):
  LOAN_MATURITY.event_date   = tape maturity (HUD RECORDED; others REPORTED)
  IO_EXPIRATION              = first_payment_date + io_term_months
  PREPAY_WINDOW_OPEN         = max(lockout_end, ym_end, premium_end)            (REPORTED)
                             = final_endorsement + 10 y for HUD 223(f)/221(d)(4) (DERIVED, window +/-6 mo)
  SPECIAL_SERVICING          = mostRecentSpecialServicerTransferDate when master-servicer return date is null
  MATURED_BALLOON.value      = paymentStatusLoanCode 4 (performing) | 5 (non-performing)
  LOAN_MODIFIED              = modifiedIndicator true (date = report period) or recorded Modification/Extension (date = recording)
  WATCHLIST                  = IRP watchlist code present (date = report period)
  OCCUPANCY_DROP             = current occupancy < 85% or down >= 10 pts vs securitization
  REFINANCE_CLOSED           = FHASL Terminated row (type prepaid/refinanced), or Reconveyance followed <= 90 d by new trust deed
  SUPPRESS_UNTIL             = new_origination + min_term(lender_type)

Recorder (no tape):
  lender_type                = assets/lender_type_dictionary.csv match on grantee tokens (default unknown -> bank_cu prior per Yardi mix)
  LOAN_MATURITY (ESTIMATED)  = recording_date + typical_term; window recording + min_term .. recording + max_term
  LOAN_MATURITY (RECORDED)   = maturity printed in the image (ORS 86.155 legend; Fannie 6025.OR / Freddie / HUD-94000M definitions)
  RATE_CAP_EXPIRY            = origination + 2-3 y when lender_type debt_fund_bridge or rate_type floating (ESTIMATED, +/-12 mo)
  UNENCUMBERED               = Reconveyance with no new trust deed within 90 d

Courts / recorder distress:
  NOD_RECORDED, TRUSTEE_SALE_EARLIEST (NOD + 120 d), CURE_DEADLINE (sale - 5 d) as in sfr-distress.md
  JUDICIAL_FORECLOSURE_FILED = complaint filing date; detail individual_guarantor when an individual is named
  LIS_PENDENS                = recording date
  RECEIVER_APPOINTED         = order date -> route lender_counterparty, owner_outreach false
  BANKRUPTCY_FILED           = petition date; detail ch11 / ch11_sare / ch7
  UCC_MEZZ_PLEDGE            = UCC-1 filing date with collateral containing "membership interests"; UCC_ART9_SALE = notice date

Ownership / operating:
  HOLD_YEARS, DEPRECIATION_EXHAUSTED, ABSENTEE_TIER, RECENT_1031_ACQUISITION as in sfr-distress.md Section 3
  ENTITY_ADMIN_DISSOLVED     = SOS status date; MANAGER_CHANGE / REGISTERED_AGENT_CHANGE = annual report date
  LISTING_WITHDRAWN          = withdrawn/expired date
  rent_gap_pct               = (market_rent - inplace_rent_est) / inplace_rent_est ; years_to_market = ln(market/inplace) / ln(1 + cap)
  relocation_exposure        = sum over units of PHB amount by bedroom where plan requires >= 10% increase (inside Portland)
```

Validation: `orig_date < maturity < orig_date + 45 y`; a tape maturity earlier than the recorder's stated maturity for the same lien -> `Verify — Conflicting Sources`, keep the tape; HUD Active rows whose project number appears in Terminated -> suppress.

## 4. Valuation and capital-stack proxy

`est_value = est_noi / cap_rate` (`income_proxy`); NOI from tape (reported) else `noi_proxy(units, ZIP rent, vacancy 0.071, opex_ratio 0.42)` (`benchmark_estimate`); cap rate from pack: market average 6.4% (Kidder Q2 2026) base case, class A 4.7 / B 5.1 / C 5.6 indicative for sensitivity. RMV is a +/-25% sanity band only; Assessed Value is never used. Price-per-unit band ($182,489/unit Q2 2026) is the last-resort proxy.

Balance: tape UPB (REPORTED/RECORDED) else amortized from stated principal (ESTIMATED); add UCC mezz slice (10-20% of value) to est_ltv when a membership-interest pledge exists. Refi test per `capital-stack-math.md` Section 5 with `dscr_floor` 1.25 (agency/CMBS) or 1.20 (bank), debt yield 8%, LTV 70%, refi rate UST10 + 175 bp. Equity cushion 10-35% is the best conversion band; <= 0 routes to `lender_counterparty`.

## 5. Scoring rubric

Canonical: `scoring/market_rate_mf.json`.

| factor | weight | rule |
|---|---|---|
| Capital-stack timing | 25 | nearest DEBT event: 0-12 mo 17; 12-24 12; 24-36 7; 36-60 3; modifiers: IO end <= 12 mo +3; floating/bridge +3 (+2 if 2021-22 origination); prepay window <= 12 mo +2; rate spread > 200 bp with maturity < 36 mo +2; cap 25; x basis multiplier (RECORDED 1.0 / REPORTED 0.9 / ESTIMATED 0.5 / PROXY 0.3) |
| Refinance gap and coverage | 20 | gap > 25% 14; 10-25% 10; 0-10% 4; <= 0 but maturity <= 12 mo 3; DSCR_refi < 1.0 +4, 1.0-1.2 +2; extension test fail +2; cap 20; x1.0 reported / x0.7 estimated NOI; x1.0 if first debt event < 24 mo, x0.5 if 24-60 |
| Hard distress events | 20 | special servicing or NP matured balloon 20; NOD 20 (14 after 100 d); receiver 18 -> lender_counterparty; judicial foreclosure / lis pendens 17 (+2 individual guarantor); SARE Ch.11 15 (counsel only); performing matured balloon 14; Article 9 sale 14; tax foreclosure list 12; modification in last 12 mo 10; mechanics-lien suit 8; watchlist 7; take max |
| Owner / sponsor profile | 15 | dissolution/partition 15; sponsor >= 3 loans maturing < 36 mo 12; probate of principal 12; admin dissolved > 1 y 9 (< 1 y 6); single-asset LLC > 7 y with bank debt 8; depreciation exhausted 8; trust/estate 6; out-of-state 4 (far 6); mgmt change 3; sibling sale +3; cap 15 |
| Operating / regulatory pressure | 10 | tax 3+ y 10, 2 y 7, 1 y 4; code-lien referral 10; dangerous building or 2+ housing cases 7 (one 3); listing withdrawn < 6 mo 7 (6-12 mo 4); rent trap > 20% on > 15-y building 6 (+3 inside Portland); tenant litigation 2+ 4; insurance non-renewal confirmed 6; take max |
| Signal stacking | 10 | 2 families 5; 3 = 8; 4+ = 10; events > 180 d old count 50% except permanent states |

Caps and routes (shared): no DEBT and no REGULATORY event inside horizon -> tier cap C; proxy-only -> cap C; cushion <= 0 -> `lender_counterparty`; assumable low-coupon HUD/agency -> `assumption_play` tag; SUPPRESS_UNTIL zeroes DEBT factors; hold < 3 y -10; rehab within 5 y -15; active listing excluded.

## 6. Owner archetypes and outreach angles

| owner_type | angle | template | gates |
|---|---|---|---|
| single_asset_llc | maturity math; 1031/DST; regulatory fatigue | `single_asset_llc` | dnc_scrub; broker_exclusive if LISTING_WITHDRAWN |
| regional_operator | portfolio liquidity; trade assets; certainty | `regional_operator` | broker_exclusive |
| institutional | formal IOI; debt assumption; speed | `institutional` | assumption_approval |
| trust_estate | trustee / PR letter; simple liquidation | `estate` | probate_cooling |
| individual (small 5-12 unit owners) | convenience, tax strategy | `individual_or_trust` | dnc_scrub |
| lender_reo_receiver | register as qualified buyer | `receiver_lender` | counsel_only when bankruptcy |

Decision maker resolution: SOS managers / GPs + trust-deed signatory for grade A (`decision-maker-enrichment.md`). Sponsor families mapped by shared registered agent / office / managers.

## 7. Lead-card additions

`Lender` and `lender_type`, `Loan type` (fixed/floating, IO), `UPB` with basis, `Note rate` and `rate_spread_bp`, `Maturity` with basis and window, `IO end`, `Prepay open`, `Assumable` flag, `DSCR (reported/estimated)`, `Refi gap %`, `Equity cushion %`, `Servicer status` (watchlist / special servicing / matured balloon), `Sponsor family` id and count of sibling maturities, `Rent gap %` and `relocation_exposure` (Portland), `Last listing` (date, ask, broker).

## 8. Pro tips and timing

- **Quote the basis breakdown before the count.** "47 loans maturing within 5 years" means nothing until it reads "7 RECORDED (HUD), 12 REPORTED (agency/CMBS), 28 ESTIMATED (recorder + lender term)".
- **Buy the image for every Tier A inferred maturity.** The Multnomah per-image fee ($3.75 per county snippet; unverified, stored in `market-params.json` with verify: true) turns a 0.50 multiplier into 1.00 and often names the signatory.
- **Commercial lenders in Oregon foreclose judicially.** ORS 86.797 bars deficiency after a trustee's sale and after judicial foreclosure of residential trust deeds, so apartment lenders with guarantors file under ORS 88 and move for a receiver (ORS 37). An NOD-only monitor misses a large share of apartment distress; court filings and lis pendens are mandatory.
- **The open window is the trigger, not the maturity.** Agency yield maintenance typically ends ~6 months before maturity; owners with 3-4% coupons sell or refinance when the penalty drops, not at the balloon.
- **2021-2022 floating-rate bridge debt is the most motivated cohort.** Cap replacement cost, extension DSCR/debt-yield tests they may fail, and 2026-2027 final maturities. CRE CLOs are not on EDGAR; find them through MSIA, trustee portals or vendors.
- **A low coupon is a buyer's edge when assumable.** HUD and agency loans assume with approval; tag `assumption_play` rather than scoring it as distress.
- **HUD's Active file lags.** Diff against Terminated and Ginnie Mae daily issuance before scoring a maturity someone refinanced last month.
- **Measure 50 AV is not value.** AV is commonly 50-55% of market; use income proxy and RMV only as a sanity band.
- **Rent trap is a Q4 conversation.** The state cap publishes by September 30; Portland relocation liability attaches to any 10%+ increase; owners plan next-year increases in Q4.
- **Insurance is a question, not a dataset.** Score non-renewal only when confirmed by the owner, broker or a filing.

## 9. Refresh cadence

| feed | cadence |
|---|---|
| HUD FHASL Active + Terminated, Ginnie Mae | monthly |
| DUS Disclose, MSIA, EX-102 / trustee IRP | monthly (remittance) |
| recorder document types (trust deed, modification, reconveyance, NOD, lis pendens, mechanics lien) | weekly |
| OJD civil / probate / receivership; PACER | weekly |
| SOS status for every owner entity on the worklist | quarterly, plus on worklist |
| assessor roll, tax payment history | quarterly; semiannual after May 16 / Nov 15 |
| BDS cases, council lien referrals | monthly |
| market params (cap, vacancy, rents, opex, UST10) | quarterly |
| vendor exports (if licensed) | monthly; diff for new transfers, extensions, maturity-date changes |

## 10. Known gaps

- No public tape for bank, credit-union, life-company, debt-fund and unsecuritized agency balance-sheet loans (a third or more of apartment debt; unverified; most of Portland's 5-49 unit stock); recorder images are the only primary source and Oregon prints maturity on page one only for line-of-credit instruments (ORS 86.155).
- EDGAR EX-102 covers SEC-registered conduit CMBS only (perhaps 2% of apartment debt); 144A conduits, SASB, CRE CLO, Freddie K/SB and Fannie GeMS need MSIA, DUS Disclose, trustee portals (investor certification for 144A) or paid vendors. CREFC watchlist codes are not an EX-102 field.
- Every source `verified_live=false` except the edgartools parser guide; HUD field names must be confirmed from the live file and `/0?f=pjson`; Washington County and Clackamas recorder index URLs and image fees unconfirmed.
- DSCR/NOI in tapes are borrower-reported and lag 1-2 quarters; benchmark NOI carries +/-15% error; score reported figures higher and show the basis.
- Vendor pricing unverified (CoStar ~$300-500+/user/mo, ~$40k/yr median contract per third parties; Yardi Matrix, Reonomy, CRED iQ, Crexi, Trepp quote-based); PropStream has no confirmed maturity-date filter; Yardi Matrix covers 50+ units only.
- Freddie MLPD and Fannie loan performance data are anonymized: calibration only, never targeting.
- Insurance non-renewal has no per-property dataset; Portland Schedule R rental registration is confidential tax information and is not a lead source; Enhanced Rental Inspections enrollment requires a public-records request.
- Scoring weights are expert heuristics; recalibrate against closings after 2-3 quarters by editing the JSON.
