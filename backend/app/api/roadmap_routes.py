from __future__ import annotations

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Query

from app.dependencies import Store, get_store, get_student_or_404, get_roadmap_or_404
from app.exceptions import LearnMateError, ServiceUnavailableError
from app.models.student import SkillLevel, StudentProfile
from app.schemas.requests import (
    RoadmapGenerateRequest,
    TopicCompleteRequest,
    ProgressUpdateBody,
)
from app.schemas.responses import ErrorResponse, RoadmapResponse, SuccessResponse
from app.services import RAG_AVAILABLE, granite_available
from app.services.roadmap_generator import RoadmapGenerator
from app.services import progress_service

logger = logging.getLogger("learnmate.api.roadmap")

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


# ── Progress endpoints (must come before /{student_id}) ────────────────


@router.get(
    "/progress/{student_id}",
    response_model=SuccessResponse,
    summary="Get student progress",
    description="Returns detailed progress including overall completion, weekly breakdown, and skill mastery.",
    responses={
        200: {"description": "Progress returned"},
        404: {"model": ErrorResponse, "description": "Student or roadmap not found"},
    },
)
async def get_progress(
    student_id: str,
    store: Store = Depends(get_store),
) -> SuccessResponse:
    profile = get_student_or_404(student_id, store)
    roadmap = get_roadmap_or_404(student_id, store)

    progress = progress_service.get_progress_summary(
        roadmap, student_skills=profile.get("current_skills", [])
    )
    return SuccessResponse(message="Progress retrieved", data=progress)


@router.put(
    "/progress/{student_id}",
    response_model=SuccessResponse,
    summary="Update student progress",
    description="Updates completed topics and recalculates roadmap progress.",
    responses={
        200: {"description": "Progress updated"},
        404: {"model": ErrorResponse, "description": "Student or roadmap not found"},
    },
)
async def update_progress(
    student_id: str,
    body: ProgressUpdateBody,
    store: Store = Depends(get_store),
) -> SuccessResponse:
    profile_dict = get_student_or_404(student_id, store)
    roadmap = get_roadmap_or_404(student_id, store)

    if body.completed_topics:
        logger.info(
            "Updating progress for student '%s' — %d topics completed",
            student_id,
            len(body.completed_topics),
        )
        generator = RoadmapGenerator()
        roadmap = generator.update_roadmap(roadmap, body.completed_topics)
        store.roadmaps[student_id] = roadmap

        # Also update student profile's completed_topics
        existing = set(profile_dict.get("completed_topics", []))
        existing.update(t.lower().strip() for t in body.completed_topics)
        profile_dict["completed_topics"] = list(existing)

        # Update progress percentage
        progress = roadmap.get("progress", {})
        profile_dict["progress_percentage"] = progress.get("percentage", 0.0)

    progress = progress_service.get_progress_summary(
        roadmap, student_skills=profile_dict.get("current_skills", [])
    )
    return SuccessResponse(message="Progress updated", data=progress)


@router.post(
    "/topic/complete",
    response_model=SuccessResponse,
    summary="Mark topic complete",
    description="Marks a single topic as completed and recalculates progress.",
    responses={
        200: {"description": "Topic marked complete"},
        404: {"model": ErrorResponse, "description": "Student or roadmap not found"},
    },
)
async def complete_topic(
    body: TopicCompleteRequest,
    store: Store = Depends(get_store),
) -> SuccessResponse:
    profile_dict = get_student_or_404(body.student_id, store)
    roadmap = get_roadmap_or_404(body.student_id, store)

    logger.info(
        "Completing topic '%s' (completed=%s) for student '%s'",
        body.topic_name,
        body.completed,
        body.student_id,
    )

    try:
        generator = RoadmapGenerator()
        roadmap = generator.update_topic_completion(
            roadmap, body.topic_name, body.completed
        )
        store.roadmaps[body.student_id] = roadmap
    except Exception as exc:
        logger.error(
            "Failed to update topic '%s' for student '%s': %s",
            body.topic_name,
            body.student_id,
            exc,
            exc_info=True,
        )
        raise LearnMateError(
            message=f"Failed to update topic '{body.topic_name}': {exc}",
            error_code="TOPIC_UPDATE_FAILED",
            status_code=500,
        )

    # Update student profile
    existing = set(profile_dict.get("completed_topics", []))
    topic_lower = body.topic_name.lower().strip()
    if body.completed:
        existing.add(topic_lower)
    else:
        existing.discard(topic_lower)
    profile_dict["completed_topics"] = list(existing)
    profile_dict["progress_percentage"] = roadmap.get("progress", {}).get("percentage", 0.0)

    progress = progress_service.get_progress_summary(
        roadmap, student_skills=profile_dict.get("current_skills", [])
    )

    logger.info(
        "Topic '%s' completed for student '%s' — progress: %.1f%% (%d/%d topics)",
        body.topic_name,
        body.student_id,
        progress.get("overall_progress", 0.0),
        progress.get("completed_topics", 0),
        progress.get("total_topics", 0),
    )

    return SuccessResponse(
        message=f"Topic '{body.topic_name}' {'completed' if body.completed else 'uncompleted'}",
        data=progress,
    )


@router.get(
    "/progress/{student_id}/weekly",
    response_model=SuccessResponse,
    summary="Get weekly progress",
    description="Returns per-week progress breakdown for a student.",
    responses={
        200: {"description": "Weekly progress returned"},
        404: {"model": ErrorResponse, "description": "Student or roadmap not found"},
    },
)
async def get_weekly_progress(
    student_id: str,
    store: Store = Depends(get_store),
) -> SuccessResponse:
    get_student_or_404(student_id, store)
    roadmap = get_roadmap_or_404(student_id, store)

    weekly = progress_service.get_weekly_progress(roadmap)
    return SuccessResponse(message="Weekly progress retrieved", data=weekly)


@router.get(
    "/progress/{student_id}/skills",
    response_model=SuccessResponse,
    summary="Get skill mastery progress",
    description="Returns skill mastery progress for a student.",
    responses={
        200: {"description": "Skill progress returned"},
        404: {"model": ErrorResponse, "description": "Student or roadmap not found"},
    },
)
async def get_skill_progress(
    student_id: str,
    store: Store = Depends(get_store),
) -> SuccessResponse:
    profile_dict = get_student_or_404(student_id, store)
    roadmap = get_roadmap_or_404(student_id, store)

    skills = progress_service.get_skill_mastery_progress(
        roadmap, profile_dict.get("current_skills", [])
    )
    return SuccessResponse(message="Skill progress retrieved", data=skills)


# ── Standard roadmap endpoints ──────────────────────────────────────────


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
