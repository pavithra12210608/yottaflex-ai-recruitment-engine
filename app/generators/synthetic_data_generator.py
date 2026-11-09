"""Deterministic Synthetic Data Generator for YottaFlex AI Recruitment Engine."""
import os
import json
import random
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import pandas as pd
from faker import Faker

from app.config import (
    DEFAULT_SEED,
    BASELINE_TARGETS,
    PROFICIENCY_LEVELS,
    EDUCATION_LEVELS,
    ROLE_LEVELS,
    ANOMALY_UNAVAILABLE_INTERVIEWER,
    ANOMALY_DUPLICATE_APPLICATION,
    ANOMALY_MISSING_FEEDBACK,
    ANOMALY_SALARY_OUTSIDE_BAND,
    ANOMALY_CLOSED_ROLE_ACTIVE_APP,
)
from app.services.screening_service import calculate_candidate_score


# Curated Master Data Templates
MASTER_DEPARTMENTS = [
    {"department_id": "DEP-001", "name": "AI & Research", "code": "AI", "cost_center": "CC-101"},
    {"department_id": "DEP-002", "name": "Enterprise Platform Engineering", "code": "ENG", "cost_center": "CC-102"},
    {"department_id": "DEP-003", "name": "Forward Deployed & Solutions", "code": "FDE", "cost_center": "CC-103"},
    {"department_id": "DEP-004", "name": "Data Systems & Infrastructure", "code": "DATA", "cost_center": "CC-104"},
    {"department_id": "DEP-005", "name": "Product & User Experience", "code": "PROD", "cost_center": "CC-105"},
    {"department_id": "DEP-006", "name": "Cloud Security & Governance", "code": "SEC", "cost_center": "CC-106"},
]

MASTER_SKILLS = [
    {"skill_id": "SKL-001", "name": "Python", "category": "Programming"},
    {"skill_id": "SKL-002", "name": "FastAPI", "category": "Framework"},
    {"skill_id": "SKL-003", "name": "PyTorch", "category": "Machine Learning"},
    {"skill_id": "SKL-004", "name": "Docker & Kubernetes", "category": "DevOps & Cloud"},
    {"skill_id": "SKL-005", "name": "Distributed Systems", "category": "Architecture"},
    {"skill_id": "SKL-006", "name": "SQL & Relational Databases", "category": "Database"},
    {"skill_id": "SKL-007", "name": "Vector Databases & Embeddings", "category": "Machine Learning"},
    {"skill_id": "SKL-008", "name": "Agentic AI & LLM Orchestration", "category": "Machine Learning"},
    {"skill_id": "SKL-009", "name": "TypeScript & React", "category": "Frontend"},
    {"skill_id": "SKL-010", "name": "System Architecture", "category": "Architecture"},
    {"skill_id": "SKL-011", "name": "Golang", "category": "Programming"},
    {"skill_id": "SKL-012", "name": "CI/CD & Infrastructure as Code", "category": "DevOps & Cloud"},
    {"skill_id": "SKL-013", "name": "GraphQL & REST APIs", "category": "Framework"},
    {"skill_id": "SKL-014", "name": "Data Pipelines & Spark", "category": "Data Engineering"},
    {"skill_id": "SKL-015", "name": "Information Security & IAM", "category": "Security"},
]

ROLE_TEMPLATES = [
    {"title": "AI Forward Deployed Engineer", "dept_idx": 2, "exp": 4, "min_sal": 150000, "max_sal": 220000, "primary_skills": ["SKL-001", "SKL-002", "SKL-008", "SKL-004"]},
    {"title": "Senior AI Systems Engineer", "dept_idx": 0, "exp": 6, "min_sal": 175000, "max_sal": 250000, "primary_skills": ["SKL-001", "SKL-003", "SKL-005", "SKL-008"]},
    {"title": "Enterprise Platform Architect", "dept_idx": 1, "exp": 8, "min_sal": 190000, "max_sal": 270000, "primary_skills": ["SKL-005", "SKL-010", "SKL-004", "SKL-006"]},
    {"title": "Backend Infrastructure Engineer", "dept_idx": 1, "exp": 3, "min_sal": 130000, "max_sal": 185000, "primary_skills": ["SKL-001", "SKL-002", "SKL-006", "SKL-004"]},
    {"title": "Principal Data Platform Engineer", "dept_idx": 3, "exp": 8, "min_sal": 195000, "max_sal": 280000, "primary_skills": ["SKL-006", "SKL-014", "SKL-005", "SKL-001"]},
    {"title": "MLOps Solutions Architect", "dept_idx": 2, "exp": 5, "min_sal": 160000, "max_sal": 230000, "primary_skills": ["SKL-004", "SKL-012", "SKL-003", "SKL-001"]},
    {"title": "Cloud Security Engineer", "dept_idx": 5, "exp": 4, "min_sal": 145000, "max_sal": 210000, "primary_skills": ["SKL-015", "SKL-004", "SKL-001", "SKL-010"]},
    {"title": "Full Stack AI Product Engineer", "dept_idx": 4, "exp": 3, "min_sal": 135000, "max_sal": 190000, "primary_skills": ["SKL-009", "SKL-001", "SKL-002", "SKL-013"]},
]

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


class SyntheticDataGenerator:
    """Deterministic, rule-based recruitment data generator."""

    def __init__(self, seed: int = DEFAULT_SEED):
        self.seed = seed
        self.rng = random.Random(seed)
        self.fake = Faker()
        self.fake.seed_instance(seed)

    def generate(
        self,
        num_requisitions: int = 100,
        num_candidates: int = 2000,
        num_applications: int = 3000,
        num_interviews: int = 600,
        num_offers: int = 150,
    ) -> Tuple[Dict[str, List[Dict[str, Any]]], List[Dict[str, Any]]]:
        """Generates all entities and ground truth anomalies."""
        # Reset RNG seeds to guarantee strict reproducibility
        self.rng = random.Random(self.seed)
        self.fake.seed_instance(self.seed)

        # 1. Master Data: Departments & Skills
        departments = list(MASTER_DEPARTMENTS)
        skills = list(MASTER_SKILLS)
        skill_id_map = {s["skill_id"]: s for s in skills}

        # 2. Interviewers (Master pool)
        interviewers = []
        num_interviewers = max(20, num_requisitions // 2)
        for i in range(1, num_interviewers + 1):
            emp_id = f"EMP-{i:04d}"
            dept = self.rng.choice(departments)
            first = self.fake.first_name()
            last = self.fake.last_name()
            name = f"{first} {last}"
            email = f"{first.lower()}.{last.lower()}.{i}@recruitment.internal"
            # Interviewer available days (2 to 4 days a week)
            k_days = self.rng.randint(2, 4)
            avail = sorted(self.rng.sample(DAYS_OF_WEEK, k=k_days))
            interviewers.append({
                "interviewer_id": emp_id,
                "name": name,
                "department_id": dept["department_id"],
                "title": f"Senior Staff {dept['code']} Engineer",
                "email": email,
                "is_active": True,
                "available_days": ",".join(avail),
            })
        interviewer_map = {emp["interviewer_id"]: emp for emp in interviewers}

        # 3. Job Requisitions & Screening Rules
        base_date = datetime(2026, 1, 15)
        requisitions = []
        screening_rules = []
        rule_seq = 1

        for i in range(1, num_requisitions + 1):
            req_id = f"REQ-2026-{i:06d}"
            role_tmpl = ROLE_TEMPLATES[(i - 1) % len(ROLE_TEMPLATES)]
            dept = departments[role_tmpl["dept_idx"]]
            role_level = self.rng.choice(ROLE_LEVELS)

            # Salary adjustment based on role level
            multiplier = {"L4": 1.0, "L5": 1.25, "L6": 1.5, "Principal": 1.8}[role_level]
            min_sal = round(role_tmpl["min_sal"] * multiplier, -3)
            max_sal = round(role_tmpl["max_sal"] * multiplier, -3)
            min_exp = max(2, int(role_tmpl["exp"] * (multiplier * 0.9)))

            open_dt = base_date + timedelta(days=(i * 2) % 120)
            status = "OPEN"
            close_dt_str = None

            # Some requisitions are CLOSED or DRAFT
            if i % 15 == 0:
                status = "CLOSED"
                close_dt = open_dt + timedelta(days=45)
                close_dt_str = close_dt.strftime("%Y-%m-%d")
            elif i % 25 == 0:
                status = "DRAFT"

            requisitions.append({
                "requisition_id": req_id,
                "department_id": dept["department_id"],
                "title": f"{role_tmpl['title']} ({role_level})",
                "role_level": role_level,
                "min_years_experience": min_exp,
                "min_salary": float(min_sal),
                "max_salary": float(max_sal),
                "status": status,
                "open_date": open_dt.strftime("%Y-%m-%d"),
                "close_date": close_dt_str,
            })

            # Screening Rules for this Requisition
            # Add primary skills as mandatory / weighted
            for skill_id in role_tmpl["primary_skills"]:
                is_mand = (skill_id == role_tmpl["primary_skills"][0])
                rule_id = f"RULE-{rule_seq:06d}"
                rule_seq += 1
                screening_rules.append({
                    "rule_id": rule_id,
                    "requisition_id": req_id,
                    "skill_id": skill_id,
                    "is_mandatory": is_mand,
                    "min_proficiency": "Intermediate" if not is_mand else "Advanced",
                    "weight": 2.0 if is_mand else 1.0,
                })

        req_map = {r["requisition_id"]: r for r in requisitions}
        rules_by_req = {}
        for rule in screening_rules:
            rules_by_req.setdefault(rule["requisition_id"], []).append(rule)

        # 4. Candidates, Resume Artifacts, Candidate Skills
        candidates = []
        resume_artifacts = []
        candidate_skills = []
        cand_skills_map = {}

        domains = [
            "AI Systems & Large Language Models",
            "Distributed Backend & Cloud Platforms",
            "Full Stack & API Architecture",
            "Data Engineering & Distributed Pipelines",
            "Cybersecurity & Cloud Governance",
        ]

        for c in range(1, num_candidates + 1):
            cand_id = f"CAND-{c:06d}"
            first = self.fake.first_name()
            last = self.fake.last_name()
            name = f"{first} {last}"
            email = f"candidate.{first.lower()}.{last.lower()}.{c}@sandbox-eval.net"
            phone = f"+1-555-{self.rng.randint(100, 999):03d}-{self.rng.randint(1000, 9999):04d}"
            exp_years = round(self.rng.triangular(1.0, 15.0, 4.5), 1)
            education = self.rng.choices(EDUCATION_LEVELS, weights=[50, 35, 10, 5])[0]
            location = f"{self.fake.city()}, {self.fake.country_code()}"

            candidates.append({
                "candidate_id": cand_id,
                "full_name": name,
                "email": email,
                "phone": phone,
                "years_of_experience": exp_years,
                "highest_education": education,
                "current_location": location,
            })

            # Resume Artifact
            domain = self.rng.choice(domains)
            summary = (
                f"Experienced {education} graduate with {exp_years} years working in {domain}. "
                f"Specializes in robust software design, performance optimization, and scalable delivery."
            )
            raw_hash_seed = f"{cand_id}:{name}:{exp_years}"
            art_sha = hashlib.sha256(raw_hash_seed.encode("utf-8")).hexdigest()
            art_id = f"ART-{c:06d}"
            resume_artifacts.append({
                "artifact_id": art_id,
                "candidate_id": cand_id,
                "file_name": f"resume_{cand_id.lower()}.pdf",
                "file_sha256": art_sha,
                "text_summary": summary,
                "domain_specialization": domain,
            })

            # Candidate Skills (Each candidate has 3 to 7 skills)
            k_skills = self.rng.randint(3, 7)
            cand_chosen_skills = self.rng.sample(skills, k=k_skills)
            cand_skills_map[cand_id] = {}

            for sk in cand_chosen_skills:
                prof = self.rng.choices(PROFICIENCY_LEVELS, weights=[20, 45, 25, 10])[0]
                sk_exp = round(min(exp_years, self.rng.uniform(1.0, max(1.0, exp_years))), 1)
                candidate_skills.append({
                    "candidate_id": cand_id,
                    "skill_id": sk["skill_id"],
                    "proficiency_level": prof,
                    "years_experience": sk_exp,
                })
                cand_skills_map[cand_id][sk["skill_id"]] = {
                    "proficiency_level": prof,
                    "years_experience": sk_exp,
                }

        cand_map = {c["candidate_id"]: c for c in candidates}
        art_map = {a["candidate_id"]: a for a in resume_artifacts}

        # 5. Applications & Screening Outcomes
        applications = []
        app_candidates_pool = candidates[:]
        self.rng.shuffle(app_candidates_pool)

        # Distribute applications across requisitions
        open_requisitions = [r for r in requisitions if r["status"] == "OPEN"]
        all_req_ids = [r["requisition_id"] for r in requisitions]

        app_id_counter = 1
        ground_truth = []
        anomaly_counter = 1

        # We will reserve space for our 5 intentional anomalies:
        # Anomaly 2: Duplicate Application (Target Candidate + Requisition)
        target_dup_cand = candidates[0]
        target_dup_req = open_requisitions[0]

        # Ensure at least one requisition is strictly CLOSED for Anomaly 5
        target_closed_req = next((r for r in requisitions if r["status"] == "CLOSED"), None)
        if not target_closed_req:
            target_closed_req = requisitions[-1]
            target_closed_req["status"] = "CLOSED"
            target_closed_req["close_date"] = "2026-03-01"

        # Track existing candidate-requisition pairs to keep regular applications unique
        seen_pairs = set()

        for _ in range(num_applications - 2):
            cand = self.rng.choice(candidates)
            req = self.rng.choice(open_requisitions if self.rng.random() > 0.05 else requisitions)
            pair = (req["requisition_id"], cand["candidate_id"])
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)

            app_id = f"APP-{req['requisition_id']}-{cand['candidate_id']}"
            req_open_dt = datetime.strptime(req["open_date"], "%Y-%m-%d")
            app_dt = req_open_dt + timedelta(days=self.rng.randint(1, 30))

            # Deterministic Screening
            req_rules = rules_by_req.get(req["requisition_id"], [])
            c_skills = cand_skills_map.get(cand["candidate_id"], {})
            cand_art = art_map.get(cand["candidate_id"], {})

            score, passed, reason, _ = calculate_candidate_score(
                candidate_experience=cand["years_of_experience"],
                candidate_education=cand["highest_education"],
                candidate_domain=cand_art.get("domain_specialization", ""),
                candidate_skills=c_skills,
                req_min_experience=req["min_years_experience"],
                req_title=req["title"],
                screening_rules=req_rules,
            )

            # Assign Status
            if not passed:
                status = "REJECTED"
            else:
                # Distribution among passing applications
                r_val = self.rng.random()
                if r_val < 0.10:
                    status = "WITHDRAWN"
                    reason = "Candidate withdrew prior to interview scheduling"
                elif r_val < 0.35:
                    status = "SCREENING"
                else:
                    status = "INTERVIEWING"  # Eligible for interview/offers

            applications.append({
                "application_id": app_id,
                "requisition_id": req["requisition_id"],
                "candidate_id": cand["candidate_id"],
                "applied_date": app_dt.strftime("%Y-%m-%d"),
                "status": status,
                "screening_score": score,
                "screening_passed": passed,
                "rejection_reason": reason,
            })

        # Inject Anomaly 2: Duplicate Application
        dup_app_1_id = f"APP-{target_dup_req['requisition_id']}-{target_dup_cand['candidate_id']}"
        # We ensure first application is present
        applications.append({
            "application_id": dup_app_1_id,
            "requisition_id": target_dup_req["requisition_id"],
            "candidate_id": target_dup_cand["candidate_id"],
            "applied_date": "2026-02-01",
            "status": "APPLIED",
            "screening_score": 82.5,
            "screening_passed": True,
            "rejection_reason": None,
        })
        # The exact duplicate application (with -DUP suffix in ID to preserve SQLite table integrity while violating business uniqueness rule)
        dup_app_2_id = f"APP-{target_dup_req['requisition_id']}-{target_dup_cand['candidate_id']}-DUP"
        applications.append({
            "application_id": dup_app_2_id,
            "requisition_id": target_dup_req["requisition_id"],
            "candidate_id": target_dup_cand["candidate_id"],
            "applied_date": "2026-02-05",
            "status": "APPLIED",
            "screening_score": 82.5,
            "screening_passed": True,
            "rejection_reason": None,
        })
        ground_truth.append({
            "anomaly_id": f"ANOM-{anomaly_counter:04d}",
            "issue_type": ANOMALY_DUPLICATE_APPLICATION,
            "target_entity": "applications",
            "target_id": dup_app_2_id,
            "details": f"Candidate {target_dup_cand['candidate_id']} applied duplicate times to requisition {target_dup_req['requisition_id']}.",
            "severity": "ERROR",
            "expected_resolution": "De-duplicate duplicate submission and retain original application.",
        })
        anomaly_counter += 1

        # Inject Anomaly 5: Closed Role Active Application
        closed_app_id = f"APP-{target_closed_req['requisition_id']}-CLOSED-ACTIVE"
        cand_for_closed = candidates[10]
        applications.append({
            "application_id": closed_app_id,
            "requisition_id": target_closed_req["requisition_id"],
            "candidate_id": cand_for_closed["candidate_id"],
            "applied_date": target_closed_req["open_date"],
            "status": "INTERVIEWING",  # In active interview status despite role being closed
            "screening_score": 88.0,
            "screening_passed": True,
            "rejection_reason": None,
        })
        ground_truth.append({
            "anomaly_id": f"ANOM-{anomaly_counter:04d}",
            "issue_type": ANOMALY_CLOSED_ROLE_ACTIVE_APP,
            "target_entity": "applications",
            "target_id": closed_app_id,
            "details": f"Requisition {target_closed_req['requisition_id']} is CLOSED, but application {closed_app_id} is still in active status 'INTERVIEWING'.",
            "severity": "ERROR",
            "expected_resolution": "Close active pipeline or transition application to REJECTED/CLOSED.",
        })
        anomaly_counter += 1

        app_map = {a["application_id"]: a for a in applications}

        # 6. Interviews & Feedback
        # Select candidates in INTERVIEWING status (excluding intentional anomalies)
        interview_eligible_apps = [
            a for a in applications 
            if a["status"] == "INTERVIEWING" 
            and not a["application_id"].endswith("-DUP") 
            and "-CLOSED-ACTIVE" not in a["application_id"]
        ]
        if not interview_eligible_apps:
            interview_eligible_apps = [a for a in applications if a["screening_passed"]]

        interviews = []
        feedbacks = []
        interview_stages = ["TECHNICAL_SCREEN", "SYSTEM_DESIGN", "BEHAVIORAL", "FINAL_ROUND"]

        target_missing_fb_app = None
        target_unavail_interview_id = None

        for idx in range(1, num_interviews + 1):
            int_id = f"INT-2026-{idx:06d}"
            app = interview_eligible_apps[(idx - 1) % len(interview_eligible_apps)]
            interviewer = interviewers[(idx - 1) % len(interviewers)]

            stage = interview_stages[(idx - 1) % len(interview_stages)]
            avail_days = interviewer["available_days"].split(",")

            # Pick a valid scheduled day matching interviewer availability by default
            scheduled_day = self.rng.choice(avail_days)
            int_date = datetime(2026, 3, 1) + timedelta(days=idx)
            int_scheduled_at = f"{int_date.strftime('%Y-%m-%d')}T14:00:00"

            # Check if this is chosen for Anomaly 1: Interview Scheduled for Unavailable Interviewer
            if idx == 1:
                # Find a day the interviewer is NOT available
                unavail_days = [d for d in DAYS_OF_WEEK if d not in avail_days]
                if not unavail_days:
                    unavail_days = ["Sunday"]
                scheduled_day = unavail_days[0]
                target_unavail_interview_id = int_id
                ground_truth.append({
                    "anomaly_id": f"ANOM-{anomaly_counter:04d}",
                    "issue_type": ANOMALY_UNAVAILABLE_INTERVIEWER,
                    "target_entity": "interviews",
                    "target_id": int_id,
                    "details": f"Interview {int_id} scheduled on {scheduled_day}, but interviewer {interviewer['interviewer_id']} is only available on: {interviewer['available_days']}.",
                    "severity": "ERROR",
                    "expected_resolution": f"Reschedule interview to one of interviewer's available days ({interviewer['available_days']}).",
                })
                anomaly_counter += 1

            interviews.append({
                "interview_id": int_id,
                "application_id": app["application_id"],
                "interviewer_id": interviewer["interviewer_id"],
                "scheduled_at": int_scheduled_at,
                "scheduled_day": scheduled_day,
                "stage": stage,
                "status": "COMPLETED",
                "duration_minutes": 60,
            })

            # Check if this is chosen for Anomaly 3: Missing Feedback with Stage Advanced
            if idx == 2:
                # Omit feedback for this interview, but mark application as OFFERED
                target_missing_fb_app = app
                app["status"] = "OFFERED"
                ground_truth.append({
                    "anomaly_id": f"ANOM-{anomaly_counter:04d}",
                    "issue_type": ANOMALY_MISSING_FEEDBACK,
                    "target_entity": "feedback",
                    "target_id": f"FB-{int_id}-{interviewer['interviewer_id']}",
                    "details": f"Application {app['application_id']} advanced to 'OFFERED' but interview {int_id} has no submitted feedback.",
                    "severity": "ERROR",
                    "expected_resolution": "Block stage progression until mandatory interview feedback is recorded.",
                })
                anomaly_counter += 1
                continue

            # Standard Feedback Generation
            tech_r = self.rng.choices([2, 3, 4, 5], weights=[10, 25, 45, 20])[0]
            comm_r = self.rng.choices([3, 4, 5], weights=[20, 50, 30])[0]
            prob_r = self.rng.choices([2, 3, 4, 5], weights=[10, 30, 40, 20])[0]

            avg_rating = (tech_r + comm_r + prob_r) / 3.0
            if avg_rating >= 4.2:
                rec = "STRONG_HIRE"
            elif avg_rating >= 3.4:
                rec = "LEAN_HIRE"
            elif avg_rating >= 2.5:
                rec = "NO_HIRE"
            else:
                rec = "STRONG_NO_HIRE"

            notes = f"Demonstrated solid proficiency in {stage.lower().replace('_', ' ')}. Technical clarity: {tech_r}/5."
            fb_id = f"FB-{int_id}-{interviewer['interviewer_id']}"
            feedbacks.append({
                "feedback_id": fb_id,
                "interview_id": int_id,
                "interviewer_id": interviewer["interviewer_id"],
                "technical_rating": tech_r,
                "communication_rating": comm_r,
                "problem_solving_rating": prob_r,
                "overall_recommendation": rec,
                "notes": notes,
                "submitted_at": f"{int_date.strftime('%Y-%m-%d')}T16:30:00",
            })

        # 7. Offers
        # Select candidates whose interviews received positive recommendations
        positive_interview_app_ids = set()
        for fb in feedbacks:
            if fb["overall_recommendation"] in ["STRONG_HIRE", "LEAN_HIRE"]:
                int_rec = next((i for i in interviews if i["interview_id"] == fb["interview_id"]), None)
                if int_rec:
                    positive_interview_app_ids.add(int_rec["application_id"])

        positive_apps = [app_map[aid] for aid in positive_interview_app_ids if aid in app_map]
        if target_missing_fb_app and target_missing_fb_app not in positive_apps:
            positive_apps.append(target_missing_fb_app)

        # Fallback to any passed application if pool is smaller than required num_offers
        if len(positive_apps) < num_offers:
            extra_passed = [
                a for a in applications 
                if a["screening_passed"] 
                and a not in positive_apps
                and "-CLOSED-ACTIVE" not in a["application_id"]
                and not a["application_id"].endswith("-DUP")
            ]
            positive_apps.extend(extra_passed[:(num_offers - len(positive_apps))])

        offers = []
        for o_idx in range(1, min(num_offers + 1, len(positive_apps) + 1)):
            off_id = f"OFF-2026-{o_idx:06d}"
            app = positive_apps[o_idx - 1]
            req = req_map[app["requisition_id"]]

            # Calculate offered salary within approved band
            band_min = req["min_salary"]
            band_max = req["max_salary"]
            offered_salary = round(self.rng.uniform(band_min, band_max), -2)

            # Check if this is chosen for Anomaly 4: Salary Outside Approved Band
            if o_idx == 1:
                # Set salary 50% above maximum approved band
                offered_salary = round(band_max * 1.50, -2)
                ground_truth.append({
                    "anomaly_id": f"ANOM-{anomaly_counter:04d}",
                    "issue_type": ANOMALY_SALARY_OUTSIDE_BAND,
                    "target_entity": "offers",
                    "target_id": off_id,
                    "details": f"Offer {off_id} salary (${offered_salary:,.2f}) exceeds approved requisition {req['requisition_id']} range [${band_min:,.2f} - ${band_max:,.2f}].",
                    "severity": "ERROR",
                    "expected_resolution": "Adjust offer compensation within approved salary band or request formal executive compensation committee approval.",
                })
                anomaly_counter += 1

            app["status"] = "OFFERED"
            # Decision
            dec = self.rng.choices(["ACCEPTED", "DECLINED", "PENDING"], weights=[60, 25, 15])[0]
            if app == target_missing_fb_app:
                dec = "ACCEPTED"  # Guarantee active progression for Anomaly 3

            if dec == "ACCEPTED":
                app["status"] = "HIRED"
            elif dec == "DECLINED":
                app["status"] = "REJECTED"
                app["rejection_reason"] = "Candidate declined final offer"

            off_dt = datetime(2026, 4, 1) + timedelta(days=o_idx)
            exp_dt = off_dt + timedelta(days=14)

            offers.append({
                "offer_id": off_id,
                "application_id": app["application_id"],
                "offered_salary": float(offered_salary),
                "approval_status": "APPROVED",
                "approved_by": "VP of Engineering & Head of People",
                "candidate_decision": dec,
                "offer_date": off_dt.strftime("%Y-%m-%d"),
                "expiration_date": exp_dt.strftime("%Y-%m-%d"),
            })

        entities = {
            "departments": departments,
            "job_requisitions": requisitions,
            "candidates": candidates,
            "resume_artifacts": resume_artifacts,
            "skills": skills,
            "candidate_skills": candidate_skills,
            "screening_rules": screening_rules,
            "applications": applications,
            "interviewers": interviewers,
            "interviews": interviews,
            "feedback": feedbacks,
            "offers": offers,
        }

        return entities, ground_truth

    def export_to_csv(self, entities: Dict[str, List[Dict[str, Any]]], ground_truth: List[Dict[str, Any]], output_dir: str):
        """Exports entities and ground truth to CSV and JSON files."""
        os.makedirs(output_dir, exist_ok=True)

        mapping = {
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

        for entity_key, filename in mapping.items():
            records = entities.get(entity_key, [])
            df = pd.DataFrame(records)
            filepath = os.path.join(output_dir, filename)
            df.to_csv(filepath, index=False)

        # Ground Truth Exports (Strictly Separate)
        gt_df = pd.DataFrame(ground_truth)
        gt_df.to_csv(os.path.join(output_dir, "ground_truth.csv"), index=False)

        with open(os.path.join(output_dir, "ground_truth.json"), "w", encoding="utf-8") as f:
            json.dump(ground_truth, f, indent=2)
