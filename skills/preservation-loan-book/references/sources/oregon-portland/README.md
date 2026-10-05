# Jurisdiction Pack: Portland, Oregon (`oregon-portland`)

The worked example for `preservation-loan-book`. A jurisdiction pack is everything that is specific to one place and one set of agencies: geography modes, the source directory, dataset schemas with declared date formats (including the agency servicing extract), agency profiles, the mandate / product file, market and statutory parameters, legal clocks, the book crosswalk and the optional equity overlay. Scripts load it with `--pack references/sources/oregon-portland`. To build another jurisdiction, copy `references/sources/_template/` and follow `references/sources/README.md`.

Agency profiles in this pack: `hfa` = Oregon Housing and Community Services; `city_housing` = Portland Housing Bureau; `county` = Multnomah / Washington / Clackamas County housing offices; `pha_am` = Home Forward (alternates: Housing Authority of Clackamas County, Housing Authority of Washington County); `cdbg_home` = Portland Consortium HOME / CDBG participating jurisdiction.

## Files

| file | purpose | read by |
|---|---|---|
| `geography.md` | modes (`city_limits`, `county`, `metro_core`, `cbsa`), FIPS, jurisdictions, resolution order, boundary sources, OHCS row counts per mode (810 / 546 / 518) | SKILL.md Step 1; `plb/geo.py` |
| `sources.md` | every source with adapter, profile, publisher, URL, access tier, fee, cadence, key fields, `verified_live`, caveats; agency records first | Step 2 inbox checklist; `smoke_test_sources.py` |
| `dataset-schemas.yaml` | declared per-column date formats, basis, event mapping, `match_any`, `required_by_kind`, enums, validations, normalizations, lead-column maps, vulnerability flags, PuSH window parameters, county FIPS for the agency servicing extract, OHCS, HUD FHASL, HUD Sec 8, REAC, forecast and NOAH files | `plb/schema.py`, every adapter |
| `agency-profiles.yaml` | per-profile behaviour: book sources, expected-book flag, qualified-purchaser / designee / PBCA / QC-administrator status, routes enabled, self-owner tokens, recapture methods, PII level, mandate defaults, Board_Totals variant | `build_universe.py`, `plb/agency_calendar.py`, `plb/scoring.py`, `plb/units.py`, `plb/pii.py` |
| `mandate.json` | open products (OHCS preservation NOFA, 4% gap, 0% rehab recap, PHB preservation RFP, Metro bond acquisition, NOAH OHAF bridge, USDA MPR) with eligibility; route-level hard filter on `nofa_offer` | `plb/mandate.py`; Mandate_Fit tab |
| `market-params.json` | affordable NOI inputs, senior DSCR floor, product rates, every statutory day / month count (PuSH 36 / 30 / 24, tenant notice, records 30, ROFR match 30, QC 12 months, HAP opt-out 12 months / 120 days, inspections, USDA 180 days, Section 250), UPB-at-risk and verdict rules; each with value / as_of / source / verify | `plb/agency_calendar.py`, `plb/recap_math.py`, `plb/units.py`; Assumptions tab |
| `legal-timelines.md` | PuSH (ORS 456.250-.265, OAR 813-115, HB 2095, HB 3042, SB 973, SB 32, SB 51), IRC 42 and the HFA's clocks, HOME / HTF / CDBG, MAHRA opt-out and renewal options, HUD legacy, USDA 515, RAD / Section 18, NSPIRE / 8823, ORS 192, book-risk stub, Measure 50 | event derivation; intervention cites |
| `rent-limits.json` | LIHTC max rents by AMI band for restricted NOI (placeholder: nulls until the user pastes current MTSP limits); used only to size a recast / recap gap on our_book rows | `plb/recap_math.py` |
| `book_crosswalk.csv` | agency_loan_id / grant_id -> property_id confirmed by an analyst; join grade `crosswalk`; grows run over run | `plb/book_join.py` |
| `equity_overlays.yaml` | optional high-displacement tracts and under-served districts (+2 / +2); empty in this build | `plb/scoring.build_context` |
| `sources_status.json` | output of `smoke_test_sources.py` (dry run by default); `run_agency_pipeline.py` reads live results to label sources | brief Run Summary, Sources_Vintages tab |

## Coverage matrix (source x county)

| source | Multnomah 41051 | Washington 41067 | Clackamas 41005 | Clark WA 53011 | Columbia / Yamhill |
|---|---|---|---|---|---|
| Agency servicing extract (book spine) | per agency | per agency | per agency | no (Oregon agencies) | OHCS yes |
| OHCS OAHI (inventory spine) | yes (546) | yes (163) | yes (101) | no | yes |
| OHCS 10-Year Forecast / PuSH notice log | yes | yes | yes | no | yes |
| OHCS HCA (PBCA) opt-out / renewal log | yes | yes | yes | no | yes |
| PHB loan portfolio / Preservation RFP | Portland only | no | no | no | no |
| Home Forward assets / PBV | yes | no (HAWC) | no (HACC) | no | no |
| HOME / CDBG PJ records | Portland Consortium | Washington County consortium | Clackamas County | no | state HOME |
| HUD FHASL, HUD Sec 8, HUD LIHTC, REAC, eGIS | yes | yes | yes | yes | yes |
| USDA MFH exit | few | few | few | some | yes |
| NHPD | yes | yes | yes | yes (WA extract) | yes |
| SOS registry / UCC | Oregon SOS | Oregon SOS | Oregon SOS | WA SOS (not verified) | Oregon SOS |
| Recorder (LURA / ROFR images) | MultcoRecords ($3.75 image, verify) | Washington Co. Recording (URL / fee unverified) | Clackamas Clerk (partial online) | Clark Auditor | county-specific; not in pack |
| Assessor exemption / delinquency | MultcoPropTax, DART reports | A&T Public Access | AscendWeb | not in pack | not in pack |
| Courts (book-risk stub) | OJD Smart Search | OJD | OJD | WA Odyssey (not verified) | OJD |
| City code enforcement | Portland BDS | none verified | none verified | not in pack | none |

## Verify-before-first-run checklist

Run `python3 scripts/smoke_test_sources.py --pack references/sources/oregon-portland` and then confirm by hand:

1. Every URL in `sources.md` resolves and the file sources return the expected header tokens (`dataset-schemas.yaml` `match_columns`). Flip `verified_live` only on success and only in `sources_status.json`. As of 2026-10-04 no government URL has been fetched (every host was egress-blocked); run `--live` from an unrestricted machine before the first run.
2. The agency servicing extract: run `python3 scripts/date_profile.py <extract>` and paste the proposed formats into the `agency_servicing_extract` block; confirm `book_kind`, `program`, `payment_type`, `covenant_status`, `recapture_method` vocabularies against the agency's system; confirm `notice_log_status` and `qc_*` columns exist or are blank (blank -> unknown, reported not scored).
3. ORS 456.259-.265 as amended through SB 973 (2025): the owner-notice months (the rule summary reads "no sooner than 30 and at least 24 months" before withdrawal; the 36-30 row in this pack is an INTERNAL prep window with no statutory basis found; the (1)/(2) split is unread), the designee-appointment paragraph ("after the owner delivers notice OR 30 months prior to expiry, whichever is earlier"), the ROFR two-step (offer with notice of intent to record, recording after 30 days) and its 24-month duration after withdrawal, the ORS 456.263 match content (affordability commitment; earnest-money / 240-day closing variations), the OAR 813-115-0050 records right (30-day response period not found), the title of ORS 456.265 ("Sanctions ... prohibited"), and the SB 973 operative date / 2028-07-01 phase-in (`market-params.json` `sb973_operative_restriction_date`). Read the statute text, not summaries, before any demand letter.
4. OAR 813 Division 115 section map (0010 / 0030 / 0035 / 0050 / 0060 / 0070) and the 30-day records response.
5. 2025 Oregon QAP and the first QAP year requiring a QC waiver; status of the OHCS Draft Qualified Contract Procedure (presentment removes the exit).
6. Oregon PBCA identity under HUD's 2024-2025 PBCA re-solicitation (`agency-profiles.yaml` `is_pbca`) before relying on the CA log as RECORDED.
7. HUD field names from the live FHASL, Sec 8 and REAC headers and from the ArcGIS layer `/0?f=pjson`.
8. `market-params.json` values flagged `verify`: every statutory day / month count, `senior_rate_default`, `ust10`, `recap_loan_rate`, product flags; `mandate.json` product windows and eligibility against the current OHCS NOFA and PHB RFP.
9. HOME affordability-period rules per written agreement for the PJ's book: pre / post 2025 final-rule vintage and dollar thresholds; 92.252(e) foreclosure-termination paragraph numbering.
10. OHCS OAHI release: re-run `scripts/date_profile.py` on the new file; if any declared format no longer fits, update `dataset-schemas.yaml` before running; confirm the 53-column header.
11. Whether a LIHTC extended-use agreement alone makes a property "publicly supported housing" under ORS 456.250 (affects which LIHTC-only rows get PuSH windows).
12. Home Forward RAD / Section 18 status and county acquisition program guidelines (`mandate.json` placeholders); confirm Portland Consortium membership for the `cdbg_home` profile.
13. Public-records posture: agency counsel review of the `pii-and-sunshine.md` packet redaction rules under ORS 192.345 / 192.355 before the first board packet.

## What a degraded run looks like here

With only the OHCS CSV in the inbox every lead is `universe_not_held` with `book_match = book_absent`: the our_capital_at_risk factor is 0 for every row, Board_Totals carries no public UPB, and the brief's Run Summary says "book absent: capital factor 0 for all rows; outputs are preservation targeting and notice compliance only". Every owner cliff is REPORTED (OHCS dates) or DERIVED (Year 15, PuSH windows, agency deadlines); `notice_status` is `unknown` for every PuSH-covered row, so no NOTICE_COMPLIANCE_BREACH is emitted and rows past their first-notice due date score 6 with `Verify — Notice Log`; 33 HUD dates are stale. Lifting it means adding, in order: the agency servicing extract (RECORDED maturities, affordability periods, covenant status, notice and QC logs), the OHCS 10-Year Forecast (preservation status and notice flips), the HUD MF Assistance & Sec 8 tape (current HAP expirations and owner organizations for the 236 blank-owner rows), HUD FHASL (senior maturities) and REAC. The brief must say which of these were absent.
