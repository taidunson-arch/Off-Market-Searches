"""Units, households and public dollars at risk (R4 / R5 / R29 / R30): restricted units from Total - Market, HAP vs PRAC vs other RA
never summed, PSH overlay, UPB-at-risk rule, Board_Totals pivot rows including stale and no-cliff rows, recapture exposure full for rental HOME (92.503(b)), prorata only for homebuyer assistance."""
from __future__ import annotations

import os
import sys
from datetime import date

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _fixture_runs import by_name, hfa_fixture_run  # noqa: E402
from plb.schema import LEAD_COLUMNS  # noqa: E402
from plb.units import fill_units_block, ohcs_units, units_at_risk_json  # noqa: E402

AS_OF = date(2026, 10, 4)


def test_ohcs_units_rules():
    row = {"Total Units": "84", "Market_Rate_Units": "4", "Total_30_AMI_Units": "10", "Total_50_AMI_Units": "30", "Total_60_AMI_Units": "40", "Rental_Assistance_Count": "12",
           "HUD Contract": "", "PSH_Units": "8", "Total_3_BR_Units": "20", "Total_4Plus_BR_Units": "2", "Property Type": "Elderly Apartments"}
    u = ohcs_units(row)
    assert u["restricted_units"] == 80 and u["units_basis"] == "reported_buckets" and u["units_at_risk"] == 80
    assert u["hap_units_at_risk"] == 0 and u["prac_units_at_risk"] == 0 and u["other_ra_units"] == 12 and u["psh_units_at_risk"] == 8
    assert u["family_3br_plus_units"] == 22 and set(u["vulnerability_flags"].split(";")) == {"elderly", "psh"}
    hap = ohcs_units({"Total Units": "47", "Rental_Assistance_Count": "47", "HUD Contract": "Housing Assistance Payment", "Total_60_AMI_Units": "46"})
    assert hap["hap_units_at_risk"] == 47 and hap["other_ra_units"] == 0 and hap["units_basis"] == "total_assumed_restricted"  # 46 != 47
    prac = ohcs_units({"Total Units": "76", "Rental_Assistance_Count": "75", "HUD Contract": "Project Rental Assistance Contract"})
    assert prac["prac_units_at_risk"] == 75 and prac["hap_units_at_risk"] == 0
    blank = ohcs_units({"Total Units": "", "Rental_Assistance_Count": "5"})
    assert blank["units_at_risk"] == "" and blank["flag"].startswith("Missing Source")


def _lead(**kw):
    base = {c: "" for c in LEAD_COLUMNS}
    base.update({"property_id": "p", "property_name": "P", "units": "40", "units_at_risk": "40", "restricted_units": "40", "book_match": "matched", "public_upb": "1000000", "public_upb_at_risk": "1000000",
                 "covenant_status": "current", "owner_cliff_band": "URGENT", "owner_cliff_date": "2028-01-01", "owner_cliff_months_out": "14.9", "county_name": "Multnomah", "signals": ""})
    base.update(kw)
    return base


def test_fill_units_block_upb_at_risk_rule_and_board_impact():
    df = pd.DataFrame([_lead(), _lead(property_id="q", owner_cliff_band="SCHEDULED", owner_cliff_date="2033-01-01", owner_cliff_months_out="75"),
                       _lead(property_id="w", owner_cliff_band="SCHEDULED", owner_cliff_date="2033-01-01", owner_cliff_months_out="75", covenant_status="watch"),
                       _lead(property_id="c", owner_cliff_band="SCHEDULED", owner_cliff_date="2033-01-01", owner_cliff_months_out="75", our_maturity="2030-06-30", senior_maturity="2031-01-01"),
                       _lead(property_id="n", book_match="not_in_book", public_upb="")]).astype(object)
    out = fill_units_block(df, AS_OF).set_index("property_id")
    assert float(out.loc["p", "public_upb_at_risk"]) == 1_000_000 and float(out.loc["p", "board_impact"]) == 30.0   # 40 x 0.75
    assert float(out.loc["q", "public_upb_at_risk"]) == 0 and float(out.loc["q", "board_impact"]) == 0.0
    assert float(out.loc["w", "public_upb_at_risk"]) == 1_000_000       # covenant watch
    assert float(out.loc["c", "public_upb_at_risk"]) == 1_000_000 and out.loc["c", "coterminous_senior_cliff"] is True
    assert out.loc["n", "public_upb_at_risk"] == ""


def test_units_at_risk_json_bands_and_headline():
    rows = [_lead(), _lead(property_id="s", owner_cliff_band="", owner_cliff_date="", owner_cliff_months_out="", signals="hap_date_stale", hap_units_at_risk="40"),
            _lead(property_id="z", owner_cliff_band="", owner_cliff_date="", owner_cliff_months_out=""), _lead(property_id="b", owner_cliff_band="BEYOND", owner_cliff_date="2040-01-01", owner_cliff_months_out="159"),
            _lead(property_id="d", exclusion_reason="in_development")]
    uar = units_at_risk_json(pd.DataFrame(rows).astype(object), AS_OF, "hfa", "loan_book")
    b = uar["by_owner_cliff_band"]
    assert b["URGENT"]["properties"] == 1 and b["stale_contract_date_verify"]["properties"] == 1 and b["no_dated_cliff"]["properties"] == 1 and b["BEYOND"]["properties"] == 1
    assert b["OVERDUE"]["properties"] == 0  # the stale row never lands in OVERDUE
    assert uar["headline"]["properties"] == 1 and uar["headline"]["units_at_risk"] == 40 and uar["headline"]["public_upb_at_risk"] == 1_000_000
    assert "Multnomah" in uar["by_jurisdiction"] and uar["by_year"]["2028"]["properties"] == 1
    assert uar["book_verdict"] in ("STABLE", "WATCH", "STRESSED", "CRITICAL")
    owned = units_at_risk_json(pd.DataFrame(rows).astype(object), AS_OF, "pha_am", "owned_assets")
    assert "owned_units" in owned["columns"] and "public_upb_at_risk" not in owned["columns"]


def test_fixture_run_units_columns_and_recapture_exposure():
    r = hfa_fixture_run()
    vg = by_name(r["leads"], "Village Garden Apartments")
    assert vg["units_at_risk"] == "35" and vg["units_basis"] in ("proxy", "reported_buckets") and vg["book_match"] == "book_only"  # in our book, not in the fixture inventory
    g42 = by_name(r["leads"], "GOING 42")
    assert float(g42["recapture_exposure"]) == 1_100_000 and float(g42["public_grant_at_risk"]) == float(g42["recapture_exposure"])  # rental HOME `full` (24 CFR 92.503(b))
    sumner = by_name(r["leads"], "Sumner Street Flats")
    assert float(sumner["recapture_exposure"]) == 480_000 and sumner["units_at_risk"] == "12"
    hill = by_name(r["leads"], "Fixture Hillside Senior")
    assert hill["hap_units_at_risk"] == "60" and hill["prac_units_at_risk"] == "0"
    # the three RA kinds are never summed into one figure
    assert {"hap_units_at_risk", "prac_units_at_risk", "other_ra_units"} <= set(r["leads"].columns) and "hap_households" not in r["leads"].columns
    # UPB at risk: Hollow Oak (covenant watch) counted, Town Center Courtyards (cliff 2048 / 2078) not
    assert float(by_name(r["leads"], "Hollow Oak Commons")["public_upb_at_risk"]) == 1_850_000
    assert float(by_name(r["leads"], "Town Center Courtyards")["public_upb_at_risk"]) == 0
