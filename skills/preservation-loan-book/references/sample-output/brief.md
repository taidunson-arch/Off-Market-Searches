# Preservation and Loan-Book Review: hfa — us-or-portland-metro — as of 2026-10-04

## Run Summary
- Agency: Oregon Housing and Community Services (hfa) · geography_mode metro_core (41051, 41067, 41005) · horizon 10 years · universe all
- Files and vintages: agency_servicing_extract 2026-10-05 (mtime); ohcs_oahi 2026-10-02 (filename); absent: hud_mf_assist_sec8, ohcs_push_forecast, hud_reac
- Basis breakdown: RECORDED 20 / REPORTED 217 / DERIVED 83 / ESTIMATED 0 / PROXY 0 / Suppressed 0 / Rejected 0 | helper deadlines 595 (notice arithmetic, LATEST duplicates; not counted above) | agency act-by 384 (next 90 days 20)
- Book: coverage partial; joins crosswalk 0 / address 8 / fuzzy 1 / unmatched 4; book rows monitored 1 vs on watch 11; book_match unmatched_expected 0
- Degraded run: yes — forecast / CA notice statuses absent: notice_status unknown for inventory rows (silence is not inferred).
- pii_scope organization; records_classification: agency working file; disclosable subject to ORS 192.345/192.355 review; tenant data excluded by design
- Urgency bands are months (OVERDUE / CRITICAL 0-12 / URGENT 12-24 / APPROACHING 24-36 / MONITOR 36-60 / SCHEDULED 60-120 / BEYOND), not critical-dates-tracker's days
- Notice log: 406 of 406 PuSH-covered rows have no notice_log_status (unknown) — reported, not scored
- Owner type unknown: 224 of 768 rows (SOS worklist)

## Board Totals
Book verdict: CRITICAL — CRITICAL >= 50% of book UPB on watch/default or >= 25% of units with a cliff <= 24 mo; STRESSED >= 25% / 12%; WATCH >= 10% / 5%; else STABLE; public UPB on watch $12,830,000 of $15,480,000
87 properties / 5690 restricted units / 771 HAP units / 567 PRAC units / 14 PSH units / $11,330,000 public UPB with an owner cliff inside 36 months or already past without termination evidence (OVERDUE rows; verify)

| owner_cliff_band | properties | units_at_risk | hap_units_at_risk | prac_units_at_risk | other_ra_units | psh_units_at_risk | public_upb_at_risk | public_grant_at_risk | being_preserved_units |
|---|---|---|---|---|---|---|---|---|---|
| OVERDUE | 15 | 778.0 | 0 | 19.0 | 118.0 | 0 | 0 | 0 | 0 |
| CRITICAL | 22 | 1136.0 | 95.0 | 0 | 71.0 | 0 | 850000.0 | 0 | 0 |
| URGENT | 20 | 1579.0 | 291.0 | 375.0 | 0 | 0 | 5600000.0 | 0 | 0 |
| APPROACHING | 30 | 2197.0 | 385.0 | 173.0 | 14.0 | 14.0 | 4880000.0 | 480000.0 | 0 |
| MONITOR | 39 | 2307.0 | 534.0 | 15.0 | 48.0 | 17.0 | 0 | 0 | 0 |
| SCHEDULED | 75 | 5533.0 | 1867.0 | 19.0 | 465.0 | 98.0 | 1500000.0 | 0 | 0 |
| beyond horizon | 275 | 19767.0 | 1312.0 | 148.0 | 1817.0 | 808.0 | 0 | 1100000.0 | 0 |
| stale contract date — verify | 14 | 269.0 | 30.0 | 229.0 | 0 | 0 | 0 | 0 | 0 |
| no dated cliff | 278 | 8655.0 | 0 | 0 | 158.0 | 22.0 | 0 | 0 | 0 |

By county: Multnomah 63 properties / 4404 units inside 36 mo / Washington 13 properties / 850 units inside 36 mo / Clackamas 11 properties / 436 units inside 36 mo
Top 5 sponsors by exposure: HOME FORWARD — 36 properties, 2057 units, $2,400,000 UPB, 4 cliffs in 36 mo; REACH GOT — 3 properties, 146 units, $0 UPB, 3 cliffs in 36 mo; BETHANY MEADOWS PHASE I AND II — 2 properties, 340 units, $0 UPB, 2 cliffs in 36 mo; TIMBER GROVE APARTMENTS — 2 properties, 72 units, $0 UPB, 2 cliffs in 36 mo; CEDAR SINAI PARK CLAY TOWER APARTMENTS — 1 properties, 235 units, $3,200,000 UPB, 1 cliffs in 36 mo

## Agency Act-By Calendar (overdue and next 90 days)

| due date | property | agency_action_type | agency owner | cite | derived from | status |
|---|---|---|---|---|---|---|
| 2025-11-05 | Cathedral Gardens | INSPECTION_DUE | compliance_officer | 24 CFR 92.504(d); 26 CFR 1.42-5 (verify) | last_inspection_date 2024-11-05 + 12 months (24 CFR 92.504(d), verify) | OVERDUE |
| 2026-01-01 | Berry Ridge Apartments | PUSH_WINDOW_PREP | push_program_manager | internal prep date (anchor - 36 months); no statutory basis found for a 36-month owner-notice start (verify) | withdrawal_anchor_date 2029-01-01 - 36 months (internal prep) | OVERDUE |
| 2026-01-01 | Berry Ridge Apartments | TENANT_NOTICE_WINDOW | compliance_officer | SB 973 (2025); ORS 456.259 (verify) | withdrawal_anchor_date 2029-01-01 - 36..30 months (SB 973 / ORS 456.259, verify) | OVERDUE |
| 2026-01-01 | Bethany Meadows II | PUSH_WINDOW_PREP | push_program_manager | internal prep date (anchor - 36 months); no statutory basis found for a 36-month owner-notice start (verify) | withdrawal_anchor_date 2029-01-01 - 36 months (internal prep) | OVERDUE |
| 2026-01-01 | Bethany Meadows II | TENANT_NOTICE_WINDOW | compliance_officer | SB 973 (2025); ORS 456.259 (verify) | withdrawal_anchor_date 2029-01-01 - 36..30 months (SB 973 / ORS 456.259, verify) | OVERDUE |
| 2026-01-01 | FIFTH AVENUE PLACE APTS | PUSH_WINDOW_PREP | push_program_manager | internal prep date (anchor - 36 months); no statutory basis found for a 36-month owner-notice start (verify) | withdrawal_anchor_date 2029-01-01 - 36 months (internal prep) | OVERDUE |
| 2026-01-01 | FIFTH AVENUE PLACE APTS | TENANT_NOTICE_WINDOW | compliance_officer | SB 973 (2025); ORS 456.259 (verify) | withdrawal_anchor_date 2029-01-01 - 36..30 months (SB 973 / ORS 456.259, verify) | OVERDUE |
| 2026-01-01 | Linc245 (fka Village at Lovejoy Fountain) | PUSH_WINDOW_PREP | push_program_manager | internal prep date (anchor - 36 months); no statutory basis found for a 36-month owner-notice start (verify) | withdrawal_anchor_date 2029-01-01 - 36 months (internal prep) | OVERDUE |
| 2026-01-01 | Linc245 (fka Village at Lovejoy Fountain) | TENANT_NOTICE_WINDOW | compliance_officer | SB 973 (2025); ORS 456.259 (verify) | withdrawal_anchor_date 2029-01-01 - 36..30 months (SB 973 / ORS 456.259, verify) | OVERDUE |
| 2026-01-01 | STADIUM STATION | PUSH_SECOND_NOTICE_DUE | push_program_manager | ORS 456.260 / OAR 813-115-0030 (owner notice at least 24 months before withdrawal; the (1)/(2) split is unread) (verify) | withdrawal_anchor_date 2028-01-01 - 24 months (owner notice at least 24 months b | OVERDUE |
| 2026-01-01 | St Anthony Village | PUSH_WINDOW_PREP | push_program_manager | internal prep date (anchor - 36 months); no statutory basis found for a 36-month owner-notice start (verify) | withdrawal_anchor_date 2029-01-01 - 36 months (internal prep) | OVERDUE |
| 2026-01-01 | St Anthony Village | TENANT_NOTICE_WINDOW | compliance_officer | SB 973 (2025); ORS 456.259 (verify) | withdrawal_anchor_date 2029-01-01 - 36..30 months (SB 973 / ORS 456.259, verify) | OVERDUE |
| 2026-01-01 | Terrace View Apartments | PUSH_SECOND_NOTICE_DUE | push_program_manager | ORS 456.260 / OAR 813-115-0030 (owner notice at least 24 months before withdrawal; the (1)/(2) split is unread) (verify) | withdrawal_anchor_date 2028-01-01 - 24 months (owner notice at least 24 months b | OVERDUE |
| 2026-01-01 | YARDS AT UNION STATION B | PUSH_WINDOW_PREP | push_program_manager | internal prep date (anchor - 36 months); no statutory basis found for a 36-month owner-notice start (verify) | withdrawal_anchor_date 2029-01-01 - 36 months (internal prep) | OVERDUE |
| 2026-01-01 | YARDS AT UNION STATION B | TENANT_NOTICE_WINDOW | compliance_officer | SB 973 (2025); ORS 456.259 (verify) | withdrawal_anchor_date 2029-01-01 - 36..30 months (SB 973 / ORS 456.259, verify) | OVERDUE |
| 2026-01-01 | Yards at Union Station A | PUSH_SECOND_NOTICE_DUE | push_program_manager | ORS 456.260 / OAR 813-115-0030 (owner notice at least 24 months before withdrawal; the (1)/(2) split is unread) (verify) | withdrawal_anchor_date 2028-01-01 - 24 months (owner notice at least 24 months b | OVERDUE |
| 2026-01-24 | OUR APARTMENT | HAP_OPTOUT_NOTICE_DEADLINE | pbca_liaison | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | HAP_EXPIRATION 2027-01-24 - 12 months (42 U.S.C. 1437f(c)(8); 24 CFR 402.8, veri | OVERDUE |
| 2026-02-15 | MLK-Wygant Housing | PUSH_FIRST_NOTICE_DUE | push_program_manager | ORS 456.260 / OAR 813-115-0030 (owner notice no sooner than 30 months before withdrawal); ORS 456.262 designee-appointment trigger at 30 months ('whichever is earlier') (verify) | withdrawal_anchor_date 2028-08-15 - 30 months (owner notice no sooner than this  | OVERDUE |
| 2026-03-31 | Powell Plaza I | HAP_OPTOUT_NOTICE_DEADLINE | pbca_liaison | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | HAP_EXPIRATION 2027-03-31 - 12 months (42 U.S.C. 1437f(c)(8); 24 CFR 402.8, veri | OVERDUE |
| 2026-03-31 | Powell Plaza II | HAP_OPTOUT_NOTICE_DEADLINE | pbca_liaison | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | HAP_EXPIRATION 2027-03-31 - 12 months (42 U.S.C. 1437f(c)(8); 24 CFR 402.8, veri | OVERDUE |
| 2026-06-01 | Village Garden Apartments | PUSH_WINDOW_PREP | push_program_manager | internal prep date (anchor - 36 months); no statutory basis found for a 36-month owner-notice start (verify) | withdrawal_anchor_date 2029-06-01 - 36 months (internal prep) | OVERDUE |
| 2026-06-01 | Village Garden Apartments | TENANT_NOTICE_WINDOW | compliance_officer | SB 973 (2025); ORS 456.259 (verify) | withdrawal_anchor_date 2029-06-01 - 36..30 months (SB 973 / ORS 456.259, verify) | OVERDUE |
| 2026-06-30 | Sumner Street Flats | PUSH_WINDOW_PREP | push_program_manager | internal prep date (anchor - 36 months); no statutory basis found for a 36-month owner-notice start (verify) | withdrawal_anchor_date 2029-06-30 - 36 months (internal prep) | OVERDUE |
| 2026-06-30 | Sumner Street Flats | TENANT_NOTICE_WINDOW | compliance_officer | SB 973 (2025); ORS 456.259 (verify) | withdrawal_anchor_date 2029-06-30 - 36..30 months (SB 973 / ORS 456.259, verify) | OVERDUE |
| 2026-07-01 | Berry Ridge Apartments | PUSH_FIRST_NOTICE_DUE | push_program_manager | ORS 456.260 / OAR 813-115-0030 (owner notice no sooner than 30 months before withdrawal); ORS 456.262 designee-appointment trigger at 30 months ('whichever is earlier') (verify) | withdrawal_anchor_date 2029-01-01 - 30 months (owner notice no sooner than this  | OVERDUE |
| 2026-07-01 | Bethany Meadows II | PUSH_FIRST_NOTICE_DUE | push_program_manager | ORS 456.260 / OAR 813-115-0030 (owner notice no sooner than 30 months before withdrawal); ORS 456.262 designee-appointment trigger at 30 months ('whichever is earlier') (verify) | withdrawal_anchor_date 2029-01-01 - 30 months (owner notice no sooner than this  | OVERDUE |
| 2026-07-01 | FIFTH AVENUE PLACE APTS | PUSH_FIRST_NOTICE_DUE | push_program_manager | ORS 456.260 / OAR 813-115-0030 (owner notice no sooner than 30 months before withdrawal); ORS 456.262 designee-appointment trigger at 30 months ('whichever is earlier') (verify) | withdrawal_anchor_date 2029-01-01 - 30 months (owner notice no sooner than this  | OVERDUE |
| 2026-07-01 | Linc245 (fka Village at Lovejoy Fountain) | PUSH_FIRST_NOTICE_DUE | push_program_manager | ORS 456.260 / OAR 813-115-0030 (owner notice no sooner than 30 months before withdrawal); ORS 456.262 designee-appointment trigger at 30 months ('whichever is earlier') (verify) | withdrawal_anchor_date 2029-01-01 - 30 months (owner notice no sooner than this  | OVERDUE |
| 2026-07-01 | St Anthony Village | PUSH_FIRST_NOTICE_DUE | push_program_manager | ORS 456.260 / OAR 813-115-0030 (owner notice no sooner than 30 months before withdrawal); ORS 456.262 designee-appointment trigger at 30 months ('whichever is earlier') (verify) | withdrawal_anchor_date 2029-01-01 - 30 months (owner notice no sooner than this  | OVERDUE |
| 2026-07-01 | YARDS AT UNION STATION B | PUSH_FIRST_NOTICE_DUE | push_program_manager | ORS 456.260 / OAR 813-115-0030 (owner notice no sooner than 30 months before withdrawal); ORS 456.262 designee-appointment trigger at 30 months ('whichever is earlier') (verify) | withdrawal_anchor_date 2029-01-01 - 30 months (owner notice no sooner than this  | OVERDUE |
| 2026-08-15 | MLK-Wygant Housing | PUSH_SECOND_NOTICE_DUE | push_program_manager | ORS 456.260 / OAR 813-115-0030 (owner notice at least 24 months before withdrawal; the (1)/(2) split is unread) (verify) | withdrawal_anchor_date 2028-08-15 - 24 months (owner notice at least 24 months b | OVERDUE |
| 2026-08-31 | ALBERTA STREET APTS | HAP_OPTOUT_NOTICE_DEADLINE | pbca_liaison | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | HAP_EXPIRATION 2027-08-31 - 12 months (42 U.S.C. 1437f(c)(8); 24 CFR 402.8, veri | OVERDUE |
| 2026-09-26 | OUR APARTMENT | HAP_OPTOUT_PACKAGE_DUE | pbca_liaison | Section 8 Renewal Policy Guide ch. 11 (verify) | HAP_EXPIRATION 2027-01-24 - 120 days (Section 8 Renewal Policy Guide ch. 11, ver | OVERDUE |
| 2026-09-30 | Mt Hood Community Apartments | HAP_OPTOUT_NOTICE_DEADLINE | pbca_liaison | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | HAP_EXPIRATION 2027-09-30 - 12 months (42 U.S.C. 1437f(c)(8); 24 CFR 402.8, veri | OVERDUE |
| 2026-12-01 | Powell Plaza I | HAP_OPTOUT_PACKAGE_DUE | pbca_liaison | Section 8 Renewal Policy Guide ch. 11 (verify) | HAP_EXPIRATION 2027-03-31 - 120 days (Section 8 Renewal Policy Guide ch. 11, ver | CRITICAL |
| 2026-12-01 | Powell Plaza II | HAP_OPTOUT_PACKAGE_DUE | pbca_liaison | Section 8 Renewal Policy Guide ch. 11 (verify) | HAP_EXPIRATION 2027-03-31 - 120 days (Section 8 Renewal Policy Guide ch. 11, ver | CRITICAL |
| 2026-12-01 | Village Garden Apartments | PUSH_FIRST_NOTICE_DUE | push_program_manager | ORS 456.260 / OAR 813-115-0030 (owner notice no sooner than 30 months before withdrawal); ORS 456.262 designee-appointment trigger at 30 months ('whichever is earlier') (verify) | withdrawal_anchor_date 2029-06-01 - 30 months (owner notice no sooner than this  | CRITICAL |
| 2026-12-10 | Rose Schnitzer Tower | HAP_OPTOUT_NOTICE_DEADLINE | pbca_liaison | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | HAP_EXPIRATION 2027-12-10 - 12 months (42 U.S.C. 1437f(c)(8); 24 CFR 402.8, veri | CRITICAL |
| 2026-12-15 | Lafayette Court Apartments | PUSH_WINDOW_PREP | push_program_manager | internal prep date (anchor - 36 months); no statutory basis found for a 36-month owner-notice start (verify) | withdrawal_anchor_date 2029-12-15 - 36 months (internal prep) | CRITICAL |
| 2026-12-15 | Lafayette Court Apartments | TENANT_NOTICE_WINDOW | compliance_officer | SB 973 (2025); ORS 456.259 (verify) | withdrawal_anchor_date 2029-12-15 - 36..30 months (SB 973 / ORS 456.259, verify) | CRITICAL |
| 2026-12-30 | Sumner Street Flats | PUSH_FIRST_NOTICE_DUE | push_program_manager | ORS 456.260 / OAR 813-115-0030 (owner notice no sooner than 30 months before withdrawal); ORS 456.262 designee-appointment trigger at 30 months ('whichever is earlier') (verify) | withdrawal_anchor_date 2029-06-30 - 30 months (owner notice no sooner than this  | CRITICAL |
| 2026-12-31 | ALOHA PROJECT | HAP_OPTOUT_NOTICE_DEADLINE | pbca_liaison | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | HAP_EXPIRATION 2027-12-31 - 12 months (42 U.S.C. 1437f(c)(8); 24 CFR 402.8, veri | CRITICAL |
| 2027-01-01 | Berry Ridge Apartments | PUSH_SECOND_NOTICE_DUE | push_program_manager | ORS 456.260 / OAR 813-115-0030 (owner notice at least 24 months before withdrawal; the (1)/(2) split is unread) (verify) | withdrawal_anchor_date 2029-01-01 - 24 months (owner notice at least 24 months b | CRITICAL |
| 2027-01-01 | Bethany Meadows II | PUSH_SECOND_NOTICE_DUE | push_program_manager | ORS 456.260 / OAR 813-115-0030 (owner notice at least 24 months before withdrawal; the (1)/(2) split is unread) (verify) | withdrawal_anchor_date 2029-01-01 - 24 months (owner notice at least 24 months b | CRITICAL |
| 2027-01-01 | Briarcreek Apartments | PUSH_WINDOW_PREP | push_program_manager | internal prep date (anchor - 36 months); no statutory basis found for a 36-month owner-notice start (verify) | withdrawal_anchor_date 2030-01-01 - 36 months (internal prep) | CRITICAL |
| 2027-01-01 | Briarcreek Apartments | TENANT_NOTICE_WINDOW | compliance_officer | SB 973 (2025); ORS 456.259 (verify) | withdrawal_anchor_date 2030-01-01 - 36..30 months (SB 973 / ORS 456.259, verify) | CRITICAL |
| 2027-01-01 | Collins Circle | PUSH_WINDOW_PREP | push_program_manager | internal prep date (anchor - 36 months); no statutory basis found for a 36-month owner-notice start (verify) | withdrawal_anchor_date 2030-01-01 - 36 months (internal prep) | CRITICAL |
| 2027-01-01 | Collins Circle | TENANT_NOTICE_WINDOW | compliance_officer | SB 973 (2025); ORS 456.259 (verify) | withdrawal_anchor_date 2030-01-01 - 36..30 months (SB 973 / ORS 456.259, verify) | CRITICAL |
| 2027-01-01 | FIFTH AVENUE PLACE APTS | PUSH_SECOND_NOTICE_DUE | push_program_manager | ORS 456.260 / OAR 813-115-0030 (owner notice at least 24 months before withdrawal; the (1)/(2) split is unread) (verify) | withdrawal_anchor_date 2029-01-01 - 24 months (owner notice at least 24 months b | CRITICAL |
| 2027-01-01 | Linc245 (fka Village at Lovejoy Fountain) | PUSH_SECOND_NOTICE_DUE | push_program_manager | ORS 456.260 / OAR 813-115-0030 (owner notice at least 24 months before withdrawal; the (1)/(2) split is unread) (verify) | withdrawal_anchor_date 2029-01-01 - 24 months (owner notice at least 24 months b | CRITICAL |
| 2027-01-01 | St Anthony Village | PUSH_SECOND_NOTICE_DUE | push_program_manager | ORS 456.260 / OAR 813-115-0030 (owner notice at least 24 months before withdrawal; the (1)/(2) split is unread) (verify) | withdrawal_anchor_date 2029-01-01 - 24 months (owner notice at least 24 months b | CRITICAL |
| 2027-01-01 | Wiedemann Park Apartments | PUSH_WINDOW_PREP | push_program_manager | internal prep date (anchor - 36 months); no statutory basis found for a 36-month owner-notice start (verify) | withdrawal_anchor_date 2030-01-01 - 36 months (internal prep) | CRITICAL |
| 2027-01-01 | Wiedemann Park Apartments | TENANT_NOTICE_WINDOW | compliance_officer | SB 973 (2025); ORS 456.259 (verify) | withdrawal_anchor_date 2030-01-01 - 36..30 months (SB 973 / ORS 456.259, verify) | CRITICAL |
| 2027-01-01 | YARDS AT UNION STATION B | PUSH_SECOND_NOTICE_DUE | push_program_manager | ORS 456.260 / OAR 813-115-0030 (owner notice at least 24 months before withdrawal; the (1)/(2) split is unread) (verify) | withdrawal_anchor_date 2029-01-01 - 24 months (owner notice at least 24 months b | CRITICAL |

## Intervention Queue

### Opt-out responses (optout_response) — 5 in CRITICAL / URGENT / APPROACHING

### [#1] Powell Plaza I — Portland  Route [optout_response] Queue [PLAN] Score [36.6] Units at risk [47] Public UPB $850,000
- Units 47 · restricted 47 (units_basis total_assumed_restricted) · HAP 47 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: HAP_OPTOUT_PACKAGE_DUE 2026-12-01 [DERIVED] — 1.9 months · owner pbca_liaison
- Owner cliff: HAP_EXPIRATION 2027-03-31 [REPORTED] — band CRITICAL
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status unknown · recap_status none
- Our position: loan L-OHCS-0002 · $850,000 hard_pay · matures 2035-01-01 [RECORDED] · affordability_end 2035-01-01 · recapture none · covenant_status current · am_officer J. Rivera
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Heartland Columbia-Powell Plaza I LP · sponsor_cliff_count 1
- Intervention: optout_tenant_notice_check — pbca_liaison — 42 U.S.C. 1437f(c)(8); 24 CFR 402.8; Section 8 Renewal Policy Guide ch. 11 (verify current text before sending) — owner notice: yes · tenant notice: yes — notice address: not on file [unknown] — first action: confirm renewal request / opt-out notice at CA
- Evidence: HAP_EXPIRATION 2027-03-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002; AFFORDABILITY_PERIOD_END 2035-01-01 [RECORDED] agency_servicing; AGENCY_LOAN_MATURITY 2035-01-01 [RECORDED] agency_servicing; LIHTC_EXTENDED_USE_END 2035-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2035-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm HAP_EXPIRATION 2027-03-31 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA; confirm HAP_OPTOUT_PACKAGE_DUE 2026-12-01 [DERIVED] via source document · flags Verify — CA Log
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence · documents to request: 3

### [#2] Powell Plaza II — Portland  Route [optout_response] Queue [PLAN] Score [36.6] Units at risk [20] Public UPB n/a
- Units 20 · restricted 20 (units_basis reported_buckets) · HAP 20 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: HAP_OPTOUT_PACKAGE_DUE 2026-12-01 [DERIVED] — 1.9 months · owner pbca_liaison
- Owner cliff: HAP_EXPIRATION 2027-03-31 [REPORTED] — band CRITICAL
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none · secondary routes nofa_offer
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_nonprofit_gp · Heartland Columbia-Powell Plaza II LP · sponsor_cliff_count 1
- Intervention: optout_tenant_notice_check — pbca_liaison — 42 U.S.C. 1437f(c)(8); 24 CFR 402.8; Section 8 Renewal Policy Guide ch. 11 (verify current text before sending) — owner notice: yes · tenant notice: yes — notice address: not on file [unknown] — first action: confirm renewal request / opt-out notice at CA
- Evidence: HAP_EXPIRATION 2027-03-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002; LIHTC_EXTENDED_USE_END 2035-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2035-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm HAP_EXPIRATION 2027-03-31 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA; confirm HAP_OPTOUT_PACKAGE_DUE 2026-12-01 [DERIVED] via source document · flags Verify — CA Log
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 3

### [#3] Mt Hood Community Apartments — Gresham  Route [optout_response] Queue [PLAN] Score [30.3] Units at risk [15] Public UPB n/a
- Units 15 · restricted 15 (units_basis total_assumed_restricted) · HAP 14 · PRAC 0 · other RA 0 · PSH 0 · flags [disabled]
- First agency act-by: HAP_OPTOUT_PACKAGE_DUE 2027-06-02 [DERIVED] — 7.9 months · owner pbca_liaison
- Owner cliff: HAP_EXPIRATION 2027-09-30 [REPORTED] — band CRITICAL
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none · secondary routes nofa_offer
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: nonprofit · Mt Hood Special Housing Inc · sponsor_cliff_count 1
- Intervention: optout_tenant_notice_check — pbca_liaison — 42 U.S.C. 1437f(c)(8); 24 CFR 402.8; Section 8 Renewal Policy Guide ch. 11 (verify current text before sending) — owner notice: yes · tenant notice: yes — notice address: not on file [unknown] — first action: confirm renewal request / opt-out notice at CA
- Evidence: HAP_EXPIRATION 2027-09-30 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm HAP_EXPIRATION 2027-09-30 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA · flags Verify — CA Log
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 1

### [#4] ALBERTA STREET APTS — Portland  Route [optout_response] Queue [WATCH] Score [22.5] Units at risk [10] Public UPB n/a
- Units 10 · restricted 10 (units_basis total_assumed_restricted) · HAP 10 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: HAP_OPTOUT_PACKAGE_DUE 2027-05-03 [DERIVED] — 6.9 months · owner pbca_liaison
- Owner cliff: HAP_EXPIRATION 2027-08-31 [REPORTED] — band CRITICAL
- Declared intent / notice status: notice_status unknown · tenant_notice_status n/a · hap_renewal_request_status n/a · recap_status none · secondary routes nofa_offer
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: unknown · owner not on file · sponsor_cliff_count 0
- Intervention: optout_tenant_notice_check — pbca_liaison — 42 U.S.C. 1437f(c)(8); 24 CFR 402.8; Section 8 Renewal Policy Guide ch. 11 (verify current text before sending) — owner notice: yes · tenant notice: yes — notice address: not on file [unknown] — first action: confirm renewal request / opt-out notice at CA
- Evidence: HAP_EXPIRATION 2027-08-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2027-08-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm HAP_EXPIRATION 2027-08-31 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA · flags Verify — CA Log
- Handoffs ready: -

### [#5] OUR APARTMENT — Oregon City  Route [optout_response] Queue [WATCH] Score [18.0] Units at risk [4] Public UPB n/a
- Units 4 · restricted 4 (units_basis total_assumed_restricted) · HAP 4 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: HAP_OPTOUT_PACKAGE_DUE 2026-09-26 [DERIVED] — -0.3 months · owner pbca_liaison
- Owner cliff: HAP_EXPIRATION 2027-01-24 [REPORTED] — band CRITICAL
- Declared intent / notice status: notice_status unknown · tenant_notice_status n/a · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: unknown · owner not on file · sponsor_cliff_count 0
- Intervention: optout_tenant_notice_check — pbca_liaison — 42 U.S.C. 1437f(c)(8); 24 CFR 402.8; Section 8 Renewal Policy Guide ch. 11 (verify current text before sending) — owner notice: yes · tenant notice: yes — notice address: not on file [unknown] — first action: confirm renewal request / opt-out notice at CA
- Evidence: HAP_EXPIRATION 2027-01-24 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2027-01-24 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm HAP_EXPIRATION 2027-01-24 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA · flags Verify — CA Log
- Handoffs ready: -

### Qualified-contract administration (qc_admin) — 1 in CRITICAL / URGENT / APPROACHING

### [#6] Cathedral Gardens — Portland  Route [qc_admin] Queue [PLAN] Score [40.5] Units at risk [124] Public UPB $1,500,000
- Units 124 · restricted 124 (units_basis reported_buckets) · HAP 124 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: INSPECTION_DUE 2025-11-05 [DERIVED] — -11.0 months · owner compliance_officer
- Owner cliff: AGENCY_LOAN_MATURITY 2033-12-31 [DERIVED] — band SCHEDULED
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none · secondary routes recap_committee;servicing_watch
- Our position: loan L-OHCS-0004 · $1,500,000 residual_receipts · matures 2033-12-31 [RECORDED] · affordability_end n/a · recapture none · covenant_status current · am_officer M. Okafor
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Cathedral Gardens Partners, Limited Partnership · sponsor_cliff_count 0
- Intervention: qc_marketing_plan — compliance_officer — IRC 42(h)(6)(F); OHCS Draft Qualified Contract Procedure (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Present a bona fide contract within the one-year period; presentment alone removes the exit
- Evidence: QC_ELIGIBILITY 2026-03-15 [RECORDED] agency_servicing; LIHTC_COMPLIANCE_END 2028-12-17 [DERIVED] OHCS OAHI p9yn-ftai 20261002; AGENCY_LOAN_MATURITY 2033-12-31 [RECORDED] agency_servicing; HAP_EXPIRATION 2033-12-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm LIHTC_COMPLIANCE_END 2028-12-17 [DERIVED] via 8609 / Compliance_Start confirmation; confirm HAP_EXPIRATION 2033-12-31 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA; confirm QC_RESPONSE_DUE 2027-03-15 [DERIVED] via source document
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting, lihtc-lpa-reviewer, sizing-lihtc-permanent-debt · documents to request: 2

### Recap committee (recap_committee) — 3 in CRITICAL / URGENT / APPROACHING

### [#7] Yards at Union Station A — Portland  Route [recap_committee] Queue [ESCALATE] Score [74.0] Units at risk [158] Public UPB $2,400,000
- Units 158 · restricted 158 (units_basis reported_buckets) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_SECOND_NOTICE_DUE 2026-01-01 [DERIVED] — -9.1 months · owner push_program_manager
- Owner cliff: AFFORDABILITY_PERIOD_END 2028-01-01 [RECORDED] — band URGENT
- Declared intent / notice status: notice_status unknown · tenant_notice_status n/a_pre_operative · hap_renewal_request_status n/a · recap_status none · secondary routes notice_compliance;servicing_watch;ta_sponsor
- Our position: loan L-OHCS-0003 · $2,400,000 deferred · matures 2028-01-01 [RECORDED] · affordability_end 2028-01-01 · recapture none · covenant_status current · am_officer M. Okafor
- Physical: no physical / REAC signal in this run
- Sponsor capacity: housing_authority · Home Forward · sponsor_cliff_count 4
- Intervention: loan_extension_recast_memo — am_officer — loan documents; NHA 236(e)(2); Notice H 2013-25; 24 CFR 92.252 (verify current text before sending) — owner notice: yes · tenant notice: no — notice address: not on file [unknown] — first action: Draft the committee memo: UPB, payment-type change, extension or resubordination, senior cliff, restricted-NOI capacity
- Evidence: AFFORDABILITY_PERIOD_END 2028-01-01 [RECORDED] agency_servicing; AGENCY_LOAN_MATURITY 2028-01-01 [RECORDED] agency_servicing; LIHTC_EXTENDED_USE_END 2028-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2028-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm LIHTC_EXTENDED_USE_END 2028-01-01 [REPORTED] via LURA / REUA from our file; confirm owner notice against the PuSH-CP log / ask OHCS before any demand letter · flags Verify — Notice Log
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting, sizing-lihtc-permanent-debt · documents to request: 2

### [#8] Rose Schnitzer Tower — Portland  Route [recap_committee] Queue [ACT] Score [61.6] Units at risk [235] Public UPB $3,200,000
- Units 235 · restricted 235 (units_basis total_assumed_restricted) · HAP 233 · PRAC 0 · other RA 0 · PSH 0 · flags [elderly;disabled]
- First agency act-by: HAP_OPTOUT_NOTICE_DEADLINE 2026-12-10 [DERIVED] — 2.2 months · owner pbca_liaison
- Owner cliff: AGENCY_LOAN_MATURITY 2027-12-10 [REPORTED] — band URGENT
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status unknown · recap_status none · secondary routes servicing_watch
- Our position: loan L-OHCS-0008 · $3,200,000 hard_pay · matures 2027-12-10 [RECORDED] · affordability_end n/a · recapture none · covenant_status current · am_officer M. Okafor
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_nonprofit_gp · Cedar Sinai Park -Clay Tower Apartments LP · sponsor_cliff_count 1
- Intervention: loan_extension_recast_memo — am_officer — loan documents; NHA 236(e)(2); Notice H 2013-25; 24 CFR 92.252 (verify current text before sending) — owner notice: yes · tenant notice: no — notice address: not on file [unknown] — first action: Draft the committee memo: UPB, payment-type change, extension or resubordination, senior cliff, restricted-NOI capacity
- Evidence: AGENCY_LOAN_MATURITY 2027-12-10 [RECORDED] agency_servicing; LOAN_MATURITY 2027-12-10 [REPORTED] agency_servicing; HAP_EXPIRATION 2027-12-10 [REPORTED] OHCS OAHI p9yn-ftai 20261002; SOFT_PROGRAM_END 2029-05-15 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm HAP_EXPIRATION 2027-12-10 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting, lihtc-lpa-reviewer, sizing-lihtc-permanent-debt · documents to request: 3

### [#9] St Anthony Village — Portland  Route [recap_committee] Queue [ACT] Score [61.5] Units at risk [127] Public UPB $700,000
- Units 127 · restricted 127 (units_basis total_assumed_restricted) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [elderly]
- First agency act-by: PUSH_WINDOW_PREP 2026-01-01 [DERIVED] — -9.1 months · owner push_program_manager
- Owner cliff: LIHTC_EXTENDED_USE_END 2029-01-01 [REPORTED] — band APPROACHING
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none · secondary routes notice_compliance;servicing_watch
- Our position: loan L-OHCS-0007 · $700,000 hard_pay · matures 2030-12-31 [RECORDED] · affordability_end n/a · recapture none · covenant_status default · am_officer J. Rivera
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · St Anthony Village Associates Limited Partnership · sponsor_cliff_count 1
- Intervention: loan_extension_recast_memo — am_officer — loan documents; NHA 236(e)(2); Notice H 2013-25; 24 CFR 92.252 (verify current text before sending) — owner notice: yes · tenant notice: no — notice address: not on file [unknown] — first action: Draft the committee memo: UPB, payment-type change, extension or resubordination, senior cliff, restricted-NOI capacity
- Evidence: COVENANT_DEFAULT 2026-10-04 [RECORDED] agency_servicing; LIHTC_EXTENDED_USE_END 2029-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2029-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002; AGENCY_LOAN_MATURITY 2030-12-31 [RECORDED] agency_servicing
- Verify before acting: confirm LIHTC_EXTENDED_USE_END 2029-01-01 [REPORTED] via LURA / REUA from our file; confirm owner notice against the PuSH-CP log / ask OHCS before any demand letter · flags Verify — Notice Log
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting, lihtc-lpa-reviewer, sizing-lihtc-permanent-debt · documents to request: 2

### Servicing watch (servicing_watch) — 5 in CRITICAL / URGENT / APPROACHING

### [#10] Village Garden Apartments — Portland  Route [servicing_watch] Queue [PLAN] Score [45.6] Units at risk [35] Public UPB $1,200,000
- Units 35 · restricted 35 (units_basis total_assumed_restricted) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2026-06-01 [DERIVED] — -4.1 months · owner push_program_manager
- Owner cliff: SOFT_PROGRAM_END 2029-05-15 [REPORTED] — band APPROACHING
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none · secondary routes notice_compliance
- Our position: loan;grant L-OHCS-0001 · $1,200,000 residual_receipts · matures 2031-06-30 [RECORDED] · affordability_end 2029-06-01 · recapture none · covenant_status current · am_officer J. Rivera
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Village Garden, LLC · sponsor_cliff_count 1
- Intervention: servicing_watch_memo — am_officer — loan / regulatory agreement (monitoring only) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: 15230 NE Sandy Blvd, Portland OR 97230 [regulatory_agreement] — first action: Servicing watch memo: confirm the trigger (our maturity, affordability end, senior cliff) against the loan file; calendar the recast / extension decision; no enforcement correspondence while covenant_status is current
- Evidence: SOFT_PROGRAM_END 2029-05-15 [REPORTED] OHCS OAHI p9yn-ftai 20261002; AFFORDABILITY_PERIOD_END 2029-06-01 [RECORDED] agency_servicing; AFFORDABILITY_PERIOD_END 2029-06-01 [RECORDED] agency_servicing; LIHTC_EXTENDED_USE_END 2029-06-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2029-06-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002; AGENCY_LOAN_MATURITY 2031-06-30 [RECORDED] agency_servicing
- Verify before acting: confirm LIHTC_EXTENDED_USE_END 2029-06-01 [REPORTED] via LURA / REUA from our file; confirm PUSH_FIRST_NOTICE_DUE 2026-12-01 [DERIVED] via source document
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, sizing-lihtc-permanent-debt · documents to request: 3

### [#11] Fixture Badly Typed — Portland  Route [servicing_watch] Queue [PLAN] Score [44.0] Units at risk [24] Public UPB $650,000
- Units 24 · restricted 24 (units_basis reported_buckets) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2028-06-30 [DERIVED] — 20.9 months · owner push_program_manager
- Owner cliff: AFFORDABILITY_PERIOD_END 2029-06-30 [RECORDED] — band APPROACHING
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: loan L-OHCS-0010;L-OHCS-0011 · $650,000 residual_receipts · matures 2032-06-30 [RECORDED] · affordability_end 2031-06-30 · recapture none · covenant_status current · am_officer A. Chen
- Physical: no physical / REAC signal in this run
- Sponsor capacity: nonprofit · Fixture Nonprofit Housing Inc · sponsor_cliff_count 1
- Intervention: servicing_watch_memo — am_officer — loan / regulatory agreement (monitoring only) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Servicing watch memo: confirm the trigger (our maturity, affordability end, senior cliff) against the loan file; calendar the recast / extension decision; no enforcement correspondence while covenant_status is current
- Evidence: AFFORDABILITY_PERIOD_END 2029-06-30 [RECORDED] agency_servicing; AFFORDABILITY_PERIOD_END 2031-06-30 [RECORDED] agency_servicing; AGENCY_LOAN_MATURITY 2032-06-30 [RECORDED] agency_servicing; AGENCY_LOAN_MATURITY 2032-06-30 [RECORDED] agency_servicing
- Verify before acting: - · flags Verify — PuSH Coverage
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, sizing-lihtc-permanent-debt

### [#12] Sumner Street Flats — Portland  Route [servicing_watch] Queue [PLAN] Score [36.0] Units at risk [12] Public UPB $480,000
- Units 12 · restricted 12 (units_basis reported_buckets) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2026-06-30 [DERIVED] — -3.2 months · owner push_program_manager
- Owner cliff: AFFORDABILITY_PERIOD_END 2029-06-30 [RECORDED] — band APPROACHING
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none · secondary routes notice_compliance
- Our position: loan L-OHCS-0014 · $480,000 deferred · matures 2039-06-30 [RECORDED] · affordability_end 2029-06-30 · recapture home_rental_repayment exposure $480,000 · covenant_status current · am_officer A. Chen
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Sumner Street Housing LLC · sponsor_cliff_count 1
- Intervention: covenant_recapture_review — cpd_program_manager — 24 CFR 92.252(e); 92.254(a)(5); 92.503; 24 CFR 93.302; 24 CFR 570.505 (verify current text before sending) — owner notice: yes · tenant notice: no — notice address: not on file [unknown] — first action: Review the recapture / resale or CDBG change-of-use position; demand repayment where triggered
- Evidence: AFFORDABILITY_PERIOD_END 2029-06-30 [RECORDED] agency_servicing; GRANT_RECAPTURE_END 2029-06-30 [RECORDED] agency_servicing
- Verify before acting: confirm PUSH_FIRST_NOTICE_DUE 2026-12-30 [DERIVED] via source document · flags Verify — PuSH Coverage
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, sizing-lihtc-permanent-debt

### [#13] Hollow Oak Commons — Portland  Route [servicing_watch] Queue [WATCH] Score [26.0] Units at risk [30] Public UPB $1,850,000
- Units 30 · restricted 30 (units_basis reported_buckets) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: none inside 12 months past / horizon
- Owner cliff: AGENCY_LOAN_MATURITY 2029-06-30 [RECORDED] — band APPROACHING
- Declared intent / notice status: notice_status unknown · tenant_notice_status n/a · hap_renewal_request_status n/a · recap_status none
- Our position: loan L-OHCS-0013 · $1,850,000 residual_receipts · matures 2029-06-30 [RECORDED] · affordability_end n/a · recapture none · covenant_status watch · am_officer J. Rivera
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Hollow Oak Housing LLC · sponsor_cliff_count 1
- Intervention: covenant_enforcement_notice — am_officer — loan / regulatory agreement covenants; 24 CFR 92.504(d); NSPIRE scoring notice (verify current text before sending) — owner notice: yes · tenant notice: no — notice address: not on file [unknown] — first action: Covenant monitoring: default / cure notice per loan documents; inspection and reserve review
- Evidence: AGENCY_LOAN_MATURITY 2029-06-30 [RECORDED] agency_servicing
- Verify before acting: -
- Handoffs ready: -

### [#14] Fixture Authority Court (HACC) — Milwaukie  Route [servicing_watch] Queue [WATCH] Score [26.0] Units at risk [40] Public UPB n/a
- Units 40 · restricted 40 (units_basis reported_buckets) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2028-03-04 [DERIVED] — 17.0 months · owner push_program_manager
- Owner cliff: AFFORDABILITY_PERIOD_END 2031-03-04 [RECORDED] — band MONITOR
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: loan L-OHCS-0009 · $650,000 deferred · matures 2031-03-04 [RECORDED] · affordability_end 2031-03-04 · recapture none · covenant_status current · am_officer A. Chen
- Physical: no physical / REAC signal in this run
- Sponsor capacity: housing_authority · Housing Authority of Clackamas County · sponsor_cliff_count 0
- Intervention: servicing_watch_memo — am_officer — loan / regulatory agreement (monitoring only) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Servicing watch memo: confirm the trigger (our maturity, affordability end, senior cliff) against the loan file; calendar the recast / extension decision; no enforcement correspondence while covenant_status is current
- Evidence: AFFORDABILITY_PERIOD_END 2031-03-04 [RECORDED] agency_servicing; AGENCY_LOAN_MATURITY 2031-03-04 [RECORDED] agency_servicing
- Verify before acting: -
- Handoffs ready: -

### NOFA / product offers (nofa_offer) — 79 in CRITICAL / URGENT / APPROACHING

### [#15] STADIUM STATION — Portland  Route [nofa_offer] Queue [ACT] Score [52.5] Units at risk [115] Public UPB n/a
- Units 115 · restricted 115 (units_basis total_assumed_restricted) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_SECOND_NOTICE_DUE 2026-01-01 [DERIVED] — -9.1 months · owner push_program_manager
- Owner cliff: LIHTC_EXTENDED_USE_END 2028-01-01 [REPORTED] — band URGENT
- Declared intent / notice status: notice_status unknown · tenant_notice_status n/a_pre_operative · hap_renewal_request_status n/a · recap_status none · secondary routes notice_compliance;ta_sponsor
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: nonprofit · Hearthstone Housing Foundation & Bayside Communities · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: LIHTC_EXTENDED_USE_END 2028-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2028-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm LIHTC_EXTENDED_USE_END 2028-01-01 [REPORTED] via LURA / REUA from our file; confirm owner notice against the PuSH-CP log / ask OHCS before any demand letter · flags Verify — PuSH Coverage;Verify — Notice Log
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 2

### [#16] Gray's Landing — Portland  Route [nofa_offer] Queue [PLAN] Score [49.5] Units at risk [209] Public UPB n/a
- Units 209 · restricted 209 (units_basis reported_buckets) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2069-11-07 [DERIVED] — 517.8 months · owner push_program_manager
- Owner cliff: LIHTC_EXTENDED_USE_END 2029-01-01 [REPORTED] — band APPROACHING
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none · secondary routes ta_sponsor
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_nonprofit_gp · REACH B49 Partners Limited Partnership · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: LIHTC_COMPLIANCE_END 2026-04-01 [DERIVED] OHCS OAHI p9yn-ftai 20261002; LIHTC_EXTENDED_USE_END 2029-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002; SOFT_PROGRAM_END 2029-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm LIHTC_EXTENDED_USE_END 2029-01-01 [REPORTED] via LURA / REUA from our file
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 3

### [#17] Bethany Meadows I — Portland  Route [nofa_offer] Queue [PLAN] Score [46.5] Units at risk [208] Public UPB n/a
- Units 208 · restricted 208 (units_basis reported_buckets) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: none inside 12 months past / horizon
- Owner cliff: LIHTC_EXTENDED_USE_END 2027-01-01 [REPORTED] — band CRITICAL
- Declared intent / notice status: notice_status unknown · tenant_notice_status n/a_pre_operative · hap_renewal_request_status n/a · recap_status none · secondary routes notice_compliance
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Bethany Meadows Phase I and II LLC · sponsor_cliff_count 2
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: LIHTC_EXTENDED_USE_END 2027-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2027-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm LIHTC_EXTENDED_USE_END 2027-01-01 [REPORTED] via LURA / REUA from our file; confirm owner notice against the PuSH-CP log / ask OHCS before any demand letter · flags Verify — PuSH Coverage;Verify — Notice Log
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 2

### [#18] Pier Park Apartments — Portland  Route [nofa_offer] Queue [PLAN] Score [46.5] Units at risk [164] Public UPB n/a
- Units 164 · restricted 164 (units_basis reported_buckets) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: none inside 12 months past / horizon
- Owner cliff: LIHTC_EXTENDED_USE_END 2027-01-01 [REPORTED] — band CRITICAL
- Declared intent / notice status: notice_status unknown · tenant_notice_status n/a_pre_operative · hap_renewal_request_status n/a · recap_status none · secondary routes notice_compliance
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Post Pier Park, LP · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: LIHTC_EXTENDED_USE_END 2027-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2027-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm LIHTC_EXTENDED_USE_END 2027-01-01 [REPORTED] via LURA / REUA from our file; confirm owner notice against the PuSH-CP log / ask OHCS before any demand letter · flags Verify — PuSH Coverage;Verify — Notice Log
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 2

### [#19] YARDS AT UNION STATION B — Portland  Route [nofa_offer] Queue [PLAN] Score [46.5] Units at risk [321] Public UPB n/a
- Units 321 · restricted 321 (units_basis total_assumed_restricted) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2026-01-01 [DERIVED] — -9.1 months · owner push_program_manager
- Owner cliff: LIHTC_EXTENDED_USE_END 2029-01-01 [REPORTED] — band APPROACHING
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none · secondary routes notice_compliance
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: individual_owner_of_record · Bell, David · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: LIHTC_EXTENDED_USE_END 2029-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2029-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm LIHTC_EXTENDED_USE_END 2029-01-01 [REPORTED] via LURA / REUA from our file; confirm owner notice against the PuSH-CP log / ask OHCS before any demand letter · flags Verify — PuSH Coverage;Verify — Notice Log
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 2

### [#20] Berry Ridge Apartments — Gresham  Route [nofa_offer] Queue [PLAN] Score [46.5] Units at risk [248] Public UPB n/a
- Units 248 · restricted 248 (units_basis reported_buckets) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2026-01-01 [DERIVED] — -9.1 months · owner push_program_manager
- Owner cliff: LIHTC_EXTENDED_USE_END 2029-01-01 [REPORTED] — band APPROACHING
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none · secondary routes notice_compliance
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Berry Ridge Gresham LLC · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: LIHTC_EXTENDED_USE_END 2029-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2029-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm LIHTC_EXTENDED_USE_END 2029-01-01 [REPORTED] via LURA / REUA from our file; confirm owner notice against the PuSH-CP log / ask OHCS before any demand letter · flags Verify — PuSH Coverage;Verify — Notice Log
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 2

### [#21] Hawthorne Villa Apartments — Tigard  Route [nofa_offer] Queue [PLAN] Score [46.5] Units at risk [119] Public UPB n/a
- Units 119 · restricted 119 (units_basis total_assumed_restricted) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: none inside 12 months past / horizon
- Owner cliff: LIHTC_EXTENDED_USE_END 2027-01-01 [REPORTED] — band CRITICAL
- Declared intent / notice status: notice_status unknown · tenant_notice_status n/a_pre_operative · hap_renewal_request_status n/a · recap_status none · secondary routes notice_compliance
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Hawthorne Villa Apartments General Partnership · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: LIHTC_EXTENDED_USE_END 2027-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2027-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm LIHTC_EXTENDED_USE_END 2027-01-01 [REPORTED] via LURA / REUA from our file; confirm owner notice against the PuSH-CP log / ask OHCS before any demand letter · flags Verify — PuSH Coverage;Verify — Notice Log
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 2

### [#22] Linc245 (fka Village at Lovejoy Fountain) — Portland  Route [nofa_offer] Queue [PLAN] Score [46.5] Units at risk [198] Public UPB n/a
- Units 198 · restricted 198 (units_basis total_assumed_restricted) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2026-01-01 [DERIVED] — -9.1 months · owner push_program_manager
- Owner cliff: LIHTC_EXTENDED_USE_END 2029-01-01 [REPORTED] — band APPROACHING
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none · secondary routes notice_compliance
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · VLF LLC · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: LIHTC_EXTENDED_USE_END 2029-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2029-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm LIHTC_EXTENDED_USE_END 2029-01-01 [REPORTED] via LURA / REUA from our file; confirm owner notice against the PuSH-CP log / ask OHCS before any demand letter · flags Verify — PuSH Coverage;Verify — Notice Log
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 2

### [#23] Terrace View Apartments — Tualatin  Route [nofa_offer] Queue [PLAN] Score [46.5] Units at risk [100] Public UPB n/a
- Units 100 · restricted 100 (units_basis total_assumed_restricted) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_SECOND_NOTICE_DUE 2026-01-01 [DERIVED] — -9.1 months · owner push_program_manager
- Owner cliff: LIHTC_EXTENDED_USE_END 2028-01-01 [REPORTED] — band URGENT
- Declared intent / notice status: notice_status unknown · tenant_notice_status n/a_pre_operative · hap_renewal_request_status n/a · recap_status none · secondary routes notice_compliance
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Terrace View Tualatin LLC · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: LIHTC_EXTENDED_USE_END 2028-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2028-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm LIHTC_EXTENDED_USE_END 2028-01-01 [REPORTED] via LURA / REUA from our file; confirm owner notice against the PuSH-CP log / ask OHCS before any demand letter · flags Verify — PuSH Coverage;Verify — Notice Log
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 2

### [#24] Bethany Meadows II — Portland  Route [nofa_offer] Queue [PLAN] Score [46.5] Units at risk [132] Public UPB n/a
- Units 132 · restricted 132 (units_basis reported_buckets) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2026-01-01 [DERIVED] — -9.1 months · owner push_program_manager
- Owner cliff: LIHTC_EXTENDED_USE_END 2029-01-01 [REPORTED] — band APPROACHING
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none · secondary routes notice_compliance
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Bethany Meadows Phase I and II LLC · sponsor_cliff_count 2
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: LIHTC_EXTENDED_USE_END 2029-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2029-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm LIHTC_EXTENDED_USE_END 2029-01-01 [REPORTED] via LURA / REUA from our file; confirm owner notice against the PuSH-CP log / ask OHCS before any demand letter · flags Verify — PuSH Coverage;Verify — Notice Log
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 2

### [#25] Belmont Dairy — Portland  Route [nofa_offer] Queue [PLAN] Score [42.0] Units at risk [85] Public UPB n/a
- Units 85 · restricted 85 (units_basis total_assumed_restricted) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: none inside 12 months past / horizon
- Owner cliff: LIHTC_EXTENDED_USE_END 2027-01-01 [REPORTED] — band CRITICAL
- Declared intent / notice status: notice_status unknown · tenant_notice_status n/a_pre_operative · hap_renewal_request_status n/a · recap_status none · secondary routes notice_compliance
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Belmont Dairy Preservation Partners LLC · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: LIHTC_EXTENDED_USE_END 2027-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2027-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm LIHTC_EXTENDED_USE_END 2027-01-01 [REPORTED] via LURA / REUA from our file; confirm owner notice against the PuSH-CP log / ask OHCS before any demand letter · flags Verify — PuSH Coverage;Verify — Notice Log
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 2

### [#26] Floyd Light Apartments — Portland  Route [nofa_offer] Queue [PLAN] Score [42.0] Units at risk [51] Public UPB n/a
- Units 51 · restricted 51 (units_basis total_assumed_restricted) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: none inside 12 months past / horizon
- Owner cliff: LIHTC_EXTENDED_USE_END 2027-01-01 [REPORTED] — band CRITICAL
- Declared intent / notice status: notice_status unknown · tenant_notice_status n/a_pre_operative · hap_renewal_request_status n/a · recap_status none · secondary routes notice_compliance
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Floyd Light Apartments L.L.C. · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: LIHTC_EXTENDED_USE_END 2027-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2027-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm LIHTC_EXTENDED_USE_END 2027-01-01 [REPORTED] via LURA / REUA from our file; confirm owner notice against the PuSH-CP log / ask OHCS before any demand letter · flags Verify — PuSH Coverage;Verify — Notice Log
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 2

### [#27] FIFTH AVENUE PLACE APTS — Portland  Route [nofa_offer] Queue [PLAN] Score [42.0] Units at risk [70] Public UPB n/a
- Units 70 · restricted 70 (units_basis total_assumed_restricted) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2026-01-01 [DERIVED] — -9.1 months · owner push_program_manager
- Owner cliff: LIHTC_EXTENDED_USE_END 2029-01-01 [REPORTED] — band APPROACHING
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none · secondary routes notice_compliance
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: individual_owner_of_record · Menashe, Michael · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: LIHTC_EXTENDED_USE_END 2029-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2029-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm LIHTC_EXTENDED_USE_END 2029-01-01 [REPORTED] via LURA / REUA from our file; confirm owner notice against the PuSH-CP log / ask OHCS before any demand letter · flags Verify — PuSH Coverage;Verify — Notice Log
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 2

### [#28] Esperanza Court — Portland  Route [nofa_offer] Queue [PLAN] Score [40.7] Units at risk [70] Public UPB n/a
- Units 70 · restricted 70 (units_basis reported_buckets) · HAP 0 · PRAC 0 · other RA 14 · PSH 14 · flags [psh]
- First agency act-by: PUSH_WINDOW_PREP 2066-01-01 [DERIVED] — 471.5 months · owner push_program_manager
- Owner cliff: SOFT_PROGRAM_END 2029-04-09 [REPORTED] — band APPROACHING
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_nonprofit_gp · Esperanza Court Limited Partnership · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: SOFT_PROGRAM_END 2029-04-09 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2029-04-09 [REPORTED] via regulatory agreement from our file
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 1

### [#29] Buckman Heights — Portland  Route [nofa_offer] Queue [PLAN] Score [40.5] Units at risk [144] Public UPB n/a
- Units 144 · restricted 144 (units_basis total_assumed_restricted) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2031-04-15 [DERIVED] — 54.4 months · owner push_program_manager
- Owner cliff: LIHTC_EXTENDED_USE_END 2028-01-01 [REPORTED] — band URGENT
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · GM Buckman Heights, LLC · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: LIHTC_EXTENDED_USE_END 2028-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2034-04-15 [REPORTED] OHCS OAHI p9yn-ftai 20261002; SOFT_PROGRAM_END 2034-04-15 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm LIHTC_EXTENDED_USE_END 2028-01-01 [REPORTED] via LURA / REUA from our file
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 3

### [#30] Lincoln Woods — Portland  Route [nofa_offer] Queue [PLAN] Score [39.8] Units at risk [70] Public UPB n/a
- Units 70 · restricted 70 (units_basis reported_buckets) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2064-01-01 [DERIVED] — 447.5 months · owner push_program_manager
- Owner cliff: SOFT_PROGRAM_END 2027-11-19 [REPORTED] — band URGENT
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_nonprofit_gp · Lincoln Woods Housing Limited Partnership · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: SOFT_PROGRAM_END 2027-11-19 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2027-11-19 [REPORTED] via regulatory agreement from our file
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 1

### [#31] 333 Oak Apartments — Portland  Route [nofa_offer] Queue [PLAN] Score [39.1] Units at risk [90] Public UPB n/a
- Units 90 · restricted 90 (units_basis reported_buckets) · HAP 90 · PRAC 0 · other RA 0 · PSH 0 · flags [elderly;disabled]
- First agency act-by: HAP_OPTOUT_NOTICE_DEADLINE 2028-09-30 [DERIVED] — 23.9 months · owner pbca_liaison
- Owner cliff: HAP_EXPIRATION 2029-09-30 [REPORTED] — band APPROACHING
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_nonprofit_gp · Oak Associates Limited Partnership · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: HAP_EXPIRATION 2029-09-30 [REPORTED] OHCS OAHI p9yn-ftai 20261002; SOFT_PROGRAM_END 2031-01-15 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm HAP_EXPIRATION 2029-09-30 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 2

### [#32] Crestview Court — Beaverton  Route [nofa_offer] Queue [PLAN] Score [36.6] Units at risk [48] Public UPB n/a
- Units 48 · restricted 48 (units_basis reported_buckets) · HAP 48 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: HAP_OPTOUT_NOTICE_DEADLINE 2031-02-28 [DERIVED] — 52.9 months · owner pbca_liaison
- Owner cliff: SOFT_PROGRAM_END 2028-03-14 [DERIVED] — band URGENT
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none · secondary routes ta_sponsor
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_nonprofit_gp · Northwest Crestview Court LLC · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: LIHTC_COMPLIANCE_END 2027-03-14 [DERIVED] OHCS OAHI p9yn-ftai 20261002; SOFT_PROGRAM_END 2028-03-14 [REPORTED] OHCS OAHI p9yn-ftai 20261002; HAP_EXPIRATION 2032-02-29 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2028-03-14 [REPORTED] via regulatory agreement from our file; confirm HAP_EXPIRATION 2032-02-29 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 3

### [#33] Creekside Woods — Wilsonville  Route [nofa_offer] Queue [PLAN] Score [36.4] Units at risk [84] Public UPB n/a
- Units 84 · restricted 84 (units_basis total_assumed_restricted) · HAP 0 · PRAC 44 · other RA 0 · PSH 0 · flags [elderly]
- First agency act-by: PUSH_WINDOW_PREP 2066-12-31 [DERIVED] — 483.5 months · owner push_program_manager
- Owner cliff: HAP_EXPIRATION 2027-12-31 [REPORTED] — band URGENT
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Creekside Woods Limited Partnership · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: HAP_EXPIRATION 2027-12-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002; SOFT_PROGRAM_END 2031-12-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm HAP_EXPIRATION 2027-12-31 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 2

### [#34] Upshur House — Portland  Route [nofa_offer] Queue [PLAN] Score [36.4] Units at risk [30] Public UPB n/a
- Units 30 · restricted 30 (units_basis reported_buckets) · HAP 30 · PRAC 0 · other RA 0 · PSH 5 · flags [psh]
- First agency act-by: HAP_OPTOUT_NOTICE_DEADLINE 2029-04-30 [DERIVED] — 30.9 months · owner pbca_liaison
- Owner cliff: HAP_EXPIRATION 2030-04-30 [REPORTED] — band MONITOR
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_nonprofit_gp · Upshur Renewal Housing, LP · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: HAP_EXPIRATION 2030-04-30 [REPORTED] OHCS OAHI p9yn-ftai 20261002; SOFT_PROGRAM_END 2032-04-10 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm HAP_EXPIRATION 2030-04-30 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 2

### [#35] Roselyn Apartments — Portland  Route [nofa_offer] Queue [PLAN] Score [35.7] Units at risk [31] Public UPB n/a
- Units 31 · restricted 31 (units_basis reported_buckets) · HAP 31 · PRAC 0 · other RA 0 · PSH 0 · flags [elderly;disabled]
- First agency act-by: HAP_OPTOUT_NOTICE_DEADLINE 2028-05-25 [DERIVED] — 19.7 months · owner pbca_liaison
- Owner cliff: HAP_EXPIRATION 2029-05-25 [REPORTED] — band APPROACHING
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_nonprofit_gp · Roselyn Renewal LLC · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: HAP_EXPIRATION 2029-05-25 [REPORTED] OHCS OAHI p9yn-ftai 20261002; SOFT_PROGRAM_END 2030-07-08 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm HAP_EXPIRATION 2029-05-25 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 2

### [#36] Country Squire Apts — Portland  Route [nofa_offer] Queue [PLAN] Score [35.4] Units at risk [32] Public UPB n/a
- Units 32 · restricted 32 (units_basis reported_buckets) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: none inside 12 months past / horizon
- Owner cliff: SOFT_PROGRAM_END 2027-05-23 [REPORTED] — band CRITICAL
- Declared intent / notice status: notice_status unknown · tenant_notice_status n/a_pre_operative · hap_renewal_request_status n/a · recap_status none · secondary routes notice_compliance
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: nonprofit · Rose Community Development Corporation · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: REGULATORY_LATEST_END 2027-05-23 [REPORTED] OHCS OAHI p9yn-ftai 20261002; SOFT_PROGRAM_END 2027-05-23 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2027-05-23 [REPORTED] via regulatory agreement from our file; confirm owner notice against the PuSH-CP log / ask OHCS before any demand letter · flags Verify — Notice Log
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 2

### [#37] Wiedemann Park Apartments — Wilsonville  Route [nofa_offer] Queue [PLAN] Score [34.8] Units at risk [58] Public UPB n/a
- Units 58 · restricted 58 (units_basis reported_buckets) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2027-01-01 [DERIVED] — 2.9 months · owner push_program_manager
- Owner cliff: LIHTC_EXTENDED_USE_END 2030-01-01 [REPORTED] — band MONITOR
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none · secondary routes ta_sponsor
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: housing_authority · Wiedemann Park Apts Limited Partnership · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: LIHTC_EXTENDED_USE_END 2030-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2030-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm LIHTC_EXTENDED_USE_END 2030-01-01 [REPORTED] via LURA / REUA from our file
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 2

### [#38] Rosewood Terrace — Oregon City  Route [nofa_offer] Queue [PLAN] Score [34.6] Units at risk [38] Public UPB n/a
- Units 38 · restricted 38 (units_basis reported_buckets) · HAP 38 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: HAP_OPTOUT_NOTICE_DEADLINE 2037-05-31 [DERIVED] — 128.0 months · owner pbca_liaison
- Owner cliff: SOFT_PROGRAM_END 2029-04-01 [REPORTED] — band APPROACHING
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: housing_authority · Northwest Rosewood Terrace LLC · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: SOFT_PROGRAM_END 2029-04-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2029-04-01 [REPORTED] via regulatory agreement from our file; confirm HAP_EXPIRATION 2038-05-31 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 1

### [#39] 1200 BUILDING — Portland  Route [nofa_offer] Queue [PLAN] Score [34.0] Units at risk [89] Public UPB n/a
- Units 89 · restricted 89 (units_basis reported_buckets) · HAP 89 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: HAP_OPTOUT_NOTICE_DEADLINE 2031-08-31 [DERIVED] — 58.9 months · owner pbca_liaison
- Owner cliff: SOFT_PROGRAM_END 2029-02-01 [REPORTED] — band APPROACHING
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: unknown · owner not on file · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: SOFT_PROGRAM_END 2029-02-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002; HAP_EXPIRATION 2032-08-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2029-02-01 [REPORTED] via regulatory agreement from our file; confirm HAP_EXPIRATION 2032-08-31 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 2

### [#40] Broadway Vantage — Portland  Route [nofa_offer] Queue [PLAN] Score [33.8] Units at risk [58] Public UPB n/a
- Units 58 · restricted 58 (units_basis reported_buckets) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2065-07-18 [DERIVED] — 466.0 months · owner push_program_manager
- Owner cliff: SOFT_PROGRAM_END 2029-03-19 [REPORTED] — band APPROACHING
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · 82nd Avenue Limited Partnership · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: SOFT_PROGRAM_END 2029-03-19 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2029-03-19 [REPORTED] via regulatory agreement from our file
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 1

### [#41] ELDERPLACE IN CULLY — Portland  Route [nofa_offer] Queue [PLAN] Score [33.6] Units at risk [42] Public UPB n/a
- Units 42 · restricted 42 (units_basis total_assumed_restricted) · HAP 0 · PRAC 0 · other RA 6 · PSH 0 · flags [-]
- First agency act-by: none inside 12 months past / horizon
- Owner cliff: SOFT_PROGRAM_END 2026-12-15 [REPORTED] — band CRITICAL
- Declared intent / notice status: notice_status unknown · tenant_notice_status n/a_pre_operative · hap_renewal_request_status n/a · recap_status none · secondary routes notice_compliance
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: nonprofit · Providence Health & Services - Oregon · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: REGULATORY_LATEST_END 2026-12-15 [REPORTED] OHCS OAHI p9yn-ftai 20261002; SOFT_PROGRAM_END 2026-12-15 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2026-12-15 [REPORTED] via regulatory agreement from our file; confirm owner notice against the PuSH-CP log / ask OHCS before any demand letter · flags Verify — Notice Log
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 2

### [#42] Whispering Pines Senior Village — Estacada  Route [nofa_offer] Queue [PLAN] Score [33.4] Units at risk [63] Public UPB n/a
- Units 63 · restricted 63 (units_basis total_assumed_restricted) · HAP 0 · PRAC 62 · other RA 0 · PSH 0 · flags [elderly]
- First agency act-by: PUSH_WINDOW_PREP 2028-06-20 [DERIVED] — 20.6 months · owner push_program_manager
- Owner cliff: HAP_EXPIRATION 2028-05-31 [REPORTED] — band URGENT
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: nonprofit · Estacada VOA Elderly Housing Inc · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: HAP_EXPIRATION 2028-05-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2031-06-20 [REPORTED] OHCS OAHI p9yn-ftai 20261002; SOFT_PROGRAM_END 2031-06-20 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm HAP_EXPIRATION 2028-05-31 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 3

### [#43] New Columbia Haven 9 — Portland  Route [nofa_offer] Queue [PLAN] Score [33.4] Units at risk [44] Public UPB n/a
- Units 44 · restricted 44 (units_basis total_assumed_restricted) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2043-01-01 [DERIVED] — 195.2 months · owner push_program_manager
- Owner cliff: SOFT_PROGRAM_END 2026-10-06 [REPORTED] — band CRITICAL
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: housing_authority · Home Forward · sponsor_cliff_count 4
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: SOFT_PROGRAM_END 2026-10-06 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2026-10-06 [REPORTED] via regulatory agreement from our file
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 1

### [#44] Timber Grove Firwood Village — Sandy  Route [nofa_offer] Queue [PLAN] Score [33.4] Units at risk [24] Public UPB n/a
- Units 24 · restricted 24 (units_basis total_assumed_restricted) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2041-05-01 [DERIVED] — 175.1 months · owner push_program_manager
- Owner cliff: SOFT_PROGRAM_END 2027-05-25 [DERIVED] — band CRITICAL
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Timber Grove Apartments LLC · sponsor_cliff_count 2
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: LIHTC_COMPLIANCE_END 2027-05-23 [DERIVED] OHCS OAHI p9yn-ftai 20261002; SOFT_PROGRAM_END 2027-05-25 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2027-05-25 [REPORTED] via regulatory agreement from our file
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 2

### [#45] Tualatin Meadows — Tualatin  Route [nofa_offer] Queue [PLAN] Score [33.3] Units at risk [240] Public UPB n/a
- Units 240 · restricted 240 (units_basis reported_buckets) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2027-09-01 [DERIVED] — 10.9 months · owner push_program_manager
- Owner cliff: LIHTC_EXTENDED_USE_END 2030-09-01 [REPORTED] — band MONITOR
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Tualatin Meadows Apartments, LP · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: LIHTC_EXTENDED_USE_END 2030-09-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2030-09-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm LIHTC_EXTENDED_USE_END 2030-09-01 [REPORTED] via LURA / REUA from our file · flags Verify — PuSH Coverage
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 2

### [#46] Lake Crest Apartments — Milwaukie  Route [nofa_offer] Queue [PLAN] Score [33.3] Units at risk [229] Public UPB n/a
- Units 229 · restricted 229 (units_basis total_assumed_restricted) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2027-09-30 [DERIVED] — 11.9 months · owner push_program_manager
- Owner cliff: LIHTC_EXTENDED_USE_END 2030-09-30 [REPORTED] — band MONITOR
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · CR Lake Crest Communities, LLC · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: LIHTC_EXTENDED_USE_END 2030-09-30 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2030-09-30 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm LIHTC_EXTENDED_USE_END 2030-09-30 [REPORTED] via LURA / REUA from our file · flags Verify — PuSH Coverage
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 2

### [#47] Briarcreek Apartments — Hillsboro  Route [nofa_offer] Queue [PLAN] Score [33.3] Units at risk [216] Public UPB n/a
- Units 216 · restricted 216 (units_basis reported_buckets) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2027-01-01 [DERIVED] — 2.9 months · owner push_program_manager
- Owner cliff: LIHTC_EXTENDED_USE_END 2030-01-01 [REPORTED] — band MONITOR
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Briarcreek LIH Limited Partnership · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: LIHTC_EXTENDED_USE_END 2030-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2030-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm LIHTC_EXTENDED_USE_END 2030-01-01 [REPORTED] via LURA / REUA from our file · flags Verify — PuSH Coverage
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 2

### [#48] Collins Circle — Portland  Route [nofa_offer] Queue [PLAN] Score [33.3] Units at risk [124] Public UPB n/a
- Units 124 · restricted 124 (units_basis total_assumed_restricted) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2027-01-01 [DERIVED] — 2.9 months · owner push_program_manager
- Owner cliff: LIHTC_EXTENDED_USE_END 2030-01-01 [REPORTED] — band MONITOR
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Fairfield Collins Circle, LLC · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: LIHTC_EXTENDED_USE_END 2030-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2030-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm LIHTC_EXTENDED_USE_END 2030-01-01 [REPORTED] via LURA / REUA from our file · flags Verify — PuSH Coverage
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 2

### [#49] MARY ANN, THE — Beaverton  Route [nofa_offer] Queue [PLAN] Score [33.0] Units at risk [54] Public UPB n/a
- Units 54 · restricted 54 (units_basis total_assumed_restricted) · HAP 0 · PRAC 0 · other RA 8 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2064-10-15 [DERIVED] — 456.9 months · owner push_program_manager
- Owner cliff: SOFT_PROGRAM_END 2027-10-02 [REPORTED] — band CRITICAL
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: nonprofit · REACH Community Development, Inc. · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: SOFT_PROGRAM_END 2027-10-02 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2027-10-02 [REPORTED] via regulatory agreement from our file
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 1

### [#50] Fifth Avenue Court — Portland  Route [nofa_offer] Queue [PLAN] Score [31.8] Units at risk [96] Public UPB n/a
- Units 96 · restricted 96 (units_basis total_assumed_restricted) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2027-06-15 [DERIVED] — 8.4 months · owner push_program_manager
- Owner cliff: LIHTC_EXTENDED_USE_END 2030-06-15 [REPORTED] — band MONITOR
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · 221 NW Fifth Avenue LLC · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: LIHTC_EXTENDED_USE_END 2030-06-15 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2030-06-15 [REPORTED] OHCS OAHI p9yn-ftai 20261002; SOFT_PROGRAM_END 2030-06-15 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm LIHTC_EXTENDED_USE_END 2030-06-15 [REPORTED] via LURA / REUA from our file
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 3

### [#51] Timber Grove Estacada Village — Estacada  Route [nofa_offer] Queue [PLAN] Score [31.6] Units at risk [48] Public UPB n/a
- Units 48 · restricted 48 (units_basis total_assumed_restricted) · HAP 0 · PRAC 0 · other RA 57 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2041-05-01 [DERIVED] — 175.1 months · owner push_program_manager
- Owner cliff: SOFT_PROGRAM_END 2027-05-25 [DERIVED] — band CRITICAL
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Timber Grove Apartments LLC · sponsor_cliff_count 2
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: LIHTC_COMPLIANCE_END 2027-05-23 [DERIVED] OHCS OAHI p9yn-ftai 20261002; SOFT_PROGRAM_END 2027-05-25 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2027-05-25 [REPORTED] via regulatory agreement from our file
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 2

### [#52] NEW COLUMBIA WOOLSEY II — Portland  Route [nofa_offer] Queue [PLAN] Score [31.6] Units at risk [47] Public UPB n/a
- Units 47 · restricted 47 (units_basis reported_buckets) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2043-01-01 [DERIVED] — 195.2 months · owner push_program_manager
- Owner cliff: SOFT_PROGRAM_END 2028-04-02 [REPORTED] — band URGENT
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: housing_authority · Home Forward · sponsor_cliff_count 4
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: SOFT_PROGRAM_END 2028-04-02 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2028-04-02 [REPORTED] via regulatory agreement from our file
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 1

### [#53] Westshore, The — Portland  Route [nofa_offer] Queue [PLAN] Score [31.5] Units at risk [113] Public UPB n/a
- Units 113 · restricted 113 (units_basis reported_buckets) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2033-01-01 [DERIVED] — 75.0 months · owner push_program_manager
- Owner cliff: SOFT_PROGRAM_END 2028-01-15 [REPORTED] — band URGENT
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Pine Street  Associates Limited Partnership · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: SOFT_PROGRAM_END 2028-01-15 [REPORTED] OHCS OAHI p9yn-ftai 20261002; LIHTC_EXTENDED_USE_END 2036-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2036-01-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2028-01-15 [REPORTED] via regulatory agreement from our file
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 3

### [#54] Miracles Club — Portland  Route [nofa_offer] Queue [PLAN] Score [30.6] Units at risk [40] Public UPB n/a
- Units 40 · restricted 40 (units_basis total_assumed_restricted) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2070-01-01 [DERIVED] — 519.6 months · owner push_program_manager
- Owner cliff: SOFT_PROGRAM_END 2027-06-01 [REPORTED] — band CRITICAL
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Miracles Club MLK Limited Partnership · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: LIHTC_COMPLIANCE_END 2026-07-27 [DERIVED] OHCS OAHI p9yn-ftai 20261002; SOFT_PROGRAM_END 2027-06-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2027-06-01 [REPORTED] via regulatory agreement from our file
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 2

### [#55] Garden Grove Apartments — Forest Grove  Route [nofa_offer] Queue [PLAN] Score [30.4] Units at risk [48] Public UPB n/a
- Units 48 · restricted 48 (units_basis reported_buckets) · HAP 48 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: HAP_OPTOUT_NOTICE_DEADLINE 2039-01-31 [DERIVED] — 148.1 months · owner pbca_liaison
- Owner cliff: SOFT_PROGRAM_END 2028-12-01 [REPORTED] — band APPROACHING
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Northwest Garden Grove LLC · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: SOFT_PROGRAM_END 2028-12-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2028-12-01 [REPORTED] via regulatory agreement from our file; confirm HAP_EXPIRATION 2040-01-31 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 1

### [#56] Weidler Commons — Portland  Route [nofa_offer] Queue [PLAN] Score [30.0] Units at risk [51] Public UPB n/a
- Units 51 · restricted 51 (units_basis reported_buckets) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2063-01-04 [DERIVED] — 435.6 months · owner push_program_manager
- Owner cliff: SOFT_PROGRAM_END 2027-05-29 [REPORTED] — band CRITICAL
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Weidler Renewal Limited Partnership · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: SOFT_PROGRAM_END 2027-05-29 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2027-05-29 [REPORTED] via regulatory agreement from our file
- Handoffs ready: critical-dates-tracker, forward-pipeline-and-news-intelligence, front-door-lihtc-underwriting · documents to request: 1

### [#57] Alma Gardens — Hillsboro  Route [nofa_offer] Queue [WATCH] Score [29.8] Units at risk [45] Public UPB n/a
- Units 45 · restricted 45 (units_basis total_assumed_restricted) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2071-01-01 [DERIVED] — 531.6 months · owner push_program_manager
- Owner cliff: SOFT_PROGRAM_END 2029-05-01 [DERIVED] — band APPROACHING
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Alma Gardens Limited Partnership · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: LIHTC_COMPLIANCE_END 2028-08-29 [DERIVED] OHCS OAHI p9yn-ftai 20261002; SOFT_PROGRAM_END 2029-05-01 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm LIHTC_COMPLIANCE_END 2028-08-29 [DERIVED] via 8609 / Compliance_Start confirmation
- Handoffs ready: -

### [#58] MLK-Wygant Housing — Portland  Route [nofa_offer] Queue [WATCH] Score [29.4] Units at risk [38] Public UPB n/a
- Units 38 · restricted 38 (units_basis total_assumed_restricted) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_FIRST_NOTICE_DUE 2026-02-15 [DERIVED] — -7.6 months · owner push_program_manager
- Owner cliff: SOFT_PROGRAM_END 2028-08-15 [REPORTED] — band URGENT
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none · secondary routes notice_compliance
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · MLK-Wygant LLC · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: REGULATORY_LATEST_END 2028-08-15 [REPORTED] OHCS OAHI p9yn-ftai 20261002; SOFT_PROGRAM_END 2028-08-15 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2028-08-15 [REPORTED] via regulatory agreement from our file; confirm owner notice against the PuSH-CP log / ask OHCS before any demand letter · flags Verify — Notice Log
- Handoffs ready: -

### [#59] Maples II — Hillsboro  Route [nofa_offer] Queue [WATCH] Score [29.2] Units at risk [21] Public UPB n/a
- Units 21 · restricted 21 (units_basis reported_buckets) · HAP 0 · PRAC 21 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2069-06-01 [DERIVED] — 512.5 months · owner push_program_manager
- Owner cliff: HAP_EXPIRATION 2028-08-31 [REPORTED] — band URGENT
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: nonprofit · Community Housing II, Inc. · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: HAP_EXPIRATION 2028-08-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm HAP_EXPIRATION 2028-08-31 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: -

### [#60] Scott Crest Plaza — Portland  Route [nofa_offer] Queue [WATCH] Score [28.9] Units at risk [42] Public UPB n/a
- Units 42 · restricted 42 (units_basis total_assumed_restricted) · HAP 42 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: HAP_OPTOUT_NOTICE_DEADLINE 2027-12-31 [DERIVED] — 14.9 months · owner pbca_liaison
- Owner cliff: HAP_EXPIRATION 2028-12-31 [REPORTED] — band APPROACHING
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_nonprofit_gp · Trillium Scott Crest Plaza Affordable Hsg LLC · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: HAP_EXPIRATION 2028-12-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm HAP_EXPIRATION 2028-12-31 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: -

### [#61] MYERS COURT — Portland  Route [nofa_offer] Queue [WATCH] Score [28.9] Units at risk [20] Public UPB n/a
- Units 20 · restricted 20 (units_basis total_assumed_restricted) · HAP 18 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: HAP_OPTOUT_NOTICE_DEADLINE 2029-09-30 [DERIVED] — 35.9 months · owner pbca_liaison
- Owner cliff: HAP_EXPIRATION 2030-09-30 [REPORTED] — band MONITOR
- Declared intent / notice status: notice_status unknown · tenant_notice_status n/a · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: housing_authority · HOUSING AUTHORITY OF CLACKAMAS COUNTY · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: HAP_EXPIRATION 2030-09-30 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2030-09-30 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm HAP_EXPIRATION 2030-09-30 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: -

### [#62] Fox Pointe Apartments — Milwaukie  Route [nofa_offer] Queue [WATCH] Score [28.8] Units at risk [96] Public UPB n/a
- Units 96 · restricted 96 (units_basis reported_buckets) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2027-11-30 [DERIVED] — 13.9 months · owner push_program_manager
- Owner cliff: LIHTC_EXTENDED_USE_END 2030-11-30 [REPORTED] — band MONITOR
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Post Fox Pointe, LLC · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: LIHTC_EXTENDED_USE_END 2030-11-30 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2030-11-30 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm LIHTC_EXTENDED_USE_END 2030-11-30 [REPORTED] via LURA / REUA from our file · flags Verify — PuSH Coverage
- Handoffs ready: -

### [#63] ALBERTA SIMMONS PLAZA — Portland  Route [nofa_offer] Queue [WATCH] Score [28.3] Units at risk [74] Public UPB n/a
- Units 74 · restricted 74 (units_basis total_assumed_restricted) · HAP 0 · PRAC 73 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: none inside 12 months past / horizon
- Owner cliff: HAP_EXPIRATION 2028-07-31 [REPORTED] — band URGENT
- Declared intent / notice status: notice_status unknown · tenant_notice_status n/a · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: unknown · owner not on file · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: HAP_EXPIRATION 2028-07-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2028-07-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm REGULATORY_LATEST_END 2028-07-31 [REPORTED] via every recorded regulatory agreement; confirm HAP_EXPIRATION 2028-07-31 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: -

### [#64] WOODLAND HEIGHTS RETIREMENT COMMUNITY — Portland  Route [nofa_offer] Queue [WATCH] Score [28.3] Units at risk [58] Public UPB n/a
- Units 58 · restricted 58 (units_basis total_assumed_restricted) · HAP 0 · PRAC 58 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: none inside 12 months past / horizon
- Owner cliff: HAP_EXPIRATION 2028-06-30 [REPORTED] — band URGENT
- Declared intent / notice status: notice_status unknown · tenant_notice_status n/a · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: unknown · owner not on file · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: HAP_EXPIRATION 2028-06-30 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2028-06-30 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm REGULATORY_LATEST_END 2028-06-30 [REPORTED] via every recorded regulatory agreement; confirm HAP_EXPIRATION 2028-06-30 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: -

### [#65] KIRKLAND UNION MANOR III — Portland  Route [nofa_offer] Queue [WATCH] Score [28.3] Units at risk [56] Public UPB n/a
- Units 56 · restricted 56 (units_basis total_assumed_restricted) · HAP 0 · PRAC 56 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: none inside 12 months past / horizon
- Owner cliff: HAP_EXPIRATION 2028-06-30 [REPORTED] — band URGENT
- Declared intent / notice status: notice_status unknown · tenant_notice_status n/a · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: unknown · owner not on file · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: HAP_EXPIRATION 2028-06-30 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2028-06-30 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm REGULATORY_LATEST_END 2028-06-30 [REPORTED] via every recorded regulatory agreement; confirm HAP_EXPIRATION 2028-06-30 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: -

### [#66] SILVERCREST RESIDENCE — Portland  Route [nofa_offer] Queue [WATCH] Score [28.3] Units at risk [76] Public UPB n/a
- Units 76 · restricted 76 (units_basis total_assumed_restricted) · HAP 0 · PRAC 75 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: none inside 12 months past / horizon
- Owner cliff: HAP_EXPIRATION 2029-09-30 [REPORTED] — band APPROACHING
- Declared intent / notice status: notice_status unknown · tenant_notice_status n/a · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: unknown · owner not on file · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: HAP_EXPIRATION 2029-09-30 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2029-09-30 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm REGULATORY_LATEST_END 2029-09-30 [REPORTED] via every recorded regulatory agreement; confirm HAP_EXPIRATION 2029-09-30 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: -

### [#67] FOREST VILLA — Forest Grove  Route [nofa_offer] Queue [WATCH] Score [28.3] Units at risk [84] Public UPB n/a
- Units 84 · restricted 84 (units_basis total_assumed_restricted) · HAP 84 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: HAP_OPTOUT_NOTICE_DEADLINE 2029-09-30 [DERIVED] — 35.9 months · owner pbca_liaison
- Owner cliff: HAP_EXPIRATION 2030-09-30 [REPORTED] — band MONITOR
- Declared intent / notice status: notice_status unknown · tenant_notice_status n/a · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: unknown · owner not on file · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: HAP_EXPIRATION 2030-09-30 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2030-09-30 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm HAP_EXPIRATION 2030-09-30 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: -

### [#68] Martin Luther King Manor — Portland  Route [nofa_offer] Queue [WATCH] Score [28.3] Units at risk [16] Public UPB n/a
- Units 16 · restricted 16 (units_basis total_assumed_restricted) · HAP 15 · PRAC 0 · other RA 0 · PSH 0 · flags [elderly;disabled]
- First agency act-by: HAP_OPTOUT_NOTICE_DEADLINE 2028-06-30 [DERIVED] — 20.9 months · owner pbca_liaison
- Owner cliff: HAP_EXPIRATION 2029-06-30 [REPORTED] — band APPROACHING
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_nonprofit_gp · MLK Manor LLC · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: HAP_EXPIRATION 2029-06-30 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm HAP_EXPIRATION 2029-06-30 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: -

### [#69] Vermont Springs — Portland  Route [nofa_offer] Queue [WATCH] Score [28.3] Units at risk [15] Public UPB n/a
- Units 15 · restricted 15 (units_basis total_assumed_restricted) · HAP 14 · PRAC 0 · other RA 0 · PSH 0 · flags [elderly;disabled]
- First agency act-by: HAP_OPTOUT_NOTICE_DEADLINE 2028-08-31 [DERIVED] — 22.9 months · owner pbca_liaison
- Owner cliff: HAP_EXPIRATION 2029-08-31 [REPORTED] — band APPROACHING
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_nonprofit_gp · Vermont Springs Apartments LLC · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: HAP_EXPIRATION 2029-08-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm HAP_EXPIRATION 2029-08-31 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: -

### [#70] Trenton Terrace — Portland  Route [nofa_offer] Queue [WATCH] Score [27.4] Units at risk [66] Public UPB n/a
- Units 66 · restricted 66 (units_basis reported_buckets) · HAP 0 · PRAC 61 · other RA 0 · PSH 0 · flags [elderly]
- First agency act-by: PUSH_WINDOW_PREP 2044-01-01 [DERIVED] — 207.2 months · owner push_program_manager
- Owner cliff: HAP_EXPIRATION 2027-12-31 [REPORTED] — band URGENT
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Trenton Terrace Limited Partnership · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: HAP_EXPIRATION 2027-12-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm HAP_EXPIRATION 2027-12-31 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: -

### [#71] Patton Park Apartments — Portland  Route [nofa_offer] Queue [WATCH] Score [27.0] Units at risk [54] Public UPB n/a
- Units 54 · restricted 54 (units_basis reported_buckets) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2066-01-01 [DERIVED] — 471.5 months · owner push_program_manager
- Owner cliff: SOFT_PROGRAM_END 2029-09-16 [REPORTED] — band APPROACHING
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Patton Square Partners Limited Partnership · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: SOFT_PROGRAM_END 2029-09-16 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2029-09-16 [REPORTED] via regulatory agreement from our file
- Handoffs ready: -

### [#72] Leander Court — Portland  Route [nofa_offer] Queue [WATCH] Score [26.4] Units at risk [37] Public UPB n/a
- Units 37 · restricted 37 (units_basis reported_buckets) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2064-01-01 [DERIVED] — 447.5 months · owner push_program_manager
- Owner cliff: SOFT_PROGRAM_END 2028-04-28 [REPORTED] — band URGENT
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Leander Court Limited Partnership · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: SOFT_PROGRAM_END 2028-04-28 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2028-04-28 [REPORTED] via regulatory agreement from our file
- Handoffs ready: -

### [#73] Lafayette Court Apartments — Portland  Route [nofa_offer] Queue [WATCH] Score [24.9] Units at risk [32] Public UPB n/a
- Units 32 · restricted 32 (units_basis total_assumed_restricted) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [elderly]
- First agency act-by: PUSH_WINDOW_PREP 2026-12-15 [DERIVED] — 2.4 months · owner push_program_manager
- Owner cliff: SOFT_PROGRAM_END 2029-12-15 [REPORTED] — band MONITOR
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: nonprofit · Cascadia Health · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: REGULATORY_LATEST_END 2029-12-15 [REPORTED] OHCS OAHI p9yn-ftai 20261002; SOFT_PROGRAM_END 2029-12-15 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2029-12-15 [REPORTED] via regulatory agreement from our file
- Handoffs ready: -

### [#74] Gresham Recovery Center — Portland  Route [nofa_offer] Queue [WATCH] Score [24.0] Units at risk [18] Public UPB n/a
- Units 18 · restricted 18 (units_basis total_assumed_restricted) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [elderly;disabled]
- First agency act-by: none inside 12 months past / horizon
- Owner cliff: SOFT_PROGRAM_END 2027-02-15 [REPORTED] — band CRITICAL
- Declared intent / notice status: notice_status unknown · tenant_notice_status n/a_pre_operative · hap_renewal_request_status n/a · recap_status none · secondary routes notice_compliance
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · CODA Properties LLC · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: REGULATORY_LATEST_END 2027-02-15 [REPORTED] OHCS OAHI p9yn-ftai 20261002; SOFT_PROGRAM_END 2027-02-15 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2027-02-15 [REPORTED] via regulatory agreement from our file; confirm owner notice against the PuSH-CP log / ask OHCS before any demand letter · flags Verify — Notice Log
- Handoffs ready: -

### [#75] Clinton Street Apartments (aka Dual Diagnoisis) — Portland  Route [nofa_offer] Queue [WATCH] Score [24.0] Units at risk [16] Public UPB n/a
- Units 16 · restricted 16 (units_basis reported_buckets) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [disabled]
- First agency act-by: PUSH_WINDOW_PREP 2031-12-07 [DERIVED] — 62.2 months · owner push_program_manager
- Owner cliff: SOFT_PROGRAM_END 2027-02-15 [REPORTED] — band CRITICAL
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: nonprofit · Cascadia Health · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: SOFT_PROGRAM_END 2027-02-15 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2034-12-07 [REPORTED] OHCS OAHI p9yn-ftai 20261002; SOFT_PROGRAM_END 2034-12-07 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2027-02-15 [REPORTED] via regulatory agreement from our file
- Handoffs ready: -

### [#76] New Columbia Woolsey 1 — Portland  Route [nofa_offer] Queue [WATCH] Score [23.4] Units at risk [42] Public UPB n/a
- Units 42 · restricted 42 (units_basis reported_buckets) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2043-01-01 [DERIVED] — 195.2 months · owner push_program_manager
- Owner cliff: SOFT_PROGRAM_END 2028-04-02 [REPORTED] — band URGENT
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Woolsey Limited Partnership · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: SOFT_PROGRAM_END 2028-04-02 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2028-04-02 [REPORTED] via regulatory agreement from our file
- Handoffs ready: -

### [#77] Clackamas Apartments NCGC 45 — Clackamas  Route [nofa_offer] Queue [WATCH] Score [23.1] Units at risk [20] Public UPB n/a
- Units 20 · restricted 20 (units_basis total_assumed_restricted) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2027-12-15 [DERIVED] — 14.4 months · owner push_program_manager
- Owner cliff: SOFT_PROGRAM_END 2030-12-15 [REPORTED] — band MONITOR
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: housing_authority · Housing Authority of Clackamas County · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: REGULATORY_LATEST_END 2030-12-15 [REPORTED] OHCS OAHI p9yn-ftai 20261002; SOFT_PROGRAM_END 2030-12-15 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2030-12-15 [REPORTED] via regulatory agreement from our file
- Handoffs ready: -

### [#78] PROVIDENCE HOUSE — Portland  Route [nofa_offer] Queue [WATCH] Score [22.9] Units at risk [40] Public UPB n/a
- Units 40 · restricted 40 (units_basis total_assumed_restricted) · HAP 0 · PRAC 39 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: none inside 12 months past / horizon
- Owner cliff: HAP_EXPIRATION 2029-02-28 [REPORTED] — band APPROACHING
- Declared intent / notice status: notice_status unknown · tenant_notice_status n/a · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: unknown · owner not on file · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: HAP_EXPIRATION 2029-02-28 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2029-02-28 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm REGULATORY_LATEST_END 2029-02-28 [REPORTED] via every recorded regulatory agreement; confirm HAP_EXPIRATION 2029-02-28 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: -

### [#79] FIR GROVE — Portland  Route [nofa_offer] Queue [WATCH] Score [22.9] Units at risk [31] Public UPB n/a
- Units 31 · restricted 31 (units_basis total_assumed_restricted) · HAP 0 · PRAC 30 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: none inside 12 months past / horizon
- Owner cliff: HAP_EXPIRATION 2029-02-28 [REPORTED] — band APPROACHING
- Declared intent / notice status: notice_status unknown · tenant_notice_status n/a · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: unknown · owner not on file · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: HAP_EXPIRATION 2029-02-28 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2029-02-28 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm REGULATORY_LATEST_END 2029-02-28 [REPORTED] via every recorded regulatory agreement; confirm HAP_EXPIRATION 2029-02-28 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: -

### [#80] MAPLES I — Hillsboro  Route [nofa_offer] Queue [WATCH] Score [22.9] Units at risk [30] Public UPB n/a
- Units 30 · restricted 30 (units_basis total_assumed_restricted) · HAP 0 · PRAC 29 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: none inside 12 months past / horizon
- Owner cliff: HAP_EXPIRATION 2029-08-31 [REPORTED] — band APPROACHING
- Declared intent / notice status: notice_status unknown · tenant_notice_status n/a · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: unknown · owner not on file · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: HAP_EXPIRATION 2029-08-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2029-08-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm REGULATORY_LATEST_END 2029-08-31 [REPORTED] via every recorded regulatory agreement; confirm HAP_EXPIRATION 2029-08-31 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: -

### [#81] FOREST MANOR I — Forest Grove  Route [nofa_offer] Queue [WATCH] Score [22.9] Units at risk [28] Public UPB n/a
- Units 28 · restricted 28 (units_basis total_assumed_restricted) · HAP 19 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: HAP_OPTOUT_NOTICE_DEADLINE 2029-03-31 [DERIVED] — 29.9 months · owner pbca_liaison
- Owner cliff: HAP_EXPIRATION 2030-03-31 [REPORTED] — band MONITOR
- Declared intent / notice status: notice_status unknown · tenant_notice_status n/a · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: unknown · owner not on file · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: HAP_EXPIRATION 2030-03-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2030-03-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm HAP_EXPIRATION 2030-03-31 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: -

### [#82] ALOHA PROJECT — Beaverton  Route [nofa_offer] Queue [WATCH] Score [22.5] Units at risk [10] Public UPB n/a
- Units 10 · restricted 10 (units_basis total_assumed_restricted) · HAP 10 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: HAP_OPTOUT_NOTICE_DEADLINE 2026-12-31 [DERIVED] — 2.9 months · owner pbca_liaison
- Owner cliff: HAP_EXPIRATION 2027-12-31 [REPORTED] — band URGENT
- Declared intent / notice status: notice_status unknown · tenant_notice_status n/a · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: unknown · owner not on file · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: HAP_EXPIRATION 2027-12-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2027-12-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm HAP_EXPIRATION 2027-12-31 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: -

### [#83] McCuller Crossing — Portland  Route [nofa_offer] Queue [WATCH] Score [21.6] Units at risk [40] Public UPB n/a
- Units 40 · restricted 40 (units_basis reported_buckets) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2060-01-01 [DERIVED] — 399.4 months · owner push_program_manager
- Owner cliff: SOFT_PROGRAM_END 2027-06-29 [REPORTED] — band CRITICAL
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · McCuller Associates Limited Partnership · sponsor_cliff_count 1
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: SOFT_PROGRAM_END 2027-06-29 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2027-06-29 [REPORTED] via regulatory agreement from our file
- Handoffs ready: -

### [#84] ALBINA PLAZA — Portland  Route [nofa_offer] Queue [WATCH] Score [20.2] Units at risk [8] Public UPB n/a
- Units 8 · restricted 8 (units_basis total_assumed_restricted) · HAP 8 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: HAP_OPTOUT_NOTICE_DEADLINE 2028-05-31 [DERIVED] — 19.9 months · owner pbca_liaison
- Owner cliff: HAP_EXPIRATION 2029-05-31 [REPORTED] — band APPROACHING
- Declared intent / notice status: notice_status unknown · tenant_notice_status n/a · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: unknown · owner not on file · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: HAP_EXPIRATION 2029-05-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2029-05-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm REGULATORY_LATEST_END 2029-05-31 [REPORTED] via every recorded regulatory agreement; confirm HAP_EXPIRATION 2029-05-31 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: -

### [#85] GOOD SHEPHERD I — Portland  Route [nofa_offer] Queue [WATCH] Score [20.2] Units at risk [5] Public UPB n/a
- Units 5 · restricted 5 (units_basis total_assumed_restricted) · HAP 5 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: HAP_OPTOUT_NOTICE_DEADLINE 2028-01-31 [DERIVED] — 15.9 months · owner pbca_liaison
- Owner cliff: HAP_EXPIRATION 2029-01-31 [REPORTED] — band APPROACHING
- Declared intent / notice status: notice_status unknown · tenant_notice_status n/a · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: unknown · owner not on file · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: HAP_EXPIRATION 2029-01-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2029-01-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm REGULATORY_LATEST_END 2029-01-31 [REPORTED] via every recorded regulatory agreement; confirm HAP_EXPIRATION 2029-01-31 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: -

### [#86] GOOD SHEPHERD II — Portland  Route [nofa_offer] Queue [WATCH] Score [20.2] Units at risk [5] Public UPB n/a
- Units 5 · restricted 5 (units_basis total_assumed_restricted) · HAP 5 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: HAP_OPTOUT_NOTICE_DEADLINE 2028-01-31 [DERIVED] — 15.9 months · owner pbca_liaison
- Owner cliff: HAP_EXPIRATION 2029-01-31 [REPORTED] — band APPROACHING
- Declared intent / notice status: notice_status unknown · tenant_notice_status n/a · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: unknown · owner not on file · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: HAP_EXPIRATION 2029-01-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2029-01-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm REGULATORY_LATEST_END 2029-01-31 [REPORTED] via every recorded regulatory agreement; confirm HAP_EXPIRATION 2029-01-31 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: -

### [#87] FAULKNER PLACE — Portland  Route [nofa_offer] Queue [WATCH] Score [17.7] Units at risk [16] Public UPB n/a
- Units 16 · restricted 16 (units_basis total_assumed_restricted) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2027-11-15 [DERIVED] — 13.4 months · owner push_program_manager
- Owner cliff: SOFT_PROGRAM_END 2030-11-15 [REPORTED] — band MONITOR
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: nonprofit · Cascadia Behavioral Healthcare, Inc · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: REGULATORY_LATEST_END 2030-11-15 [REPORTED] OHCS OAHI p9yn-ftai 20261002; SOFT_PROGRAM_END 2030-11-15 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2030-11-15 [REPORTED] via regulatory agreement from our file
- Handoffs ready: -

### [#88] BARBARA ROBERTS — Portland  Route [nofa_offer] Queue [WATCH] Score [17.7] Units at risk [10] Public UPB n/a
- Units 10 · restricted 10 (units_basis total_assumed_restricted) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2028-07-15 [DERIVED] — 21.4 months · owner push_program_manager
- Owner cliff: SOFT_PROGRAM_END 2031-07-15 [REPORTED] — band MONITOR
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: nonprofit · Cascadia Behavioral Healthcare, Inc · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: REGULATORY_LATEST_END 2031-07-15 [REPORTED] OHCS OAHI p9yn-ftai 20261002; SOFT_PROGRAM_END 2031-07-15 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2031-07-15 [REPORTED] via regulatory agreement from our file
- Handoffs ready: -

### [#89] SMALLWOOD — Hillsboro  Route [nofa_offer] Queue [WATCH] Score [17.5] Units at risk [18] Public UPB n/a
- Units 18 · restricted 18 (units_basis total_assumed_restricted) · HAP 17 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: HAP_OPTOUT_NOTICE_DEADLINE 2029-08-23 [DERIVED] — 34.7 months · owner pbca_liaison
- Owner cliff: HAP_EXPIRATION 2030-08-23 [REPORTED] — band MONITOR
- Declared intent / notice status: notice_status unknown · tenant_notice_status n/a · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: unknown · owner not on file · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: HAP_EXPIRATION 2030-08-23 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2030-08-23 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm HAP_EXPIRATION 2030-08-23 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: -

### [#90] FOREST MANOR II — Forest Grove  Route [nofa_offer] Queue [WATCH] Score [17.5] Units at risk [6] Public UPB n/a
- Units 6 · restricted 6 (units_basis total_assumed_restricted) · HAP 6 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: HAP_OPTOUT_NOTICE_DEADLINE 2029-03-31 [DERIVED] — 29.9 months · owner pbca_liaison
- Owner cliff: HAP_EXPIRATION 2030-03-31 [REPORTED] — band MONITOR
- Declared intent / notice status: notice_status unknown · tenant_notice_status n/a · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: unknown · owner not on file · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: HAP_EXPIRATION 2030-03-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002; REGULATORY_LATEST_END 2030-03-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm HAP_EXPIRATION 2030-03-31 [REPORTED] via HAP contract / renewal request (HUD-9624) via the CA
- Handoffs ready: -

### [#91] FOREST GROVE BEEHIVE — Forest Grove  Route [nofa_offer] Queue [WATCH] Score [17.1] Units at risk [44] Public UPB n/a
- Units 44 · restricted 44 (units_basis total_assumed_restricted) · HAP 0 · PRAC 0 · other RA 9 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2027-12-15 [DERIVED] — 14.4 months · owner push_program_manager
- Owner cliff: SOFT_PROGRAM_END 2030-12-15 [REPORTED] — band MONITOR
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Forest Grove Beehive, LLC · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: REGULATORY_LATEST_END 2030-12-15 [REPORTED] OHCS OAHI p9yn-ftai 20261002; SOFT_PROGRAM_END 2030-12-15 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2030-12-15 [REPORTED] via regulatory agreement from our file
- Handoffs ready: -

### [#92] Studio Pointe Apts (fka Ellis Apts) — Portland  Route [nofa_offer] Queue [WATCH] Score [17.1] Units at risk [30] Public UPB n/a
- Units 30 · restricted 30 (units_basis total_assumed_restricted) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2027-12-31 [DERIVED] — 14.9 months · owner push_program_manager
- Owner cliff: SOFT_PROGRAM_END 2030-12-31 [REPORTED] — band MONITOR
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Studio Pointe, LLC · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: REGULATORY_LATEST_END 2030-12-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002; SOFT_PROGRAM_END 2030-12-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2030-12-31 [REPORTED] via regulatory agreement from our file · flags Verify — Conflicting Sources: Compliance_Start_Date 2020-10-20 is -1 months from Financial_Closing_Date 2020-11-20
- Handoffs ready: -

### [#93] Enclave 54 — Portland  Route [nofa_offer] Queue [WATCH] Score [17.1] Units at risk [28] Public UPB n/a
- Units 28 · restricted 28 (units_basis total_assumed_restricted) · HAP 0 · PRAC 0 · other RA 0 · PSH 0 · flags [-]
- First agency act-by: PUSH_WINDOW_PREP 2027-12-31 [DERIVED] — 14.9 months · owner push_program_manager
- Owner cliff: SOFT_PROGRAM_END 2030-12-31 [REPORTED] — band MONITOR
- Declared intent / notice status: notice_status unknown · tenant_notice_status unknown · hap_renewal_request_status n/a · recap_status none
- Our position: not in book
- Physical: no physical / REAC signal in this run
- Sponsor capacity: lihtc_partnership_forprofit_gp · Milwaukie Apartments LLC · sponsor_cliff_count 0
- Intervention: preservation_nofa_invitation — nofa_program_manager — ORS ch. 456/458 program statutes; 24 CFR 92; 24 CFR 93; IRC 42 (4%) (verify current text before sending) — owner notice: no · tenant notice: no — notice address: not on file [unknown] — first action: Invite a preservation application under the open product; align the award cohort 12-24 months before the cliff
- Evidence: REGULATORY_LATEST_END 2030-12-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002; SOFT_PROGRAM_END 2030-12-31 [REPORTED] OHCS OAHI p9yn-ftai 20261002
- Verify before acting: confirm SOFT_PROGRAM_END 2030-12-31 [REPORTED] via regulatory agreement from our file
- Handoffs ready: -

Beyond 36 months (summarized by band and route): MONITOR: nofa_offer 18; BEYOND: ta_sponsor 6; SCHEDULED: ta_sponsor 8

## Book Watchlist

| property | ids | book_kind | upb | payment_type | maturity (basis) | affordability_end | covenant_status | am_officer | route | queue |
|---|---|---|---|---|---|---|---|---|---|---|
| Yards at Union Station A | L-OHCS-0003 | loan | $2,400,000 | deferred | 2028-01-01 (RECORDED) | 2028-01-01 | current | M. Okafor | recap_committee | ESCALATE |
| Rose Schnitzer Tower | L-OHCS-0008 | loan | $3,200,000 | hard_pay | 2027-12-10 (RECORDED) |  | current | M. Okafor | recap_committee | ACT |
| St Anthony Village | L-OHCS-0007 | loan | $700,000 | hard_pay | 2030-12-31 (RECORDED) |  | default | J. Rivera | recap_committee | ACT |
| Powell Plaza I | L-OHCS-0002 | loan | $850,000 | hard_pay | 2035-01-01 (RECORDED) | 2035-01-01 | current | J. Rivera | optout_response | PLAN |
| Cathedral Gardens | L-OHCS-0004 | loan | $1,500,000 | residual_receipts | 2033-12-31 (RECORDED) |  | current | M. Okafor | qc_admin | PLAN |
| Village Garden Apartments | L-OHCS-0001 | loan;grant | $1,200,000 | residual_receipts | 2031-06-30 (RECORDED) | 2029-06-01 | current | J. Rivera | servicing_watch | PLAN |
| Fixture Badly Typed | L-OHCS-0010;L-OHCS-0011 | loan | $650,000 | residual_receipts | 2032-06-30 (RECORDED) | 2031-06-30 | current | A. Chen | servicing_watch | PLAN |
| Sumner Street Flats | L-OHCS-0014 | loan | $480,000 | deferred | 2039-06-30 (RECORDED) | 2029-06-30 | current | A. Chen | servicing_watch | PLAN |
| Hollow Oak Commons | L-OHCS-0013 | loan | $1,850,000 | residual_receipts | 2029-06-30 (RECORDED) |  | watch | J. Rivera | servicing_watch | WATCH |
| Fixture Authority Court (HACC) | L-OHCS-0009 | loan | $650,000 | deferred | 2031-03-04 (RECORDED) | 2031-03-04 | current | A. Chen | servicing_watch | WATCH |
| Town Center Courtyards | L-OHCS-0006 | loan | $900,000 | deferred | 2048-08-01 (RECORDED) | 2078-08-01 | current | A. Chen | ta_sponsor | WATCH |
| GOING 42 | L-OHCS-0005 | loan | $1,100,000 | deferred | 2058-09-08 (RECORDED) | 2058-09-08 | current | A. Chen | monitoring | WATCH |

Book rows not found in the inventory (servicing_unmatched.csv): 4 — Fixture Authority Court (HACC); Fixture Badly Typed; Hollow Oak Commons; Sumner Street Flats

## Preservation Queue (not in our book)

| property | jurisdiction | queue | score | route | owner cliff | units at risk | HAP | owner type | mandate_fit |
|---|---|---|---|---|---|---|---|---|---|
| STADIUM STATION | Portland | ACT | 52.5 | nofa_offer | LIHTC_EXTENDED_USE_END 2028-01-01 | 115 | 0 | nonprofit | eligible |
| Powell Plaza II | Portland | PLAN | 36.6 | optout_response | HAP_EXPIRATION 2027-03-31 | 20 | 20 | lihtc_partnership_nonprofit_gp | eligible |
| Mt Hood Community Apartments | Gresham | PLAN | 30.3 | optout_response | HAP_EXPIRATION 2027-09-30 | 15 | 14 | nonprofit | eligible |
| Gray's Landing | Portland | PLAN | 49.5 | nofa_offer | LIHTC_EXTENDED_USE_END 2029-01-01 | 209 | 0 | lihtc_partnership_nonprofit_gp | eligible |
| Bethany Meadows I | Portland | PLAN | 46.5 | nofa_offer | LIHTC_EXTENDED_USE_END 2027-01-01 | 208 | 0 | lihtc_partnership_forprofit_gp | eligible |
| Pier Park Apartments | Portland | PLAN | 46.5 | nofa_offer | LIHTC_EXTENDED_USE_END 2027-01-01 | 164 | 0 | lihtc_partnership_forprofit_gp | eligible |
| YARDS AT UNION STATION B | Portland | PLAN | 46.5 | nofa_offer | LIHTC_EXTENDED_USE_END 2029-01-01 | 321 | 0 | individual_owner_of_record | eligible |
| Berry Ridge Apartments | Gresham | PLAN | 46.5 | nofa_offer | LIHTC_EXTENDED_USE_END 2029-01-01 | 248 | 0 | lihtc_partnership_forprofit_gp | eligible |
| Hawthorne Villa Apartments | Tigard | PLAN | 46.5 | nofa_offer | LIHTC_EXTENDED_USE_END 2027-01-01 | 119 | 0 | lihtc_partnership_forprofit_gp | eligible |
| Linc245 (fka Village at Lovejoy Fountain) | Portland | PLAN | 46.5 | nofa_offer | LIHTC_EXTENDED_USE_END 2029-01-01 | 198 | 0 | lihtc_partnership_forprofit_gp | eligible |
| Terrace View Apartments | Tualatin | PLAN | 46.5 | nofa_offer | LIHTC_EXTENDED_USE_END 2028-01-01 | 100 | 0 | lihtc_partnership_forprofit_gp | eligible |
| Bethany Meadows II | Portland | PLAN | 46.5 | nofa_offer | LIHTC_EXTENDED_USE_END 2029-01-01 | 132 | 0 | lihtc_partnership_forprofit_gp | eligible |
| Belmont Dairy | Portland | PLAN | 42.0 | nofa_offer | LIHTC_EXTENDED_USE_END 2027-01-01 | 85 | 0 | lihtc_partnership_forprofit_gp | eligible |
| Floyd Light Apartments | Portland | PLAN | 42.0 | nofa_offer | LIHTC_EXTENDED_USE_END 2027-01-01 | 51 | 0 | lihtc_partnership_forprofit_gp | eligible |
| FIFTH AVENUE PLACE APTS | Portland | PLAN | 42.0 | nofa_offer | LIHTC_EXTENDED_USE_END 2029-01-01 | 70 | 0 | individual_owner_of_record | eligible |
| Esperanza Court | Portland | PLAN | 40.7 | nofa_offer | SOFT_PROGRAM_END 2029-04-09 | 70 | 0 | lihtc_partnership_nonprofit_gp | eligible |
| Buckman Heights | Portland | PLAN | 40.5 | nofa_offer | LIHTC_EXTENDED_USE_END 2028-01-01 | 144 | 0 | lihtc_partnership_forprofit_gp | eligible |
| Lincoln Woods | Portland | PLAN | 39.8 | nofa_offer | SOFT_PROGRAM_END 2027-11-19 | 70 | 0 | lihtc_partnership_nonprofit_gp | eligible |
| 333 Oak Apartments | Portland | PLAN | 39.1 | nofa_offer | HAP_EXPIRATION 2029-09-30 | 90 | 90 | lihtc_partnership_nonprofit_gp | eligible |
| Crestview Court | Beaverton | PLAN | 36.6 | nofa_offer | SOFT_PROGRAM_END 2028-03-14 | 48 | 48 | lihtc_partnership_nonprofit_gp | eligible |
| Creekside Woods | Wilsonville | PLAN | 36.4 | nofa_offer | HAP_EXPIRATION 2027-12-31 | 84 | 0 | lihtc_partnership_forprofit_gp | eligible |
| Upshur House | Portland | PLAN | 36.4 | nofa_offer | HAP_EXPIRATION 2030-04-30 | 30 | 30 | lihtc_partnership_nonprofit_gp | eligible |
| Roselyn Apartments | Portland | PLAN | 35.7 | nofa_offer | HAP_EXPIRATION 2029-05-25 | 31 | 31 | lihtc_partnership_nonprofit_gp | eligible |
| Country Squire Apts | Portland | PLAN | 35.4 | nofa_offer | SOFT_PROGRAM_END 2027-05-23 | 32 | 0 | nonprofit | eligible |
| Wiedemann Park Apartments | Wilsonville | PLAN | 34.8 | nofa_offer | LIHTC_EXTENDED_USE_END 2030-01-01 | 58 | 0 | housing_authority | eligible |
| Rosewood Terrace | Oregon City | PLAN | 34.6 | nofa_offer | SOFT_PROGRAM_END 2029-04-01 | 38 | 38 | housing_authority | eligible |
| 1200 BUILDING | Portland | PLAN | 34.0 | nofa_offer | SOFT_PROGRAM_END 2029-02-01 | 89 | 89 | unknown | eligible |
| Carriage Court | Canby | PLAN | 33.9 | nofa_offer | SOFT_PROGRAM_END 2029-10-01 | 30 | 30 | housing_authority | eligible |
| Broadway Vantage | Portland | PLAN | 33.8 | nofa_offer | SOFT_PROGRAM_END 2029-03-19 | 58 | 0 | lihtc_partnership_forprofit_gp | eligible |
| ELDERPLACE IN CULLY | Portland | PLAN | 33.6 | nofa_offer | SOFT_PROGRAM_END 2026-12-15 | 42 | 0 | nonprofit | eligible |
| Whispering Pines Senior Village | Estacada | PLAN | 33.4 | nofa_offer | HAP_EXPIRATION 2028-05-31 | 63 | 0 | nonprofit | eligible |
| New Columbia Haven 9 | Portland | PLAN | 33.4 | nofa_offer | SOFT_PROGRAM_END 2026-10-06 | 44 | 0 | housing_authority | eligible |
| Timber Grove Firwood Village | Sandy | PLAN | 33.4 | nofa_offer | SOFT_PROGRAM_END 2027-05-25 | 24 | 0 | lihtc_partnership_forprofit_gp | eligible |
| Tualatin Meadows | Tualatin | PLAN | 33.3 | nofa_offer | LIHTC_EXTENDED_USE_END 2030-09-01 | 240 | 0 | lihtc_partnership_forprofit_gp | eligible |
| Lake Crest Apartments | Milwaukie | PLAN | 33.3 | nofa_offer | LIHTC_EXTENDED_USE_END 2030-09-30 | 229 | 0 | lihtc_partnership_forprofit_gp | eligible |
| Briarcreek Apartments | Hillsboro | PLAN | 33.3 | nofa_offer | LIHTC_EXTENDED_USE_END 2030-01-01 | 216 | 0 | lihtc_partnership_forprofit_gp | eligible |
| Collins Circle | Portland | PLAN | 33.3 | nofa_offer | LIHTC_EXTENDED_USE_END 2030-01-01 | 124 | 0 | lihtc_partnership_forprofit_gp | eligible |
| Uptown Tower | Portland | PLAN | 33.3 | nofa_offer | SOFT_PROGRAM_END 2031-01-12 | 72 | 71 | individual_owner_of_record | eligible |
| MARY ANN, THE | Beaverton | PLAN | 33.0 | nofa_offer | SOFT_PROGRAM_END 2027-10-02 | 54 | 0 | nonprofit | eligible |
| Fifth Avenue Court | Portland | PLAN | 31.8 | nofa_offer | LIHTC_EXTENDED_USE_END 2030-06-15 | 96 | 0 | lihtc_partnership_forprofit_gp | eligible |
| Timber Grove Estacada Village | Estacada | PLAN | 31.6 | nofa_offer | SOFT_PROGRAM_END 2027-05-25 | 48 | 0 | lihtc_partnership_forprofit_gp | eligible |
| NEW COLUMBIA WOOLSEY II | Portland | PLAN | 31.6 | nofa_offer | SOFT_PROGRAM_END 2028-04-02 | 47 | 0 | housing_authority | eligible |
| Admiral Apartments | Portland | PLAN | 31.6 | nofa_offer | SOFT_PROGRAM_END 2031-01-27 | 37 | 37 | lihtc_partnership_nonprofit_gp | eligible |
| Westshore, The | Portland | PLAN | 31.5 | nofa_offer | SOFT_PROGRAM_END 2028-01-15 | 113 | 0 | lihtc_partnership_forprofit_gp | eligible |
| Farmington Meadows | Beaverton | PLAN | 31.5 | nofa_offer | SOFT_PROGRAM_END 2030-12-20 | 69 | 69 | regional_operator | eligible |
| Town Center Station | Happy Valley | PLAN | 31.5 | nofa_offer | SOFT_PROGRAM_END 2030-10-01 | 52 | 0 | lihtc_partnership_nonprofit_gp | eligible |
| Miracles Club | Portland | PLAN | 30.6 | nofa_offer | SOFT_PROGRAM_END 2027-06-01 | 40 | 0 | lihtc_partnership_forprofit_gp | eligible |
| Ridgecrest Timbers | Portland | PLAN | 30.6 | nofa_offer | LIHTC_EXTENDED_USE_END 2030-10-01 | 97 | 0 | lihtc_partnership_forprofit_gp | eligible |
| Garden Grove Apartments | Forest Grove | PLAN | 30.4 | nofa_offer | SOFT_PROGRAM_END 2028-12-01 | 48 | 48 | lihtc_partnership_forprofit_gp | eligible |
| Weidler Commons | Portland | PLAN | 30.0 | nofa_offer | SOFT_PROGRAM_END 2027-05-29 | 51 | 0 | lihtc_partnership_forprofit_gp | eligible |
| Eastgate Station | Portland | PLAN | 30.0 | nofa_offer | SOFT_PROGRAM_END 2031-02-17 | 61 | 0 | lihtc_partnership_forprofit_gp | eligible |

## Notice Compliance

| req_id | property | statute cite (verify) | window | due date | status | evidence | remediation ask |
|---|---|---|---|---|---|---|---|
| PUSH-01 | Yards at Union Station A | ORS 456.260(1); OAR 813-115-0030 (verify) | 2025-01-01..2025-07-01 | 2025-07-01 | due passed; confirm log | notice_status=unknown; window_state=closed_first_due |  |
| PUSH-02 | Yards at Union Station A | ORS 456.260(2); OAR 813-115-0030 (verify) | 2025-07-01..2026-01-01 | 2026-01-01 | confirm log | notice_status=unknown |  |
| PUSH-03 | Yards at Union Station A | SB 973 (2025); ORS 456.259 (verify operative date) | .. |  | n/a_pre_operative |  |  |
| PUSH-01 | Rose Schnitzer Tower | ORS 456.260(1); OAR 813-115-0030 (verify) | 2036-10-15..2037-04-15 | 2037-04-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Rose Schnitzer Tower | SB 973 (2025); ORS 456.259 (verify operative date) | 2036-10-15..2037-04-15 | 2037-04-15 | unknown |  | tenant_notice_check |
| HAP-01 | Rose Schnitzer Tower | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2026-12-10 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Rose Schnitzer Tower | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2027-08-12 | renewal_request_status=unknown |  |  |
| PUSH-01 | St Anthony Village | ORS 456.260(1); OAR 813-115-0030 (verify) | 2026-01-01..2026-07-01 | 2026-07-01 | due passed; confirm log | notice_status=unknown; window_state=closed_first_due |  |
| PUSH-02 | St Anthony Village | ORS 456.260(2); OAR 813-115-0030 (verify) | 2026-07-01..2027-01-01 | 2027-01-01 | confirm log | notice_status=unknown |  |
| PUSH-03 | St Anthony Village | SB 973 (2025); ORS 456.259 (verify operative date) | 2026-01-01..2026-07-01 | 2026-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | STADIUM STATION | ORS 456.260(1); OAR 813-115-0030 (verify) | 2025-01-01..2025-07-01 | 2025-07-01 | due passed; confirm log | notice_status=unknown; window_state=closed_first_due |  |
| PUSH-02 | STADIUM STATION | ORS 456.260(2); OAR 813-115-0030 (verify) | 2025-07-01..2026-01-01 | 2026-01-01 | confirm log | notice_status=unknown |  |
| PUSH-03 | STADIUM STATION | SB 973 (2025); ORS 456.259 (verify operative date) | .. |  | n/a_pre_operative |  |  |
| PUSH-01 | Powell Plaza I | ORS 456.260(1); OAR 813-115-0030 (verify) | 2032-01-01..2032-07-01 | 2032-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Powell Plaza I | SB 973 (2025); ORS 456.259 (verify operative date) | 2032-01-01..2032-07-01 | 2032-07-01 | unknown |  | tenant_notice_check |
| HAP-01 | Powell Plaza I | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2026-03-31 | renewal_request_status=unknown; deadline passed unconfirmed | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Powell Plaza I | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2026-12-01 | renewal_request_status=unknown |  |  |
| PUSH-01 | Cathedral Gardens | ORS 456.260(1); OAR 813-115-0030 (verify) | 2042-01-01..2042-07-01 | 2042-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Cathedral Gardens | SB 973 (2025); ORS 456.259 (verify operative date) | 2042-01-01..2042-07-01 | 2042-07-01 | unknown |  | tenant_notice_check |
| HAP-01 | Cathedral Gardens | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2032-12-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Cathedral Gardens | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2033-09-02 | renewal_request_status=unknown |  |  |
| PUSH-01 | Village Garden Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2026-06-01..2026-12-01 | 2026-12-01 | window open | notice_status=unknown; window_state=open_first |  |
| PUSH-03 | Village Garden Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2026-06-01..2026-12-01 | 2026-12-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Fixture Badly Typed | ORS 456.260(1); OAR 813-115-0030 (verify) | 2028-06-30..2028-12-30 | 2028-12-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Fixture Badly Typed | SB 973 (2025); ORS 456.259 (verify operative date) | 2028-06-30..2028-12-30 | 2028-12-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Sumner Street Flats | ORS 456.260(1); OAR 813-115-0030 (verify) | 2026-06-30..2026-12-30 | 2026-12-30 | window open | notice_status=unknown; window_state=open_first |  |
| PUSH-03 | Sumner Street Flats | SB 973 (2025); ORS 456.259 (verify operative date) | 2026-06-30..2026-12-30 | 2026-12-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Powell Plaza II | ORS 456.260(1); OAR 813-115-0030 (verify) | 2032-01-01..2032-07-01 | 2032-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Powell Plaza II | SB 973 (2025); ORS 456.259 (verify operative date) | 2032-01-01..2032-07-01 | 2032-07-01 | unknown |  | tenant_notice_check |
| HAP-01 | Powell Plaza II | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2026-03-31 | renewal_request_status=unknown; deadline passed unconfirmed | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Powell Plaza II | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2026-12-01 | renewal_request_status=unknown |  |  |
| PUSH-01 | Mt Hood Community Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2045-03-15..2045-09-15 | 2045-09-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Mt Hood Community Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2045-03-15..2045-09-15 | 2045-09-15 | unknown |  | tenant_notice_check |
| HAP-01 | Mt Hood Community Apartments | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2026-09-30 | renewal_request_status=unknown; deadline passed unconfirmed | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Mt Hood Community Apartments | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2027-06-02 | renewal_request_status=unknown |  |  |
| PUSH-01 | Gray's Landing | ORS 456.260(1); OAR 813-115-0030 (verify) | 2069-11-07..2070-05-07 | 2070-05-07 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Gray's Landing | SB 973 (2025); ORS 456.259 (verify operative date) | 2069-11-07..2070-05-07 | 2070-05-07 | unknown |  | tenant_notice_check |
| PUSH-01 | Bethany Meadows I | ORS 456.260(1); OAR 813-115-0030 (verify) | 2024-01-01..2024-07-01 | 2024-07-01 | due passed; confirm log | notice_status=unknown; window_state=closed_first_due |  |
| PUSH-02 | Bethany Meadows I | ORS 456.260(2); OAR 813-115-0030 (verify) | 2024-07-01..2025-01-01 | 2025-01-01 | confirm log | notice_status=unknown |  |
| PUSH-03 | Bethany Meadows I | SB 973 (2025); ORS 456.259 (verify operative date) | .. |  | n/a_pre_operative |  |  |
| PUSH-01 | Pier Park Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2024-01-01..2024-07-01 | 2024-07-01 | due passed; confirm log | notice_status=unknown; window_state=closed_first_due |  |
| PUSH-02 | Pier Park Apartments | ORS 456.260(2); OAR 813-115-0030 (verify) | 2024-07-01..2025-01-01 | 2025-01-01 | confirm log | notice_status=unknown |  |
| PUSH-03 | Pier Park Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | .. |  | n/a_pre_operative |  |  |
| PUSH-01 | YARDS AT UNION STATION B | ORS 456.260(1); OAR 813-115-0030 (verify) | 2026-01-01..2026-07-01 | 2026-07-01 | due passed; confirm log | notice_status=unknown; window_state=closed_first_due |  |
| PUSH-02 | YARDS AT UNION STATION B | ORS 456.260(2); OAR 813-115-0030 (verify) | 2026-07-01..2027-01-01 | 2027-01-01 | confirm log | notice_status=unknown |  |
| PUSH-03 | YARDS AT UNION STATION B | SB 973 (2025); ORS 456.259 (verify operative date) | 2026-01-01..2026-07-01 | 2026-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Berry Ridge Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2026-01-01..2026-07-01 | 2026-07-01 | due passed; confirm log | notice_status=unknown; window_state=closed_first_due |  |
| PUSH-02 | Berry Ridge Apartments | ORS 456.260(2); OAR 813-115-0030 (verify) | 2026-07-01..2027-01-01 | 2027-01-01 | confirm log | notice_status=unknown |  |
| PUSH-03 | Berry Ridge Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2026-01-01..2026-07-01 | 2026-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Hawthorne Villa Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2024-01-01..2024-07-01 | 2024-07-01 | due passed; confirm log | notice_status=unknown; window_state=closed_first_due |  |
| PUSH-02 | Hawthorne Villa Apartments | ORS 456.260(2); OAR 813-115-0030 (verify) | 2024-07-01..2025-01-01 | 2025-01-01 | confirm log | notice_status=unknown |  |
| PUSH-03 | Hawthorne Villa Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | .. |  | n/a_pre_operative |  |  |
| PUSH-01 | Linc245 (fka Village at Lovejoy Fountain) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2026-01-01..2026-07-01 | 2026-07-01 | due passed; confirm log | notice_status=unknown; window_state=closed_first_due |  |
| PUSH-02 | Linc245 (fka Village at Lovejoy Fountain) | ORS 456.260(2); OAR 813-115-0030 (verify) | 2026-07-01..2027-01-01 | 2027-01-01 | confirm log | notice_status=unknown |  |
| PUSH-03 | Linc245 (fka Village at Lovejoy Fountain) | SB 973 (2025); ORS 456.259 (verify operative date) | 2026-01-01..2026-07-01 | 2026-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Terrace View Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2025-01-01..2025-07-01 | 2025-07-01 | due passed; confirm log | notice_status=unknown; window_state=closed_first_due |  |
| PUSH-02 | Terrace View Apartments | ORS 456.260(2); OAR 813-115-0030 (verify) | 2025-07-01..2026-01-01 | 2026-01-01 | confirm log | notice_status=unknown |  |
| PUSH-03 | Terrace View Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | .. |  | n/a_pre_operative |  |  |
| PUSH-01 | Bethany Meadows II | ORS 456.260(1); OAR 813-115-0030 (verify) | 2026-01-01..2026-07-01 | 2026-07-01 | due passed; confirm log | notice_status=unknown; window_state=closed_first_due |  |
| PUSH-02 | Bethany Meadows II | ORS 456.260(2); OAR 813-115-0030 (verify) | 2026-07-01..2027-01-01 | 2027-01-01 | confirm log | notice_status=unknown |  |
| PUSH-03 | Bethany Meadows II | SB 973 (2025); ORS 456.259 (verify operative date) | 2026-01-01..2026-07-01 | 2026-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Belmont Dairy | ORS 456.260(1); OAR 813-115-0030 (verify) | 2024-01-01..2024-07-01 | 2024-07-01 | due passed; confirm log | notice_status=unknown; window_state=closed_first_due |  |
| PUSH-02 | Belmont Dairy | ORS 456.260(2); OAR 813-115-0030 (verify) | 2024-07-01..2025-01-01 | 2025-01-01 | confirm log | notice_status=unknown |  |
| PUSH-03 | Belmont Dairy | SB 973 (2025); ORS 456.259 (verify operative date) | .. |  | n/a_pre_operative |  |  |
| PUSH-01 | Floyd Light Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2024-01-01..2024-07-01 | 2024-07-01 | due passed; confirm log | notice_status=unknown; window_state=closed_first_due |  |
| PUSH-02 | Floyd Light Apartments | ORS 456.260(2); OAR 813-115-0030 (verify) | 2024-07-01..2025-01-01 | 2025-01-01 | confirm log | notice_status=unknown |  |
| PUSH-03 | Floyd Light Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | .. |  | n/a_pre_operative |  |  |
| PUSH-01 | FIFTH AVENUE PLACE APTS | ORS 456.260(1); OAR 813-115-0030 (verify) | 2026-01-01..2026-07-01 | 2026-07-01 | due passed; confirm log | notice_status=unknown; window_state=closed_first_due |  |
| PUSH-02 | FIFTH AVENUE PLACE APTS | ORS 456.260(2); OAR 813-115-0030 (verify) | 2026-07-01..2027-01-01 | 2027-01-01 | confirm log | notice_status=unknown |  |
| PUSH-03 | FIFTH AVENUE PLACE APTS | SB 973 (2025); ORS 456.259 (verify operative date) | 2026-01-01..2026-07-01 | 2026-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Esperanza Court | ORS 456.260(1); OAR 813-115-0030 (verify) | 2066-01-01..2066-07-01 | 2066-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Esperanza Court | SB 973 (2025); ORS 456.259 (verify operative date) | 2066-01-01..2066-07-01 | 2066-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Buckman Heights | ORS 456.260(1); OAR 813-115-0030 (verify) | 2031-04-15..2031-10-15 | 2031-10-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Buckman Heights | SB 973 (2025); ORS 456.259 (verify operative date) | 2031-04-15..2031-10-15 | 2031-10-15 | unknown |  | tenant_notice_check |
| PUSH-01 | Lincoln Woods | ORS 456.260(1); OAR 813-115-0030 (verify) | 2064-01-01..2064-07-01 | 2064-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Lincoln Woods | SB 973 (2025); ORS 456.259 (verify operative date) | 2064-01-01..2064-07-01 | 2064-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | 333 Oak Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2057-01-01..2057-07-01 | 2057-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | 333 Oak Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2057-01-01..2057-07-01 | 2057-07-01 | unknown |  | tenant_notice_check |
| HAP-01 | 333 Oak Apartments | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2028-09-30 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | 333 Oak Apartments | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2029-06-02 | renewal_request_status=unknown |  |  |
| PUSH-01 | Crestview Court | ORS 456.260(1); OAR 813-115-0030 (verify) | 2050-01-01..2050-07-01 | 2050-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Crestview Court | SB 973 (2025); ORS 456.259 (verify operative date) | 2050-01-01..2050-07-01 | 2050-07-01 | unknown |  | tenant_notice_check |
| HAP-01 | Crestview Court | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2031-02-28 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Crestview Court | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2031-11-01 | renewal_request_status=unknown |  |  |
| PUSH-01 | Creekside Woods | ORS 456.260(1); OAR 813-115-0030 (verify) | 2066-12-31..2067-06-30 | 2067-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Creekside Woods | SB 973 (2025); ORS 456.259 (verify operative date) | 2066-12-31..2067-06-30 | 2067-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Upshur House | ORS 456.260(1); OAR 813-115-0030 (verify) | 2069-05-01..2069-11-01 | 2069-11-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Upshur House | SB 973 (2025); ORS 456.259 (verify operative date) | 2069-05-01..2069-11-01 | 2069-11-01 | unknown |  | tenant_notice_check |
| HAP-01 | Upshur House | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2029-04-30 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Upshur House | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2029-12-31 | renewal_request_status=unknown |  |  |
| PUSH-01 | Roselyn Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2067-01-11..2067-07-11 | 2067-07-11 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Roselyn Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2067-01-11..2067-07-11 | 2067-07-11 | unknown |  | tenant_notice_check |
| HAP-01 | Roselyn Apartments | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2028-05-25 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Roselyn Apartments | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2029-01-25 | renewal_request_status=unknown |  |  |
| PUSH-01 | Country Squire Apts | ORS 456.260(1); OAR 813-115-0030 (verify) | 2024-05-23..2024-11-23 | 2024-11-23 | due passed; confirm log | notice_status=unknown; window_state=closed_first_due |  |
| PUSH-02 | Country Squire Apts | ORS 456.260(2); OAR 813-115-0030 (verify) | 2024-11-23..2025-05-23 | 2025-05-23 | confirm log | notice_status=unknown |  |
| PUSH-03 | Country Squire Apts | SB 973 (2025); ORS 456.259 (verify operative date) | .. |  | n/a_pre_operative |  |  |
| PUSH-01 | Wiedemann Park Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2027-01-01..2027-07-01 | 2027-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Wiedemann Park Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2027-01-01..2027-07-01 | 2027-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Rosewood Terrace | ORS 456.260(1); OAR 813-115-0030 (verify) | 2046-01-01..2046-07-01 | 2046-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Rosewood Terrace | SB 973 (2025); ORS 456.259 (verify operative date) | 2046-01-01..2046-07-01 | 2046-07-01 | unknown |  | tenant_notice_check |
| HAP-01 | Rosewood Terrace | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2037-05-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Rosewood Terrace | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2038-01-31 | renewal_request_status=unknown |  |  |
| PUSH-01 | 1200 BUILDING | ORS 456.260(1); OAR 813-115-0030 (verify) | 2072-01-01..2072-07-01 | 2072-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | 1200 BUILDING | SB 973 (2025); ORS 456.259 (verify operative date) | 2072-01-01..2072-07-01 | 2072-07-01 | unknown |  | tenant_notice_check |
| HAP-01 | 1200 BUILDING | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2031-08-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | 1200 BUILDING | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2032-05-03 | renewal_request_status=unknown |  |  |
| PUSH-01 | Carriage Court | ORS 456.260(1); OAR 813-115-0030 (verify) | 2037-05-15..2037-11-15 | 2037-11-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Carriage Court | SB 973 (2025); ORS 456.259 (verify operative date) | 2037-05-15..2037-11-15 | 2037-11-15 | unknown |  | tenant_notice_check |
| HAP-01 | Carriage Court | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2038-12-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Carriage Court | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2039-09-02 | renewal_request_status=unknown |  |  |
| PUSH-01 | Broadway Vantage | ORS 456.260(1); OAR 813-115-0030 (verify) | 2065-07-18..2066-01-18 | 2066-01-18 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Broadway Vantage | SB 973 (2025); ORS 456.259 (verify operative date) | 2065-07-18..2066-01-18 | 2066-01-18 | unknown |  | tenant_notice_check |
| PUSH-01 | ELDERPLACE IN CULLY | ORS 456.260(1); OAR 813-115-0030 (verify) | 2023-12-15..2024-06-15 | 2024-06-15 | due passed; confirm log | notice_status=unknown; window_state=closed_first_due |  |
| PUSH-02 | ELDERPLACE IN CULLY | ORS 456.260(2); OAR 813-115-0030 (verify) | 2024-06-15..2024-12-15 | 2024-12-15 | confirm log | notice_status=unknown |  |
| PUSH-03 | ELDERPLACE IN CULLY | SB 973 (2025); ORS 456.259 (verify operative date) | .. |  | n/a_pre_operative |  |  |
| PUSH-01 | Whispering Pines Senior Village | ORS 456.260(1); OAR 813-115-0030 (verify) | 2028-06-20..2028-12-20 | 2028-12-20 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Whispering Pines Senior Village | SB 973 (2025); ORS 456.259 (verify operative date) | 2028-06-20..2028-12-20 | 2028-12-20 | unknown |  | tenant_notice_check |
| PUSH-01 | New Columbia Haven 9 | ORS 456.260(1); OAR 813-115-0030 (verify) | 2043-01-01..2043-07-01 | 2043-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | New Columbia Haven 9 | SB 973 (2025); ORS 456.259 (verify operative date) | 2043-01-01..2043-07-01 | 2043-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Timber Grove Firwood Village | ORS 456.260(1); OAR 813-115-0030 (verify) | 2041-05-01..2041-11-01 | 2041-11-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Timber Grove Firwood Village | SB 973 (2025); ORS 456.259 (verify operative date) | 2041-05-01..2041-11-01 | 2041-11-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Tualatin Meadows | ORS 456.260(1); OAR 813-115-0030 (verify) | 2027-09-01..2028-03-01 | 2028-03-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Tualatin Meadows | SB 973 (2025); ORS 456.259 (verify operative date) | 2027-09-01..2028-03-01 | 2028-03-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Lake Crest Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2027-09-30..2028-03-30 | 2028-03-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Lake Crest Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2027-09-30..2028-03-30 | 2028-03-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Briarcreek Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2027-01-01..2027-07-01 | 2027-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Briarcreek Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2027-01-01..2027-07-01 | 2027-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Collins Circle | ORS 456.260(1); OAR 813-115-0030 (verify) | 2027-01-01..2027-07-01 | 2027-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Collins Circle | SB 973 (2025); ORS 456.259 (verify operative date) | 2027-01-01..2027-07-01 | 2027-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Uptown Tower | ORS 456.260(1); OAR 813-115-0030 (verify) | 2069-01-01..2069-07-01 | 2069-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Uptown Tower | SB 973 (2025); ORS 456.259 (verify operative date) | 2069-01-01..2069-07-01 | 2069-07-01 | unknown |  | tenant_notice_check |
| HAP-01 | Uptown Tower | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2032-07-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Uptown Tower | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2033-04-02 | renewal_request_status=unknown |  |  |
| PUSH-01 | MARY ANN, THE | ORS 456.260(1); OAR 813-115-0030 (verify) | 2064-10-15..2065-04-15 | 2065-04-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | MARY ANN, THE | SB 973 (2025); ORS 456.259 (verify operative date) | 2064-10-15..2065-04-15 | 2065-04-15 | unknown |  | tenant_notice_check |
| PUSH-01 | Fifth Avenue Court | ORS 456.260(1); OAR 813-115-0030 (verify) | 2027-06-15..2027-12-15 | 2027-12-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Fifth Avenue Court | SB 973 (2025); ORS 456.259 (verify operative date) | 2027-06-15..2027-12-15 | 2027-12-15 | unknown |  | tenant_notice_check |
| PUSH-01 | Timber Grove Estacada Village | ORS 456.260(1); OAR 813-115-0030 (verify) | 2041-05-01..2041-11-01 | 2041-11-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Timber Grove Estacada Village | SB 973 (2025); ORS 456.259 (verify operative date) | 2041-05-01..2041-11-01 | 2041-11-01 | unknown |  | tenant_notice_check |
| PUSH-01 | NEW COLUMBIA WOOLSEY II | ORS 456.260(1); OAR 813-115-0030 (verify) | 2043-01-01..2043-07-01 | 2043-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | NEW COLUMBIA WOOLSEY II | SB 973 (2025); ORS 456.259 (verify operative date) | 2043-01-01..2043-07-01 | 2043-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Admiral Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2068-01-01..2068-07-01 | 2068-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Admiral Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2068-01-01..2068-07-01 | 2068-07-01 | unknown |  | tenant_notice_check |
| HAP-01 | Admiral Apartments | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2043-09-30 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Admiral Apartments | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2044-06-02 | renewal_request_status=unknown |  |  |
| PUSH-01 | Westshore, The | ORS 456.260(1); OAR 813-115-0030 (verify) | 2033-01-01..2033-07-01 | 2033-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Westshore, The | SB 973 (2025); ORS 456.259 (verify operative date) | 2033-01-01..2033-07-01 | 2033-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Farmington Meadows | ORS 456.260(1); OAR 813-115-0030 (verify) | 2071-01-01..2071-07-01 | 2071-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Farmington Meadows | SB 973 (2025); ORS 456.259 (verify operative date) | 2071-01-01..2071-07-01 | 2071-07-01 | unknown |  | tenant_notice_check |
| HAP-01 | Farmington Meadows | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2031-10-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Farmington Meadows | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2032-07-03 | renewal_request_status=unknown |  |  |
| PUSH-01 | Town Center Station | ORS 456.260(1); OAR 813-115-0030 (verify) | 2066-04-14..2066-10-14 | 2066-10-14 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Town Center Station | SB 973 (2025); ORS 456.259 (verify operative date) | 2066-04-14..2066-10-14 | 2066-10-14 | unknown |  | tenant_notice_check |
| PUSH-01 | Miracles Club | ORS 456.260(1); OAR 813-115-0030 (verify) | 2070-01-01..2070-07-01 | 2070-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Miracles Club | SB 973 (2025); ORS 456.259 (verify operative date) | 2070-01-01..2070-07-01 | 2070-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Ridgecrest Timbers | ORS 456.260(1); OAR 813-115-0030 (verify) | 2033-04-15..2033-10-15 | 2033-10-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Ridgecrest Timbers | SB 973 (2025); ORS 456.259 (verify operative date) | 2033-04-15..2033-10-15 | 2033-10-15 | unknown |  | tenant_notice_check |
| PUSH-01 | Garden Grove Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2046-01-01..2046-07-01 | 2046-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Garden Grove Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2046-01-01..2046-07-01 | 2046-07-01 | unknown |  | tenant_notice_check |
| HAP-01 | Garden Grove Apartments | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2039-01-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Garden Grove Apartments | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2039-10-03 | renewal_request_status=unknown |  |  |
| PUSH-01 | Weidler Commons | ORS 456.260(1); OAR 813-115-0030 (verify) | 2063-01-04..2063-07-04 | 2063-07-04 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Weidler Commons | SB 973 (2025); ORS 456.259 (verify operative date) | 2063-01-04..2063-07-04 | 2063-07-04 | unknown |  | tenant_notice_check |
| PUSH-01 | Eastgate Station | ORS 456.260(1); OAR 813-115-0030 (verify) | 2067-01-01..2067-07-01 | 2067-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Eastgate Station | SB 973 (2025); ORS 456.259 (verify operative date) | 2067-01-01..2067-07-01 | 2067-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Fixture Authority Court (HACC) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2028-03-04..2028-09-04 | 2028-09-04 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Fixture Authority Court (HACC) | SB 973 (2025); ORS 456.259 (verify operative date) | 2028-03-04..2028-09-04 | 2028-09-04 | unknown |  | tenant_notice_check |
| PUSH-01 | Town Center Courtyards | ORS 456.260(1); OAR 813-115-0030 (verify) | 2075-08-01..2076-02-01 | 2076-02-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Town Center Courtyards | SB 973 (2025); ORS 456.259 (verify operative date) | 2075-08-01..2076-02-01 | 2076-02-01 | unknown |  | tenant_notice_check |
| PUSH-01 | GOING 42 | ORS 456.260(1); OAR 813-115-0030 (verify) | 2055-09-08..2056-03-08 | 2056-03-08 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | GOING 42 | SB 973 (2025); ORS 456.259 (verify operative date) | 2055-09-08..2056-03-08 | 2056-03-08 | unknown |  | tenant_notice_check |
| HAP-01 | ALBERTA STREET APTS | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2026-08-31 | renewal_request_status=unknown; deadline passed unconfirmed | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | ALBERTA STREET APTS | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2027-05-03 | renewal_request_status=unknown |  |  |
| HAP-01 | OUR APARTMENT | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2026-01-24 | renewal_request_status=unknown; deadline passed unconfirmed | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | OUR APARTMENT | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2026-09-26 | renewal_request_status=unknown |  |  |
| PUSH-01 | Alma Gardens | ORS 456.260(1); OAR 813-115-0030 (verify) | 2071-01-01..2071-07-01 | 2071-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Alma Gardens | SB 973 (2025); ORS 456.259 (verify operative date) | 2071-01-01..2071-07-01 | 2071-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | MLK-Wygant Housing | ORS 456.260(1); OAR 813-115-0030 (verify) | 2025-08-15..2026-02-15 | 2026-02-15 | due passed; confirm log | notice_status=unknown; window_state=closed_first_due |  |
| PUSH-02 | MLK-Wygant Housing | ORS 456.260(2); OAR 813-115-0030 (verify) | 2026-02-15..2026-08-15 | 2026-08-15 | confirm log | notice_status=unknown |  |
| PUSH-03 | MLK-Wygant Housing | SB 973 (2025); ORS 456.259 (verify operative date) | 2025-08-15..2026-02-15 | 2026-02-15 | unknown |  | tenant_notice_check |
| PUSH-01 | Maples II | ORS 456.260(1); OAR 813-115-0030 (verify) | 2069-06-01..2069-12-01 | 2069-12-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Maples II | SB 973 (2025); ORS 456.259 (verify operative date) | 2069-06-01..2069-12-01 | 2069-12-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Scott Crest Plaza | ORS 456.260(1); OAR 813-115-0030 (verify) | 2057-01-01..2057-07-01 | 2057-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Scott Crest Plaza | SB 973 (2025); ORS 456.259 (verify operative date) | 2057-01-01..2057-07-01 | 2057-07-01 | unknown |  | tenant_notice_check |
| HAP-01 | Scott Crest Plaza | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2027-12-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Scott Crest Plaza | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2028-09-02 | renewal_request_status=unknown |  |  |
| HAP-01 | MYERS COURT | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2029-09-30 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | MYERS COURT | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2030-06-02 | renewal_request_status=unknown |  |  |
| PUSH-01 | Fox Pointe Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2027-11-30..2028-05-30 | 2028-05-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Fox Pointe Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2027-11-30..2028-05-30 | 2028-05-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Greenbriar Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2031-10-15..2032-04-15 | 2032-04-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Greenbriar Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2031-10-15..2032-04-15 | 2032-04-15 | unknown |  | tenant_notice_check |
| HAP-01 | FOREST VILLA | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2029-09-30 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | FOREST VILLA | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2030-06-02 | renewal_request_status=unknown |  |  |
| PUSH-01 | Martin Luther King Manor | ORS 456.260(1); OAR 813-115-0030 (verify) | 2044-12-15..2045-06-15 | 2045-06-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Martin Luther King Manor | SB 973 (2025); ORS 456.259 (verify operative date) | 2044-12-15..2045-06-15 | 2045-06-15 | unknown |  | tenant_notice_check |
| HAP-01 | Martin Luther King Manor | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2028-06-30 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Martin Luther King Manor | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2029-03-02 | renewal_request_status=unknown |  |  |
| PUSH-01 | Vermont Springs | ORS 456.260(1); OAR 813-115-0030 (verify) | 2044-12-15..2045-06-15 | 2045-06-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Vermont Springs | SB 973 (2025); ORS 456.259 (verify operative date) | 2044-12-15..2045-06-15 | 2045-06-15 | unknown |  | tenant_notice_check |
| HAP-01 | Vermont Springs | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2028-08-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Vermont Springs | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2029-05-03 | renewal_request_status=unknown |  |  |
| PUSH-01 | Trenton Terrace | ORS 456.260(1); OAR 813-115-0030 (verify) | 2044-01-01..2044-07-01 | 2044-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Trenton Terrace | SB 973 (2025); ORS 456.259 (verify operative date) | 2044-01-01..2044-07-01 | 2044-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Patton Park Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2066-01-01..2066-07-01 | 2066-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Patton Park Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2066-01-01..2066-07-01 | 2066-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Leander Court | ORS 456.260(1); OAR 813-115-0030 (verify) | 2064-01-01..2064-07-01 | 2064-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Leander Court | SB 973 (2025); ORS 456.259 (verify operative date) | 2064-01-01..2064-07-01 | 2064-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Miraflores | ORS 456.260(1); OAR 813-115-0030 (verify) | 2066-01-01..2066-07-01 | 2066-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Miraflores | SB 973 (2025); ORS 456.259 (verify operative date) | 2066-01-01..2066-07-01 | 2066-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Lafayette Court Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2026-12-15..2027-06-15 | 2027-06-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Lafayette Court Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2026-12-15..2027-06-15 | 2027-06-15 | unknown |  | tenant_notice_check |
| PUSH-01 | WALNUT PARK | ORS 456.260(1); OAR 813-115-0030 (verify) | 2068-12-31..2069-06-30 | 2069-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | WALNUT PARK | SB 973 (2025); ORS 456.259 (verify operative date) | 2068-12-31..2069-06-30 | 2069-06-30 | unknown |  | tenant_notice_check |
| HAP-01 | WALNUT PARK | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2043-09-30 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | WALNUT PARK | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2044-06-02 | renewal_request_status=unknown |  |  |
| PUSH-01 | Gresham Recovery Center | ORS 456.260(1); OAR 813-115-0030 (verify) | 2024-02-15..2024-08-15 | 2024-08-15 | due passed; confirm log | notice_status=unknown; window_state=closed_first_due |  |
| PUSH-02 | Gresham Recovery Center | ORS 456.260(2); OAR 813-115-0030 (verify) | 2024-08-15..2025-02-15 | 2025-02-15 | confirm log | notice_status=unknown |  |
| PUSH-03 | Gresham Recovery Center | SB 973 (2025); ORS 456.259 (verify operative date) | .. |  | n/a_pre_operative |  |  |
| PUSH-01 | Clinton Street Apartments (aka Dual Diagnoisis) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2031-12-07..2032-06-07 | 2032-06-07 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Clinton Street Apartments (aka Dual Diagnoisis) | SB 973 (2025); ORS 456.259 (verify operative date) | 2031-12-07..2032-06-07 | 2032-06-07 | unknown |  | tenant_notice_check |
| PUSH-01 | Charleston Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2068-01-01..2068-07-01 | 2068-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Charleston Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2068-01-01..2068-07-01 | 2068-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | New Columbia Woolsey 1 | ORS 456.260(1); OAR 813-115-0030 (verify) | 2043-01-01..2043-07-01 | 2043-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | New Columbia Woolsey 1 | SB 973 (2025); ORS 456.259 (verify operative date) | 2043-01-01..2043-07-01 | 2043-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Clackamas Apartments NCGC 45 | ORS 456.260(1); OAR 813-115-0030 (verify) | 2027-12-15..2028-06-15 | 2028-06-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Clackamas Apartments NCGC 45 | SB 973 (2025); ORS 456.259 (verify operative date) | 2027-12-15..2028-06-15 | 2028-06-15 | unknown |  | tenant_notice_check |
| HAP-01 | PINES I | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2030-07-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | PINES I | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2031-04-02 | renewal_request_status=unknown |  |  |
| HAP-01 | EMILIE HOUSE | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2030-07-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | EMILIE HOUSE | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2031-04-02 | renewal_request_status=unknown |  |  |
| HAP-01 | FOREST MANOR I | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2029-03-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | FOREST MANOR I | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2029-12-01 | renewal_request_status=unknown |  |  |
| HAP-01 | ALOHA PROJECT | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2026-12-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | ALOHA PROJECT | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2027-09-02 | renewal_request_status=unknown |  |  |
| PUSH-01 | McCuller Crossing | ORS 456.260(1); OAR 813-115-0030 (verify) | 2060-01-01..2060-07-01 | 2060-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | McCuller Crossing | SB 973 (2025); ORS 456.259 (verify operative date) | 2060-01-01..2060-07-01 | 2060-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Reedville Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2034-07-22..2035-01-22 | 2035-01-22 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Reedville Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2034-07-22..2035-01-22 | 2035-01-22 | unknown |  | tenant_notice_check |
| HAP-01 | ALBINA PLAZA | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2028-05-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | ALBINA PLAZA | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2029-01-31 | renewal_request_status=unknown |  |  |
| HAP-01 | GOOD SHEPHERD I | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2028-01-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | GOOD SHEPHERD I | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2028-10-03 | renewal_request_status=unknown |  |  |
| HAP-01 | GOOD SHEPHERD II | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2028-01-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | GOOD SHEPHERD II | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2028-10-03 | renewal_request_status=unknown |  |  |
| HAP-01 | PINES II | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2030-07-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | PINES II | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2031-04-02 | renewal_request_status=unknown |  |  |
| PUSH-01 | Midland Commons | ORS 456.260(1); OAR 813-115-0030 (verify) | 2062-01-01..2062-07-01 | 2062-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Midland Commons | SB 973 (2025); ORS 456.259 (verify operative date) | 2062-01-01..2062-07-01 | 2062-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | FAULKNER PLACE | ORS 456.260(1); OAR 813-115-0030 (verify) | 2027-11-15..2028-05-15 | 2028-05-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | FAULKNER PLACE | SB 973 (2025); ORS 456.259 (verify operative date) | 2027-11-15..2028-05-15 | 2028-05-15 | unknown |  | tenant_notice_check |
| PUSH-01 | BARBARA ROBERTS | ORS 456.260(1); OAR 813-115-0030 (verify) | 2028-07-15..2029-01-15 | 2029-01-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | BARBARA ROBERTS | SB 973 (2025); ORS 456.259 (verify operative date) | 2028-07-15..2029-01-15 | 2029-01-15 | unknown |  | tenant_notice_check |
| HAP-01 | SMALLWOOD | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2029-08-23 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | SMALLWOOD | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2030-04-25 | renewal_request_status=unknown |  |  |
| HAP-01 | ME RE CENTER | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2030-07-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | ME RE CENTER | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2031-04-02 | renewal_request_status=unknown |  |  |
| HAP-01 | MCCARTHY PLACE | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2030-08-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | MCCARTHY PLACE | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2031-05-03 | renewal_request_status=unknown |  |  |
| HAP-01 | FOREST MANOR II | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2029-03-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | FOREST MANOR II | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2029-12-01 | renewal_request_status=unknown |  |  |
| PUSH-01 | FOREST GROVE BEEHIVE | ORS 456.260(1); OAR 813-115-0030 (verify) | 2027-12-15..2028-06-15 | 2028-06-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | FOREST GROVE BEEHIVE | SB 973 (2025); ORS 456.259 (verify operative date) | 2027-12-15..2028-06-15 | 2028-06-15 | unknown |  | tenant_notice_check |
| PUSH-01 | Studio Pointe Apts (fka Ellis Apts) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2027-12-31..2028-06-30 | 2028-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Studio Pointe Apts (fka Ellis Apts) | SB 973 (2025); ORS 456.259 (verify operative date) | 2027-12-31..2028-06-30 | 2028-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Enclave 54 | ORS 456.260(1); OAR 813-115-0030 (verify) | 2027-12-31..2028-06-30 | 2028-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Enclave 54 | SB 973 (2025); ORS 456.259 (verify operative date) | 2027-12-31..2028-06-30 | 2028-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | CSP Park Tower Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2072-01-15..2072-07-15 | 2072-07-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | CSP Park Tower Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2072-01-15..2072-07-15 | 2072-07-15 | unknown |  | tenant_notice_check |
| HAP-01 | CSP Park Tower Apartments | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2031-12-18 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | CSP Park Tower Apartments | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2032-08-20 | renewal_request_status=unknown |  |  |
| PUSH-01 | Ikoi So Terrace | ORS 456.260(1); OAR 813-115-0030 (verify) | 2072-07-01..2073-01-01 | 2073-01-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Ikoi So Terrace | SB 973 (2025); ORS 456.259 (verify operative date) | 2072-07-01..2073-01-01 | 2073-01-01 | unknown |  | tenant_notice_check |
| HAP-01 | Ikoi So Terrace | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2033-06-30 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Ikoi So Terrace | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2034-03-02 | renewal_request_status=unknown |  |  |
| PUSH-01 | Hollyfield Village | ORS 456.260(1); OAR 813-115-0030 (verify) | 2071-01-01..2071-07-01 | 2071-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Hollyfield Village | SB 973 (2025); ORS 456.259 (verify operative date) | 2071-01-01..2071-07-01 | 2071-07-01 | unknown |  | tenant_notice_check |
| HAP-01 | Hollyfield Village | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2032-02-28 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Hollyfield Village | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2032-10-31 | renewal_request_status=unknown |  |  |
| PUSH-01 | Hawthorne East | ORS 456.260(1); OAR 813-115-0030 (verify) | 2074-12-16..2075-06-16 | 2075-06-16 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Hawthorne East | SB 973 (2025); ORS 456.259 (verify operative date) | 2074-12-16..2075-06-16 | 2075-06-16 | unknown |  | tenant_notice_check |
| HAP-01 | Hawthorne East | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2035-01-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Hawthorne East | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2035-10-03 | renewal_request_status=unknown |  |  |
| PUSH-01 | Orchards at Orenco II, The | ORS 456.260(1); OAR 813-115-0030 (verify) | 2074-08-01..2075-02-01 | 2075-02-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Orchards at Orenco II, The | SB 973 (2025); ORS 456.259 (verify operative date) | 2074-08-01..2075-02-01 | 2075-02-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Bridge Meadows Beaverton | ORS 456.260(1); OAR 813-115-0030 (verify) | 2075-12-31..2076-06-30 | 2076-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Bridge Meadows Beaverton | SB 973 (2025); ORS 456.259 (verify operative date) | 2075-12-31..2076-06-30 | 2076-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Plaza Townhomes | ORS 456.260(1); OAR 813-115-0030 (verify) | 2044-12-31..2045-06-30 | 2045-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Plaza Townhomes | SB 973 (2025); ORS 456.259 (verify operative date) | 2044-12-31..2045-06-30 | 2045-06-30 | unknown |  | tenant_notice_check |
| HAP-01 | Plaza Townhomes | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2035-08-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Plaza Townhomes | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2036-05-03 | renewal_request_status=unknown |  |  |
| PUSH-01 | Bronaugh Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2073-07-01..2074-01-01 | 2074-01-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Bronaugh Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2073-07-01..2074-01-01 | 2074-01-01 | unknown |  | tenant_notice_check |
| HAP-01 | Bronaugh Apartments | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2034-04-30 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Bronaugh Apartments | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2034-12-31 | renewal_request_status=unknown |  |  |
| PUSH-01 | Gilman Court (aka Glisan Commons Phase II) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2072-11-01..2073-05-01 | 2073-05-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Gilman Court (aka Glisan Commons Phase II) | SB 973 (2025); ORS 456.259 (verify operative date) | 2072-11-01..2073-05-01 | 2073-05-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Rosewood Plaza | ORS 456.260(1); OAR 813-115-0030 (verify) | 2074-01-01..2074-07-01 | 2074-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Rosewood Plaza | SB 973 (2025); ORS 456.259 (verify operative date) | 2074-01-01..2074-07-01 | 2074-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Hill Park Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2075-06-01..2075-12-01 | 2075-12-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Hill Park Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2075-06-01..2075-12-01 | 2075-12-01 | unknown |  | tenant_notice_check |
| PUSH-01 | 85 Stories Group 1 | ORS 456.260(1); OAR 813-115-0030 (verify) | 2043-01-01..2043-07-01 | 2043-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | 85 Stories Group 1 | SB 973 (2025); ORS 456.259 (verify operative date) | 2043-01-01..2043-07-01 | 2043-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | 85 Stories - Group 2 (2 scattered sites) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2043-04-14..2043-10-14 | 2043-10-14 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | 85 Stories - Group 2 (2 scattered sites) | SB 973 (2025); ORS 456.259 (verify operative date) | 2043-04-14..2043-10-14 | 2043-10-14 | unknown |  | tenant_notice_check |
| PUSH-01 | CSP Lexington Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2072-01-15..2072-07-15 | 2072-07-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | CSP Lexington Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2072-01-15..2072-07-15 | 2072-07-15 | unknown |  | tenant_notice_check |
| HAP-01 | CSP Lexington Apartments | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2031-12-18 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | CSP Lexington Apartments | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2032-08-20 | renewal_request_status=unknown |  |  |
| PUSH-01 | Erickson Fritz Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2073-01-15..2073-07-15 | 2073-07-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Erickson Fritz Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2073-01-15..2073-07-15 | 2073-07-15 | unknown |  | tenant_notice_check |
| PUSH-01 | Magnolia, The (aka Eliot MLK Project) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2070-12-01..2071-06-01 | 2071-06-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Magnolia, The (aka Eliot MLK Project) | SB 973 (2025); ORS 456.259 (verify operative date) | 2070-12-01..2071-06-01 | 2071-06-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Macdonald West Apts | ORS 456.260(1); OAR 813-115-0030 (verify) | 2069-11-27..2070-05-27 | 2070-05-27 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Macdonald West Apts | SB 973 (2025); ORS 456.259 (verify operative date) | 2069-11-27..2070-05-27 | 2070-05-27 | unknown |  | tenant_notice_check |
| PUSH-01 | Glisan Commons | ORS 456.260(1); OAR 813-115-0030 (verify) | 2072-03-31..2072-09-30 | 2072-09-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Glisan Commons | SB 973 (2025); ORS 456.259 (verify operative date) | 2072-03-31..2072-09-30 | 2072-09-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Easton Ridge | ORS 456.260(1); OAR 813-115-0030 (verify) | 2041-01-01..2041-07-01 | 2041-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Easton Ridge | SB 973 (2025); ORS 456.259 (verify operative date) | 2041-01-01..2041-07-01 | 2041-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Stephens Creek Crossing North | ORS 456.260(1); OAR 813-115-0030 (verify) | 2071-04-01..2071-10-01 | 2071-10-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Stephens Creek Crossing North | SB 973 (2025); ORS 456.259 (verify operative date) | 2071-04-01..2071-10-01 | 2071-10-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Beech Street | ORS 456.260(1); OAR 813-115-0030 (verify) | 2072-01-01..2072-07-01 | 2072-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Beech Street | SB 973 (2025); ORS 456.259 (verify operative date) | 2072-01-01..2072-07-01 | 2072-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Fisher Ridge Apartments (fka Morton Road Apts) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2037-08-04..2038-02-04 | 2038-02-04 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Fisher Ridge Apartments (fka Morton Road Apts) | SB 973 (2025); ORS 456.259 (verify operative date) | 2037-08-04..2038-02-04 | 2038-02-04 | unknown |  | tenant_notice_check |
| PUSH-01 | Garlington Place | ORS 456.260(1); OAR 813-115-0030 (verify) | 2076-01-01..2076-07-01 | 2076-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Garlington Place | SB 973 (2025); ORS 456.259 (verify operative date) | 2076-01-01..2076-07-01 | 2076-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Candalaria Plaza | ORS 456.260(1); OAR 813-115-0030 (verify) | 2057-01-01..2057-07-01 | 2057-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Candalaria Plaza | SB 973 (2025); ORS 456.259 (verify operative date) | 2057-01-01..2057-07-01 | 2057-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Orchards of 82nd | ORS 456.260(1); OAR 813-115-0030 (verify) | 2077-04-01..2077-10-01 | 2077-10-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Orchards of 82nd | SB 973 (2025); ORS 456.259 (verify operative date) | 2077-04-01..2077-10-01 | 2077-10-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Centennial Place Apts | ORS 456.260(1); OAR 813-115-0030 (verify) | 2080-12-31..2081-06-30 | 2081-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Centennial Place Apts | SB 973 (2025); ORS 456.259 (verify operative date) | 2080-12-31..2081-06-30 | 2081-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Henry Building | ORS 456.260(1); OAR 813-115-0030 (verify) | 2048-12-31..2049-06-30 | 2049-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Henry Building | SB 973 (2025); ORS 456.259 (verify operative date) | 2048-12-31..2049-06-30 | 2049-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Chaucer Court Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2070-01-01..2070-07-01 | 2070-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Chaucer Court Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2070-01-01..2070-07-01 | 2070-07-01 | unknown |  | tenant_notice_check |
| HAP-01 | Chaucer Court Apartments | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2030-10-20 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Chaucer Court Apartments | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2031-06-22 | renewal_request_status=unknown |  |  |
| PUSH-01 | King + Parks Apts | ORS 456.260(1); OAR 813-115-0030 (verify) | 2078-12-31..2079-06-30 | 2079-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | King + Parks Apts | SB 973 (2025); ORS 456.259 (verify operative date) | 2078-12-31..2079-06-30 | 2079-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Red Rock Creek Commons | ORS 456.260(1); OAR 813-115-0030 (verify) | 2048-12-31..2049-06-30 | 2049-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Red Rock Creek Commons | SB 973 (2025); ORS 456.259 (verify operative date) | 2048-12-31..2049-06-30 | 2049-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Cornelius Place | ORS 456.260(1); OAR 813-115-0030 (verify) | 2076-12-31..2077-06-30 | 2077-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Cornelius Place | SB 973 (2025); ORS 456.259 (verify operative date) | 2076-12-31..2077-06-30 | 2077-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Orchards at Orenco III, The | ORS 456.260(1); OAR 813-115-0030 (verify) | 2075-12-31..2076-06-30 | 2076-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Orchards at Orenco III, The | SB 973 (2025); ORS 456.259 (verify operative date) | 2075-12-31..2076-06-30 | 2076-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Project Open Door | ORS 456.260(1); OAR 813-115-0030 (verify) | 2029-11-15..2030-05-15 | 2030-05-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Project Open Door | SB 973 (2025); ORS 456.259 (verify operative date) | 2029-11-15..2030-05-15 | 2030-05-15 | unknown |  | tenant_notice_check |
| PUSH-01 | Turning Point | ORS 456.260(1); OAR 813-115-0030 (verify) | 2030-02-05..2030-08-05 | 2030-08-05 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Turning Point | SB 973 (2025); ORS 456.259 (verify operative date) | 2030-02-05..2030-08-05 | 2030-08-05 | unknown |  | tenant_notice_check |
| PUSH-01 | Oregon City Terrace | ORS 456.260(1); OAR 813-115-0030 (verify) | 2078-12-31..2079-06-30 | 2079-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Oregon City Terrace | SB 973 (2025); ORS 456.259 (verify operative date) | 2078-12-31..2079-06-30 | 2079-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Acadia Gardens | ORS 456.260(1); OAR 813-115-0030 (verify) | 2049-03-29..2049-09-29 | 2049-09-29 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Acadia Gardens | SB 973 (2025); ORS 456.259 (verify operative date) | 2049-03-29..2049-09-29 | 2049-09-29 | unknown |  | tenant_notice_check |
| PUSH-01 | Cedar Park Gardens | ORS 456.260(1); OAR 813-115-0030 (verify) | 2039-06-01..2039-12-01 | 2039-12-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Cedar Park Gardens | SB 973 (2025); ORS 456.259 (verify operative date) | 2039-06-01..2039-12-01 | 2039-12-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Harvey Rice Heritage | ORS 456.260(1); OAR 813-115-0030 (verify) | 2081-12-31..2082-06-30 | 2082-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Harvey Rice Heritage | SB 973 (2025); ORS 456.259 (verify operative date) | 2081-12-31..2082-06-30 | 2082-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Wynne Watts Commons (fka Albertina Kerr Workforce and Inclusive Housing) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2050-03-30..2050-09-30 | 2050-09-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Wynne Watts Commons (fka Albertina Kerr Workforce and Inclusive Housing) | SB 973 (2025); ORS 456.259 (verify operative date) | 2050-03-30..2050-09-30 | 2050-09-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Stephens Creek Crossing South (Hillsdale Terrace) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2071-07-01..2072-01-01 | 2072-01-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Stephens Creek Crossing South (Hillsdale Terrace) | SB 973 (2025); ORS 456.259 (verify operative date) | 2071-07-01..2072-01-01 | 2072-01-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Harvey Rice Heritage | ORS 456.260(1); OAR 813-115-0030 (verify) | 2081-12-31..2082-06-30 | 2082-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Harvey Rice Heritage | SB 973 (2025); ORS 456.259 (verify operative date) | 2081-12-31..2082-06-30 | 2082-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Vibrant! | ORS 456.260(1); OAR 813-115-0030 (verify) | 2046-12-31..2047-06-30 | 2047-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Vibrant! | SB 973 (2025); ORS 456.259 (verify operative date) | 2046-12-31..2047-06-30 | 2047-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Greenview Terrace | ORS 456.260(1); OAR 813-115-0030 (verify) | 2071-01-01..2071-07-01 | 2071-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Greenview Terrace | SB 973 (2025); ORS 456.259 (verify operative date) | 2071-01-01..2071-07-01 | 2071-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Rockwood Building, The | ORS 456.260(1); OAR 813-115-0030 (verify) | 2070-01-01..2070-07-01 | 2070-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Rockwood Building, The | SB 973 (2025); ORS 456.259 (verify operative date) | 2070-01-01..2070-07-01 | 2070-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | 72 Foster | ORS 456.260(1); OAR 813-115-0030 (verify) | 2076-05-01..2076-11-01 | 2076-11-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | 72 Foster | SB 973 (2025); ORS 456.259 (verify operative date) | 2076-05-01..2076-11-01 | 2076-11-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Nawikka Court Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2044-12-15..2045-06-15 | 2045-06-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Nawikka Court Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2044-12-15..2045-06-15 | 2045-06-15 | unknown |  | tenant_notice_check |
| HAP-01 | Nawikka Court Apartments | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2032-04-30 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Nawikka Court Apartments | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2032-12-31 | renewal_request_status=unknown |  |  |
| PUSH-01 | Mamook Tokatee fka Going 42 | ORS 456.260(1); OAR 813-115-0030 (verify) | 2079-02-11..2079-08-11 | 2079-08-11 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Mamook Tokatee fka Going 42 | SB 973 (2025); ORS 456.259 (verify operative date) | 2079-02-11..2079-08-11 | 2079-08-11 | unknown |  | tenant_notice_check |
| PUSH-01 | 85 Stories Group 6 (9 Scattered Sites) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2047-12-31..2048-06-30 | 2048-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | 85 Stories Group 6 (9 Scattered Sites) | SB 973 (2025); ORS 456.259 (verify operative date) | 2047-12-31..2048-06-30 | 2048-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Gateway Hermiston Buri Building and Juniper Apartments (fka Gateway Workforce and Hermiston Housing) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2057-12-31..2058-06-30 | 2058-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Gateway Hermiston Buri Building and Juniper Apartments (fka Gateway Workforce and Hermiston Housing) | SB 973 (2025); ORS 456.259 (verify operative date) | 2057-12-31..2058-06-30 | 2058-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Argyle Gardens (fka LISAH) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2077-12-31..2078-06-30 | 2078-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Argyle Gardens (fka LISAH) | SB 973 (2025); ORS 456.259 (verify operative date) | 2077-12-31..2078-06-30 | 2078-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Rose, The | ORS 456.260(1); OAR 813-115-0030 (verify) | 2078-12-31..2079-06-30 | 2079-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Rose, The | SB 973 (2025); ORS 456.259 (verify operative date) | 2078-12-31..2079-06-30 | 2079-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Renaissance Commons fka REACH Argyle | ORS 456.260(1); OAR 813-115-0030 (verify) | 2051-12-31..2052-06-30 | 2052-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Renaissance Commons fka REACH Argyle | SB 973 (2025); ORS 456.259 (verify operative date) | 2051-12-31..2052-06-30 | 2052-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Knoll at Tigard, The | ORS 456.260(1); OAR 813-115-0030 (verify) | 2069-01-01..2069-07-01 | 2069-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Knoll at Tigard, The | SB 973 (2025); ORS 456.259 (verify operative date) | 2069-01-01..2069-07-01 | 2069-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Greenburg Oaks Apts fka Villa La Paz Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2081-12-31..2082-06-30 | 2082-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Greenburg Oaks Apts fka Villa La Paz Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2081-12-31..2082-06-30 | 2082-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Mary Ann, The | ORS 456.260(1); OAR 813-115-0030 (verify) | 2078-12-31..2079-06-30 | 2079-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Mary Ann, The | SB 973 (2025); ORS 456.259 (verify operative date) | 2078-12-31..2079-06-30 | 2079-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Spencer House | ORS 456.260(1); OAR 813-115-0030 (verify) | 2071-02-01..2071-08-01 | 2071-08-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Spencer House | SB 973 (2025); ORS 456.259 (verify operative date) | 2071-02-01..2071-08-01 | 2071-08-01 | unknown |  | tenant_notice_check |
| HAP-01 | Spencer House | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2031-07-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Spencer House | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2032-04-02 | renewal_request_status=unknown |  |  |
| PUSH-01 | Cedar Grove (Beaverton) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2077-12-31..2078-06-30 | 2078-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Cedar Grove (Beaverton) | SB 973 (2025); ORS 456.259 (verify operative date) | 2077-12-31..2078-06-30 | 2078-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | ORCHARDS AT ORENCO I | ORS 456.260(1); OAR 813-115-0030 (verify) | 2073-02-01..2073-08-01 | 2073-08-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | ORCHARDS AT ORENCO I | SB 973 (2025); ORS 456.259 (verify operative date) | 2073-02-01..2073-08-01 | 2073-08-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Tryon Mews Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2044-12-15..2045-06-15 | 2045-06-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Tryon Mews Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2044-12-15..2045-06-15 | 2045-06-15 | unknown |  | tenant_notice_check |
| PUSH-01 | Hillside Manor | ORS 456.260(1); OAR 813-115-0030 (verify) | 2079-12-31..2080-06-30 | 2080-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Hillside Manor | SB 973 (2025); ORS 456.259 (verify operative date) | 2079-12-31..2080-06-30 | 2080-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Oakridge Park | ORS 456.260(1); OAR 813-115-0030 (verify) | 2070-01-01..2070-07-01 | 2070-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Oakridge Park | SB 973 (2025); ORS 456.259 (verify operative date) | 2070-01-01..2070-07-01 | 2070-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Sandy Vista Phase I | ORS 456.260(1); OAR 813-115-0030 (verify) | 2058-11-20..2059-05-20 | 2059-05-20 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Sandy Vista Phase I | SB 973 (2025); ORS 456.259 (verify operative date) | 2058-11-20..2059-05-20 | 2059-05-20 | unknown |  | tenant_notice_check |
| PUSH-01 | Blackburn Building | ORS 456.260(1); OAR 813-115-0030 (verify) | 2076-09-01..2077-03-01 | 2077-03-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Blackburn Building | SB 973 (2025); ORS 456.259 (verify operative date) | 2076-09-01..2077-03-01 | 2077-03-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Pisgah Home Colony | ORS 456.260(1); OAR 813-115-0030 (verify) | 2028-10-23..2029-04-23 | 2029-04-23 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Pisgah Home Colony | SB 973 (2025); ORS 456.259 (verify operative date) | 2028-10-23..2029-04-23 | 2029-04-23 | unknown |  | tenant_notice_check |
| PUSH-01 | Hazel Heights | ORS 456.260(1); OAR 813-115-0030 (verify) | 2076-03-01..2076-09-01 | 2076-09-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Hazel Heights | SB 973 (2025); ORS 456.259 (verify operative date) | 2076-03-01..2076-09-01 | 2076-09-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Portsmouth Commons | ORS 456.260(1); OAR 813-115-0030 (verify) | 2032-01-01..2032-07-01 | 2032-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Portsmouth Commons | SB 973 (2025); ORS 456.259 (verify operative date) | 2032-01-01..2032-07-01 | 2032-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Irvington Village | ORS 456.260(1); OAR 813-115-0030 (verify) | 2029-01-01..2029-07-01 | 2029-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Irvington Village | SB 973 (2025); ORS 456.259 (verify operative date) | 2029-01-01..2029-07-01 | 2029-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Portsmouth Commons | ORS 456.260(1); OAR 813-115-0030 (verify) | 2080-12-31..2081-06-30 | 2081-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Portsmouth Commons | SB 973 (2025); ORS 456.259 (verify operative date) | 2080-12-31..2081-06-30 | 2081-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | St Francis Park Apts | ORS 456.260(1); OAR 813-115-0030 (verify) | 2044-09-01..2045-03-01 | 2045-03-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | St Francis Park Apts | SB 973 (2025); ORS 456.259 (verify operative date) | 2044-09-01..2045-03-01 | 2045-03-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Charlotte B Rutherford Place | ORS 456.260(1); OAR 813-115-0030 (verify) | 2076-12-31..2077-06-30 | 2077-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Charlotte B Rutherford Place | SB 973 (2025); ORS 456.259 (verify operative date) | 2076-12-31..2077-06-30 | 2077-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Magnolia Apartments Phase II | ORS 456.260(1); OAR 813-115-0030 (verify) | 2060-11-15..2061-05-15 | 2061-05-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Magnolia Apartments Phase II | SB 973 (2025); ORS 456.259 (verify operative date) | 2060-11-15..2061-05-15 | 2061-05-15 | unknown |  | tenant_notice_check |
| PUSH-01 | Louisa Flowers, The (fka NE Grand) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2048-12-31..2049-06-30 | 2049-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Louisa Flowers, The (fka NE Grand) | SB 973 (2025); ORS 456.259 (verify operative date) | 2048-12-31..2049-06-30 | 2049-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Hopewell Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2031-12-23..2032-06-23 | 2032-06-23 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Hopewell Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2031-12-23..2032-06-23 | 2032-06-23 | unknown |  | tenant_notice_check |
| PUSH-01 | Vera, The | ORS 456.260(1); OAR 813-115-0030 (verify) | 2077-04-01..2077-10-01 | 2077-10-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Vera, The | SB 973 (2025); ORS 456.259 (verify operative date) | 2077-04-01..2077-10-01 | 2077-10-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Beatrice Morrow, The | ORS 456.260(1); OAR 813-115-0030 (verify) | 2076-08-01..2077-02-01 | 2077-02-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Beatrice Morrow, The | SB 973 (2025); ORS 456.259 (verify operative date) | 2076-08-01..2077-02-01 | 2077-02-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Dresden Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2030-03-24..2030-09-24 | 2030-09-24 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Dresden Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2030-03-24..2030-09-24 | 2030-09-24 | unknown |  | tenant_notice_check |
| PUSH-01 | 85 Stories Group 5 (7 Scattered Sites) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2047-12-31..2048-06-30 | 2048-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | 85 Stories Group 5 (7 Scattered Sites) | SB 973 (2025); ORS 456.259 (verify operative date) | 2047-12-31..2048-06-30 | 2048-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | KEARNEY HOUSE | ORS 456.260(1); OAR 813-115-0030 (verify) | 2033-01-01..2033-07-01 | 2033-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | KEARNEY HOUSE | SB 973 (2025); ORS 456.259 (verify operative date) | 2033-01-01..2033-07-01 | 2033-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | HELENS VIEW | ORS 456.260(1); OAR 813-115-0030 (verify) | 2030-07-31..2031-01-31 | 2031-01-31 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | HELENS VIEW | SB 973 (2025); ORS 456.259 (verify operative date) | 2030-07-31..2031-01-31 | 2031-01-31 | unknown |  | tenant_notice_check |
| PUSH-01 | Gladstone Square - Multnomah Manor | ORS 456.260(1); OAR 813-115-0030 (verify) | 2055-01-01..2055-07-01 | 2055-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Gladstone Square - Multnomah Manor | SB 973 (2025); ORS 456.259 (verify operative date) | 2055-01-01..2055-07-01 | 2055-07-01 | unknown |  | tenant_notice_check |
| HAP-01 | Gladstone Square - Multnomah Manor | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2031-09-30 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Gladstone Square - Multnomah Manor | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2032-06-02 | renewal_request_status=unknown |  |  |
| PUSH-01 | Stewart Terrace | ORS 456.260(1); OAR 813-115-0030 (verify) | 2060-01-01..2060-07-01 | 2060-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Stewart Terrace | SB 973 (2025); ORS 456.259 (verify operative date) | 2060-01-01..2060-07-01 | 2060-07-01 | unknown |  | tenant_notice_check |
| HAP-01 | Stewart Terrace | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2032-03-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Stewart Terrace | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2032-12-01 | renewal_request_status=unknown |  |  |
| HAP-01 | METZGER PARK | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2033-07-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | METZGER PARK | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2034-04-02 | renewal_request_status=unknown |  |  |
| PUSH-01 | Willows, The | ORS 456.260(1); OAR 813-115-0030 (verify) | 2030-09-30..2031-03-30 | 2031-03-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Willows, The | SB 973 (2025); ORS 456.259 (verify operative date) | 2030-09-30..2031-03-30 | 2031-03-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Pacific Park Apartments Canby West | ORS 456.260(1); OAR 813-115-0030 (verify) | 2073-12-31..2074-06-30 | 2074-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Pacific Park Apartments Canby West | SB 973 (2025); ORS 456.259 (verify operative date) | 2073-12-31..2074-06-30 | 2074-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Greens at Ridings, The | ORS 456.260(1); OAR 813-115-0030 (verify) | 2076-03-01..2076-09-01 | 2076-09-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Greens at Ridings, The | SB 973 (2025); ORS 456.259 (verify operative date) | 2076-03-01..2076-09-01 | 2076-09-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Wy'East Plaza | ORS 456.260(1); OAR 813-115-0030 (verify) | 2048-12-31..2049-06-30 | 2049-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Wy'East Plaza | SB 973 (2025); ORS 456.259 (verify operative date) | 2048-12-31..2049-06-30 | 2049-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Station 162 | ORS 456.260(1); OAR 813-115-0030 (verify) | 2074-12-31..2075-06-30 | 2075-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Station 162 | SB 973 (2025); ORS 456.259 (verify operative date) | 2074-12-31..2075-06-30 | 2075-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | L Roy Gardens | ORS 456.260(1); OAR 813-115-0030 (verify) | 2044-03-10..2044-09-10 | 2044-09-10 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | L Roy Gardens | SB 973 (2025); ORS 456.259 (verify operative date) | 2044-03-10..2044-09-10 | 2044-09-10 | unknown |  | tenant_notice_check |
| PUSH-01 | Rockwood Village (fka Rockwood 10) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2049-12-31..2050-06-30 | 2050-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Rockwood Village (fka Rockwood 10) | SB 973 (2025); ORS 456.259 (verify operative date) | 2049-12-31..2050-06-30 | 2050-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | GARDEN PROJECT - A PHILLIPS SQUARE | ORS 456.260(1); OAR 813-115-0030 (verify) | 2044-03-10..2044-09-10 | 2044-09-10 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | GARDEN PROJECT - A PHILLIPS SQUARE | SB 973 (2025); ORS 456.259 (verify operative date) | 2044-03-10..2044-09-10 | 2044-09-10 | unknown |  | tenant_notice_check |
| PUSH-01 | Fields Apts, The | ORS 456.260(1); OAR 813-115-0030 (verify) | 2047-10-15..2048-04-15 | 2048-04-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Fields Apts, The | SB 973 (2025); ORS 456.259 (verify operative date) | 2047-10-15..2048-04-15 | 2048-04-15 | unknown |  | tenant_notice_check |
| PUSH-01 | Willow Creek Crossing Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2047-12-31..2048-06-30 | 2048-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Willow Creek Crossing Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2047-12-31..2048-06-30 | 2048-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Tenino Terrace | ORS 456.260(1); OAR 813-115-0030 (verify) | 2032-01-01..2032-07-01 | 2032-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Tenino Terrace | SB 973 (2025); ORS 456.259 (verify operative date) | 2032-01-01..2032-07-01 | 2032-07-01 | unknown |  | tenant_notice_check |
| HAP-01 | Tenino Terrace | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2033-04-30 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Tenino Terrace | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2033-12-31 | renewal_request_status=unknown |  |  |
| PUSH-01 | Walsh Commons | ORS 456.260(1); OAR 813-115-0030 (verify) | 2076-12-31..2077-06-30 | 2077-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Walsh Commons | SB 973 (2025); ORS 456.259 (verify operative date) | 2076-12-31..2077-06-30 | 2077-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Willamalane | ORS 456.260(1); OAR 813-115-0030 (verify) | 2033-01-01..2033-07-01 | 2033-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Willamalane | SB 973 (2025); ORS 456.259 (verify operative date) | 2033-01-01..2033-07-01 | 2033-07-01 | unknown |  | tenant_notice_check |
| HAP-01 | Willamalane | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2041-03-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Willamalane | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2041-12-01 | renewal_request_status=unknown |  |  |
| PUSH-01 | SENECA TERRACE | ORS 456.260(1); OAR 813-115-0030 (verify) | 2068-01-01..2068-07-01 | 2068-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | SENECA TERRACE | SB 973 (2025); ORS 456.259 (verify operative date) | 2068-01-01..2068-07-01 | 2068-07-01 | unknown |  | tenant_notice_check |
| HAP-01 | SENECA TERRACE | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2038-02-28 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | SENECA TERRACE | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2038-10-31 | renewal_request_status=unknown |  |  |
| PUSH-01 | Pioneer Enterprises | ORS 456.260(1); OAR 813-115-0030 (verify) | 2078-12-31..2079-06-30 | 2079-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Pioneer Enterprises | SB 973 (2025); ORS 456.259 (verify operative date) | 2078-12-31..2079-06-30 | 2079-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Sitka Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2033-01-01..2033-07-01 | 2033-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Sitka Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2033-01-01..2033-07-01 | 2033-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Garden Park Estates | ORS 456.260(1); OAR 813-115-0030 (verify) | 2030-01-01..2030-07-01 | 2030-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Garden Park Estates | SB 973 (2025); ORS 456.259 (verify operative date) | 2030-01-01..2030-07-01 | 2030-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Cedar Commons (fka Division Street Apartments) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2049-12-31..2050-06-30 | 2050-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Cedar Commons (fka Division Street Apartments) | SB 973 (2025); ORS 456.259 (verify operative date) | 2049-12-31..2050-06-30 | 2050-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Fairview Arms | ORS 456.260(1); OAR 813-115-0030 (verify) | 2075-12-31..2076-06-30 | 2076-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Fairview Arms | SB 973 (2025); ORS 456.259 (verify operative date) | 2075-12-31..2076-06-30 | 2076-06-30 | unknown |  | tenant_notice_check |
| HAP-01 | Fairview Arms | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2036-11-30 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Fairview Arms | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2037-08-02 | renewal_request_status=unknown |  |  |
| PUSH-01 | Nick Fish, The (AKA Halsey 106) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2048-12-31..2049-06-30 | 2049-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Nick Fish, The (AKA Halsey 106) | SB 973 (2025); ORS 456.259 (verify operative date) | 2048-12-31..2049-06-30 | 2049-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Gateway Park Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2030-11-15..2031-05-15 | 2031-05-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Gateway Park Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2030-11-15..2031-05-15 | 2031-05-15 | unknown |  | tenant_notice_check |
| PUSH-01 | East Fair Terrace | ORS 456.260(1); OAR 813-115-0030 (verify) | 2031-03-19..2031-09-19 | 2031-09-19 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | East Fair Terrace | SB 973 (2025); ORS 456.259 (verify operative date) | 2031-03-19..2031-09-19 | 2031-09-19 | unknown |  | tenant_notice_check |
| HAP-01 | East Fair Terrace | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2036-03-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | East Fair Terrace | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2036-12-01 | renewal_request_status=unknown |  |  |
| PUSH-01 | Amanda Court | ORS 456.260(1); OAR 813-115-0030 (verify) | 2050-12-31..2051-06-30 | 2051-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Amanda Court | SB 973 (2025); ORS 456.259 (verify operative date) | 2050-12-31..2051-06-30 | 2051-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Gresham Station Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2034-01-01..2034-07-01 | 2034-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Gresham Station Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2034-01-01..2034-07-01 | 2034-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Abigail, The | ORS 456.260(1); OAR 813-115-0030 (verify) | 2073-10-01..2074-04-01 | 2074-04-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Abigail, The | SB 973 (2025); ORS 456.259 (verify operative date) | 2073-10-01..2074-04-01 | 2074-04-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Spruce Park Apartments (fka Springtree Apartments) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2079-12-31..2080-06-30 | 2080-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Spruce Park Apartments (fka Springtree Apartments) | SB 973 (2025); ORS 456.259 (verify operative date) | 2079-12-31..2080-06-30 | 2080-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | TILLICUM COURT | ORS 456.260(1); OAR 813-115-0030 (verify) | 2044-12-15..2045-06-15 | 2045-06-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | TILLICUM COURT | SB 973 (2025); ORS 456.259 (verify operative date) | 2044-12-15..2045-06-15 | 2045-06-15 | unknown |  | tenant_notice_check |
| HAP-01 | TILLICUM COURT | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2034-01-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | TILLICUM COURT | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2034-10-03 | renewal_request_status=unknown |  |  |
| PUSH-01 | Westmorelands Union Manor | ORS 456.260(1); OAR 813-115-0030 (verify) | 2074-06-01..2074-12-01 | 2074-12-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Westmorelands Union Manor | SB 973 (2025); ORS 456.259 (verify operative date) | 2074-06-01..2074-12-01 | 2074-12-01 | unknown |  | tenant_notice_check |
| HAP-01 | Westmorelands Union Manor | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2034-05-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Westmorelands Union Manor | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2035-01-31 | renewal_request_status=unknown |  |  |
| PUSH-01 | Milepost 5 | ORS 456.260(1); OAR 813-115-0030 (verify) | 2048-12-31..2049-06-30 | 2049-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Milepost 5 | SB 973 (2025); ORS 456.259 (verify operative date) | 2048-12-31..2049-06-30 | 2049-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Nesika Illahee (fka Holman 42) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2077-12-31..2078-06-30 | 2078-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Nesika Illahee (fka Holman 42) | SB 973 (2025); ORS 456.259 (verify operative date) | 2077-12-31..2078-06-30 | 2078-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Woodland Park Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2075-01-01..2075-07-01 | 2075-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Woodland Park Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2075-01-01..2075-07-01 | 2075-07-01 | unknown |  | tenant_notice_check |
| HAP-01 | Woodland Park Apartments | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2034-09-30 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Woodland Park Apartments | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2035-06-02 | renewal_request_status=unknown |  |  |
| PUSH-01 | Pacific Park Apartments Sherwood Park | ORS 456.260(1); OAR 813-115-0030 (verify) | 2073-12-31..2074-06-30 | 2074-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Pacific Park Apartments Sherwood Park | SB 973 (2025); ORS 456.259 (verify operative date) | 2073-12-31..2074-06-30 | 2074-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Autumn Park Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2061-09-17..2062-03-17 | 2062-03-17 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Autumn Park Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2061-09-17..2062-03-17 | 2062-03-17 | unknown |  | tenant_notice_check |
| PUSH-01 | Canby Village | ORS 456.260(1); OAR 813-115-0030 (verify) | 2032-01-01..2032-07-01 | 2032-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Canby Village | SB 973 (2025); ORS 456.259 (verify operative date) | 2032-01-01..2032-07-01 | 2032-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | PRINCETON VILLAGE | ORS 456.260(1); OAR 813-115-0030 (verify) | 2033-01-15..2033-07-15 | 2033-07-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | PRINCETON VILLAGE | SB 973 (2025); ORS 456.259 (verify operative date) | 2033-01-15..2033-07-15 | 2033-07-15 | unknown |  | tenant_notice_check |
| PUSH-01 | River Glen Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2043-04-03..2043-10-03 | 2043-10-03 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | River Glen Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2043-04-03..2043-10-03 | 2043-10-03 | unknown |  | tenant_notice_check |
| HAP-01 | River Glen Apartments | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2033-04-30 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | River Glen Apartments | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2033-12-31 | renewal_request_status=unknown |  |  |
| PUSH-01 | Rosewood Station | ORS 456.260(1); OAR 813-115-0030 (verify) | 2048-12-31..2049-06-30 | 2049-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Rosewood Station | SB 973 (2025); ORS 456.259 (verify operative date) | 2048-12-31..2049-06-30 | 2049-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Station Place Tower | ORS 456.260(1); OAR 813-115-0030 (verify) | 2061-01-01..2061-07-01 | 2061-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Station Place Tower | SB 973 (2025); ORS 456.259 (verify operative date) | 2061-01-01..2061-07-01 | 2061-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Albina Corner | ORS 456.260(1); OAR 813-115-0030 (verify) | 2033-01-01..2033-07-01 | 2033-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Albina Corner | SB 973 (2025); ORS 456.259 (verify operative date) | 2033-01-01..2033-07-01 | 2033-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Twelfth Avenue Terrace | ORS 456.260(1); OAR 813-115-0030 (verify) | 2051-01-01..2051-07-01 | 2051-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Twelfth Avenue Terrace | SB 973 (2025); ORS 456.259 (verify operative date) | 2051-01-01..2051-07-01 | 2051-07-01 | unknown |  | tenant_notice_check |
| HAP-01 | KIRKLAND UNION MANOR I | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2034-02-28 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | KIRKLAND UNION MANOR I | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2034-10-31 | renewal_request_status=unknown |  |  |
| HAP-01 | BEACON MANOR | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2031-08-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | BEACON MANOR | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2032-05-03 | renewal_request_status=unknown |  |  |
| HAP-01 | WESTMORELANDS UNION MANOR II | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2034-05-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | WESTMORELANDS UNION MANOR II | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2035-01-31 | renewal_request_status=unknown |  |  |
| HAP-01 | UNTHANK PLAZA | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2033-02-28 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | UNTHANK PLAZA | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2033-10-31 | renewal_request_status=unknown |  |  |
| HAP-01 | KENILWORTH PARK PLAZA | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2034-10-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | KENILWORTH PARK PLAZA | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2035-07-03 | renewal_request_status=unknown |  |  |
| HAP-01 | ROSENBAUM PLAZA | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2033-01-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | ROSENBAUM PLAZA | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2033-10-03 | renewal_request_status=unknown |  |  |
| PUSH-01 | Oliver Station | ORS 456.260(1); OAR 813-115-0030 (verify) | 2045-09-12..2046-03-12 | 2046-03-12 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Oliver Station | SB 973 (2025); ORS 456.259 (verify operative date) | 2045-09-12..2046-03-12 | 2046-03-12 | unknown |  | tenant_notice_check |
| PUSH-01 | LAURELHURST ASSISTED LIVING FACILITY | ORS 456.260(1); OAR 813-115-0030 (verify) | 2033-05-15..2033-11-15 | 2033-11-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | LAURELHURST ASSISTED LIVING FACILITY | SB 973 (2025); ORS 456.259 (verify operative date) | 2033-05-15..2033-11-15 | 2033-11-15 | unknown |  | tenant_notice_check |
| HAP-01 | EMERSON PLAZA | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2032-05-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | EMERSON PLAZA | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2033-01-31 | renewal_request_status=unknown |  |  |
| HAP-01 | AVENUE PLAZA | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2032-06-30 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | AVENUE PLAZA | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2033-03-02 | renewal_request_status=unknown |  |  |
| PUSH-01 | Wood Ridge Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2045-11-15..2046-05-15 | 2046-05-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Wood Ridge Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2045-11-15..2046-05-15 | 2046-05-15 | unknown |  | tenant_notice_check |
| PUSH-01 | Sunset View Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2046-12-31..2047-06-30 | 2047-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Sunset View Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2046-12-31..2047-06-30 | 2047-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Barcelona at Beaverton, The | ORS 456.260(1); OAR 813-115-0030 (verify) | 2072-12-31..2073-06-30 | 2073-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Barcelona at Beaverton, The | SB 973 (2025); ORS 456.259 (verify operative date) | 2072-12-31..2073-06-30 | 2073-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Gateway Commons Apts | ORS 456.260(1); OAR 813-115-0030 (verify) | 2031-01-01..2031-07-01 | 2031-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Gateway Commons Apts | SB 973 (2025); ORS 456.259 (verify operative date) | 2031-01-01..2031-07-01 | 2031-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Wyndhaven Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2036-01-01..2036-07-01 | 2036-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Wyndhaven Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2036-01-01..2036-07-01 | 2036-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | GATEWAY COMMONS | ORS 456.260(1); OAR 813-115-0030 (verify) | 2031-01-01..2031-07-01 | 2031-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | GATEWAY COMMONS | SB 973 (2025); ORS 456.259 (verify operative date) | 2031-01-01..2031-07-01 | 2031-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Jeffrey Apartments, The | ORS 456.260(1); OAR 813-115-0030 (verify) | 2065-06-17..2065-12-17 | 2065-12-17 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Jeffrey Apartments, The | SB 973 (2025); ORS 456.259 (verify operative date) | 2065-06-17..2065-12-17 | 2065-12-17 | unknown |  | tenant_notice_check |
| PUSH-01 | Rockwood Landing | ORS 456.260(1); OAR 813-115-0030 (verify) | 2057-01-01..2057-07-01 | 2057-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Rockwood Landing | SB 973 (2025); ORS 456.259 (verify operative date) | 2057-01-01..2057-07-01 | 2057-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Helen Ann Swindells Bldg | ORS 456.260(1); OAR 813-115-0030 (verify) | 2050-11-02..2051-05-02 | 2051-05-02 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Helen Ann Swindells Bldg | SB 973 (2025); ORS 456.259 (verify operative date) | 2050-11-02..2051-05-02 | 2051-05-02 | unknown |  | tenant_notice_check |
| PUSH-01 | James Hawthorne (fka University Place) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2066-04-10..2066-10-10 | 2066-10-10 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | James Hawthorne (fka University Place) | SB 973 (2025); ORS 456.259 (verify operative date) | 2066-04-10..2066-10-10 | 2066-10-10 | unknown |  | tenant_notice_check |
| PUSH-01 | Aldercrest Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2080-12-31..2081-06-30 | 2081-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Aldercrest Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2080-12-31..2081-06-30 | 2081-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Patton Home | ORS 456.260(1); OAR 813-115-0030 (verify) | 2058-01-01..2058-07-01 | 2058-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Patton Home | SB 973 (2025); ORS 456.259 (verify operative date) | 2058-01-01..2058-07-01 | 2058-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Las Adelitas | ORS 456.260(1); OAR 813-115-0030 (verify) | 2050-12-31..2051-06-30 | 2051-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Las Adelitas | SB 973 (2025); ORS 456.259 (verify operative date) | 2050-12-31..2051-06-30 | 2051-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Montebello Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2047-12-31..2048-06-30 | 2048-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Montebello Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2047-12-31..2048-06-30 | 2048-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Oleson Woods Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2062-11-07..2063-05-07 | 2063-05-07 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Oleson Woods Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2062-11-07..2063-05-07 | 2063-05-07 | unknown |  | tenant_notice_check |
| PUSH-01 | VIEWFINDER, THE | ORS 456.260(1); OAR 813-115-0030 (verify) | 2060-12-31..2061-06-30 | 2061-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | VIEWFINDER, THE | SB 973 (2025); ORS 456.259 (verify operative date) | 2060-12-31..2061-06-30 | 2061-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Peter Paulson Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2052-09-11..2053-03-11 | 2053-03-11 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Peter Paulson Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2052-09-11..2053-03-11 | 2053-03-11 | unknown |  | tenant_notice_check |
| PUSH-01 | Willow Tree Housing (aka Willow Tree Inn) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2060-01-17..2060-07-17 | 2060-07-17 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Willow Tree Housing (aka Willow Tree Inn) | SB 973 (2025); ORS 456.259 (verify operative date) | 2060-01-17..2060-07-17 | 2060-07-17 | unknown |  | tenant_notice_check |
| PUSH-01 | Schiller Way fka Schiller Liebe Family Housing | ORS 456.260(1); OAR 813-115-0030 (verify) | 2034-05-06..2034-11-06 | 2034-11-06 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Schiller Way fka Schiller Liebe Family Housing | SB 973 (2025); ORS 456.259 (verify operative date) | 2034-05-06..2034-11-06 | 2034-11-06 | unknown |  | tenant_notice_check |
| PUSH-01 | Hamilton West Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2056-12-31..2057-06-30 | 2057-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Hamilton West Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2056-12-31..2057-06-30 | 2057-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Fenwick Avenue Housing | ORS 456.260(1); OAR 813-115-0030 (verify) | 2061-09-01..2062-03-01 | 2062-03-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Fenwick Avenue Housing | SB 973 (2025); ORS 456.259 (verify operative date) | 2061-09-01..2062-03-01 | 2062-03-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Sequoia Square | ORS 456.260(1); OAR 813-115-0030 (verify) | 2058-01-01..2058-07-01 | 2058-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Sequoia Square | SB 973 (2025); ORS 456.259 (verify operative date) | 2058-01-01..2058-07-01 | 2058-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Interstate Crossing | ORS 456.260(1); OAR 813-115-0030 (verify) | 2035-08-15..2036-02-15 | 2036-02-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Interstate Crossing | SB 973 (2025); ORS 456.259 (verify operative date) | 2035-08-15..2036-02-15 | 2036-02-15 | unknown |  | tenant_notice_check |
| PUSH-01 | Kafoury Commons | ORS 456.260(1); OAR 813-115-0030 (verify) | 2058-01-01..2058-07-01 | 2058-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Kafoury Commons | SB 973 (2025); ORS 456.259 (verify operative date) | 2058-01-01..2058-07-01 | 2058-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | ST. FRANCIS APTS | ORS 456.260(1); OAR 813-115-0030 (verify) | 2060-01-01..2060-07-01 | 2060-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | ST. FRANCIS APTS | SB 973 (2025); ORS 456.259 (verify operative date) | 2060-01-01..2060-07-01 | 2060-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | BUD CLARK COMMONS | ORS 456.260(1); OAR 813-115-0030 (verify) | 2069-01-01..2069-07-01 | 2069-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | BUD CLARK COMMONS | SB 973 (2025); ORS 456.259 (verify operative date) | 2069-01-01..2069-07-01 | 2069-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | NEW COLUMBIA WOOLSEY III | ORS 456.260(1); OAR 813-115-0030 (verify) | 2045-01-01..2045-07-01 | 2045-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | NEW COLUMBIA WOOLSEY III | SB 973 (2025); ORS 456.259 (verify operative date) | 2045-01-01..2045-07-01 | 2045-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Lovejoy Station | ORS 456.260(1); OAR 813-115-0030 (verify) | 2059-01-01..2059-07-01 | 2059-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Lovejoy Station | SB 973 (2025); ORS 456.259 (verify operative date) | 2059-01-01..2059-07-01 | 2059-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | KELLY PLACE | ORS 456.260(1); OAR 813-115-0030 (verify) | 2054-01-01..2054-07-01 | 2054-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | KELLY PLACE | SB 973 (2025); ORS 456.259 (verify operative date) | 2054-01-01..2054-07-01 | 2054-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Tukwila Springs (fka Webster Road Redev) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2050-12-31..2051-06-30 | 2051-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Tukwila Springs (fka Webster Road Redev) | SB 973 (2025); ORS 456.259 (verify operative date) | 2050-12-31..2051-06-30 | 2051-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Waterleaf (fka RiverPlace Phase 2) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2079-12-31..2080-06-30 | 2080-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Waterleaf (fka RiverPlace Phase 2) | SB 973 (2025); ORS 456.259 (verify operative date) | 2079-12-31..2080-06-30 | 2080-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Center Village Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2057-08-09..2058-02-09 | 2058-02-09 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Center Village Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2057-08-09..2058-02-09 | 2058-02-09 | unknown |  | tenant_notice_check |
| PUSH-01 | Ankeny Woods | ORS 456.260(1); OAR 813-115-0030 (verify) | 2080-12-31..2081-06-30 | 2081-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Ankeny Woods | SB 973 (2025); ORS 456.259 (verify operative date) | 2080-12-31..2081-06-30 | 2081-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | McCoy Village (fka Gladys McCoy Village) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2069-07-01..2070-01-01 | 2070-01-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | McCoy Village (fka Gladys McCoy Village) | SB 973 (2025); ORS 456.259 (verify operative date) | 2069-07-01..2070-01-01 | 2070-01-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Park Terrace | ORS 456.260(1); OAR 813-115-0030 (verify) | 2059-01-01..2059-07-01 | 2059-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Park Terrace | SB 973 (2025); ORS 456.259 (verify operative date) | 2059-01-01..2059-07-01 | 2059-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Clifford Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2068-02-28..2068-08-28 | 2068-08-28 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Clifford Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2068-02-28..2068-08-28 | 2068-08-28 | unknown |  | tenant_notice_check |
| PUSH-01 | Dekum Court 2021 Redevelopment | ORS 456.260(1); OAR 813-115-0030 (verify) | 2051-12-31..2052-06-30 | 2052-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Dekum Court 2021 Redevelopment | SB 973 (2025); ORS 456.259 (verify operative date) | 2051-12-31..2052-06-30 | 2052-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Firland | ORS 456.260(1); OAR 813-115-0030 (verify) | 2069-11-30..2070-05-30 | 2070-05-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Firland | SB 973 (2025); ORS 456.259 (verify operative date) | 2069-11-30..2070-05-30 | 2070-05-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Rosemont Court (fka Villa St Rose) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2058-01-01..2058-07-01 | 2058-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Rosemont Court (fka Villa St Rose) | SB 973 (2025); ORS 456.259 (verify operative date) | 2058-01-01..2058-07-01 | 2058-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Allen Fremont Plaza | ORS 456.260(1); OAR 813-115-0030 (verify) | 2044-05-01..2044-11-01 | 2044-11-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Allen Fremont Plaza | SB 973 (2025); ORS 456.259 (verify operative date) | 2044-05-01..2044-11-01 | 2044-11-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Hattie Redmond Apartments fka Baldwin Project | ORS 456.260(1); OAR 813-115-0030 (verify) | 2050-02-21..2050-08-21 | 2050-08-21 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Hattie Redmond Apartments fka Baldwin Project | SB 973 (2025); ORS 456.259 (verify operative date) | 2050-02-21..2050-08-21 | 2050-08-21 | unknown |  | tenant_notice_check |
| PUSH-01 | Fountain Place | ORS 456.260(1); OAR 813-115-0030 (verify) | 2079-12-31..2080-06-30 | 2080-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Fountain Place | SB 973 (2025); ORS 456.259 (verify operative date) | 2079-12-31..2080-06-30 | 2080-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Fremont Manor | ORS 456.260(1); OAR 813-115-0030 (verify) | 2051-12-31..2052-06-30 | 2052-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Fremont Manor | SB 973 (2025); ORS 456.259 (verify operative date) | 2051-12-31..2052-06-30 | 2052-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Lents 2000 | ORS 456.260(1); OAR 813-115-0030 (verify) | 2073-10-01..2074-04-01 | 2074-04-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Lents 2000 | SB 973 (2025); ORS 456.259 (verify operative date) | 2073-10-01..2074-04-01 | 2074-04-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Clinton Ridge Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2060-01-01..2060-07-01 | 2060-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Clinton Ridge Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2060-01-01..2060-07-01 | 2060-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | MAYFIELD COURT | ORS 456.260(1); OAR 813-115-0030 (verify) | 2046-04-01..2046-10-01 | 2046-10-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | MAYFIELD COURT | SB 973 (2025); ORS 456.259 (verify operative date) | 2046-04-01..2046-10-01 | 2046-10-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Alder House | ORS 456.260(1); OAR 813-115-0030 (verify) | 2079-12-31..2080-06-30 | 2080-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Alder House | SB 973 (2025); ORS 456.259 (verify operative date) | 2079-12-31..2080-06-30 | 2080-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Prescott Terrace | ORS 456.260(1); OAR 813-115-0030 (verify) | 2062-02-25..2062-08-25 | 2062-08-25 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Prescott Terrace | SB 973 (2025); ORS 456.259 (verify operative date) | 2062-02-25..2062-08-25 | 2062-08-25 | unknown |  | tenant_notice_check |
| PUSH-01 | VILLA DE CLARA VISTA | ORS 456.260(1); OAR 813-115-0030 (verify) | 2042-01-01..2042-07-01 | 2042-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | VILLA DE CLARA VISTA | SB 973 (2025); ORS 456.259 (verify operative date) | 2042-01-01..2042-07-01 | 2042-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | MAYBELLE CLARK MACDONALD CENTER | ORS 456.260(1); OAR 813-115-0030 (verify) | 2064-01-01..2064-07-01 | 2064-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | MAYBELLE CLARK MACDONALD CENTER | SB 973 (2025); ORS 456.259 (verify operative date) | 2064-01-01..2064-07-01 | 2064-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Susan Emmons, The | ORS 456.260(1); OAR 813-115-0030 (verify) | 2050-12-31..2051-06-30 | 2051-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Susan Emmons, The | SB 973 (2025); ORS 456.259 (verify operative date) | 2050-12-31..2051-06-30 | 2051-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | LYNDON MUSOLF MANOR | ORS 456.260(1); OAR 813-115-0030 (verify) | 2065-01-01..2065-07-01 | 2065-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | LYNDON MUSOLF MANOR | SB 973 (2025); ORS 456.259 (verify operative date) | 2065-01-01..2065-07-01 | 2065-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | MIRACLES-CENTRAL | ORS 456.260(1); OAR 813-115-0030 (verify) | 2074-07-01..2075-01-01 | 2075-01-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | MIRACLES-CENTRAL | SB 973 (2025); ORS 456.259 (verify operative date) | 2074-07-01..2075-01-01 | 2075-01-01 | unknown |  | tenant_notice_check |
| PUSH-01 | MARK O HATFIELD BUILDING | ORS 456.260(1); OAR 813-115-0030 (verify) | 2051-11-10..2052-05-10 | 2052-05-10 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | MARK O HATFIELD BUILDING | SB 973 (2025); ORS 456.259 (verify operative date) | 2051-11-10..2052-05-10 | 2052-05-10 | unknown |  | tenant_notice_check |
| PUSH-01 | Cathedral Village | ORS 456.260(1); OAR 813-115-0030 (verify) | 2049-12-31..2050-06-30 | 2050-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Cathedral Village | SB 973 (2025); ORS 456.259 (verify operative date) | 2049-12-31..2050-06-30 | 2050-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | MORRISON PARK | ORS 456.260(1); OAR 813-115-0030 (verify) | 2046-01-01..2046-07-01 | 2046-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | MORRISON PARK | SB 973 (2025); ORS 456.259 (verify operative date) | 2046-01-01..2046-07-01 | 2046-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Cascadian Terrace | ORS 456.260(1); OAR 813-115-0030 (verify) | 2047-06-01..2047-12-01 | 2047-12-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Cascadian Terrace | SB 973 (2025); ORS 456.259 (verify operative date) | 2047-06-01..2047-12-01 | 2047-12-01 | unknown |  | tenant_notice_check |
| HAP-01 | Cascadian Terrace | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2037-09-30 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | Cascadian Terrace | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2038-06-02 | renewal_request_status=unknown |  |  |
| PUSH-01 | Hayu Tilixam | ORS 456.260(1); OAR 813-115-0030 (verify) | 2050-12-31..2051-06-30 | 2051-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Hayu Tilixam | SB 973 (2025); ORS 456.259 (verify operative date) | 2050-12-31..2051-06-30 | 2051-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Viewfinder (fka Tigard Triangle) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2048-12-31..2049-06-30 | 2049-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Viewfinder (fka Tigard Triangle) | SB 973 (2025); ORS 456.259 (verify operative date) | 2048-12-31..2049-06-30 | 2049-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Spruce Place | ORS 456.260(1); OAR 813-115-0030 (verify) | 2047-12-31..2048-06-30 | 2048-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Spruce Place | SB 973 (2025); ORS 456.259 (verify operative date) | 2047-12-31..2048-06-30 | 2048-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Nueva Esperanza | ORS 456.260(1); OAR 813-115-0030 (verify) | 2051-12-31..2052-06-30 | 2052-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Nueva Esperanza | SB 973 (2025); ORS 456.259 (verify operative date) | 2051-12-31..2052-06-30 | 2052-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Juniper Gardens I | ORS 456.260(1); OAR 813-115-0030 (verify) | 2042-11-07..2043-05-07 | 2043-05-07 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Juniper Gardens I | SB 973 (2025); ORS 456.259 (verify operative date) | 2042-11-07..2043-05-07 | 2043-05-07 | unknown |  | tenant_notice_check |
| PUSH-01 | Pomeroy Place | ORS 456.260(1); OAR 813-115-0030 (verify) | 2075-12-31..2076-06-30 | 2076-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Pomeroy Place | SB 973 (2025); ORS 456.259 (verify operative date) | 2075-12-31..2076-06-30 | 2076-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Villa Capri Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2060-01-01..2060-07-01 | 2060-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Villa Capri Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2060-01-01..2060-07-01 | 2060-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Alongside Senior Housing | ORS 456.260(1); OAR 813-115-0030 (verify) | 2051-12-31..2052-06-30 | 2052-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Alongside Senior Housing | SB 973 (2025); ORS 456.259 (verify operative date) | 2051-12-31..2052-06-30 | 2052-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | KINNAMAN TOWNHOMES | ORS 456.260(1); OAR 813-115-0030 (verify) | 2041-06-28..2041-12-28 | 2041-12-28 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | KINNAMAN TOWNHOMES | SB 973 (2025); ORS 456.259 (verify operative date) | 2041-06-28..2041-12-28 | 2041-12-28 | unknown |  | tenant_notice_check |
| PUSH-01 | Plaza Los Robles | ORS 456.260(1); OAR 813-115-0030 (verify) | 2055-04-01..2055-10-01 | 2055-10-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Plaza Los Robles | SB 973 (2025); ORS 456.259 (verify operative date) | 2055-04-01..2055-10-01 | 2055-10-01 | unknown |  | tenant_notice_check |
| PUSH-01 | HUMMINGBIRD APTS | ORS 456.260(1); OAR 813-115-0030 (verify) | 2042-08-23..2043-02-23 | 2043-02-23 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | HUMMINGBIRD APTS | SB 973 (2025); ORS 456.259 (verify operative date) | 2042-08-23..2043-02-23 | 2043-02-23 | unknown |  | tenant_notice_check |
| HAP-01 | CASCADE MEADOWS | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2043-09-30 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | CASCADE MEADOWS | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2044-06-02 | renewal_request_status=unknown |  |  |
| HAP-01 | 300 MAIN | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2039-12-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | 300 MAIN | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2040-09-02 | renewal_request_status=unknown |  |  |
| PUSH-01 | Sandy Vista Phase II | ORS 456.260(1); OAR 813-115-0030 (verify) | 2060-06-17..2060-12-17 | 2060-12-17 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Sandy Vista Phase II | SB 973 (2025); ORS 456.259 (verify operative date) | 2060-06-17..2060-12-17 | 2060-12-17 | unknown |  | tenant_notice_check |
| PUSH-01 | Renaissance Court - Villebois | ORS 456.260(1); OAR 813-115-0030 (verify) | 2044-05-17..2044-11-17 | 2044-11-17 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Renaissance Court - Villebois | SB 973 (2025); ORS 456.259 (verify operative date) | 2044-05-17..2044-11-17 | 2044-11-17 | unknown |  | tenant_notice_check |
| PUSH-01 | The Katherine Gray (fka Martha Washington) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2067-01-01..2067-07-01 | 2067-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | The Katherine Gray (fka Martha Washington) | SB 973 (2025); ORS 456.259 (verify operative date) | 2067-01-01..2067-07-01 | 2067-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Maggie Gibson Plaza | ORS 456.260(1); OAR 813-115-0030 (verify) | 2033-12-06..2034-06-06 | 2034-06-06 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Maggie Gibson Plaza | SB 973 (2025); ORS 456.259 (verify operative date) | 2033-12-06..2034-06-06 | 2034-06-06 | unknown |  | tenant_notice_check |
| PUSH-01 | Pearl Court Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2053-01-01..2053-07-01 | 2053-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Pearl Court Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2053-01-01..2053-07-01 | 2053-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Pioneer Place Apts | ORS 456.260(1); OAR 813-115-0030 (verify) | 2041-11-17..2042-05-17 | 2042-05-17 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Pioneer Place Apts | SB 973 (2025); ORS 456.259 (verify operative date) | 2041-11-17..2042-05-17 | 2042-05-17 | unknown |  | tenant_notice_check |
| PUSH-01 | Maya Angelou | ORS 456.260(1); OAR 813-115-0030 (verify) | 2046-02-08..2046-08-08 | 2046-08-08 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Maya Angelou | SB 973 (2025); ORS 456.259 (verify operative date) | 2046-02-08..2046-08-08 | 2046-08-08 | unknown |  | tenant_notice_check |
| PUSH-01 | Tistilal Village | ORS 456.260(1); OAR 813-115-0030 (verify) | 2055-07-22..2056-01-22 | 2056-01-22 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Tistilal Village | SB 973 (2025); ORS 456.259 (verify operative date) | 2055-07-22..2056-01-22 | 2056-01-22 | unknown |  | tenant_notice_check |
| PUSH-01 | NAYA Generations | ORS 456.260(1); OAR 813-115-0030 (verify) | 2075-03-31..2075-09-30 | 2075-09-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | NAYA Generations | SB 973 (2025); ORS 456.259 (verify operative date) | 2075-03-31..2075-09-30 | 2075-09-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Bukas Place | ORS 456.260(1); OAR 813-115-0030 (verify) | 2058-12-17..2059-06-17 | 2059-06-17 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Bukas Place | SB 973 (2025); ORS 456.259 (verify operative date) | 2058-12-17..2059-06-17 | 2059-06-17 | unknown |  | tenant_notice_check |
| PUSH-01 | Marwood Plaza | ORS 456.260(1); OAR 813-115-0030 (verify) | 2057-01-01..2057-07-01 | 2057-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Marwood Plaza | SB 973 (2025); ORS 456.259 (verify operative date) | 2057-01-01..2057-07-01 | 2057-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Scattered Multiplexes | ORS 456.260(1); OAR 813-115-0030 (verify) | 2056-07-15..2057-01-15 | 2057-01-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Scattered Multiplexes | SB 973 (2025); ORS 456.259 (verify operative date) | 2056-07-15..2057-01-15 | 2057-01-15 | unknown |  | tenant_notice_check |
| PUSH-01 | Kateri Park | ORS 456.260(1); OAR 813-115-0030 (verify) | 2073-07-05..2074-01-05 | 2074-01-05 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Kateri Park | SB 973 (2025); ORS 456.259 (verify operative date) | 2073-07-05..2074-01-05 | 2074-01-05 | unknown |  | tenant_notice_check |
| PUSH-01 | Minerva Plaza | ORS 456.260(1); OAR 813-115-0030 (verify) | 2057-01-01..2057-07-01 | 2057-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Minerva Plaza | SB 973 (2025); ORS 456.259 (verify operative date) | 2057-01-01..2057-07-01 | 2057-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | On Your Own | ORS 456.260(1); OAR 813-115-0030 (verify) | 2057-11-27..2058-05-27 | 2058-05-27 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | On Your Own | SB 973 (2025); ORS 456.259 (verify operative date) | 2057-11-27..2058-05-27 | 2058-05-27 | unknown |  | tenant_notice_check |
| PUSH-01 | Holgate Plaza | ORS 456.260(1); OAR 813-115-0030 (verify) | 2057-01-01..2057-07-01 | 2057-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Holgate Plaza | SB 973 (2025); ORS 456.259 (verify operative date) | 2057-01-01..2057-07-01 | 2057-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Betty Campbell Building | ORS 456.260(1); OAR 813-115-0030 (verify) | 2053-05-16..2053-11-16 | 2053-11-16 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Betty Campbell Building | SB 973 (2025); ORS 456.259 (verify operative date) | 2053-05-16..2053-11-16 | 2053-11-16 | unknown |  | tenant_notice_check |
| PUSH-01 | Kehillah Housing | ORS 456.260(1); OAR 813-115-0030 (verify) | 2071-11-01..2072-05-01 | 2072-05-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Kehillah Housing | SB 973 (2025); ORS 456.259 (verify operative date) | 2071-11-01..2072-05-01 | 2072-05-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Douglas Fir Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2080-04-04..2080-10-04 | 2080-10-04 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Douglas Fir Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2080-04-04..2080-10-04 | 2080-10-04 | unknown |  | tenant_notice_check |
| PUSH-01 | Douglas Meadows | ORS 456.260(1); OAR 813-115-0030 (verify) | 2058-06-25..2058-12-25 | 2058-12-25 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Douglas Meadows | SB 973 (2025); ORS 456.259 (verify operative date) | 2058-06-25..2058-12-25 | 2058-12-25 | unknown |  | tenant_notice_check |
| PUSH-01 | Bellrose Station | ORS 456.260(1); OAR 813-115-0030 (verify) | 2069-03-20..2069-09-20 | 2069-09-20 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Bellrose Station | SB 973 (2025); ORS 456.259 (verify operative date) | 2069-03-20..2069-09-20 | 2069-09-20 | unknown |  | tenant_notice_check |
| PUSH-01 | Tistilal Village | ORS 456.260(1); OAR 813-115-0030 (verify) | 2055-07-22..2056-01-22 | 2056-01-22 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Tistilal Village | SB 973 (2025); ORS 456.259 (verify operative date) | 2055-07-22..2056-01-22 | 2056-01-22 | unknown |  | tenant_notice_check |
| PUSH-01 | Rosemont Town Homes | ORS 456.260(1); OAR 813-115-0030 (verify) | 2058-01-01..2058-07-01 | 2058-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Rosemont Town Homes | SB 973 (2025); ORS 456.259 (verify operative date) | 2058-01-01..2058-07-01 | 2058-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | PCRI Scattered Site Project | ORS 456.260(1); OAR 813-115-0030 (verify) | 2056-11-11..2057-05-11 | 2057-05-11 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | PCRI Scattered Site Project | SB 973 (2025); ORS 456.259 (verify operative date) | 2056-11-11..2057-05-11 | 2057-05-11 | unknown |  | tenant_notice_check |
| PUSH-01 | New Meadows | ORS 456.260(1); OAR 813-115-0030 (verify) | 2075-05-30..2075-11-30 | 2075-11-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | New Meadows | SB 973 (2025); ORS 456.259 (verify operative date) | 2075-05-30..2075-11-30 | 2075-11-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Ainsworth Court | ORS 456.260(1); OAR 813-115-0030 (verify) | 2068-08-31..2069-02-28 | 2069-02-28 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Ainsworth Court | SB 973 (2025); ORS 456.259 (verify operative date) | 2068-08-31..2069-02-28 | 2069-02-28 | unknown |  | tenant_notice_check |
| PUSH-01 | Beyer Court | ORS 456.260(1); OAR 813-115-0030 (verify) | 2056-08-23..2057-02-23 | 2057-02-23 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Beyer Court | SB 973 (2025); ORS 456.259 (verify operative date) | 2056-08-23..2057-02-23 | 2057-02-23 | unknown |  | tenant_notice_check |
| PUSH-01 | Relay Huckleberry and Juniper Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2038-12-31..2039-06-30 | 2039-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Relay Huckleberry and Juniper Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2038-12-31..2039-06-30 | 2039-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | LOU BURGES PLACE | ORS 456.260(1); OAR 813-115-0030 (verify) | 2035-12-15..2036-06-15 | 2036-06-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | LOU BURGES PLACE | SB 973 (2025); ORS 456.259 (verify operative date) | 2035-12-15..2036-06-15 | 2036-06-15 | unknown |  | tenant_notice_check |
| PUSH-01 | Commons, The | ORS 456.260(1); OAR 813-115-0030 (verify) | 2057-07-01..2058-01-01 | 2058-01-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Commons, The | SB 973 (2025); ORS 456.259 (verify operative date) | 2057-07-01..2058-01-01 | 2058-01-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Family Scattered Site | ORS 456.260(1); OAR 813-115-0030 (verify) | 2055-03-24..2055-09-24 | 2055-09-24 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Family Scattered Site | SB 973 (2025); ORS 456.259 (verify operative date) | 2055-03-24..2055-09-24 | 2055-09-24 | unknown |  | tenant_notice_check |
| PUSH-01 | Plaza de Cedro | ORS 456.260(1); OAR 813-115-0030 (verify) | 2059-02-13..2059-08-13 | 2059-08-13 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Plaza de Cedro | SB 973 (2025); ORS 456.259 (verify operative date) | 2059-02-13..2059-08-13 | 2059-08-13 | unknown |  | tenant_notice_check |
| PUSH-01 | Columbia View | ORS 456.260(1); OAR 813-115-0030 (verify) | 2055-05-11..2055-11-11 | 2055-11-11 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Columbia View | SB 973 (2025); ORS 456.259 (verify operative date) | 2055-05-11..2055-11-11 | 2055-11-11 | unknown |  | tenant_notice_check |
| PUSH-01 | Ritzdorf Court | ORS 456.260(1); OAR 813-115-0030 (verify) | 2057-01-01..2057-07-01 | 2057-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Ritzdorf Court | SB 973 (2025); ORS 456.259 (verify operative date) | 2057-01-01..2057-07-01 | 2057-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | CEEL-OCKS MANOR | ORS 456.260(1); OAR 813-115-0030 (verify) | 2041-09-28..2042-03-28 | 2042-03-28 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | CEEL-OCKS MANOR | SB 973 (2025); ORS 456.259 (verify operative date) | 2041-09-28..2042-03-28 | 2042-03-28 | unknown |  | tenant_notice_check |
| PUSH-01 | BUTTE HOTEL | ORS 456.260(1); OAR 813-115-0030 (verify) | 2070-03-31..2070-09-30 | 2070-09-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | BUTTE HOTEL | SB 973 (2025); ORS 456.259 (verify operative date) | 2070-03-31..2070-09-30 | 2070-09-30 | unknown |  | tenant_notice_check |
| PUSH-01 | RUSSET & MORRIS GREEN PLEXES | ORS 456.260(1); OAR 813-115-0030 (verify) | 2061-03-11..2061-09-11 | 2061-09-11 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | RUSSET & MORRIS GREEN PLEXES | SB 973 (2025); ORS 456.259 (verify operative date) | 2061-03-11..2061-09-11 | 2061-09-11 | unknown |  | tenant_notice_check |
| HAP-01 | MARSHALL UNION MANOR II | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2041-07-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | MARSHALL UNION MANOR II | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2042-04-02 | renewal_request_status=unknown |  |  |
| PUSH-01 | Wygant Street | ORS 456.260(1); OAR 813-115-0030 (verify) | 2046-04-08..2046-10-08 | 2046-10-08 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Wygant Street | SB 973 (2025); ORS 456.259 (verify operative date) | 2046-04-08..2046-10-08 | 2046-10-08 | unknown |  | tenant_notice_check |
| PUSH-01 | Coburn Woods Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2034-09-29..2035-03-29 | 2035-03-29 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Coburn Woods Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2034-09-29..2035-03-29 | 2035-03-29 | unknown |  | tenant_notice_check |
| PUSH-01 | Endelea Court | ORS 456.260(1); OAR 813-115-0030 (verify) | 2055-06-24..2055-12-24 | 2055-12-24 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Endelea Court | SB 973 (2025); ORS 456.259 (verify operative date) | 2055-06-24..2055-12-24 | 2055-12-24 | unknown |  | tenant_notice_check |
| PUSH-01 | ARBOR GLEN | ORS 456.260(1); OAR 813-115-0030 (verify) | 2066-01-01..2066-07-01 | 2066-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | ARBOR GLEN | SB 973 (2025); ORS 456.259 (verify operative date) | 2066-01-01..2066-07-01 | 2066-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Harkson Court (DIS) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2069-10-19..2070-04-19 | 2070-04-19 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Harkson Court (DIS) | SB 973 (2025); ORS 456.259 (verify operative date) | 2069-10-19..2070-04-19 | 2070-04-19 | unknown |  | tenant_notice_check |
| PUSH-01 | Juniper Gardens II | ORS 456.260(1); OAR 813-115-0030 (verify) | 2071-10-01..2072-04-01 | 2072-04-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Juniper Gardens II | SB 973 (2025); ORS 456.259 (verify operative date) | 2071-10-01..2072-04-01 | 2072-04-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Woodspring Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2081-12-31..2082-06-30 | 2082-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Woodspring Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2081-12-31..2082-06-30 | 2082-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Belleau Woods Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2080-12-31..2081-06-30 | 2081-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Belleau Woods Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2080-12-31..2081-06-30 | 2081-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | City Center Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2036-01-01..2036-07-01 | 2036-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | City Center Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2036-01-01..2036-07-01 | 2036-07-01 | unknown |  | tenant_notice_check |
| HAP-01 | TARKINGTON SQUARE | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2042-12-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | TARKINGTON SQUARE | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2043-09-02 | renewal_request_status=unknown |  |  |
| HAP-01 | ALOHA PARK | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2041-06-30 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | ALOHA PARK | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2042-03-02 | renewal_request_status=unknown |  |  |
| PUSH-01 | Bear Creek Apartments (fka Molalla Apartments) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2051-12-31..2052-06-30 | 2052-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Bear Creek Apartments (fka Molalla Apartments) | SB 973 (2025); ORS 456.259 (verify operative date) | 2051-12-31..2052-06-30 | 2052-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Rain Garden Apts | ORS 456.260(1); OAR 813-115-0030 (verify) | 2066-08-19..2067-02-19 | 2067-02-19 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Rain Garden Apts | SB 973 (2025); ORS 456.259 (verify operative date) | 2066-08-19..2067-02-19 | 2067-02-19 | unknown |  | tenant_notice_check |
| PUSH-01 | West Gresham Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2063-01-01..2063-07-01 | 2063-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | West Gresham Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2063-01-01..2063-07-01 | 2063-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Lawrence, the fka 148th Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2051-12-31..2052-06-30 | 2052-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Lawrence, the fka 148th Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2051-12-31..2052-06-30 | 2052-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Sunset Gardens Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2050-01-01..2050-07-01 | 2050-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Sunset Gardens Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2050-01-01..2050-07-01 | 2050-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Sierra West | ORS 456.260(1); OAR 813-115-0030 (verify) | 2050-01-01..2050-07-01 | 2050-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Sierra West | SB 973 (2025); ORS 456.259 (verify operative date) | 2050-01-01..2050-07-01 | 2050-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Casa Verde | ORS 456.260(1); OAR 813-115-0030 (verify) | 2057-01-01..2057-07-01 | 2057-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Casa Verde | SB 973 (2025); ORS 456.259 (verify operative date) | 2057-01-01..2057-07-01 | 2057-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Fuller Station Affordable Housing | ORS 456.260(1); OAR 813-115-0030 (verify) | 2050-12-31..2051-06-30 | 2051-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Fuller Station Affordable Housing | SB 973 (2025); ORS 456.259 (verify operative date) | 2050-12-31..2051-06-30 | 2051-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Chez Ami Mental Health Housing | ORS 456.260(1); OAR 813-115-0030 (verify) | 2059-01-01..2059-07-01 | 2059-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Chez Ami Mental Health Housing | SB 973 (2025); ORS 456.259 (verify operative date) | 2059-01-01..2059-07-01 | 2059-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Meadows at Hope Village, The | ORS 456.260(1); OAR 813-115-0030 (verify) | 2041-01-01..2041-07-01 | 2041-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Meadows at Hope Village, The | SB 973 (2025); ORS 456.259 (verify operative date) | 2041-01-01..2041-07-01 | 2041-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Cascade House at HOPE Village | ORS 456.260(1); OAR 813-115-0030 (verify) | 2034-05-28..2034-11-28 | 2034-11-28 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Cascade House at HOPE Village | SB 973 (2025); ORS 456.259 (verify operative date) | 2034-05-28..2034-11-28 | 2034-11-28 | unknown |  | tenant_notice_check |
| PUSH-01 | Molalla Gardens | ORS 456.260(1); OAR 813-115-0030 (verify) | 2075-03-31..2075-09-30 | 2075-09-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Molalla Gardens | SB 973 (2025); ORS 456.259 (verify operative date) | 2075-03-31..2075-09-30 | 2075-09-30 | unknown |  | tenant_notice_check |
| PUSH-01 | THE GREENS AT RIDINGS | ORS 456.260(1); OAR 813-115-0030 (verify) | 2076-03-01..2076-09-01 | 2076-09-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | THE GREENS AT RIDINGS | SB 973 (2025); ORS 456.259 (verify operative date) | 2076-03-01..2076-09-01 | 2076-09-01 | unknown |  | tenant_notice_check |
| HAP-01 | THE GREENS AT RIDINGS | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2037-03-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | THE GREENS AT RIDINGS | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2037-12-01 | renewal_request_status=unknown |  |  |
| PUSH-01 | North Main Apts | ORS 456.260(1); OAR 813-115-0030 (verify) | 2052-12-31..2053-06-30 | 2053-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | North Main Apts | SB 973 (2025); ORS 456.259 (verify operative date) | 2052-12-31..2053-06-30 | 2053-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | The Bria Apartments (fka146th East West) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2050-12-31..2051-06-30 | 2051-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | The Bria Apartments (fka146th East West) | SB 973 (2025); ORS 456.259 (verify operative date) | 2050-12-31..2051-06-30 | 2051-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Crescent Court (fka 115th Street Housing) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2080-12-31..2081-06-30 | 2081-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Crescent Court (fka 115th Street Housing) | SB 973 (2025); ORS 456.259 (verify operative date) | 2080-12-31..2081-06-30 | 2081-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Watershed at Hillsdale, The (aka Bertha Station) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2064-12-17..2065-06-17 | 2065-06-17 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Watershed at Hillsdale, The (aka Bertha Station) | SB 973 (2025); ORS 456.259 (verify operative date) | 2064-12-17..2065-06-17 | 2065-06-17 | unknown |  | tenant_notice_check |
| PUSH-01 | Alpha Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2057-10-01..2058-04-01 | 2058-04-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Alpha Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2057-10-01..2058-04-01 | 2058-04-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Villa de Suenos | ORS 456.260(1); OAR 813-115-0030 (verify) | 2055-05-07..2055-11-07 | 2055-11-07 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Villa de Suenos | SB 973 (2025); ORS 456.259 (verify operative date) | 2055-05-07..2055-11-07 | 2055-11-07 | unknown |  | tenant_notice_check |
| PUSH-01 | St James | ORS 456.260(1); OAR 813-115-0030 (verify) | 2041-01-01..2041-07-01 | 2041-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | St James | SB 973 (2025); ORS 456.259 (verify operative date) | 2041-01-01..2041-07-01 | 2041-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Clara Vista Townhomes | ORS 456.260(1); OAR 813-115-0030 (verify) | 2063-03-01..2063-09-01 | 2063-09-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Clara Vista Townhomes | SB 973 (2025); ORS 456.259 (verify operative date) | 2063-03-01..2063-09-01 | 2063-09-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Pine Point Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2058-01-01..2058-07-01 | 2058-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Pine Point Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2058-01-01..2058-07-01 | 2058-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Los Jardines De La Paz | ORS 456.260(1); OAR 813-115-0030 (verify) | 2074-07-01..2075-01-01 | 2075-01-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Los Jardines De La Paz | SB 973 (2025); ORS 456.259 (verify operative date) | 2074-07-01..2075-01-01 | 2075-01-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Lents Village Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2044-01-01..2044-07-01 | 2044-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Lents Village Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2044-01-01..2044-07-01 | 2044-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Andrea Place | ORS 456.260(1); OAR 813-115-0030 (verify) | 2072-07-01..2073-01-01 | 2073-01-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Andrea Place | SB 973 (2025); ORS 456.259 (verify operative date) | 2072-07-01..2073-01-01 | 2073-01-01 | unknown |  | tenant_notice_check |
| PUSH-01 | 146th East & West | ORS 456.260(1); OAR 813-115-0030 (verify) | 2074-06-01..2074-12-01 | 2074-12-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | 146th East & West | SB 973 (2025); ORS 456.259 (verify operative date) | 2074-06-01..2074-12-01 | 2074-12-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Cedar Meadows | ORS 456.260(1); OAR 813-115-0030 (verify) | 2047-10-11..2048-04-11 | 2048-04-11 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Cedar Meadows | SB 973 (2025); ORS 456.259 (verify operative date) | 2047-10-11..2048-04-11 | 2048-04-11 | unknown |  | tenant_notice_check |
| PUSH-01 | Bridge Meadows Senior | ORS 456.260(1); OAR 813-115-0030 (verify) | 2069-01-01..2069-07-01 | 2069-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Bridge Meadows Senior | SB 973 (2025); ORS 456.259 (verify operative date) | 2069-01-01..2069-07-01 | 2069-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Park Vista | ORS 456.260(1); OAR 813-115-0030 (verify) | 2058-01-01..2058-07-01 | 2058-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Park Vista | SB 973 (2025); ORS 456.259 (verify operative date) | 2058-01-01..2058-07-01 | 2058-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Shaver Green Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2067-03-12..2067-09-12 | 2067-09-12 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Shaver Green Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2067-03-12..2067-09-12 | 2067-09-12 | unknown |  | tenant_notice_check |
| PUSH-01 | Starlight fka CCC Westwind Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2050-12-31..2051-06-30 | 2051-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Starlight fka CCC Westwind Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2050-12-31..2051-06-30 | 2051-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | RAMONA APTS | ORS 456.260(1); OAR 813-115-0030 (verify) | 2039-02-01..2039-08-01 | 2039-08-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | RAMONA APTS | SB 973 (2025); ORS 456.259 (verify operative date) | 2039-02-01..2039-08-01 | 2039-08-01 | unknown |  | tenant_notice_check |
| PUSH-01 | YARDS AT UNION STATION C | ORS 456.260(1); OAR 813-115-0030 (verify) | 2041-02-15..2041-08-15 | 2041-08-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | YARDS AT UNION STATION C | SB 973 (2025); ORS 456.259 (verify operative date) | 2041-02-15..2041-08-15 | 2041-08-15 | unknown |  | tenant_notice_check |
| PUSH-01 | Hazelwood Station | ORS 456.260(1); OAR 813-115-0030 (verify) | 2061-01-01..2061-07-01 | 2061-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Hazelwood Station | SB 973 (2025); ORS 456.259 (verify operative date) | 2061-01-01..2061-07-01 | 2061-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Fircrest Manor Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2075-03-01..2075-09-01 | 2075-09-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Fircrest Manor Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2075-03-01..2075-09-01 | 2075-09-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Jose Arciga Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2059-01-01..2059-07-01 | 2059-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Jose Arciga Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2059-01-01..2059-07-01 | 2059-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Willow Park Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2050-01-01..2050-07-01 | 2050-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Willow Park Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2050-01-01..2050-07-01 | 2050-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Terrace at Mt Scott, The | ORS 456.260(1); OAR 813-115-0030 (verify) | 2044-01-01..2044-07-01 | 2044-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Terrace at Mt Scott, The | SB 973 (2025); ORS 456.259 (verify operative date) | 2044-01-01..2044-07-01 | 2044-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | KINGSBERRY HEIGHTS | ORS 456.260(1); OAR 813-115-0030 (verify) | 2041-01-01..2041-07-01 | 2041-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | KINGSBERRY HEIGHTS | SB 973 (2025); ORS 456.259 (verify operative date) | 2041-01-01..2041-07-01 | 2041-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | DEERFIELD VILLAGE | ORS 456.260(1); OAR 813-115-0030 (verify) | 2034-09-15..2035-03-15 | 2035-03-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | DEERFIELD VILLAGE | SB 973 (2025); ORS 456.259 (verify operative date) | 2034-09-15..2035-03-15 | 2035-03-15 | unknown |  | tenant_notice_check |
| PUSH-01 | BEAVER STATE - MONTEBELLO | ORS 456.260(1); OAR 813-115-0030 (verify) | 2049-12-15..2050-06-15 | 2050-06-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | BEAVER STATE - MONTEBELLO | SB 973 (2025); ORS 456.259 (verify operative date) | 2049-12-15..2050-06-15 | 2050-06-15 | unknown |  | tenant_notice_check |
| PUSH-01 | Our House | ORS 456.260(1); OAR 813-115-0030 (verify) | 2063-02-23..2063-08-23 | 2063-08-23 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Our House | SB 973 (2025); ORS 456.259 (verify operative date) | 2063-02-23..2063-08-23 | 2063-08-23 | unknown |  | tenant_notice_check |
| PUSH-01 | Hewitt Place | ORS 456.260(1); OAR 813-115-0030 (verify) | 2065-09-12..2066-03-12 | 2066-03-12 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Hewitt Place | SB 973 (2025); ORS 456.259 (verify operative date) | 2065-09-12..2066-03-12 | 2066-03-12 | unknown |  | tenant_notice_check |
| PUSH-01 | New Columbia Trouton | ORS 456.260(1); OAR 813-115-0030 (verify) | 2043-01-01..2043-07-01 | 2043-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | New Columbia Trouton | SB 973 (2025); ORS 456.259 (verify operative date) | 2043-01-01..2043-07-01 | 2043-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Findley Commons | ORS 456.260(1); OAR 813-115-0030 (verify) | 2049-12-31..2050-06-30 | 2050-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Findley Commons | SB 973 (2025); ORS 456.259 (verify operative date) | 2049-12-31..2050-06-30 | 2050-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Market Street Home | ORS 456.260(1); OAR 813-115-0030 (verify) | 2044-11-05..2045-05-05 | 2045-05-05 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Market Street Home | SB 973 (2025); ORS 456.259 (verify operative date) | 2044-11-05..2045-05-05 | 2045-05-05 | unknown |  | tenant_notice_check |
| PUSH-01 | L Roy Gardens | ORS 456.260(1); OAR 813-115-0030 (verify) | 2044-03-10..2044-09-10 | 2044-09-10 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | L Roy Gardens | SB 973 (2025); ORS 456.259 (verify operative date) | 2044-03-10..2044-09-10 | 2044-09-10 | unknown |  | tenant_notice_check |
| PUSH-01 | Humboldt Gardens | ORS 456.260(1); OAR 813-115-0030 (verify) | 2065-05-20..2065-11-20 | 2065-11-20 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Humboldt Gardens | SB 973 (2025); ORS 456.259 (verify operative date) | 2065-05-20..2065-11-20 | 2065-11-20 | unknown |  | tenant_notice_check |
| PUSH-01 | Village at the Headwaters, The | ORS 456.260(1); OAR 813-115-0030 (verify) | 2065-01-01..2065-07-01 | 2065-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Village at the Headwaters, The | SB 973 (2025); ORS 456.259 (verify operative date) | 2065-01-01..2065-07-01 | 2065-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Troutdale Terrace | ORS 456.260(1); OAR 813-115-0030 (verify) | 2059-01-01..2059-07-01 | 2059-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Troutdale Terrace | SB 973 (2025); ORS 456.259 (verify operative date) | 2059-01-01..2059-07-01 | 2059-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | New Columbia Cecelia | ORS 456.260(1); OAR 813-115-0030 (verify) | 2042-07-28..2043-01-28 | 2043-01-28 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | New Columbia Cecelia | SB 973 (2025); ORS 456.259 (verify operative date) | 2042-07-28..2043-01-28 | 2043-01-28 | unknown |  | tenant_notice_check |
| PUSH-01 | Pacific Tower | ORS 456.260(1); OAR 813-115-0030 (verify) | 2062-01-01..2062-07-01 | 2062-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Pacific Tower | SB 973 (2025); ORS 456.259 (verify operative date) | 2062-01-01..2062-07-01 | 2062-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Springwater Commons | ORS 456.260(1); OAR 813-115-0030 (verify) | 2061-01-01..2061-07-01 | 2061-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Springwater Commons | SB 973 (2025); ORS 456.259 (verify operative date) | 2061-01-01..2061-07-01 | 2061-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Hazelwood Community Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2040-07-15..2041-01-15 | 2041-01-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Hazelwood Community Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2040-07-15..2041-01-15 | 2041-01-15 | unknown |  | tenant_notice_check |
| PUSH-01 | Cedar Commons fka Division St Apts | ORS 456.260(1); OAR 813-115-0030 (verify) | 2049-12-31..2050-06-30 | 2050-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Cedar Commons fka Division St Apts | SB 973 (2025); ORS 456.259 (verify operative date) | 2049-12-31..2050-06-30 | 2050-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Cascade Crossing | ORS 456.260(1); OAR 813-115-0030 (verify) | 2057-01-01..2057-07-01 | 2057-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Cascade Crossing | SB 973 (2025); ORS 456.259 (verify operative date) | 2057-01-01..2057-07-01 | 2057-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | The Terrace at Columbia Knoll | ORS 456.260(1); OAR 813-115-0030 (verify) | 2063-01-01..2063-07-01 | 2063-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | The Terrace at Columbia Knoll | SB 973 (2025); ORS 456.259 (verify operative date) | 2063-01-01..2063-07-01 | 2063-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Morrison, The | ORS 456.260(1); OAR 813-115-0030 (verify) | 2065-01-01..2065-07-01 | 2065-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Morrison, The | SB 973 (2025); ORS 456.259 (verify operative date) | 2065-01-01..2065-07-01 | 2065-07-01 | unknown |  | tenant_notice_check |
| HAP-01 | CARITAS PLAZA | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2037-03-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | CARITAS PLAZA | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2037-12-01 | renewal_request_status=unknown |  |  |
| HAP-01 | FREMONT MANOR | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2041-02-28 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | FREMONT MANOR | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2041-10-31 | renewal_request_status=unknown |  |  |
| PUSH-01 | 8 NW 8th Building (aka Richard L Harris Building) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2061-01-01..2061-07-01 | 2061-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | 8 NW 8th Building (aka Richard L Harris Building) | SB 973 (2025); ORS 456.259 (verify operative date) | 2061-01-01..2061-07-01 | 2061-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Columbia Knoll Heights (Elderly) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2063-01-01..2063-07-01 | 2063-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Columbia Knoll Heights (Elderly) | SB 973 (2025); ORS 456.259 (verify operative date) | 2063-01-01..2063-07-01 | 2063-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Hotel Alder | ORS 456.260(1); OAR 813-115-0030 (verify) | 2062-01-01..2062-07-01 | 2062-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Hotel Alder | SB 973 (2025); ORS 456.259 (verify operative date) | 2062-01-01..2062-07-01 | 2062-07-01 | unknown |  | tenant_notice_check |
| HAP-01 | MARION STREET | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2036-11-30 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | MARION STREET | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2037-08-02 | renewal_request_status=unknown |  |  |
| HAP-01 | KIRKLAND UNION MANOR II | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2041-03-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | KIRKLAND UNION MANOR II | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2041-12-01 | renewal_request_status=unknown |  |  |
| PUSH-01 | KINGS GARDEN APTS | ORS 456.260(1); OAR 813-115-0030 (verify) | 2096-12-31..2097-06-30 | 2097-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | KINGS GARDEN APTS | SB 973 (2025); ORS 456.259 (verify operative date) | 2096-12-31..2097-06-30 | 2097-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Villas de Mariposas | ORS 456.260(1); OAR 813-115-0030 (verify) | 2063-01-01..2063-07-01 | 2063-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Villas de Mariposas | SB 973 (2025); ORS 456.259 (verify operative date) | 2063-01-01..2063-07-01 | 2063-07-01 | unknown |  | tenant_notice_check |
| HAP-01 | MATTIE YOUNKIN MANOR | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2039-05-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | MATTIE YOUNKIN MANOR | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2040-02-01 | renewal_request_status=unknown |  |  |
| HAP-01 | MARSHALL UNION MANOR I | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2041-07-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | MARSHALL UNION MANOR I | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2042-04-02 | renewal_request_status=unknown |  |  |
| HAP-01 | SUMMER RUN | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2041-03-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | SUMMER RUN | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2041-12-01 | renewal_request_status=unknown |  |  |
| HAP-01 | BURLWOOD | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2043-09-30 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | BURLWOOD | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2044-06-02 | renewal_request_status=unknown |  |  |
| HAP-01 | PRESCOTT PLACE | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2041-03-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | PRESCOTT PLACE | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2041-12-01 | renewal_request_status=unknown |  |  |
| PUSH-01 | Breitung Building (aka Garfield Veterans Apartments) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2077-04-30..2077-10-30 | 2077-10-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Breitung Building (aka Garfield Veterans Apartments) | SB 973 (2025); ORS 456.259 (verify operative date) | 2077-04-30..2077-10-30 | 2077-10-30 | unknown |  | tenant_notice_check |
| PUSH-01 | BOOKMARK | ORS 456.260(1); OAR 813-115-0030 (verify) | 2060-01-01..2060-07-01 | 2060-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | BOOKMARK | SB 973 (2025); ORS 456.259 (verify operative date) | 2060-01-01..2060-07-01 | 2060-07-01 | unknown |  | tenant_notice_check |
| HAP-01 | ESTATES PLAZA | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2040-12-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | ESTATES PLAZA | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2041-09-02 | renewal_request_status=unknown |  |  |
| HAP-01 | MARLA MANOR | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2039-03-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | MARLA MANOR | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2039-12-02 | renewal_request_status=unknown |  |  |
| HAP-01 | CARITAS VILLA | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2037-03-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | CARITAS VILLA | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2037-12-01 | renewal_request_status=unknown |  |  |
| PUSH-01 | Ava II | ORS 456.260(1); OAR 813-115-0030 (verify) | 2056-09-03..2057-03-03 | 2057-03-03 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Ava II | SB 973 (2025); ORS 456.259 (verify operative date) | 2056-09-03..2057-03-03 | 2057-03-03 | unknown |  | tenant_notice_check |
| HAP-01 | POWELL VISTA MANOR | 42 U.S.C. 1437f(c)(8); 24 CFR 402.8 (verify) | .. | 2039-05-31 | renewal_request_status=unknown | Verify — CA Log | confirm renewal request / opt-out notice at CA |
| HAP-02 | POWELL VISTA MANOR | Section 8 Renewal Policy Guide ch. 11 (verify) | .. | 2040-02-01 | renewal_request_status=unknown |  |  |
| PUSH-01 | Merlo Station Apts II | ORS 456.260(1); OAR 813-115-0030 (verify) | 2065-01-01..2065-07-01 | 2065-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Merlo Station Apts II | SB 973 (2025); ORS 456.259 (verify operative date) | 2065-01-01..2065-07-01 | 2065-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | North Plains Senior Plaza (aka Kent Apt/Fifth Ave) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2053-10-16..2054-04-16 | 2054-04-16 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | North Plains Senior Plaza (aka Kent Apt/Fifth Ave) | SB 973 (2025); ORS 456.259 (verify operative date) | 2053-10-16..2054-04-16 | 2054-04-16 | unknown |  | tenant_notice_check |
| PUSH-01 | Village at Washington Square | ORS 456.260(1); OAR 813-115-0030 (verify) | 2078-12-31..2079-06-30 | 2079-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Village at Washington Square | SB 973 (2025); ORS 456.259 (verify operative date) | 2078-12-31..2079-06-30 | 2079-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Carriage Place Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2039-01-01..2039-07-01 | 2039-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Carriage Place Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2039-01-01..2039-07-01 | 2039-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Brentwood Oaks Senior Apartments (aka Tuality Park) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2041-01-01..2041-07-01 | 2041-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Brentwood Oaks Senior Apartments (aka Tuality Park) | SB 973 (2025); ORS 456.259 (verify operative date) | 2041-01-01..2041-07-01 | 2041-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Tualatin View Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2039-01-01..2039-07-01 | 2039-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Tualatin View Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2039-01-01..2039-07-01 | 2039-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | West Ridge Meadows Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2045-04-15..2045-10-15 | 2045-10-15 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | West Ridge Meadows Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2045-04-15..2045-10-15 | 2045-10-15 | unknown |  | tenant_notice_check |
| PUSH-01 | Willow Springs Apts (fka Willow Creek Commons) | ORS 456.260(1); OAR 813-115-0030 (verify) | 2044-01-01..2044-07-01 | 2044-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Willow Springs Apts (fka Willow Creek Commons) | SB 973 (2025); ORS 456.259 (verify operative date) | 2044-01-01..2044-07-01 | 2044-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Merlo Station Apts I | ORS 456.260(1); OAR 813-115-0030 (verify) | 2065-01-01..2065-07-01 | 2065-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Merlo Station Apts I | SB 973 (2025); ORS 456.259 (verify operative date) | 2065-01-01..2065-07-01 | 2065-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Covey Run Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2048-01-01..2048-07-01 | 2048-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Covey Run Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2048-01-01..2048-07-01 | 2048-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | Valfre at Avenida 26, The | ORS 456.260(1); OAR 813-115-0030 (verify) | 2049-12-31..2050-06-30 | 2050-06-30 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Valfre at Avenida 26, The | SB 973 (2025); ORS 456.259 (verify operative date) | 2049-12-31..2050-06-30 | 2050-06-30 | unknown |  | tenant_notice_check |
| PUSH-01 | Terrace Glen Apartments | ORS 456.260(1); OAR 813-115-0030 (verify) | 2051-01-01..2051-07-01 | 2051-07-01 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | Terrace Glen Apartments | SB 973 (2025); ORS 456.259 (verify operative date) | 2051-01-01..2051-07-01 | 2051-07-01 | unknown |  | tenant_notice_check |
| PUSH-01 | KAYBERN TERRACE | ORS 456.260(1); OAR 813-115-0030 (verify) | 2034-11-26..2035-05-26 | 2035-05-26 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | KAYBERN TERRACE | SB 973 (2025); ORS 456.259 (verify operative date) | 2034-11-26..2035-05-26 | 2035-05-26 | unknown |  | tenant_notice_check |
| PUSH-01 | ELM PARK I | ORS 456.260(1); OAR 813-115-0030 (verify) | 2037-10-14..2038-04-14 | 2038-04-14 | not yet due | notice_status=unknown; window_state=not_open |  |
| PUSH-03 | ELM PARK I | SB 973 (2025); ORS 456.259 (verify operative date) | 2037-10-14..2038-04-14 | 2038-04-14 | unknown |  | tenant_notice_check |

1796 checklist rows in notice_compliance_queue.csv; no demand or records letter is generated before the statutory trigger it cites.

## Mandate Fit

- Products open as of 2026-10-04: lihtc_4pct_gap, zero_pct_rehab_recap, metro_bond_acquisition, noah_ohaf_bridge, usda_mpr; eligible leads 542; ineligible 226 (top reasons: usda_mpr: program not eligible x226; ohcs_preservation_nofa: program not eligible x221; lihtc_4pct_gap: program not eligible x221)
- The mandate filter is route-level: an ineligible row loses nofa_offer only and keeps every other route (never an exclusion, never a multiplier).

## Status Flips Since Last Run

No prior run supplied (prior_run); status flips need a prior leads_scored.csv.

## Pipeline, not scored

- 46 rows Status = In Development -> map-progress-monitor / map-troubled-project-escalator: Cascade Creek, fka Bornstedt Village; Hillside Park - Building C; Marylhurst Commons (Greenbrae); Good Shepherd Village; Estacada Apartments II; Las Flores Apartments fka Maple Apts; 85 Stories Group 7 (4 Scattered-Sites); Powellhurst Apartments

## Data Gaps and Verification Queue

- Stale contract dates: 33 (request current HAP contract / TRACS; never OVERDUE, never lost)
- Notice log unknown after due date: 18 (Verify — Notice Log)
- CA log unknown after opt-out notice deadline: 5 (Verify — CA Log)
- Book join gaps: 0 (Verify — Book Join; suggested crosswalk rows in book_join_gaps.csv); book rows unmatched to the inventory: 4
- Documents to request from our own file room: 112 (feeds critical-dates-tracker)
- SOS worklist: 54 organizations
- Rejected / conflicting dates: 0 rejected;  verify flags on the OHCS adapter

## Assumptions, Statutory Cites and Limits

- Every statutory cite in this run is verified_live: false; confirm current text before sending any letter (ORS 456.265 reads 'sanctions against withdrawing owner prohibited' — PuSH enforcement is never a fine)
- UPB-at-risk rule: upb where any owner-cliff PRESSURE event <= 36 mo OR covenant_status in {watch, default} OR coterminous_senior_cliff; Board_Totals band on owner_cliff_band, the queue sorts on action_band = min(agency act-by, owner cliff)
- Equity overlay: placeholder (no tract / district list) -> high_displacement_tract / underserved_district modifiers score 0 unless a tract / district list is supplied
- Board headline window: owner_cliff_months_out <= 36 (CRITICAL / URGENT / APPROACHING) plus OVERDUE rows whose restriction or contract date already passed with no termination evidence (verify cases); STALE_CONTRACT_DATE HAP rows are excluded and reported on their own Board_Totals row
- Market params as of 2026-10-04; cap_rate_affordable 0.0675 (verify); senior_dscr_floor 1.15; recap_loan_rate 0.0
- Proxy-only leads capped at PLAN; no inferred maturities (PROXY mini-perm dates excluded unless include_proxies); the agency's own ledger is RECORDED
- A/B/C tiers never appear; queue bands are ESCALATE / ACT / PLAN / WATCH / EXCLUDED; `none` = monitoring, `excluded` names its exclusion_reason
- Sources not verified live: ohcs_oahi, ohcs_push_forecast, hud_mf_assist_sec8, hud_lihtc_db, hud_reac, usda_mfh_exit, nhpd, multco_records, oregon_sos_registry
