"""Tests for missing feedback anomaly when stage is advanced (Anomaly 3)."""
import pytest
from app.config import TEST_TARGETS, ANOMALY_MISSING_FEEDBACK
from app.generators.synthetic_data_generator import SyntheticDataGenerator
from app.validators.validation_engine import ValidationEngine


def test_missing_feedback_stage_advanced_detected():
    gen = SyntheticDataGenerator(seed=20261022)
    entities, ground_truth = gen.generate(**TEST_TARGETS)

    # Ground truth verification
    missing_gt = [gt for gt in ground_truth if gt["issue_type"] == ANOMALY_MISSING_FEEDBACK]
    assert len(missing_gt) >= 1

    # Validation engine verification
    validator = ValidationEngine(entities)
    report = validator.run_all_validations()

    findings = [f for f in report["findings"] if f["check_name"] == ANOMALY_MISSING_FEEDBACK]
    assert len(findings) >= 1
    assert any("advanced to stage" in f["message"] for f in findings)


def test_complete_feedback_passes():
    entities = {
        "applications": [
            {"application_id": "APP-1", "status": "OFFERED"}
        ],
        "interviews": [
            {"interview_id": "INT-1", "application_id": "APP-1"}
        ],
        "feedback": [
            {"interview_id": "INT-1", "feedback_id": "FB-1"}
        ],
    }
    validator = ValidationEngine(entities)
    validator.validate_missing_feedback()

    failures = [f for f in validator.findings if f["severity"] == "FAIL"]
    assert len(failures) == 0
