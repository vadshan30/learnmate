"""Reusable prompt templates for LearnMate AI Gemini integration.

Provides modular, reusable prompt builders for different AI features.
Each template is designed to work with Gemini's instruction-following
capabilities and produces structured, parseable output.
"""

from app.services.prompts.mentor_prompt import (
    build_explain_prompt,
)
from app.services.prompts.career_prompt import (
    build_career_advice_prompt,
    build_career_transition_prompt,
)
from app.services.prompts.quiz_prompt import (
    build_quiz_generation_prompt,
    build_flashcard_prompt,
    build_coding_challenge_prompt,
)
from app.services.prompts.roadmap_prompt import (
    build_roadmap_generation_prompt,
    build_study_plan_prompt,
    build_revision_schedule_prompt,
)
from app.services.prompts.revision_prompt import (
    build_revision_prompt,
    build_weekly_feedback_prompt,
    build_resume_review_prompt,
    build_interview_prep_prompt,
    build_learning_tips_prompt,
)

__all__ = [
    # Mentor
    "build_explain_prompt",
    # Career
    "build_career_advice_prompt",
    "build_career_transition_prompt",
    # Quiz
    "build_quiz_generation_prompt",
    "build_flashcard_prompt",
    "build_coding_challenge_prompt",
    # Roadmap / Study
    "build_roadmap_generation_prompt",
    "build_study_plan_prompt",
    "build_revision_schedule_prompt",
    # Revision / AI features
    "build_revision_prompt",
    "build_weekly_feedback_prompt",
    "build_resume_review_prompt",
    "build_interview_prep_prompt",
    "build_learning_tips_prompt",
]
