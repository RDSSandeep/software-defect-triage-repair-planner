from fastapi import FastAPI
from app.models.database import init_db
from app.routes.bug_routes import router as bug_router

app = FastAPI(title="Software Defect Triage & Repair Planner API")

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()

app.include_router(bug_router)

@app.get("/")
def read_root():
    return {"message": "Software Defect Triage System API is running"}
