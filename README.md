# Public-agency preservation and loan-book monitoring

The active agency implementation is `skills/preservation-loan-book/scripts/`.
The root `App.tsx`, commercial data, and off-market archives are legacy buyer-oriented material; they are not the agency application.

Start with [the HFA operations guide](skills/preservation-loan-book/references/hfa-operations.md) and [instrument model](skills/preservation-loan-book/references/instrument-model.md).

The agency pipeline provides preservation screening, instrument-level loan/grant records,
board outputs, separate risk dimensions, and an optional persistent local work queue.
It remains a pilot tool: legal rules need agency review and financial thresholds and
results need validation against an authorized real servicing book.

Install Python 3.12 and the requirements in `skills/preservation-loan-book/scripts/requirements.txt`.
Run the test runner in that folder's `tests/` directory; set `OHCS_CSV` to the included
`Oregon_Affordable_Housing_Inventory_20261002.csv` to exercise the real inventory tests.
The servicing fixture is synthetic, even when joined to the real public inventory.
