# Data Dictionary - YottaFlex AI Recruitment Engine

This document provides a comprehensive specification for all 12 relational entities, their fields, types, constraints, and validation rules within the YottaFlex AI Recruitment Engine.

---

## 1. Department (`departments`)
Master corporate business units managing requisitions and hiring staff.

| Field Name | Type | Req/Opt | Allowed Values | Unique | PK | FK | Validation Rule | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `department_id` | String(32) | Required | Format: `DEP-001` | Yes | Yes | No | Regex `^DEP-\d{3}$` | Unique identifier for the department |
| `name` | String(128) | Required | Dept names (e.g. "AI & Research") | Yes | No | No | Non-empty string | Official department name |
| `code` | String(16) | Required | E.g. "AI", "ENG", "FDE", "DATA" | Yes | No | No | Alpha uppercase | Short business code |
| `cost_center` | String(32) | Required | Format: `CC-101` | No | No | No | Format `CC-\d+` | Internal finance accounting center |
| `created_at` | DateTime | Required | ISO 8601 Timestamp | No | No | No | Valid past datetime | Record creation timestamp |

---

## 2. JobRequisition (`job_requisitions`)
Formal approved hiring mandates detailing role level, compensation band, and experience.

| Field Name | Type | Req/Opt | Allowed Values | Unique | PK | FK | Validation Rule | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `requisition_id` | String(32) | Required | Format: `REQ-2026-000001` | Yes | Yes | No | Regex `^REQ-2026-\d{6}$` | Unique requisition identifier |
| `department_id` | String(32) | Required | Existing department ID | No | No | Yes | References `departments.department_id` | Sponsoring department |
| `title` | String(128) | Required | E.g. "AI Forward Deployed Engineer (L5)" | No | No | No | Non-empty string | Official role title |
| `role_level` | String(16) | Required | `L4`, `L5`, `L6`, `Principal` | No | No | No | Must be in allowed enum set | Seniority grade level |
| `min_years_experience`| Integer | Required | 1 to 20 | No | No | No | `>= 1` | Minimum required experience |
| `min_salary` | Float | Required | Positive float | No | No | No | `min_salary < max_salary` | Approved salary band lower bound |
| `max_salary` | Float | Required | Positive float | No | No | No | `max_salary > min_salary` | Approved salary band upper bound |
| `status` | String(32) | Required | `DRAFT`, `APPROVED`, `OPEN`, `CLOSED` | No | No | No | Enum check | Operational state of the requisition |
| `open_date` | String(32) | Required | Format: `YYYY-MM-DD` | No | No | No | Valid date | Date requisition opened |
| `close_date` | String(32) | Optional | Format: `YYYY-MM-DD` or NULL | No | No | No | If present, `>= open_date` | Date requisition closed |
| `created_at` | DateTime | Required | ISO 8601 Timestamp | No | No | No | Valid past datetime | Record creation timestamp |

---

## 3. Candidate (`candidates`)
Synthetically generated applicant profiles. Excludes all protected/demographic classes.

| Field Name | Type | Req/Opt | Allowed Values | Unique | PK | FK | Validation Rule | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `candidate_id` | String(32) | Required | Format: `CAND-000001` | Yes | Yes | No | Regex `^CAND-\d{6}$` | Unique candidate identifier |
| `full_name` | String(128) | Required | Synthetic name string | No | No | No | Non-empty string | Synthetic full name |
| `email` | String(128) | Required | Synthetic email format | Yes | No | No | Standard email regex | Synthetic email address |
| `phone` | String(32) | Required | Synthetic phone string | No | No | No | Valid format | Synthetic phone number |
| `years_of_experience` | Float | Required | 0.0 to 30.0 | No | No | No | `>= 0.0` | Total verified professional experience |
| `highest_education` | String(64) | Required | `Bootcamp`, `BSc`, `MSc`, `PhD` | No | No | No | Allowed enum set | Educational qualification level |
| `current_location` | String(128) | Required | Synthetic city/country | No | No | No | Non-empty string | Synthetic residential location |
| `created_at` | DateTime | Required | ISO 8601 Timestamp | No | No | No | Valid past datetime | Record creation timestamp |

---

## 4. ResumeArtifact (`resume_artifacts`)
Simulated resume document metadata, domain specializations, and SHA-256 integrity digests.

| Field Name | Type | Req/Opt | Allowed Values | Unique | PK | FK | Validation Rule | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `artifact_id` | String(32) | Required | Format: `ART-000001` | Yes | Yes | No | Regex `^ART-\d{6}$` | Unique resume artifact ID |
| `candidate_id` | String(32) | Required | Existing candidate ID | Yes | No | Yes | References `candidates.candidate_id` | 1-to-1 link to candidate |
| `file_name` | String(128) | Required | E.g. `resume_cand_000001.pdf` | No | No | No | `.pdf` extension | File name |
| `file_sha256` | String(64) | Required | 64-char hexadecimal hash | No | No | No | Regex `^[a-f0-9]{64}$` | Cryptographic SHA-256 digest |
| `text_summary` | Text | Required | Synthetic professional summary | No | No | No | Min 20 characters | Extracted profile summary |
| `domain_specialization`| String(128) | Required | E.g. "AI Systems & LLMs" | No | No | No | Non-empty string | Core technical domain |
| `created_at` | DateTime | Required | ISO 8601 Timestamp | No | No | No | Valid past datetime | Record creation timestamp |

---

## 5. Skill (`skills`)
Master catalog of standardized technical skills.

| Field Name | Type | Req/Opt | Allowed Values | Unique | PK | FK | Validation Rule | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `skill_id` | String(32) | Required | Format: `SKL-001` | Yes | Yes | No | Regex `^SKL-\d{3}$` | Unique skill identifier |
| `name` | String(64) | Required | E.g. "Python", "FastAPI" | Yes | No | No | Non-empty string | Standardized skill name |
| `category` | String(64) | Required | Programming, Framework, ML, Cloud | No | No | No | Allowed category set | Functional taxonomy group |

---

## 6. CandidateSkill (`candidate_skills`)
Bridge table representing many-to-many relationships between Candidates and Skills.

| Field Name | Type | Req/Opt | Allowed Values | Unique | PK | FK | Validation Rule | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `candidate_id` | String(32) | Required | Existing candidate ID | Composite | Yes (1/2) | Yes | References `candidates.candidate_id` | Candidate reference |
| `skill_id` | String(32) | Required | Existing skill ID | Composite | Yes (2/2) | Yes | References `skills.skill_id` | Skill reference |
| `proficiency_level` | String(32) | Required | `Beginner`, `Intermediate`, `Advanced`, `Expert` | No | No | No | Allowed enum set | Evaluated competence level |
| `years_experience` | Float | Required | 0.5 to 25.0 | No | No | No | `<= candidate.years_of_experience` | Years using this specific skill |

---

## 7. ScreeningRule (`screening_rules`)
Requisition-specific technical screening criteria (mandatory vs. weighted skills).

| Field Name | Type | Req/Opt | Allowed Values | Unique | PK | FK | Validation Rule | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `rule_id` | String(32) | Required | Format: `RULE-000001` | Yes | Yes | No | Regex `^RULE-\d{6}$` | Unique rule identifier |
| `requisition_id` | String(32) | Required | Existing requisition ID | No | No | Yes | References `job_requisitions.requisition_id`| Associated requisition |
| `skill_id` | String(32) | Required | Existing skill ID | No | No | Yes | References `skills.skill_id` | Required skill |
| `is_mandatory` | Boolean | Required | `True`, `False` | No | No | No | Boolean | If true, disqualifies candidate if missing |
| `min_proficiency` | String(32) | Required | `Beginner`, `Intermediate`, `Advanced`, `Expert` | No | No | No | Allowed enum set | Minimum competence threshold |
| `weight` | Float | Required | 1.0 to 5.0 | No | No | No | `> 0.0` | Relative weight in score aggregation |

---

## 8. Application (`applications`)
Central workflow entity tracking candidate candidacy, screening score, and lifecycle status.

| Field Name | Type | Req/Opt | Allowed Values | Unique | PK | FK | Validation Rule | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `application_id` | String(96) | Required | Format: `APP-<req-id>-<cand-id>` | Yes | Yes | No | Non-empty unique string | Immutable application identifier |
| `requisition_id` | String(32) | Required | Existing requisition ID | No | No | Yes | References `job_requisitions.requisition_id`| Applied job opening |
| `candidate_id` | String(32) | Required | Existing candidate ID | No | No | Yes | References `candidates.candidate_id` | Applying candidate |
| `applied_date` | String(32) | Required | Format: `YYYY-MM-DD` | No | No | No | `>= requisition.open_date` | Submission date |
| `status` | String(32) | Required | `APPLIED`, `SCREENING`, `INTERVIEWING`, `OFFERED`, `HIRED`, `REJECTED`, `WITHDRAWN` | No | No | No | Allowed enum set | Current pipeline lifecycle stage |
| `screening_score` | Float | Required | 0.0 to 100.0 | No | No | No | Bounded `[0.0, 100.0]` | Deterministic composite screening score |
| `screening_passed` | Boolean | Required | `True`, `False` | No | No | No | `score >= 70.0 and not mandatory_failed` | Qualification determination |
| `rejection_reason` | String(256)| Optional | Reason string or NULL | No | No | No | Required if status is REJECTED | Audit reason for rejection |
| `updated_at` | DateTime | Required | ISO 8601 Timestamp | No | No | No | Valid datetime | Last stage transition timestamp |

---

## 9. Interviewer (`interviewers`)
Engineers and hiring managers authorized to conduct technical evaluations.

| Field Name | Type | Req/Opt | Allowed Values | Unique | PK | FK | Validation Rule | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `interviewer_id` | String(32) | Required | Format: `EMP-0001` | Yes | Yes | No | Regex `^EMP-\d{4}$` | Unique employee identifier |
| `name` | String(128) | Required | Full name | No | No | No | Non-empty string | Interviewer name |
| `department_id` | String(32) | Required | Existing department ID | No | No | Yes | References `departments.department_id` | Affiliated department |
| `title` | String(128) | Required | E.g. "Staff Engineer" | No | No | No | Non-empty string | Corporate title |
| `email` | String(128) | Required | Corporate email string | Yes | No | No | Valid email | Work email |
| `is_active` | Boolean | Required | `True`, `False` | No | No | No | Boolean | Availability flag |
| `available_days` | String(128) | Required | Comma-separated days (e.g. `Monday,Wednesday`) | No | No | No | Valid weekdays subset | Permitted interview days |

---

## 10. Interview (`interviews`)
Scheduled evaluation events between candidate applications and interviewers.

| Field Name | Type | Req/Opt | Allowed Values | Unique | PK | FK | Validation Rule | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `interview_id` | String(32) | Required | Format: `INT-2026-000001` | Yes | Yes | No | Regex `^INT-2026-\d{6}$` | Unique interview round identifier |
| `application_id` | String(96) | Required | Existing application ID | No | No | Yes | References `applications.application_id` | Target application dossier |
| `interviewer_id` | String(32) | Required | Existing interviewer ID | No | No | Yes | References `interviewers.interviewer_id` | Assigned evaluator |
| `scheduled_at` | String(32) | Required | Format: `YYYY-MM-DDTHH:MM:SS` | No | No | No | Valid ISO datetime | Interview timestamp |
| `scheduled_day` | String(16) | Required | Weekday name (e.g. `Monday`) | No | No | No | Must match `interviewer.available_days` | Scheduled day of the week |
| `stage` | String(32) | Required | `TECHNICAL_SCREEN`, `SYSTEM_DESIGN`, `BEHAVIORAL`, `FINAL_ROUND` | No | No | No | Allowed enum set | Assessment round type |
| `status` | String(32) | Required | `SCHEDULED`, `COMPLETED`, `CANCELLED` | No | No | No | Allowed enum set | Execution state |
| `duration_minutes`| Integer | Required | 30 to 120 | No | No | No | Positive integer | Round duration |
| `created_at` | DateTime | Required | ISO 8601 Timestamp | No | No | No | Valid past datetime | Record creation timestamp |

---

## 11. Feedback (`feedback`)
Structured quantitative scorecards and notes submitted following an interview.

| Field Name | Type | Req/Opt | Allowed Values | Unique | PK | FK | Validation Rule | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `feedback_id` | String(96) | Required | Format: `FB-<int-id>-<emp-id>` | Yes | Yes | No | Unique composite string | Immutable feedback identifier |
| `interview_id` | String(32) | Required | Existing interview ID | Yes | No | Yes | References `interviews.interview_id` | 1-to-1 link to interview round |
| `interviewer_id` | String(32) | Required | Existing interviewer ID | No | No | Yes | References `interviewers.interviewer_id` | Submitting evaluator |
| `technical_rating` | Integer | Required | 1 to 5 | No | No | No | Integer `1 <= x <= 5` | Technical skill score |
| `communication_rating` | Integer | Required | 1 to 5 | No | No | No | Integer `1 <= x <= 5` | Communication competence score |
| `problem_solving_rating` | Integer | Required | 1 to 5 | No | No | No | Integer `1 <= x <= 5` | Analytical problem-solving score |
| `overall_recommendation` | String(32) | Required | `STRONG_NO_HIRE`, `NO_HIRE`, `LEAN_HIRE`, `STRONG_HIRE` | No | No | No | Allowed enum set | Final hiring recommendation |
| `notes` | Text | Required | Descriptive text string | No | No | No | Min 10 characters | Qualitative feedback commentary |
| `submitted_at` | String(32) | Required | Format: `YYYY-MM-DDTHH:MM:SS` | No | No | No | `>= interview.scheduled_at` | Submission timestamp |

---

## 12. Offer (`offers`)
Formal employment contracts extended to successful candidates.

| Field Name | Type | Req/Opt | Allowed Values | Unique | PK | FK | Validation Rule | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `offer_id` | String(32) | Required | Format: `OFF-2026-000001` | Yes | Yes | No | Regex `^OFF-2026-\d{6}$` | Unique offer identifier |
| `application_id` | String(96) | Required | Existing application ID | Yes | No | Yes | References `applications.application_id` | 1-to-1 link to application |
| `offered_salary` | Float | Required | Positive float | No | No | No | Must fall within requisition band | Proposed base salary |
| `approval_status` | String(32) | Required | `PENDING_APPROVAL`, `APPROVED`, `REJECTED` | No | No | No | Allowed enum set | Executive compensation state |
| `approved_by` | String(128) | Optional | Approver name/title | No | No | No | Required if APPROVED | Executive approver signatory |
| `candidate_decision`| String(32) | Required | `PENDING`, `ACCEPTED`, `DECLINED` | No | No | No | Allowed enum set | Candidate acceptance status |
| `offer_date` | String(32) | Required | Format: `YYYY-MM-DD` | No | No | No | Valid date | Date offer extended |
| `expiration_date` | String(32) | Required | Format: `YYYY-MM-DD` | No | No | No | `>= offer_date` | Offer expiration date |
| `created_at` | DateTime | Required | ISO 8601 Timestamp | No | No | No | Valid past datetime | Record creation timestamp |
