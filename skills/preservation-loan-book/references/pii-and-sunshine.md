# PII and Sunshine Policy

The agency's working file is a public record the day it is created. This pack therefore produces, by default, nothing it could not defend disclosing, and it never collects the categories that would make disclosure harmful. There is no skip tracing, no personal phone or email on any output, and tenant-level data never enters the pipeline. `plb/pii.py` enforces the policy on every CSV, JSON, workbook and markdown writer; `test_pii.py` asserts it.

Legal footing (Oregon; verify current text, counsel review recommended before finalizing packet language): ORS 192.311-192.431 (Public Records Law); ORS 192.345 conditional exemptions (public-interest balancing); ORS 192.355(2) exemption for information of a personal nature whose disclosure would be an unreasonable invasion of privacy absent clear and convincing public interest — Oregon DOJ treats personal contact information (home address, personal phone, personal email) under this paragraph. HUD tenant data (TRACS / HUD-50059) is excluded by design and never a pipeline input. `verified_live: false` for every cite in this build.

## Contents

1. Scopes
2. Column classes
3. Redaction rules for the public packet
4. Natural-person owners
5. Notice address and registered agent
6. What is never collected
7. records_classification and the manifest
8. How this differs from the buyer-side pack

---

## 1. Scopes

`pii_scope` in {`public_packet`, `organization` (default), `internal`}. Set by `--board-packet` (public_packet, second workbook + `board_packet.md`), the default, or `--internal`. Recorded in `manifest.json` and on every lead row.

| scope | audience | what prints |
|---|---|---|
| `public_packet` | board, council, commission, public meeting | allow-list only (Section 3), with redaction and a Redaction_Log |
| `organization` | the agency's asset managers, compliance staff, counsel | everything except INTERNAL columns; owner organizations, management agents, registered agents (as service addresses), `am_officer` name and role |
| `internal` | the asset manager's own file, agency records retention permitting | adds `am_officer_email` and `officer_names` drawn only from public filings (SOS officers / directors, Form 990 Part VII) |

## 2. Column classes

| class | columns | treatment |
|---|---|---|
| NEVER | `owner_phone`, `owner_email`, `cell`, `personal_email`, `decision_maker_name`, `skip_trace_*` (any vendor output) | dropped at adapter write; never a lead column; the HUD Sec 8 adapter's `owner_main_phone_number_text` alias may remain for join but is never written |
| INTERNAL | `am_officer_email`, `officer_names` | written only with `--internal` |
| ORGANIZATION | everything else: property identity, programs, units, dates and bases, owner organization, developer, management agent, registered agent and business address, notice_address + source, sos_status, `am_officer` (name and role), routes, interventions, cites, flags, book columns (ids, upb, maturity, covenant_status) | default |
| PUBLIC_PACKET allow-list | property identity (name, address, jurisdiction), programs, units*, dates and bases, owner organization, registered_agent (+ business address), route, intervention, statutory_cite, flags, Board_Totals, Status_Flips, Sponsor_Exposure | with Section 3 redactions |

`am_officer` is organization scope on purpose: a public employee's assignment on a loan file is a public record and the watchlist is useless without it. Their email is internal.

## 3. Redaction rules for the public packet

`apply_pii_scope(df, "public_packet")`:

1. Drop every column not on the allow-list (book `upb` detail rows are aggregated into Board_Totals; per-loan UPB is not in the packet unless the agency elects otherwise in `agency-profiles.yaml` `pii_level_public_packet`).
2. `is_natural_person(owner_name)` (surname-comma pattern such as "Bell, David"; or `infer_owner_type` individual_* with no entity tokens) -> print "individual owner (name withheld; see internal file)".
3. Residential registered-agent address heuristics (Apt / Unit / # tokens, address equal to the owner mailing address, no Suite / Ste / Floor token) -> omit the address, keep the agent name only when it is an entity.
4. Every redaction writes a `Redaction_Log` row: field, rows redacted, cite (ORS 192.355(2) / 192.345, verify).
5. `board_packet.md` and the second workbook carry the banner "Prepared for public meeting; personal information redacted under ORS 192.355(2) (verify)".

## 4. Natural-person owners

OHCS individual owner names (e.g. Yards at Union Station B "Bell, David"; Fifth Avenue Place Apts "Menashe, Michael") are public record and print in `organization` scope without any contact detail. In `public_packet` scope they are redacted per Section 3. No individual is ever skip-traced, and no mailing address for an individual is carried beyond the property address; the notice address for an individual owner comes from the regulatory agreement or HAP contract in the agency's file (Section 5).

## 5. Notice address and registered agent

The registered agent is the service address for statutory notices, which is why it prints at organization level and in the packet (as an entity). Order for `notice_address` / `notice_address_source`: `regulatory_agreement` > `hap_contract` > `loan_docs` (the agency's own file) > `sos_registered_agent` (with `Verify — Notice Address`) > `unknown`. Every intervention letter prints the address and its source. A registered agent is never presented as the owner (`sponsor-resolution.md`).

## 6. What is never collected

- Skip-trace vendor output of any kind; personal phones, cells, personal emails; relatives, deceased flags, age, voter data, household composition.
- Tenant-level data: names, incomes, certifications, TRACS / HUD-50059, complaint or FED records. Tenant counts (units, HAP households) are aggregates from the inventory and the contract, never from tenant files.
- Officer names from anything other than public filings (no social-media or data-broker sources).

## 7. records_classification and the manifest

Every run writes `records_classification` into `manifest.json`, the workbook Summary and the brief: "agency working file; disclosable subject to ORS 192.345/192.355 review; tenant data excluded by design". `pii_scope` is recorded beside it. The `Notes` free-text column that v2 carried on the Targets tab is removed (free text in a public record is unreviewable); the `AM status` dropdown replaces it.

## 8. How this differs from the buyer-side pack

off-market-deal-finder resolved owners to named decision makers and permitted licensed skip tracing of individual SFR owners. This pack resolves owners to organizations and notice addresses only, keeps `org_resolution_grade` A/B/C for how well the organization is resolved, and never names a natural person except as the owner of record already printed in a public inventory. `references/sponsor-resolution.md` Section 9 is the operational checklist.
