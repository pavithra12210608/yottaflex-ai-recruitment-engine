"""Tests for offer salary band compliance and anomaly detection (Anomaly 4)."""
import pytest
from app.config import TEST_TARGETS, ANOMALY_SALARY_OUTSIDE_BAND
from app.generators.synthetic_data_generator import SyntheticDataGenerator
from app.validators.validation_engine import ValidationEngine


def test_salary_outside_band_detected():
    gen = SyntheticDataGenerator(seed=20261022)
    entities, ground_truth = gen.generate(**TEST_TARGETS)

    # Check ground truth
    salary_gt = [gt for gt in ground_truth if gt["issue_type"] == ANOMALY_SALARY_OUTSIDE_BAND]
    assert len(salary_gt) >= 1
    target_off_id = salary_gt[0]["target_id"]

    # Validate
    validator = ValidationEngine(entities)
    report = validator.run_all_validations()

    findings = [f for f in report["findings"] if f["check_name"] == ANOMALY_SALARY_OUTSIDE_BAND]
    assert len(findings) >= 1
    assert any(f["record_id"] == target_off_id for f in findings)


def test_salary_within_band_passes():
    entities = {
        "job_requisitions": [
            {"requisition_id": "REQ-1", "min_salary": 100000.0, "max_salary": 150000.0}
        ],
        "applications": [
            {"application_id": "APP-1", "requisition_id": "REQ-1"}
        ],
        "offers": [
            {"offer_id": "OFF-1", "application_id": "APP-1", "offered_salary": 125000.0}
        ],
    }

    validator = ValidationEngine(entities)
    validator.validate_salary_bands()

    failures = [f for f in validator.findings if f["severity"] == "FAIL"]
    assert len(failures) == 0
