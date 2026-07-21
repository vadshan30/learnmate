"""Career Aptitude Test data models for LearnMate AI."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CareerOption(BaseModel):
    id: str = Field(..., description="Career identifier")
    name: str = Field(..., description="Career display name")
    description: str = Field(default="", description="Brief career description")
    skills: List[str] = Field(default_factory=list, description="Key skills for this career")


class AnswerOption(BaseModel):
    id: str = Field(..., description="Answer identifier (a, b, c, d)")
    text: str = Field(..., description="Answer display text")
    scores: Dict[str, int] = Field(default_factory=dict, description="Career score increments")


class Question(BaseModel):
    id: int = Field(..., description="Question number")
    text: str = Field(..., description="Question text")
    category: str = Field(default="", description="Question category")
    options: List[AnswerOption] = Field(..., description="Answer choices")


class TestSubmission(BaseModel):
    answers: Dict[str, str] = Field(..., description="question_id -> answer_id mapping")


class CareerScore(BaseModel):
    career_id: str = Field(..., description="Career identifier")
    career_name: str = Field(..., description="Career display name")
    score: float = Field(..., description="Raw score")
    percentage: float = Field(..., description="Normalized percentage 0-100")
    explanation: str = Field(default="", description="AI-generated explanation")


class CareerTestResult(BaseModel):
    id: str = Field(default="", description="Result ID")
    user_id: str = Field(default="", description="User ID")
    top_careers: List[CareerScore] = Field(default_factory=list, description="Top 3 career matches")
    all_scores: List[CareerScore] = Field(default_factory=list, description="All career scores")
    answers: Dict[str, str] = Field(default_factory=dict, description="Submitted answers")
    ai_explanation: Dict[str, Any] = Field(default_factory=dict, description="Gemini AI analysis")
    created_at: str = Field(default="", description="ISO timestamp")
