"""Recruitment Service layer for querying, seeding, and business workflows."""
import os
import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import pandas as pd
from sqlalchemy.orm import Session

from app.config import (
    DATA_DIR,
    DEFAULT_SEED,
    BASELINE_TARGETS,
    TEST_TARGETS,
)
from app.models import (
    Department,
    JobRequisition,
    Candidate,
    ResumeArtifact,
    Skill,
    CandidateSkill,
    ScreeningRule,
    Application,
    Interviewer,
    Interview,
    Feedback,
    Offer,
)
from app.generators.synthetic_data_generator import SyntheticDataGenerator
from app.validators.validation_engine import ValidationEngine


def seed_database_from_entities(db: Session, entities: Dict[str, List[Dict[str, Any]]]):
    """Clears existing database records and inserts all generated entities in dependency order."""
    # Delete child tables first to avoid FK constraint violations
    db.query(Feedback).delete()
    db.query(Interview).delete()
    db.query(Offer).delete()
    db.query(Application).delete()
    db.query(ScreeningRule).delete()
    db.query(CandidateSkill).delete()
    db.query(ResumeArtifact).delete()
    db.query(Candidate).delete()
    db.query(Interviewer).delete()
    db.query(JobRequisition).delete()
    db.query(Skill).delete()
    db.query(Department).delete()
    db.commit()

    # 1. Departments
    for d in entities["departments"]:
        db.add(Department(**d))
    db.commit()

    # 2. Skills
    for s in entities["skills"]:
        db.add(Skill(**s))
    db.commit()

    # 3. Job Requisitions
    for r in entities["job_requisitions"]:
        db.add(JobRequisition(**r))
    db.commit()

    # 4. Interviewers
    for i in entities["interviewers"]:
        db.add(Interviewer(**i))
    db.commit()

    # 5. Candidates
    for c in entities["candidates"]:
        db.add(Candidate(**c))
    db.commit()

    # 6. Resume Artifacts
    for ra in entities["resume_artifacts"]:
        db.add(ResumeArtifact(**ra))
    db.commit()

    # 7. Candidate Skills
    for cs in entities["candidate_skills"]:
        db.add(CandidateSkill(**cs))
    db.commit()

    # 8. Screening Rules
    for sr in entities["screening_rules"]:
        db.add(ScreeningRule(**sr))
    db.commit()

    # 9. Applications
    for a in entities["applications"]:
        db.add(Application(**a))
    db.commit()

    # 10. Interviews
    for intv in entities["interviews"]:
        db.add(Interview(**intv))
    db.commit()

    # 11. Feedback
    for fb in entities["feedback"]:
        db.add(Feedback(**fb))
    db.commit()

    # 12. Offers
    for off in entities["offers"]:
        db.add(Offer(**off))
    db.commit()


def load_entities_from_csv(data_dir: str = str(DATA_DIR)) -> Dict[str, List[Dict[str, Any]]]:
    """Reads all entity CSVs from the data directory into in-memory dictionaries."""
    files = {
        "departments": "departments.csv",
        "job_requisitions": "requisitions.csv",
        "candidates": "candidates.csv",
        "resume_artifacts": "resume_artifacts.csv",
        "skills": "skills.csv",
        "candidate_skills": "candidate_skills.csv",
        "screening_rules": "screening_rules.csv",
        "applications": "applications.csv",
        "interviewers": "interviewers.csv",
        "interviews": "interviews.csv",
        "feedback": "feedback.csv",
        "offers": "offers.csv",
    }
    entities = {}
    for key, filename in files.items():
        path = os.path.join(data_dir, filename)
        if os.path.exists(path):
            df = pd.read_csv(path)
            # Replace NaN with None
            entities[key] = df.where(pd.notnull(df), None).to_dict(orient="records")
        else:
            entities[key] = []
    return entities


def load_ground_truth(data_dir: str = str(DATA_DIR)) -> List[Dict[str, Any]]:
    """Loads independent ground truth anomalies from ground_truth.json."""
    gt_path = os.path.join(data_dir, "ground_truth.json")
    if os.path.exists(gt_path):
        with open(gt_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def generate_and_save_data(
    seed: int = DEFAULT_SEED,
    num_requisitions: int = 100,
    num_candidates: int = 2000,
    num_applications: int = 3000,
    num_interviews: int = 600,
    num_offers: int = 150,
    db: Optional[Session] = None,
) -> Tuple[Dict[str, int], int]:
    """Generates synthetic dataset, exports CSVs/JSON, and optionally updates SQLite DB."""
    generator = SyntheticDataGenerator(seed=seed)
    entities, ground_truth = generator.generate(
        num_requisitions=num_requisitions,
        num_candidates=num_candidates,
        num_applications=num_applications,
        num_interviews=num_interviews,
        num_offers=num_offers,
    )

    # Export to CSV / JSON
    generator.export_to_csv(entities, ground_truth, str(DATA_DIR))

    # Seed Database if session provided
    if db:
        seed_database_from_entities(db, entities)

    row_counts = {k: len(v) for k, v in entities.items()}
    return row_counts, len(ground_truth)


def get_dashboard_summary(db: Session) -> Dict[str, Any]:
    """Calculates aggregated dashboard metrics."""
    tot_depts = db.query(Department).count()
    tot_reqs = db.query(JobRequisition).count()
    tot_cands = db.query(Candidate).count()
    tot_apps = db.query(Application).count()
    tot_ints = db.query(Interview).count()
    tot_offers = db.query(Offer).count()

    # Application Status breakdown
    app_statuses = db.query(Application.status).all()
    status_counts = {}
    for (st,) in app_statuses:
        status_counts[st] = status_counts.get(st, 0) + 1

    # Offers Decision breakdown
    offer_decisions = db.query(Offer.candidate_decision).all()
    decision_counts = {}
    for (dec,) in offer_decisions:
        decision_counts[dec] = decision_counts.get(dec, 0) + 1

    # Screening pass rate
    passed_apps = db.query(Application).filter(Application.screening_passed == True).count()
    pass_rate = round((passed_apps / tot_apps * 100.0) if tot_apps > 0 else 0.0, 1)

    # Count known anomalies in ground truth
    gt = load_ground_truth()

    return {
        "total_departments": tot_depts,
        "total_requisitions": tot_reqs,
        "total_candidates": tot_cands,
        "total_applications": tot_apps,
        "total_interviews": tot_ints,
        "total_offers": tot_offers,
        "total_anomalies_flagged": len(gt),
        "applications_by_status": status_counts,
        "offers_by_decision": decision_counts,
        "screening_pass_rate": pass_rate,
    }


def compute_dataset_hashes(data_dir: str = str(DATA_DIR)) -> Dict[str, str]:
    """Computes SHA-256 hashes of all generated CSVs and ground_truth files."""
    files = [
        "departments.csv",
        "requisitions.csv",
        "candidates.csv",
        "resume_artifacts.csv",
        "skills.csv",
        "candidate_skills.csv",
        "screening_rules.csv",
        "applications.csv",
        "interviewers.csv",
        "interviews.csv",
        "feedback.csv",
        "offers.csv",
        "ground_truth.csv",
        "ground_truth.json",
    ]
    checksums = {}
    for fname in files:
        fpath = os.path.join(data_dir, fname)
        if os.path.exists(fpath):
            with open(fpath, "rb") as f:
                checksums[fname] = hashlib.sha256(f.read()).hexdigest()
        else:
            checksums[fname] = "MISSING"
    return checksums
