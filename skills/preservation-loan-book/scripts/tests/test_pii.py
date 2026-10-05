"""Sunshine / PII scopes: default outputs carry organization-level data only (am_officer yes, am_officer_email no, never a phone);
the board packet withholds natural-person owners and residential registered-agent addresses and logs every redaction."""
from __future__ import annotations

import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _fixture_runs import hfa_fixture_run  # noqa: E402
from plb.entities import is_natural_person  # noqa: E402
from plb.pii import RECORDS_CLASSIFICATION, WITHHELD, apply_pii_scope, assert_no_pii, is_residential_agent_address  # noqa: E402


def _df():
    return pd.DataFrame([
        {"property_id": "a", "property_name": "Fixture Fifth Place", "owner_name": "Bell, David", "owner_type": "individual_owner_of_record", "registered_agent": "David Bell",
         "registered_agent_address": "1500 SW Fixture Pl Apt 4, Portland OR", "am_officer": "J. Rivera", "am_officer_email": "j@example.invalid", "owner_phone": "503-555-0100",
         "units": "70", "programs": "LIHTC_9", "primary_route": "notice_compliance", "intervention": "push_window_prep", "statutory_cite": "ORS 456.260 (verify)"},
        {"property_id": "b", "property_name": "Village Garden Apartments", "owner_name": "Village Garden, LLC", "owner_type": "lihtc_partnership_forprofit_gp", "registered_agent": "Registered Agents Inc",
         "registered_agent_address": "1000 SW Broadway Suite 200, Portland OR", "am_officer": "J. Rivera", "am_officer_email": "j@example.invalid", "owner_phone": "",
         "units": "35", "programs": "OTHER_OHCS", "primary_route": "servicing_watch", "intervention": "covenant_enforcement_notice", "statutory_cite": "loan documents"},
    ])


def test_organization_scope_keeps_am_officer_drops_contact_detail():
    out, log = apply_pii_scope(_df(), "organization")
    assert "am_officer" in out.columns and "am_officer_email" not in out.columns and "owner_phone" not in out.columns
    assert assert_no_pii(out) == [] and log == []
    internal, _ = apply_pii_scope(_df(), "internal")
    assert "am_officer_email" in internal.columns and "owner_phone" not in internal.columns  # NEVER columns are gone even internally


def test_public_packet_redacts_individuals_and_residential_agents_with_log():
    out, log = apply_pii_scope(_df(), "public_packet")
    assert out.loc[out["property_id"] == "a", "owner_name"].iloc[0] == WITHHELD
    assert out.loc[out["property_id"] == "b", "owner_name"].iloc[0] == "Village Garden, LLC"
    assert out.loc[out["property_id"] == "a", "registered_agent_address"].iloc[0] == "(residential address omitted)"
    assert "Suite 200" in out.loc[out["property_id"] == "b", "registered_agent_address"].iloc[0]
    fields = {x["field"] for x in log}
    assert "owner_name" in fields and "registered_agent_address" in fields and all("ORS 192.355" in x["cite"] for x in log)
    assert "am_officer" not in out.columns  # packet is organization + registered agent + program facts


def test_natural_person_and_residential_heuristics():
    assert is_natural_person("Bell, David") and is_natural_person("Menashe, Michael")
    assert not is_natural_person("Village Garden, LLC") and not is_natural_person("Home Forward") and not is_natural_person("Cedar Sinai Park -Clay Tower Apartments LP")
    assert is_residential_agent_address("4410 SE Hollow Oak Ct Apt 2") and not is_residential_agent_address("1000 SW Broadway Ste 200")


def test_fixture_run_default_outputs_are_clean():
    r = hfa_fixture_run()
    for df in (r["leads"], r["scored"]):
        assert assert_no_pii(df) == [] and "am_officer_email" not in df.columns and "decision_maker_name" not in df.columns
    assert (r["scored"]["am_officer"] != "").any()
    assert (r["scored"]["pii_scope"] == "organization").all()
    assert "ORS 192" in RECORDS_CLASSIFICATION
    packet, log = apply_pii_scope(r["scored"], "public_packet")
    bell = packet[packet["property_name"] == "Fixture Fifth Place"]
    assert len(bell) == 1 and bell.iloc[0]["owner_name"] == WITHHELD
