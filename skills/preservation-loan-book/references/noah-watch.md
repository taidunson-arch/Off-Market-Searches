# Optional Module: NOAH Watch (`noah_unregulated`)

Off by default for every profile. A screen of unregulated 5+ unit properties absent from OHCS / HUD / NHPD that a city or county acquisition program (Metro bond, PHB acquisition strategy) might buy and restrict, with NOAH's Oregon Housing Acquisition Fund as the bridge lender named in `mandate.json`. It is a public-acquisition screen, not a private-equity refinance screen: no valuation beyond the rent / FMR gap, no outreach, one route (`nofa_offer` against an `acquisition_grant` product).

## Enabling

`--noah-watch --noah <noah_candidates.csv>` on `build_universe.py` / `score_preservation.py`, or `noah_watch: true` in `run_config.json`. When the profile is `city_housing` or `county` AND `mandate.json` lists an open `acquisition_grant` product, SKILL.md asks one question offering to enable it rather than enabling silently. Never enabled by a keyword.

## Inputs

Manual `noah_candidates.csv` (the pack ships no adapter for assessor exports; the v2 assessor adapter was dropped): `property_name, address, city, zip, county_fips, parcel_id, units, year_built, owner_name, hold_years, tax_delinquent_years, est_rent (per unit, in place or asking), bedroom_mix (optional), lender_type, maturity (RECORDED/REPORTED only, with source), code_cases_open`. Declare every date column in `dataset-schemas.yaml` block `noah_candidates`. `rent_to_fmr_ratio` = est_rent / FMR or SAFMR from the pack `market-params.json` `safmr` block (by ZIP and bedroom; verify current FY).

## Scoring (`references/scoring/noah_watch.json`, 100 points)

| factor | wt | bands |
|---|---|---|
| units_5plus_unregulated | 20 | 5-19 units with no program events 12; 20+ 20 |
| rent_vs_fmr_gap | 25 | ratio <= 0.85 -> 25; 0.85-0.95 -> 15 |
| tax_delinquency | 15 | 1 year 8; 2+ years 15 |
| long_hold | 15 | HOLD_YEARS >= 15 -> 15; 10-15 -> 8 |
| maturity | 15 | LOAN_MATURITY <= 24 months, RECORDED / REPORTED only -> 15 |
| physical | 10 | code case 6; dangerous building 10 |

Queue bands and basis multipliers from `shared_adjustments.json`. A property with any program in `programs_list` is excluded from this class (it belongs in `affordable_public_am`).

## Outputs

- `asset_class = noah_unregulated`; `primary_route = nofa_offer` when score >= 30 and `mandate_fit = eligible` for an `acquisition_grant`; otherwise `none`.
- `intervention = preservation_nofa_invitation` (acquisition-rehab framing); `owner_outreach: false` everywhere.
- `handoff/off-market-deal-finder.json`: `{asset_class: market_rate_mf, geography, property_ids, owner_outreach: false, purpose: public_acquisition_screen}` so the buyer-side sibling's value-proxy and refinance-gap plumbing can be run by the agency's acquisition team if it chooses; this pack never consumes that sibling's outreach templates, buyer profiles or acquisition routes.
- NOAH rows appear in `Preservation_Queue` with a `noah` tag and in Board_Totals only as a separate "NOAH candidates" line (never summed into units_at_risk, which counts restricted units only).

## Limits

No relocation or URA analysis (that follows any later federally funded rehab); no owner contact; no price. The screen says where an acquisition grant would buy the most affordability per dollar, nothing more.
