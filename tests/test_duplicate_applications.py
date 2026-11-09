"""Tests for duplicate candidate application detection (Anomaly 2)."""
import pytest
from app.config import TEST_TARGETS, ANOMALY_DUPLICATE_APPLICATION
from app.generators.synthetic_data_generator import SyntheticDataGenerator
from app.validators.validation_engine import ValidationEngine


def test_duplicate_application_detected():
    gen = SyntheticDataGenerator(seed=20261022)
    entities, ground_truth = gen.generate(**TEST_TARGETS)

    # Confirm ground truth logs the duplicate anomaly
    dup_gt = [gt for gt in ground_truth if gt["issue_type"] == ANOMALY_DUPLICATE_APPLICATION]
    assert len(dup_gt) >= 1
    dup_record_id = dup_gt[0]["target_id"]

    # Run validation engine
    validator = ValidationEngine(entities)
    report = validator.run_all_validations()

    # Verify validator finds the exact duplicate
    dup_findings = [f for f in report["findings"] if f["check_name"] == ANOMALY_DUPLICATE_APPLICATION]
    assert len(dup_findings) >= 1
    assert any(f["record_id"] == dup_record_id for f in dup_findings)


def test_no_false_positive_duplicates_when_unique():
    gen = SyntheticDataGenerator(seed=20261022)
    entities, _ = gen.generate(**TEST_TARGETS)

    # Remove the intentional duplicate record
    entities["applications"] = [a for a in entities["applications"] if not a["application_id"].endswith("-DUP")]

    validator = ValidationEngine(entities)
    validator.validate_duplicate_applications()

    dup_findings = [f for f in validator.findings if f["check_name"] == ANOMALY_DUPLICATE_APPLICATION]
    assert len(dup_findings) == 0
