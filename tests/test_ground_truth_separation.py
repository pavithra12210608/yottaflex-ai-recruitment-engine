"""Tests for architectural ground truth separation and zero feature leakage."""
import os
import json
import pytest
import pandas as pd
from app.config import DATA_DIR, TEST_TARGETS
from app.generators.synthetic_data_generator import SyntheticDataGenerator


def test_ground_truth_files_exist_and_isolated():
    gt_csv = DATA_DIR / "ground_truth.csv"
    gt_json = DATA_DIR / "ground_truth.json"

    assert gt_csv.exists(), "ground_truth.csv must exist in data directory"
    assert gt_json.exists(), "ground_truth.json must exist in data directory"

    with open(gt_json, "r", encoding="utf-8") as f:
        gt_data = json.load(f)

    assert isinstance(gt_data, list)
    assert len(gt_data) >= 5

    # Confirm required schema in ground truth
    required_keys = {"anomaly_id", "issue_type", "target_entity", "target_id", "details", "severity", "expected_resolution"}
    for item in gt_data:
        assert required_keys.issubset(set(item.keys()))


def test_zero_leakage_into_feature_tables():
    """Verify that none of the core business entity tables contain ground truth metadata columns."""
    forbidden_columns = {"anomaly_id", "is_anomaly", "ground_truth", "issue_type", "expected_resolution"}

    entity_files = [
        "departments.csv",
        "requisitions.csv",
        "candidates.csv",
        "resume_artifacts.csv",
        "skills.csv",
        "candidate_skills.csv",
        "applications.csv",
        "screening_rules.csv",
        "interviews.csv",
        "interviewers.csv",
        "feedback.csv",
        "offers.csv",
    ]

    for fname in entity_files:
        fpath = DATA_DIR / fname
        if fpath.exists():
            df = pd.read_csv(fpath)
            cols = set(df.columns)
            leakage = cols.intersection(forbidden_columns)
            assert not leakage, f"Data leakage detected! File {fname} contains forbidden columns: {leakage}"
