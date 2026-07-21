"""Mentor API Routes for LearnMate AI.

Provides comprehensive AI mentor endpoints including quizzes,
flashcards, study plans, career advice, interview prep, and more.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends

from app.dependencies import Store, get_store, get_student_or_404
from app.schemas.requests import (
    MentorQuizRequest,
    MentorExplainRequest,
    MentorStudyPlanRequest,
    MentorRevisionRequest,
    MentorCareerRequest,
    MentorFlashcardRequest,
    MentorCodingChallengeRequest,
    MentorResumeReviewRequest,
    MentorInterviewPrepRequest,
)
from app.schemas.responses import SuccessResponse, ErrorResponse
from app.services import mentor_service

logger = logging.getLogger("learnmate.api.mentor")

router = APIRouter(prefix="/api/mentor", tags=["mentor"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_profile(student_id: str, store: Store) -> Dict[str, Any]:
    """Get student profile or raise 404."""
    return get_student_or_404(student_id, store)


# ---------------------------------------------------------------------------
# Explain concept
# ---------------------------------------------------------------------------


@router.post(
    "/explain",
    response_model=SuccessResponse,
    summary="Explain a concept",
    description="Get a personalized explanation of a concept at the student's skill level.",
    responses={
        200: {"description": "Concept explanation"},
        404: {"model": ErrorResponse, "description": "Student not found"},
    },
)
async def mentor_explain(body: MentorExplainRequest, store: Store = Depends(get_store)) -> SuccessResponse:
    profile = _get_profile(body.student_id, store)

    result = await mentor_service.explain(
        concept=body.concept,
        profile=profile,
        level=body.level,
    )

    return SuccessResponse(
        message="Explanation generated",
        data=result,
    )


# ---------------------------------------------------------------------------
# Quiz generation
# ---------------------------------------------------------------------------


@router.post(
    "/quiz",
    response_model=SuccessResponse,
    summary="Generate a quiz",
    description="Generate a personalized quiz on a topic with multiple-choice questions.",
    responses={
        200: {"description": "Generated quiz"},
        404: {"model": ErrorResponse, "description": "Student not found"},
    },
)
async def mentor_quiz(body: MentorQuizRequest, store: Store = Depends(get_store)) -> SuccessResponse:
    profile = _get_profile(body.student_id, store)

    result = await mentor_service.generate_quiz(
        topic=body.topic,
        profile=profile,
        num_questions=body.num_questions,
        difficulty=body.difficulty,
    )

    return SuccessResponse(
        message="Quiz generated",
        data=result,
    )


# ---------------------------------------------------------------------------
# Flashcard generation
# ---------------------------------------------------------------------------


@router.post(
    "/flashcards",
    response_model=SuccessResponse,
    summary="Generate flashcards",
    description="Generate study flashcards on a topic.",
    responses={
        200: {"description": "Generated flashcards"},
        404: {"model": ErrorResponse, "description": "Student not found"},
    },
)
async def mentor_flashcards(body: MentorFlashcardRequest, store: Store = Depends(get_store)) -> SuccessResponse:
    profile = _get_profile(body.student_id, store)

    result = await mentor_service.generate_flashcards(
        topic=body.topic,
        profile=profile,
        num_cards=body.num_cards,
    )

    return SuccessResponse(
        message="Flashcards generated",
        data=result,
    )


# ---------------------------------------------------------------------------
# Study plan
# ---------------------------------------------------------------------------


@router.post(
    "/study-plan",
    response_model=SuccessResponse,
    summary="Generate a study plan",
    description="Generate a personalized daily study plan.",
    responses={
        200: {"description": "Generated study plan"},
        404: {"model": ErrorResponse, "description": "Student not found"},
    },
)
async def mentor_study_plan(body: MentorStudyPlanRequest, store: Store = Depends(get_store)) -> SuccessResponse:
    profile = _get_profile(body.student_id, store)

    result = await mentor_service.generate_study_plan(
        request_context=body.context,
        profile=profile,
    )

    return SuccessResponse(
        message="Study plan generated",
        data=result,
    )


# ---------------------------------------------------------------------------
# Revision
# ---------------------------------------------------------------------------


@router.post(
    "/revise",
    response_model=SuccessResponse,
    summary="Get revision help",
    description="Get personalized revision assistance and schedule for specific topics.",
    responses={
        200: {"description": "Revision guide"},
        404: {"model": ErrorResponse, "description": "Student not found"},
    },
)
async def mentor_revise(body: MentorRevisionRequest, store: Store = Depends(get_store)) -> SuccessResponse:
    profile = _get_profile(body.student_id, store)

    if body.exam_date:
        result = await mentor_service.generate_revision_schedule(
            topics=body.topics,
            exam_date=body.exam_date,
            profile=profile,
        )
    else:
        result = await mentor_service.get_revision_help(
            topic=body.topics[0] if body.topics else "General Review",
            profile=profile,
            focus_areas=body.focus_areas,
        )

    return SuccessResponse(
        message="Revision material generated",
        data=result,
    )


# ---------------------------------------------------------------------------
# Career advice
# ---------------------------------------------------------------------------


@router.post(
    "/career",
    response_model=SuccessResponse,
    summary="Get career advice",
    description="Get personalized career guidance and pathway recommendations.",
    responses={
        200: {"description": "Career advice with citations"},
        404: {"model": ErrorResponse, "description": "Student not found"},
    },
)
async def mentor_career(body: MentorCareerRequest, store: Store = Depends(get_store)) -> SuccessResponse:
    profile = _get_profile(body.student_id, store)

    result = await mentor_service.get_career_advice(
        question=body.question,
        profile=profile,
    )

    return SuccessResponse(
        message="Career advice generated",
        data=result,
    )


# ---------------------------------------------------------------------------
# Coding challenge
# ---------------------------------------------------------------------------


@router.post(
    "/coding-challenge",
    response_model=SuccessResponse,
    summary="Generate a coding challenge",
    description="Generate a personalized coding challenge with examples and hints.",
    responses={
        200: {"description": "Generated coding challenge"},
        404: {"model": ErrorResponse, "description": "Student not found"},
    },
)
async def mentor_coding_challenge(
    body: MentorCodingChallengeRequest,
    store: Store = Depends(get_store),
) -> SuccessResponse:
    profile = _get_profile(body.student_id, store)

    result = await mentor_service.generate_coding_challenge(
        topic=body.topic,
        profile=profile,
        difficulty=body.difficulty,
        language=body.language,
    )

    return SuccessResponse(
        message="Coding challenge generated",
        data=result,
    )


# ---------------------------------------------------------------------------
# Resume review
# ---------------------------------------------------------------------------


@router.post(
    "/resume-review",
    response_model=SuccessResponse,
    summary="Review a resume",
    description="Get AI-powered resume review with personalized feedback.",
    responses={
        200: {"description": "Resume review"},
        404: {"model": ErrorResponse, "description": "Student not found"},
    },
)
async def mentor_resume_review(
    body: MentorResumeReviewRequest,
    store: Store = Depends(get_store),
) -> SuccessResponse:
    profile = _get_profile(body.student_id, store)

    result = await mentor_service.review_resume(
        resume_text=body.resume_text,
        profile=profile,
        target_role=body.target_role,
    )

    return SuccessResponse(
        message="Resume review generated",
        data=result,
    )


# ---------------------------------------------------------------------------
# Interview preparation
# ---------------------------------------------------------------------------


@router.post(
    "/interview-prep",
    response_model=SuccessResponse,
    summary="Prepare for interviews",
    description="Generate interview questions and preparation material for a target role.",
    responses={
        200: {"description": "Interview preparation material"},
        404: {"model": ErrorResponse, "description": "Student not found"},
    },
)
async def mentor_interview_prep(
    body: MentorInterviewPrepRequest,
    store: Store = Depends(get_store),
) -> SuccessResponse:
    profile = _get_profile(body.student_id, store)

    result = await mentor_service.prepare_interview(
        role=body.role,
        profile=profile,
        num_questions=body.num_questions,
        focus=body.focus,
    )

    return SuccessResponse(
        message="Interview preparation material generated",
        data=result,
    )


# ---------------------------------------------------------------------------
# Learning tips
# ---------------------------------------------------------------------------


@router.post(
    "/learning-tips",
    response_model=SuccessResponse,
    summary="Get learning tips",
    description="Get personalized learning tips and strategies.",
    responses={
        200: {"description": "Personalized learning tips"},
        404: {"model": ErrorResponse, "description": "Student not found"},
    },
)
async def mentor_learning_tips(
    student_id: str,
    specific_area: str = "",
    store: Store = Depends(get_store),
) -> SuccessResponse:
    profile = _get_profile(student_id, store)

    result = await mentor_service.get_learning_tips(
        profile=profile,
        specific_area=specific_area,
    )

    return SuccessResponse(
        message="Learning tips generated",
        data=result,
    )
