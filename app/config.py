"""Application configuration and constants."""
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_URL = f"sqlite:///{DATA_DIR / 'recruitment.db'}"

# Deterministic Seed
DEFAULT_SEED = 20261022

# Baseline Synthetic Dataset Target Counts
BASELINE_TARGETS = {
    "num_requisitions": 100,
    "num_candidates": 2000,
    "num_applications": 3000,
    "num_interviews": 600,
    "num_offers": 150,
}

# Fast Test Target Counts (for fast unit testing)
TEST_TARGETS = {
    "num_requisitions": 12,
    "num_candidates": 60,
    "num_applications": 90,
    "num_interviews": 30,
    "num_offers": 10,
}

# Lifecycle Enums
REQUISITION_STATUSES = ["DRAFT", "APPROVED", "OPEN", "CLOSED"]
APPLICATION_STATUSES = [
    "APPLIED",
    "SCREENING",
    "INTERVIEWING",
    "OFFERED",
    "HIRED",
    "REJECTED",
    "WITHDRAWN",
]
INTERVIEW_STAGES = [
    "TECHNICAL_SCREEN",
    "SYSTEM_DESIGN",
    "BEHAVIORAL",
    "FINAL_ROUND",
]
INTERVIEW_STATUSES = ["SCHEDULED", "COMPLETED", "CANCELLED"]
OFFER_APPROVAL_STATUSES = ["PENDING_APPROVAL", "APPROVED", "REJECTED"]
CANDIDATE_DECISIONS = ["PENDING", "ACCEPTED", "DECLINED"]
PROFICIENCY_LEVELS = ["Beginner", "Intermediate", "Advanced", "Expert"]
EDUCATION_LEVELS = ["BSc", "MSc", "PhD", "Bootcamp"]
ROLE_LEVELS = ["L4", "L5", "L6", "Principal"]

# Anomaly Types
ANOMALY_UNAVAILABLE_INTERVIEWER = "INTERVIEW_UNAVAILABLE_INTERVIEWER"
ANOMALY_DUPLICATE_APPLICATION = "DUPLICATE_APPLICATION"
ANOMALY_MISSING_FEEDBACK = "MISSING_FEEDBACK_STAGE_ADVANCED"
ANOMALY_SALARY_OUTSIDE_BAND = "SALARY_OUTSIDE_BAND"
ANOMALY_CLOSED_ROLE_ACTIVE_APP = "CLOSED_ROLE_ACTIVE_APPLICATION"
