"""Mandate predicate: every branch of product_qualifies, the three mandate_fit values, profile default product subsets."""
from __future__ import annotations

import json
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from plb.mandate import mandate_fit, product_qualifies  # noqa: E402
from plb.schema import load_mandate  # noqa: E402

AS_OF = date(2026, 10, 4)
FX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
PACK = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "references", "sources", "oregon-portland"))
BASE = {"product_id": "p", "status": "open", "eligible_programs": ["LIHTC_9", "HAP"], "eligible_owner_types": [], "ineligible_owner_types": ["institutional"], "min_units": 5}


def test_each_predicate_branch():
    assert product_qualifies(BASE, ["LIHTC_9"], "nonprofit", 40, AS_OF) is None
    assert product_qualifies(dict(BASE, status="closed"), ["LIHTC_9"], "nonprofit", 40, AS_OF).startswith("status")
    assert product_qualifies(BASE, ["HOME"], "nonprofit", 40, AS_OF) == "program not eligible"
    assert "ineligible" in product_qualifies(BASE, ["LIHTC_9"], "institutional", 40, AS_OF)
    assert "not eligible" in product_qualifies(dict(BASE, eligible_owner_types=["nonprofit"]), ["LIHTC_9"], "housing_authority", 40, AS_OF)
    assert "min_units" in product_qualifies(BASE, ["LIHTC_9"], "nonprofit", 4, AS_OF)
    assert "min_units" in product_qualifies(BASE, ["LIHTC_9"], "nonprofit", None, AS_OF)
    assert product_qualifies(dict(BASE, application_window={"open": "2027-02-01", "close": "2027-05-31"}), ["LIHTC_9"], "nonprofit", 40, AS_OF) == "outside application window"
    assert product_qualifies(dict(BASE, application_window={"open": "2026-02-01", "close": "2027-05-31"}), ["LIHTC_9"], "nonprofit", 40, AS_OF) is None
    assert product_qualifies(dict(BASE, eligible_programs=[]), ["ANYTHING"], "nonprofit", 40, AS_OF) is None  # empty list = any program


def test_mandate_fit_values():
    m = {"products": [BASE, dict(BASE, product_id="q", status="closed")]}
    ok = mandate_fit(m, ["LIHTC_9"], "nonprofit", 40, AS_OF)
    assert ok["mandate_fit"] == "eligible" and ok["mandate_eligible_products"] == "p"
    bad = mandate_fit(m, ["HOME"], "nonprofit", 40, AS_OF)
    assert bad["mandate_fit"] == "ineligible" and "p: program not eligible" in bad["mandate_ineligible_reason"] and "q: status closed" in bad["mandate_ineligible_reason"]
    assert mandate_fit(None, ["HOME"], "nonprofit", 40, AS_OF)["mandate_fit"] == "no_mandate_file"
    assert mandate_fit({"products": []}, ["HOME"], "nonprofit", 40, AS_OF)["mandate_fit"] == "no_mandate_file"


def test_oregon_mandate_fixture_has_a_closed_product_and_profile_defaults():
    m = json.load(open(os.path.join(FX, "mandate_sample.json")))
    assert any(p.get("status") == "closed" for p in m["products"])
    cdbg = mandate_fit(m, ["HOME"], "nonprofit", 40, AS_OF, profile="cdbg_home")
    assert cdbg["mandate_fit"] == "ineligible" and "phb_preservation_rfp" in cdbg["mandate_ineligible_reason"]  # the spring 2025 RFP is closed
    hfa = mandate_fit(m, ["LIHTC_9"], "lihtc_partnership_forprofit_gp", 40, AS_OF, profile="hfa")
    assert hfa["mandate_fit"] == "eligible" and "lihtc_4pct_gap" in hfa["mandate_eligible_products"]
    assert load_mandate(PACK) is not None and load_mandate(PACK, "none") is None
