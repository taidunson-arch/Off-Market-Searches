# Sponsor Resolution

How the skill turns an owner-of-record string into a resolved organization with a notice address and an intervention owner at the agency, and how it classifies owners for the sponsor-capacity factor. This replaces v2's decision-maker enrichment: the agency does not need a named person to call; it needs the entity, the GP or managing member role, the registered agent as a service address, the address its own regulatory agreement names for notices, and a grade for how well the organization is resolved. No individual is skip-traced and no personal contact detail is collected (`pii-and-sunshine.md`).

## Contents

1. Principles
2. owner_type inference rules
3. Resolution chain
4. Organization resolution grades
5. Archetype table: capacity reading, default route, intervention owner
6. Notice-address order
7. SOS worklist specification
8. Oregon and Washington registry notes
9. What not to do

---

## 1. Principles

- Resolve to an organization and a role, never to a person: `GP managing member`, `nonprofit executive director`, `PHA development director`, `receiver`, `HUD contract administrator`. The role determines the intervention owner at the agency and the salutation on a letter; the organization and its notice address determine where the letter goes.
- The registered agent is never the owner. It is a service address, and for statutory notices (PuSH demand, records request) it is a valid one when the agency's own file has nothing better (`Verify — Notice Address`).
- Write `not in public record` rather than guessing. A grade C organization (entity + principal office) is a usable notice target; a fabricated name is not.
- Prefer the agency's own file over every public source: the regulatory agreement, HAP contract, loan documents and grant agreement name the owner entity, its GP, the management agent and the notice address.
- Every hop is logged in `sponsor_contact_role` and the worklist `reason`; the chain is auditable.

## 2. owner_type inference rules

Applied in order; first match wins. Inputs: HFA `Owner Name`, `Owner Type` where provided (OHCS: 43% of rows, mixed case), HUD `owner_organization_name`, LIHTC `NON_PROF`, Developer / Management names, the servicing extract's property owner, SOS entity type, and the profile's `self_owner_tokens`.

| order | rule | owner_type |
|---|---|---|
| 0 | name matches the profile's `self_owner_tokens` (pha_am: "Home Forward", "Housing Authority of Portland") | `self_owned` |
| 1 | court-appointed receiver, special servicer, trustee's-deed grantee, REO vesting | `lender_reo_receiver` |
| 2 | tokens `Housing Authority`, `Home Forward`, `HACSA`, `Housing Works`, or Owner Type `Housing Authority` | `housing_authority` |
| 3 | tokens `City of`, `County of`, `State of`, `Metro`, `Urban Renewal`, `Prosper Portland`, or Owner Type `Government` | `government` |
| 4 | Owner Type `Non-Profit` (any case), LIHTC `NON_PROF = 1`, or tokens `Inc`, `Corp`, `Community`, `Foundation`, `Ministries`, `Catholic`, `Lutheran`, `Habitat`, `CDC`, `Housing Development Corp`, `Neighborhood`, `Services` with no `LLC/LP` token and no for-profit developer | `nonprofit`; an LP / LLC whose GP or manager is a nonprofit (SOS or Developer Name) -> `lihtc_partnership_nonprofit_gp` |
| 5 | tokens `LP`, `L.P.`, `LLLP`, `Limited Partnership`, or `LLC` with LIHTC programs and Owner Type `For-Profit` / `Limited Dividend` / `Profit` / blank, and the developer is not a nonprofit | `lihtc_partnership_forprofit_gp` |
| 6 | `LLC`/`LP` with no regulatory programs; SOS principal office shared with 3+ other property-owning entities or a management company | `regional_operator` |
| 7 | `LLC`/`LP` with no regulatory programs; single entity | `single_asset_llc` |
| 8 | REIT, fund, pension, insurance company, national operator | `institutional` |
| 9 | `Trust`, `Trustee`, `Estate of`, `Family LP`, `Living Trust` | `trust_estate` |
| 10 | individual name(s) (surname-comma pattern such as "Bell, David"); occupancy is not inferred — "absentee" is an acquisition-sourcing label with no meaning for a 5+ unit regulated asset | `individual_owner_of_record` |
| 11 | (reserved) | |
| 12 | anything else | `unknown` (signal `owner_type_unknown`; SOS worklist) |

OHCS specifics: `Owner Type` values `PROFIT` -> For-Profit, `NON-PROFIT` -> Non-Profit, `HOUSING AUTHORITY`, `GOVERNMENT`, `Limited Dividend` (treat as for-profit). Blank in 1,039 of 1,819 rows (443 of 810 metro: 172 with LLC / LP tokens in Owner Name, 236 with a blank Owner Name that are HUD-contract-only rows whose owner comes from the HUD Sec 8 `owner_organization_name`). Infer from `Owner Name`, then `Developer Name`, then `Management Name` (a nonprofit manager does not make the owner a nonprofit; a nonprofit developer of an LP usually does make it the GP).

`owner_archetype` is the Section 5 row id derived from `owner_type` plus overlays: `hud_usda_assisted` when `hud_contract` or `USDA_515` is present; `book_risk` when a ROUTING HARD_DISTRESS event is present; `self_owned` when rule 0 fired.

## 3. Resolution chain

Stop at the first hop that yields grade A; record every hop tried.

| hop | source | what you get |
|---|---|---|
| 1 | the agency's own file: regulatory agreement / LURA / REUA, HAP contract, loan and grant documents, 8609 Part II in the compliance file | owner entity, GP, management agent, **notice address** (`notice_address_source` regulatory_agreement / hap_contract / loan_docs), signatory roles |
| 2 | HFA / HUD record | OHCS `Owner Name` / `Developer Name` / `Management Name`; HUD `owner_organization_name`, `mgmt_agent_org_name`; USDA borrower |
| 3 | State business registry (Oregon SOS; WA SOS; home state via OpenCorporates for foreign entities) | status, registry date, registered agent (service address, `sos_registered_agent`), principal office, managers or at least one member (LLC), every general partner (LP), officers / directors (nonprofit), annual-report history; follow the GP LLC once |
| 4 | Nonprofit filings | IRS Form 990 Part VII officer roles (executive director, CFO, board chair) — roles only on default outputs; names only with `--internal` |
| 5 | Court and servicing records | receiver and lender counsel, special servicer, debtor's counsel (PACER); these replace the owner as the notice counterparty |

The recorder image purchase is no longer a routine hop: the agency already holds the instruments for its own book, and for universe_not_held properties the recorded LURA / Notice of ROFR goes on `documents_to_request.csv` only when a specific question needs it.

Corroboration to grade A: agency-file entity == SOS entity with Active status; SOS GP == LURA GP; HUD owner org == SOS entity. Conflicting names across hops -> `Verify — Conflicting Sources` on `owner_name` and grade B.

Sponsor mapping (feeds `sponsor_cliff_count` and the Sponsor_Exposure tab): cluster entities by normalized owner organization (case-folded), then by shared registered agent, principal office and manager names across SOS; count properties with a cliff inside 36 months and sum public UPB; flag `sponsor_concentration` when UPB share >= 10% or 3+ cliffs in 36 months.

## 4. Organization resolution grades

`org_resolution_grade` replaces v2's contact grade. It grades how well the organization and its notice address are resolved, not whether a person can be reached.

| grade | definition | typical evidence | usable for |
|---|---|---|---|
| `A` | owner entity confirmed Active in the registry AND the notice address comes from the agency's own regulatory agreement / HAP contract / loan documents (or two independent public filings agree) | agency file + SOS Active; SOS GP == LURA GP | statutory notices and demand letters as written |
| `B` | entity from one filing, or notice address from the SOS registered agent only | SOS annual report only; HUD owner org only | letters to the role at the principal office; `Verify — Notice Address` printed |
| `C` | entity string plus a mailing address only, or registry status Inactive / Administratively Dissolved | inventory record only | SOS worklist first; letter to the entity asking for the right role; ENTITY_ADMIN_DISSOLVED event |

LP annual reports are understood to list every general partner (ORS 70.610) and member-managed LLCs at least one member (ORS 63.787); verify the current text and the SOS annual-report form, since grade A for LIHTC partnerships rests on the LP rule.

## 5. Archetype table: capacity reading, default route, intervention owner

| owner_type | detection | organization role to address | capacity reading (public interest) | default route | intervention owner at agency | typical interventions |
|---|---|---|---|---|---|---|
| `lihtc_partnership_forprofit_gp` | LP / LLC with LIHTC programs, for-profit or Limited Dividend GP | GP managing member (SOS LP record lists every GP); syndicator asset manager as LP | preservation risk at Year 15 / 30; LP may have traded to an aggregator; sponsor_capacity 6 at Year 15, +8 on LP / GP change | notice_compliance (prep -> demand); designee_rofr on notice; qc_admin (hfa) on a QC request | push_program_manager; compliance_officer; legal_counsel | push_window_prep, push_notice_demand_letter, push_records_request, rofr_notice_recording, qc_request_acknowledgement |
| `lihtc_partnership_nonprofit_gp` / `nonprofit` | nonprofit GP or nonprofit owner | executive director / CFO (roles) | mission partner with 42(i)(7) ROFR standing and recap capacity; sponsor_capacity 6 | ta_sponsor; nofa_offer | nofa_program_manager; push_program_manager | ta_sponsor_engagement, preservation_nofa_invitation, rofr_assignment_memo |
| `housing_authority` / `government` (not self) | PHA or public body | development director (role) | partner; RAD / Section 18 / mixed-finance recap; sponsor_capacity 6; never capped | ta_sponsor; recap_committee when in book | nofa_program_manager; am_officer | ta_sponsor_engagement, pha_repositioning (as partner), loan_extension_recast_memo |
| `self_owned` | profile `self_owner_tokens` | our own asset management | capacity is ours; sponsor_capacity 6; RAD / Section 18 +4 | recap_committee; servicing_watch | pha_development; am_officer | pha_repositioning, loan_extension_recast_memo, prac_renewal_coordination |
| `institutional` | REIT / fund / aggregator | asset manager (role) | aggregator posture; Year-15 litigation risk; out-of-state +4 | notice_compliance; designee_rofr | legal_counsel; push_program_manager | push_notice_demand_letter, rofr_notice_recording, lihtc-lpa-reviewer handoff |
| `single_asset_llc` / `regional_operator` (regulated) | LLC / LP with a program but no LIHTC partnership structure | managing member / principal (role) | for-profit holder of a HAP or soft-program property; opt-out or exit risk | optout_response (HAP); notice_compliance | pbca_liaison; push_program_manager | optout_tenant_notice_check, optout_response_plan, push_window_prep |
| HUD / USDA-assisted owner (overlay) | `hud_contract` or USDA program present | owner org and management agent; HUD / RD as decision-makers | the agency is the CA / AE counterpart or eligible public body | optout_response; prac_renewal_coordination; usda_prepay_response; hud_legacy_response | pbca_liaison; hud_mf_asset_manager; rd_state_office | as named |
| `lender_reo_receiver` | ROUTING HARD_DISTRESS events | receiver / special servicer / debtor's counsel | book risk; covenant extinguishment at foreclosure (HOME 92.252, verify) | recap_committee (workout) | legal_counsel; am_officer | loan_extension_recast_memo (workout), covenant_recapture_review; compliance gate counsel_only |
| `individual_*` | individual name on the inventory | owner of record (organization-level letter; no contact detail) | public-record name; redacted in the board packet | per events | push_program_manager | letters to the notice address in our file only |
| `trust_estate` | trust / estate tokens | trustee (role) | | per events | legal_counsel | |
| `unknown` | nothing matched | — | 0 points; signal owner_type_unknown | per events | compliance_officer | SOS worklist |

## 6. Notice-address order

`notice_address` / `notice_address_source`: (1) `regulatory_agreement` (LURA / REUA / local covenant in the agency file), (2) `hap_contract`, (3) `loan_docs` (note, trust deed, grant agreement), (4) `sos_registered_agent` with `Verify — Notice Address`, (5) `unknown` (letter held; SOS worklist). Every intervention letter prints the address and its source. A REGISTERED_AGENT_CHANGE or ENTITY_ADMIN_DISSOLVED event forces re-confirmation before any letter.

## 7. SOS worklist specification

`scripts/make_handoffs.py` writes `sos_worklist.csv` (one row per distinct owner organization among the exported routes whose `org_resolution_grade` is C or whose `owner_type` is unknown) beside the sibling payloads; the brief's Verification Queue quotes the count.

| column | content |
|---|---|
| `owner_name_raw` | as in source |
| `normalized_name` | upper, punctuation stripped, `LLC` / `L.L.C.` unified, `LIMITED PARTNERSHIP` -> `LP` |
| `state` | registry to search (OR, WA, or home state from foreign registration) |
| `registry_search_url` | registry search page from the pack `sources.md` (never a constructed deep link) |
| `reason` | `gp_resolution`, `manager_resolution`, `status_check`, `sibling_cluster`, `foreign_followup`, `notice_address` |
| `property_ids` | `;`-separated |

Fill results back into `leads.csv` columns `registered_agent`, `registered_agent_address`, `sos_status`, `notice_address` (+ source), `sponsor_contact_role`, `org_resolution_grade`, and emit `ENTITY_ADMIN_DISSOLVED`, `MANAGER_CHANGE`, `REGISTERED_AGENT_CHANGE` events when found. Confirmed book joins go into `book_crosswalk.csv`.

## 8. Oregon and Washington registry notes

- Oregon SOS Business Registry: free search; returns status (Active / Inactive / Administratively Dissolved), registry date, next renewal, registered agent, principal place of business, and the managers (manager-managed) or at least one member (member-managed) per ORS 63.787; LPs list every general partner per ORS 70.610; nonprofits list president / secretary and directors. Administrative dissolution roughly 45 days after a missed annual report; reinstatement within 5 years. Bulk "Active Businesses - ALL" on data.oregon.gov lacks roles. Site not reachable from this build; `verified_live=false`.
- Oregon SOS UCC search: free uncertified search by debtor; collateral text reveals pledged membership interests (UCC_MEZZ_PLEDGE).
- Washington: Corporations and Charities Filing System (WA SOS) for Clark County entities; URLs to confirm in the pack checklist.
- Foreign (DE / CA / WA) entities show only the Oregon foreign registration; follow the registered agent / principal office to the home-state filing via OpenCorporates and confirm in the official record.

## 9. What not to do

- Do not present a registered agent, property manager or attorney as the owner; print the agent as the service address it is.
- Do not skip-trace anyone; do not collect personal phones, cells, personal emails, age, voter or household data.
- Do not name a natural person on a default output except as the owner of record already printed in a public inventory, and redact that in the board packet.
- Do not infer an organization's officers from social media; use SOS and Form 990 roles only, and names only with `--internal`.
- Do not contact tenants or use tenant records; units and households are counted from the inventory and the contract.
- Do not send a statutory letter to an address whose source is `unknown`; resolve first.
