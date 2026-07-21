"""Learning roadmap data models for LearnMate AI.

Defines the structured entities for courses, projects, certifications,
weekly learning plans, and the full personalized roadmap.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Supporting Enums
# ---------------------------------------------------------------------------


class DifficultyLevel(str, Enum):
    """Difficulty rating for courses, projects, and certifications."""

    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class TopicCompletion(BaseModel):
    """Tracks completion state for a single topic within a week.

    Attributes:
        topic_id: Unique identifier for the topic (e.g. "week-3-topic-0").
        topic_name: Human-readable topic name.
        completed: Whether the topic has been completed.
        completed_at: ISO timestamp when completed, or None.
        week_number: The week this topic belongs to.
    """

    topic_id: str = Field(..., description="Unique topic identifier")
    topic_name: str = Field(..., description="Human-readable topic name")
    completed: bool = Field(default=False, description="Completion state")
    completed_at: Optional[str] = Field(default=None, description="ISO timestamp of completion")
    week_number: int = Field(default=1, ge=1, description="Parent week number")


class WeekProgress(BaseModel):
    """Tracks progress for a single week.

    Attributes:
        week_number: The week number (1-indexed).
        completed: Whether all topics in this week are done.
        total_topics: Total topics in this week.
        completed_topics_count: How many topics are done.
        percentage: Completion percentage for this week.
        status: One of 'pending', 'in_progress', 'completed'.
    """

    week_number: int = Field(..., ge=1, description="Week number")
    completed: bool = Field(default=False, description="All topics done")
    total_topics: int = Field(default=0, ge=0, description="Total topics")
    completed_topics_count: int = Field(default=0, ge=0, description="Completed topics")
    percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Week completion %")
    status: str = Field(default="pending", description="pending|in_progress|completed")


class RoadmapProgress(BaseModel):
    """Tracks the student's progress through a generated roadmap.

    Attributes:
        completed_weeks: Number of weeks fully completed.
        total_weeks: Total weeks in the roadmap.
        percentage: Completion percentage (0-100).
        current_week: The week the student is currently on.
        total_topics: Total topics across all weeks.
        completed_topics_count: Number of completed topics.
        week_progress: Per-week progress breakdown.
        completion_status: Overall status string.
    """

    completed_weeks: int = Field(default=0, ge=0, description="Weeks finished")
    total_weeks: int = Field(default=10, ge=1, description="Total weeks in plan")
    percentage: float = Field(
        default=0.0, ge=0.0, le=100.0, description="Completion percentage"
    )
    current_week: int = Field(default=1, ge=1, description="Current active week")
    total_topics: int = Field(default=0, ge=0, description="Total topics across all weeks")
    completed_topics_count: int = Field(default=0, ge=0, description="Completed topics")
    week_progress: List[WeekProgress] = Field(
        default_factory=list, description="Per-week progress"
    )
    completion_status: str = Field(default="not_started", description="not_started|in_progress|completed")


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
    provider: str = Field(default="", description="Course provider or platform")
    url: str = Field(default="", description="Course URL")
    prerequisites: List[str] = Field(
        default_factory=list, description="Prerequisites (IDs or skill names)"
    )
    skills_gained: List[str] = Field(
        default_factory=list, description="Skills gained on completion"
    )
    tags: List[str] = Field(
        default_factory=list, description="Searchable tags"
    )
    category: str = Field(default="", description="Course category (alias for domain)")


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


class Book(BaseModel):
    """Represents a free programming book from GoalKicker.

    Attributes:
        id: Unique book identifier.
        title: Book title.
        category: Always 'Books'.
        language: Programming language or subject.
        provider: Book provider or publisher.
        free: Whether the book is free.
        description: Book description.
        url: URL to the book page.
        domain: Domain category.
        level: Difficulty level.
        tags: Searchable tags.
        skills_covered: Skills covered by the book.
    """

    id: str = Field(default="", description="Unique book identifier")
    title: str = Field(..., min_length=1, description="Book title")
    category: str = Field(default="Books", description="Resource category")
    language: str = Field(default="", description="Programming language or subject")
    provider: str = Field(default="", description="Book provider or publisher")
    free: bool = Field(default=True, description="Whether the book is free")
    description: str = Field(default="", description="Book description")
    url: str = Field(default="", description="URL to the book page")
    domain: str = Field(default="", description="Domain category")
    level: str = Field(default="All Levels", description="Difficulty level")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    skills_covered: List[str] = Field(default_factory=list, description="Skills covered")


class Certification(BaseModel):
    """Represents an industry certification the student may pursue.

    Attributes:
        id: Unique certification identifier.
        name: Official certification name.
        provider: Issuing organization.
        level: Difficulty / experience level.
        category: Certification category (e.g. "Cloud Computing").
        description: Overview of the certification.
        duration: Estimated study/prep time.
        exam_fee: Cost of the exam.
        validity: How long the certification is valid.
        prerequisites: Requirements before attempting.
        exam_link: URL to the official exam page.
        skills_covered: Skills validated by this certification.
        learning_outcomes: What the learner will gain.
        official_badge: Badge name or image URL.
        recommended_courses: Course IDs recommended as preparation.
        career_roles: Job roles this certification supports.
    """

    id: str = Field(default="", description="Unique certification identifier")
    name: str = Field(..., min_length=1, description="Certification name")
    provider: str = Field(..., min_length=1, description="Issuing organization")
    level: DifficultyLevel = Field(
        default=DifficultyLevel.BEGINNER, description="Certification level"
    )
    category: str = Field(default="", description="Certification category")
    description: str = Field(default="", description="Description")
    duration: str = Field(default="", description="Estimated study/prep time")
    exam_fee: str = Field(default="", description="Exam fee")
    validity: str = Field(default="", description="Certification validity period")
    prerequisites: List[str] = Field(
        default_factory=list, description="Prerequisites"
    )
    exam_link: str = Field(default="", description="Official exam URL")
    skills_covered: List[str] = Field(
        default_factory=list, description="Skills covered"
    )
    learning_outcomes: List[str] = Field(
        default_factory=list, description="Learning outcomes"
    )
    official_badge: str = Field(default="", description="Official badge name")
    recommended_courses: List[str] = Field(
        default_factory=list, description="Recommended course IDs"
    )
    career_roles: List[str] = Field(
        default_factory=list, description="Career roles"
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
    completion_status: str = Field(default="pending", description="pending|in_progress|completed")
    completed: bool = Field(default=False, description="Whether this week is fully completed")
    learning_outcomes: List[str] = Field(
        default_factory=list, description="Learning outcomes for this week"
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
    recommendations: List[str] = Field(
        default_factory=list, description="Learning recommendations"
    )
