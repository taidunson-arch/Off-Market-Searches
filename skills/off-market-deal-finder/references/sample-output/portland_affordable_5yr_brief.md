# Off-Market Targets — us-or-multnomah — affordable_regulated — maturity — as of 2026-10-04

## Run Summary

- as_of_date: 2026-10-04  |  geography_mode: metro_core  |  counties: 41051, 41067, 41005  |  buyer_profile: principal
- horizon_years (debt): 5  |  regulatory_horizon_years: 5  |  query_type: maturity
- files ingested: Oregon_Affordable_Housing_Inventory_20261002.csv (vintage 2026-10-02 from filename)
- dated events inside horizon: 152 on 141 properties (+117 helper deadlines not counted)
- **Basis breakdown (read this before the count): RECORDED 0 / REPORTED 114 / DERIVED 37 / ESTIMATED 0 / PROXY 1 / Suppressed 0 / Rejected 0 | helper deadlines 117 (notice arithmetic, LATEST duplicates; not counted above)**
- leads: 141  |  tiers: {'WATCH': 114, 'C': 17, 'EXCLUDED': 10}  |  routes: {'watch': 74, 'partnership_preservation': 40, 'acquisition': 17, 'excluded': 10}
- **maturity hits: 2 leads carry a dated maturity event; 139 regulatory-/other-family-only leads are shown as secondary.** A `maturity` query is not the same list as `all`; the secondary leads are kept because their owners face a dated event of another kind.
- Degraded run: no RECORDED dates. Every maturity is REPORTED/DERIVED/PROXY, so Tier A is out of reach until a RECORDED or declared-intent family arrives: HUD FHASL Active, HUD MF Assistance & Sec 8, the OHCS 10-Year Forecast (normalize_ohcs_forecast.py; field names unverified) or recorder images.
- Sources still verified_live=false (URL not fetched in this build; file-on-disk checks do not count): ohcs_oahi, ohcs_push_forecast, ohcs_hca_optout, hud_fhasl_active / hud_fhasl_terminated, hud_mf_assist_sec8, hud_lihtc_db, hud_reac, usda_mfh_exit, nhpd, multco_records, oregon_sos_registry

## Event Horizon

| family | RECORDED | REPORTED | DERIVED | ESTIMATED | PROXY |
|---|---|---|---|---|---|
| DEBT | 0 | 1 | 0 | 0 | 1 |
| REGULATORY | 0 | 113 | 37 | 0 | 0 |

Urgency: {'APPROACHING': 38, 'CRITICAL': 28, 'MONITOR': 61, 'URGENT': 25}  |  helper deadlines by type: {'HAP_OPTOUT_NOTICE_DEADLINE': 34, 'PRESERVATION_NOTICE_WINDOW': 26, 'REGULATORY_LATEST_END': 57}

## Top Targets


### Secondary: no dated maturity event, ranked on other families

### [#1] Village Garden Apartments — 15230 NE Sandy Boulevard, Portland  Tier [C] Score [42.5] Route [acquisition]
- Class / Units / Built / Rehab / Owner type: affordable_regulated / 35 / 1999 / - / lihtc_partnership_forprofit_gp
- First debt event: none in horizon
- First regulatory event: SOFT_PROGRAM_END 2029-05-15 [REPORTED] — 31.4 mo (OHCS OAHI p9yn-ftai 20261002)
- Capital stack: lender_type not in public record; balance not in public record [-]; value $6,387,115 (ppu_band (market avg $/unit; as-restricted value is usually lower))
- Refi screen: LTV n/a; dscr_refi n/a; gap n/a; cushion n/a
- Signals: hfa_inventory;push_window_open;extended_use_le_36;programs_2_same_24mo;forprofit_gp
- Decision maker: not in public record, GP managing member + syndicator asset manager, grade C — evidence: pending SOS registry resolution
- Outreach: Year-15 buyout / resyndication, LP exit funding; respect 42(i)(7) ROFR and QC mechanics via template lihtc_gp_year15; gates: dnc_scrub
- Verify before outreach: confirm LIHTC_EXTENDED_USE_END 2029-06-01 [REPORTED] via LURA / REUA; Missing Source — Request Document: rent roll / HFA rent limits
- Handoffs ready: see handoff/*.json

### [#2] CSP Lexington Apartments — 1125 SW 12th Avenue, Portland  Tier [C] Score [36.0] Route [acquisition]
- Class / Units / Built / Rehab / Owner type: affordable_regulated / 54 / 2013 / - / lihtc_partnership_forprofit_gp
- First debt event: none in horizon
- First regulatory event: LIHTC_COMPLIANCE_END 2027-12-19 [DERIVED] — 14.5 mo (OHCS OAHI p9yn-ftai 20261002)
- Capital stack: lender_type not in public record; balance not in public record [-]; value $9,854,406 (ppu_band (market avg $/unit; as-restricted value is usually lower))
- Refi screen: LTV n/a; dscr_refi n/a; gap n/a; cushion n/a
- Signals: hfa_inventory;hud_contract:HAP;year15_forprofit;programs_3plus_same_24mo;forprofit_gp
- Decision maker: not in public record, GP managing member + syndicator asset manager, grade C — evidence: pending SOS registry resolution
- Outreach: Year-15 buyout / resyndication, LP exit funding; respect 42(i)(7) ROFR and QC mechanics via template lihtc_gp_year15; gates: dnc_scrub
- Verify before outreach: confirm LIHTC_COMPLIANCE_END 2027-12-19 [DERIVED] via 8609 / Compliance_Start confirmation; Missing Source — Request Document: rent roll / HFA rent limits
- Handoffs ready: see handoff/*.json

### [#3] St Anthony Village — 3560 SE 79th Street, Portland  Tier [C] Score [32.5] Route [acquisition]
- Class / Units / Built / Rehab / Owner type: affordable_regulated / 127 / 1999 / - / lihtc_partnership_forprofit_gp
- First debt event: none in horizon
- First regulatory event: LIHTC_EXTENDED_USE_END 2029-01-01 [REPORTED] — 27.0 mo (OHCS OAHI p9yn-ftai 20261002)
- Capital stack: lender_type not in public record; balance not in public record [-]; value $23,176,103 (ppu_band (market avg $/unit; as-restricted value is usually lower))
- Refi screen: LTV n/a; dscr_refi n/a; gap n/a; cushion n/a
- Signals: hfa_inventory;extended_use_le_36;forprofit_gp
- Decision maker: not in public record, GP managing member + syndicator asset manager, grade C — evidence: pending SOS registry resolution
- Outreach: Year-15 buyout / resyndication, LP exit funding; respect 42(i)(7) ROFR and QC mechanics via template lihtc_gp_year15; gates: dnc_scrub
- Verify before outreach: confirm LIHTC_EXTENDED_USE_END 2029-01-01 [REPORTED] via LURA / REUA; Missing Source — Request Document: rent roll / HFA rent limits
- Handoffs ready: see handoff/*.json

### [#4] Pier Park Apartments — 8660 Columbia Boulevard, Portland  Tier [C] Score [32.5] Route [acquisition]
- Class / Units / Built / Rehab / Owner type: affordable_regulated / 164 / 1997 / - / lihtc_partnership_forprofit_gp
- First debt event: none in horizon
- First regulatory event: LIHTC_EXTENDED_USE_END 2027-01-01 [REPORTED] — 2.9 mo (OHCS OAHI p9yn-ftai 20261002)
- Capital stack: lender_type not in public record; balance not in public record [-]; value $29,928,196 (ppu_band (market avg $/unit; as-restricted value is usually lower))
- Refi screen: LTV n/a; dscr_refi n/a; gap n/a; cushion n/a
- Signals: hfa_inventory;extended_use_le_36;forprofit_gp
- Decision maker: not in public record, GP managing member + syndicator asset manager, grade C — evidence: pending SOS registry resolution
- Outreach: Year-15 buyout / resyndication, LP exit funding; respect 42(i)(7) ROFR and QC mechanics via template lihtc_gp_year15; gates: dnc_scrub
- Verify before outreach: confirm LIHTC_EXTENDED_USE_END 2027-01-01 [REPORTED] via LURA / REUA; Missing Source — Request Document: rent roll / HFA rent limits
- Handoffs ready: see handoff/*.json

### [#5] Floyd Light Apartments — 1005 SE 106th Avenue, Portland  Tier [C] Score [32.5] Route [acquisition]
- Class / Units / Built / Rehab / Owner type: affordable_regulated / 51 / 1997 / - / lihtc_partnership_forprofit_gp
- First debt event: none in horizon
- First regulatory event: LIHTC_EXTENDED_USE_END 2027-01-01 [REPORTED] — 2.9 mo (OHCS OAHI p9yn-ftai 20261002)
- Capital stack: lender_type not in public record; balance not in public record [-]; value $9,306,939 (ppu_band (market avg $/unit; as-restricted value is usually lower))
- Refi screen: LTV n/a; dscr_refi n/a; gap n/a; cushion n/a
- Signals: hfa_inventory;extended_use_le_36;forprofit_gp
- Decision maker: not in public record, GP managing member + syndicator asset manager, grade C — evidence: pending SOS registry resolution
- Outreach: Year-15 buyout / resyndication, LP exit funding; respect 42(i)(7) ROFR and QC mechanics via template lihtc_gp_year15; gates: dnc_scrub
- Verify before outreach: confirm LIHTC_EXTENDED_USE_END 2027-01-01 [REPORTED] via LURA / REUA; Missing Source — Request Document: rent roll / HFA rent limits
- Handoffs ready: see handoff/*.json

### [#6] Berry Ridge Apartments — 2711 W Powell Boulevard, Gresham  Tier [C] Score [32.5] Route [acquisition]
- Class / Units / Built / Rehab / Owner type: affordable_regulated / 248 / 1998 / - / lihtc_partnership_forprofit_gp
- First debt event: none in horizon
- First regulatory event: LIHTC_EXTENDED_USE_END 2029-01-01 [REPORTED] — 27.0 mo (OHCS OAHI p9yn-ftai 20261002)
- Capital stack: lender_type not in public record; balance not in public record [-]; value $45,257,272 (ppu_band (market avg $/unit; as-restricted value is usually lower))
- Refi screen: LTV n/a; dscr_refi n/a; gap n/a; cushion n/a
- Signals: hfa_inventory;extended_use_le_36;forprofit_gp
- Decision maker: not in public record, GP managing member + syndicator asset manager, grade C — evidence: pending SOS registry resolution
- Outreach: Year-15 buyout / resyndication, LP exit funding; respect 42(i)(7) ROFR and QC mechanics via template lihtc_gp_year15; gates: dnc_scrub
- Verify before outreach: confirm LIHTC_EXTENDED_USE_END 2029-01-01 [REPORTED] via LURA / REUA; Missing Source — Request Document: rent roll / HFA rent limits
- Handoffs ready: see handoff/*.json

### [#7] Buckman Heights — 430 NE 16th Avenue, Portland  Tier [C] Score [32.5] Route [acquisition]
- Class / Units / Built / Rehab / Owner type: affordable_regulated / 144 / 1998 / - / lihtc_partnership_forprofit_gp
- First debt event: none in horizon
- First regulatory event: LIHTC_EXTENDED_USE_END 2028-01-01 [REPORTED] — 14.9 mo (OHCS OAHI p9yn-ftai 20261002)
- Capital stack: lender_type not in public record; balance not in public record [-]; value $26,278,416 (ppu_band (market avg $/unit; as-restricted value is usually lower))
- Refi screen: LTV n/a; dscr_refi n/a; gap n/a; cushion n/a
- Signals: hfa_inventory;extended_use_le_36;forprofit_gp
- Decision maker: not in public record, GP managing member + syndicator asset manager, grade C — evidence: pending SOS registry resolution
- Outreach: Year-15 buyout / resyndication, LP exit funding; respect 42(i)(7) ROFR and QC mechanics via template lihtc_gp_year15; gates: dnc_scrub
- Verify before outreach: confirm LIHTC_EXTENDED_USE_END 2028-01-01 [REPORTED] via LURA / REUA; Missing Source — Request Document: rent roll / HFA rent limits
- Handoffs ready: see handoff/*.json

### [#8] Belmont Dairy — 3340 SE Morrison Street, Portland  Tier [C] Score [32.5] Route [acquisition]
- Class / Units / Built / Rehab / Owner type: affordable_regulated / 85 / 1997 / - / lihtc_partnership_forprofit_gp
- First debt event: none in horizon
- First regulatory event: LIHTC_EXTENDED_USE_END 2027-01-01 [REPORTED] — 2.9 mo (OHCS OAHI p9yn-ftai 20261002)
- Capital stack: lender_type not in public record; balance not in public record [-]; value $15,511,565 (ppu_band (market avg $/unit; as-restricted value is usually lower))
- Refi screen: LTV n/a; dscr_refi n/a; gap n/a; cushion n/a
- Signals: hfa_inventory;extended_use_le_36;forprofit_gp
- Decision maker: not in public record, GP managing member + syndicator asset manager, grade C — evidence: pending SOS registry resolution
- Outreach: Year-15 buyout / resyndication, LP exit funding; respect 42(i)(7) ROFR and QC mechanics via template lihtc_gp_year15; gates: dnc_scrub
- Verify before outreach: confirm LIHTC_EXTENDED_USE_END 2027-01-01 [REPORTED] via LURA / REUA; Missing Source — Request Document: rent roll / HFA rent limits
- Handoffs ready: see handoff/*.json

### [#9] Linc245 (fka Village at Lovejoy Fountain) — 245 SW LINCOLN ST, Portland  Tier [C] Score [32.5] Route [acquisition]
- Class / Units / Built / Rehab / Owner type: affordable_regulated / 198 / 1999 / - / lihtc_partnership_forprofit_gp
- First debt event: none in horizon
- First regulatory event: LIHTC_EXTENDED_USE_END 2029-01-01 [REPORTED] — 27.0 mo (OHCS OAHI p9yn-ftai 20261002)
- Capital stack: lender_type not in public record; balance not in public record [-]; value $36,132,822 (ppu_band (market avg $/unit; as-restricted value is usually lower))
- Refi screen: LTV n/a; dscr_refi n/a; gap n/a; cushion n/a
- Signals: hfa_inventory;extended_use_le_36;forprofit_gp
- Decision maker: not in public record, GP managing member + syndicator asset manager, grade C — evidence: pending SOS registry resolution
- Outreach: Year-15 buyout / resyndication, LP exit funding; respect 42(i)(7) ROFR and QC mechanics via template lihtc_gp_year15; gates: dnc_scrub
- Verify before outreach: confirm LIHTC_EXTENDED_USE_END 2029-01-01 [REPORTED] via LURA / REUA; Missing Source — Request Document: rent roll / HFA rent limits
- Handoffs ready: see handoff/*.json

### [#10] Bethany Meadows II — 15817 NW Athens Drive, Portland  Tier [C] Score [32.5] Route [acquisition]
- Class / Units / Built / Rehab / Owner type: affordable_regulated / 132 / 1998 / - / lihtc_partnership_forprofit_gp
- First debt event: none in horizon
- First regulatory event: LIHTC_EXTENDED_USE_END 2029-01-01 [REPORTED] — 27.0 mo (OHCS OAHI p9yn-ftai 20261002)
- Capital stack: lender_type not in public record; balance not in public record [-]; value $24,088,548 (ppu_band (market avg $/unit; as-restricted value is usually lower))
- Refi screen: LTV n/a; dscr_refi n/a; gap n/a; cushion n/a
- Signals: hfa_inventory;extended_use_le_36;forprofit_gp
- Decision maker: not in public record, GP managing member + syndicator asset manager, grade C — evidence: pending SOS registry resolution
- Outreach: Year-15 buyout / resyndication, LP exit funding; respect 42(i)(7) ROFR and QC mechanics via template lihtc_gp_year15; gates: dnc_scrub
- Verify before outreach: confirm LIHTC_EXTENDED_USE_END 2029-01-01 [REPORTED] via LURA / REUA; Missing Source — Request Document: rent roll / HFA rent limits
- Handoffs ready: see handoff/*.json

### [#11] Terrace View Apartments — 6685 SW Sagert, Tualatin  Tier [C] Score [32.5] Route [acquisition]
- Class / Units / Built / Rehab / Owner type: affordable_regulated / 100 / 1976 / - / lihtc_partnership_forprofit_gp
- First debt event: none in horizon
- First regulatory event: LIHTC_EXTENDED_USE_END 2028-01-01 [REPORTED] — 14.9 mo (OHCS OAHI p9yn-ftai 20261002)
- Capital stack: lender_type not in public record; balance not in public record [-]; value $18,248,900 (ppu_band (market avg $/unit; as-restricted value is usually lower))
- Refi screen: LTV n/a; dscr_refi n/a; gap n/a; cushion n/a
- Signals: hfa_inventory;extended_use_le_36;forprofit_gp
- Decision maker: not in public record, GP managing member + syndicator asset manager, grade C — evidence: pending SOS registry resolution
- Outreach: Year-15 buyout / resyndication, LP exit funding; respect 42(i)(7) ROFR and QC mechanics via template lihtc_gp_year15; gates: dnc_scrub
- Verify before outreach: confirm LIHTC_EXTENDED_USE_END 2028-01-01 [REPORTED] via LURA / REUA; Missing Source — Request Document: rent roll / HFA rent limits
- Handoffs ready: see handoff/*.json

### [#12] Hawthorne Villa Apartments — 7709 SW PFAFFLE ST, Tigard  Tier [C] Score [32.5] Route [acquisition]
- Class / Units / Built / Rehab / Owner type: affordable_regulated / 119 / 1996 / - / lihtc_partnership_forprofit_gp
- First debt event: none in horizon
- First regulatory event: LIHTC_EXTENDED_USE_END 2027-01-01 [REPORTED] — 2.9 mo (OHCS OAHI p9yn-ftai 20261002)
- Capital stack: lender_type not in public record; balance not in public record [-]; value $21,716,191 (ppu_band (market avg $/unit; as-restricted value is usually lower))
- Refi screen: LTV n/a; dscr_refi n/a; gap n/a; cushion n/a
- Signals: hfa_inventory;extended_use_le_36;forprofit_gp
- Decision maker: not in public record, GP managing member + syndicator asset manager, grade C — evidence: pending SOS registry resolution
- Outreach: Year-15 buyout / resyndication, LP exit funding; respect 42(i)(7) ROFR and QC mechanics via template lihtc_gp_year15; gates: dnc_scrub
- Verify before outreach: confirm LIHTC_EXTENDED_USE_END 2027-01-01 [REPORTED] via LURA / REUA; Missing Source — Request Document: rent roll / HFA rent limits
- Handoffs ready: see handoff/*.json

### [#13] Bethany Meadows I — 16050 NW LAIDLAW RD, Portland  Tier [C] Score [32.5] Route [acquisition]
- Class / Units / Built / Rehab / Owner type: affordable_regulated / 208 / 1997 / - / lihtc_partnership_forprofit_gp
- First debt event: none in horizon
- First regulatory event: LIHTC_EXTENDED_USE_END 2027-01-01 [REPORTED] — 2.9 mo (OHCS OAHI p9yn-ftai 20261002)
- Capital stack: lender_type not in public record; balance not in public record [-]; value $37,957,712 (ppu_band (market avg $/unit; as-restricted value is usually lower))
- Refi screen: LTV n/a; dscr_refi n/a; gap n/a; cushion n/a
- Signals: hfa_inventory;extended_use_le_36;forprofit_gp
- Decision maker: not in public record, GP managing member + syndicator asset manager, grade C — evidence: pending SOS registry resolution
- Outreach: Year-15 buyout / resyndication, LP exit funding; respect 42(i)(7) ROFR and QC mechanics via template lihtc_gp_year15; gates: dnc_scrub
- Verify before outreach: confirm LIHTC_EXTENDED_USE_END 2027-01-01 [REPORTED] via LURA / REUA; Missing Source — Request Document: rent roll / HFA rent limits
- Handoffs ready: see handoff/*.json

### [#14] Erickson Fritz Apartments — 9 NW Second Avenue, Portland  Tier [C] Score [32.0] Route [acquisition]
- Class / Units / Built / Rehab / Owner type: affordable_regulated / 62 / 2014 / 2016 / lihtc_partnership_forprofit_gp
- First debt event: none in horizon
- First regulatory event: LIHTC_COMPLIANCE_END 2029-08-15 [DERIVED] — 34.4 mo (OHCS OAHI p9yn-ftai 20261002)
- Capital stack: lender_type not in public record; balance not in public record [-]; value $11,314,318 (ppu_band (market avg $/unit; as-restricted value is usually lower))
- Refi screen: LTV n/a; dscr_refi n/a; gap n/a; cushion n/a
- Signals: hfa_inventory;year15_forprofit;programs_2_same_24mo;forprofit_gp
- Decision maker: not in public record, GP managing member + syndicator asset manager, grade C — evidence: pending SOS registry resolution
- Outreach: Year-15 buyout / resyndication, LP exit funding; respect 42(i)(7) ROFR and QC mechanics via template lihtc_gp_year15; gates: dnc_scrub
- Verify before outreach: confirm LIHTC_COMPLIANCE_END 2029-08-15 [DERIVED] via 8609 / Compliance_Start confirmation; Missing Source — Request Document: rent roll / HFA rent limits
- Handoffs ready: see handoff/*.json

### [#15] Magnolia, The (aka Eliot MLK Project) — 3250 NE Martin Luther King Jr Blvd, Portland  Tier [C] Score [32.0] Route [acquisition]
- Class / Units / Built / Rehab / Owner type: affordable_regulated / 50 / 2013 / - / lihtc_partnership_forprofit_gp
- First debt event: none in horizon
- First regulatory event: LIHTC_COMPLIANCE_END 2028-09-26 [DERIVED] — 23.8 mo (OHCS OAHI p9yn-ftai 20261002)
- Capital stack: lender_type not in public record; balance not in public record [-]; value $9,124,450 (ppu_band (market avg $/unit; as-restricted value is usually lower))
- Refi screen: LTV n/a; dscr_refi n/a; gap n/a; cushion n/a
- Signals: hfa_inventory;year15_forprofit;programs_2_same_24mo;forprofit_gp
- Decision maker: not in public record, GP managing member + syndicator asset manager, grade C — evidence: pending SOS registry resolution
- Outreach: Year-15 buyout / resyndication, LP exit funding; respect 42(i)(7) ROFR and QC mechanics via template lihtc_gp_year15; gates: dnc_scrub
- Verify before outreach: confirm LIHTC_COMPLIANCE_END 2028-09-26 [DERIVED] via 8609 / Compliance_Start confirmation; Missing Source — Request Document: rent roll / HFA rent limits
- Handoffs ready: see handoff/*.json

### [#16] Macdonald West Apts — 127 NW 6th Avenue, Portland  Tier [C] Score [32.0] Route [acquisition]
- Class / Units / Built / Rehab / Owner type: affordable_regulated / 42 / 2012 / - / lihtc_partnership_forprofit_gp
- First debt event: none in horizon
- First regulatory event: LIHTC_COMPLIANCE_END 2027-11-27 [DERIVED] — 13.8 mo (OHCS OAHI p9yn-ftai 20261002)
- Capital stack: lender_type not in public record; balance not in public record [-]; value $7,664,538 (ppu_band (market avg $/unit; as-restricted value is usually lower))
- Refi screen: LTV n/a; dscr_refi n/a; gap n/a; cushion n/a
- Signals: hfa_inventory;year15_forprofit;programs_2_same_24mo;forprofit_gp
- Decision maker: not in public record, GP managing member + syndicator asset manager, grade C — evidence: pending SOS registry resolution
- Outreach: Year-15 buyout / resyndication, LP exit funding; respect 42(i)(7) ROFR and QC mechanics via template lihtc_gp_year15; gates: dnc_scrub
- Verify before outreach: confirm LIHTC_COMPLIANCE_END 2027-11-27 [DERIVED] via 8609 / Compliance_Start confirmation; Missing Source — Request Document: rent roll / HFA rent limits
- Handoffs ready: see handoff/*.json

### [#17] Glisan Commons — 555 NE 100th Avenue, Portland  Tier [C] Score [32.0] Route [acquisition]
- Class / Units / Built / Rehab / Owner type: affordable_regulated / 67 / 2014 / - / lihtc_partnership_forprofit_gp
- First debt event: none in horizon
- First regulatory event: LIHTC_COMPLIANCE_END 2029-01-22 [DERIVED] — 27.7 mo (OHCS OAHI p9yn-ftai 20261002)
- Capital stack: lender_type not in public record; balance not in public record [-]; value $12,226,763 (ppu_band (market avg $/unit; as-restricted value is usually lower))
- Refi screen: LTV n/a; dscr_refi n/a; gap n/a; cushion n/a
- Signals: hfa_inventory;year15_forprofit;programs_2_same_24mo;forprofit_gp
- Decision maker: not in public record, GP managing member + syndicator asset manager, grade C — evidence: pending SOS registry resolution
- Outreach: Year-15 buyout / resyndication, LP exit funding; respect 42(i)(7) ROFR and QC mechanics via template lihtc_gp_year15; gates: dnc_scrub
- Verify before outreach: confirm LIHTC_COMPLIANCE_END 2029-01-22 [DERIVED] via 8609 / Compliance_Start confirmation; Missing Source — Request Document: rent roll / HFA rent limits
- Handoffs ready: see handoff/*.json

## Partnership Track

- Reedville Apartments (nonprofit; USDA_515_MATURITY 2030-08-15 [REPORTED] — 46.4 mo) — template nonprofit_partnership; signals hfa_inventory;usda_36_60;nonprofit_gp;families_2
- Gray's Landing (lihtc_partnership_nonprofit_gp; LIHTC_EXTENDED_USE_END 2029-01-01 [REPORTED] — 27.0 mo) — template nonprofit_partnership; signals hfa_inventory;extended_use_le_36;programs_2_same_24mo;nonprofit_gp
- STADIUM STATION (nonprofit; LIHTC_EXTENDED_USE_END 2028-01-01 [REPORTED] — 14.9 mo) — template nonprofit_partnership; signals hfa_inventory;extended_use_le_36;nonprofit_gp
- Esperanza Court (lihtc_partnership_nonprofit_gp; SOFT_PROGRAM_END 2029-04-09 [REPORTED] — 30.2 mo) — template nonprofit_partnership; signals hfa_inventory;soft_program_end_le_36;programs_3plus_same_24mo;nonprofit_gp
- Lincoln Woods (lihtc_partnership_nonprofit_gp; SOFT_PROGRAM_END 2027-11-19 [REPORTED] — 13.5 mo) — template nonprofit_partnership; signals hfa_inventory;soft_program_end_le_36;programs_3plus_same_24mo;nonprofit_gp
- Crestview Court (lihtc_partnership_nonprofit_gp; LIHTC_COMPLIANCE_END 2027-03-14 [DERIVED] — 5.3 mo) — template nonprofit_partnership; signals hfa_inventory;hud_contract:HAP;soft_program_end_le_36;programs_3plus_same_24mo;nonprofit_gp
- Rose Schnitzer Tower (lihtc_partnership_nonprofit_gp; HAP_EXPIRATION 2027-12-10 [REPORTED] — 14.2 mo) — template nonprofit_partnership; signals hfa_inventory;hud_contract:HAP;hap_le_24;programs_2_same_24mo;nonprofit_gp
- Maples II (nonprofit; HAP_EXPIRATION 2028-08-31 [REPORTED] — 22.9 mo) — template nonprofit_partnership; signals hfa_inventory;hud_contract:PRAC;hap_le_24;programs_2_same_24mo;nonprofit_gp
- Country Squire Apts (nonprofit; REGULATORY_LATEST_END 2027-05-23 [REPORTED] — 7.6 mo) — template nonprofit_partnership; signals hfa_inventory;latest_end_le_36;nonprofit_gp
- ELDERPLACE IN CULLY (nonprofit; REGULATORY_LATEST_END 2026-12-15 [REPORTED] — 2.4 mo) — template nonprofit_partnership; signals hfa_inventory;latest_end_le_36;nonprofit_gp
- Roselyn Apartments (lihtc_partnership_nonprofit_gp; HAP_EXPIRATION 2029-05-25 [REPORTED] — 31.7 mo) — template nonprofit_partnership; signals hfa_inventory;hud_contract:HAP;programs_3plus_same_24mo;nonprofit_gp
- CSP Park Tower Apartments (lihtc_partnership_nonprofit_gp; LIHTC_COMPLIANCE_END 2028-12-31 [DERIVED] — 26.9 mo) — template nonprofit_partnership; signals hfa_inventory;hud_contract:HAP;year15_nonprofit_or_pha;programs_3plus_same_24mo;nonprofit_gp
- Hawthorne East (lihtc_partnership_nonprofit_gp; LIHTC_COMPLIANCE_END 2031-02-12 [DERIVED] — 52.4 mo) — template nonprofit_partnership; signals hfa_inventory;hud_contract:HAP;programs_3plus_same_24mo;nonprofit_gp
- Orchards at Orenco II, The (lihtc_partnership_nonprofit_gp; LIHTC_COMPLIANCE_END 2030-06-29 [DERIVED] — 44.9 mo) — template nonprofit_partnership; signals hfa_inventory;programs_3plus_same_24mo;nonprofit_gp
- Bridge Meadows Beaverton (nonprofit; LIHTC_COMPLIANCE_END 2031-09-19 [DERIVED] — 59.6 mo) — template nonprofit_partnership; signals hfa_inventory;programs_3plus_same_24mo;nonprofit_gp
- Whispering Pines Senior Village (nonprofit; HAP_EXPIRATION 2028-05-31 [REPORTED] — 19.9 mo) — template nonprofit_partnership; signals hfa_inventory;hud_contract:PRAC;hap_le_24;nonprofit_gp
- Powell Plaza II (lihtc_partnership_nonprofit_gp; HAP_EXPIRATION 2027-03-31 [REPORTED] — 5.9 mo) — template nonprofit_partnership; signals hfa_inventory;hud_contract:HAP;hap_le_24;nonprofit_gp
- Mt Hood Community Apartments (nonprofit; HAP_EXPIRATION 2027-09-30 [REPORTED] — 11.9 mo) — template nonprofit_partnership; signals hfa_inventory;hud_contract:HAP;hap_le_24;nonprofit_gp
- Clinton Street Apartments (aka Dual Diagnoisis) (nonprofit; SOFT_PROGRAM_END 2027-02-15 [REPORTED] — 4.4 mo) — template nonprofit_partnership; signals hfa_inventory;soft_program_end_le_36;nonprofit_gp
- MARY ANN, THE (nonprofit; SOFT_PROGRAM_END 2027-10-02 [REPORTED] — 11.9 mo) — template nonprofit_partnership; signals hfa_inventory;soft_program_end_le_36;nonprofit_gp
- Roselyn Villa (nonprofit; SOFT_PROGRAM_END 2027-05-01 [REPORTED] — 6.9 mo) — template nonprofit_partnership; signals hfa_inventory;soft_program_end_le_36;nonprofit_gp
- Ikoi So Terrace (lihtc_partnership_nonprofit_gp; LIHTC_COMPLIANCE_END 2029-07-11 [DERIVED] — 33.3 mo) — template nonprofit_partnership; signals hfa_inventory;hud_contract:HAP;year15_nonprofit_or_pha;programs_2_same_24mo;nonprofit_gp
- Town Center Station (lihtc_partnership_nonprofit_gp; SOFT_PROGRAM_END 2030-10-01 [REPORTED] — 48.0 mo) — template nonprofit_partnership; signals hfa_inventory;programs_2_same_24mo;nonprofit_gp
- Hollyfield Village (lihtc_partnership_nonprofit_gp; LIHTC_COMPLIANCE_END 2028-10-10 [DERIVED] — 24.2 mo) — template nonprofit_partnership; signals hfa_inventory;hud_contract:HAP;year15_nonprofit_or_pha;programs_2_same_24mo;nonprofit_gp
- Upshur House (lihtc_partnership_nonprofit_gp; HAP_EXPIRATION 2030-04-30 [REPORTED] — 42.9 mo) — template nonprofit_partnership; signals hfa_inventory;hud_contract:HAP;programs_2_same_24mo;nonprofit_gp
- Plaza Townhomes (lihtc_partnership_nonprofit_gp; LIHTC_COMPLIANCE_END 2031-08-01 [DERIVED] — 58.0 mo) — template nonprofit_partnership; signals hfa_inventory;hud_contract:HAP;programs_2_same_24mo;nonprofit_gp
- Vermont Springs (lihtc_partnership_nonprofit_gp; HAP_EXPIRATION 2029-08-31 [REPORTED] — 34.9 mo) — template nonprofit_partnership; signals hfa_inventory;hud_contract:HAP;programs_2_same_24mo;nonprofit_gp
- 333 Oak Apartments (lihtc_partnership_nonprofit_gp; HAP_EXPIRATION 2029-09-30 [REPORTED] — 35.9 mo) — template nonprofit_partnership; signals hfa_inventory;hud_contract:HAP;programs_2_same_24mo;nonprofit_gp
- Bronaugh Apartments (lihtc_partnership_nonprofit_gp; LIHTC_COMPLIANCE_END 2030-06-12 [DERIVED] — 44.3 mo) — template nonprofit_partnership; signals hfa_inventory;hud_contract:HAP;programs_2_same_24mo;nonprofit_gp
- Gilman Court (aka Glisan Commons Phase II) (lihtc_partnership_nonprofit_gp; LIHTC_COMPLIANCE_END 2030-04-13 [DERIVED] — 42.3 mo) — template nonprofit_partnership; signals hfa_inventory;programs_2_same_24mo;nonprofit_gp
- Martin Luther King Manor (lihtc_partnership_nonprofit_gp; HAP_EXPIRATION 2029-06-30 [REPORTED] — 32.9 mo) — template nonprofit_partnership; signals hfa_inventory;hud_contract:HAP;programs_2_same_24mo;nonprofit_gp
- Rosewood Plaza (lihtc_partnership_nonprofit_gp; LIHTC_COMPLIANCE_END 2029-10-14 [DERIVED] — 36.4 mo) — template nonprofit_partnership; signals hfa_inventory;programs_2_same_24mo;nonprofit_gp
- Town Center Courtyards (lihtc_partnership_nonprofit_gp; LIHTC_COMPLIANCE_END 2030-08-14 [DERIVED] — 46.4 mo) — template nonprofit_partnership; signals hfa_inventory;nonprofit_gp
- Scott Crest Plaza (lihtc_partnership_nonprofit_gp; HAP_EXPIRATION 2028-12-31 [REPORTED] — 26.9 mo) — template nonprofit_partnership; signals hfa_inventory;hud_contract:HAP;nonprofit_gp
- Miraflores (lihtc_partnership_nonprofit_gp; SOFT_PROGRAM_END 2029-12-15 [REPORTED] — 38.4 mo) — template nonprofit_partnership; signals hfa_inventory;nonprofit_gp
- Hill Park Apartments (lihtc_partnership_nonprofit_gp; LIHTC_COMPLIANCE_END 2031-05-01 [DERIVED] — 54.9 mo) — template nonprofit_partnership; signals hfa_inventory;nonprofit_gp
- Admiral Apartments (lihtc_partnership_nonprofit_gp; SOFT_PROGRAM_END 2031-01-27 [REPORTED] — 51.8 mo) — template nonprofit_partnership; signals hfa_inventory;hud_contract:HAP;nonprofit_gp
- Lafayette Court Apartments (nonprofit; REGULATORY_LATEST_END 2029-12-15 [REPORTED] — 38.4 mo) — template nonprofit_partnership; signals hfa_inventory;nonprofit_gp
- BARBARA ROBERTS (nonprofit; REGULATORY_LATEST_END 2031-07-15 [REPORTED] — 57.4 mo) — template nonprofit_partnership; signals hfa_inventory;nonprofit_gp
- FAULKNER PLACE (nonprofit; REGULATORY_LATEST_END 2030-11-15 [REPORTED] — 49.4 mo) — template nonprofit_partnership; signals hfa_inventory;nonprofit_gp

## Lender-Counterparty Track

- none

## Pipeline Actions

| priority | action | channel | compliance gate | count |
|---|---|---|---|---|
| 1 | PuSH first-notice window open now (Village Garden Apartments, ALBINA PLAZA, SILVERCREST RESIDENCE, MAPLES I): file a records request with the OHCS PuSH-CP Program Manager and the affected city for any owner notice; a confirmed notice becomes PRESERVATION_NOTICE_RECEIVED (20 pts) | records request | preservation_law | 4 |
| 4 | Tier C: Monitor; add tapes / images that upgrade PROXY or ESTIMATED dates | letter / business line | per card | 17 |
| 5 | Tier WATCH: Quarterly re-check | letter / business line | per card | 114 |

## Data Gaps and Verification Queue

- Rejects_Verify rows: 4 = rejected 0 + verify-flag rows 4
- Leads with a conflict / ambiguity flag: 4; leads with a document request (Missing Source — Request Document, e.g. rent roll for the value proxy): 141
- Sources still verified_live=false: ohcs_oahi, ohcs_push_forecast, ohcs_hca_optout, hud_fhasl_active / hud_fhasl_terminated, hud_mf_assist_sec8, hud_lihtc_db, hud_reac, usda_mfh_exit, nhpd, multco_records, oregon_sos_registry
- SOS worklist: 16 owner entities to resolve (handoff/sos_worklist.csv); documents to request: 30 rows (handoff/documents_to_request.csv; recorder image fee from market-params, verify: true)
- Decision makers: every entity owner is `not in public record` until the SOS worklist is resolved (two independent filings for grade A).

## Assumptions and Limits

- Scoring tables: references/scoring/*.json; basis multipliers RECORDED 1.00 / REPORTED 0.90 / DERIVED 0.80 / ESTIMATED 0.50 / PROXY 0.30.
- Mini-perm maturities derived from Financial_Closing_Date + 15y (17y for 4% bond deals) are PROXY (0.30) and alone cap a lead at Tier C.
- HAP expirations under annual renewal roll forward (confidence 0.70); Year 15 assumes the credit period began in the Compliance_Start year (+1y election possible).
- PuSH notice windows come from OAR 813-115 snippets (ORS 456.260-.265 text not read in this build); confirm before quoting to a counterparty.
- Assessed Value is never used as market value (Oregon Measure 50). Value proxies: ppu_band (units x market $/unit) until rent-limits.json is populated; every market parameter marked verify must be re-pulled before a run that depends on it.