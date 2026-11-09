"""Tests for relational integrity and foreign-key references."""
import pytest
from app.config import TEST_TARGETS
from app.generators.synthetic_data_generator import SyntheticDataGenerator


@pytest.fixture(scope="module")
def entities():
    gen = SyntheticDataGenerator(seed=20261022)
    ents, _ = gen.generate(**TEST_TARGETS)
    return ents


def test_requisitions_department_foreign_key(entities):
    dept_ids = {d["department_id"] for d in entities["departments"]}
    for req in entities["job_requisitions"]:
        assert req["department_id"] in dept_ids


def test_resume_artifacts_candidate_foreign_key(entities):
    cand_ids = {c["candidate_id"] for c in entities["candidates"]}
    for art in entities["resume_artifacts"]:
        assert art["candidate_id"] in cand_ids


def test_candidate_skills_foreign_keys(entities):
    cand_ids = {c["candidate_id"] for c in entities["candidates"]}
    skill_ids = {s["skill_id"] for s in entities["skills"]}
    for cs in entities["candidate_skills"]:
        assert cs["candidate_id"] in cand_ids
        assert cs["skill_id"] in skill_ids


def test_screening_rules_foreign_keys(entities):
    req_ids = {r["requisition_id"] for r in entities["job_requisitions"]}
    skill_ids = {s["skill_id"] for s in entities["skills"]}
    for rule in entities["screening_rules"]:
        assert rule["requisition_id"] in req_ids
        assert rule["skill_id"] in skill_ids


def test_applications_foreign_keys(entities):
    req_ids = {r["requisition_id"] for r in entities["job_requisitions"]}
    cand_ids = {c["candidate_id"] for c in entities["candidates"]}
    for app in entities["applications"]:
        assert app["requisition_id"] in req_ids
        assert app["candidate_id"] in cand_ids


def test_interviews_foreign_keys(entities):
    app_ids = {a["application_id"] for a in entities["applications"]}
    emp_ids = {e["interviewer_id"] for e in entities["interviewers"]}
    for intv in entities["interviews"]:
        assert intv["application_id"] in app_ids
        assert intv["interviewer_id"] in emp_ids


def test_feedback_foreign_keys(entities):
    int_ids = {i["interview_id"] for i in entities["interviews"]}
    emp_ids = {e["interviewer_id"] for e in entities["interviewers"]}
    for fb in entities["feedback"]:
        assert fb["interview_id"] in int_ids
        assert fb["interviewer_id"] in emp_ids


def test_offers_foreign_keys(entities):
    app_ids = {a["application_id"] for a in entities["applications"]}
    for off in entities["offers"]:
        assert off["application_id"] in app_ids
