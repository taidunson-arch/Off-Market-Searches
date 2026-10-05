# Source Directory: <Metro>, <State> pack (preservation-loan-book)

One row per source. Columns are fixed: `source_id | adapter | profile | publisher | URL | access | fee | cadence | key fields | verified_live | caveats`. The agency's own records come first; copy national rows from `references/sources/federal/README.md` and add the state and local ones. `verified_live` starts `false`; `scripts/smoke_test_sources.py` writes `sources_status.json` and a human flips the column. Never construct a URL you have not seen; describe how to find the page instead. No paid consolidators, skip-trace vendors, sheriff-sale or trustee monitors, wholesaler or equity-purchaser statutes belong in this pack.

## Agency records (the primary tape; RECORDED)

| source_id | adapter | profile | publisher | URL | access | fee | cadence | key fields | verified_live | caveats |
|---|---|---|---|---|---|---|---|---|---|---|
| agency_servicing_extract | `ingest_servicing_extract.py` (run first) | all | <the agency's loan / grant / asset system> | internal export | manual | none | monthly | canonical columns in `references/servicing-extract.md` | true when supplied | profile dates with date_profile.py |
| <hfa>_notice_log | servicing extract notice_* columns | hfa | <HFA preservation program> | internal | manual | none | on receipt | owner notices, opt-out notices, designee appointments, recorded ROFRs | false | the RECORDED source for notice_status |
| <hfa>_qc_log | servicing extract qc_* columns | hfa | <HFA LIHTC compliance> | internal | manual | none | on receipt | QC requests, completeness, waiver status, presentment | false | |
| <pbca>_optout_log | servicing extract hap_renewal_* columns | hfa or <PBCA> | <state PBCA> | internal / records request | manual | none | on receipt | renewal requests, opt-out letters, tenant-letter review | false | verify the state's PBCA identity |
| <city>_loan_portfolio | servicing extract (loan / grant) | city_housing, cdbg_home | <city housing bureau> | <URL or internal> | manual | none | monthly | city loans, covenant ends, HOME / CDBG awards | false | |
| <pha>_assets | servicing extract (owned_asset / administered_contract) | pha_am | <PHA> | <board packets URL> | manual / free-public | none | board cycle | owned assets, RAD / Section 18 status, PBV contracts | false | |
| hud_idis_home_reports | servicing extract (grant) | cdbg_home | HUD IDIS (PJ login) | HUD Exchange IDIS page | free-registration (PJ) | none | per PJ reporting | HOME completion dates, per-unit investment, inspections | false | PJ extract is the RECORDED source for AFFORDABILITY_PERIOD_END |
| book_crosswalk | `plb/book_join.py` | all | this pack | `book_crosswalk.csv` | internal | none | after every run | agency ids -> property_id (analyst-confirmed) | n/a | |

## Statewide and federal inventories

| source_id | adapter | profile | publisher | URL | access | fee | cadence | key fields | verified_live | caveats |
|---|---|---|---|---|---|---|---|---|---|---|
| <state>_hfa_inventory | `<adapter>` (file-drop) | all | <State HFA> | <URL> | free-public | none | <cadence> | property, address, county, owner, owner type, programs, total / assisted / PSH units, bedroom mix, compliance start, program expiration dates, HFA-funded flag (declare formats in dataset-schemas.yaml) | false | <date formats; data quality; HAP date freshness> |
| <state>_preservation_registry | records request / dataset (`normalize_ohcs_forecast.py` pattern) | all | <State HFA preservation program> | <URL> | free-public / manual | none | <cadence> | expiring list, notice status, preservation status | false | public registry of notices? (`federal/preservation-notice-laws-by-state.md`) |
| <state>_qap | reference | hfa | <State HFA> | <URL> | free-public | none | annual | extended-use term, QC waiver policy and first year | false | |
| <state>_nofa | reference (mandate.json) | hfa | <State HFA> | <URL> | free-public | none | annual | preservation products, eligibility, windows | false | |
| hud_fhasl_active / hud_fhasl_terminated | `normalize_hud_insured.py` | all | HUD | https://www.hud.gov/hud-partners/multifamily-fhasl-active ; https://www.hud.gov/hud-partners/multifamily-fhasl-terminated | free-public | none | monthly | see federal/README.md | false | filter state; county via ZIP crosswalk |
| hud_mf_assist_sec8 | `normalize_hud_sec8.py` | all | HUD | https://www.hud.gov/hud-partners/multifamily-assist-section8-database | free-public | none | monthly | see federal/README.md | false | overrides the state inventory's HAP date |
| hud_lihtc_db | adapter (future) | all | HUD PD&R | https://www.huduser.gov/portal/datasets/lihtc.html | free-public | none | annual | see federal/README.md | false | |
| hud_reac | `normalize_reac_scores.py` | all | HUD REAC | https://www.hud.gov/stat/mfh/inspection-scores | free-public | none | per release | see federal/README.md | false | |
| hud_renewal_guide | reference | all | HUD | locate "Section 8 Renewal Policy Guidebook" on the HUD Multifamily site | free-public | none | per revision | renewal options; ch. 11 opt-out | false | |
| usda_mfh_exit | adapter (future) | all | USDA RD | https://www.sc.egov.usda.gov/data/MFH.html | free-public | none | semiannual | see federal/README.md | false | RD state office holds prepayment requests |
| nhpd | manual export | all | PAHRC / NLIHC | https://preservationdatabase.org/ | free-registration | none | quarterly | see federal/README.md | false | |
| hud_zip_county_crosswalk | geo | all | HUD PD&R | https://www.huduser.gov/portal/datasets/usps_crosswalk.html | free-public (files) | none | quarterly | ZIP, county, RES_RATIO | false | |
| hud_fmr_safmr | market-params | all | HUD PD&R | https://www.huduser.gov/portal/datasets/fmr.html | free-public | none | annual | FMR / SAFMR | false | NOAH watch and restricted NOI floor only |
| <local_bond_or_levy> | reference (mandate.json) | city_housing, county | <regional government> | <URL> | free-public | none | annual | acquisition / preservation funds | false | |
| <bridge_lender> | reference (mandate.json external) | city_housing, county | <CDFI> | <URL> | manual | none | rolling | bridge acquisition loans | false | |

## Organization resolution and public records (organization level only)

| source_id | adapter | profile | publisher | URL | access | fee | cadence | key fields | verified_live | caveats |
|---|---|---|---|---|---|---|---|---|---|---|
| <state>_sos_registry | manual (SOS worklist) | all | <State SOS> | <URL> | free-public | none | continuous | status, formation date, registered agent (service address), principal office, managers / members / GPs / officers (roles only by default) | false | <what the annual report must list> |
| <state>_sos_ucc | manual | all | <State SOS or DOL> | <URL> | free-public | <certified fee> | continuous | debtor, secured party, collateral | false | |
| irs_teos_990 | manual | all | IRS TEOS; ProPublica Nonprofit Explorer | https://apps.irs.gov/app/eos/ ; https://projects.propublica.org/nonprofits/ | free-public | none | annual | Form 990 Part VII roles | false | |
| <county>_recorder | documents_to_request (LURA / ROFR images only) | all | <County Recorder / Clerk / Auditor> | <URL or "from the recorder's home page, Recorded Documents Search"> | free-public index; images <fee> | <fee> | daily | regulatory agreements, ROFR notices, trust deeds | false | the agency's own file comes first |
| <county>_assessor | manual file (exemption codes, delinquency, foreclosure list) | all | <County Assessor / Treasurer> | <URL> | free-public / manual | none | annual roll | exemption code by year, delinquent years, foreclosure list | false | <is assessed value market value?> |
| <state>_courts | manual (book-risk stub) | all | <State courts portal> | <URL> | free-registration / paid | <fee> | continuous | foreclosure, receivership filings on regulated assets | false | |
| pacer_<district> | manual | all | US Bankruptcy Court, <District> | <URL> | paid | $0.10/page | continuous | debtor, chapter | false | gate counsel_only |
| <city>_code_enforcement | manual file (CODE_CASE_OPEN, DANGEROUS_BUILDING) | city_housing | <City department> | <URL> | free-public / manual | none | <cadence> | case type, address, status | false | |

## Statutes and guidance (see legal-timelines.md)

| source_id | URL | verified_live |
|---|---|---|
| <state>_preservation_notice_law and rules | <URL> | false |
| <state>_public_records_law | <URL> | false |
| <state>_entity_law (annual report contents) | <URL> | false |
| irc_42; 26 CFR 1.42-5; 1.42-18 | https://www.law.cornell.edu/uscode/text/26/42 ; https://www.law.cornell.edu/cfr/text/26/1.42-5 ; https://www.law.cornell.edu/cfr/text/26/1.42-18 | false |
| 42 U.S.C. 1437f(c)(8), (t); 24 CFR 402.8 | https://www.law.cornell.edu/uscode/text/42/1437f ; https://www.law.cornell.edu/cfr/text/24/402.8 | false |
| 24 CFR 92 / 93 / 570 | https://www.ecfr.gov/current/title-24/subtitle-A/part-92 ; https://www.law.cornell.edu/cfr/text/24/93.302 ; https://www.law.cornell.edu/cfr/text/24/570.505 | false |
| 7 CFR 3560 subpart N | https://www.ecfr.gov/current/title-7/subtitle-B/chapter-XXXV/part-3560/subpart-N | false |
| HUD notices (H 2013-17, H 2013-25, H 2022-05, RAD REV-4, PIH 2026-23) | see federal/README.md | false |
