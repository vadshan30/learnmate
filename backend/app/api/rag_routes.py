"""RAG management API routes for LearnMate AI.

Provides endpoints to query the RAG service status and trigger
dataset reloads.  These complement the existing search endpoint
in search_routes.py.
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from app.exceptions import ServiceUnavailableError
from app.schemas.responses import ErrorResponse, SuccessResponse
from app.services import RAG_AVAILABLE, rag_service

router = APIRouter(prefix="/api/rag", tags=["rag"])


@router.get(
    "/status",
    response_model=SuccessResponse,
    summary="RAG service status",
    description="Returns detailed status of the RAG service including document counts and health.",
    responses={
        200: {"description": "RAG status returned"},
        503: {"model": ErrorResponse, "description": "RAG service unavailable"},
    },
)
async def rag_status() -> SuccessResponse:
    if not RAG_AVAILABLE or rag_service is None:
        raise ServiceUnavailableError("RAG")

    stats = await rag_service.get_collection_stats()
    return SuccessResponse(message="RAG status", data=stats)


@router.post(
    "/reload",
    response_model=SuccessResponse,
    summary="Reload RAG datasets",
    description="Force-reloads all learning resource datasets into the ChromaDB vector store.",
    responses={
        200: {"description": "Datasets reloaded"},
        503: {"model": ErrorResponse, "description": "RAG service unavailable"},
    },
)
async def rag_reload() -> SuccessResponse:
    if not RAG_AVAILABLE or rag_service is None:
        raise ServiceUnavailableError("RAG")

    counts = await rag_service.reload_all()
    return SuccessResponse(
        message=f"Reloaded {counts.get('total', 0)} documents",
        data=counts,
    )
