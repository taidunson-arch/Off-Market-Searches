# Pipeline Contract

Canonical vocabulary, tables and file formats shared by every script, module and output of `off-market-deal-finder`. When any other file in this skill disagrees with this one, this file governs and the other file should be reconciled.

## Contents

1. Enumerations
2. Basis levels and verify flags
3. Event taxonomy
4. Event validation rules
5. Canonical lead table (leads.csv)
6. Companion events table (events.csv)
7. Rejects table (rejects.csv)
8. Calendar summary (calendar_summary.json)
9. Run manifest (runs/<as_of>/manifest.json)
10. Diff semantics (diff.csv)
11. Scoring JSON schema (references/scoring/*.json)
12. Identity and join rules

---

## 1. Enumerations

Use these exact strings. Scripts reject unknown values rather than coercing them.

| Enum | Values |
|---|---|
| `asset_class` | `sfr_small_res` \| `market_rate_mf` \| `affordable_regulated` (inputs may also say `all` \| `auto`) |
| `query_type` | `distress` \| `maturity` \| `regulatory_expiry` \| `all` |
| `geography_mode` | `city_limits` \| `county` \| `metro_core` \| `cbsa` \| `custom` |
| `geo_grade` | `county_field` \| `zip_crosswalk` \| `point_in_polygon` \| `city_name_weak` |
| `basis` | `RECORDED` \| `REPORTED` \| `DERIVED` \| `ESTIMATED` \| `PROXY` |
| `verify_flag` | `null` \| `Verify — Ambiguous` \| `Verify — Conflicting Sources` \| `Needs Anchor Date` \| `Missing Source — Request Document` \| `Rejected — Out of Range` \| `No Format Declared` |
| `event_family` | `DEBT` \| `REGULATORY` \| `HARD_DISTRESS` \| `TAX_LIEN` \| `PHYSICAL` \| `OWNERSHIP` \| `OPERATING` |
| `direction` | `PRESSURE` \| `SUPPRESSION` \| `ROUTING` |
| `urgency_band` | `CRITICAL` (0-12 mo) \| `URGENT` (12-24) \| `APPROACHING` (24-36) \| `MONITOR` (36-60) \| `SCHEDULED` (60+) |
| `owner_type` | `individual_occupant` \| `individual_absentee` \| `trust_estate` \| `single_asset_llc` \| `regional_operator` \| `institutional` \| `lihtc_partnership_forprofit_gp` \| `lihtc_partnership_nonprofit_gp` \| `nonprofit` \| `housing_authority` \| `government` \| `lender_reo_receiver` \| `unknown` |
| `contact_grade` | `A` \| `B` \| `C` (definitions in `decision-maker-enrichment.md`) |
| `route` | `acquisition` \| `partnership_preservation` \| `lender_counterparty` \| `assumption_play` \| `watch` \| `excluded` |
| `tier` | `A` (score >= 70) \| `B` (50-69) \| `C` (30-49) \| `WATCH` (< 30 with any dated PRESSURE event inside horizon) \| `EXCLUDED` |
| `buyer_profile` | `principal` \| `wholesaler` \| `nonprofit_preservation` \| `qualified_purchaser` |
| `lender_type` | `hud_fha` \| `fannie_dus` \| `freddie_k_sb` \| `cmbs` \| `bank_cu` \| `life_co` \| `debt_fund_bridge` \| `usda_rd` \| `state_soft` \| `local_soft` \| `hecm` \| `seller_private` \| `unknown` |
| `program` | `LIHTC_9` \| `LIHTC_4` \| `HAP` \| `PRAC` \| `RAC` \| `PAC` \| `HUD_INSURED` \| `HUD_236` \| `HUD_202_811` \| `USDA_515` \| `HOME` \| `OAHTC` \| `GHAP` \| `HDGP` \| `LIFT` \| `HTF` \| `OTHER_OHCS` \| `LOCAL_REG` \| `IH_SET_ASIDE` |

Portland `geography_mode` definitions: `county` = 41051; `metro_core` = 41051, 41067, 41005; `cbsa` = 41005, 41009, 41051, 41067, 41071, 53011, 53059. See `sources/oregon-portland/geography.md`.

Urgency band timing-factor fraction of maximum points: CRITICAL 1.00, URGENT 0.75, APPROACHING 0.50, MONITOR 0.25, SCHEDULED 0.

## 2. Basis levels and verify flags

A date or dollar figure is only as good as where it came from. Every value carries a `basis` and a `source`; scoring multiplies factor points by the basis multiplier of the governing event. Keeping the five levels separate is what lets a user see "7 recorded maturities, 40 proxies" instead of "47 loans coming due".

| basis | multiplier | meaning | typical examples | what upgrades it |
|---|---|---|---|---|
| `RECORDED` | 1.00 | taken from a recorded instrument, court order, or a government ledger that is the system of record for that loan or program | HUD FHASL Maturity Date, recorder index NOD, trust-deed image maturity, SOS status | nothing; this is the ceiling |
| `REPORTED` | 0.90 | reported by a party to the loan or program to a disclosure system; current but not the instrument itself | DUS Disclose / MSIA / EX-102 maturity, HUD Sec 8 `tracs_overall_expiration_date`, OHCS `*_Expiration_Date`, REAC score | recorded instrument or executed contract via `critical-dates-tracker` |
| `DERIVED` | 0.80 | arithmetic on a RECORDED or REPORTED anchor using a rule fixed by statute or program design | Year 15 = Dec 31 (YR_PIS + 14); HUD prepay window = final endorsement + 10y; cure deadline = sale - 5 d | the program document stating the actual date (LURA, note) |
| `ESTIMATED` | 0.50 | arithmetic on a RECORDED anchor using a market convention, with an explicit window | recording_date + lender-type term (5/7/10y); bridge cap expiry = origination + 2-3y | trust-deed image read; lender tape |
| `PROXY` | 0.30 | a stand-in from a dataset that does not describe the thing being dated | OHCS `Financial_Closing_Date + 15y` as loan maturity | any of the above |

`AMBIGUOUS` is not a basis. A value whose format could not be disambiguated keeps its declared basis but carries `verify_flag = Verify — Ambiguous`, which forces the multiplier to 0.40 regardless of basis and stores both parses in `alt_dates`.

Verify flags (vocabulary shared with `critical-dates-tracker`):

| flag | when to set | downstream effect |
|---|---|---|
| `Verify — Ambiguous` | slash date with both fields <= 12 under `format: auto`; two candidate parses | multiplier 0.40; `alt_dates` populated; appears in Rejects_Verify tab |
| `Verify — Conflicting Sources` | two sources give different dates for the same event (e.g. OHCS LATEST != max of components; expiration before compliance start) | keep the higher-basis value; list alternates; appears in Rejects_Verify |
| `Needs Anchor Date` | a DERIVED/ESTIMATED event has no anchor (no YR_PIS, no closing date, no recording date) | event not emitted; property keeps row with flag |
| `Missing Source — Request Document` | event exists only below RECORDED and a document would settle it | listed in `documents_to_request` for `critical-dates-tracker` |
| `Rejected — Out of Range` | fails a Section 4 validation | row written to rejects.csv; event not scored |
| `No Format Declared` | column has date-like values but no schema format | adapter stops; user runs `date_profile.py` |

## 3. Event taxonomy

One list for all three classes. Names align to the Loan/Financing and Regulatory/Compliance categories in `critical-dates-tracker` so the two skills' outputs join on `event_type`. Classes: 1 = `sfr_small_res`, 2 = `market_rate_mf`, 3 = `affordable_regulated`.

| event_type | family | classes | derivation / source | default basis | default window |
|---|---|---|---|---|---|
| LOAN_MATURITY | DEBT | 2,3 | HUD FHASL `Maturity Date`, Ginnie Mae, recorder image (RECORDED); DUS/MSIA/EX-102 (REPORTED); recording_date + term(lender_type) (ESTIMATED, window rec+min_term..rec+max_term); `Financial_Closing_Date + 15y` (17y if LIHTC_4) (PROXY, +/-36 mo) | per source | 0 |
| IO_EXPIRATION | DEBT | 2 | first_payment + io_term (tape) | REPORTED | 0 |
| PREPAY_WINDOW_OPEN | DEBT | 2,3 | max(lockout_end, ym_end, premium_end) (REPORTED); HUD final_endorsement + 10y (DERIVED) | REPORTED/DERIVED | +/-6 mo |
| RATE_CAP_EXPIRY | DEBT | 2 | bridge origination + initial term (2-3y) | ESTIMATED | +/-12 mo |
| LOAN_MODIFIED | DEBT | 2 | recorded Modification/Extension; CMBS modifiedIndicator | RECORDED | 0 |
| SPECIAL_SERVICING | HARD_DISTRESS | 2 | CMBS mostRecentSpecialServicerTransferDate with null return date | RECORDED | 0 |
| MATURED_BALLOON | HARD_DISTRESS | 2 | CMBS paymentStatus 4 (performing) / 5 (non-performing); store `value` = 4 or 5 | RECORDED | 0 |
| WATCHLIST | OPERATING | 2 | trustee IRP watchlist / MSIA flag | REPORTED | 0 |
| REFINANCE_CLOSED | DEBT (SUPPRESSION) | all | FHASL Terminated row, or Reconveyance followed <= 90 d by new trust deed; emits SUPPRESS_UNTIL = new_orig + min_term(lender_type) | RECORDED | 0 |
| UNENCUMBERED | OWNERSHIP | all | Reconveyance with no new lien | RECORDED | 0 |
| UCC_MEZZ_PLEDGE | HARD_DISTRESS | 2,3 | SOS UCC debtor = owner; collateral = membership interests | RECORDED | 0 |
| UCC_ART9_SALE | HARD_DISTRESS | 2,3 | Article 9 disposition notice | RECORDED | 0 |
| LIHTC_COMPLIANCE_END | REGULATORY | 3 | Dec 31 of (YR_PIS + 14); fallback Compliance_Start_Date + 15y; flag `+15 election possible` | DERIVED (0.80) | +12 mo |
| LIHTC_EXTENDED_USE_END | REGULATORY | 3 | OHCS LIHTC_4/9_Expiration_Date or LURA (REPORTED); fallback Dec 31 (YR_PIS + 29) (DERIVED) | REPORTED | 0 |
| QC_ELIGIBILITY | REGULATORY | 3 | year >= 15 and allocation vintage before state waiver year and state does not prohibit; `status` in {eligible, requested, lapsed_decontrol} | DERIVED | 0 |
| HAP_EXPIRATION | REGULATORY | 3 | HUD `tracs_overall_expiration_date`; OHCS HUD_MF_Expiration_Date | REPORTED, confidence 0.70 when renewal term <= 5y or unknown; 0.90 when 20-year MAHRA renewal | 0 |
| HAP_OPTOUT_NOTICE_DEADLINE | REGULATORY | 3 | HAP_EXPIRATION - 12 mo | DERIVED | 0 |
| PRESERVATION_NOTICE_WINDOW | REGULATORY | 3 | per-state statute; Oregon first notice = expiration - 36..30 mo, second = - 30..24 mo | DERIVED | window stored |
| PRESERVATION_NOTICE_RECEIVED | REGULATORY | 3 | state forecast-list status flip; records request; PBCA opt-out log; `detail` in {push_first, push_second, hap_optout} | RECORDED | 0 |
| ROFR_RECORDED | REGULATORY (ROUTING) | 3 | recorder index "Notice of Right of First Refusal" / designee agreement | RECORDED | 0 |
| HUD_DIRECT_LOAN_MATURITY | DEBT | 3 | FHASL rows with SOA in {236, 221(d)(3), 202} | RECORDED | 0 |
| USDA_515_MATURITY | DEBT | 3 | USDA MFH exit data; OHCS USDA_RD_Expiration_Date | RECORDED / REPORTED | 0 |
| USDA_515_PREPAY_ELIGIBLE | DEBT | 3 | USDA MFH exit data prepay flag/date | RECORDED | 0 |
| USDA_EXIT_PROJECTED | DEBT | 3 | USDA estimated exit year | REPORTED | +/-12 mo |
| SOFT_PROGRAM_END | REGULATORY | 3 | each OHCS HOME/OAHTC/GHAP/HDGP/LIFT/HTF/Other_OHCS date (affordability period end, not a note maturity) | REPORTED | 0 |
| SOFT_LOAN_MATURITY | DEBT | 3 | only when a recorded trust deed, PHB loan record or loan doc states it | RECORDED | 0 |
| REGULATORY_LATEST_END | REGULATORY | 3 | LATEST_Expiration_Date (recompute as max of components when blank) | REPORTED | 0 |
| NOD_RECORDED | HARD_DISTRESS | 1,2 | Oregon combined Notice of Default and Election to Sell (ORS 86.752) | RECORDED | 0 |
| SUCCESSOR_TRUSTEE_APPOINTED | HARD_DISTRESS | 1 | recorder index (pre-NOD leading indicator) | RECORDED | 0 |
| OFAP_CERT_RECORDED | HARD_DISTRESS | 1 | recorder index Certificate of Compliance / exemption affidavit (ORS 86.736, 86.726) | RECORDED | 0 |
| NOTS_RECORDED | HARD_DISTRESS | 1,2 | Washington Notice of Trustee's Sale (RCW 61.24.040) | RECORDED | 0 |
| TRUSTEE_SALE_EARLIEST | HARD_DISTRESS | 1,2 | OR: NOD + 120 d; WA: NOTS + 90/120 d | DERIVED | 0 |
| CURE_DEADLINE | HARD_DISTRESS | 1,2 | OR: sale - 5 d; WA: sale - 11 d | DERIVED | 0 |
| NOD_RESCISSION | HARD_DISTRESS (SUPPRESSION) | 1,2 | recorder | RECORDED | 0 |
| TRUSTEES_DEED | HARD_DISTRESS (ROUTING) | 1,2 | recorder | RECORDED | 0 |
| JUDICIAL_FORECLOSURE_FILED | HARD_DISTRESS | 1,2 | court index (ORS 88) | RECORDED | 0 |
| LIS_PENDENS | HARD_DISTRESS | 1,2 | recorder (ORS 93.740) | RECORDED | 0 |
| RECEIVER_APPOINTED | HARD_DISTRESS (ROUTING) | 2 | court order (ORS ch. 37) | RECORDED | 0 |
| BANKRUPTCY_FILED | HARD_DISTRESS (ROUTING) | all | PACER; `detail` chapter and SARE flag | RECORDED | 0 |
| CH13_DISMISSED | HARD_DISTRESS | all | PACER (a dismissed Chapter 13 lets the foreclosure resume: PRESSURE, not routing) | RECORDED | 0 |
| PROBATE_FILED | OWNERSHIP | all | OJD Smart Search (PR cases) | RECORDED | 0 |
| DISSOLUTION_FILED | OWNERSHIP | all | OJD civil (entity dissolution) or domestic relations; `detail` says which | RECORDED | 0 |
| PARTITION_FILED | OWNERSHIP | all | OJD civil (ORS 105) | RECORDED | 0 |
| ENTITY_ADMIN_DISSOLVED | OWNERSHIP | all | SOS registry status | RECORDED | 0 |
| MANAGER_CHANGE | OWNERSHIP | all | SOS annual report diff | RECORDED | 0 |
| REGISTERED_AGENT_CHANGE | OWNERSHIP | all | SOS annual report diff | RECORDED | 0 |
| HECM_ON_RECORD | OWNERSHIP | 1 | recorder (2nd trust deed to Secretary of HUD) | RECORDED | 0 |
| DOR_DEFERRAL_LIEN | OWNERSHIP | 1 | recorder (Oregon DOR senior/disabled deferral lien) | RECORDED | 0 |
| TAX_DELINQUENT_YEARS | TAX_LIEN | all | assessor payment history; `value` = 1 / 2 / 3+ | RECORDED | 0 |
| TAX_FORECLOSURE_LIST | TAX_LIEN | all | county list (ORS 312 / RCW 84.64) | RECORDED | 0 |
| TAX_REDEMPTION_END | TAX_LIEN | all | judgment date + 2 y | DERIVED | 0 |
| MECHANICS_LIEN | TAX_LIEN | all | recorder Claim of Lien (ORS 87) | RECORDED | 0 |
| JUDGMENT_LIEN | TAX_LIEN | all | recorder / OJCIN judgment index | RECORDED | 0 |
| CODE_LIEN_REFERRAL | TAX_LIEN | all | council ordinances / committee referral lists | RECORDED | 0 |
| UTILITY_LIEN_CERTIFIED | TAX_LIEN | all | annual certification ordinance | RECORDED | 0 |
| CODE_CASE_OPEN | PHYSICAL | all | BDS open-case lists, PortlandMaps; `detail` case type | REPORTED | 0 |
| DANGEROUS_BUILDING | PHYSICAL | all | BDS dangerous-building list | REPORTED | 0 |
| REAC_SCORE | OPERATING | 3 | HUD inspection file (`value` score, `detail` protocol) | REPORTED | 0 |
| TAX_EXEMPTION_LOST | OPERATING | 3 | assessor exemption-code diff | RECORDED | 0 |
| STABILIZATION_AWARD | OPERATING | 3 | HFA award list | RECORDED | 0 |
| OCCUPANCY_DROP | OPERATING | 2 | tape | REPORTED | 0 |
| LISTING_WITHDRAWN | OPERATING | 2 | CoStar / LoopNet | REPORTED | 0 |
| MGMT_CHANGE | OPERATING | 2 | observed | REPORTED | 0 |
| INSURANCE_NONRENEWAL_CONFIRMED | OPERATING | 2 | confirmed only (owner, broker, filing text) | REPORTED | 0 |
| HOLD_YEARS | OWNERSHIP | all | assessor DEED_DATE / SALE_DATE; `value` years | RECORDED | n/a |
| DEPRECIATION_EXHAUSTED | OWNERSHIP | all | HOLD_YEARS >= 27.5 | RECORDED | n/a |
| RECENT_1031_ACQUISITION | OWNERSHIP (SUPPRESSION) | all | hold < 3 y with exchange language / typical lender; drives the shared -10 penalty, never pressure | RECORDED | n/a |
| ABSENTEE_TIER | OWNERSHIP | all | mailing vs situs; `value` in {local, in_state, out_of_state, far} | RECORDED | n/a |
| SUPPRESS_UNTIL | DEBT (SUPPRESSION) | all | from REFINANCE_CLOSED | DERIVED | 0 |

Direction defaults: events marked SUPPRESSION or ROUTING in the family column carry that `direction`; all others are `PRESSURE`. `scripts/omdf/schema.py` `EVENT_TAXONOMY` is generated to match this table and `scripts/tests/test_contract.py` fails when the two drift.

Helper deadlines: `PRESERVATION_NOTICE_WINDOW` and `HAP_OPTOUT_NOTICE_DEADLINE` are arithmetic on another event of the same property, and `REGULATORY_LATEST_END` restates a component program end when the dates coincide. They are never a property's `first_*` event and are reported on the calendar header's `helper deadlines` line, outside the five basis counts (Section 8).

## 4. Event validation rules

Run before an event is accepted; failures write a rejects.csv row with `Rejected — Out of Range` and the event is not scored.

| rule | applies to | test |
|---|---|---|
| loan range | DEBT events with an origination anchor | `orig_date < event_date < orig_date + 45 years` |
| subsidy anchor | REGULATORY events when `Compliance_Start_Date` present | `event_date >= Compliance_Start_Date` (fail -> `Verify — Conflicting Sources`, not rejected, per OHCS schema) |
| plausible year | all | `1960 <= year <= 2100` |
| development status | all | `Status != In Development` (row excluded entirely, counted in `rows_excluded_in_development`) |
| month sanity | all slash dates | parsed month <= 12 (a declared format that produces month > 12 means the declaration is wrong; stop and re-profile) |

## 5. Canonical lead table (leads.csv)

Flat CSV, one row per property. Same column names appear in JSON `leads[]` and in the workbook `Targets` tab.

| column | type | notes |
|---|---|---|
| `property_id` | string | `{state}-{county_fips}-{parcel_id}` when parcel known; else `addr:` + first 12 hex of sha1(upper USPS-normalized address + zip5) |
| `property_name` | string | as in source; OHCS keys on `Property Name + Address` |
| `address`, `city`, `zip` | string | USPS-normalized address; zip5 |
| `county_fips`, `county_name` | string | 5-digit FIPS; title-cased name |
| `jurisdiction` | string | city or `Unincorporated {County}` |
| `geo_modes` | pipe list | modes the property satisfies, e.g. `county|metro_core|cbsa` |
| `geo_grade` | enum | how geography was established |
| `lat`, `lon` | float | from Geocode WKT or ArcGIS layer; blank if unknown |
| `asset_class` | enum | |
| `status` | string | source status (Active etc.) |
| `units` | int | total units |
| `year_built`, `rehab_year` | int | |
| `property_type` | string | source value after dropping `0` / `ERROR: #N/A` |
| `programs` | `;` list | `program` enum values |
| `hud_contract` | string | HAP / PRAC / RAC / PAC / blank |
| `ami_30_60_units`, `ami_80_units`, `market_rate_units`, `rental_assistance_units` | int | |
| `owner_name`, `developer_name`, `manager_name` | string | as in source |
| `owner_type` | enum | |
| `owner_archetype` | string | template id from `decision-maker-enrichment.md` |
| `decision_maker_name`, `decision_maker_role`, `dm_source` | string | `not in public record` when unresolved |
| `contact_grade` | enum | |
| `first_debt_event_type`, `first_debt_event_date`, `first_debt_months_out`, `first_debt_basis`, `first_debt_source` | | earliest DEBT-family PRESSURE event within `horizon_years`, not suppressed |
| `first_reg_event_type`, `first_reg_event_date`, `first_reg_months_out`, `first_reg_basis`, `first_reg_source` | | earliest REGULATORY-family PRESSURE event within `regulatory_horizon_years` |
| `events_in_horizon` | JSON list | `{event_type, event_date, months_out, basis, confidence, source, verify_flag, alt_dates, window_start, window_end, direction}` |
| `est_value`, `value_source` | number, string | see `capital-stack-math.md` |
| `est_noi`, `noi_source` | number, string | |
| `est_loan_balance`, `balance_basis` | number, enum | |
| `est_ltv`, `est_dscr_refi`, `refi_gap_pct`, `equity_cushion_pct` | float | blank when inputs missing |
| `assumable_debt` | bool | HUD / agency loans |
| `signals` | `;` list | signal tokens that fired |
| `verify_flags` | `;` list | |
| `score_raw`, `motivation_score` | number | before / after multipliers and caps |
| `tier`, `route` | enum | |
| `outreach_angle`, `outreach_template` | string | template id from `assets/outreach-templates/` |
| `compliance_gates` | `;` list | gate ids from `outreach-and-compliance.md` |
| `verify_before_outreach` | string | human-readable list |
| `next_action` | string | |
| `source_vintages` | string | `source_id=vintage;...` |
| `as_of_date` | date | run date |

`months_out` = (event_date - as_of_date).days / 30.4, rounded to one decimal.

## 6. Companion events table (events.csv)

One row per event. Columns: `event_id, property_id, event_type, event_family, direction, event_date, months_out, urgency_band, basis, confidence, source, source_vintage, derivation, program, detail, value, verify_flag, alt_dates, window_start, window_end, status, event_date_quality` (`scripts/omdf/schema.py` `EVENT_COLUMNS`; `test_contract.py` compares the two lists).

- `event_id` is unique within a run and adapter-defined (`{property_id}:{n}` for the OHCS adapter, `{property_id}:{event_type}:{date}` for the others); join on `property_id` + `event_type` + `event_date` across runs, never on `event_id`.
- `urgency_band` is the Section 1 band for `months_out`; `program` is the `program` enum value the event belongs to (blank when none); `event_date_quality` in `declared_format | auto_unambiguous | ambiguous | rejected | blank` records how the date was parsed.
- `status` in `FUTURE | PAST | SUPPRESSED | RETIRED | REJECTED`. SUPPRESSED is set by `merge_leads.py` on DEBT events while `SUPPRESS_UNTIL` is in the future; RETIRED when a SUPPRESSION or ROUTING event closes the lead (NOD_RESCISSION, TRUSTEES_DEED); REJECTED rows are kept for the Rejects_Verify tab and never scored.
- `derivation` is a human-readable formula, e.g. `Financial_Closing_Date + 15y mini-perm (17y 4% bond)`.

## 7. Rejects table (rejects.csv)

`property_key, property_id, column, raw_value, reason, flag, alt_dates`. Every row in the workbook `Rejects_Verify` tab comes from this file: parse rejections (`Rejected — Out of Range`) plus lead-level conflict flags (`Verify — Conflicting Sources`, `Verify — Ambiguous`). The tab's row count therefore equals `rejected + verify-flag rows` as reported in the Summary; `Missing Source — Request Document` requests go to `documents_to_request.csv`, not here.

## 8. Calendar summary (calendar_summary.json)

```jsonc
{
  "as_of": "YYYY-MM-DD",
  "horizon_years": 5,
  "regulatory_horizon_years": 5,
  "rows_in_geography": 810,
  "rows_excluded_in_development": 0,
  "by_basis": {"RECORDED": 0, "REPORTED": 0, "DERIVED": 0, "ESTIMATED": 0, "PROXY": 0},
  "by_family": {"DEBT": 0, "REGULATORY": 0, "HARD_DISTRESS": 0, "TAX_LIEN": 0, "PHYSICAL": 0, "OWNERSHIP": 0, "OPERATING": 0},
  "suppressed": 0,
  "rejected": 0,
  "helper_events": 0,
  "helper_by_type": {"PRESERVATION_NOTICE_WINDOW": 0, "HAP_OPTOUT_NOTICE_DEADLINE": 0, "REGULATORY_LATEST_END": 0},
  "push_window_open_count": 0,
  "header": "RECORDED 0 / REPORTED 0 / DERIVED 0 / ESTIMATED 0 / PROXY 0 / Suppressed 0 / Rejected 0 | helper deadlines 0 (notice arithmetic, LATEST duplicates; not counted above)"
}
```

The `header` string is what the brief quotes before any count of "loans coming due". The five basis counts cover PRESSURE events that carry their own information; helper deadlines (notice arithmetic on another event of the same property) and `REGULATORY_LATEST_END` rows that duplicate a component date are counted on the trailing `helper deadlines` segment so that `DERIVED` means Year-15 dates, not notice arithmetic (`scripts/omdf/calendar.py`).

## 9. Run manifest (runs/<as_of>/manifest.json)

```jsonc
{
  "as_of": "YYYY-MM-DD",
  "market_id": "us-or-multnomah",
  "config": {},                                  // full run_config snapshot
  "inputs": [{"file": "", "schema": "", "sha256": "", "vintage": "YYYY-MM-DD", "vintage_source": "filename | mtime | header"}],
  "pack": "references/sources/oregon-portland",
  "omdf_version": "2.0.x",
  "flags": {"query_type": "all", "buyer_profile": "principal", "owner_types_include": null, "owner_types_exclude": null, "lender_types": null,
            "price_or_value_band": null, "strict_size_fit": false, "unit_range": [5, null], "programs": null},
  "sources_verified_live_false": ["..."],
  "outputs": {"run_dir_files": [], "handoff_files": [], "worklists": ["handoff/sos_worklist.csv", "handoff/documents_to_request.csv"]}
}
```

## 10. Diff semantics (diff.csv)

Compared on `property_id` between this run and `--prior-run`. Columns: `property_id, property_name, change, prior_tier, new_tier, prior_score, new_score, prior_first_event, new_first_event, retiring_event, note`.

| change | rule |
|---|---|
| `new` | present now, absent in prior |
| `escalated` | tier moved toward A, or score up >= 10, or first event moved closer by >= 6 months |
| `de_escalated` | tier moved toward C/WATCH, or score down >= 10, or SUPPRESS_UNTIL set |
| `retired` | removed by a SUPPRESSION/ROUTING event (`retiring_event` names it) or fell outside geography/horizon |
| `unchanged` | not written unless `--diff-all` |

## 11. Scoring JSON schema (references/scoring/*.json)

Each class file:

```jsonc
{
  "class": "market_rate_mf",
  "version": "2.0",
  "total_weight": 100,
  "factors": [
    {
      "name": "capital_stack_timing",
      "weight": 25,
      "take": "max",                    // max | sum across matched bands (then modifiers added)
      "event_driven": true,             // true: bands match events.csv rows; false: bands match lead columns
      "apply_basis_multiplier": true,
      "bands": [
        {
          "id": "debt_0_12",
          "event_type": "LOAN_MATURITY",      // must exist in Section 3, or null for attribute bands
          "signal": null,                     // lead column or signal token for attribute bands
          "match": {"field": "months_out", "op": "between", "value": [0, 12]},
          "points": 17,
          "reading": "one line: how the seller-side decision maker experiences it",
          "lever": "approach angle"
        }
      ],
      "modifiers": [ /* same shape as bands; always additive after take */ ],
      "cap": 25,
      "notes": ""
    }
  ],
  "hard_filters": [],
  "routes": [],
  "quality_rules": []
}
```

`match.op` values: `between` (inclusive low, exclusive high unless `inclusive: true`), `lt`, `lte`, `gt`, `gte`, `eq`, `in`, `exists`, `days_since_between`. `match.field` for event bands is one of `months_out`, `value`, `detail`, `days_since`, `status`; for attribute bands it is a lead column. Multiple conditions use `"all": [...]`. Shared mechanics live in `shared_adjustments.json`; class files never restate multipliers or tier bands.

## 12. Identity and join rules

- Normalize addresses with USPS abbreviations, strip unit designators for building-level keys, upper-case, collapse whitespace.
- HUD Project Number vs Ginnie Mae case number: compare digits only.
- OHCS rows: key `Property Name + Address`; never row order (row count changed 1,763 -> 1,819 between releases).
- Fuzzy fallback in `merge_leads.py`: upper(name) + zip5 token-set ratio >= 0.92, logged to `merge_log.csv`.
- When two sources disagree on a field, keep the higher basis; store the alternate in `alt_dates` (dates) or `alt_values` (numbers) and set `Verify — Conflicting Sources` if the gap is material (dates > 6 months; balances > 15%).
- SAIL, PortlandMaps and RLIS taxlots share county upstream data; agreement among them is not corroboration. Recorder documents and court records are the independent legs.
