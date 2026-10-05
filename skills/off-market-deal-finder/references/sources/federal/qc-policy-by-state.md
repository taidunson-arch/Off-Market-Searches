# LIHTC Qualified-Contract Policy by State

Drives `QC_ELIGIBILITY` (status `eligible`) in `affordable_regulated`: a project is QC-eligible when it is past year 14, its allocation vintage predates the state's waiver adoption year, the state does not prohibit QC requests, and the recorded REUA/LURA contains no waiver. For allocations made before a state adopted a waiver policy, QC remains available regardless of current policy. Where the table says `not researched`, treat the state as `silent` with `verify` and read the current QAP before scoring.

Policy values: `prohibited` (agency bars QC requests as an allocation condition) | `waiver_required` (owner must waive QC right to receive an allocation) | `incentivized` (points or priority for waiving / extending) | `silent` (no stated policy; statutory QC right intact). Adoption year is the first allocation year the policy bound; earlier vintages retain QC rights.

Context (Treasury "LIHTC Best Practices to Discourage Qualified Contracts", dated Dec 2024 per snippets; NCSHA 2017 recommended practice; Tax Credit Advisor / Novogradac survey): 14 allocating agencies reportedly prohibit QC requests as a condition of allocation; most others require or incentivize waivers for 9% and 4%; roughly 115,000 units have left the program through QC nationally, 6,000-10,000 per year. The leading Year-15 ROFR case is SunAmerica Housing Fund 1050 v. Pathway of Pontiac, Inc., 33 F.4th 872 (6th Cir. 2022). None of these pages was fetched in this build (home.treasury.gov blocked); every row is `verified: no` with its evidence note, and the Treasury figures stay unverified until the page is read.

| state | policy | adoption year | evidence / source | verified |
|---|---|---|---|---|
| Oregon (OR) | unknown / likely `waiver_required` for recent allocations (OHCS Reservation and Extended Use Agreements and QAPs are widely understood to require applicants to waive the qualified-contract option; absence from 2017-2019 waiver lists is weak negative evidence) | verify in OHCS QAP history (adoption year unknown) | Oregon absent from 2017-2019 mandatory-waiver state lists; OHCS has a draft Qualified Contract Procedure PDF and REUAs of >= 15 years beyond compliance (LIFT 60 years). Set `QC_ELIGIBILITY.status = eligible` for an Oregon property only after reading that property's recorded REUA / Declaration (no waiver clause) and the QAP for its allocation year; never from this table alone. https://www.oregon.gov/ohcs/rental-housing/housing-development/development-resources/Documents/QAP/2025-qap-final.pdf | no |
| California (CA) | prohibited | verify (TCAC regulations; reported among the 14 prohibiting agencies) | Treasury Dec 2024 names California among agencies prohibiting QC requests | no |
| Nevada (NV) | waiver_required | verify | Treasury Dec 2024 state examples | no |
| Louisiana (LA) | waiver_required | verify | Treasury Dec 2024 state examples | no |
| North Dakota (ND) | waiver_required | verify | Treasury Dec 2024 state examples | no |
| Michigan (MI) | waiver_required | verify | Treasury Dec 2024 state examples | no |
| Colorado (CO) | incentivized (points for 5-25 extra years of affordability) | verify | Treasury Dec 2024 state examples | no |
| Maine (ME) | incentivized / disqualifies prior QC requesters | verify | Treasury Dec 2024 state examples | no |
| North Carolina (NC) | incentivized / disqualifies prior QC requesters | verify | Treasury Dec 2024 state examples | no |
| Washington (WA) | not researched | verify WSHFC QAP / policies | Relevant for Clark County; WSHFC not reached in this build | no |
| other states | not researched | verify | Fill from the current QAP; National Housing Trust publishes a state map (not retrieved) and Novogradac/Tax Credit Advisor survey QC volume by state | no |

## How to fill a row

1. Open the state's current QAP and search for "qualified contract" in the threshold and selection-criteria sections; note whether a waiver is a threshold requirement (waiver_required), scored (incentivized), or barred by regulation (prohibited).
2. Find the first QAP year the policy appeared; that is the adoption year. Projects allocated earlier keep their statutory QC right unless their individual REUA says otherwise.
3. Record the URL you read and set `verified: yes` with the date.
4. For any individual target, the recorded Declaration / REUA / LURA governs over the table: read its QC clause.

## Scoring linkage

| QC status | points (declared_intent_and_notice) | note |
|---|---|---|
| `eligible` (pre-waiver vintage, year >= 15, no waiver) | 8 | owner holds a conversion lever |
| `requested` (confirmed with the agency) | 17 | one-year clock running |
| `lapsed_decontrol` (agency failed to present a QC) | 20 | 3-year decontrol; conversion or last-chance preservation |
| state `prohibited` or REUA waiver | 0 | do not score QC |
