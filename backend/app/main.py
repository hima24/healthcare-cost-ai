import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import init_db
from .ml.predictor import get_predictor
from .routers import dashboard, jobs, predict, upload

app = FastAPI(
    title="Healthcare Cost Prediction & Resource Planning API",
    description=(
        "Predicts per-patient healthcare cost from Medicare-claims-style "
        "features, supports single and bulk (async) scoring, and powers "
        "the resource-planning dashboard."
    ),
    version="1.0.0",
)

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://127.0.0.1:5500,http://localhost:5500",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router)
app.include_router(upload.router)
app.include_router(jobs.router)
app.include_router(dashboard.router)


@app.on_event("startup")
def on_startup():
    init_db()
    get_predictor()  # trains/loads the model once at boot so first request isn't slow


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api")
def root():
    return {
        "message": "Healthcare Cost Prediction API is running.",
        "docs": "/docs",
    }


# ============================================================
# STATIC FRONTEND (single-container deploy, e.g. Cloud Run)
# ============================================================
# All real API routes live under /api/* (see the routers above),
# plus FastAPI's own /docs, /openapi.json, /redoc. Those are matched
# first because they were registered first, so mounting the static
# frontend at "/" here is safe and never shadows them.
# Only mounted if the frontend/ folder is present next to backend/
# (it is, in this repo's layout: <project_root>/frontend).
_frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if _frontend_dir.is_dir():
    app.mount("/", StaticFiles(directory=_frontend_dir, html=True), name="frontend")
