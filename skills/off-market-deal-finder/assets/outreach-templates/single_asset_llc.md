# Template: single_asset_llc

Archetype: `single_asset_llc` (one-property LLC or LP, usually class 2; also 2-4 unit landlords holding in an LLC). Decision maker: the managing member named in the SOS filing or the trust-deed signature block.

Gates before use: `dnc_scrub` (calls to a business line only); `broker_exclusive` when LISTING_WITHDRAWN inside 12 months; `assumption_approval` when `assumable_debt`. Address the principal office, never the registered agent. No dollar figure in the first touch.

## Letter to the managing member

```
[Date]

[Managing member name], Managing Member (grade A) / Managing Member (grade B, name unknown)
[Owner LLC name]
[Principal office address from SOS]

Re: [Property name], [situs address] ([units] units)

Dear [Mr./Ms. Last name],

I own and operate apartment buildings in [metro] and I am writing directly rather than through a broker because I would like to own [property name] for the long term.

Many owners who financed between 2016 and 2021 are now looking at a refinance at materially higher rates and, in some cases, a loan balance that today's debt service coverage will not support. If that is part of your planning for [property name], I can offer a straightforward alternative: a direct sale with a certain close, no financing contingency, and the ability to assume existing debt where the lender allows it. [Optional, Portland only: I also understand the cost of operating under the current rent-increase cap and relocation rules, and I am not asking you to reposition anything before closing.]

If you would rather hold, I understand and will not follow up unless you ask. If a conversation would be useful, I can be reached at [business phone] or [email].

Sincerely,
[Name]
[Company]
```

## Call (business line, 10-14 days after the letter)

Confirm the letter; ask how they are thinking about the [year] maturity; offer to share your refinance math (DSCR at today's rates, proceeds at 65-70% LTV) as a courtesy; propose a site visit. If they are already working with a broker on an exclusive, stop and route through the broker.

## Variants

- **Maturity math** (LOAN_MATURITY inside 24 months, refi_gap_pct > 0): include one sentence noting that new proceeds at current coverage typically fall short of balances originated at 3-4% coupons, without stating their numbers.
- **1031 / DST** (HOLD_YEARS >= 20 or DEPRECIATION_EXHAUSTED): add the tax-strategy paragraph from `individual_or_trust.md`.
- **Regulatory fatigue** (rent_gap_pct > 0.20 inside Portland, tenant litigation): acknowledge the operating environment; never criticize tenants or the city.
- **Assumption play** (assumable HUD/agency debt with a low coupon): say that preserving the existing financing is part of your plan, subject to lender approval.

## Do not

- Address or call the registered agent as if they were the owner.
- Quote their loan balance, rate or maturity in writing; you hold estimates, not facts, until the image or tape says so.
- Approach during a live broker exclusive.
- Use personal cell numbers obtained without consent.
