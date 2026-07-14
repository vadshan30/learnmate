from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class StudentCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Student full name")
    current_skills: List[str] = Field(default_factory=list, description="Skills already acquired")
    interests: List[str] = Field(default_factory=list, description="Area of interest")
    career_goal: str = Field(default="", description="Target career role")
    skill_level: str = Field(default="beginner", pattern="^(beginner|intermediate|advanced)$")
    completed_topics: List[str] = Field(default_factory=list)
    learning_style: Optional[str] = Field(default=None, description="Preferred learning style")
    hours_per_week: Optional[float] = Field(default=None, ge=1.0, le=60.0)
    email: Optional[str] = Field(default=None, description="Email address")
    preferred_study_time: Optional[str] = Field(default=None, description="morning|afternoon|evening|night")
    preferred_job_role: Optional[str] = Field(default=None, description="Preferred job role")
    dream_company: Optional[str] = Field(default=None, description="Dream company to work at")
    current_goals: List[str] = Field(default_factory=list, description="Current goals checklist")
    experience_level: Optional[str] = Field(default=None, description="student|fresher|intern|working-professional")
    github_url: Optional[str] = Field(default=None, description="GitHub profile URL")
    linkedin_url: Optional[str] = Field(default=None, description="LinkedIn profile URL")


class StudentUpdateRequest(BaseModel):
    current_skills: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    career_goal: Optional[str] = None
    skill_level: Optional[str] = Field(default=None, pattern="^(beginner|intermediate|advanced)$")
    completed_topics: Optional[List[str]] = None
    learning_style: Optional[str] = None
    hours_per_week: Optional[float] = Field(default=None, ge=1.0, le=60.0)
    email: Optional[str] = None
    preferred_study_time: Optional[str] = None
    preferred_job_role: Optional[str] = None
    dream_company: Optional[str] = None
    current_goals: Optional[List[str]] = None
    experience_level: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None


class RoadmapGenerateRequest(BaseModel):
    student_id: str = Field(..., min_length=1, description="Student identifier (lowercase name)")
    weeks: int = Field(default=12, ge=1, le=52, description="Roadmap duration in weeks")
    hours_per_week: float = Field(default=10.0, ge=1.0, le=60.0)
    focus_area: Optional[str] = Field(default=None, description="Specific area to focus on")


class ProgressUpdateRequest(BaseModel):
    student_id: str = Field(..., min_length=1)
    week_number: int = Field(..., ge=1, le=52)
    completed_topics: List[str] = Field(default_factory=list)
    hours_studied: float = Field(default=0.0, ge=0.0)
    notes: Optional[str] = None
    rating: Optional[int] = Field(default=None, ge=1, le=5)


class ChatRequest(BaseModel):
    student_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1, max_length=2000)
    history: List[Dict[str, str]] = Field(default_factory=list, description="Prior chat turns")


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=5, ge=1, le=20)
    skill_filter: Optional[str] = None


class TopicCompleteRequest(BaseModel):
    student_id: str = Field(..., min_length=1)
    topic_name: str = Field(..., min_length=1, description="Topic name to mark complete")
    completed: bool = Field(default=True, description="Completion state")


class ProgressUpdateBody(BaseModel):
    completed_topics: List[str] = Field(default_factory=list, description="Topics to mark as completed")
    hours_studied: float = Field(default=0.0, ge=0.0)
