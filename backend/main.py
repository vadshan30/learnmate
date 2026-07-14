"""LearnMate AI – FastAPI Application Entry Point.

Sets up the FastAPI application, loads environment variables,
mounts static data, and exposes core API routes via modular routers.
"""

from __future__ import annotations

import json
import logging
import os
from contextlib import asynccontextmanager
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
# Lifespan (startup / shutdown)
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load datasets and initialise services on startup, clean up on shutdown."""
    logger.info("Starting LearnMate AI – env=%s", APP_ENV)

    init_store()
    store = get_store_direct()

    from app.utils.data_loader import (
        load_courses,
        load_certifications,
        load_projects,
    )

    courses = load_courses()
    store.loaded_courses = [Course(**item) for item in courses]
    logger.info("Loaded %d courses into Store", len(store.loaded_courses))

    certs = load_certifications()
    store.loaded_certifications = [Certification(**item) for item in certs]
    logger.info("Loaded %d certifications into Store", len(store.loaded_certifications))

    projects = load_projects()
    store.loaded_projects = [Project(**item) for item in projects]
    logger.info("Loaded %d projects into Store", len(store.loaded_projects))

    if RAG_AVAILABLE and rag_service is not None:
        try:
            await rag_service.initialise()
            stats = await rag_service.get_collection_stats()
            logger.info(
                "RAG service initialised – %d documents indexed, status=%s",
                stats.get("total_documents", 0),
                stats.get("status", "unknown"),
            )
        except Exception as exc:
            logger.error("[RAG ERROR] Initialization failed: %s", exc)
    else:
        logger.warning(
            "[RAG] ChromaDB/sentence-transformers not installed – RAG endpoints return 503"
        )

    logger.info("LearnMate AI ready (watsonx=%s, rag=%s)", granite_available, RAG_AVAILABLE)

    yield

    logger.info("LearnMate AI shutting down")


# ---------------------------------------------------------------------------
# Application instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title="LearnMate AI",
    description="AI-powered personalised learning coach platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
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
    from fastapi import HTTPException as _HTTPException
    for course in store.loaded_courses:
        if course.id == course_id:
            return course
    raise _HTTPException(status_code=404, detail=f"Course '{course_id}' not found")


@app.get("/api/certifications", response_model=List[Certification], tags=["Catalog"])
async def list_certifications() -> List[Certification]:
    return store.loaded_certifications


@app.get("/api/projects", response_model=List[Project], tags=["Catalog"])
async def list_projects() -> List[Project]:
    return store.loaded_projects


@app.get("/api/profile/{name}", tags=["Student Profile"])
async def get_profile_legacy(name: str) -> Dict[str, Any]:
    from fastapi import HTTPException as _HTTPException
    key = name.lower().strip()
    profile = store.student_profiles.get(key)
    if profile is None:
        raise _HTTPException(status_code=404, detail=f"Profile '{name}' not found")
    return profile


@app.post("/api/profile", tags=["Student Profile"])
async def create_profile_legacy(profile: Dict[str, Any]) -> Dict[str, Any]:
    key = profile.get("name", "").lower().strip()
    store.student_profiles[key] = profile
    return profile
