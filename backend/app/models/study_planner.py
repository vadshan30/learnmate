"""Study Planner data models for LearnMate AI.

Defines Pydantic schemas for study sessions, study goals,
calendar events, analytics, and related request/response payloads.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SessionStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    MISSED = "missed"


class SessionPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SessionDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class RepeatType(str, Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class StudySessionCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Session title")
    description: str = Field(default="", max_length=2000, description="Session description")
    topic: Optional[str] = Field(default=None, max_length=200, description="Related topic")
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Date YYYY-MM-DD")
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Start time HH:MM")
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="End time HH:MM")
    duration: Optional[float] = Field(default=None, ge=0.25, le=12.0, description="Duration in hours (auto-calculated if omitted)")
    status: SessionStatus = Field(default=SessionStatus.SCHEDULED)
    priority: SessionPriority = Field(default=SessionPriority.MEDIUM)
    difficulty: Optional[SessionDifficulty] = None
    course_id: Optional[str] = Field(default=None, max_length=100)
    project_id: Optional[str] = Field(default=None, max_length=100)
    repeat_type: RepeatType = Field(default=RepeatType.NONE)
    reminder_minutes: Optional[int] = Field(default=15, ge=0, le=1440, description="Reminder minutes before start")

    @field_validator("title")
    @classmethod
    def title_must_be_non_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Title cannot be empty")
        return stripped

    def model_post_init(self, __context: Any) -> None:
        if self.duration is None:
            try:
                sh, sm = map(int, self.start_time.split(":"))
                eh, em = map(int, self.end_time.split(":"))
                self.duration = round(((eh * 60 + em) - (sh * 60 + sm)) / 60.0, 2)
                if self.duration <= 0:
                    self.duration = 1.0
            except (ValueError, AttributeError):
                self.duration = 1.0


class StudySessionUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    topic: Optional[str] = Field(default=None, max_length=200)
    date: Optional[str] = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    start_time: Optional[str] = Field(default=None, pattern=r"^\d{2}:\d{2}$")
    end_time: Optional[str] = Field(default=None, pattern=r"^\d{2}:\d{2}$")
    duration: Optional[float] = Field(default=None, ge=0.25, le=12.0)
    status: Optional[SessionStatus] = None
    priority: Optional[SessionPriority] = None
    difficulty: Optional[SessionDifficulty] = None
    course_id: Optional[str] = Field(default=None, max_length=100)
    project_id: Optional[str] = Field(default=None, max_length=100)
    repeat_type: Optional[RepeatType] = None
    reminder_minutes: Optional[int] = Field(default=None, ge=0, le=1440)


class StudyGoalUpdate(BaseModel):
    weekly_goal_hours: float = Field(..., ge=1.0, le=60.0, description="Weekly study goal in hours")
    daily_goal_minutes: Optional[int] = Field(default=None, ge=5, le=720)
    preferred_study_time: Optional[str] = Field(default=None, pattern=r"^(morning|afternoon|evening|night)$")
    preferred_days: Optional[List[str]] = Field(default=None, description="Preferred study days")


class AutoScheduleRequest(BaseModel):
    weekly_hours: float = Field(default=10.0, ge=1.0, le=60.0)
    preferred_days: List[str] = Field(default_factory=lambda: ["Monday", "Wednesday", "Friday"])
    start_date: Optional[str] = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class StudySessionResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: str = ""
    topic: Optional[str] = None
    date: str
    start_time: str
    end_time: str
    duration: float
    status: str
    priority: str
    difficulty: Optional[str] = None
    course_id: Optional[str] = None
    project_id: Optional[str] = None
    repeat_type: str = "none"
    reminder_minutes: Optional[int] = None
    completed_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class StudyGoalResponse(BaseModel):
    id: Optional[int] = None
    user_id: str
    weekly_goal_hours: float
    daily_goal_minutes: Optional[int] = None
    preferred_study_time: Optional[str] = None
    preferred_days: List[str] = Field(default_factory=list)


class StudyPlannerDashboard(BaseModel):
    planned_hours_this_week: float = 0.0
    weekly_goal_hours: float = 10.0
    weekly_goal_progress: float = 0.0
    current_streak: int = 0
    sessions_completed: int = 0
    sessions_total: int = 0
    today_sessions: List[StudySessionResponse] = Field(default_factory=list)
    upcoming_sessions: List[StudySessionResponse] = Field(default_factory=list)


class StudyAnalytics(BaseModel):
    weekly_hours: float = 0.0
    monthly_hours: float = 0.0
    average_session_length: float = 0.0
    completion_rate: float = 0.0
    most_studied_topic: Optional[str] = None
    favorite_study_time: Optional[str] = None
    current_streak: int = 0
    longest_streak: int = 0
    total_sessions: int = 0
    completed_sessions: int = 0
    weekly_hours_history: List[Dict[str, Any]] = Field(default_factory=list)
    monthly_hours_history: List[Dict[str, Any]] = Field(default_factory=list)
    status_distribution: Dict[str, int] = Field(default_factory=dict)


class CalendarEvent(BaseModel):
    id: str
    title: str
    start: str  # ISO datetime
    end: str    # ISO datetime
    status: str
    priority: str
    topic: Optional[str] = None
