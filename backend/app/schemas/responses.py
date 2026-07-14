from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    rag_available: bool = False
    watsonx_available: bool = False
    services: Dict[str, str] = Field(default_factory=dict)


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
    source: str = "watsonx"


class ChatResponse(BaseModel):
    student_id: str
    response: str
    source: str = "watsonx"
    mentor_type: str = "general"


class ProgressResponse(BaseModel):
    student_id: str
    progress: Dict[str, Any] = Field(default_factory=dict)
    message: str = ""


class SuccessResponse(BaseModel):
    success: bool = True
    message: str = ""
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: str
    details: Optional[Any] = None
