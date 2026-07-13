from __future__ import annotations

from fastapi import APIRouter, Query

from app.exceptions import ServiceUnavailableError
from app.schemas.responses import ErrorResponse, SuccessResponse
from app.services import RAG_AVAILABLE, rag_service

router = APIRouter(prefix="/api", tags=["search"])


@router.get(
    "/search",
    response_model=SuccessResponse,
    summary="Search learning resources",
    description="Searches the RAG knowledge base for courses, projects, and certifications.",
    responses={
        200: {"description": "Search results"},
        503: {"model": ErrorResponse, "description": "RAG service unavailable"},
    },
)
async def search_resources(
    q: str = Query(..., min_length=1, description="Search query"),
    top_k: int = Query(default=5, ge=1, le=20, description="Number of results"),
) -> SuccessResponse:
    if not RAG_AVAILABLE or rag_service is None:
        raise ServiceUnavailableError("RAG")

    results = await rag_service.search_courses(query=q, n=top_k)
    return SuccessResponse(message=f"Found {len(results)} results", data=results)


@router.get(
    "/rag/stats",
    response_model=SuccessResponse,
    summary="RAG knowledge base stats",
    description="Returns statistics about the RAG knowledge base.",
    responses={
        200: {"description": "Stats returned"},
        503: {"model": ErrorResponse, "description": "RAG service unavailable"},
    },
)
async def rag_stats() -> SuccessResponse:
    if not RAG_AVAILABLE or rag_service is None:
        raise ServiceUnavailableError("RAG")

    stats = await rag_service.get_collection_stats()
    return SuccessResponse(message="RAG stats", data=stats)
