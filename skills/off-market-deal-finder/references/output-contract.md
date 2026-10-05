# Output Contract

The fixed structure of everything `off-market-deal-finder` produces: the JSON result, the Excel workbook, the markdown brief, and the handoff payloads for sibling skills. The structure is the deliverable's contract; vary the content, not the shape. Column names repeat `pipeline-contract.md` Section 5 exactly.

## Contents

1. JSON result (full jsonc)
2. Excel workbook specification
3. Markdown brief template
4. Lead card format
5. Handoff payload field maps
6. Pipeline Mode checkpoint

---

## 1. JSON result

```jsonc
{
  "run": {
    "skill": "off-market-deal-finder",
    "version": "2.0",
    "as_of_date": "YYYY-MM-DD",                       // date.today() unless --as-of
    "market_id": "us-or-multnomah",
    "asset_class": "sfr_small_res | market_rate_mf | affordable_regulated | all",
    "query_type": "distress | maturity | regulatory_expiry | all",
    "horizon_years": 5,
    "regulatory_horizon_years": 5,
    "buyer_profile": "principal | wholesaler | nonprofit_preservation | qualified_purchaser",
    "unit_range": [5, null],
    "price_or_value_band": [null, null],
    "strict_size_fit": false,
    "programs_filter": ["LIHTC_9", "HAP"],
    "max_results": 100,
    "degraded": true,                                 // true when Tier A is impossible with the files present
    "degraded_reason": "string | null",
    "manifest_path": "runs/YYYY-MM-DD/manifest.json"
  },
  "geography": {
    "mode": "city_limits | county | metro_core | cbsa | custom",
    "label": "Portland metro core (Multnomah, Washington, Clackamas)",
    "county_fips": ["41051", "41067", "41005"],
    "jurisdictions": ["Portland", "Gresham", "Beaverton"],
    "resolution_order": ["county_field", "zip_crosswalk", "point_in_polygon", "city_name_weak"],
    "rows_by_grade": {"county_field": 810, "zip_crosswalk": 0, "point_in_polygon": 0, "city_name_weak": 0},
    "sources_stopping_at_state_line": ["ohcs_oahi", "metro_rlis_affordable"]
  },
  "sources": [
    {
      "source_id": "ohcs_oahi",
      "publisher": "Oregon Housing and Community Services",
      "access": "free-public | free-registration | paid | manual",
      "verified_live": false,
      "vintage": "2026-10-02",
      "vintage_source": "filename | header | mtime | user_stated",
      "file": "Oregon_Affordable_Housing_Inventory_20261002.csv",
      "sha256": "string",
      "rows_ingested": 1819,
      "rows_in_geography": 810,
      "events_emitted": 0,
      "caveats": ["expiration dates are regulatory, not loan maturities"]
    }
  ],
  "assumptions": {
    "market_params_as_of": "YYYY-MM-DD",
    "benchmarks_source": "multifamily-benchmarks Quick Reference 2026-05",
    "cap_rate_used": {"value": 0.064, "source": "Kidder Mathews Q2 2026", "as_of": "2026-06-30"},
    "refi_rate": {"value": 0.059, "components": {"ust10": 0.0415, "spread_bp": 175}, "verify": true},
    "dscr_floor": 1.25,
    "debt_yield_floor": 0.08,
    "ltv_max": 0.70,
    "opex_per_unit": 9400,
    "vacancy": 0.071,
    "lender_term_table": "sources/oregon-portland/lender-term-assumptions.md",
    "av_is_market": false
  },
  "calendar_summary": {
    "header": "RECORDED n / REPORTED n / DERIVED n / ESTIMATED n / PROXY n / Suppressed n / Rejected n",
    "by_basis": {"RECORDED": 0, "REPORTED": 0, "DERIVED": 0, "ESTIMATED": 0, "PROXY": 0},
    "by_family": {"DEBT": 0, "REGULATORY": 0, "HARD_DISTRESS": 0, "TAX_LIEN": 0, "PHYSICAL": 0, "OWNERSHIP": 0, "OPERATING": 0},
    "by_urgency": {"CRITICAL": 0, "URGENT": 0, "APPROACHING": 0, "MONITOR": 0, "SCHEDULED": 0},
    "suppressed": 0,
    "rejected": 0
  },
  "summary": {
    "properties_in_geography": 810,
    "properties_with_event_in_horizon": 0,
    "tiers": {"A": 0, "B": 0, "C": 0, "WATCH": 0, "EXCLUDED": 0},
    "routes": {"acquisition": 0, "partnership_preservation": 0, "lender_counterparty": 0, "assumption_play": 0, "watch": 0, "excluded": 0},
    "proxy_only_count": 0,
    "contact_grades": {"A": 0, "B": 0, "C": 0}
  },
  "leads": [
    {
      // every column of pipeline-contract.md Section 5, same names, same order
      "property_id": "OR-41051-R123456",
      "property_name": "string",
      "address": "string", "city": "string", "zip": "97202",
      "county_fips": "41051", "county_name": "Multnomah", "jurisdiction": "Portland",
      "geo_modes": "county|metro_core|cbsa", "geo_grade": "county_field",
      "lat": 45.5, "lon": -122.6,
      "asset_class": "affordable_regulated", "status": "Active",
      "units": 48, "year_built": 1972, "rehab_year": null, "property_type": "Family",
      "programs": "LIHTC_9;HOME;HAP", "hud_contract": "Housing Assistance Payment",
      "ami_30_60_units": 48, "ami_80_units": 0, "market_rate_units": 0, "rental_assistance_units": 20,
      "owner_name": "string", "owner_type": "lihtc_partnership_forprofit_gp", "owner_archetype": "lihtc_gp_year15",
      "developer_name": "string", "manager_name": "string",
      "decision_maker_name": "not in public record", "decision_maker_role": "GP managing member", "dm_source": "sos_or:pending",
      "contact_grade": "C",
      "first_debt_event_type": "LOAN_MATURITY", "first_debt_event_date": "2029-01-26", "first_debt_months_out": 27.6,
      "first_debt_basis": "PROXY", "first_debt_source": "ohcs_oahi:Financial_Closing_Date+15y",
      "first_reg_event_type": "HAP_EXPIRATION", "first_reg_event_date": "2027-09-30", "first_reg_months_out": 11.9,
      "first_reg_basis": "REPORTED", "first_reg_source": "ohcs_oahi:HUD_MF_Expiration_Date",
      "events_in_horizon": [
        {"event_type": "HAP_EXPIRATION", "event_date": "2027-09-30", "months_out": 11.9, "basis": "REPORTED", "confidence": 0.7,
         "source": "ohcs_oahi:HUD_MF_Expiration_Date", "verify_flag": null, "alt_dates": [], "window_start": null, "window_end": null, "direction": "PRESSURE"}
      ],
      "est_value": 7200000, "value_source": "restricted_income_proxy",
      "est_noi": 486000, "noi_source": "benchmark_estimate",
      "est_loan_balance": null, "balance_basis": "PROXY",
      "est_ltv": null, "est_dscr_refi": null, "refi_gap_pct": null, "equity_cushion_pct": null,
      "assumable_debt": false,
      "signals": "hap_le_24;forprofit_gp;programs_2_same_24mo",
      "verify_flags": "",
      "score_raw": 52, "motivation_score": 46, "tier": "C", "route": "acquisition",
      "outreach_angle": "HAP renewal vs preservation sale", "outreach_template": "lihtc_gp_year15",
      "compliance_gates": "preservation_law;lihtc_tenant_protections;dnc_scrub",
      "verify_before_outreach": "GP name via SOS; HAP renewal term via HUD Sec 8 DB; first-mortgage maturity via recorder",
      "next_action": "Pull HUD MF Assistance & Sec 8 contract row; order trust-deed image",
      "source_vintages": "ohcs_oahi=2026-10-02",
      "as_of_date": "YYYY-MM-DD",
      "factors": {                                   // from score_leads.py factors_json
        "regulatory_event_timing": {"points": 15, "multiplier": 0.9, "evidence": ["evt:abc123"], "reading": "string", "lever": "string"}
      }
    }
  ],
  "rejects": [
    {"property_key": "string", "column": "Financial_Closing_Date", "raw_value": "string", "reason": "string", "flag": "Rejected — Out of Range", "alt_dates": []}
  ],
  "partnership_track": [ /* lead objects with route partnership_preservation, same shape as leads[] */ ],
  "counterparty_track": [ /* lead objects with route lender_counterparty */ ],
  "on_market_excluded": [ {"property_id": "string", "listing_source": "deal-finder", "listed_date": "YYYY-MM-DD"} ],
  "handoffs": {
    "comp-analyzer": "handoff/comp-analyzer.json",
    "underwriting-market-rate-multifamily": "handoff/underwriting-market-rate-multifamily.json",
    "front-door-lihtc-underwriting": "handoff/front-door-lihtc-underwriting.json",
    "residential-deal-underwriter": "handoff/residential-deal-underwriter.json",
    "critical-dates-tracker": "handoff/critical-dates-tracker.json",
    "forward-pipeline-and-news-intelligence": "handoff/forward-pipeline-and-news-intelligence.json",
    "legal-title-risk-assessment": "handoff/legal-title-risk-assessment.json",
    "deal-finder": "handoff/deal-finder.json"
  },
  "data_gaps": [
    {"gap": "No HUD FHASL Active file in inbox", "effect": "no RECORDED loan maturities; Tier A unavailable", "fix": "download HUD Insured Multifamily Mortgages (Active) and drop in inbox"}
  ]
}
```

## 2. Excel workbook specification

Build with openpyxl; read `/mnt/skills/public/xlsx/SKILL.md` first when available and run `python /mnt/skills/public/xlsx/scripts/recalc.py <xlsx>` afterwards if present (do not fail when absent). File name pattern: `{Market}_{Class}_{Mode}_{horizon}yr_Targets.xlsx`.

| tab | contents | formatting |
|---|---|---|
| `Summary` | run block (as_of, market, mode, class, horizons, query_type, buyer_profile), basis breakdown header (helper deadlines on their own line), query hits when query_type != all, counts by tier/route/urgency, degraded flag and reason, sources still `verified_live=false` (URL status; a file opened on disk does not count), reject count (rejected + verify-flag rows = Rejects_Verify row count) | labels col A, values col B; inputs blue font `0000FF` |
| `Targets` | one row per lead, every column of pipeline-contract Section 5 in order, plus `Analyst status` and `Analyst notes` | freeze A2; autofilter; tier fill on `tier` cell: A `C6EFCE`, B `FFEB9C`, C `E7E6E6`, WATCH none; basis fill on `first_debt_basis` and `first_reg_basis`: RECORDED `C6EFCE`, REPORTED `DDEBF7`, DERIVED `E2EFDA`, ESTIMATED `FFF2CC`, PROXY `E7E6E6` italic; dropdown on `Analyst status` {New, Contacted, Verifying, Nurture, Dead}; widths: property_name 32, address 30, owner_name 30, decision_maker_name 24, events_in_horizon 60, others 14 |
| `Events` | events.csv rows sorted by property then date | basis fills as above; `direction` SUPPRESSION rows grey italic |
| `Capital_Stack` | per lead: est_value, value_source, est_noi, noi_source, est_loan_balance, balance_basis, lender_type, note_rate, rate_type, io_end, prepay_open, est_ltv, est_dscr_refi, refi_gap_pct, equity_cushion_pct, rate_spread_bp, assumable_debt, soft_debt_layers (text) | formulas live where inputs exist (refi test recomputed from Assumptions tab cells); basis fills on balance_basis |
| `Regulatory` | class 3 only (empty note otherwise): programs, compliance_start, year15_date, extended_use_end, hap_expiration, hap_renewal_pattern, usda dates, soft program ends, preservation notice window start/end, notice status, rofr_recorded, qc_status, latest_end | basis fills |
| `Owners_DecisionMakers` | owner_name, owner_type, owner_archetype, decision_maker_name, role, dm_source, contact_grade, principal office, registered agent (labeled as not owner), sponsor family id, SOS status, worklist reason | grade A green, B amber, C none |
| `Signals` | long table: property_id, factor, band id, points, multiplier, evidence event ids, reading, lever | |
| `Sources_Vintages` | sources[] from JSON: source_id, file, sha256, vintage, vintage_source (filename / mtime), file_verified, url_verified_live, access, url, note | url_verified_live false in amber; file_verified says the header matched the schema, nothing more |
| `Assumptions` | market-params.json flattened: name, value, as_of, source, verify flag; benchmarks date; lender term table | inputs blue font |
| `Rejects_Verify` | rejects.csv rows plus lead-level verify_flags | |
| `Diff_vs_Prior` | diff.csv when `--prior` given, else a single note row | new green, escalated amber, retired grey |

## 3. Markdown brief template

Fixed section order. Quote the calendar header before any count.

```markdown
# Off-Market Targets — [Market label], [asset class], [query type], [horizon] years
As of [as_of_date] · geography_mode [mode] ([county FIPS list]) · buyer_profile [profile]

## Run Summary
- Basis breakdown: RECORDED n / REPORTED n / DERIVED n / ESTIMATED n / PROXY n / Suppressed n / Rejected n | helper deadlines n
- query_type hits (when not `all`): n leads carry a dated <query> event; n shown as secondary
- Properties in geography: n · with a dated event inside horizon: n · Tier A n / B n / C n / WATCH n
- Routes: acquisition n · partnership_preservation n · lender_counterparty n · assumption_play n
- Degraded run: [yes/no — reason; which files would lift the cap]
- Sources used (vintage, verified_live): ...

## Event Horizon
| months out | DEBT | REGULATORY | HARD_DISTRESS | TAX_LIEN | PHYSICAL | OWNERSHIP | OPERATING |
| 0-12 | ... |
| 12-24 | ... |
| 24-36 | ... |
| 36-60 | ... |

## Top Targets
[lead cards, Section 4 format, ranked by motivation_score within route acquisition / assumption_play]

## Partnership Track
[cards for route partnership_preservation: nonprofit GP, housing authority, ROFR-encumbered]

## Lender-Counterparty Track
[cards for route lender_counterparty: receiver, special servicer, trustee's deed, bankruptcy]

## Pipeline Actions
| # | property | action | owner of action | by when | gate |

## Data Gaps and Verification Queue
- [gap -> effect -> fix]
- Documents to request per Tier A lead (feeds critical-dates-tracker)
- SOS worklist: n entities

## Assumptions and Limits
- Market params as of ...; benchmarks source ...; refi rate ... (UST10 flagged verify)
- Every date carries a basis; proxy-only leads are capped at Tier C
- Sources not verified live: ...
```

## 4. Lead card format

```markdown
### [#n] [property_name] — [address], [jurisdiction]  Tier [A] Score [78] Route [acquisition]
- Class [affordable_regulated] · Units [48] · Built [1972] · Rehab [—] · Owner type [lihtc_partnership_forprofit_gp]
- First debt event: [LOAN_MATURITY 2027-06-01 [RECORDED] HUD FHASL] — [8] months
- First regulatory event: [HAP_EXPIRATION 2027-09-30 [REPORTED 0.70] HUD Sec 8 DB] — [12] months
- Capital stack: [HUD 223(f) $4.1M UPB @ 3.45% (RECORDED); PHB soft loan (SOFT_LOAN_MATURITY not in public record)]
- Refi screen: [value $7.2M restricted_income_proxy · LTV 0.57 · DSCR_refi 1.31 · gap -4% · cushion 43%]
- Signals: [hap_le_24; forprofit_gp; programs_2_same_24mo]
- Decision maker: [Jane Doe, GP managing member, grade A — SOS LP record + trust-deed signatory]
- Outreach: [lihtc_gp_year15 — HAP renewal vs preservation sale] · Gates: [preservation_law; lihtc_tenant_protections; dnc_scrub]
- Verify before outreach: [HAP renewal term; PuSH notice status; LURA extended-use date]
- Handoffs ready: [front-door-lihtc-underwriting; critical-dates-tracker; legal-title-risk-assessment]
```

## 5. Handoff payload field maps

`scripts/make_handoffs.py` writes one JSON per sibling for Tier A leads (`--tier` overrides). Each file: `{"from": "off-market-deal-finder", "as_of": "...", "items": [ ... ]}`.

| sibling | item fields |
|---|---|
| `comp-analyzer` | `subject_address`, `property_type` (`multifamily` / `residential`), `unit_count`, `year_built`, `valuation_mode: "as_is"`, `current_value_proxy`, `value_source` |
| `cap-rate-comp-selector` | `subject_address`, `asset_class`, `units`, `year_built`, `est_noi`, `noi_source`, `cap_rate_proxy` |
| `underwriting-market-rate-multifamily` | `deal_name`, `asset_address`, `total_units`, `year_built`, `estimated_in_place_rent`, `existing_debt: {upb, rate, maturity, basis, lender_type, assumable}`, `needs_sponsor_data: ["rent roll", "T-12", "loan agreement", ...]` |
| `front-door-lihtc-underwriting` | `lihtc_context: {credit_type, compliance_start, year15_date, extended_use_end, ami_units: {30: n, 40: n, 50: n, 60: n, 80: n, market: n}, hud_contract, hap_expiration, soft_debt_sources: [], sponsor_type, qc_eligible, preservation_notice_status}`, `existing_debt` as above, `composition_mode: true` |
| `residential-deal-underwriter` | `address`, `units`, `value_est`, `value_source`, `liens: [{type, holder, amount_est, basis}]`, `occupancy_status`, `distress_stage` |
| `critical-dates-tracker` | `seed_dates: [{event_type, date, basis, source}]`, `documents_to_request: [...]` — one entry per non-RECORDED event: loan note/agreement, trust-deed image, LURA/REUA, HAP contract, USDA loan docs, PHB loan agreement |
| `forward-pipeline-and-news-intelligence` | `asset_location`, `asset_class`, `deal_strategy` (e.g. "Year-15 LIHTC resyndication/preservation", "maturity-driven recap of 1970s Class C", "pre-foreclosure fourplex as-is purchase") |
| `legal-title-risk-assessment` | `parcel_id`, `address`, `recorded_instruments: [{instrument_number, type, date, grantor, grantee}]`, `liens_to_confirm: []` |
| `deal-finder` | `leads: [{address, apn, units, property_type}]` — run before outreach; any active listing sets `on_market=true` and moves the lead to `on_market_excluded[]` |

Also written by `make_handoffs.py`: `sos_worklist.csv` (`owner_name_raw, normalized_name, state, registry_search_url, reason, property_ids`; one row per distinct owner entity still `not in public record`, `decision-maker-enrichment.md` Section 6) and `documents_to_request.csv` (`property_id, property_name, tier, event_type, event_date, basis, document, where_to_get, est_cost`; one row per non-RECORDED governing event; `est_cost` quotes the recorder image fee from `market-params.json`, which is snippet-derived and marked verify). The brief's Data Gaps section states both counts.

## 6. Pipeline Mode checkpoint

`data/status/{market_id}/sourcing/off-market-targets.json`:

```jsonc
{
  "agent": "off-market-deal-finder",
  "phase": "sourcing",
  "market_id": "us-or-multnomah",
  "status": "COMPLETE | PARTIAL | FAILED",
  "as_of": "YYYY-MM-DD",
  "payload": {
    "result_json": "path",
    "workbook": "path",
    "brief": "path",
    "tiers": {"A": 0, "B": 0, "C": 0},
    "degraded": true,
    "handoffs": {}
  }
}
```

Append a line to `data/logs/{market_id}/sourcing.log` with timestamp, status and the calendar header.
