"""Servicing extract <-> inventory join: crosswalk > address > fuzzy > unmatched; phase tokens are hard discriminators; unmatched book
rows surface in servicing_unmatched.csv; the real inventory joins at least eight fixture rows (skipped when the file is absent)."""
from __future__ import annotations

import os
import sys
from unittest import SkipTest

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _fixture_runs import hfa_fixture_run, real_available, real_run  # noqa: E402
from plb import geo as G  # noqa: E402
from plb.book_join import join_book, phase_tokens, token_set_ratio  # noqa: E402


def _inv(name, addr, zipc, fips="41051"):
    return {"property_id": G.property_id("OR", fips, None, addr, zipc), "property_name": name, "address": addr, "zip": zipc}


def _book(name, addr, zipc, loan="", fips="41051", **kw):
    row = {"property_id": G.property_id("OR", fips, None, addr, zipc) if addr else G.property_id("OR", None, None, f"{name} Portland", zipc),
           "property_name": name, "address": addr, "zip": zipc, "county_fips": fips, "agency_loan_ids": loan, "grant_ids": "", "ohcs_property_key": "", "site_type": ""}
    row.update(kw)
    return row


def test_join_grades_in_order():
    inv = pd.DataFrame([_inv("Powell Plaza I", "13320-1 SE Powell Boulevard", "97236"), _inv("Powell Plaza II", "13320-3 SE Powell Boulevard", "97236"),
                        _inv("Village Garden Apartments", "15230 NE Sandy Boulevard", "97205"), _inv("Fixture Authority Court", "900 SE Fixture St", "97222", "41005")])
    xw = {"L-9": G.property_id("OR", "41005", None, "900 SE Fixture St", "97222")}
    book = pd.DataFrame([
        _book("Fixture Authority Court (HACC)", "PO Box 1510", "97222", "L-9", "41005"),            # crosswalk
        _book("Powell Plaza I", "13320-1 SE Powell Boulevard", "97236", "L-2"),                    # address
        _book("Powell Plaza I", "13320-1 SE Powell Boulevard", "97236", "L-2b", parcel_id="R123"),  # address regardless of parcel_id
        _book("Village Gardens Apartments", "", "97205", "", grant_ids="G-12"),                   # fuzzy 0.98
        _book("Powell Plaza I", "", "97236", "L-x"),                                             # fuzzy candidate blocked by phase tokens vs Powell Plaza II? no: I == I -> joins I only
        _book("Powell Plaza III", "", "97236", "L-y"),                                           # phase III: never joins I or II
        _book("Hollow Oak Commons", "4410 SE Hollow Oak Ct", "97206", "L-13"),                     # unmatched
    ])
    dec, log = join_book(book, inv, xw)
    grades = [dec[str(p)]["grade"] for p in book["property_id"]]
    assert grades[0] == "crosswalk" and grades[1] == "address" and grades[2] == "address"
    assert grades[3] == "fuzzy" and dec[str(book.iloc[3]["property_id"])]["ratio"] >= 0.92
    assert dec[str(book.iloc[4]["property_id"])]["inventory_pid"] == inv.iloc[0]["property_id"]
    assert grades[5] == "unmatched" and grades[6] == "unmatched"
    assert len(log) == len(book) and all(r["grade"] for r in log)


def test_phase_tokens_block_sibling_phases():
    assert phase_tokens("Powell Plaza I") != phase_tokens("Powell Plaza II") and phase_tokens("Village Garden Apartments") == frozenset()
    assert token_set_ratio("Powell Plaza I", "Powell Plaza II") > 0.92  # the ratio alone would join; phase tokens stop it
    assert token_set_ratio("Village Gardens Apartments", "Village Garden Apartments") >= 0.92


def test_fixture_run_grades_unmatched_and_two_loans_one_property():
    r = hfa_fixture_run()
    g = r["cal"]["book_join_grades"]
    assert g.get("crosswalk") == 1 and g.get("address", 0) >= 2
    un = set(r["unmatched"]["property_name"])
    assert {"Hollow Oak Commons", "Sumner Street Flats", "Village Garden Apartments"} <= un  # not in the fixture inventory
    assert "Fixture Authority Court (HACC)" not in un and "Fixture Badly Typed" not in un
    bt = r["leads"][r["leads"]["property_name"] == "Fixture Badly Typed"]
    assert len(bt) == 1 and set(bt.iloc[0]["agency_loan_ids"].split(";")) == {"L-OHCS-0010", "L-OHCS-0011"} and float(bt.iloc[0]["public_upb"]) == 650_000
    ev = r["events"][(r["events"]["property_id"] == bt.iloc[0]["property_id"]) & (r["events"]["event_type"] == "AGENCY_LOAN_MATURITY")]
    assert len(ev) == 2 and set(ev["event_date"]) == {"2032-06-30"} and (ev["verify_flag"] == "").all()  # same-day maturities survive, no conflict flag
    hac = r["leads"][r["leads"]["property_name"] == "Fixture Authority Court"].iloc[0]
    assert hac["book_join_grade"] == "crosswalk" and hac["universe"] == "our_book" and hac["agency_loan_ids"] == "L-OHCS-0009"
    assert (r["leads"][r["leads"]["book_match"] == "unmatched_expected"]["ohcs_funded"].str.lower() == "true").all()
    assert len(r["gaps"]) == int((r["leads"]["book_match"] == "unmatched_expected").sum()) >= 1
    # book-only rows carry book_match book_only (never 'matched'), universe our_book, in_inventory false
    bo = r["leads"][r["leads"]["property_name"].isin(["Hollow Oak Commons", "Sumner Street Flats"])]
    assert len(bo) == 2 and (bo["book_match"] == "book_only").all() and (bo["universe"] == "our_book").all() and (bo["in_inventory"].str.lower() == "false").all()
    assert (bo["book_join_grade"] == "unmatched").all()


def test_real_inventory_joins_at_least_eight_fixture_rows():
    if not real_available():
        raise SkipTest("real OHCS CSV not found (set OHCS_CSV)")
    r = real_run()
    g = r["cal"]["book_join_grades"]
    assert g.get("address", 0) >= 8 and g.get("fuzzy", 0) >= 1
    un = set(r["unmatched"]["property_name"])
    assert {"Hollow Oak Commons", "Sumner Street Flats"} <= un and "Village Garden Apartments" not in un
    # two instruments on one property (loan by address + grant by fuzzy): book_kind is a ';'-list in BOOK_KINDS order (loan first);
    # the loan row supplies payment_type; ids union
    vg = r["leads"][r["leads"]["property_name"] == "Village Garden Apartments"].iloc[0]
    assert vg["book_kind"] == "loan;grant" and vg["payment_type"] == "residual_receipts" and vg["grant_ids"] == "G-OHCS-0012" and vg["agency_loan_ids"] == "L-OHCS-0001"
    vg = r["leads"][r["leads"]["property_name"] == "Village Garden Apartments"]
    assert len(vg) == 1 and vg.iloc[0]["universe"] == "our_book" and vg.iloc[0]["in_inventory"] in ("True", "true")
    fuzzy = r["merge_log"][r["merge_log"]["grade"] == "fuzzy"]
    assert (fuzzy["name"] == "Village Gardens Apartments").any() and float(fuzzy.iloc[0]["ratio"]) >= 0.92
    assert not ((r["merge_log"]["name"] == "Powell Plaza I") & (r["merge_log"]["merged_into"].str.contains("II", na=False))).any()
