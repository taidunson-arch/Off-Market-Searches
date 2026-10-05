# Outreach and Compliance

What to say, through which channel, to which archetype, and which legal gates must clear first. Compliance gates are listed on every lead card before any contact field so the person running outreach sees the constraint before the phone number. Statute text was confirmed from full-text mirrors for ORS 86 and ORS 646 and from search snippets for the rest; re-verify before relying on a specific figure (see `sources/oregon-portland/legal-timelines.md`).

## Contents

1. Per-archetype outreach matrix
2. Compliance gates
3. buyer_profile gating
4. Channel rules
5. Cadence and sequencing
6. Language that is never used

---

## 1. Per-archetype outreach matrix

| archetype (template id) | first-touch channel | angle | second touch | do not |
|---|---|---|---|---|
| `individual_or_trust` | letter (plain, one page, no dollar figures) | "You may be weighing options for [address]; we buy as-is, close on your timeline, cover closing costs." Tax-strategy content for long holds (1031, installment, DST). | DNC-scrubbed call to a landline/business number 10-14 days later; door knock only if local and not in foreclosure | price in first touch; references to foreclosure status in the envelope or opening line; contacting a DNC number; texts without consent |
| `estate` | letter to the personal representative or estate counsel, 60-120 days after letters issue | "We work with families settling estates; one buyer, one closing, no repairs." | call to counsel's office | contact before letters testamentary; contacting heirs directly when counsel is on the docket; any mention of the decedent's debts |
| `single_asset_llc` | letter to the principal office addressed to the managing member by name (grade A) or by role (grade B) | maturity math: "loans originated 2016-2019 are repricing; we can close before [quarter] and assume or retire the debt." Regulatory fatigue for Portland Class B/C. | call to business line; LinkedIn message only to corroborate contact | personal cell without consent; addressing the registered agent |
| `regional_operator` | direct principal email or call (business) | portfolio liquidity; trade one asset to fund another; off-market certainty | meeting | approaching during a live broker exclusive without the broker |
| `institutional` | formal IOI through the dispositions or asset-management contact | certainty of close, debt assumption, no financing contingency | follow their process | retail letters; unsolicited price talk below their basis |
| `lihtc_gp_year15` | letter to the GP managing member; courtesy call to the syndicator asset manager | Year 15: fund the LP exit, GP buyout or resyndication; Year 30: preservation purchase or conversion partner. Acknowledge ROFR and qualified-contract mechanics explicitly. | GP meeting; model the resyndication | contacting tenants; implying the agency's position; pressuring on QC timing |
| `nonprofit_partnership` | request a meeting with the executive director or CFO | recapitalization or JV; preservation capital; support for their §42(i)(7) ROFR; development partnership | board-level introduction | distress scripts; acquisition pitch unless invited; approaching staff below ED/CFO |
| `housing_authority_partnership` | letter or email to the development director | RAD / conversion partner; mixed-finance JV; disposition partner if they are disposing | agency process | expecting a sale; lobbying board members |
| `hud_usda_assisted_owner` | owner letter plus process call to the HUD/HFA/RD account executive | HAP renewal vs opt-out economics (Mark-Up-to-Market), 236 decoupling, 515 transfer with RA, M2M note treatment | owner meeting with the AE informed | contacting tenants; representing HUD or RD positions; suggesting opt-out as a tactic |
| `receiver_lender` | register as a qualified buyer with the receiver / special servicer / debtor's counsel | speed, as-is, no financing contingency, proof of funds | track sale motions; bid | contacting the owner (owner_outreach = false); contacting a bankrupt debtor other than through counsel |

## 2. Compliance gates

Gate ids are what `compliance_gates` carries on the lead. Scripts attach them from triggers; the analyst confirms them before contact.

| gate id | trigger | rule | source (verify status) |
|---|---|---|---|
| `dnc_scrub` | any phone or text channel, any class | Scrub against the National DNC Registry, which Oregon designates as its state list (ORS 646.572); calling a registered number is an unlawful trade practice (ORS 646.569 -> 646.608). ORS 646.561 (amended 2025) includes text messages in "telephone solicitation". Keep an internal DNC. TCPA: prior express written consent for autodialed, prerecorded or AI-voice calls and texts to cells; 8am-9pm local; $500-$1,500 per violation. Whether a buy-side offer is a "solicitation" is unsettled, so scrub regardless. | ORS 646.561-.574 (full text mirror read); TCPA (knowledge, verify) |
| `consent_capture` | before any text or automated call | Written consent recorded with date, channel and scope. | TCPA / FCC rules (verify current one-to-one status) |
| `wholesaler_registration` | `buyer_profile == wholesaler`, class 1 (`score_leads.py --buyer-profile wholesaler` attaches it automatically) | Oregon HB 4058 (2024): residential property wholesalers must register with the Oregon Real Estate Agency from 2025-01-01, give written disclosures to sellers and buyers, and honor a seller cancellation right; criminal penalties up to 364 days / $6,250 plus civil penalties. Principals buying for their own account are exempt. Inject the disclosure text into class 1 templates. | HB 4058 chaptered (digest verified via mirror); fee / cancellation-period details unverified |
| `equity_purchaser_rules` | any pre-foreclosure lead (NOD_RECORDED, NOTS_RECORDED, TRUSTEE_SALE_EARLIEST) where a leaseback, option or "we help you avoid foreclosure" structure is contemplated | Oregon Mortgage Rescue Fraud Protection Act (ORS 646A.702 et seq.) and Washington Distressed Property Conveyances Act (RCW 61.34) impose contract contents, cancellation rights and fiduciary-type duties on equity purchasers and distressed-home consultants. Counsel review before outreach language is finalized. | not re-read this build; verify with counsel |
| `probate_cooling` | PROBATE_FILED | No contact until letters testamentary / of administration have issued and at least 60 days have passed; 60-120 days is the window; address the PR or counsel. | practice standard |
| `preservation_law` | class 3, Oregon: any property meeting ORS 456.250 (5+ units with a HUD/USDA/OHCS affordability contract) | Owner notices to OHCS and local government 36-30 and 30-24 months before expiration (OAR 813-115); withdrawal no sooner than 30 months after notice; qualified purchasers (OHCS, local government, OHCS designee) may record a Notice of Right of First Refusal and have 30 days to match a third-party offer, which the owner must accept (ORS 456.263); tenant notice 12-14 months (SB 973 raises to 30 months in five languages, operative 2026-01-01 for restrictions ending on/after 2028-07-01). Any PSA with a non-qualified buyer is subject to the match. ROFR duration (24 vs 36 months) unresolved. | ORS 456.250-.265, OAR 813-115, SB 973 (snippets; verify current text) |
| `fair_housing_tenant_data` | any use of tenant complaint, eviction (FED) or habitability records | Use only to assess owner motivation; never to screen, contact or evaluate tenants; never in a way that could facilitate retaliation. | FHA / ORS 659A (knowledge) |
| `counsel_only` | BANKRUPTCY_FILED active | Automatic stay; contact only debtor's counsel or trustee. | 11 U.S.C. 362 (knowledge) |
| `lihtc_tenant_protections` | class 3 with LIHTC_EXTENDED_USE_END or QC_ELIGIBILITY inside horizon | 3-year decontrol after extended use ends: no eviction without good cause and no non-§42 rent increases for existing tenants (IRC 42(h)(6)(E)(ii)); enhanced vouchers at Section 8 opt-out; USDA 515 prepayment requires RD approval, advance tenant notice (period per 7 CFR part 3560 subpart N; verify) and restrictive-use provisions. Underwrite with these in place. | IRC 42; HUD / RD rules (knowledge; verify) |
| `broker_exclusive` | LISTING_WITHDRAWN within 12 months or a known listing agreement | Confirm the exclusive has lapsed before direct principal contact (procuring-cause exposure). | practice standard |
| `assumption_approval` | `assumable_debt == true` | HUD and agency assumptions need lender/HUD approval (TPA); do not represent assumption as certain. | HUD / agency rules (knowledge) |

## 3. buyer_profile gating

| buyer_profile | effect on templates and routes |
|---|---|
| `principal` | default; class 1 templates omit HB 4058 text |
| `wholesaler` | class 1 templates inject the HB 4058 registration disclosure and seller cancellation language; `wholesaler_registration` gate on every class 1 lead; class 2/3 unaffected by HB 4058 but assignment language still disclosed |
| `nonprofit_preservation` | enables the OHCS-designee strategy in class 3: templates reference qualified-purchaser status, ROFR support and preservation capital; `partnership_preservation` leads are primary, not secondary; `score_leads.py` adds the `designee_strategy` signal |
| `qualified_purchaser` | user is OHCS, an affected local government or an appointed designee: templates cite ORS 456.262-.263 rights; `rofr_encumbered` becomes an advantage flag rather than a constraint |

## 4. Channel rules

- Mail is the default first touch for every archetype except `institutional`, `regional_operator` and `receiver_lender`.
- Phone: business lines for entities; individuals only after `dnc_scrub` and only to numbers the licensed vendor did not flag; no texts without `consent_capture`.
- Email: only to addresses from official filings, firm websites or prior correspondence; no scraped personal addresses.
- In-person: never for pre-foreclosure, probate or tenant-occupied units without an appointment.
- No dollar figures in a first touch for individuals, estates and single-asset LLCs; price conversations start after the owner responds.

## 5. Cadence and sequencing

| archetype | touches | spacing | stop rule |
|---|---|---|---|
| individual / trust / estate | 3 letters + 1 call | 3-4 weeks | any "no"; DNC flag; property sold or lead retired |
| single_asset_llc / regional_operator | letter, call, meeting request | 2-3 weeks | explicit decline; active listing (route excluded) |
| lihtc_gp_year15 | GP letter, LP courtesy call, GP meeting | 3-4 weeks; begin 24-36 months before Year 15/30 | ROFR exercised; resyndication closed |
| nonprofit / housing authority | meeting request, follow-up, board intro | 4-6 weeks | they say the asset is not in play |
| hud_usda_assisted_owner | owner letter + AE call in the same week | per HAP timeline; 12+ months before expiration | 20-year MAHRA renewal executed |
| receiver_lender | register, then follow the docket | per court/servicer schedule | sale approved to another party |

Timing anchors: class 1 Oregon NOD leads days 15-90 after recording; Washington NOTS leads immediately; class 2 maturities 9-18 months out, agency YM windows ~6 months out; class 3 Year 15/30 and HAP 24-36 months out, matching the PuSH notice windows.

## 6. Language that is never used

- "Avoid foreclosure", "save your home", "we can stop the sale" (equity-purchaser statutes).
- Any statement of what HUD, OHCS, RD or a lender will or will not approve.
- Any reference to the owner's age, health, family situation or the decedent's debts.
- Any price, discount percentage or "cash offer of $X" in a first touch to an individual, estate or single-asset LLC.
- Any text message to a number without recorded consent.
