# Decision-Maker Enrichment

How the skill turns an owner-of-record string into a named decision maker with an evidence chain, and how it classifies owners into the archetypes that drive routing and outreach. This replaces the v1 skip-trace model, which assumed the owner was a person. For most 5+ unit assets the owner is an LLC, LP or nonprofit, and the person who can say yes is one or two hops away in public filings.

## Contents

1. Principles
2. owner_type inference rules
3. Six-hop resolution chain
4. Contact grades
5. Archetype table
6. SOS worklist specification
7. Oregon and Washington registry notes
8. Individual skip tracing (class 1 only)
9. What not to do

---

## 1. Principles

- Name a person only with two independent evidence items (for example: SOS annual report lists them as manager, and they signed the recorded trust deed for the owning entity). One filing alone yields grade B.
- The registered agent is never the owner. It is a service address.
- Write `not in public record` rather than guessing. A blank decision-maker field with a grade C contact (entity + principal office mailing address) is a usable lead; a fabricated name is not.
- Resolve to a role before a name: `GP managing member`, `nonprofit executive director`, `receiver`, `special servicer asset manager`, `personal representative`. The role determines the channel and the template.
- Every hop is logged in `dm_source` as `source:identifier` pairs (e.g. `sos_or:1234567-89;multco_td:2018-061234`).

## 2. owner_type inference rules

Applied in order; first match wins. Inputs: assessor/HFA `Owner Name`, `Owner Type` where provided (OHCS has it in 43% of rows, mixed case), HUD `owner_organization_name`, LIHTC `NON_PROF`, Developer/Management names, mailing vs situs address, SOS entity type.

| order | rule | owner_type |
|---|---|---|
| 1 | owner is a court-appointed receiver, special servicer, trustee's-deed grantee, or REO vesting (`FEDERAL NATIONAL MORTGAGE`, `BANK ... AS TRUSTEE`, lender name) | `lender_reo_receiver` |
| 2 | name tokens `Housing Authority`, `Home Forward`, `HACSA`, `Housing Works`, or Owner Type `Housing Authority` | `housing_authority` |
| 3 | name tokens `City of`, `County of`, `State of`, `Metro`, `Urban Renewal`, `Prosper Portland`, or Owner Type `Government` | `government` |
| 4 | Owner Type `Non-Profit` (any case), LIHTC `NON_PROF = 1`, or tokens `Inc`, `Corp`, `Community`, `Foundation`, `Ministries`, `Catholic`, `Lutheran`, `Habitat`, `CDC`, `Housing Development Corp`, `Neighborhood`, `Services` with no `LLC/LP` token, and no for-profit developer | `nonprofit`; if the entity is an LP/LLC whose GP or manager is a nonprofit (SOS or Developer Name) -> `lihtc_partnership_nonprofit_gp` |
| 5 | tokens `LP`, `L.P.`, `LLLP`, `Limited Partnership`, or `LLC` with LIHTC programs and Owner Type `For-Profit` / `Limited Dividend` / `Profit` / blank, and the developer is not a nonprofit | `lihtc_partnership_forprofit_gp` |
| 6 | `LLC`/`LP` with no regulatory programs; SOS shows a principal office shared with 3+ other property-owning entities or a management company | `regional_operator` |
| 7 | `LLC`/`LP` with no regulatory programs; SOS registry date within 12 months of the acquisition deed and no sibling entities | `single_asset_llc` |
| 8 | REIT, fund, pension, insurance company, national operator (tokens `REIT`, `Fund`, `Capital Partners`, `Investors L.P.`, `Trust` with SEC filings) | `institutional` |
| 9 | tokens `Trust`, `Trustee`, `Estate of`, `Family LP` (no operating business), `Living Trust`, `Revocable` | `trust_estate` |
| 10 | individual name(s), mailing address == situs | `individual_occupant` |
| 11 | individual name(s), mailing address != situs | `individual_absentee` |
| 12 | anything else | `unknown` |

OHCS specifics: `Owner Type` values `PROFIT` -> For-Profit, `NON-PROFIT` -> Non-Profit, `HOUSING AUTHORITY`, `GOVERNMENT`, `Limited Dividend` (treat as for-profit). Blank in 1,039 of 1,819 rows: infer from `Owner Name`, then `Developer Name`, then `Management Name` (a nonprofit manager does not make the owner a nonprofit; a nonprofit developer of an LP usually does make it the GP).

`owner_archetype` is the template id (Section 5) derived from `owner_type` plus overlays: `hud_usda_assisted_owner` when `hud_contract` or `USDA_515` is present; `receiver_lender` when any ROUTING event moved the route to `lender_counterparty`.

## 3. Six-hop resolution chain

Stop at the first hop that yields grade A; record every hop tried.

| hop | source | what you get | adapter / how |
|---|---|---|---|
| 1 | Assessor / HFA / HUD record | owner-of-record string, mailing address (`mailing_address` column from `normalize_assessor_taxlots.py`), HUD `owner_organization_name`, `owner_main_phone_number_text`, `mgmt_agent_org_name`, OHCS `Owner Name` / `Developer Name` / `Management Name` | from the ingested files; mailing address vs situs sets `ABSENTEE_TIER` |
| 2 | Recorded vesting deed and trust deed signature blocks | signatory name and title; the entity chain ("by ABC Manager LLC, its manager, by Jane Doe, Managing Member") | recorder image (Multnomah $3.75 per county snippet, unverified, `market-params.json`; Clark WA free, unverified); extraction schema in `capital-stack-math.md` Section 8 |
| 3 | State business registry (Oregon SOS; WA SOS; home state via OpenCorporates for foreign entities) | status, registry date, registered agent (not owner), principal office, managers or at least one member (LLC), every general partner (LP), officers/directors (nonprofit), annual-report history | manual search; worklist CSV (Section 6). Follow the GP LLC to its own managers (hop 3 repeats once) |
| 4 | Program documents | LURA / Declaration of Land Use Restrictive Covenants names the owner LP and GP; HAP contract names owner and agent; Form 8609 Part II names the owner; USDA borrower record | recorder index (LURA is recorded); OHCS / HUD / RD records request |
| 5 | Nonprofit filings | IRS Form 990 Part VII officers and key employees; executive director, CFO; board chair | ProPublica Nonprofit Explorer or IRS TEOS (free) |
| 6 | Court and servicing records | receiver and lender counsel (order appointing receiver), special servicer (CMBS IRP / Annex A), debtor's counsel (PACER), personal representative and estate counsel (probate docket) | OJD Smart Search, PACER, trustee IRP; these replace the owner as counterparty |

Corroboration patterns that reach grade A: SOS manager == trust-deed signatory; SOS GP == LURA GP; HUD owner contact == SOS officer; 990 officer == SOS director. Conflicting names across hops -> `Verify — Conflicting Sources` on `decision_maker_name` and grade B.

Sponsor-family mapping (feeds `sponsor_loans_maturing_36mo`): cluster entities by shared registered agent, principal office and manager names across SOS plus OpenCorporates; run every sibling through the recorder and court indexes; require two independent indicators before scoring portfolio stress.

## 4. Contact grades

| grade | definition | typical evidence | usable for |
|---|---|---|---|
| `A` | named person from an official filing plus a corroborating signature or second filing | SOS manager + trust-deed signatory; LP filing GP + LURA | direct letter to the person; DNC-scrubbed call to a business line |
| `B` | entity officer/manager from one filing | SOS annual report only; HUD owner contact only | letter addressed to the role at the principal office |
| `C` | entity plus mailing address only | assessor record | letter to the entity; ask for the right person |

LP annual reports are understood to list every general partner (ORS 70.610; verify current ORS 70.610 text and the SOS annual-report form, since this is what lets LIHTC partnerships reach grade A once the LURA or trust deed is read). Member-managed Oregon LLCs need list only one member (ORS 63.787; verify likewise), so a single SOS filing is grade B until a signature block confirms it. The grading rule stands; its statutory footing is contingent on those two sections reading as described.

## 5. Archetype table

| owner_type | detection rule | decision maker | where found | channel | outreach angle | do not | template id |
|---|---|---|---|---|---|---|---|
| `individual_occupant` / `individual_absentee` | individual name on the roll; mailing == / != situs | the owner | assessor; licensed skip trace (class 1 Tier A/B only) | letter first, then DNC-scrubbed call | convenience, certainty, tax strategy (1031, installment) | never price-first; no age or voter data; no contact if DNC/litigator flag | `individual_or_trust` |
| `trust_estate` | `Trust`, `Trustee`, `Estate of`; PROBATE_FILED | trustee or personal representative | deed into trust; probate docket (PR and counsel) | letter to PR or estate counsel after 60-120 days | simple liquidation; stepped-up basis removes the recapture lock | no contact before letters testamentary issue; never lead with price | `estate` |
| `single_asset_llc` | LLC formed near acquisition, no siblings | managing member | SOS; trust-deed signatory | letter to principal office; call business line | maturity math, 1031/DST, regulatory fatigue | registered agent is not the owner; no personal cell without consent | `single_asset_llc` |
| `regional_operator` | SOS sibling cluster, shared office / PM | principal or acquisitions head | SOS cluster; firm website | direct principal conversation | portfolio liquidity; swap or trade assets | no broker bypass during a live exclusive | `regional_operator` |
| `institutional` | REIT / fund / life co | asset manager or dispositions | fund site; CMBS Annex A; SEC filings | formal IOI through their process | certainty, debt assumption, speed | no retail letters | `institutional` |
| `lihtc_partnership_forprofit_gp` | LP/LLC with LIHTC programs, for-profit GP | GP managing member plus syndicator asset manager (LP) | SOS LP record (every GP), LURA, OHCS Developer Name, HUD owner org | GP letter plus LP courtesy call | Year-15 buyout or resyndication; fund the LP exit; Year-30 conversion or preservation sale | respect §42(i)(7) ROFR and qualified-contract mechanics; no tenant-facing contact | `lihtc_gp_year15` |
| `lihtc_partnership_nonprofit_gp` / `nonprofit` | nonprofit GP or nonprofit owner | executive director, CFO, board chair | SOS officers; Form 990 Part VII | mission-partnership meeting | recap or JV; preservation capital; ROFR support | no distress script; no acquisition pitch unless invited | `nonprofit_partnership` |
| `housing_authority` / `government` | PHA or public body | development director | agency website | partnership only | RAD or conversion partner; development JV | do not expect a sale | `housing_authority_partnership` |
| HUD/USDA-assisted owner (overlay on any type above) | `hud_contract` or USDA program present | owner organization and management agent; HUD/HFA/RD account executive as process contact | HUD MF Assistance DB; USDA borrower record | owner letter; process call to AE | HAP renewal vs opt-out economics; 236 decoupling; 515 transfer with RA | do not contact tenants; do not represent HUD positions | `hud_usda_assisted_owner` |
| `lender_reo_receiver` | ROUTING events (TRUSTEES_DEED, RECEIVER_APPOINTED, SPECIAL_SERVICING, BANKRUPTCY) | receiver, special servicer, debtor's counsel, REO asset manager | court order; CMBS IRP; PACER | register as qualified buyer; IOI | speed, no financing contingency, as-is | owner_outreach = false; counsel_only when bankruptcy active | `receiver_lender` |

Templates live in `assets/outreach-templates/<template id>.md`; compliance gating in `outreach-and-compliance.md`.

## 6. SOS worklist specification

`scripts/make_handoffs.py` writes `sos_worklist.csv` (one row per distinct owner entity among the exported tiers whose decision maker is still `not in public record`) and `documents_to_request.csv` beside the sibling payloads; the brief's Verification Queue quotes both counts:

| column | content |
|---|---|
| `owner_name_raw` | as in source |
| `normalized_name` | upper, punctuation stripped, `LLC`/`L.L.C.` unified, `LIMITED PARTNERSHIP` -> `LP` |
| `state` | registry to search (OR, WA, or home state from foreign registration) |
| `registry_search_url` | registry search page from the pack `sources.md` (never a constructed deep link unless the pack verified the pattern) |
| `reason` | `gp_resolution`, `manager_resolution`, `status_check`, `sibling_cluster`, `foreign_followup` |
| `property_ids` | `;`-separated |

Fill results back into `leads.csv` columns `decision_maker_name`, `decision_maker_role`, `dm_source`, `contact_grade`, and emit `ENTITY_ADMIN_DISSOLVED`, `MANAGER_CHANGE`, `REGISTERED_AGENT_CHANGE` events when found.

## 7. Oregon and Washington registry notes

- Oregon SOS Business Registry: free search; returns status (Active / Inactive / Administratively Dissolved), registry date, next renewal, registered agent, principal place of business, and the managers (manager-managed) or at least one member (member-managed) per ORS 63.787; LPs list every general partner per ORS 70.610; nonprofits list president/secretary and directors. Administrative dissolution follows roughly 45 days after a missed annual report; reinstatement allowed within 5 years. Bulk "Active Businesses - ALL" dataset on data.oregon.gov lacks member/manager roles. Site not reachable from this build environment; `verified_live=false`.
- Oregon SOS UCC search: free uncertified search by debtor; collateral text reveals pledged membership interests (mezz/pref) and rate-cap agreements (bridge debt). Fixture filings may instead be in county real-property records (ORS 79.0501).
- Washington: Corporations and Charities Filing System (WA SOS) for Clark County entities; WA Department of Licensing for UCC. URLs to be confirmed in the pack checklist.
- Foreign (DE/CA/WA) entities show only the Oregon foreign registration; follow the registered agent / principal office to the home-state filing via OpenCorporates (officer coverage partial; confirm in the official record).
- Oregon death records are confidential for 50 years (ORS chapter 432; ORS 432.350 is believed to be the operative section, verify): principal death is detected via probate dockets (OJD Smart Search PR cases), obituaries and SSDI mirrors, not vital records.

## 8. Individual skip tracing (class 1 only)

Permitted only for `sfr_small_res`, Tier A or B, through a licensed vendor (BatchData, REISkip, PropStream, PropertyRadar; TLOxp/idiCORE/Tracers only with GLBA/DPPA credentialing). Carry the vendor's DNC and litigator flags verbatim into the lead; corroborate the match on mailing address before dialing; never collect or store age, voter registration or household composition. The user's existing off-market-sourcing-system skip-trace evidence-chain contract applies unchanged.

## 9. What not to do

- Do not present a registered agent, property manager or attorney as the owner.
- Do not infer a decision maker from a LinkedIn profile alone; it can corroborate a filing but cannot be the primary evidence.
- Do not contact tenants or use tenant complaint records in a way that could be read as facilitating retaliation.
- Do not skip-trace institutional, nonprofit or government officers to personal numbers; use business channels.
