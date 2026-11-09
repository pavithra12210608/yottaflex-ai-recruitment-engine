"""Tests for offer generation and approval governance."""
import pytest
from app.config import TEST_TARGETS
from app.generators.synthetic_data_generator import SyntheticDataGenerator


def test_offer_approval_governance():
    gen = SyntheticDataGenerator(seed=20261022)
    entities, _ = gen.generate(**TEST_TARGETS)

    for off in entities["offers"]:
        assert off["approval_status"] in ["APPROVED", "PENDING_APPROVAL", "REJECTED"]
        if off["approval_status"] == "APPROVED":
            assert off["approved_by"] is not None
            assert len(off["approved_by"]) > 0

        assert off["candidate_decision"] in ["ACCEPTED", "DECLINED", "PENDING"]
        assert off["offer_date"] <= off["expiration_date"]


def test_hired_applications_correspond_to_accepted_offers():
    gen = SyntheticDataGenerator(seed=20261022)
    entities, _ = gen.generate(**TEST_TARGETS)

    accepted_offers_app_ids = {
        off["application_id"]
        for off in entities["offers"]
        if off["candidate_decision"] == "ACCEPTED"
    }

    hired_app_ids = {
        app["application_id"]
        for app in entities["applications"]
        if app["status"] == "HIRED"
    }

    # Every hired application must have an accepted offer
    assert hired_app_ids.issubset(accepted_offers_app_ids)
