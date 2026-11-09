"""Tests for active applications on closed requisitions (Anomaly 5)."""
import pytest
from app.config import TEST_TARGETS, ANOMALY_CLOSED_ROLE_ACTIVE_APP
from app.generators.synthetic_data_generator import SyntheticDataGenerator
from app.validators.validation_engine import ValidationEngine


def test_closed_role_active_application_detected():
    gen = SyntheticDataGenerator(seed=20261022)
    entities, ground_truth = gen.generate(**TEST_TARGETS)

    # Check ground truth
    closed_gt = [gt for gt in ground_truth if gt["issue_type"] == ANOMALY_CLOSED_ROLE_ACTIVE_APP]
    assert len(closed_gt) >= 1
    target_app_id = closed_gt[0]["target_id"]

    # Validate
    validator = ValidationEngine(entities)
    report = validator.run_all_validations()

    findings = [f for f in report["findings"] if f["check_name"] == ANOMALY_CLOSED_ROLE_ACTIVE_APP]
    assert len(findings) >= 1
    assert any(f["record_id"] == target_app_id for f in findings)


def test_closed_role_terminal_application_passes():
    entities = {
        "job_requisitions": [
            {"requisition_id": "REQ-1", "status": "CLOSED"}
        ],
        "applications": [
            {"application_id": "APP-1", "requisition_id": "REQ-1", "status": "REJECTED"}
        ],
    }

    validator = ValidationEngine(entities)
    validator.validate_closed_requisitions_active_apps()

    failures = [f for f in validator.findings if f["severity"] == "FAIL"]
    assert len(failures) == 0
