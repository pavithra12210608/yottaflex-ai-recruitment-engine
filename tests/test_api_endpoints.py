"""Tests for FastAPI REST API route endpoints and responses."""
import pytest
from app.database import init_db, SessionLocal
from app.routes.api import (
    health_check,
    get_dashboard,
    list_departments,
    list_requisitions,
    list_candidates,
    list_applications,
    get_application_detail,
    list_interviews,
    list_offers,
    list_anomalies,
    get_validation_report,
    trigger_validation,
    run_reproducibility_check,
)


@pytest.fixture(scope="module")
def db_session():
    init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_health_endpoint():
    res = health_check()
    assert res["status"] == "healthy"
    assert "YottaFlex" in res["service"]


def test_dashboard_endpoint(db_session):
    res = get_dashboard(db=db_session)
    assert res["total_departments"] >= 6
    assert res["total_requisitions"] >= 10
    assert res["total_applications"] >= 10
    assert "screening_pass_rate" in res


def test_departments_endpoint(db_session):
    depts = list_departments(db=db_session)
    assert len(depts) >= 6
    assert any(d.code == "AI" for d in depts)


def test_requisitions_endpoint(db_session):
    reqs = list_requisitions(limit=10, offset=0, db=db_session)
    assert len(reqs) > 0
    assert len(reqs) <= 10
    assert reqs[0].requisition_id.startswith("REQ-2026-")


def test_candidates_endpoint(db_session):
    cands = list_candidates(limit=10, offset=0, db=db_session)
    assert len(cands) > 0
    assert len(cands) <= 10
    assert cands[0].candidate_id.startswith("CAND-")


def test_applications_endpoint(db_session):
    apps = list_applications(limit=10, offset=0, db=db_session)
    assert len(apps) > 0
    assert len(apps) <= 10

    # Test single application detail
    first_app_id = apps[0].application_id
    detail = get_application_detail(application_id=first_app_id, db=db_session)
    assert detail.application_id == first_app_id
    assert detail.candidate_details is not None


def test_interviews_endpoint(db_session):
    intvs = list_interviews(limit=10, offset=0, db=db_session)
    assert len(intvs) > 0
    assert len(intvs) <= 10
    assert intvs[0].interview_id.startswith("INT-2026-")


def test_offers_endpoint(db_session):
    offers = list_offers(limit=10, offset=0, db=db_session)
    assert len(offers) > 0
    assert len(offers) <= 10
    assert offers[0].offer_id.startswith("OFF-2026-")


def test_anomalies_endpoint():
    anomalies = list_anomalies()
    assert len(anomalies) >= 5
    issue_types = {a["issue_type"] for a in anomalies}
    assert "INTERVIEW_UNAVAILABLE_INTERVIEWER" in issue_types
    assert "DUPLICATE_APPLICATION" in issue_types
    assert "MISSING_FEEDBACK_STAGE_ADVANCED" in issue_types
    assert "SALARY_OUTSIDE_BAND" in issue_types
    assert "CLOSED_ROLE_ACTIVE_APPLICATION" in issue_types


def test_validation_endpoints():
    get_res = get_validation_report()
    assert get_res["total_checks"] > 0
    assert get_res["status"] == "FAIL"  # Because intentional anomalies are benchmarked

    post_res = trigger_validation()
    assert post_res["total_checks"] > 0


def test_reproducibility_endpoint():
    res = run_reproducibility_check(seed=20261022)
    assert res["reproducible"] is True
    assert "100% bitwise identical" in res["message"]
