"""REST API endpoints for YottaFlex AI Recruitment Engine."""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import DEFAULT_SEED
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
from app.schemas import (
    DepartmentResponse,
    JobRequisitionResponse,
    CandidateResponse,
    ApplicationResponse,
    ApplicationDetailResponse,
    InterviewResponse,
    OfferResponse,
    AnomalyItem,
    DashboardStats,
    ValidationReportResponse,
    GenerateDataRequest,
    GenerateDataResponse,
    ReproducibilityResponse,
)
from app.services.recruitment_service import (
    get_dashboard_summary,
    load_ground_truth,
    load_entities_from_csv,
    generate_and_save_data,
    compute_dataset_hashes,
)
from app.validators.validation_engine import ValidationEngine
from app.generators.synthetic_data_generator import SyntheticDataGenerator

router = APIRouter()


@router.get("/health", tags=["System"])
def health_check():
    """Health status and service availability."""
    return {"status": "healthy", "service": "YottaFlex AI Recruitment Engine", "version": "1.0.0"}


@router.get("/dashboard", response_model=DashboardStats, tags=["Analytics"])
def get_dashboard(db: Session = Depends(get_db)):
    """Summary dashboard metrics including pipeline counts and rates."""
    return get_dashboard_summary(db)


@router.get("/departments", response_model=List[DepartmentResponse], tags=["Master Data"])
def list_departments(db: Session = Depends(get_db)):
    """List all corporate departments."""
    return db.query(Department).all()


@router.get("/requisitions", response_model=List[JobRequisitionResponse], tags=["Recruitment"])
def list_requisitions(
    department_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """List job requisitions with optional filters and pagination."""
    query = db.query(JobRequisition)
    if department_id:
        query = query.filter(JobRequisition.department_id == department_id)
    if status:
        query = query.filter(JobRequisition.status == status)

    reqs = query.offset(offset).limit(limit).all()
    results = []
    for r in reqs:
        res = JobRequisitionResponse.model_validate(r)
        res.department_name = r.department.name if r.department else None
        res.application_count = len(r.applications) if r.applications else 0
        results.append(res)
    return results


@router.get("/candidates", response_model=List[CandidateResponse], tags=["Recruitment"])
def list_candidates(
    education: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """List synthetic candidates with skills and resume artifacts."""
    query = db.query(Candidate)
    if education:
        query = query.filter(Candidate.highest_education == education)

    cands = query.offset(offset).limit(limit).all()
    return cands


@router.get("/applications", response_model=List[ApplicationResponse], tags=["Recruitment"])
def list_applications(
    requisition_id: Optional[str] = None,
    candidate_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """List candidate applications with deterministic screening outcomes."""
    query = db.query(Application)
    if requisition_id:
        query = query.filter(Application.requisition_id == requisition_id)
    if candidate_id:
        query = query.filter(Application.candidate_id == candidate_id)
    if status:
        query = query.filter(Application.status == status)

    apps = query.offset(offset).limit(limit).all()
    results = []
    for a in apps:
        item = ApplicationResponse.model_validate(a)
        item.candidate_name = a.candidate.full_name if a.candidate else None
        item.candidate_email = a.candidate.email if a.candidate else None
        item.requisition_title = a.requisition.title if a.requisition else None
        item.department_name = a.requisition.department.name if (a.requisition and a.requisition.department) else None
        results.append(item)
    return results


@router.get("/applications/{application_id}", response_model=ApplicationDetailResponse, tags=["Recruitment"])
def get_application_detail(application_id: str, db: Session = Depends(get_db)):
    """Get complete 360-degree application dossier including candidate, requisition, interviews, and offer."""
    app = db.query(Application).filter(Application.application_id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    detail = ApplicationDetailResponse.model_validate(app)
    detail.candidate_name = app.candidate.full_name if app.candidate else None
    detail.candidate_email = app.candidate.email if app.candidate else None
    detail.requisition_title = app.requisition.title if app.requisition else None
    detail.department_name = app.requisition.department.name if (app.requisition and app.requisition.department) else None

    if app.candidate:
        detail.candidate_details = CandidateResponse.model_validate(app.candidate)
    if app.requisition:
        detail.requisition_details = JobRequisitionResponse.model_validate(app.requisition)

    detail.interviews = [InterviewResponse.model_validate(i) for i in app.interviews]
    if app.offer:
        detail.offer = OfferResponse.model_validate(app.offer)

    return detail


@router.get("/interviews", response_model=List[InterviewResponse], tags=["Recruitment"])
def list_interviews(
    stage: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """List scheduled interviews and submitted structured feedback."""
    query = db.query(Interview)
    if stage:
        query = query.filter(Interview.stage == stage)

    intvs = query.offset(offset).limit(limit).all()
    results = []
    for i in intvs:
        res = InterviewResponse.model_validate(i)
        res.interviewer_name = i.interviewer.name if i.interviewer else None
        results.append(res)
    return results


@router.get("/offers", response_model=List[OfferResponse], tags=["Recruitment"])
def list_offers(
    decision: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """List formal job offers with approval states and candidate decisions."""
    query = db.query(Offer)
    if decision:
        query = query.filter(Offer.candidate_decision == decision)

    offers = query.offset(offset).limit(limit).all()
    results = []
    for o in offers:
        res = OfferResponse.model_validate(o)
        if o.application:
            res.candidate_name = o.application.candidate.full_name if o.application.candidate else None
            res.requisition_title = o.application.requisition.title if o.application.requisition else None
        results.append(res)
    return results


@router.get("/anomalies", response_model=List[AnomalyItem], tags=["Quality & Compliance"])
def list_anomalies():
    """Retrieve independently stored ground truth anomalies and negative test cases."""
    return load_ground_truth()


@router.get("/validation", response_model=ValidationReportResponse, tags=["Quality & Compliance"])
def get_validation_report():
    """Execute live validation suite against current dataset and return detailed report."""
    entities = load_entities_from_csv()
    validator = ValidationEngine(entities)
    return validator.run_all_validations()


@router.post("/validate", response_model=ValidationReportResponse, tags=["Quality & Compliance"])
def trigger_validation():
    """Trigger full validation run on demand."""
    entities = load_entities_from_csv()
    validator = ValidationEngine(entities)
    return validator.run_all_validations()


@router.post("/generate", response_model=GenerateDataResponse, tags=["Data Management"])
def generate_dataset(req: GenerateDataRequest, db: Session = Depends(get_db)):
    """Trigger deterministic synthetic data generation with custom seed and size parameters."""
    row_counts, anomalies_count = generate_and_save_data(
        seed=req.seed,
        num_requisitions=req.num_requisitions,
        num_candidates=req.num_candidates,
        num_applications=req.num_applications,
        num_interviews=req.num_interviews,
        num_offers=req.num_offers,
        db=db,
    )
    return {
        "message": "Dataset generated and database seeded successfully.",
        "seed": req.seed,
        "row_counts": row_counts,
        "anomalies_injected": anomalies_count,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/reproducibility", response_model=ReproducibilityResponse, tags=["Quality & Compliance"])
def run_reproducibility_check(seed: int = DEFAULT_SEED):
    """Verify bitwise reproducibility by running 2 distinct generations with given seed and comparing checksums."""
    import tempfile
    import shutil

    t1 = tempfile.mkdtemp(prefix="rep_api_1_")
    t2 = tempfile.mkdtemp(prefix="rep_api_2_")

    try:
        gen1 = SyntheticDataGenerator(seed=seed)
        ent1, gt1 = gen1.generate(num_requisitions=10, num_candidates=50, num_applications=80, num_interviews=25, num_offers=10)
        gen1.export_to_csv(ent1, gt1, t1)
        h1 = compute_dataset_hashes(t1)

        gen2 = SyntheticDataGenerator(seed=seed)
        ent2, gt2 = gen2.generate(num_requisitions=10, num_candidates=50, num_applications=80, num_interviews=25, num_offers=10)
        gen2.export_to_csv(ent2, gt2, t2)
        h2 = compute_dataset_hashes(t2)

        comparison = []
        is_reproducible = True
        all_keys = sorted(set(h1.keys()) | set(h2.keys()))
        for k in all_keys:
            matched = (h1.get(k) == h2.get(k)) and (h1.get(k) != "MISSING")
            if not matched:
                is_reproducible = False
            comparison.append({
                "file": k,
                "run_1_hash": h1.get(k),
                "run_2_hash": h2.get(k),
                "matches": matched,
            })

        return {
            "reproducible": is_reproducible,
            "seed": seed,
            "run_1_checksums": h1,
            "run_2_checksums": h2,
            "comparison_details": comparison,
            "message": "100% bitwise identical hashes verified." if is_reproducible else "Hash mismatch detected.",
        }
    finally:
        shutil.rmtree(t1, ignore_errors=True)
        shutil.rmtree(t2, ignore_errors=True)
