from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "2.0.0"
    backend: str = "online"
    database: str = "online"
    gemini: str = "disabled"
    rag: str = "disabled"
    services: Dict[str, str] = Field(default_factory=dict)
    environment: str = "development"
    python_version: Optional[str] = None
    database_type: Optional[str] = None
    database_size_kb: Optional[float] = None
    indexed_documents: Optional[int] = None
    server_uptime_seconds: Optional[float] = None
    operating_system: Optional[str] = None


class StudentProfileResponse(BaseModel):
    student_id: str
    name: str
    current_skills: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    career_goal: str = ""
    skill_level: str = "beginner"
    completed_topics: List[str] = Field(default_factory=list)
    progress_percentage: float = 0.0
    learning_style: Optional[str] = None
    hours_per_week: Optional[float] = None
    email: Optional[str] = None
    preferred_study_time: Optional[str] = None
    preferred_job_role: Optional[str] = None
    dream_company: Optional[str] = None
    current_goals: List[str] = Field(default_factory=list)
    experience_level: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None


class RoadmapResponse(BaseModel):
    student_id: str
    roadmap: Optional[Dict[str, Any]] = None
    fallback: bool = False
    source: str = "gemini"


class SuccessResponse(BaseModel):
    success: bool = True
    message: str = ""
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: str
    details: Optional[Any] = None
