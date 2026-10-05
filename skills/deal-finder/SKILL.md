---
name: deal-finder
description: >
  Source investment properties through two pipelines: off-market (pre-foreclosures, probate, 
  tax delinquencies, absentee owners) and on-market (LoopNet, Zillow, Redfin, CoStar, or 
  any listing site). Off-market mode produces ranked leads with motivation scores and contact 
  info via `off-market-deal-finder`. On-market mode searches listing sites, collects property data, runs batch DCF 
  valuations, and produces a comparative screening package with Strong Buy / Buy / Hold 
  verdicts. Outputs JSON + Excel. Use whenever the user mentions "find deals", "deal 
  pipeline", "source properties", "search LoopNet", "search Zillow", "what's for sale in 
  [city]", "off-market leads", "on-market listings", "screen deals", "batch valuation", 
  "DCF analysis on listings", "pre-foreclosure", "absentee owners", or needs to build an 
  acquisition pipeline in a target market.
---

# Deal Finder (Off-Market + On-Market)

Two deal sourcing pipelines in one skill. **Off-market mode** mines public records for 
distressed and motivated seller signals. **On-market mode** searches listing sites, scrapes 
property data, and builds a comparative investment screening package with DCF valuations.

The user can run either mode or both for the same market.

## When to Use

**Off-market mode:**
- Building a direct-to-seller acquisition pipeline outside the MLS
- Identifying pre-foreclosure properties before they go to auction
- Finding absentee owners or probate properties
- Targeting tax delinquent parcels with significant equity

**On-market mode:**
- Searching listing sites for properties matching investment criteria
- Screening 10-20+ candidates simultaneously instead of one at a time
- Building a comparative DCF package for an investment committee
- Entering a new market and need to survey what's available
- Comparing yields, price/sqft, and cap rates across a batch of listings

## Mode Selection

| Trigger | Mode |
|---------|------|
| User mentions pre-foreclosure, probate, tax delinquent, absentee, off-market, loan maturity, expiring LIHTC/HAP | **Off-market → hand off to `off-market-deal-finder`** |
| User mentions LoopNet, Zillow, listings, for sale, search for properties | **On-market** |
| User mentions both or says "find deals in [city]" without specifying | **Ask which mode** |

## Inputs — Off-market Mode

Not taken here. Off-market requests are handed to `off-market-deal-finder`, which owns the signal catalogs, scoring and inputs for SFR, market-rate and affordable multifamily.

## Inputs — On-market Mode

| Parameter | Type | Required | Description |
|---|---|---|---|
| target_market | string | Yes | City, state, or geographic area to search |
| property_type | string | Yes | office, multifamily, retail, industrial, mixed-use, SFR |
| listing_source | string | No | LoopNet, Zillow, Redfin, CoStar, Rightmove, or "any" (default: web search) |
| max_price | number | No | Maximum listing price filter |
| min_price | number | No | Minimum listing price filter |
| min_sqft | number | No | Minimum square footage |
| max_results | number | No | Target number of listings to analyze (default: 12) |
| dcf_discount_rate | number | No | Discount rate for DCF valuations (default: 8.0%) |
| dcf_rental_growth | number | No | Annual rental growth assumption (default: 3.0%) |
| dcf_exit_cap | number | No | Terminal cap rate for DCF exit (default: 6.5%) |
| dcf_hold_period | number | No | Investment horizon in years (default: 10) |
| dcf_void_allowance | number | No | Annual vacancy provision (default: 5%) |
| dcf_mgmt_cost_pct | number | No | Management fee as % of rent (default: 5%) |
| dcf_capex_reserve_pct | number | No | Capex reserve as % of rent (default: 3%) |

## Off-Market Process

For off-market sourcing (pre-foreclosure, probate, tax delinquency, loan maturity, LIHTC/HAP expirations) use `off-market-deal-finder`; this skill covers on-market listing search and batch DCF only.

---

## On-Market Process

### Step OM-1: Search Listing Sites

Search for active listings matching the user's criteria. Use web search to find listings 
on the specified platform, then web_fetch to extract listing details.

**Search strategy by platform:**

```
LoopNet:     "[city] [property_type] for sale site:loopnet.com"
Zillow:      "[city] [property_type] for sale site:zillow.com"
Redfin:      "[city] commercial for sale site:redfin.com"
CoStar:      "[city] [property_type] for sale" (user may need to provide data)
General:     "[city] [property_type] for sale [year]"
```

Run multiple searches to maximize coverage. Target `max_results` listings (default 12). 
If a specific listing URL is provided, fetch it directly.

### Step OM-2: Extract Listing Data

For each listing found, extract all available data:

| Field | Source | Required |
|-------|--------|----------|
| Address | Listing | Yes |
| Asking Price | Listing | Yes |
| Square Footage | Listing | Yes |
| Property Type / Use | Listing | Yes |
| Year Built | Listing or web search | Preferred |
| Current Rent / NOI | Listing | If available |
| Cap Rate (listed) | Listing | If available |
| Occupancy | Listing | If available |
| Parking | Listing | If available |
| Lot Size | Listing | If available |
| Zoning | Listing or web search | If available |
| Tenure | Listing | If available (freehold/leasehold) |
| Brochure URL | Listing | Download if available |

Calculate derived metrics:
```
Price per Sqft = asking_price / sqft
Current Yield = (current_rent / asking_price) × 100  (if rent known)
Price per Unit = asking_price / unit_count  (if multifamily)
```

If rental income is not provided, estimate from market data:
```
Search: "[city] [property_type] average rent per sqft [year]"
Estimated Rent = sqft × market_rent_per_sqft
```
Flag estimated values explicitly.

### Step OM-3: Online Research Per Property

For each listing, search for additional intelligence:

```
Search: "[property address] planning applications"
Search: "[property address] news"
Search: "[property address] sold history"
Search: "[neighborhood] development projects"
```

Look for: planning applications (development upside), recent news, prior sale history 
(price trajectory), nearby development projects (appreciation catalysts), tenant 
information, and any red flags (structural issues, flooding, contamination).

### Step OM-4: Batch DCF Valuation

Run a 10-year discounted cash flow valuation for each property using the user's 
assumptions (or defaults):

```
For each property:
  Year 0: Acquisition at asking price
  
  Years 1-N:
    Gross Rent      = estimated_or_actual_rent × (1 + rental_growth)^(year-1)
    Less: Voids     = gross_rent × void_allowance
    Less: Mgmt      = gross_rent × mgmt_cost_pct
    Less: CapEx     = gross_rent × capex_reserve_pct
    Net Rent        = gross_rent - voids - mgmt - capex
  
  Year N Exit:
    Exit Value      = year_N_net_rent / exit_cap_rate
    Less: Selling Costs (2%)
    Net Reversion   = exit_value - selling_costs
  
  DCF Value = Σ(net_rent_yr / (1 + discount_rate)^yr) + net_reversion / (1 + discount_rate)^N
  
  Variance = DCF_value - asking_price
  Variance % = variance / asking_price × 100
```

Properties where DCF value exceeds asking price by >10% are flagged as undervalued.
Properties where asking price exceeds DCF value by >10% are flagged as overpriced.

### Step OM-5: Comparative Screening & Ranking

Rank all listings and assign verdicts:

| Metric | Weight | Scoring |
|--------|--------|---------|
| Current/Potential Yield | 30% | Highest yield = 10, scale to lowest = 1 |
| DCF Variance (value vs price) | 25% | Most undervalued = 10, scale to most overpriced = 1 |
| Price per Sqft (vs market avg) | 15% | Lowest $/sqft = 10, scale to highest = 1 |
| Development Upside | 15% | Planning consent + conversion potential = 10, none = 1 |
| Location Quality | 15% | Transport, amenities, tenant demand = 1-10 |

```
Composite Score = Σ(metric_score × weight)

Verdicts:
  Score ≥ 7.5: STRONG BUY — exceptional value or upside
  Score 5.5-7.4: BUY — solid opportunity, proceed to DD
  Score 3.5-5.4: HOLD — fairly priced, no urgency
  Score < 3.5: PASS — overpriced or weak fundamentals
```

### Step OM-6: Assemble Deal Package

Produce the complete deliverable:

**Excel Workbook (5 tabs):**

| Tab | Contents |
|-----|----------|
| Property Summary | All listings with price, size, $/sqft, yield, verdict. Sortable. |
| DCF Valuation | 10-year cash flow projection per property. Each property in a block. Assumptions at top in blue/yellow. DCF value, variance to asking price. |
| Comparison Analysis | Side-by-side with composite scores, component scores, and verdicts. Conditional formatting: green = Strong Buy, blue = Buy, yellow = Hold, red = Pass. |
| Market Context | Market rent ranges, cap rate benchmarks, vacancy rates, demand drivers for the target market. DCF assumptions documented. |
| Research Summary | Per-property online research findings: planning apps, news, tenant info, development potential. |

**Evaluation Report (.md or conversational):**
- Executive summary with market context
- Individual property analysis (1 paragraph each with key highlights and recommendation)
- Investment recommendations summary table
- Methodology notes and limitations

**Downloaded Brochures:** If brochure PDFs are available on listing pages, download them 
to `/home/claude/brochures/` and note file paths.

---

## On-Market Output — JSON Summary

```jsonc
{
  "mode": "on_market",
  "target_market": "string",
  "property_type": "string",
  "listings_found": "integer",
  "dcf_assumptions": {
    "discount_rate": 0.08,
    "rental_growth": 0.03,
    "exit_cap_rate": 0.065,
    "hold_period_years": 10,
    "void_allowance": 0.05,
    "mgmt_cost_pct": 0.05,
    "capex_reserve_pct": 0.03
  },
  "properties": [
    {
      "address": "string",
      "asking_price": "number",
      "sqft": "number",
      "price_per_sqft": "number",
      "current_yield_pct": "number | null",
      "potential_yield_pct": "number",
      "estimated_rent": "number",
      "rent_source": "listing | estimated",
      "dcf_value": "number",
      "dcf_variance_pct": "number",
      "composite_score": "number",
      "verdict": "STRONG BUY | BUY | HOLD | PASS",
      "key_highlights": ["string"],
      "risks": ["string"],
      "research_findings": "string"
    }
  ],
  "recommendations_summary": {
    "strong_buy": ["string — addresses"],
    "buy": ["string"],
    "hold": ["string"],
    "pass": ["string"]
  }
}
```

---

## Integration

| Downstream Skill | What This Feeds |
|-----------------|----------------|
| `comp-analyzer` | Validate listing prices with adjusted comps |
| `residential-deal-underwriter` | Underwrite the top candidates from screening |
| `underwriting-market-rate-multifamily` | Full underwriting for MF candidates |
| `neighborhood-analyzer` | Validate location quality for top picks |
| `environmental-risk-assessment` | DD on candidates advancing to offers |
| `legal-title-risk-assessment` | Title DD on candidates advancing to offers |
| `operating-expense-analysis` | Validate expense assumptions in DCF |
| `market-research-assistant` | Metro-level context for market assumptions |
