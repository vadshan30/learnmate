from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies import get_store, Store
from app.schemas.responses import HealthResponse
from app.services import RAG_AVAILABLE, granite_available, rag_service

router = APIRouter(tags=["health"])


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
    rag_status_str = "unavailable"
    if RAG_AVAILABLE and rag_service is not None:
        try:
            stats = await rag_service.get_collection_stats()
            doc_count = stats.get("total_documents", 0)
            if doc_count > 0:
                rag_status_str = "healthy"
            else:
                rag_status_str = "empty"
        except Exception:
            rag_status_str = "error"
    return HealthResponse(
        status="ok",
        version="1.0.0",
        rag_available=RAG_AVAILABLE and rag_status_str in ("healthy", "empty"),
        watsonx_available=granite_available,
        services={
            "rag": rag_status_str,
            "watsonx": "available" if granite_available else "unavailable",
            "skill_analyzer": "available",
            "roadmap_generator": "available",
        },
    )
