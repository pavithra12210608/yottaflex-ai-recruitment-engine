"""Main FastAPI Application Entrypoint for YottaFlex AI Recruitment Engine."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db, SessionLocal
from app.routes.api import router as api_router
from app.routes.ui import router as ui_router
from app.models import Department
from app.services.recruitment_service import generate_and_save_data, load_entities_from_csv, seed_database_from_entities

app = FastAPI(
    title="YottaFlex.ai Recruitment Engine",
    description=(
        "Autonomous, deterministic hiring workflow management platform with synthetic data generation, "
        "job-related screening, interview scheduling, validation compliance rules, and intentional edge-case auditing."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for open local accessibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(ui_router)
app.include_router(api_router)


@app.on_event("startup")
def startup_event():
    """Ensure database schema is created and populated on initial startup."""
    init_db()
    db = SessionLocal()
    try:
        # Check if database is already populated
        dept_count = db.query(Department).count()
        if dept_count == 0:
            # Check if CSVs exist to load, otherwise generate
            entities = load_entities_from_csv()
            if any(len(v) > 0 for v in entities.values()):
                seed_database_from_entities(db, entities)
            else:
                generate_and_save_data(db=db)
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
