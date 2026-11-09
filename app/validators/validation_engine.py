"""Comprehensive Validation Engine for YottaFlex AI Recruitment Engine."""
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import math
import pandas as pd

from app.config import (
    REQUISITION_STATUSES,
    APPLICATION_STATUSES,
    INTERVIEW_STAGES,
    INTERVIEW_STATUSES,
    OFFER_APPROVAL_STATUSES,
    CANDIDATE_DECISIONS,
    PROFICIENCY_LEVELS,
    EDUCATION_LEVELS,
    ROLE_LEVELS,
    ANOMALY_UNAVAILABLE_INTERVIEWER,
    ANOMALY_DUPLICATE_APPLICATION,
    ANOMALY_MISSING_FEEDBACK,
    ANOMALY_SALARY_OUTSIDE_BAND,
    ANOMALY_CLOSED_ROLE_ACTIVE_APP,
)


def _parse_date(val: Any) -> Optional[datetime]:
    """Safely normalizes date/datetime values from string, datetime, or date objects, ignoring null/NaN."""
    if val is None or pd.isna(val):
        return None
    if isinstance(val, float):
        if math.isnan(val):
            return None
        return None
    if isinstance(val, str):
        val_str = val.strip()
        if not val_str or val_str.lower() in ("nan", "none", "null", "nat"):
            return None
        val_str = val_str.replace("Z", "").split(".")[0]
        try:
            if "T" in val_str:
                return datetime.strptime(val_str, "%Y-%m-%dT%H:%M:%S")
            return datetime.strptime(val_str, "%Y-%m-%d")
        except ValueError:
            return None
    if isinstance(val, datetime):
        return val
    if hasattr(val, "year") and hasattr(val, "month") and hasattr(val, "day"):
        return datetime(val.year, val.month, val.day)
    return None


class ValidationEngine:
    """Validates recruitment data integrity, business rules, and detects anomalies."""

    def __init__(self, entities: Dict[str, List[Dict[str, Any]]]):
        self.entities = entities
        self.findings: List[Dict[str, Any]] = []
        self.passed_checks = 0
        self.failed_checks = 0
        self.warning_checks = 0

    def add_finding(self, check_name: str, entity: str, record_id: Optional[str], severity: str, message: str):
        self.findings.append({
            "check_name": check_name,
            "entity": entity,
            "record_id": record_id,
            "severity": severity,
            "message": message,
        })
        if severity == "PASS":
            self.passed_checks += 1
        elif severity == "FAIL":
            self.failed_checks += 1
        elif severity == "WARNING":
            self.warning_checks += 1

    def run_all_validations(self) -> Dict[str, Any]:
        """Executes full validation test suite and returns structured report."""
        self.findings = []
        self.passed_checks = 0
        self.failed_checks = 0
        self.warning_checks = 0

        self.validate_primary_keys()
        self.validate_foreign_keys()
        self.validate_enum_constraints()
        self.validate_date_orderings()
        self.validate_duplicate_applications()
        self.validate_interviewer_availability()
        self.validate_missing_feedback()
        self.validate_salary_bands()
        self.validate_closed_requisitions_active_apps()
        self.validate_screening_arithmetic()

        total = self.passed_checks + self.failed_checks + self.warning_checks
        overall_status = "FAIL" if self.failed_checks > 0 else ("WARNING" if self.warning_checks > 0 else "PASS")

        return {
            "status": overall_status,
            "total_checks": total,
            "passed_checks": self.passed_checks,
            "failed_checks": self.failed_checks,
            "warning_checks": self.warning_checks,
            "findings": self.findings,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def validate_primary_keys(self):
        """Validates primary key uniqueness across all entity collections."""
        pk_definitions = {
            "departments": "department_id",
            "job_requisitions": "requisition_id",
            "candidates": "candidate_id",
            "resume_artifacts": "artifact_id",
            "skills": "skill_id",
            "screening_rules": "rule_id",
            "applications": "application_id",
            "interviewers": "interviewer_id",
            "interviews": "interview_id",
            "feedback": "feedback_id",
            "offers": "offer_id",
        }

        for entity_name, pk_col in pk_definitions.items():
            records = self.entities.get(entity_name, [])
            keys = [r[pk_col] for r in records if pk_col in r]
            duplicates = len(keys) - len(set(keys))
            if duplicates == 0:
                self.add_finding("PK_UNIQUENESS", entity_name, None, "PASS", f"All {len(keys)} records have unique primary keys.")
            else:
                self.add_finding("PK_UNIQUENESS", entity_name, None, "FAIL", f"Found {duplicates} duplicate primary keys in {entity_name}.")

        # Candidate skills composite primary key
        cand_skills = self.entities.get("candidate_skills", [])
        pairs = [(cs["candidate_id"], cs["skill_id"]) for cs in cand_skills]
        dup_pairs = len(pairs) - len(set(pairs))
        if dup_pairs == 0:
            self.add_finding("PK_UNIQUENESS", "candidate_skills", None, "PASS", f"All {len(pairs)} candidate-skill pairs are unique.")
        else:
            self.add_finding("PK_UNIQUENESS", "candidate_skills", None, "FAIL", f"Found {dup_pairs} duplicate composite keys in candidate_skills.")

    def validate_foreign_keys(self):
        """Validates foreign key referential integrity."""
        fk_relationships = [
            ("job_requisitions", "department_id", "departments", "department_id"),
            ("resume_artifacts", "candidate_id", "candidates", "candidate_id"),
            ("candidate_skills", "candidate_id", "candidates", "candidate_id"),
            ("candidate_skills", "skill_id", "skills", "skill_id"),
            ("screening_rules", "requisition_id", "job_requisitions", "requisition_id"),
            ("screening_rules", "skill_id", "skills", "skill_id"),
            ("applications", "requisition_id", "job_requisitions", "requisition_id"),
            ("applications", "candidate_id", "candidates", "candidate_id"),
            ("interviewers", "department_id", "departments", "department_id"),
            ("interviews", "application_id", "applications", "application_id"),
            ("interviews", "interviewer_id", "interviewers", "interviewer_id"),
            ("feedback", "interview_id", "interviews", "interview_id"),
            ("feedback", "interviewer_id", "interviewers", "interviewer_id"),
            ("offers", "application_id", "applications", "application_id"),
        ]

        for child_entity, child_fk, parent_entity, parent_pk in fk_relationships:
            parent_ids = {r[parent_pk] for r in self.entities.get(parent_entity, [])}
            child_records = self.entities.get(child_entity, [])
            orphans = [r[child_fk] for r in child_records if r[child_fk] not in parent_ids]

            if not orphans:
                self.add_finding("FK_INTEGRITY", child_entity, None, "PASS", f"Foreign key {child_fk} -> {parent_entity}.{parent_pk} perfectly intact.")
            else:
                self.add_finding("FK_INTEGRITY", child_entity, None, "FAIL", f"Found {len(orphans)} orphaned records in {child_entity} referencing non-existent {parent_entity}.{parent_pk}.")

    def validate_enum_constraints(self):
        """Validates enum column values."""
        enum_checks = [
            ("job_requisitions", "status", REQUISITION_STATUSES),
            ("job_requisitions", "role_level", ROLE_LEVELS),
            ("candidates", "highest_education", EDUCATION_LEVELS),
            ("candidate_skills", "proficiency_level", PROFICIENCY_LEVELS),
            ("applications", "status", APPLICATION_STATUSES),
            ("interviews", "stage", INTERVIEW_STAGES),
            ("interviews", "status", INTERVIEW_STATUSES),
            ("offers", "approval_status", OFFER_APPROVAL_STATUSES),
            ("offers", "candidate_decision", CANDIDATE_DECISIONS),
        ]

        for entity_name, field, allowed in enum_checks:
            records = self.entities.get(entity_name, [])
            invalid = [r for r in records if r.get(field) not in allowed]
            if not invalid:
                self.add_finding("ENUM_VALIDATION", entity_name, None, "PASS", f"Field '{field}' adheres strictly to allowed domain values.")
            else:
                self.add_finding("ENUM_VALIDATION", entity_name, None, "FAIL", f"Found {len(invalid)} invalid enum values in {entity_name}.{field}.")

    def validate_date_orderings(self):
        """Validates temporal order of lifecycle milestones."""
        req_map = {r["requisition_id"]: r for r in self.entities.get("job_requisitions", [])}
        app_map = {a["application_id"]: a for a in self.entities.get("applications", [])}

        # 1. Requisition open_date <= close_date
        invalid_req_dates = []
        for req in self.entities.get("job_requisitions", []):
            open_dt = _parse_date(req.get("open_date"))
            close_dt = _parse_date(req.get("close_date"))
            if open_dt and close_dt:
                if open_dt > close_dt:
                    invalid_req_dates.append(req["requisition_id"])

        if not invalid_req_dates:
            self.add_finding("DATE_ORDERING", "job_requisitions", None, "PASS", "Requisition open dates precede close dates.")
        else:
            self.add_finding("DATE_ORDERING", "job_requisitions", None, "FAIL", f"Requisitions with invalid date order: {invalid_req_dates}")

        # 2. Offer expiration_date >= offer_date
        invalid_offers = []
        for off in self.entities.get("offers", []):
            off_dt = _parse_date(off.get("offer_date"))
            exp_dt = _parse_date(off.get("expiration_date"))
            if off_dt and exp_dt:
                if off_dt > exp_dt:
                    invalid_offers.append(off["offer_id"])

        if not invalid_offers:
            self.add_finding("DATE_ORDERING", "offers", None, "PASS", "Offer dates precede expiration dates.")
        else:
            self.add_finding("DATE_ORDERING", "offers", None, "FAIL", f"Offers with expiration earlier than offer date: {invalid_offers}")

    def validate_duplicate_applications(self):
        """Detects duplicate applications for the same candidate and requisition (Anomaly 2)."""
        apps = self.entities.get("applications", [])
        seen_cand_req = {}
        duplicates_found = []

        for a in apps:
            cand_id = a["candidate_id"]
            req_id = a["requisition_id"]
            key = (cand_id, req_id)

            if key in seen_cand_req:
                duplicates_found.append({
                    "application_id": a["application_id"],
                    "candidate_id": cand_id,
                    "requisition_id": req_id,
                    "previous_application_id": seen_cand_req[key],
                })
            else:
                seen_cand_req[key] = a["application_id"]

        if duplicates_found:
            for dup in duplicates_found:
                self.add_finding(
                    ANOMALY_DUPLICATE_APPLICATION,
                    "applications",
                    dup["application_id"],
                    "FAIL",
                    f"Candidate {dup['candidate_id']} has duplicate application {dup['application_id']} for requisition {dup['requisition_id']} (first: {dup['previous_application_id']}).",
                )
        else:
            self.add_finding("DUPLICATE_APPLICATIONS_CHECK", "applications", None, "PASS", "No duplicate candidate-requisition applications detected.")

    def validate_interviewer_availability(self):
        """Detects interviews scheduled when interviewer is unavailable (Anomaly 1)."""
        interviewers = {i["interviewer_id"]: i for i in self.entities.get("interviewers", [])}
        interviews = self.entities.get("interviews", [])
        availability_conflicts = []

        for intv in interviews:
            interviewer = interviewers.get(intv["interviewer_id"])
            if not interviewer:
                continue

            avail_days = [d.strip() for d in interviewer["available_days"].split(",")]
            sched_day = intv.get("scheduled_day")

            if sched_day and sched_day not in avail_days:
                availability_conflicts.append((intv["interview_id"], interviewer["interviewer_id"], sched_day, avail_days))

        if availability_conflicts:
            for int_id, emp_id, s_day, a_days in availability_conflicts:
                self.add_finding(
                    ANOMALY_UNAVAILABLE_INTERVIEWER,
                    "interviews",
                    int_id,
                    "FAIL",
                    f"Interview {int_id} scheduled on {s_day}, but interviewer {emp_id} is only available on: {', '.join(a_days)}.",
                )
        else:
            self.add_finding("INTERVIEW_AVAILABILITY_CHECK", "interviews", None, "PASS", "All scheduled interviews align with interviewer availability.")

    def validate_missing_feedback(self):
        """Detects applications advanced to OFFERED/HIRED without interview feedback (Anomaly 3)."""
        feedbacks = {fb["interview_id"]: fb for fb in self.entities.get("feedback", [])}
        interviews = self.entities.get("interviews", [])
        app_map = {a["application_id"]: a for a in self.entities.get("applications", [])}

        missing_feedback_cases = []

        for intv in interviews:
            app = app_map.get(intv["application_id"])
            if not app:
                continue

            # If application advanced to OFFERED or HIRED, every interview must have submitted feedback
            if app["status"] in ["OFFERED", "HIRED"]:
                if intv["interview_id"] not in feedbacks:
                    missing_feedback_cases.append((intv["interview_id"], app["application_id"], app["status"]))

        if missing_feedback_cases:
            for int_id, app_id, status in missing_feedback_cases:
                self.add_finding(
                    ANOMALY_MISSING_FEEDBACK,
                    "feedback",
                    f"FB-{int_id}",
                    "FAIL",
                    f"Application {app_id} advanced to stage '{status}' but interview {int_id} has no recorded feedback.",
                )
        else:
            self.add_finding("MISSING_FEEDBACK_CHECK", "feedback", None, "PASS", "All advanced applications have complete interview feedback recorded.")

    def validate_salary_bands(self):
        """Detects offers outside approved salary bands (Anomaly 4)."""
        app_map = {a["application_id"]: a for a in self.entities.get("applications", [])}
        req_map = {r["requisition_id"]: r for r in self.entities.get("job_requisitions", [])}
        offers = self.entities.get("offers", [])

        salary_violations = []

        for off in offers:
            app = app_map.get(off["application_id"])
            if not app:
                continue
            req = req_map.get(app["requisition_id"])
            if not req:
                continue

            offered = off["offered_salary"]
            min_sal = req["min_salary"]
            max_sal = req["max_salary"]

            if offered < min_sal or offered > max_sal:
                salary_violations.append((off["offer_id"], req["requisition_id"], offered, min_sal, max_sal))

        if salary_violations:
            for off_id, req_id, sal, min_s, max_s in salary_violations:
                self.add_finding(
                    ANOMALY_SALARY_OUTSIDE_BAND,
                    "offers",
                    off_id,
                    "FAIL",
                    f"Offer {off_id} salary (${sal:,.2f}) violates requisition {req_id} approved band [${min_s:,.2f} - ${max_s:,.2f}].",
                )
        else:
            self.add_finding("SALARY_BAND_CHECK", "offers", None, "PASS", "All offer salaries fall within approved requisition bands.")

    def validate_closed_requisitions_active_apps(self):
        """Detects active applications under closed job requisitions (Anomaly 5)."""
        req_map = {r["requisition_id"]: r for r in self.entities.get("job_requisitions", [])}
        apps = self.entities.get("applications", [])

        active_statuses = {"APPLIED", "SCREENING", "INTERVIEWING", "OFFERED"}
        active_under_closed = []

        for a in apps:
            req = req_map.get(a["requisition_id"])
            if req and req["status"] == "CLOSED":
                if a["status"] in active_statuses:
                    active_under_closed.append((a["application_id"], req["requisition_id"], a["status"]))

        if active_under_closed:
            for app_id, req_id, status in active_under_closed:
                self.add_finding(
                    ANOMALY_CLOSED_ROLE_ACTIVE_APP,
                    "applications",
                    app_id,
                    "FAIL",
                    f"Requisition {req_id} is CLOSED, but application {app_id} remains active in '{status}' status.",
                )
        else:
            self.add_finding("CLOSED_ROLE_CHECK", "applications", None, "PASS", "No active applications belong to closed job requisitions.")

    def validate_screening_arithmetic(self):
        """Validates that screening scores are bounded between 0.0 and 100.0."""
        apps = self.entities.get("applications", [])
        out_of_bounds = [a["application_id"] for a in apps if not (0.0 <= a.get("screening_score", 0.0) <= 100.0)]

        if not out_of_bounds:
            self.add_finding("ARITHMETIC_RECONCILIATION", "applications", None, "PASS", "All screening scores are strictly bounded within [0.0, 100.0].")
        else:
            self.add_finding("ARITHMETIC_RECONCILIATION", "applications", None, "FAIL", f"Found {len(out_of_bounds)} applications with scores out of bounds.")
