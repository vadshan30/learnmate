from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies import Store, get_store, get_student_or_404, get_roadmap_or_404
from app.exceptions import ServiceUnavailableError
from app.models.student import SkillLevel, StudentProfile
from app.schemas.requests import RoadmapGenerateRequest
from app.schemas.responses import ErrorResponse, RoadmapResponse, SuccessResponse
from app.services import RAG_AVAILABLE, granite_available
from app.services.roadmap_generator import RoadmapGenerator

router = APIRouter(prefix="/api/roadmap", tags=["roadmap"])


def _dict_to_profile(data: dict) -> StudentProfile:
    level = data.get("skill_level", "beginner")
    level_map = {"beginner": SkillLevel.BEGINNER, "intermediate": SkillLevel.INTERMEDIATE, "advanced": SkillLevel.ADVANCED}
    return StudentProfile(
        name=data.get("name", "Unknown"),
        current_skills=data.get("current_skills", []),
        interests=data.get("interests", []),
        career_goal=data.get("career_goal", "General"),
        skill_level=level_map.get(level.lower(), SkillLevel.BEGINNER),
        completed_topics=data.get("completed_topics", []),
        progress_percentage=data.get("progress_percentage", 0.0),
    )


@router.post(
    "",
    response_model=RoadmapResponse,
    status_code=201,
    summary="Generate learning roadmap",
    description="Generates a personalized AI learning roadmap for a student.",
    responses={
        201: {"description": "Roadmap generated"},
        404: {"model": ErrorResponse, "description": "Student not found"},
        503: {"model": ErrorResponse, "description": "AI service unavailable"},
    },
)
async def generate_roadmap(
    body: RoadmapGenerateRequest,
    store: Store = Depends(get_store),
) -> RoadmapResponse:
    profile_dict = get_student_or_404(body.student_id, store)
    profile = _dict_to_profile(profile_dict)
    generator = RoadmapGenerator()
    result = await generator.generate_roadmap(profile)
    store.roadmaps[body.student_id] = result
    source = "watsonx" if granite_available else "fallback"
    return RoadmapResponse(
        student_id=body.student_id,
        roadmap=result,
        fallback=not granite_available,
        source=source,
    )


@router.get(
    "/{student_id}",
    response_model=RoadmapResponse,
    summary="Get student roadmap",
    description="Returns the existing roadmap for a student.",
    responses={
        200: {"description": "Roadmap found"},
        404: {"model": ErrorResponse, "description": "Roadmap not found"},
    },
)
async def get_roadmap(student_id: str, store: Store = Depends(get_store)) -> RoadmapResponse:
    get_student_or_404(student_id, store)
    roadmap = get_roadmap_or_404(student_id, store)
    source = "watsonx" if granite_available else "fallback"
    return RoadmapResponse(
        student_id=student_id,
        roadmap=roadmap,
        fallback=not granite_available,
        source=source,
    )


@router.put(
    "/{student_id}",
    response_model=SuccessResponse,
    summary="Update roadmap",
    description="Updates an existing roadmap by regenerating it.",
    responses={
        200: {"description": "Roadmap updated"},
        404: {"model": ErrorResponse, "description": "Student not found"},
    },
)
async def update_roadmap(
    student_id: str,
    body: RoadmapGenerateRequest,
    store: Store = Depends(get_store),
) -> SuccessResponse:
    profile_dict = get_student_or_404(student_id, store)
    profile = _dict_to_profile(profile_dict)
    generator = RoadmapGenerator()
    result = await generator.generate_roadmap(profile)
    store.roadmaps[student_id] = result
    return SuccessResponse(message="Roadmap updated", data=result)


@router.delete(
    "/{student_id}",
    response_model=SuccessResponse,
    summary="Delete roadmap",
    description="Deletes a student's roadmap.",
    responses={
        200: {"description": "Roadmap deleted"},
        404: {"model": ErrorResponse, "description": "Student not found"},
    },
)
async def delete_roadmap(student_id: str, store: Store = Depends(get_store)) -> SuccessResponse:
    get_student_or_404(student_id, store)
    store.roadmaps.pop(student_id, None)
    return SuccessResponse(message="Roadmap deleted")
