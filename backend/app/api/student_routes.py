from __future__ import annotations

import uuid
from typing import Any, Dict

from fastapi import APIRouter, Depends, Query

from app.dependencies import Store, get_store, get_student_or_404
from app.schemas.requests import StudentCreateRequest, StudentUpdateRequest
from app.schemas.responses import ErrorResponse, SuccessResponse, StudentProfileResponse

router = APIRouter(prefix="/api/student", tags=["student"])


def _slug(name: str) -> str:
    return name.lower().strip().replace(" ", "-")


def _to_response(student_id: str, profile: Dict[str, Any]) -> StudentProfileResponse:
    return StudentProfileResponse(
        student_id=student_id,
        name=profile.get("name", ""),
        current_skills=profile.get("current_skills", []),
        interests=profile.get("interests", []),
        career_goal=profile.get("career_goal", ""),
        skill_level=profile.get("skill_level", "beginner"),
        completed_topics=profile.get("completed_topics", []),
        progress_percentage=profile.get("progress_percentage", 0.0),
        learning_style=profile.get("learning_style"),
    )


@router.post(
    "",
    response_model=SuccessResponse,
    status_code=201,
    summary="Create student profile",
    description="Creates a new student profile with skills, interests, and career goal.",
    responses={
        201: {"description": "Profile created successfully"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
)
async def create_student(body: StudentCreateRequest, store: Store = Depends(get_store)) -> SuccessResponse:
    student_id = _slug(body.name)
    profile = {
        "name": body.name,
        "student_id": student_id,
        "current_skills": body.current_skills,
        "interests": body.interests,
        "career_goal": body.career_goal,
        "skill_level": body.skill_level,
        "completed_topics": body.completed_topics,
        "progress_percentage": 0.0,
        "learning_style": body.learning_style,
    }
    store.student_profiles[student_id] = profile
    return SuccessResponse(message="Profile created", data=_to_response(student_id, profile).model_dump())


@router.get(
    "",
    response_model=list[StudentProfileResponse],
    summary="List all students",
    description="Returns all student profiles.",
)
async def list_students(store: Store = Depends(get_store)) -> list[StudentProfileResponse]:
    return [_to_response(sid, p) for sid, p in store.student_profiles.items()]


@router.get(
    "/{student_id}",
    response_model=StudentProfileResponse,
    summary="Get student profile",
    description="Returns a single student profile by ID.",
    responses={
        200: {"description": "Student found"},
        404: {"model": ErrorResponse, "description": "Student not found"},
    },
)
async def get_student(student_id: str, store: Store = Depends(get_store)) -> StudentProfileResponse:
    profile = get_student_or_404(student_id, store)
    return _to_response(student_id, profile)


@router.put(
    "/{student_id}",
    response_model=SuccessResponse,
    summary="Update student profile",
    description="Updates fields on an existing student profile.",
    responses={
        200: {"description": "Profile updated"},
        404: {"model": ErrorResponse, "description": "Student not found"},
    },
)
async def update_student(
    student_id: str,
    body: StudentUpdateRequest,
    store: Store = Depends(get_store),
) -> SuccessResponse:
    profile = get_student_or_404(student_id, store)
    updates = body.model_dump(exclude_unset=True)
    profile.update(updates)
    return SuccessResponse(message="Profile updated", data=_to_response(student_id, profile).model_dump())


@router.delete(
    "/{student_id}",
    response_model=SuccessResponse,
    summary="Delete student profile",
    description="Deletes a student profile and associated data.",
    responses={
        200: {"description": "Profile deleted"},
        404: {"model": ErrorResponse, "description": "Student not found"},
    },
)
async def delete_student(student_id: str, store: Store = Depends(get_store)) -> SuccessResponse:
    get_student_or_404(student_id, store)
    del store.student_profiles[student_id]
    store.roadmaps.pop(student_id, None)
    store.chat_histories.pop(student_id, None)
    store.progress.pop(student_id, None)
    return SuccessResponse(message="Profile deleted")


@router.post(
    "/{student_id}/progress",
    response_model=SuccessResponse,
    status_code=201,
    summary="Record learning progress",
    description="Records a study session for a student in a given week.",
    responses={
        201: {"description": "Progress recorded"},
        404: {"model": ErrorResponse, "description": "Student not found"},
    },
)
async def record_progress(
    student_id: str,
    week_number: int = Query(..., ge=1, le=52),
    completed_topics: str = Query(default="", description="Comma-separated topics"),
    hours_studied: float = Query(default=0.0, ge=0.0),
    store: Store = Depends(get_store),
) -> SuccessResponse:
    get_student_or_404(student_id, store)
    if student_id not in store.progress:
        store.progress[student_id] = {"weeks": {}, "total_hours": 0.0, "total_topics": 0}
    entry = store.progress[student_id]
    topics = [t.strip() for t in completed_topics.split(",") if t.strip()]
    entry["weeks"][str(week_number)] = {
        "completed_topics": topics,
        "hours_studied": hours_studied,
    }
    entry["total_hours"] += hours_studied
    entry["total_topics"] += len(topics)
    return SuccessResponse(
        message="Progress recorded",
        data={"week": week_number, "topics_added": len(topics), "hours": hours_studied},
    )
