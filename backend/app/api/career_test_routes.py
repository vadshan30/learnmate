"""Career Aptitude Test API routes for LearnMate AI.

Provides endpoints for the 25-question career aptitude test,
result calculation, AI explanations, and test history.
All results are persisted to the database via the Store.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import Store, get_store
from app.models.career_test import CareerTestResult, TestSubmission
from app.schemas.responses import SuccessResponse
from app.services.career_test_ai import generate_career_explanation
from app.services.career_test_service import (
    CAREERS,
    calculate_scores,
    get_career_recommendations,
    get_questions,
    get_top_careers,
)

logger = logging.getLogger("learnmate.api.career_test")

router = APIRouter(prefix="/api/career-test", tags=["career-test"])


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/questions",
    response_model=SuccessResponse,
    summary="Get career test questions",
    description="Returns all 25 questions without answer scores (client-safe).",
)
async def list_questions() -> SuccessResponse:
    questions = get_questions()
    return SuccessResponse(
        message=f"Returned {len(questions)} questions",
        data={"questions": questions, "total": len(questions)},
    )


@router.get(
    "/careers",
    response_model=SuccessResponse,
    summary="Get available career options",
    description="Returns the list of all careers the test scores against.",
)
async def list_careers() -> SuccessResponse:
    return SuccessResponse(
        message=f"Returned {len(CAREERS)} careers",
        data=CAREERS,
    )


@router.post(
    "/submit",
    response_model=SuccessResponse,
    summary="Submit career test answers",
    description="Submits answers, calculates scores, generates AI explanation, saves to DB, returns full result.",
)
async def submit_test(
    submission: TestSubmission,
    user_id: str = Query(..., description="User ID"),
    store: Store = Depends(get_store),
) -> SuccessResponse:
    uid = user_id.strip().lower()
    answers = submission.answers

    if not answers:
        raise HTTPException(status_code=400, detail="No answers provided")

    # Calculate deterministic scores
    all_scores = calculate_scores(answers)
    top_3 = all_scores[:3]

    # Get questions for AI context
    questions = get_questions()

    # Generate AI explanation
    try:
        ai_explanation = await generate_career_explanation(top_3, answers, questions)
    except Exception as exc:
        logger.error("AI explanation failed: %s", exc)
        ai_explanation = {}

    # Build result
    result_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    result = {
        "id": result_id,
        "user_id": uid,
        "top_careers": top_3,
        "all_scores": all_scores,
        "answers": answers,
        "ai_explanation": ai_explanation,
        "created_at": now,
    }

    # Persist to database
    if store._db:
        try:
            store._db.save_career_test_result(result_id, result)
        except Exception as exc:
            logger.error("Failed to save career test result to DB: %s", exc)

    # Also keep in-memory cache for fast reads
    if uid not in store.career_test_history:
        store.career_test_history[uid] = []
    store.career_test_history[uid].insert(0, result)
    # Keep last 20 tests in memory
    if len(store.career_test_history[uid]) > 20:
        store.career_test_history[uid] = store.career_test_history[uid][:20]

    return SuccessResponse(
        message="Career test submitted successfully",
        data=result,
    )


@router.get(
    "/result/{result_id}",
    response_model=SuccessResponse,
    summary="Get a specific test result",
    description="Retrieves a previously submitted test result by ID.",
)
async def get_result(
    result_id: str,
    user_id: str = Query(..., description="User ID"),
    store: Store = Depends(get_store),
) -> SuccessResponse:
    uid = user_id.strip().lower()

    # Try in-memory first
    history = store.career_test_history.get(uid, [])
    for result in history:
        if result["id"] == result_id:
            return SuccessResponse(
                message="Result found",
                data=result,
            )

    # Fallback to DB
    if store._db:
        try:
            db_results = store._db.load_career_test_results(uid)
            for result in db_results:
                if result["id"] == result_id:
                    return SuccessResponse(
                        message="Result found",
                        data=result,
                    )
        except Exception as exc:
            logger.error("Failed to load career test result from DB: %s", exc)

    raise HTTPException(status_code=404, detail="Result not found")


@router.get(
    "/history",
    response_model=SuccessResponse,
    summary="Get test history",
    description="Returns past test results for a user, most recent first.",
)
async def get_history(
    user_id: str = Query(..., description="User ID"),
    store: Store = Depends(get_store),
) -> SuccessResponse:
    uid = user_id.strip().lower()

    # Try in-memory first
    history = store.career_test_history.get(uid, [])

    # Fallback to DB if empty
    if not history and store._db:
        try:
            history = store._db.load_career_test_results(uid)
            store.career_test_history[uid] = history
        except Exception as exc:
            logger.error("Failed to load career test history from DB: %s", exc)
            history = []

    return SuccessResponse(
        message=f"Found {len(history)} past results",
        data=history,
    )


@router.post(
    "/retake",
    response_model=SuccessResponse,
    summary="Start a new test (clears current)",
    description="Returns fresh questions for a retake. History is preserved.",
)
async def retake_test() -> SuccessResponse:
    questions = get_questions()
    return SuccessResponse(
        message="Ready for retake",
        data={"questions": questions, "total": len(questions)},
    )


@router.get(
    "/recommendations/{career_id}",
    response_model=SuccessResponse,
    summary="Get resources for a career",
    description="Returns courses, projects, certs, and books relevant to a career.",
)
async def get_recommendations(
    career_id: str,
    store: Store = Depends(get_store),
) -> SuccessResponse:
    resources = {
        "courses": [c.__dict__ if hasattr(c, "__dict__") else c for c in store.loaded_courses],
        "projects": [p.__dict__ if hasattr(p, "__dict__") else p for p in store.loaded_projects],
        "certifications": [c.__dict__ if hasattr(c, "__dict__") else c for c in store.loaded_certifications],
        "books": [b.__dict__ if hasattr(b, "__dict__") else b for b in store.loaded_books],
    }
    recommendations = get_career_recommendations(career_id, resources)
    return SuccessResponse(
        message=f"Recommendations for {career_id}",
        data=recommendations,
    )
