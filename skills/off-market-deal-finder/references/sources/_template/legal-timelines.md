# Legal Timelines: <State> (and <adjacent state> if the metro crosses a line)

Statutory clocks the event-derivation rules encode for this market. Cite section numbers from the current statute text, record the edition/date you read, and mark anything taken from summaries as `verify`. Nothing here is legal advice; equity-purchaser and preservation-law items need counsel before outreach language is finalized.

## 1. Mortgage / deed-of-trust foreclosure

State regime: <judicial | non-judicial | both>. Fill the table with the instruments that are actually recorded or filed and their timing, because the first recorded instrument is the skill's day 0.

| step | section | rule | event mapping |
|---|---|---|---|
| pre-foreclosure notice / contact requirement | <section> | <recorded? mailed only?> | <leading indicator or none> |
| first recorded or filed instrument (NOD / notice of sale / complaint) | <section> | <who records, where> | NOD_RECORDED / NOTS_RECORDED / JUDICIAL_FORECLOSURE_FILED |
| notice period before sale | <section> | <days> | TRUSTEE_SALE_EARLIEST = day 0 + <days> |
| publication | <section> | <frequency, last run before sale> | publication window |
| cure / reinstatement deadline | <section> | <days before sale> | CURE_DEADLINE = sale - <days> |
| postponement / continuance limits | <section> | <max days> | detail postponed |
| post-sale redemption (judicial) | <section> | <days> | |
| deficiency rules | <section> | <when barred; drives whether commercial lenders foreclose judicially> | |
| lis pendens | <section> | <exists?> | LIS_PENDENS |
| receivership | <section> | <grounds, powers> | RECEIVER_APPOINTED |
| maturity printed on recorded instrument | <section or practice> | <when required> | RECORDED maturity |

## 2. Liens and entity law

| instrument | section | timing | event mapping |
|---|---|---|---|
| mechanics / construction lien | <section> | <record within; suit within; expiry> | MECHANICS_LIEN |
| HOA / condominium lien | <section> | | JUDGMENT_LIEN (detail hoa) |
| partition | <section> | | PARTITION_FILED |
| LLC / LP annual report contents | <section> | <managers / members / GPs listed?> | decision-maker grades |
| administrative dissolution | <section> | <days after missed report; reinstatement window> | ENTITY_ADMIN_DISSOLVED |
| death records access | <section> | <restricted?> | probate / obituary detection |

## 3. Property-tax foreclosure

| step | rule | event mapping |
|---|---|---|
| delinquency date | <date after tax year> | TAX_DELINQUENT_YEARS |
| foreclosure list / certificate of delinquency | <years delinquent; when published; where> | TAX_FORECLOSURE_LIST |
| redemption | <period> | TAX_REDEMPTION_END |
| senior / disabled deferral lien | <program> | DOR_DEFERRAL_LIEN equivalent |
| utility liens certified to tax roll | <statute> | UTILITY_LIEN_CERTIFIED |

## 4. Preservation-notice law (publicly supported housing)

Copy the state's row from `references/sources/federal/preservation-notice-laws-by-state.md` and verify it against statute text.

| element | section | rule | status |
|---|---|---|---|
| definition of covered housing | | | verify |
| owner notice timing to agency / local government | | | verify |
| tenant notice | | | verify |
| purchase right / ROFR / offer period and its duration | | | verify |
| public registry of notices | | | verify |
| sanctions | | | verify |

## 5. LIHTC federal mechanics

IRC 42(i)(1) compliance period; 42(h)(6) extended use (state minimum beyond 15 years: <years>); 42(h)(6)(E)-(F) qualified contract (state policy: see `federal/qc-policy-by-state.md`); 42(h)(6)(E)(ii) three-year decontrol; 42(i)(7) nonprofit ROFR.

## 6. Outreach compliance

| law | rule | status |
|---|---|---|
| state telephone-solicitation / DNC statute | <does the state use the national registry? are texts covered?> | verify |
| TCPA | consent for autodialed / prerecorded / AI-voice calls and texts to cells; 8am-9pm | verify current |
| wholesaler registration / disclosure statute | <exists?> | verify |
| equity-purchaser / foreclosure-rescue statute | <exists? cancellation rights, leaseback rules> | counsel |
| fair housing overlay | tenant data used only for owner-motivation assessment | |
| bankruptcy stay | counsel only | |

## 7. Assessment regime

<Does assessed value track market value? Describe caps (e.g. acquisition-value systems) and what the roll exposes (market value, assessed value, exemptions). Set `av_is_market` in market-params.json accordingly and state the valuation rule for the skill.>

## 8. Rent and tenant regulation that drives motivation

| rule | source | current value | use |
|---|---|---|---|
| rent cap | | | rent-trap metric |
| relocation assistance | | | underwriting line and motivation |
| just-cause / screening / deposit rules | | | regulatory-fatigue angle |
| rental registration / inspection program | | | cost line; records-request signal |
