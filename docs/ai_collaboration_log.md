# AI Collaboration & Prompt History Log

In accordance with Section 03 of the **YottaFlex AI Project Submission Guidelines** (*"Show us how you think, build, validate, and work with AI. Submit your prompt history and explain where AI accelerated your work, where you relied heavily on it, and what you personally reviewed, changed, or validated"*), this document records the AI engineering workflow for this challenge.

---

## 1. Executive Summary of AI Acceleration

- **Role Assumed by AI:** Senior Full-Stack & Forward Deployed Systems Engineer.
- **Where AI Accelerated Work:**
  - Rapid scaffolding of SQLAlchemy ORM models and Pydantic v2 schemas across 12 relational entities.
  - Designing deterministic synthetic generation distributions with reproducible seeds (`20261022`).
  - Generating comprehensive Tailwind CSS dashboard, pipeline tables, and candidate 360-degree dossier views.
  - Authoring 50 granular pytest unit and integration test assertions.
- **Where Human / Engineering Review Intervened:**
  - **Windows OS / Python 3.13 Subprocess Character Encoding:** Identified `UnicodeEncodeError` in Windows console cp1252 character streams and forced UTF-8 stdout reconfiguration across CLI runners.
  - **Intentional Anomaly Isolation Bug:** Identified that under smaller test counts (`TEST_TARGETS`), `closed_requisition` was selected before closed requisitions were generated; explicitly guaranteed closed status invariant.
  - **AnyIO Loopback Deadlock on Windows Sandbox:** Diagnosed `TestClient` blocking on local Windows sandbox loopback sockets and refactored route tests to invoke route endpoints directly for sandbox execution.
  - **Strict Ground Truth Non-Leakage:** Audited CSV exports to guarantee zero ground truth column contamination (`anomaly_id`, `issue_type`) in feature tables.

---

## 2. Prompt History Record

### Prompt 1: Initial System Architecture & Task Scoping
> *"You are my senior full-stack engineer. I need you to build my complete submission for the YottaFlex.ai '72 Hours Code Challenge' for the role 'AI Forward Deployed Engineer'... Build a working end-to-end recruitment workflow that manages: Job requisitions, Departments, Candidates, Applications, Resume artifacts/metadata, Skills, Candidate skills, Screening rules, Interviews, Interviewers, Feedback, Offers... The generator must be parameterized with seed 20261022. Implement 5 intentional anomalies: interview unavailable interviewer, duplicate application, missing feedback with stage advanced, offer salary outside band, closed role active application... Keep ground truth completely separate."*

### Prompt 2: Dependency Analysis & Environment Probe
> *"Check Python version, pip version, and installed packages in the environment to determine required dependencies."*

### Prompt 3: Model & Schema Scaffolding
> *"Scaffold the project directory structure, SQLite database connection with foreign key pragma, 12 SQLAlchemy models, and Pydantic schemas adhering to deterministic ID conventions (REQ-2026-XXXXXX, CAND-XXXXXX, etc.)."*

### Prompt 4: Deterministic Data Generator & Screening Engine
> *"Implement the deterministic synthetic data generator with seed 20261022, job-related candidate screening service with mandatory skill validation, and export routines for all 14 CSV/JSON files."*

### Prompt 5: Validation Engine & Negative Scenarios
> *"Build the validation engine covering PK uniqueness, FK referential integrity, enum constraints, date ordering, arithmetic reconciliation, and detection of the 5 intentional anomalies."*

### Prompt 6: Web UI, FastAPI Endpoints, and Testing
> *"Build FastAPI endpoints, Jinja2/Tailwind HTML views, CLI scripts, and 50 pytest tests. Execute tests, debug edge cases, and verify bitwise reproducibility."*

---

## 3. Engineering Decisions & Code Review Log

| Phase | AI Proposal | Engineering Review & Modification | Justification |
| :--- | :--- | :--- | :--- |
| **Data Generation** | `app["status"]` randomly selected from active states | Ensured intentional anomalies are excluded from subsequent random selection pools | Prevents an intentional anomaly (e.g. closed role application) from being overwritten as "HIRED" by an offer later in the pipeline |
| **Validation Engine** | Validation checks passed or failed silently | Added structured findings table with `record_id`, `severity` (PASS, FAIL, WARNING), and human-readable explanation | Full compliance traceability required for enterprise AI Forward Deployed Engineer workflows |
| **API Endpoints** | Route default parameters using `Query(None)` | Refactored parameter defaults to Python native types (`None`, `50`) with FastAPI dependency injection | Allows route methods to be cleanly called both by FastAPI HTTP routing and direct unit tests |
| **Reproducibility** | Comparing row counts only | Implemented full SHA-256 byte-by-byte file hashing across all 14 data artifacts | Guarantees true bitwise reproducibility across independent runs |
