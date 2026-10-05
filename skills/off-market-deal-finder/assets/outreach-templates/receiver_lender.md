# Template: receiver_lender

Archetype: `lender_reo_receiver`. Route `lender_counterparty`; `owner_outreach = false`. Counterparty depends on the routing event: court-appointed receiver (RECEIVER_APPOINTED), special servicer (SPECIAL_SERVICING, MATURED_BALLOON), trustee or REO asset manager (TRUSTEES_DEED), debtor's counsel or trustee (BANKRUPTCY_FILED, `counsel_only`), mezzanine lender (UCC_ART9_SALE).

Gates before use: `counsel_only` when a bankruptcy case is active (contact only debtor's counsel or the trustee; the automatic stay applies); no contact with the owner once the route is `lender_counterparty`; no contact with tenants.

## Registration email to a receiver

```
Subject: Qualified buyer registration — [Property name], [County] Circuit Court Case No. [number]

[Receiver name], [Firm]

[Company] owns and operates [n] apartment units in [metro]. We understand you were appointed receiver over [property name] by order dated [date]. We would like to be registered as a prospective purchaser in the event the court authorizes a sale, and to receive any marketing materials, bid procedures or data-room access you make available.

For your file: we close without a financing contingency, can take the property as-is with tenants in place, and are prepared to provide proof of funds under a confidentiality agreement. Our counsel is [firm].

[Name] | [Company] | [Business phone] | [Email]
```

## Special servicer / matured balloon

Email the special servicer's asset manager for the loan (from the IRP or Annex A): state interest in acquiring the asset through a consensual sale, a note sale or a discounted payoff with the borrower's cooperation, and ask for the process. Do not contact the borrower unless the servicer asks you to.

## REO (Trustee's Deed recorded)

Contact the REO asset manager at the beneficiary named in the trustee's deed; ask for the disposition timeline and whether a broker has been engaged. Close the owner lead in the pipeline; track the REO as a separate lead.

## Bankruptcy (Chapter 11 / SARE)

Write to debtor's counsel (from the PACER docket): express interest as a plan sponsor, stalking-horse bidder or purchaser under a Section 363 sale; ask whether bid procedures have been proposed. Monitor sale and lift-stay motions. Use scheduled values and claims from Schedules A/B and D as the debt facts (RECORDED).

## Article 9 sale (mezzanine lender)

Contact the secured party on the UCC notice; ask for the sale terms and whether a pre-sale consensual transfer is possible. The counterparty is the mezz lender; the sponsor is losing the entity.

## Do not

- Contact the owner, guarantor or tenants after the route changes.
- Contact a bankrupt debtor other than through counsel.
- Represent your proof of funds or timeline beyond what you can document.
