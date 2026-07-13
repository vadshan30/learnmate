"""Learning roadmap data models for LearnMate AI.

Defines the structured entities for courses, projects, certifications,
weekly learning plans, and the full personalized roadmap.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Supporting Enums
# ---------------------------------------------------------------------------


class DifficultyLevel(str, Enum):
    """Difficulty rating for courses, projects, and certifications."""

    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class RoadmapProgress(BaseModel):
    """Tracks the student's progress through a generated roadmap.

    Attributes:
        completed_weeks: Number of weeks fully completed.
        total_weeks: Total weeks in the roadmap.
        percentage: Completion percentage (0-100).
        current_week: The week the student is currently on.
    """

    completed_weeks: int = Field(default=0, ge=0, description="Weeks finished")
    total_weeks: int = Field(default=10, ge=1, description="Total weeks in plan")
    percentage: float = Field(
        default=0.0, ge=0.0, le=100.0, description="Completion percentage"
    )
    current_week: int = Field(default=1, ge=1, description="Current active week")


# ---------------------------------------------------------------------------
# Core Content Models
# ---------------------------------------------------------------------------


class Course(BaseModel):
    """Represents a single learning course available in the platform catalog.

    Attributes:
        id: Unique identifier for the course.
        title: Short descriptive title.
        domain: High-level domain category (e.g. "Data Science").
        description: Detailed course description.
        duration: Human-readable duration string.
        level: Difficulty level of the course.
        prerequisites: List of course IDs or skill names required beforehand.
        skills_gained: Skills the learner will acquire upon completion.
        tags: Searchable tags for filtering and recommendation.
    """

    id: str = Field(..., min_length=1, description="Unique course identifier")
    title: str = Field(..., min_length=1, description="Course title")
    domain: str = Field(..., min_length=1, description="Domain category")
    description: str = Field(default="", description="Detailed description")
    duration: str = Field(default="", description="Duration string, e.g. '4 weeks'")
    level: DifficultyLevel = Field(
        default=DifficultyLevel.BEGINNER, description="Difficulty level"
    )
    prerequisites: List[str] = Field(
        default_factory=list, description="Prerequisites (IDs or skill names)"
    )
    skills_gained: List[str] = Field(
        default_factory=list, description="Skills gained on completion"
    )
    tags: List[str] = Field(
        default_factory=list, description="Searchable tags"
    )


class Project(BaseModel):
    """Represents a hands-on portfolio project.

    Attributes:
        id: Unique project identifier.
        title: Short project title.
        description: What the project involves.
        domain: Domain area of the project.
        difficulty: Difficulty rating.
        estimated_time: Human-readable time estimate.
        required_skills: Skills needed to complete the project.
        learning_outcomes: What the student will learn.
        technologies: Technologies and tools used.
    """

    id: str = Field(default="", description="Unique project identifier")
    title: str = Field(..., min_length=1, description="Project title")
    description: str = Field(default="", description="Project description")
    domain: str = Field(default="", description="Domain area")
    difficulty: DifficultyLevel = Field(
        default=DifficultyLevel.BEGINNER, description="Difficulty rating"
    )
    estimated_time: str = Field(
        default="", description="Estimated completion time"
    )
    required_skills: List[str] = Field(
        default_factory=list, description="Skills required"
    )
    learning_outcomes: List[str] = Field(
        default_factory=list, description="Learning outcomes"
    )
    technologies: List[str] = Field(
        default_factory=list, description="Technologies used"
    )


class Certification(BaseModel):
    """Represents an industry certification the student may pursue.

    Attributes:
        id: Unique certification identifier.
        name: Official certification name.
        provider: Issuing organization.
        level: Difficulty / experience level.
        description: Overview of the certification.
        prerequisites: Requirements before attempting.
        exam_link: URL to the official exam page.
        skills_covered: Skills validated by this certification.
    """

    id: str = Field(default="", description="Unique certification identifier")
    name: str = Field(..., min_length=1, description="Certification name")
    provider: str = Field(..., min_length=1, description="Issuing organization")
    level: DifficultyLevel = Field(
        default=DifficultyLevel.BEGINNER, description="Certification level"
    )
    description: str = Field(default="", description="Description")
    prerequisites: List[str] = Field(
        default_factory=list, description="Prerequisites"
    )
    exam_link: str = Field(default="", description="Official exam URL")
    skills_covered: List[str] = Field(
        default_factory=list, description="Skills covered"
    )


# ---------------------------------------------------------------------------
# Weekly Plan & Full Roadmap
# ---------------------------------------------------------------------------


class LearningWeek(BaseModel):
    """A single week within a personalized learning roadmap.

    Attributes:
        week_number: 1-indexed week position.
        title: Descriptive title for the week.
        topics: Specific topics or sub-topics to study.
        projects: Projects assigned during this week.
        assessments: Quizzes, exercises, or review tasks.
        estimated_hours: Approximate study hours for the week.
    """

    week_number: int = Field(..., ge=1, le=52, description="Week number (1-indexed)")
    title: str = Field(default="", description="Week title")
    topics: List[str] = Field(default_factory=list, description="Topics to study")
    projects: List[str] = Field(
        default_factory=list, description="Projects for this week"
    )
    assessments: List[str] = Field(
        default_factory=list, description="Assessments or exercises"
    )
    estimated_hours: float = Field(
        default=10.0, ge=0.0, description="Estimated study hours"
    )


class LearningRoadmap(BaseModel):
    """A complete personalized learning roadmap generated for a student.

    Attributes:
        roadmap_id: Unique roadmap identifier.
        student_name: Name of the student this roadmap belongs to.
        career_goal: Target career role driving the roadmap.
        total_duration: Human-readable total duration (e.g. "10 weeks").
        weeks: Ordered list of weekly learning plans.
        certifications: Recommended certifications to pursue.
        final_project: Capstone project at the end of the roadmap.
        progress: Tracks completion status.
    """

    roadmap_id: str = Field(..., description="Unique roadmap identifier")
    student_name: str = Field(..., min_length=1, description="Student name")
    career_goal: str = Field(..., min_length=1, description="Target career goal")
    total_duration: str = Field(
        default="10 weeks", description="Total roadmap duration"
    )
    weeks: List[LearningWeek] = Field(
        default_factory=list, description="Weekly learning plans"
    )
    certifications: List[Certification] = Field(
        default_factory=list, description="Recommended certifications"
    )
    final_project: Optional[Project] = Field(
        default=None, description="Capstone project"
    )
    progress: RoadmapProgress = Field(
        default_factory=RoadmapProgress, description="Progress tracker"
    )
