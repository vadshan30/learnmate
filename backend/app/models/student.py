"""Student profile data model for LearnMate AI.

Defines the core student entity used across profile creation,
skill-gap analysis, and personalized roadmap generation.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class SkillLevel(str, Enum):
    """Enumeration of supported skill proficiency levels."""

    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class StudentProfile(BaseModel):
    """Represents a learner's profile within the LearnMate AI platform.

    Attributes:
        name: Full name of the student.
        current_skills: Skills the student already possesses.
        interests: Topic domains the student is passionate about.
        career_goal: Target professional role the student is working toward.
        skill_level: Self-assessed overall proficiency level.
        completed_topics: List of topic identifiers already mastered.
        progress_percentage: Overall completion percentage (0-100).
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Full name of the student",
        examples=["Alice Johnson"],
    )
    current_skills: List[str] = Field(
        default_factory=list,
        description="Skills the student already has",
        examples=[["Python", "Git", "SQL"]],
    )
    interests: List[str] = Field(
        default_factory=list,
        description="Domain interests of the student",
        examples=[["Artificial Intelligence", "Machine Learning"]],
    )
    career_goal: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Target career role",
        examples=["ML Engineer"],
    )
    skill_level: SkillLevel = Field(
        default=SkillLevel.BEGINNER,
        description="Self-assessed skill level",
    )
    completed_topics: List[str] = Field(
        default_factory=list,
        description="Topics the student has already completed",
        examples=[["Variables", "Loops"]],
    )
    progress_percentage: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Overall progress percentage (0-100)",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Alice",
                    "current_skills": ["Python", "Git"],
                    "interests": ["AI", "Machine Learning"],
                    "career_goal": "ML Engineer",
                    "skill_level": "Beginner",
                    "completed_topics": ["Variables", "Loops"],
                    "progress_percentage": 20.0,
                }
            ]
        }
    }

    @field_validator("name")
    @classmethod
    def name_must_be_non_empty(cls, value: str) -> str:
        """Strip whitespace and ensure name is not empty after stripping."""
        stripped = value.strip()
        if not stripped:
            raise ValueError("Student name cannot be empty or whitespace only")
        return stripped

    @field_validator("career_goal")
    @classmethod
    def career_goal_must_be_non_empty(cls, value: str) -> str:
        """Strip whitespace and ensure career goal is meaningful."""
        stripped = value.strip()
        if not stripped:
            raise ValueError("Career goal cannot be empty or whitespace only")
        return stripped
