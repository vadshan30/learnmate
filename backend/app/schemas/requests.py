from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


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

    @field_validator("current_skills", "interests", "current_goals", mode="before")
    @classmethod
    def deduplicate_list(cls, v: List[str]) -> List[str]:
        if not v:
            return []
        seen = set()
        result = []
        for item in v:
            key = item.strip().lower()
            if key not in seen:
                seen.add(key)
                result.append(item.strip())
        return result

    @field_validator("name")
    @classmethod
    def name_must_be_non_empty(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Name cannot be empty or whitespace only")
        return stripped

    @field_validator("career_goal")
    @classmethod
    def career_goal_must_be_non_empty(cls, value: str) -> str:
        return value.strip() if value else value


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

    @field_validator("current_skills", "interests", "current_goals", mode="before")
    @classmethod
    def deduplicate_list(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is None:
            return v
        if not v:
            return []
        seen = set()
        result = []
        for item in v:
            key = item.strip().lower()
            if key not in seen:
                seen.add(key)
                result.append(item.strip())
        return result

    @field_validator("career_goal")
    @classmethod
    def career_goal_must_be_non_empty(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return value.strip()


class RoadmapGenerateRequest(BaseModel):
    student_id: str = Field(..., min_length=1, description="Student identifier (lowercase name)")
    weeks: int = Field(default=12, ge=1, le=52, description="Roadmap duration in weeks")
    hours_per_week: float = Field(default=10.0, ge=1.0, le=60.0)
    focus_area: Optional[str] = Field(default=None, description="Specific area to focus on")


class TopicCompleteRequest(BaseModel):
    student_id: str = Field(..., min_length=1)
    topic_name: str = Field(..., min_length=1, description="Topic name to mark complete")
    completed: bool = Field(default=True, description="Completion state")


class ProgressUpdateBody(BaseModel):
    completed_topics: List[str] = Field(default_factory=list, description="Topics to mark as completed")
    hours_studied: float = Field(default=0.0, ge=0.0)


# ---------------------------------------------------------------------------
# Mentor-specific request schemas
# ---------------------------------------------------------------------------


class MentorQuizRequest(BaseModel):
    student_id: str = Field(..., min_length=1)
    topic: str = Field(..., min_length=1, max_length=200, description="Quiz topic")
    num_questions: int = Field(default=5, ge=1, le=20, description="Number of questions")
    difficulty: Optional[str] = Field(default=None, pattern="^(beginner|intermediate|advanced)$")


class MentorExplainRequest(BaseModel):
    student_id: str = Field(..., min_length=1)
    concept: str = Field(..., min_length=1, max_length=200, description="Concept to explain")
    level: Optional[str] = Field(default=None, pattern="^(beginner|intermediate|advanced)$")


class MentorStudyPlanRequest(BaseModel):
    student_id: str = Field(..., min_length=1)
    context: str = Field(..., min_length=1, max_length=1000, description="Study plan context/requirements")


class MentorRevisionRequest(BaseModel):
    student_id: str = Field(..., min_length=1)
    topics: List[str] = Field(..., min_length=1, description="Topics to revise")
    exam_date: Optional[str] = Field(default=None, description="Target exam date (YYYY-MM-DD)")
    focus_areas: Optional[List[str]] = Field(default=None, description="Specific focus areas")


class MentorCareerRequest(BaseModel):
    student_id: str = Field(..., min_length=1)
    question: str = Field(..., min_length=1, max_length=1000, description="Career-related question")


class MentorFlashcardRequest(BaseModel):
    student_id: str = Field(..., min_length=1)
    topic: str = Field(..., min_length=1, max_length=200, description="Flashcard topic")
    num_cards: int = Field(default=10, ge=1, le=50, description="Number of flashcards")


class MentorCodingChallengeRequest(BaseModel):
    student_id: str = Field(..., min_length=1)
    topic: str = Field(..., min_length=1, max_length=200, description="Challenge topic")
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")
    language: str = Field(default="Python", max_length=50)


class MentorResumeReviewRequest(BaseModel):
    student_id: str = Field(..., min_length=1)
    resume_text: str = Field(..., min_length=10, max_length=10000, description="Resume content")
    target_role: str = Field(default="", max_length=200)


class MentorInterviewPrepRequest(BaseModel):
    student_id: str = Field(..., min_length=1)
    role: str = Field(..., min_length=1, max_length=200, description="Target job role")
    num_questions: int = Field(default=5, ge=1, le=20)
    focus: str = Field(default="mixed", pattern="^(technical|behavioral|mixed)$")
