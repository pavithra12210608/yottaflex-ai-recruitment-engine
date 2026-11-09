"""Tests for interviewer availability and scheduling conflicts (Anomaly 1)."""
import pytest
from app.config import TEST_TARGETS, ANOMALY_UNAVAILABLE_INTERVIEWER
from app.generators.synthetic_data_generator import SyntheticDataGenerator
from app.validators.validation_engine import ValidationEngine


def test_unavailable_interviewer_detected():
    gen = SyntheticDataGenerator(seed=20261022)
    entities, ground_truth = gen.generate(**TEST_TARGETS)

    # Check ground truth
    unavail_gt = [gt for gt in ground_truth if gt["issue_type"] == ANOMALY_UNAVAILABLE_INTERVIEWER]
    assert len(unavail_gt) >= 1
    target_int_id = unavail_gt[0]["target_id"]

    # Validate
    validator = ValidationEngine(entities)
    report = validator.run_all_validations()

    findings = [f for f in report["findings"] if f["check_name"] == ANOMALY_UNAVAILABLE_INTERVIEWER]
    assert len(findings) >= 1
    assert any(f["record_id"] == target_int_id for f in findings)


def test_interviewer_valid_schedule_passes():
    entities = {
        "interviewers": [
            {"interviewer_id": "EMP-0001", "available_days": "Monday,Wednesday,Friday"}
        ],
        "interviews": [
            {"interview_id": "INT-2026-000001", "interviewer_id": "EMP-0001", "scheduled_day": "Monday"}
        ],
    }

    validator = ValidationEngine(entities)
    validator.validate_interviewer_availability()

    failures = [f for f in validator.findings if f["severity"] == "FAIL"]
    assert len(failures) == 0
