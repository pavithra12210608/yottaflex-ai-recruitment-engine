"""Web UI route controllers rendering HTML pages via Jinja2."""
import os
import tempfile
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import DEFAULT_SEED, TEST_TARGETS
from app.models import (
    Department,
    JobRequisition,
    Candidate,
    Application,
    Interview,
    Offer,
)
from app.services.recruitment_service import (
    get_dashboard_summary,
    load_ground_truth,
    load_entities_from_csv,
    compute_dataset_hashes,
)
from app.validators.validation_engine import ValidationEngine
from app.generators.synthetic_data_generator import SyntheticDataGenerator

templates_dir = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
@router.get("/ui/dashboard", response_class=HTMLResponse)
def dashboard_view(request: Request, db: Session = Depends(get_db)):
    """Render main operations dashboard."""
    stats = get_dashboard_summary(db)
    return templates.TemplateResponse("dashboard.html", {"request": request, "stats": stats})


@router.get("/ui/requisitions", response_class=HTMLResponse)
def requisitions_view(request: Request, db: Session = Depends(get_db)):
    """Render requisitions catalog."""
    reqs = db.query(JobRequisition).all()
    return templates.TemplateResponse("requisitions.html", {"request": request, "requisitions": reqs})


@router.get("/ui/candidates", response_class=HTMLResponse)
def candidates_view(request: Request, db: Session = Depends(get_db)):
    """Render candidates listing."""
    candidates = db.query(Candidate).limit(100).all()
    return templates.TemplateResponse("candidates.html", {"request": request, "candidates": candidates})


@router.get("/ui/applications", response_class=HTMLResponse)
def applications_view(request: Request, db: Session = Depends(get_db)):
    """Render applications pipeline."""
    apps = db.query(Application).limit(150).all()
    return templates.TemplateResponse("applications.html", {"request": request, "applications": apps})


@router.get("/ui/applications/{application_id}", response_class=HTMLResponse)
def application_detail_view(application_id: str, request: Request, db: Session = Depends(get_db)):
    """Render 360-degree candidate application dossier."""
    app_record = db.query(Application).filter(Application.application_id == application_id).first()
    if not app_record:
        raise HTTPException(status_code=404, detail="Application not found")
    return templates.TemplateResponse("application_detail.html", {"request": request, "app": app_record})


@router.get("/ui/interviews", response_class=HTMLResponse)
def interviews_view(request: Request, db: Session = Depends(get_db)):
    """Render scheduled interviews and feedback."""
    interviews = db.query(Interview).limit(100).all()
    return templates.TemplateResponse("interviews.html", {"request": request, "interviews": interviews})


@router.get("/ui/offers", response_class=HTMLResponse)
def offers_view(request: Request, db: Session = Depends(get_db)):
    """Render offers and decision tracker."""
    offers = db.query(Offer).limit(100).all()
    return templates.TemplateResponse("offers.html", {"request": request, "offers": offers})


@router.get("/ui/anomalies", response_class=HTMLResponse)
def anomalies_view(request: Request):
    """Render intentional ground-truth negative scenarios."""
    anomalies = load_ground_truth()
    return templates.TemplateResponse("anomalies.html", {"request": request, "anomalies": anomalies})


@router.get("/ui/validation", response_class=HTMLResponse)
def validation_view(request: Request):
    """Render real-time validation compliance engine report."""
    entities = load_entities_from_csv()
    validator = ValidationEngine(entities)
    report = validator.run_all_validations()
    return templates.TemplateResponse("validation.html", {"request": request, "report": report})


@router.get("/ui/reproducibility", response_class=HTMLResponse)
def reproducibility_view(request: Request):
    """Render bitwise reproducibility matrix comparison."""
    t1 = tempfile.mkdtemp(prefix="rep_ui_1_")
    t2 = tempfile.mkdtemp(prefix="rep_ui_2_")

    try:
        gen1 = SyntheticDataGenerator(seed=DEFAULT_SEED)
        ent1, gt1 = gen1.generate(num_requisitions=10, num_candidates=50, num_applications=80, num_interviews=25, num_offers=10)
        gen1.export_to_csv(ent1, gt1, t1)
        h1 = compute_dataset_hashes(t1)

        gen2 = SyntheticDataGenerator(seed=DEFAULT_SEED)
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
                "h1": h1.get(k),
                "h2": h2.get(k),
                "match": matched,
            })

        return templates.TemplateResponse(
            "reproducibility.html",
            {
                "request": request,
                "comparison": comparison,
                "is_reproducible": is_reproducible,
            },
        )
    finally:
        shutil.rmtree(t1, ignore_errors=True)
        shutil.rmtree(t2, ignore_errors=True)
