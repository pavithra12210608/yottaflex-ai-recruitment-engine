"""Tests for full validation engine reporting and severity classifications."""
import pytest
from app.config import TEST_TARGETS
from app.generators.synthetic_data_generator import SyntheticDataGenerator
from app.validators.validation_engine import ValidationEngine


def test_validation_engine_full_report():
    gen = SyntheticDataGenerator(seed=20261022)
    entities, _ = gen.generate(**TEST_TARGETS)

    validator = ValidationEngine(entities)
    report = validator.run_all_validations()

    assert "status" in report
    assert "total_checks" in report
    assert "passed_checks" in report
    assert "failed_checks" in report
    assert "findings" in report
    assert isinstance(report["findings"], list)

    # Because our generator injects the 5 required intentional anomalies,
    # the failed_checks count must equal 5 and status must be FAIL.
    assert report["failed_checks"] == 5
    assert report["status"] == "FAIL"

    # Verify that each finding contains check_name, entity, severity, and informative message
    for f in report["findings"]:
        assert f["severity"] in ["PASS", "FAIL", "WARNING"]
        assert len(f["message"]) > 0
        assert f["check_name"] is not None
