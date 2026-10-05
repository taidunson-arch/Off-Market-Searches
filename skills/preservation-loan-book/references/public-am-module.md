# Module: Public-Agency Preservation and Loan-Book Asset Management (`affordable_public_am`)

The one module of `preservation-loan-book`. It replaces off-market-deal-finder v2's `affordable-regulated.md`: the same events, dates, bases and derivations, read from the seat of the lender, grantor or qualified purchaser instead of the acquirer. Shared vocabulary is `pipeline-contract.md`; recap arithmetic is `recap-math.md`; the canonical weights are `scoring/affordable_public_am.json` (Section 5 reproduces them and must match). Oregon is the worked example; `sources/federal/` generalizes it.

## Contents

1. Scope and the two universes
2. Signal catalog
3. Event derivation rules
4. Restricted NOI for recap sizing
5. Scoring rubric
6. Sponsor capacity and intervention owner
7. Lead-card additions
8. Pro tips (inverted)
9. Refresh cadence
10. Known gaps

---

## 1. Scope and the two universes

In scope: any rental property with an active affordability restriction or subsidy that the agency holds, administers, regulates or could purchase under a preservation statute: LIHTC (9% / 4%) in the compliance or extended-use period, project-based Section 8 (HAP, RAC) and PRAC / PAC, PBV contracts the PHA administers, HUD-insured or HUD-held debt with a use agreement (221(d)(3) BMIR, 236, 202 / 811, 223(f) with LIHTC), USDA 514 / 515, HOME and CDBG affordability periods, HTF, state soft-loan programs (Oregon: OAHTC, GHAP, HDGP, LIFT, HTF, Other OHCS), local regulatory agreements (PHB loans and the City's 60-year covenant, TIF / URA, levy), and PHA-owned assets. Classes 1-2 of v2 (SFR distress, market-rate maturity hunting) are off; the optional NOAH watch (`noah-watch.md`) is a separate module enabled only by flag.

**Two universes, one merge** (`build_universe.py`):

| universe | spine | what is scored | output |
|---|---|---|---|
| `our_book` — loans and grants we made, assets we own, contracts we administer | the agency servicing / grant extract (`servicing-extract.md`), RECORDED | covenant end, our maturity, recapture window, REAC / findings, occupancy, sponsor, and whether a senior HUD / HAP cliff lands in the same window | Book_Watchlist for AM officers (`servicing_watch`, `recap_committee`; healthy loans `none` / Monitoring) |
| `universe_not_held` — inventory we do not hold | OHCS / HUD / NHPD inventory minus our book | opt-out, QC, extended-use end, PuSH notice silence, for-profit GP Year 15, stacking | Preservation_Queue: NOFA targeting and statutory-notice enforcement, including properties we might never finance because a mission GP is already recapping (labeled `recap_status`, never excluded) |

A property in both is `our_book` with `in_inventory = true`. `Status == In Development` rows are EXCLUDED and listed under "Pipeline, not scored" with a pointer to `map-progress-monitor` / `map-troubled-project-escalator`; a construction loan enters this module when its close-out memo moves it to the servicing book. Housing authority and government owners are never capped or routed as non-events: for `pha_am` they are the user (`self_owned`); for every other profile they are mission sponsors and partners.

Horizon: 10 years for both DEBT and REGULATORY families (the board's 10-year list); urgency bands in months (OVERDUE / CRITICAL / URGENT / APPROACHING / MONITOR / SCHEDULED / BEYOND).

## 2. Signal catalog

Every row keeps v2's source and field notes; the points rule is rewritten to the agency rubric (Section 5). `verified_live` is true only for the OHCS CSV on disk and the agency's own extract.

| signal | event_type | family | source (adapter) | access | window | basis | points rule (agency) | agency owner |
|---|---|---|---|---|---|---|---|---|
| Agency servicing / grant ledger: our maturities, affordability periods, recapture, covenant status, notice and QC logs | AGENCY_LOAN_MATURITY, AFFORDABILITY_PERIOD_END, GRANT_RECAPTURE_END, SHARED_APPRECIATION_DUE, COVENANT_DEFAULT, NONCOMPLIANCE_FINDING, PRESERVATION_NOTICE_RECEIVED, QC_ELIGIBILITY (requested), THIRD_PARTY_OFFER_RECEIVED, INSPECTION_DUE, QC_RESPONSE_DUE, ROFR_MATCH_DEADLINE, RECORDS_REQUEST_DUE | DEBT / REGULATORY / OPERATING / AGENCY_DEADLINE | the agency's loan and grant system export (`ingest_servicing_extract.py`); run first | manual | 0-120 mo | RECORDED | our_capital_at_risk: default 15, recapture trigger 15, maturity <= 36 mo 12, 36-60 6, 60-120 3, our affordability end <= 36 10, recapture end <= 36 8, shared appreciation 6, covenant watch 6; coterminous senior cliff +3; missing expected join -> 0 + WATCH, never a guessed balance | am_officer; compliance_officer |
| State HFA inventory regulatory expirations (Oregon OAHI) | LIHTC_EXTENDED_USE_END, SOFT_PROGRAM_END, HAP_EXPIRATION (0.70, program stamped, detail term_unknown_annual_assumed), USDA_515_MATURITY, REGULATORY_LATEST_END; DERIVED LIHTC_COMPLIANCE_END; PROXY LOAN_MATURITY opt-in only | REGULATORY / DEBT | OHCS Oregon Affordable Housing Inventory CSV (`ohcs_inventory_targets.py`); also PSH_Units, Rental_Assistance_Count, bedroom mix, OHCS Funded?, Scattered/Single Site, Property Type for units_at_risk and vulnerability_flags | free-public | 0-120 mo | REPORTED; DERIVED; PROXY | restriction_hap_qc_clock bands; units_households_at_risk reads units from this file; `OHCS Funded?` is the hfa expected_book_flag | push_program_manager; nofa_program_manager |
| LIHTC Year 15 (compliance period end) | LIHTC_COMPLIANCE_END | REGULATORY | OHCS Compliance_Start_Date + 15y (shipped); HUD LIHTC DB YR_PIS + 14 (future) | free-public | 36 mo before to 24 mo after | DERIVED (0.80) | 12-36 mo out 14 for ANY owner; > 24 mo past with no transfer 8; sponsor_capacity reads the owner type separately | compliance_officer |
| LIHTC Year 30 / extended-use end | LIHTC_EXTENDED_USE_END | REGULATORY | OHCS LIHTC_4/9_Expiration_Date; recorded REUA / LURA from the agency's own file first | free-public / agency file | <= 36 mo 20; 36-60 12 | REPORTED / RECORDED | restriction_hap_qc_clock; withdrawal anchor for PuSH | push_program_manager |
| Qualified contract request / lapse / waiver | QC_ELIGIBILITY (requested / lapsed_decontrol), QC_REQUEST_INELIGIBLE, QC_RESPONSE_DUE | REGULATORY / AGENCY_DEADLINE | the HFA's own QC log (servicing `qc_request_complete_date`, `qc_waived`); the recorded REUA waiver clause; `sources/federal/qc-policy-by-state.md` | agency file | one-year agency period | RECORDED | declared_intent: requested 13, lapsed 15; clock: QC_RESPONSE_DUE <= 12 mo +4; `eligible` from vintage alone never scores; qc_admin only for the profile that administers QC | compliance_officer |
| HAP / RAC / PRAC / PAC contract expiration, renewal status and renewal option | HAP_EXPIRATION, HAP_OPTOUT_NOTICE_DEADLINE, HAP_OPTOUT_PACKAGE_DUE | REGULATORY / AGENCY_DEADLINE | HUD MF Assistance & Sec 8 (`normalize_hud_sec8.py`; overrides OHCS; is_hud_administered -> PBCA flag; hap_renewal_request_status / option when the CA supplies them); OHCS HUD_MF_Expiration_Date | free-public / CA log | HAP <= 24 mo 18 (x0.70 / 0.90); 24-60 10; stale past date 6; PRAC/PAC <= 24 10 | REPORTED (0.70 / 0.90) | optout_response only for HAP / RAC / PBV; PRAC risk is appropriation and sponsor capacity; a past date with no termination evidence is STALE_CONTRACT_DATE | pbca_liaison |
| Section 8 opt-out / renewal-intent notice | PRESERVATION_NOTICE_RECEIVED (hap_optout) | REGULATORY | the CA's own opt-out log (RECORDED when the agency is the PBCA); PBCA records request otherwise | agency file / manual | 12 mo before expiration | RECORDED | declared_intent 15; route optout_response | pbca_liaison |
| Oregon PuSH owner notices, 10-Year Expiration Forecast, Preservation Dashboard | PRESERVATION_NOTICE_WINDOW (two windows), PUSH_WINDOW_PREP, PUSH_FIRST_NOTICE_DUE, PUSH_SECOND_NOTICE_DUE, TENANT_NOTICE_WINDOW, PRESERVATION_NOTICE_RECEIVED, NOTICE_COMPLIANCE_BREACH; notice_status | REGULATORY / AGENCY_DEADLINE | the agency's PuSH-CP notice log (hfa) or received-notice file (local government) as `notice_log_status`; OHCS 10-Year Forecast (`normalize_ohcs_forecast.py`, `--prior` writes status flips) | agency file / free-public | windows 36-30 and 30-24 mo before the withdrawal anchor | RECORDED (log) / DERIVED (windows, breach) | window open: 0 points, signal push_window_open_prep, prep only; due passed + not_received_confirmed: NOTICE_COMPLIANCE_BREACH 15, demand letter, designee appointment; due passed + unknown: 6 + Verify — Notice Log | push_program_manager |
| Recorded Notice of ROFR / designee agreement / third-party offer | ROFR_RECORDED, THIRD_PARTY_OFFER_RECEIVED, ROFR_MATCH_DEADLINE | REGULATORY / AGENCY_DEADLINE | the agency's own recording and the owner's certified mailing (servicing `third_party_offer_mailed_date`); recorder index | agency file / free-public | 30 days from mailing | RECORDED | declared_intent: offer received 15, our ROFR recorded 8; route designee_rofr | legal_counsel |
| HUD-insured / HUD-held loan maturity and prepayment window | LOAN_MATURITY (senior), HUD_DIRECT_LOAN_MATURITY, PREPAY_WINDOW_OPEN, REFINANCE_CLOSED | DEBT | HUD FHASL Active + Terminated (`normalize_hud_insured.py`; writes senior_lien_type hud_fha, senior_upb, senior_maturity) | free-public | <= 36 mo 16 (regulatory leg) | RECORDED | restriction_hap_qc_clock hud_direct_le_36 16; coterminous_senior_cliff +3 when within 24 mo of our maturity; route recap_committee when in book | hud_mf_asset_manager; am_officer |
| USDA 514 / 515 maturity, prepayment eligibility, prepayment request | USDA_515_MATURITY, USDA_515_PREPAY_ELIGIBLE, USDA_EXIT_PROJECTED, USDA_PREPAY_REQUEST_RECEIVED, USDA_PUBLIC_BODY_OFFER_WINDOW_END | DEBT / REGULATORY / AGENCY_DEADLINE | USDA MFH exit data (future adapter); OHCS USDA_RD_Expiration_Date; RD notice to the agency as interested party | free-public / RD | <= 36 mo 16; prepay eligible 12; request received 16 / 13 | RECORDED / REPORTED | the agency is an eligible public-body purchaser (7 CFR 3560.659, verify); route designee_rofr / nofa_offer | rd_state_office; nofa_program_manager |
| HOME / CDBG / HTF affordability periods, recapture, inspections | AFFORDABILITY_PERIOD_END, GRANT_RECAPTURE_END, RECAPTURE_TRIGGER, INSPECTION_DUE | REGULATORY / AGENCY_DEADLINE | the PJ's own HOME / CDBG records (servicing extract book_kind grant); IDIS reports; OHCS HOME dates (REPORTED, mostly paired with LIHTC) | agency file | 24 CFR 92.252(e) periods 5 / 10 / 15 / 20 yrs; HTF 30; CDBG 5 after closeout | RECORDED / DERIVED | clock affordability_period_end_le_36 14; capital affordability_period_end_ours_le_36 10, recapture_end 8; recapture_exposure -> public_grant_at_risk; cdbg_home gets INSPECTION_DUE in place of PuSH enforcement | cpd_program_manager |
| REAC / NSPIRE inspection scores, compliance findings, 8823s | REAC_SCORE, NONCOMPLIANCE_FINDING | OPERATING | HUD inspection export (`normalize_reac_scores.py`, REPORTED); the agency's own monitoring file (RECORDED) | free-public / agency file | within 12 mo of a failing score | REPORTED / RECORDED | physical: <= 30 10 (DEC referral), < 60 10 (blocks MU2M), 60-79 or decline 6, open finding 8 | compliance_officer |
| Property-tax exemption lost, delinquency, foreclosure list, code cases, liens | TAX_EXEMPTION_LOST, TAX_DELINQUENT_YEARS, TAX_FORECLOSURE_LIST, CODE_CASE_OPEN, DANGEROUS_BUILDING, MECHANICS_LIEN, JUDGMENT_LIEN | OPERATING / TAX_LIEN / PHYSICAL | assessor roll, county list, city open-case lists (manual files) | free-public / manual | annual | RECORDED / REPORTED | physical: 6 / 3-6 / 10 / 4 / 10 / 3 — troubled-asset AM, covenant extinguishment risk | am_officer |
| Ownership structure: for-profit GP at Year 15, LP transfer to aggregator, GP / agent change, dissolution, APPS flag, sponsor cliff count | owner_type; MANAGER_CHANGE, REGISTERED_AGENT_CHANGE, ENTITY_ADMIN_DISSOLVED; apps_flag; sponsor_cliff_count | OWNERSHIP | Oregon SOS registry (worklist); LURA from the agency file; OHCS Developer Name; HUD 2530 / APPS status on request | free-public / agency | Year 15 +/- 3 y | RECORDED | sponsor_capacity: mission sponsor 6, self-owned 6, for-profit GP at Year 15 6, LP / GP change 8, dissolved 6, APPS 4, RAD / Section 18 4; out-of-state (for-profit only) +4, 2+ cliffs +4, agent change +2; nothing subtracts | compliance_officer; legal_counsel |
| Book-risk hard distress on a regulated asset | JUDICIAL_FORECLOSURE_FILED, LIS_PENDENS, RECEIVER_APPOINTED, BANKRUPTCY_FILED, UCC_MEZZ_PLEDGE, UCC_ART9_SALE | HARD_DISTRESS | court index, recorder, PACER, SOS UCC (manual) | free-public / paid | on filing | RECORDED | route recap_committee (workout; HOME covenant may terminate on foreclosure, 24 CFR 92.252, verify); BANKRUPTCY_FILED -> compliance gate counsel_only | legal_counsel; am_officer |
| Local regulatory layers (Metro RLIS, PHB portfolio), stabilization awards, equity overlays | LOCAL_REG / PHB_LOAN / TIF program tags; COVENANT_END; STABILIZATION_AWARD; high_displacement_tract, underserved_district | REGULATORY / OPERATING | city / county extracts; pack `equity_overlays.yaml` | free-registration / agency | | REPORTED / RECORDED | clock covenant_end_le_36 14; stacking overlay +2 / +2 (0 when the overlay file is absent) | nofa_program_manager; board_liaison |
| Quality / negative signals | status, rehab_year, recap_status | n/a | OHCS fields; forecast Preserved / Resyndicated / Extended; the agency's application pipeline | | | | exclude In Development; recent_rehab -5 in physical only; recap_status under_application / closed x0.5 on clock and declared intent (RECORDED / REPORTED evidence only); proxy-only cap PLAN | |

## 3. Event derivation rules

```
OHCS OAHI (declared formats; sources/oregon-portland/dataset-schemas.yaml) — verbatim from v2:
  Financial_Closing_Date        '%d/%m/%Y'  (day-first: 222 of 298 values have first field > 12, zero have second > 12)
  Compliance_Start_Date, every *_Expiration_Date, LATEST_Expiration_Date   '%m/%d/%Y'
  USDA_RD_Expiration_Date       '%Y %b %d %I:%M:%S %p'   e.g. '2038 Nov 17 12:00:00 AM'
  LATEST_Expiration_Date        recompute = max(components) when blank (554 rows); equals max in 1,263 of 1,265 populated rows;
                                exceptions Casa Sonada 4, Riverside Terrace -> 'Verify — Conflicting Sources', not rejected

  LIHTC_EXTENDED_USE_END        = LIHTC_9_Expiration_Date / LIHTC_4_Expiration_Date (REPORTED; program tag per column)
  SOFT_PROGRAM_END              = each HOME/OAHTC/GHAP/HDGP/LIFT/HTF/Other_OHCS date (REPORTED; program per column) -- affordability period end, not a note maturity
  HAP_EXPIRATION                = HUD_MF_Expiration_Date (REPORTED, confidence 0.70); program = HUD_CONTRACT_TO_PROGRAM[HUD Contract];
                                  detail term_unknown_annual_assumed when OHCS is the only source; replaced by HUD Sec 8 tracs_overall_expiration_date when present;
                                  a date already past with no termination evidence -> status STALE_CONTRACT_DATE (Section 4 of pipeline-contract)
  USDA_515_MATURITY             = USDA_RD_Expiration_Date (REPORTED); replaced by USDA exit data when present
  REGULATORY_LATEST_END         = LATEST_Expiration_Date (REPORTED)
  LIHTC_COMPLIANCE_END          = Compliance_Start_Date + 15 y (DERIVED, window +12 mo; flag '+15 election possible'; only when programs contain LIHTC)
  LOAN_MATURITY (PROXY)         = Financial_Closing_Date + 15 y (17 y when LIHTC_4), window +/-36 mo; OPT-IN ONLY (--include-proxies); dropped when a RECORDED AGENCY_LOAN_MATURITY exists
  units_at_risk inputs          = Total Units, Market_Rate_Units, Rental_Assistance_Count + HUD Contract, PSH_Units, Total_3_BR_Units + Total_4Plus_BR_Units,
                                  Property Type (Elderly*/Disabled*/Veteran/SRO -> vulnerability_flags), OHCS Funded? (-> ohcs_funded), Scattered/Single Site (-> site_type)

Agency servicing extract (servicing-extract.md Section 4): every event source = agency_servicing, basis from the basis column (default RECORDED),
  detail = <id_kind>=<id>, event_id = {pid}:{etype}:{id}:{date}.
  AGENCY_LOAN_MATURITY = maturity ; AFFORDABILITY_PERIOD_END = affordability_end (program carried) ; GRANT_RECAPTURE_END = recapture_end ;
  HAP_EXPIRATION (PBV/HAP, 0.90) = contract_expiration ; COVENANT_DEFAULT = covenant_status default (dated as_of) ; SHARED_APPRECIATION_DUE ;
  QC_ELIGIBILITY requested + QC_RESPONSE_DUE (+1 y) = qc_request_complete_date with qc_waived != true ; QC_REQUEST_INELIGIBLE = qc_waived true ;
  THIRD_PARTY_OFFER_RECEIVED + ROFR_MATCH_DEADLINE (+30 d) = third_party_offer_mailed_date ; PRESERVATION_NOTICE_RECEIVED + RECORDS_REQUEST_DUE (+10 d) = notice_log_status received ;
  USDA_PREPAY_REQUEST_RECEIVED + USDA_PUBLIC_BODY_OFFER_WINDOW_END (+180 d) ; RAD_CHAP ; SECTION_18_APPLICATION ; NONCOMPLIANCE_FINDING ; REAC_SCORE (RECORDED) ;
  INSPECTION_DUE = last_inspection_date + cadence ; LOAN_MATURITY (REPORTED, detail lender_type=<senior_lien_type>) = senior_maturity

HUD Sec 8 (normalize_hud_sec8.py):
  HAP_EXPIRATION                = tracs_overall_expiration_date ; detail short_renewal_pattern when (overall - effective) <= 5 y repeatedly ;
                                  annual_renewal when term <= 1 y ; mahra_20yr_recent when a 20-y term started within 24 mo ; overrides the OHCS date
  hap_units_at_risk             = assisted_units_count (program HAP/RAC) ; prac_units_at_risk (PRAC/PAC)
  is_hud_administered           -> pbca flag for the optout_response route ; hap_renewal_request_status / hap_renewal_option when the CA supplies them
  no owner_phone is written (pii-and-sunshine.md)

HUD FHASL (normalize_hud_insured.py):
  LOAN_MATURITY                 = Maturity Date (RECORDED) ; HUD_DIRECT_LOAN_MATURITY when SOA in {236, 221(d)(3), 202} ; detail 236_irp / no_hap_overlay
  PREPAY_WINDOW_OPEN            = Final Endorsement Date + 10 y (DERIVED, +/-6 mo)
  REFINANCE_CLOSED / SUPPRESS_UNTIL from Terminated rows matched on digits-only HUD Project Number
  senior_lien_type hud_fha, senior_upb, senior_maturity written for the coterminous_senior_cliff test ; no refi test, no assumable flag

Oregon PuSH and the agency calendar (agency-calendar.md; ORS 456.250-.265, OAR 813-115 -- statute text NOT read in this build):
  withdrawal_anchor_date        = max of restriction-type ends only (LIHTC_EXTENDED_USE_END, SOFT_PROGRAM_END, AFFORDABILITY_PERIOD_END, COVENANT_END, USDA_515_MATURITY, HUD use-agreement end);
                                  HAP/PRAC/PAC only with a non-renewal signal ; push_anchor_source recorded
  PRESERVATION_NOTICE_WINDOW    = [anchor - 36, anchor - 30] (push_first_window) and [anchor - 30, anchor - 24] (push_second_window) ; DERIVED ; units >= 5 and PuSH-covered programs
  PUSH_WINDOW_PREP = anchor - 36 mo ; PUSH_FIRST_NOTICE_DUE = anchor - 30 mo ; PUSH_SECOND_NOTICE_DUE = anchor - 24 mo ; TENANT_NOTICE_WINDOW = anchor - 36..-30 (SB 973, operative date per pack)
  NOTICE_COMPLIANCE_BREACH      = PUSH_FIRST_NOTICE_DUE passed and notice_status = not_received_confirmed (DERIVED; event_date = due date)
  RECORDS_REQUEST_DUE           = PRESERVATION_NOTICE_RECEIVED + 10 d (never before a notice) ; RECORDS_RESPONSE_DUE = request + 30 d
  ROFR_MATCH_DEADLINE           = third_party_offer_mailed_date + 30 d ; QC_RESPONSE_DUE = qc_request_complete_date + 1 y
  HAP_OPTOUT_NOTICE_DEADLINE    = HAP_EXPIRATION - 12 mo ; HAP_OPTOUT_PACKAGE_DUE = HAP_EXPIRATION - 120 d (HAP/RAC/PBV, FUTURE only, never from a stale date)
```

Validation: every REGULATORY event >= Compliance_Start_Date when present (else `Verify — Conflicting Sources`); Compliance_Start_Date within 36 months after Financial_Closing_Date when both present; month <= 12 after parsing; year 1960-2100; exclude In Development; servicing enums validated; servicing required columns by `book_kind`.

## 4. Restricted NOI for recap sizing

Restricted NOI (`recap-math.md` Section 2) is computed only when the pack's `rent-limits.json` holds current MTSP max rents; otherwise `est_restricted_noi` is blank with `Missing Source — Request Document` (rent roll / operating statement from the agency's own file). It is used for one purpose: sizing a recast, 0% recap or resyndication gap on an `our_book` property with `recap_status` announced / under_application (`recap_gap`, ESTIMATED, +/- 15%), and framing the supportable senior debt handed to `sizing-lihtc-permanent-debt` as before / after recast scenarios. There is no market value, no conversion scenario, no refinance test, no LTV and no equity cushion anywhere in the pack. A QC price band exists only inside the `qc_marketing_plan` memo.

## 5. Scoring rubric

Canonical: `scoring/affordable_public_am.json` (version 1.0; `shared_adjustments.json` for multipliers, queue bands, caps, decay, route precedence). Same events and basis multipliers as v2; different weights and readings. Empty evidence still scores 0. Basis arithmetic (one rule, mirrored in `shared_adjustments.governing_event_rule` and `pipeline-contract.md` Section 11): points = (base-band take + modifiers, capped at the weight) x basis multiplier x post multipliers; the basis multiplier is the minimum across the BASE bands that scored (governing owner-cliff event for `basis_from: governing_event`), modifiers never move it, and an event's confidence (< 1) scales every band or modifier that event matched. Powell Plaza I clock: (18 x 0.70 + 2 x 0.70 + 3) x 0.90 = 15.3 of 20.

| factor | weight | rule |
|---|---|---|
| Units and households at risk | 25 | restricted or HAP units inside the event window (governing owner cliff within -12..60 months; beyond 60 months 0 while units still appear in Board_Totals): 1-4 units 3, 5-19 8, 20-49 14, 50-99 20, 100+ 25; modifiers +3 PSH units > 0, +2 elderly / disabled property type, +2 3BR+ share >= 25%, +3 HAP share >= 50%; basis multiplier borrowed from the governing event; cap 25 |
| Restriction / HAP / QC clock | 20 | extended-use end <= 36 mo 20, 36-60 12; Year 15 12-36 mo 14 for ANY owner, > 24 mo past with no transfer 8; HAP / RAC / PBV <= 24 mo 18 (x0.70 annual / unknown, x0.90 MAHRA or agency PBV), 24-60 10, stale past date (<= 12 mo) 6; PRAC / PAC <= 24 10; HUD direct maturity <= 36 16; USDA maturity <= 36 16, prepay eligible 12, prepay request received 16; affordability period end <= 36 14; covenant end <= 36 14; soft program end <= 36 10, 36-60 5; latest end <= 36 10; modifiers -5 fresh 20-year MAHRA, +2 annual renewal, +4 PUSH_FIRST_NOTICE_DUE <= 6 mo with no notice, +4 QC_RESPONSE_DUE <= 12 mo, +3 HAP_OPTOUT_PACKAGE_DUE <= 6 mo; x0.5 recap_status under_application / closed; take max; cap 20; x basis |
| Declared intent vs silence | 15 | PuSH first or second notice received 15; opt-out notice 15; third-party offer mailed 15; NOTICE_COMPLIANCE_BREACH (due passed, not_received_confirmed) 15; QC lapsed 15; QC requested (RECORDED) 13; USDA prepayment request 13; due passed with notice_status unknown 6 + Verify — Notice Log; our ROFR recorded 8; inside the first-notice window 0 with signal push_window_open_prep; x0.5 recap_status; cap 15 |
| Our capital at risk | 15 | requires book_match matched / self_owned (unmatched_expected -> 0 + factor WATCH + Verify — Book Join; not_in_extract / not_in_book / book_absent -> n/a): covenant default 15; recapture trigger 15; our maturity <= 36 mo 12, 36-60 6, 60-120 3; our affordability period end <= 36 10; grant recapture end <= 36 8; shared appreciation due <= 36 6; covenant watch 6; owned-asset cliff <= 36 8; +3 coterminous senior cliff; cap 15; x basis |
| Physical / REAC / occupancy | 10 | REAC <= 30 10, 31-59 10, 60-79 or 15-point decline 6; open finding / 8823 8; dangerous building 10; tax foreclosure list 10; occupancy drop 6; exemption lost 6; tax delinquent 2+ y 6, 1 y 3; code case 4; mechanics / judgment lien 3; management change 2; -5 rehab within 5 years (the only place this penalty lives); take max; cap 10 |
| Sponsor capacity | 10 | mission sponsor (nonprofit / nonprofit GP / PHA / government) 6; self-owned 6; for-profit or Limited Dividend GP at Year 15 (-24..36 mo) 6; LP transfer / GP or manager change 8; entity dissolved 6; APPS flag 4; RAD / Section 18 in progress 4; modifiers +4 out-of-state (for-profit GP / institutional only, from the extract or SOS worklist), +4 sponsor with 2+ cliffs in 36 mo, +2 registered agent change; unknown owner type 0 + signal; floor 0; nothing subtracts; cap 10 |
| Stacking / geography equity | 5 | 2 restrictions ending in the same 24 mo 3; 3+ 5; HAP and extended use in the same 24 mo 4; +2 high-displacement tract; +2 under-served district (0 when `equity_overlays.yaml` absent); cap 5 |

Queue bands: ESCALATE >= 70, ACT 50-69, PLAN 30-49, WATCH < 30 with a dated PRESSURE event, EXCLUDED otherwise. Caps: proxy-only -> PLAN. Routes and precedence: `pipeline-contract.md` Section 12; mandate hard filter on nofa_offer only.

## 6. Sponsor capacity and intervention owner

| owner_type | reading (public-interest) | default route | intervention owner at the agency | notice address order |
|---|---|---|---|---|
| lihtc_partnership_forprofit_gp (incl. Limited Dividend) | Year-15 / Year-30 exit is the most likely; preservation risk, not a buy-side signal; LP may have traded to an aggregator | notice_compliance (prep -> demand when due passes); designee_rofr when a notice arrives; qc_admin (hfa) on a QC request | push_program_manager; compliance_officer | regulatory_agreement > hap_contract > sos_registered_agent |
| lihtc_partnership_nonprofit_gp / nonprofit | mission partner with ROFR standing (IRC 42(i)(7)) and recap capacity; needs TA and an award cohort | ta_sponsor; nofa_offer | nofa_program_manager; push_program_manager | regulatory_agreement > loan_docs |
| housing_authority / government (not self) | partner; RAD / Section 18 / mixed-finance recap; never a cap or a non-event | ta_sponsor; recap_committee when in book | nofa_program_manager; am_officer | agency file |
| self_owned (pha_am) | our own asset; levers are repositioning and recapitalization | recap_committee; servicing_watch | pha_development; am_officer | n/a |
| institutional (funds holding LP / fee interests) | aggregator posture; Year-15 litigation risk; out-of-state | notice_compliance; designee_rofr | legal_counsel; push_program_manager | sos_registered_agent (Verify — Notice Address) |
| HUD / USDA-assisted owner (overlay) | the agency is the contract administrator / AE counterpart or the eligible public body | optout_response; prac_renewal_coordination; usda_prepay_response; hud_legacy_response | pbca_liaison; hud_mf_asset_manager; rd_state_office | hap_contract |
| lender_reo_receiver | book risk; covenant may be extinguished at foreclosure | recap_committee (workout); compliance gate counsel_only when bankruptcy | legal_counsel; am_officer | counsel of record |
| individual owner (OHCS prints a few) | public record name, no contact detail; organization-level letter to the notice address in our file | per events | push_program_manager | regulatory_agreement / hap_contract only |
| unknown | 0 points, signal owner_type_unknown; SOS worklist | per events | compliance_officer | sos_registered_agent |

Sponsor resolution, organization grades and the SOS worklist: `sponsor-resolution.md`. Intervention drafts: `intervention-catalog.md`.

## 7. Lead-card additions

`Units at risk` (restricted, HAP, PRAC, other RA, PSH, units_basis, vulnerability_flags); `First agency act-by` (type, date, basis, months, agency owner, cite with verify note); `Owner cliff` (type, date, basis, source; next_expected_expiration for annual HAP); `Declared intent / notice status` (notice_status, tenant_notice_status, hap_renewal_request_status / option, recap_status, qc_status / qc_waived, rofr_recorded); `Our position` (ids, book_kind, upb, payment_type, maturity + basis, affordability_end, recapture exposure, covenant_status, am_officer, or "not in book" / "expected in book — join missing" / "book absent"); `Physical` (REAC, findings, code, tax); `Sponsor capacity` (owner_type, org, SOS status, agent change, sponsor_cliff_count); `Intervention` (catalog id, agency owner, cite + verify, owner vs tenant notice, notice address + source); `Evidence`; `Verify before acting`; `Handoffs ready`.

## 8. Pro tips (inverted from v2)

- **Year 15 is a decision point; Year 30 is the cliff.** Score Year 15 for any owner. The mission GP's ROFR and the for-profit GP's exit are both reasons for the agency to act: TA and a NOFA invitation for one, a notice audit and a recorded ROFR for the other.
- **A for-profit GP with an aggregator LP is the strongest preservation-risk signal**, not an acquisition signal. Check whether LP interests have traded (MANAGER_CHANGE, litigation dockets, 2C review of the LPA in your own file).
- **You are the qualified purchaser.** OHCS, the affected local government, or an OHCS designee perfects the ROFR in two steps: deliver the qualified purchaser's offer with notice of intent to record (on or after the owner's notice or anchor - 30 months, whichever is earlier), then record the Notice of ROFR no earlier than offer + 30 days (`ROFR_RECORDABLE_DATE`); the right expires 24 months after the withdrawal date. The owner must mail any third-party offer; run the 30-day match from the certified mailing date, not from when the letter crossed your desk, and the match must carry the affordability-preservation commitment (ORS 456.262-.263, OAR 813-115-0060/-0070; confirm current text post-SB 973 before quoting to an owner).
- **Silence inside a statutory window is a compliance case, not a weak signal — but only once the due date passes and your own log confirms no notice.** Inside the 36-30 month window the owner is not late; prepare. Absence in a dataset is never owner silence.
- **An annual HAP date in the past is a stale record, not a lost contract.** 33 of 130 metro HUD dates in the 2026-10-02 OHCS file are already past. Request the current HAP contract / TRACS expiration from the CA; never count a stale date in OVERDUE or `lost`.
- **HAP dates roll annually; PRAC is not an opt-out risk.** Weigh an annual HAP at 0.70 until the CA log or a notice confirms intent; PRAC / PAC risk is appropriation and sponsor capacity.
- **Request the LURA / REUA from your own file first.** The agency holds the regulatory agreement, the HAP contract and the note; the recorder image is the fallback, not the first move.
- **Parse OHCS dates with declared formats, never a heuristic.** Financial_Closing_Date is day-first; every other slash column is month-first; USDA is `YYYY Mon DD hh:mm:ss AM`.
- **LATEST is blank 30% of the time.** Recompute it as the max of components and flag the two known exceptions rather than rejecting them.
- **Never guess a balance.** An expected book row that did not join scores 0 on capital with a WATCH factor and a Book_Join_Gaps row; confirm the crosswalk and re-run.
- **Boards buy units, not lead scores.** The headline is properties / restricted units / HAP units / PSH units / public UPB with a cliff inside 36 months, banded on the owner cliff; the queue sorts on the agency's act-by date.
- **Present the qualified contract; you do not have to close it.** Presentment of a bona fide contract within the one-year period removes the exit permanently (OHCS draft QC procedure; verify).
- **236 maturities end the use agreement.** Decoupling (Notice H 2013-25) and 202 prepayment with a 20-year use agreement (H 2013-17) are recap tools, not risks, when a mission sponsor is in place.
- **USDA 515 makes the agency an eligible public-body purchaser** during the 180-day offer window after a prepayment request (7 CFR 3560.659, verify); pair MPR with 4% credits for the take-out.

## 9. Refresh cadence

| feed | cadence |
|---|---|
| agency servicing / grant extract | monthly (or on every ledger close); re-profile dates on a new export |
| agency notice log (PuSH-CP), QC log, CA opt-out / renewal log | on receipt; confirm at every run |
| OHCS OAHI | each release (key on Property Name + Address, not row order) |
| OHCS 10-Year Forecast / dashboard | quarterly diff (status flips) |
| HUD FHASL Active + Terminated | monthly |
| HUD MF Assistance & Sec 8 | monthly |
| HUD REAC / NSPIRE scores | per release (semiannual) |
| HUD LIHTC DB | annual |
| USDA MFH exit data | semiannual |
| NHPD | quarterly |
| recorder (LURA, ROFR notices, trust deeds, modifications) | on worklist; monthly for book properties |
| SOS (GP / manager / status / agent) | on worklist; quarterly for the sponsor map |
| assessor exemption codes / tax status | annual roll; semiannual tax |
| rent limits and HAP rents | annual (HUD income limits release) |
| book_crosswalk.csv | after every run (confirm fuzzy matches) |

## 10. Known gaps

- No real agency servicing extract existed in this build; the canonical schema is a design proposal and the fixture is synthetic. Confirm column names, date formats (`date_profile.py`) and the `book_kind` validation against the first real export.
- OHCS data quality: Owner Type blank in 1,039 of 1,819 rows (443 of 810 metro); County / City mixed case; `Portalnd`; Property Type `0` (25) and `ERROR: #N/A` (8); Financial_Closing_Date in only 298 rows; AMI buckets fail to reconcile to Total Units in 527 of 810 metro rows (hence `units_basis`); Market_Rate_Units > 0 in only 5 rows; 33 of 130 metro HUD dates already past (hence STALE_CONTRACT_DATE); 236 metro rows with a blank Owner Name are HUD-contract-only (owner from the HUD Sec 8 tape).
- OHCS publishes no discrete log of PuSH owner notices or Section 8 opt-out notices; for `hfa` the PuSH-CP log is internal and RECORDED, for every other profile it is a records request. The PBCA identity under HUD's 2024-2025 PBCA re-solicitation was not checked.
- ORS 456.260 exact notice language post-SB 973 (the rule summary reads "no sooner than 30 and at least 24 months"; the 36..30 row is an INTERNAL prep window with no statutory basis found, and `NOTICE_COMPLIANCE_BREACH` is a working label meaning "clock not started; designee available", not a breach finding), the (1)/(2) notice split, the ORS 456.262 two-step offer-then-record sequence and the 24-month ROFR duration (snippets; no source supports 36), the OAR 813-115 section map (0010 covered programs / 0030 notice / 0035 designee / 0050 records / 0060 ROFR recording / 0070 third-party offer; the 30-day records-response figure was not found), the SB 973 operative date nuance (operative 1/1/2026 vs restrictions ending on/after 2028-07-01) and ORS 456.265's title ("Sanctions against withdrawing property owner prohibited" — not penalties) were taken from snippets; read the statute before quoting a month to an owner.
- Whether a LIHTC extended-use agreement alone, or a HOME-only PJ loan with no OHCS contract, makes a property "publicly supported housing" under ORS 456.250 depends on OAR 813-115-0010 identifying those programs (unread). `PUSH_COVERED_PROGRAMS` includes both; with the pack parameter `push_program_coverage_verified` false such rows receive their PuSH window and clock points with `Verify — PuSH Coverage` rather than scoring silently — a 12-unit PJ HOME-only loan in the synthetic run is the case to check.
- Oregon QAP first year requiring a QC waiver (2016 vs earlier) is unconfirmed; `qc_waived` must come from the recorded REUA or the agency's QC log.
- Treas. Reg. 1.42-18 (adjusted investor equity COLA, "low-income portion") was not read; the QC price band stays ESTIMATED and memo-only.
- Section 8 Renewal Guide cites (120-day package ch. 11; Option 1B criteria; nonprofit exception ch. 15) came from secondary summaries; HOME 2025 final-rule dollar thresholds and the 92.252 foreclosure-termination paragraph numbering were not reproduced; NSPIRE DEC referral thresholds are from the pre-NSPIRE procedure; 7 CFR 3560 subpart N figures (30 / 180 days, 10 years) are from snippets; Section 250 timing (150-270 days) is from a notice summary.
- No OHCS, PHB or Home Forward asset-management, recast or subordination policy document was located; the recap gap and recast levers are generic conventions.
- No tract or council-district field exists in the OHCS CSV; `equity_overlays.yaml` is optional and Portland council districts need a point-in-polygon join deferred to a later build. OR legislative districts and county are the available jurisdiction keys.
- Every external source `verified_live=false` except the OHCS file on disk; re-verify URLs, field names and vintages before hard-coding them.
