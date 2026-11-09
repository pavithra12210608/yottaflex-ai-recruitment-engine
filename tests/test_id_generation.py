"""Tests for deterministic ID conventions and patterns."""
import re
import pytest
from app.config import TEST_TARGETS
from app.generators.synthetic_data_generator import SyntheticDataGenerator


@pytest.fixture(scope="module")
def generated_data():
    gen = SyntheticDataGenerator(seed=20261022)
    entities, ground_truth = gen.generate(**TEST_TARGETS)
    return entities, ground_truth


def test_department_ids(generated_data):
    entities, _ = generated_data
    for dept in entities["departments"]:
        assert re.match(r"^DEP-\d{3}$", dept["department_id"])


def test_requisition_ids(generated_data):
    entities, _ = generated_data
    for req in entities["job_requisitions"]:
        assert re.match(r"^REQ-2026-\d{6}$", req["requisition_id"])


def test_candidate_ids(generated_data):
    entities, _ = generated_data
    for cand in entities["candidates"]:
        assert re.match(r"^CAND-\d{6}$", cand["candidate_id"])


def test_resume_artifact_ids(generated_data):
    entities, _ = generated_data
    for art in entities["resume_artifacts"]:
        assert re.match(r"^ART-\d{6}$", art["artifact_id"])
        assert len(art["file_sha256"]) == 64  # SHA-256


def test_skill_ids(generated_data):
    entities, _ = generated_data
    for skill in entities["skills"]:
        assert re.match(r"^SKL-\d{3}$", skill["skill_id"])


def test_screening_rule_ids(generated_data):
    entities, _ = generated_data
    for rule in entities["screening_rules"]:
        assert re.match(r"^RULE-\d{6}$", rule["rule_id"])


def test_interviewer_ids(generated_data):
    entities, _ = generated_data
    for emp in entities["interviewers"]:
        assert re.match(r"^EMP-\d{4}$", emp["interviewer_id"])


def test_interview_ids(generated_data):
    entities, _ = generated_data
    for intv in entities["interviews"]:
        assert re.match(r"^INT-2026-\d{6}$", intv["interview_id"])


def test_feedback_ids(generated_data):
    entities, _ = generated_data
    for fb in entities["feedback"]:
        assert re.match(r"^FB-INT-2026-\d{6}-EMP-\d{4}$", fb["feedback_id"])


def test_offer_ids(generated_data):
    entities, _ = generated_data
    for off in entities["offers"]:
        assert re.match(r"^OFF-2026-\d{6}$", off["offer_id"])
