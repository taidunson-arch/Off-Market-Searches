# Source Directory: <Metro>, <State> market pack

One row per source. Columns are fixed: `source_id | adapter | class | publisher | URL | access | fee | cadence | key fields | verified_live | caveats`. Copy national rows from `references/sources/federal/README.md` and add the local ones. `verified_live` starts `false`; `scripts/smoke_test_sources.py` writes `sources_status.json` and a human flips the column. Never construct a URL you have not seen; describe how to find the page instead.

## Statewide and federal tapes

| source_id | adapter | class | publisher | URL | access | fee | cadence | key fields | verified_live | caveats |
|---|---|---|---|---|---|---|---|---|---|---|
| <state>_hfa_inventory | `<adapter>` (file-drop) | 3 | <State HFA> | <URL> | free-public | none | <cadence> | property, address, county, owner, programs, compliance start, program expiration dates (declare formats in dataset-schemas.yaml) | false | <date formats; data quality> |
| <state>_preservation_notices | records request / dataset | 3 | <State HFA preservation program> | <URL> | free-public / manual | none | <cadence> | expiring list, notice status | false | |
| <state>_qap | reference | 3 | <State HFA> | <URL> | free-public | none | annual | REUA term, QC waiver policy | false | |
| hud_fhasl_active / hud_fhasl_terminated | `normalize_hud_insured.py` | 2,3 | HUD | https://www.hud.gov/hud-partners/multifamily-fhasl-active ; https://www.hud.gov/hud-partners/multifamily-fhasl-terminated | free-public | none | monthly | see federal/README.md | false | filter state; county via ZIP crosswalk |
| hud_mf_assist_sec8 | `normalize_hud_sec8.py` | 3 | HUD | https://www.hud.gov/hud-partners/multifamily-assist-section8-database | free-public | none | monthly | see federal/README.md | false | |
| hud_lihtc_db | adapter (future) | 3 | HUD PD&R | https://www.huduser.gov/portal/datasets/lihtc.html | free-public | none | annual | see federal/README.md | false | |
| hud_reac | adapter (future) | 3 | HUD REAC | https://www.hud.gov/stat/mfh/inspection-scores | free-public | none | per release | see federal/README.md | false | |
| usda_mfh_exit | adapter (future) | 3 | USDA RD | https://www.sc.egov.usda.gov/data/MFH.html | free-public | none | semiannual | see federal/README.md | false | |
| nhpd | manual export | 3 | PAHRC / NLIHC | https://preservationdatabase.org/ | free-registration | none | quarterly | see federal/README.md | false | |
| ginnie_mf / fannie_dus_disclose / freddie_msia / sec_edgar_ex102 / cmbs_trustee_irp | see federal/README.md | 2,3 | | | | | monthly | | false | |
| hud_zip_county_crosswalk | geo | all | HUD PD&R | https://www.huduser.gov/portal/datasets/usps_crosswalk.html | free-registration | none | quarterly | ZIP, county, RES_RATIO | false | |

## County recorders, assessors and courts (one block per county)

| source_id | adapter | class | publisher | URL | access | fee | cadence | key fields | verified_live | caveats |
|---|---|---|---|---|---|---|---|---|---|---|
| <county>_recorder | `recorder_<st>` | all | <County Recorder / Clerk / Auditor> (<address>; <phone>) | <URL or "from the county recorder's home page, Recorded Documents Search"> | free-public index; images <fee> | <fee> | daily | instrument no., recording date, document type, grantor/grantee, legal description; images since <year> | false | <search semantics: name vs parcel; pre-sale instrument recorded?> |
| <county>_assessor | `assessor_<st>` | all | <County Assessor> | <URL> | free-public / free-registration | none | <cadence> | owner, mailing address, situs, values (market vs assessed), year built, units, sale date/price, deed reference, exemption, tax status | false | <is assessed value market value?> |
| <county>_tax_collector | records request | all | <County Treasurer / Tax Collector> | <URL> | manual | <fee> | annual list | delinquent years, foreclosure list, redemption | false | |
| <county>_gis | geo | all | <County / regional GIS> | <URL> | free-public | none | <cadence> | taxlots, jurisdiction polygons | false | |
| <state>_courts | `court_<st>` | all | <State courts portal> | <URL> | free-registration / paid | <fee> | continuous | case type (probate, civil, landlord-tenant, domestic), parties, filing date | false | <documents available?> |
| pacer_<district> | `court_fed` | all | US Bankruptcy Court, <District> | <URL> | paid | $0.10/page | continuous | debtor, chapter, schedules | false | |
| <state>_sos_registry | manual (worklist) | all | <State SOS> | <URL> | free-public | none | continuous | status, formation date, registered agent, principal office, managers / members / GPs / officers | false | <what the annual report must list> |
| <state>_sos_ucc | manual | 2,3 | <State SOS or DOL> | <URL> | free-public | <certified fee> | continuous | debtor, secured party, collateral | false | |
| <city>_code_enforcement | `code_<city>` | 1,2 | <City department> | <URL> | free-public / manual | none | <cadence> | case type, address, status, open date | false | <owner names included?> |
| <city>_liens | shortlist only | 1,2 | <City> | <URL> | paid / manual | <fee> | continuous | lien balances, referral status | false | |
| <city>_rental_program | reference | 1,2 | <City> | <URL> | free-public | none | annual | registration, inspection, relocation, rent rules | false | |
| <sheriff>_sales | monitor | 1,2 | <County Sheriff> | <URL> | free-public | none | as scheduled | judicial sale calendar | false | |
| <state>_public_notices | monitor | 1,2 | <state press association notices site> | <URL> | free-public | none | daily | trustee / sheriff sale notices, tax lists | false | |

## Paid consolidators

Copy the relevant rows from `references/sources/federal/README.md`; add local coverage notes (e.g. Yardi Matrix 50+ units only).

## Market parameter sources

| source_id | publisher | URL | access | cadence | fields | verified_live |
|---|---|---|---|---|---|---|
| <broker_report> | <brokerage research> | <URL> | free-public | quarterly | vacancy, asking rent, cap rate, price/unit | false |
| <local_apartment_association> | | | | | submarket rent and vacancy | false |
| zumper_<metro> / rentcafe_<metro> / apartment_list_rents | Zumper; Yardi RentCafe; Apartment List | <URLs> | free-public | monthly | rent by bedroom / ZIP | false |
| irem_income_expense_iq | IREM | https://www.irem.org/learning/tools/income-expense-iq | paid (summary free) | annual | opex per unit | false |
| hud_fmr_safmr | HUD PD&R | https://www.huduser.gov/portal/datasets/fmr.html | free-public | annual | FMR / SAFMR | false |
| <assessor_faq> | <County Assessor> | <URL> | free-public | — | assessment regime (market vs capped) | false |

## Statutes (see legal-timelines.md)

| source_id | URL | verified_live |
|---|---|---|
| <state>_foreclosure_statute | <URL> | false |
| <state>_receivership / liens / tax foreclosure | <URL> | false |
| <state>_preservation_notice_law | <URL> | false |
| <state>_telephone_solicitation / dnc | <URL> | false |
| <state>_wholesaler / equity_purchaser | <URL> | false |
| irc_42 | https://www.law.cornell.edu/uscode/text/26/42 | false |
