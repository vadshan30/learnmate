"""Study Planner API routes for LearnMate AI.

Provides RESTful endpoints for managing study sessions, goals,
calendar views, analytics, and AI-powered schedule generation.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query

from app.dependencies import Store, get_store
from app.exceptions import LearnMateError, StudySessionNotFoundError
from app.models.study_planner import (
    AutoScheduleRequest,
    StudyGoalResponse,
    StudyGoalUpdate,
    StudySessionCreate,
    StudySessionResponse,
    StudySessionUpdate,
)
from app.schemas.responses import SuccessResponse
from app.services import study_planner_ai, study_planner_service

logger = logging.getLogger("learnmate.api.study_planner")

router = APIRouter(prefix="/api/study-planner", tags=["study-planner"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_user_id_from_query(user_id: str) -> str:
    """Extract user_id. In production this would come from JWT."""
    return user_id.strip().lower()


def _ensure_user_sessions(store: Store, user_id: str) -> list:
    """Ensure the user has a sessions list in the store."""
    if user_id not in store.study_sessions:
        store.study_sessions[user_id] = []
    return store.study_sessions[user_id]


def _find_session(store: Store, user_id: str, session_id: str) -> Dict[str, Any]:
    """Find a specific session by ID, raising 404 if not found."""
    sessions = _ensure_user_sessions(store, user_id)
    for s in sessions:
        if s.get("id") == session_id:
            return s
    raise StudySessionNotFoundError(session_id)


# ---------------------------------------------------------------------------
# CRUD Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "",
    response_model=SuccessResponse,
    summary="Get all study sessions",
    description="Returns study sessions for a user, optionally filtered by week, month, or status.",
)
async def get_sessions(
    user_id: str = Query(..., description="User ID"),
    status: Optional[str] = Query(default=None, description="Filter by status"),
    start_date: Optional[str] = Query(default=None, description="Filter from date YYYY-MM-DD"),
    end_date: Optional[str] = Query(default=None, description="Filter to date YYYY-MM-DD"),
    store: Store = Depends(get_store),
) -> SuccessResponse:
    uid = _get_user_id_from_query(user_id)
    sessions = _ensure_user_sessions(store, uid)

    if status:
        sessions = [s for s in sessions if s.get("status") == status]
    if start_date:
        sessions = [s for s in sessions if s.get("date", "") >= start_date]
    if end_date:
        sessions = [s for s in sessions if s.get("date", "") <= end_date]

    # Sort by date and start_time
    sessions.sort(key=lambda x: (x.get("date", ""), x.get("start_time", "")))

    return SuccessResponse(message="Sessions retrieved", data=sessions)


@router.post(
    "",
    response_model=SuccessResponse,
    status_code=201,
    summary="Create a study session",
    description="Creates a new study session for the user.",
)
async def create_session(
    body: StudySessionCreate,
    user_id: str = Query(..., description="User ID"),
    store: Store = Depends(get_store),
) -> SuccessResponse:
    uid = _get_user_id_from_query(user_id)
    sessions = _ensure_user_sessions(store, uid)

    session_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    session_data = {
        "id": session_id,
        "user_id": uid,
        "title": body.title.strip(),
        "description": body.description or "",
        "topic": body.topic,
        "date": body.date,
        "start_time": body.start_time,
        "end_time": body.end_time,
        "duration": body.duration or 1.0,
        "status": body.status.value,
        "priority": body.priority.value,
        "difficulty": body.difficulty.value if body.difficulty else None,
        "course_id": body.course_id,
        "project_id": body.project_id,
        "repeat_type": body.repeat_type.value,
        "reminder_minutes": body.reminder_minutes,
        "completed_at": None,
        "created_at": now,
        "updated_at": now,
    }

    sessions.append(session_data)
    await asyncio.to_thread(store.save_single_study_session, session_data)

    logger.info("Created session '%s' for user '%s'", session_id, uid)
    return SuccessResponse(message="Session created", data=session_data)


@router.put(
    "/{session_id}",
    response_model=SuccessResponse,
    summary="Update a study session",
    description="Updates an existing study session (supports drag-and-drop reschedule).",
)
async def update_session(
    session_id: str,
    body: StudySessionUpdate,
    user_id: str = Query(..., description="User ID"),
    store: Store = Depends(get_store),
) -> SuccessResponse:
    uid = _get_user_id_from_query(user_id)
    session = _find_session(store, uid, session_id)

    update_data = body.model_dump(exclude_unset=True)
    # Handle enum values
    for key in ("status", "priority", "difficulty", "repeat_type"):
        val = update_data.get(key)
        if val is not None and hasattr(val, "value"):
            update_data[key] = val.value

    session.update(update_data)
    session["updated_at"] = datetime.now(timezone.utc).isoformat()

    # Auto-recalculate duration if times changed
    if "start_time" in update_data or "end_time" in update_data:
        try:
            sh, sm = map(int, session["start_time"].split(":"))
            eh, em = map(int, session["end_time"].split(":"))
            duration = round(((eh * 60 + em) - (sh * 60 + sm)) / 60.0, 2)
            if duration > 0:
                session["duration"] = duration
        except (ValueError, KeyError):
            pass

    await asyncio.to_thread(store.save_single_study_session, session)

    logger.info("Updated session '%s' for user '%s'", session_id, uid)
    return SuccessResponse(message="Session updated", data=session)


@router.delete(
    "/{session_id}",
    response_model=SuccessResponse,
    summary="Delete a study session",
    description="Deletes a study session.",
)
async def delete_session(
    session_id: str,
    user_id: str = Query(..., description="User ID"),
    store: Store = Depends(get_store),
) -> SuccessResponse:
    uid = _get_user_id_from_query(user_id)
    sessions = _ensure_user_sessions(store, uid)

    original_len = len(sessions)
    store.study_sessions[uid] = [s for s in sessions if s.get("id") != session_id]

    if len(store.study_sessions[uid]) == original_len:
        raise StudySessionNotFoundError(session_id)

    await asyncio.to_thread(store.delete_study_session, session_id)

    logger.info("Deleted session '%s' for user '%s'", session_id, uid)
    return SuccessResponse(message="Session deleted")


@router.post(
    "/{session_id}/complete",
    response_model=SuccessResponse,
    summary="Complete a study session",
    description="Marks a study session as completed and updates progress.",
)
async def complete_session(
    session_id: str,
    user_id: str = Query(..., description="User ID"),
    store: Store = Depends(get_store),
) -> SuccessResponse:
    uid = _get_user_id_from_query(user_id)
    session = _find_session(store, uid, session_id)

    session["status"] = "completed"
    session["completed_at"] = datetime.now(timezone.utc).isoformat()
    session["updated_at"] = datetime.now(timezone.utc).isoformat()

    await asyncio.to_thread(store.save_single_study_session, session)

    logger.info("Completed session '%s' for user '%s'", session_id, uid)
    return SuccessResponse(message="Session completed", data=session)


# ---------------------------------------------------------------------------
# Calendar
# ---------------------------------------------------------------------------

@router.get(
    "/calendar",
    response_model=SuccessResponse,
    summary="Get calendar events",
    description="Returns sessions formatted as calendar events for a date range.",
)
async def get_calendar(
    user_id: str = Query(..., description="User ID"),
    start: Optional[str] = Query(default=None, description="Start date YYYY-MM-DD"),
    end: Optional[str] = Query(default=None, description="End date YYYY-MM-DD"),
    store: Store = Depends(get_store),
) -> SuccessResponse:
    uid = _get_user_id_from_query(user_id)
    sessions = _ensure_user_sessions(store, uid)

    if start:
        sessions = [s for s in sessions if s.get("date", "") >= start]
    if end:
        sessions = [s for s in sessions if s.get("date", "") <= end]

    events = study_planner_service.format_calendar_events(sessions)
    return SuccessResponse(message="Calendar events retrieved", data=events)


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------

@router.get(
    "/analytics",
    response_model=SuccessResponse,
    summary="Get study analytics",
    description="Returns comprehensive analytics for the user's study sessions.",
)
async def get_analytics(
    user_id: str = Query(..., description="User ID"),
    store: Store = Depends(get_store),
) -> SuccessResponse:
    uid = _get_user_id_from_query(user_id)
    sessions = _ensure_user_sessions(store, uid)

    analytics = study_planner_service.compute_analytics(sessions)
    return SuccessResponse(message="Analytics retrieved", data=analytics)


# ---------------------------------------------------------------------------
# Dashboard summary
# ---------------------------------------------------------------------------

@router.get(
    "/dashboard",
    response_model=SuccessResponse,
    summary="Get planner dashboard",
    description="Returns dashboard summary with planned hours, streak, and today's sessions.",
)
async def get_dashboard(
    user_id: str = Query(..., description="User ID"),
    store: Store = Depends(get_store),
) -> SuccessResponse:
    uid = _get_user_id_from_query(user_id)
    sessions = _ensure_user_sessions(store, uid)
    goal = store.study_goals.get(uid, {})
    goal_hours = goal.get("weekly_goal_hours", 10.0)

    summary = study_planner_service.get_weekly_summary(sessions, goal_hours)
    return SuccessResponse(message="Dashboard retrieved", data=summary)


# ---------------------------------------------------------------------------
# Weekly planner
# ---------------------------------------------------------------------------

@router.get(
    "/weekly",
    response_model=SuccessResponse,
    summary="Get weekly planner",
    description="Returns sessions grouped by day of the week.",
)
async def get_weekly(
    user_id: str = Query(..., description="User ID"),
    store: Store = Depends(get_store),
) -> SuccessResponse:
    uid = _get_user_id_from_query(user_id)
    sessions = _ensure_user_sessions(store, uid)

    weekly = study_planner_service.get_weekly_sessions(sessions)
    return SuccessResponse(message="Weekly planner retrieved", data=weekly)


# ---------------------------------------------------------------------------
# Auto-schedule from roadmap
# ---------------------------------------------------------------------------

@router.post(
    "/generate",
    response_model=SuccessResponse,
    summary="Generate sessions from roadmap",
    description="AI-generates study sessions based on the user's roadmap and preferences.",
)
async def generate_schedule(
    body: AutoScheduleRequest,
    user_id: str = Query(..., description="User ID"),
    store: Store = Depends(get_store),
) -> SuccessResponse:
    uid = _get_user_id_from_query(user_id)
    roadmap = store.roadmaps.get(uid)
    if not roadmap:
        raise LearnMateError(
            message="No roadmap found. Generate a roadmap first.",
            error_code="ROADMAP_NOT_FOUND",
            status_code=404,
        )

    generated = await study_planner_ai.generate_sessions_from_roadmap(
        roadmap=roadmap,
        weekly_hours=body.weekly_hours,
        preferred_days=body.preferred_days,
        start_date=body.start_date,
    )

    # Convert generated sessions to full session objects and store them
    sessions = _ensure_user_sessions(store, uid)
    now = datetime.now(timezone.utc).isoformat()

    new_sessions = []
    for g in generated:
        session_id = str(uuid.uuid4())
        session_data = {
            "id": session_id,
            "user_id": uid,
            "title": g.get("title", "Study Session"),
            "description": "",
            "topic": g.get("topic"),
            "date": g.get("date", ""),
            "start_time": g.get("start_time", "18:00"),
            "end_time": g.get("end_time", "20:00"),
            "duration": g.get("duration", 2.0),
            "status": "scheduled",
            "priority": g.get("priority", "medium"),
            "difficulty": g.get("difficulty"),
            "course_id": None,
            "project_id": None,
            "repeat_type": "none",
            "reminder_minutes": 15,
            "completed_at": None,
            "created_at": now,
            "updated_at": now,
        }
        sessions.append(session_data)
        new_sessions.append(session_data)

    # Persist all sessions
    await asyncio.to_thread(store.save_study_sessions, uid)

    logger.info("Generated %d sessions for user '%s'", len(new_sessions), uid)
    return SuccessResponse(
        message=f"Generated {len(new_sessions)} study sessions",
        data=new_sessions,
    )


# ---------------------------------------------------------------------------
# Study Goal
# ---------------------------------------------------------------------------

@router.get(
    "/goal",
    response_model=SuccessResponse,
    summary="Get study goal",
    description="Returns the user's weekly study goal.",
)
async def get_goal(
    user_id: str = Query(..., description="User ID"),
    store: Store = Depends(get_store),
) -> SuccessResponse:
    uid = _get_user_id_from_query(user_id)
    goal = store.study_goals.get(uid)

    if not goal:
        goal = {
            "user_id": uid,
            "weekly_goal_hours": 10.0,
            "daily_goal_minutes": None,
            "preferred_study_time": None,
            "preferred_days": [],
        }

    return SuccessResponse(message="Goal retrieved", data=goal)


@router.put(
    "/goal",
    response_model=SuccessResponse,
    summary="Update study goal",
    description="Sets or updates the user's weekly study goal.",
)
async def update_goal(
    body: StudyGoalUpdate,
    user_id: str = Query(..., description="User ID"),
    store: Store = Depends(get_store),
) -> SuccessResponse:
    uid = _get_user_id_from_query(user_id)

    goal_data = {
        "user_id": uid,
        "weekly_goal_hours": body.weekly_goal_hours,
        "daily_goal_minutes": body.daily_goal_minutes,
        "preferred_study_time": body.preferred_study_time,
        "preferred_days": body.preferred_days or [],
    }

    store.study_goals[uid] = goal_data
    await asyncio.to_thread(store.save_study_goal, uid)

    logger.info("Updated study goal for user '%s': %.1f hrs/week", uid, body.weekly_goal_hours)
    return SuccessResponse(message="Goal updated", data=goal_data)


# ---------------------------------------------------------------------------
# Streak
# ---------------------------------------------------------------------------

@router.get(
    "/streak",
    response_model=SuccessResponse,
    summary="Get study streak",
    description="Returns current and longest study streaks.",
)
async def get_streak(
    user_id: str = Query(..., description="User ID"),
    store: Store = Depends(get_store),
) -> SuccessResponse:
    uid = _get_user_id_from_query(user_id)
    sessions = _ensure_user_sessions(store, uid)

    current, longest = study_planner_service.calculate_streak(sessions)
    return SuccessResponse(
        message="Streak retrieved",
        data={"current_streak": current, "longest_streak": longest},
    )


# ---------------------------------------------------------------------------
# AI Recommendations
# ---------------------------------------------------------------------------

@router.post(
    "/optimize",
    response_model=SuccessResponse,
    summary="Get AI schedule optimization",
    description="Uses Gemini to analyze schedule and provide optimization tips.",
)
async def optimize_schedule(
    user_id: str = Query(..., description="User ID"),
    store: Store = Depends(get_store),
) -> SuccessResponse:
    uid = _get_user_id_from_query(user_id)
    sessions = _ensure_user_sessions(store, uid)
    goal = store.study_goals.get(uid, {})
    profile = store.student_profiles.get(uid, {})

    recommendations = await study_planner_ai.optimize_schedule(
        sessions=sessions,
        goal_hours=goal.get("weekly_goal_hours", 10.0),
        student_context=f"Career goal: {profile.get('career_goal', 'N/A')}",
    )

    return SuccessResponse(message="Recommendations generated", data={"recommendations": recommendations})


@router.get(
    "/daily-tip",
    response_model=SuccessResponse,
    summary="Get daily learning tip",
    description="Returns a personalized daily learning recommendation.",
)
async def daily_tip(
    user_id: str = Query(..., description="User ID"),
    store: Store = Depends(get_store),
) -> SuccessResponse:
    uid = _get_user_id_from_query(user_id)
    sessions = _ensure_user_sessions(store, uid)
    profile = store.student_profiles.get(uid, {})
    progress = store.progress.get(uid)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    upcoming = [s for s in sessions if s.get("date", "") >= today and s.get("status") != "completed"][:3]

    tip = await study_planner_ai.get_daily_recommendation(profile, progress, upcoming)
    return SuccessResponse(message="Daily tip", data={"tip": tip})
