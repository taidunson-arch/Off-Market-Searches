# LIHTC Qualified-Contract Policy by State

Drives the HFA-side handling of `QC_ELIGIBILITY` in `affordable_public_am`. In this pack the agency administers the qualified contract (profile `administers_qc`) and the clock is the agency's: `QC_RESPONSE_DUE` = the complete request date + one year (IRC 42(h)(6)(I)); the termination trigger is 42(h)(6)(E)(i)(II); the price is 42(h)(6)(F) / Treas. Reg. 1.42-18. A `requested` status scores only when RECORDED from the agency's own QC log or a read REUA; `eligible` computed from allocation vintage alone is a watch note that never scores. Where the table says `not researched`, treat the state as `silent` with `verify` and read the current QAP before encoding anything.

Policy values: `prohibited` (agency bars QC requests as an allocation condition) | `waiver_required` (owner must waive QC right to receive an allocation) | `incentivized` (points or priority for waiving / extending) | `silent` (no stated policy; statutory QC right intact). Adoption year is the first allocation year the policy bound; earlier vintages retain QC rights unless their individual REUA says otherwise.

Context (Treasury "LIHTC Best Practices to Discourage Qualified Contracts", Dec 2024 per snippets; NCSHA Qualified Contract Background, Aug 2024; Tax Credit Advisor / Novogradac surveys): roughly 14 allocating agencies prohibit QC requests as a condition of allocation; most others require or incentivize waivers; roughly 115,000 units have left the program through QC nationally. The Year-15 ROFR case is SunAmerica Housing Fund 1050 v. Pathway of Pontiac, Inc., 33 F.4th 872 (6th Cir. 2022). None of these pages was fetched in this build; every row is `verified: no`.

| state | policy | adoption year | evidence / source | agency procedure note | verified |
|---|---|---|---|---|---|
| Oregon (OR) | unknown / likely `waiver_required` for recent allocations (OHCS Reservation and Extended Use Agreements and 2016+ QAPs are widely understood to require applicants to waive the QC option; absence from 2017-2019 waiver lists is weak negative evidence) | verify in OHCS QAP history (2016 reported; adoption year unconfirmed) | OHCS Draft Qualified Contract Procedure: the Department's only obligation is to present a bona fide signed contract at the QC price; once presented, regardless of closing, the extended use period can no longer be terminated. https://www.oregon.gov/ohcs/development/Documents/LIHTC/QAP/draft-qualified-contract-procedure.pdf ; https://www.oregon.gov/ohcs/rental-housing/housing-development/development-resources/Documents/QAP/2025-qap-final.pdf | `qc_waived` from the recorded REUA / Declaration (never from this table alone); `qc_waiver_acknowledgement` when true; `qc_request_acknowledgement` -> `qc_marketing_plan` ("present a contract") when false | no |
| California (CA) | prohibited | verify (TCAC regulations) | Treasury Dec 2024 names California among agencies prohibiting QC requests | no QC clock; `QC_REQUEST_INELIGIBLE` | no |
| Nevada (NV) | waiver_required | verify | Treasury Dec 2024 state examples | | no |
| Louisiana (LA) | waiver_required | verify | Treasury Dec 2024 | | no |
| North Dakota (ND) | waiver_required | verify | Treasury Dec 2024 | | no |
| Michigan (MI) | waiver_required | verify | Treasury Dec 2024 | MSHDA-style tenant QC status letters are a model for the tenant-notice element of `qc_request_acknowledgement` | no |
| Colorado (CO) | incentivized (points for 5-25 extra years) | verify | Treasury Dec 2024 | | no |
| Maine (ME) | incentivized / disqualifies prior QC requesters | verify | Treasury Dec 2024 | | no |
| North Carolina (NC) | incentivized / disqualifies prior QC requesters | verify | Treasury Dec 2024 | | no |
| New Hampshire (NH) | not researched; requires Year-15 investor / aggregator certification (NHHFA Exhibit 20) | verify | https://nhhfa.org/wp-content/uploads/2024/09/Exhibit-20-Year-15-Investor-and-Aggregators-Certification-.pdf | model for an aggregator certification the HFA can add to its QAP (sponsor_capacity lp_transfer_or_gp_change) | no |
| Washington (WA) | not researched | verify WSHFC QAP | | | no |
| other states | not researched | verify | current QAP; National Housing Trust state map; Novogradac / Tax Credit Advisor surveys | | no |

## How to fill a row

1. Open the state's current QAP and search for "qualified contract" in the threshold and selection-criteria sections; note whether a waiver is a threshold requirement (waiver_required), scored (incentivized), or barred by regulation (prohibited).
2. Find the first QAP year the policy appeared; that is the adoption year. Projects allocated earlier keep their statutory QC right unless their individual REUA says otherwise.
3. Read the HFA's QC procedure: what makes a request complete (starts the one-year clock), the price certification it demands, and whether presentment alone satisfies the agency's obligation.
4. Record the URL you read and set `verified: yes` with the date.
5. For any individual property the recorded Declaration / REUA / LURA governs over the table: read its QC clause and set `qc_waived` in the servicing extract.

## Scoring and routing linkage (agency side)

| QC status | declared_intent_vs_silence | restriction_hap_qc_clock | route / intervention | note |
|---|---|---|---|---|
| `requested` (RECORDED from the agency QC log; `qc_waived` != true) | 13 | `QC_RESPONSE_DUE` <= 12 months +4 | `qc_admin` (administers_qc) -> `qc_request_acknowledgement`, `qc_marketing_plan`; non-HFA profiles -> `ta_sponsor` / `nofa_offer` with `qc_coordination_with_hfa` | the one-year clock is the HFA's (42(h)(6)(I)); present a bona fide contract; presentment removes the exit |
| `lapsed_decontrol` (no contract presented inside the year) | 15 | — | `qc_admin` -> `qc_marketing_plan` (last-chance award); monitor the 42(h)(6)(E)(ii) three-year protection | `lost` only on evidence that extended use has ended |
| `eligible` (pre-waiver vintage, year >= 15, no waiver in the REUA) | 0 (watch note) | — | none; appears on the card as "QC-eligible vintage; no request on file" | never scores from vintage alone |
| `qc_waived` true | 0 | — | `QC_REQUEST_INELIGIBLE` -> `qc_waiver_acknowledgement` (no clock) | read from the recorded REUA |
| state `prohibited` | 0 | — | none | |
