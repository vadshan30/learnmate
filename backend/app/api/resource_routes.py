"""Resource API routes for LearnMate AI.

Provides endpoints for browsing, searching, and filtering
courses, projects, and certifications.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query

from app.dependencies import Store, get_store
from app.schemas.responses import ErrorResponse, SuccessResponse
from app.services import RAG_AVAILABLE, rag_service
from app.services import resource_service

router = APIRouter(prefix="/api/resources", tags=["resources"])


@router.get(
    "/courses",
    response_model=SuccessResponse,
    summary="Get all courses",
    description="Returns all available courses with optional filtering.",
    responses={200: {"description": "Courses returned"}},
)
async def list_courses(
    domain: Optional[str] = Query(default=None, description="Filter by domain"),
    difficulty: Optional[str] = Query(default=None, description="Filter by difficulty"),
    provider: Optional[str] = Query(default=None, description="Filter by provider"),
) -> SuccessResponse:
    courses = resource_service.get_all_courses()

    if domain:
        domain_lower = domain.lower().strip()
        courses = [
            c for c in courses
            if domain_lower in (c.get("domain", "") or "").lower()
        ]

    if difficulty:
        courses = [
            c for c in courses
            if resource_service._matches_difficulty(c, difficulty)
        ]

    if provider:
        provider_lower = provider.lower().strip()
        courses = [
            c for c in courses
            if provider_lower in (c.get("provider", "") or "").lower()
        ]

    return SuccessResponse(
        message=f"Found {len(courses)} courses",
        data=courses,
    )


@router.get(
    "/courses/{course_id}",
    response_model=SuccessResponse,
    summary="Get a course by ID",
    description="Returns a single course by its ID.",
    responses={
        200: {"description": "Course found"},
        404: {"description": "Course not found"},
    },
)
async def get_course(course_id: str) -> SuccessResponse:
    course = resource_service.get_course(course_id)
    if course is None:
        from app.exceptions import LearnMateError
        raise LearnMateError(
            message=f"Course '{course_id}' not found",
            error_code="COURSE_NOT_FOUND",
            status_code=404,
        )
    return SuccessResponse(message="Course found", data=course)


@router.get(
    "/projects",
    response_model=SuccessResponse,
    summary="Get all projects",
    description="Returns all available projects.",
    responses={200: {"description": "Projects returned"}},
)
async def list_projects(
    difficulty: Optional[str] = Query(default=None, description="Filter by difficulty"),
) -> SuccessResponse:
    projects = resource_service.get_projects()

    if difficulty:
        projects = [
            p for p in projects
            if resource_service._matches_difficulty(p, difficulty)
        ]

    return SuccessResponse(
        message=f"Found {len(projects)} projects",
        data=projects,
    )


@router.get(
    "/certifications",
    response_model=SuccessResponse,
    summary="Get all certifications",
    description="Returns all available certifications.",
    responses={200: {"description": "Certifications returned"}},
)
async def list_certifications(
    provider: Optional[str] = Query(default=None, description="Filter by provider"),
) -> SuccessResponse:
    certifications = resource_service.get_certifications()

    if provider:
        provider_lower = provider.lower().strip()
        certifications = [
            c for c in certifications
            if provider_lower in (c.get("provider", "") or "").lower()
        ]

    return SuccessResponse(
        message=f"Found {len(certifications)} certifications",
        data=certifications,
    )


@router.get(
    "/search",
    response_model=SuccessResponse,
    summary="Search resources",
    description="Search across courses, projects, and certifications.",
    responses={200: {"description": "Search results"}},
)
async def search_resources(
    q: str = Query(..., min_length=1, description="Search query"),
    top_k: int = Query(default=10, ge=1, le=50, description="Max results"),
    difficulty: Optional[str] = Query(default=None, description="Filter by difficulty"),
    domain: Optional[str] = Query(default=None, description="Filter by domain"),
    provider: Optional[str] = Query(default=None, description="Filter by provider"),
    type: Optional[str] = Query(default=None, description="Filter by type: course, project, certification"),
) -> SuccessResponse:
    results = resource_service.search_resources(
        query=q,
        top_k=top_k,
        difficulty=difficulty,
        domain=domain,
        provider=provider,
        resource_type=type,
    )
    return SuccessResponse(
        message=f"Found {len(results)} results",
        data=results,
    )


@router.post(
    "/sync",
    response_model=SuccessResponse,
    summary="Sync resources to RAG",
    description="Force-reloads all resources into the RAG vector store.",
    responses={
        200: {"description": "Resources synced"},
        503: {"model": ErrorResponse, "description": "RAG service unavailable"},
    },
)
async def sync_resources() -> SuccessResponse:
    if not RAG_AVAILABLE or rag_service is None:
        from app.exceptions import ServiceUnavailableError
        raise ServiceUnavailableError("RAG")

    counts = await rag_service.reload_all()
    return SuccessResponse(
        message=f"Synced {counts.get('total', 0)} documents",
        data=counts,
    )


@router.get(
    "/pathways",
    response_model=SuccessResponse,
    summary="Get career pathways",
    description="Returns all available career pathways.",
    responses={200: {"description": "Pathways returned"}},
)
async def list_pathways() -> SuccessResponse:
    pathways = resource_service.get_career_pathways()
    return SuccessResponse(
        message=f"Found {len(pathways)} pathways",
        data=pathways,
    )
