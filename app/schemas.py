"""Pydantic schemas for request validation and API responses."""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, ConfigDict


# ==================== Master Data Schemas ====================

class DepartmentBase(BaseModel):
    department_id: str
    name: str
    code: str
    cost_center: str

class DepartmentResponse(DepartmentBase):
    model_config = ConfigDict(from_attributes=True)


class SkillBase(BaseModel):
    skill_id: str
    name: str
    category: str

class SkillResponse(SkillBase):
    model_config = ConfigDict(from_attributes=True)


class CandidateSkillBase(BaseModel):
    skill_id: str
    proficiency_level: str
    years_experience: float

class CandidateSkillResponse(CandidateSkillBase):
    skill_name: Optional[str] = None
    category: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ScreeningRuleBase(BaseModel):
    rule_id: str
    requisition_id: str
    skill_id: str
    is_mandatory: bool
    min_proficiency: str
    weight: float

class ScreeningRuleResponse(ScreeningRuleBase):
    skill_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# ==================== Core Business Schemas ====================

class JobRequisitionBase(BaseModel):
    requisition_id: str
    department_id: str
    title: str
    role_level: str
    min_years_experience: int
    min_salary: float
    max_salary: float
    status: str
    open_date: str
    close_date: Optional[str] = None

class JobRequisitionResponse(JobRequisitionBase):
    department_name: Optional[str] = None
    application_count: Optional[int] = 0
    model_config = ConfigDict(from_attributes=True)


class ResumeArtifactResponse(BaseModel):
    artifact_id: str
    candidate_id: str
    file_name: str
    file_sha256: str
    text_summary: str
    domain_specialization: str
    model_config = ConfigDict(from_attributes=True)


class CandidateBase(BaseModel):
    candidate_id: str
    full_name: str
    email: str
    phone: str
    years_of_experience: float
    highest_education: str
    current_location: str

class CandidateResponse(CandidateBase):
    skills: Optional[List[CandidateSkillResponse]] = []
    resume_artifact: Optional[ResumeArtifactResponse] = None
    model_config = ConfigDict(from_attributes=True)


class InterviewerBase(BaseModel):
    interviewer_id: str
    name: str
    department_id: str
    title: str
    email: str
    is_active: bool
    available_days: str

class InterviewerResponse(InterviewerBase):
    department_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class FeedbackBase(BaseModel):
    feedback_id: str
    interview_id: str
    interviewer_id: str
    technical_rating: int
    communication_rating: int
    problem_solving_rating: int
    overall_recommendation: str
    notes: str
    submitted_at: str

class FeedbackResponse(FeedbackBase):
    interviewer_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class InterviewBase(BaseModel):
    interview_id: str
    application_id: str
    interviewer_id: str
    scheduled_at: str
    scheduled_day: str
    stage: str
    status: str
    duration_minutes: int

class InterviewResponse(InterviewBase):
    interviewer_name: Optional[str] = None
    feedback: Optional[FeedbackResponse] = None
    model_config = ConfigDict(from_attributes=True)


class OfferBase(BaseModel):
    offer_id: str
    application_id: str
    offered_salary: float
    approval_status: str
    approved_by: Optional[str] = None
    candidate_decision: str
    offer_date: str
    expiration_date: str

class OfferResponse(OfferBase):
    candidate_name: Optional[str] = None
    requisition_title: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ApplicationBase(BaseModel):
    application_id: str
    requisition_id: str
    candidate_id: str
    applied_date: str
    status: str
    screening_score: float
    screening_passed: bool
    rejection_reason: Optional[str] = None

class ApplicationResponse(ApplicationBase):
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    requisition_title: Optional[str] = None
    department_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ApplicationDetailResponse(ApplicationResponse):
    candidate_details: Optional[CandidateResponse] = None
    requisition_details: Optional[JobRequisitionResponse] = None
    interviews: Optional[List[InterviewResponse]] = []
    offer: Optional[OfferResponse] = None


# ==================== Ground Truth & Anomaly Schemas ====================

class AnomalyItem(BaseModel):
    anomaly_id: str
    issue_type: str
    target_entity: str
    target_id: str
    details: str
    severity: str
    expected_resolution: str


# ==================== Dashboard & Validation Schemas ====================

class DashboardStats(BaseModel):
    total_departments: int
    total_requisitions: int
    total_candidates: int
    total_applications: int
    total_interviews: int
    total_offers: int
    total_anomalies_flagged: int
    applications_by_status: Dict[str, int]
    offers_by_decision: Dict[str, int]
    screening_pass_rate: float


class ValidationFinding(BaseModel):
    check_name: str
    entity: str
    record_id: Optional[str] = None
    severity: str  # PASS, FAIL, WARNING
    message: str


class ValidationReportResponse(BaseModel):
    status: str  # PASS, FAIL, WARNING
    total_checks: int
    passed_checks: int
    failed_checks: int
    warning_checks: int
    findings: List[ValidationFinding]
    timestamp: str


class GenerateDataRequest(BaseModel):
    seed: int = 20261022
    num_requisitions: int = 100
    num_candidates: int = 2000
    num_applications: int = 3000
    num_interviews: int = 600
    num_offers: int = 150


class GenerateDataResponse(BaseModel):
    message: str
    seed: int
    row_counts: Dict[str, int]
    anomalies_injected: int
    timestamp: str


class ReproducibilityResponse(BaseModel):
    reproducible: bool
    seed: int
    run_1_checksums: Dict[str, str]
    run_2_checksums: Dict[str, str]
    comparison_details: List[Dict[str, Any]]
    message: str
