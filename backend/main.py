"""LearnMate AI – FastAPI Application Entry Point.

Sets up the FastAPI application, loads environment variables,
mounts static data, and exposes core API routes via modular routers.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ALL_ROUTERS
from app.dependencies import get_store_direct, init_store
from app.exceptions import register_exception_handlers
from app.models.roadmap import Certification, Course, Project
from app.services import RAG_AVAILABLE, granite_available, rag_service

# ---------------------------------------------------------------------------
# Environment & paths
# ---------------------------------------------------------------------------

load_dotenv(Path(__file__).parent / ".env")

APP_ENV: str = os.getenv("APP_ENV", "development")
DATA_DIR: Path = Path(__file__).parent.parent / "data"

# ---------------------------------------------------------------------------
# Structured logging
# ---------------------------------------------------------------------------

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("learnmate")

# ---------------------------------------------------------------------------
# Application instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title="LearnMate AI",
    description="AI-powered personalized learning coach platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------

register_exception_handlers(app)

# ---------------------------------------------------------------------------
# Register routers
# ---------------------------------------------------------------------------

for router in ALL_ROUTERS:
    app.include_router(router)

# ---------------------------------------------------------------------------
# Legacy inline routes (backward compatibility for catalog & profile)
# ---------------------------------------------------------------------------

store = get_store_direct()


@app.on_event("startup")
async def load_datasets() -> None:
    """Load JSON datasets and initialise services on application startup."""
    logger.info("Starting LearnMate AI – env=%s", APP_ENV)

    init_store()
    store = get_store_direct()

    courses_path = DATA_DIR / "courses.json"
    if courses_path.exists():
        with open(courses_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            store.loaded_courses = [Course(**item) for item in raw]
        logger.info("Loaded %d courses", len(store.loaded_courses))

    certs_path = DATA_DIR / "certifications.json"
    if certs_path.exists():
        with open(certs_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            store.loaded_certifications = [Certification(**item) for item in raw]
        logger.info("Loaded %d certifications", len(store.loaded_certifications))

    projects_path = DATA_DIR / "projects.json"
    if projects_path.exists():
        with open(projects_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            store.loaded_projects = [Project(**item) for item in raw]
        logger.info("Loaded %d projects", len(store.loaded_projects))

    if RAG_AVAILABLE and rag_service is not None:
        await rag_service.initialise()
        logger.info("RAG service initialised")
    else:
        logger.warning(
            "ChromaDB/sentence-transformers not installed – RAG endpoints return 503"
        )

    logger.info("LearnMate AI ready (watsonx=%s, rag=%s)", granite_available, RAG_AVAILABLE)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    logger.info("LearnMate AI shutting down")


# ---------------------------------------------------------------------------
# Root & legacy endpoints
# ---------------------------------------------------------------------------


@app.get("/", tags=["System"])
async def root() -> Dict[str, str]:
    return {
        "app": "LearnMate AI",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/api/courses", response_model=List[Course], tags=["Catalog"])
async def list_courses() -> List[Course]:
    return store.loaded_courses


@app.get("/api/courses/{course_id}", response_model=Course, tags=["Catalog"])
async def get_course(course_id: str) -> Course:
    for course in store.loaded_courses:
        if course.id == course_id:
            return course
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail=f"Course '{course_id}' not found")


@app.get("/api/certifications", response_model=List[Certification], tags=["Catalog"])
async def list_certifications() -> List[Certification]:
    return store.loaded_certifications


@app.get("/api/projects", response_model=List[Project], tags=["Catalog"])
async def list_projects() -> List[Project]:
    return store.loaded_projects


@app.get("/api/profile/{name}", tags=["Student Profile"])
async def get_profile_legacy(name: str) -> Dict[str, Any]:
    key = name.lower().strip()
    profile = store.student_profiles.get(key)
    if profile is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Profile '{name}' not found")
    return profile


@app.post("/api/profile", tags=["Student Profile"])
async def create_profile_legacy(profile: Dict[str, Any]) -> Dict[str, Any]:
    key = profile.get("name", "").lower().strip()
    store.student_profiles[key] = profile
    return profile
