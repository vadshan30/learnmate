from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies import get_store, Store
from app.schemas.responses import HealthResponse
from app.services import RAG_AVAILABLE, granite_available

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
    return HealthResponse(
        status="ok",
        version="1.0.0",
        rag_available=RAG_AVAILABLE,
        watsonx_available=granite_available,
        services={
            "rag": "available" if RAG_AVAILABLE else "unavailable",
            "watsonx": "available" if granite_available else "unavailable",
            "skill_analyzer": "available",
            "roadmap_generator": "available",
        },
    )
