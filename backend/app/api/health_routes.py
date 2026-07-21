from __future__ import annotations

import logging
import os
import platform
import sys
import time
from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy import text

from app.dependencies import get_store, Store
from app.schemas.responses import HealthResponse
from app.services import RAG_AVAILABLE, gemini_available, rag_service

logger = logging.getLogger("learnmate.health")

router = APIRouter(tags=["health"])

_SERVER_START_TIME = time.time()


def _check_database() -> bool:
    """Lightweight check that the SQLite database is reachable."""
    try:
        from app.database import SessionLocal
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.warning("Database health check failed: %s", e)
        return False


def _get_database_size_kb() -> float | None:
    """Return the SQLite database file size in KB, or None if unavailable."""
    try:
        from app.database import DB_PATH
        if DB_PATH.exists():
            return round(DB_PATH.stat().st_size / 1024, 1)
    except Exception:
        pass
    return None


async def _get_rag_doc_count() -> int | None:
    """Return the number of indexed RAG documents, or None if unavailable."""
    if not RAG_AVAILABLE or rag_service is None:
        return None
    try:
        stats = await rag_service.get_collection_stats()
        return stats.get("total_documents", 0)
    except Exception:
        return None


async def _check_rag() -> str:
    """Return RAG service status string."""
    if not RAG_AVAILABLE or rag_service is None:
        return "disabled"
    try:
        stats = await rag_service.get_collection_stats()
        doc_count = stats.get("total_documents", 0)
        return "healthy" if doc_count > 0 else "empty"
    except Exception:
        return "error"


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns service health status including availability of optional AI services.",
    responses={
        200: {"description": "Service is healthy"},
    },
)
async def health_check(store: Store = Depends(get_store)) -> HealthResponse:
    db_ok = _check_database()
    rag_status = await _check_rag()

    indexed_docs = await _get_rag_doc_count()

    return HealthResponse(
        status="healthy",
        version="2.0.0",
        backend="online",
        database="online" if db_ok else "offline",
        gemini="online" if gemini_available else "disabled",
        rag=rag_status if rag_status in ("healthy", "empty") else (
            "offline" if rag_status == "error" else "disabled"
        ),
        services={
            "database": "online" if db_ok else "offline",
            "rag": rag_status,
            "gemini": "online" if gemini_available else "disabled",
            "mentor": "online",
            "skill_analyzer": "online",
            "roadmap_generator": "online",
        },
        environment=os.getenv("APP_ENV", "development"),
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        database_type="SQLite",
        database_size_kb=_get_database_size_kb(),
        indexed_documents=indexed_docs,
        server_uptime_seconds=round(time.time() - _SERVER_START_TIME, 1),
        operating_system=f"{platform.system()} {platform.release()}",
    )
