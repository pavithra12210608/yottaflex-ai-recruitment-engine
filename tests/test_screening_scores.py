"""Tests for job-related deterministic screening score calculations."""
import pytest
from app.services.screening_service import calculate_candidate_score, SCREENING_PASS_THRESHOLD


def test_perfect_candidate_screening():
    candidate_skills = {
        "SKL-001": {"proficiency_level": "Expert", "years_experience": 6.0},
        "SKL-002": {"proficiency_level": "Advanced", "years_experience": 5.0},
        "SKL-008": {"proficiency_level": "Advanced", "years_experience": 4.0},
    }
    rules = [
        {"skill_id": "SKL-001", "is_mandatory": True, "min_proficiency": "Advanced", "weight": 2.0},
        {"skill_id": "SKL-002", "is_mandatory": False, "min_proficiency": "Intermediate", "weight": 1.0},
        {"skill_id": "SKL-008", "is_mandatory": False, "min_proficiency": "Intermediate", "weight": 1.0},
    ]

    score, passed, reason, breakdown = calculate_candidate_score(
        candidate_experience=7.0,
        candidate_education="MSc",
        candidate_domain="AI Systems & Large Language Models",
        candidate_skills=candidate_skills,
        req_min_experience=4,
        req_title="AI Forward Deployed Engineer",
        screening_rules=rules,
    )

    assert score >= 90.0
    assert passed is True
    assert reason is None
    assert breakdown["mandatory_failed"] is False


def test_missing_mandatory_skill_fails_screening():
    candidate_skills = {
        "SKL-002": {"proficiency_level": "Intermediate", "years_experience": 2.0},
    }
    # SKL-001 is mandatory but candidate lacks it
    rules = [
        {"skill_id": "SKL-001", "is_mandatory": True, "min_proficiency": "Intermediate", "weight": 2.0},
    ]

    score, passed, reason, breakdown = calculate_candidate_score(
        candidate_experience=5.0,
        candidate_education="BSc",
        candidate_domain="Distributed Backend",
        candidate_skills=candidate_skills,
        req_min_experience=3,
        req_title="Backend Engineer",
        screening_rules=rules,
    )

    assert passed is False
    assert breakdown["mandatory_failed"] is True
    assert "Missing mandatory skill" in reason


def test_insufficient_experience_penalized():
    candidate_skills = {
        "SKL-001": {"proficiency_level": "Advanced", "years_experience": 1.0},
    }
    rules = [
        {"skill_id": "SKL-001", "is_mandatory": False, "min_proficiency": "Intermediate", "weight": 1.0},
    ]

    # Candidate has 1 year experience, role requires 8 years
    score, passed, reason, breakdown = calculate_candidate_score(
        candidate_experience=1.0,
        candidate_education="Bootcamp",
        candidate_domain="General",
        candidate_skills=candidate_skills,
        req_min_experience=8,
        req_title="Principal Architect",
        screening_rules=rules,
    )

    assert breakdown["experience_score"] < 50.0
    assert score < SCREENING_PASS_THRESHOLD
    assert passed is False
