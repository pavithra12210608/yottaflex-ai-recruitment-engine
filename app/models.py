"""SQLAlchemy models for YottaFlex AI Recruitment Engine."""
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    ForeignKey,
    DateTime,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.database import Base


class Department(Base):
    """Department master data entity."""
    __tablename__ = "departments"

    department_id = Column(String(32), primary_key=True)
    name = Column(String(128), nullable=False, unique=True)
    code = Column(String(16), nullable=False, unique=True)
    cost_center = Column(String(32), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    requisitions = relationship("JobRequisition", back_populates="department")
    interviewers = relationship("Interviewer", back_populates="department")


class JobRequisition(Base):
    """Job requisition entity."""
    __tablename__ = "job_requisitions"

    requisition_id = Column(String(32), primary_key=True)  # REQ-2026-000001
    department_id = Column(String(32), ForeignKey("departments.department_id"), nullable=False)
    title = Column(String(128), nullable=False)
    role_level = Column(String(16), nullable=False)  # L4, L5, L6, Principal
    min_years_experience = Column(Integer, nullable=False)
    min_salary = Column(Float, nullable=False)
    max_salary = Column(Float, nullable=False)
    status = Column(String(32), nullable=False, default="OPEN")  # DRAFT, APPROVED, OPEN, CLOSED
    open_date = Column(String(32), nullable=False)
    close_date = Column(String(32), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    department = relationship("Department", back_populates="requisitions")
    screening_rules = relationship("ScreeningRule", back_populates="requisition", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="requisition")


class Candidate(Base):
    """Candidate entity."""
    __tablename__ = "candidates"

    candidate_id = Column(String(32), primary_key=True)  # CAND-000001
    full_name = Column(String(128), nullable=False)
    email = Column(String(128), nullable=False, unique=True)
    phone = Column(String(32), nullable=False)
    years_of_experience = Column(Float, nullable=False)
    highest_education = Column(String(64), nullable=False)
    current_location = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    resume_artifact = relationship("ResumeArtifact", uselist=False, back_populates="candidate", cascade="all, delete-orphan")
    skills = relationship("CandidateSkill", back_populates="candidate", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="candidate")


class ResumeArtifact(Base):
    """Resume metadata artifact entity."""
    __tablename__ = "resume_artifacts"

    artifact_id = Column(String(32), primary_key=True)  # ART-000001
    candidate_id = Column(String(32), ForeignKey("candidates.candidate_id"), nullable=False, unique=True)
    file_name = Column(String(128), nullable=False)
    file_sha256 = Column(String(64), nullable=False)
    text_summary = Column(Text, nullable=False)
    domain_specialization = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    candidate = relationship("Candidate", back_populates="resume_artifact")


class Skill(Base):
    """Skill master entity."""
    __tablename__ = "skills"

    skill_id = Column(String(32), primary_key=True)  # SKL-001
    name = Column(String(64), nullable=False, unique=True)
    category = Column(String(64), nullable=False)  # Programming, Framework, ML, Cloud, Database

    # Relationships
    candidate_skills = relationship("CandidateSkill", back_populates="skill")
    screening_rules = relationship("ScreeningRule", back_populates="skill")


class CandidateSkill(Base):
    """Bridge table between Candidate and Skill (Many-to-Many)."""
    __tablename__ = "candidate_skills"

    candidate_id = Column(String(32), ForeignKey("candidates.candidate_id"), primary_key=True)
    skill_id = Column(String(32), ForeignKey("skills.skill_id"), primary_key=True)
    proficiency_level = Column(String(32), nullable=False)  # Beginner, Intermediate, Advanced, Expert
    years_experience = Column(Float, nullable=False)

    # Relationships
    candidate = relationship("Candidate", back_populates="skills")
    skill = relationship("Skill", back_populates="candidate_skills")


class ScreeningRule(Base):
    """Screening rule for a requisition (mandatory/optional skills and criteria)."""
    __tablename__ = "screening_rules"

    rule_id = Column(String(32), primary_key=True)  # RULE-000001
    requisition_id = Column(String(32), ForeignKey("job_requisitions.requisition_id"), nullable=False)
    skill_id = Column(String(32), ForeignKey("skills.skill_id"), nullable=False)
    is_mandatory = Column(Boolean, default=False, nullable=False)
    min_proficiency = Column(String(32), nullable=False, default="Intermediate")
    weight = Column(Float, default=1.0, nullable=False)

    # Relationships
    requisition = relationship("JobRequisition", back_populates="screening_rules")
    skill = relationship("Skill", back_populates="screening_rules")


class Application(Base):
    """Application entity linking candidate to requisition."""
    __tablename__ = "applications"

    # In standard operations: APP-<requisition-id>-<candidate-id>
    # Note: To support intentional anomaly DUPLICATE_APPLICATION without SQLite primary key crash on duplicate,
    # the primary key is application_id, which can have an anomaly suffix or distinct ID.
    application_id = Column(String(96), primary_key=True)
    requisition_id = Column(String(32), ForeignKey("job_requisitions.requisition_id"), nullable=False)
    candidate_id = Column(String(32), ForeignKey("candidates.candidate_id"), nullable=False)
    applied_date = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False, default="APPLIED")  # APPLIED, SCREENING, INTERVIEWING, OFFERED, HIRED, REJECTED, WITHDRAWN
    screening_score = Column(Float, nullable=False, default=0.0)
    screening_passed = Column(Boolean, nullable=False, default=False)
    rejection_reason = Column(String(256), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    requisition = relationship("JobRequisition", back_populates="applications")
    candidate = relationship("Candidate", back_populates="applications")
    interviews = relationship("Interview", back_populates="application", cascade="all, delete-orphan")
    offer = relationship("Offer", uselist=False, back_populates="application", cascade="all, delete-orphan")


class Interviewer(Base):
    """Interviewer entity."""
    __tablename__ = "interviewers"

    interviewer_id = Column(String(32), primary_key=True)  # EMP-0001
    name = Column(String(128), nullable=False)
    department_id = Column(String(32), ForeignKey("departments.department_id"), nullable=False)
    title = Column(String(128), nullable=False)
    email = Column(String(128), nullable=False, unique=True)
    is_active = Column(Boolean, default=True, nullable=False)
    available_days = Column(String(128), nullable=False)  # JSON or comma-separated days: "Monday,Wednesday,Friday"

    # Relationships
    department = relationship("Department", back_populates="interviewers")
    interviews = relationship("Interview", back_populates="interviewer")
    feedbacks = relationship("Feedback", back_populates="interviewer")


class Interview(Base):
    """Interview scheduling entity."""
    __tablename__ = "interviews"

    interview_id = Column(String(32), primary_key=True)  # INT-2026-000001
    application_id = Column(String(96), ForeignKey("applications.application_id"), nullable=False)
    interviewer_id = Column(String(32), ForeignKey("interviewers.interviewer_id"), nullable=False)
    scheduled_at = Column(String(32), nullable=False)  # ISO datetime
    scheduled_day = Column(String(16), nullable=False)  # Monday, Tuesday, etc.
    stage = Column(String(32), nullable=False)  # TECHNICAL_SCREEN, SYSTEM_DESIGN, BEHAVIORAL, FINAL_ROUND
    status = Column(String(32), nullable=False, default="SCHEDULED")  # SCHEDULED, COMPLETED, CANCELLED
    duration_minutes = Column(Integer, nullable=False, default=60)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    application = relationship("Application", back_populates="interviews")
    interviewer = relationship("Interviewer", back_populates="interviews")
    feedback = relationship("Feedback", uselist=False, back_populates="interview", cascade="all, delete-orphan")


class Feedback(Base):
    """Interview feedback entity."""
    __tablename__ = "feedback"

    feedback_id = Column(String(96), primary_key=True)  # FB-<interview-id>-<interviewer-id>
    interview_id = Column(String(32), ForeignKey("interviews.interview_id"), nullable=False, unique=True)
    interviewer_id = Column(String(32), ForeignKey("interviewers.interviewer_id"), nullable=False)
    technical_rating = Column(Integer, nullable=False)  # 1 - 5
    communication_rating = Column(Integer, nullable=False)  # 1 - 5
    problem_solving_rating = Column(Integer, nullable=False)  # 1 - 5
    overall_recommendation = Column(String(32), nullable=False)  # STRONG_NO_HIRE, NO_HIRE, LEAN_HIRE, STRONG_HIRE
    notes = Column(Text, nullable=False)
    submitted_at = Column(String(32), nullable=False)

    # Relationships
    interview = relationship("Interview", back_populates="feedback")
    interviewer = relationship("Interviewer", back_populates="feedbacks")


class Offer(Base):
    """Job offer entity."""
    __tablename__ = "offers"

    offer_id = Column(String(32), primary_key=True)  # OFF-2026-000001
    application_id = Column(String(96), ForeignKey("applications.application_id"), nullable=False, unique=True)
    offered_salary = Column(Float, nullable=False)
    approval_status = Column(String(32), nullable=False, default="PENDING_APPROVAL")  # PENDING_APPROVAL, APPROVED, REJECTED
    approved_by = Column(String(128), nullable=True)
    candidate_decision = Column(String(32), nullable=False, default="PENDING")  # PENDING, ACCEPTED, DECLINED
    offer_date = Column(String(32), nullable=False)
    expiration_date = Column(String(32), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    application = relationship("Application", back_populates="offer")
