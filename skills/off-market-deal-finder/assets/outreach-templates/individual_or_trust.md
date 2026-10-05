# Template: individual_or_trust

Archetypes: `individual_occupant`, `individual_absentee`, `trust_estate` (trustee of a living trust; for probate estates use `estate.md`). Class 1 and small class 2 owners.

Gates before use: `dnc_scrub` (any call); `consent_capture` (any text); `equity_purchaser_rules` when the property is in foreclosure (NOD/NOTS recorded) and any leaseback, option or "help" framing is contemplated; `wholesaler_registration` when `buyer_profile = wholesaler` (append the HB 4058 block). No dollar figure, no reference to foreclosure, probate, age or debts in the first touch.

## Letter 1 (first touch, plain one-page, hand-addressed envelope, no teaser copy)

```
[Date]

[Owner name as on the deed, or "Trustee" when a trust holds title]
[Mailing address from the assessor record]

Re: [Situs address]

Dear [Mr./Ms. Last name / Trustee],

I buy a small number of houses and small apartment buildings each year in [county or neighborhood], and I hold them rather than resell them. I am writing because [situs address] is the kind of property I would like to own long term.

If you have been thinking about selling at some point, I would welcome a short conversation. I buy as-is, on your timeline, pay closing costs, and do not need you to make repairs or clean out the property. If the timing is not right, there is no follow-up unless you ask.

You can reach me at [business phone] or [email]. If you prefer not to hear from me again, a note or a call saying so is all it takes.

Sincerely,
[Name]
[Company, if any]
[Mailing address]
```

## Letter 2 (3-4 weeks later, only if no response)

Shorter; one new piece of substance: an offer to meet at the property or to send a written outline of how a sale would work (timeline, who pays what), still without a price.

## Call script (business or landline number only, after DNC scrub; 8am-9pm; no autodialer)

Open with name and the letter; ask whether they received it; ask one question ("Is selling something you have thought about?"); if yes, ask what matters most to them (timing, tenants, repairs, taxes); propose a walk-through; if no, thank them and close the lead.

## Long-hold / tax-strategy variant (HOLD_YEARS >= 20 or DEPRECIATION_EXHAUSTED)

Add one paragraph: "Owners who have held a property for many years often want to understand options such as a 1031 exchange, an installment sale, or a Delaware Statutory Trust before deciding. I am happy to share what I have seen work; your tax advisor should confirm anything specific to you."

## HB 4058 block (wholesaler buyer_profile only, class 1)

"[Company] is registered with the Oregon Real Estate Agency as a residential property wholesaler (registration [number]). If we enter into a purchase agreement, we may assign it to another buyer; you will receive the written disclosures and cancellation rights required by Oregon law." Confirm current fee, registration number and cancellation period on the OREA page before use.

## Do not

- Mention the NOD, sale date, probate, HECM, tax delinquency, age or health.
- Put a price, "cash offer", or percentage in the first two touches.
- Call or text any number flagged DNC or litigator; text without recorded consent.
- Knock on the door of a property in foreclosure or occupied by tenants without an appointment.
