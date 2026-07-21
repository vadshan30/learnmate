"""AI Mentor Service for LearnMate AI.

Orchestrates Gemini AI, RAG retrieval, and conversation memory into
a unified mentoring pipeline. Handles all AI-powered features including
quizzes, flashcards, study plans, career advice, and more.

Workflow:
    User Question
        -> Search ChromaDB (RAG)
        -> Retrieve relevant resources
        -> Build context-aware prompt
        -> Send to Gemini with student profile
        -> Return grounded answer with citations
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from app.services import gemini_service
from app.services.gemini_service import gemini_available
from app.services.rag_service import rag_service, RAG_AVAILABLE
from app.services.prompts.mentor_prompt import (
    EXPLAIN_SYSTEM_INSTRUCTION,
    build_explain_prompt,
)
from app.services.prompts.career_prompt import (
    CAREER_SYSTEM_INSTRUCTION,
    build_career_advice_prompt,
)
from app.services.prompts.quiz_prompt import (
    QUIZ_SYSTEM_INSTRUCTION,
    FLASHCARD_SYSTEM_INSTRUCTION,
    CODING_CHALLENGE_SYSTEM_INSTRUCTION,
    build_quiz_generation_prompt,
    build_flashcard_prompt,
    build_coding_challenge_prompt,
)
from app.services.prompts.roadmap_prompt import (
    STUDY_PLAN_SYSTEM_INSTRUCTION,
    REVISION_SCHEDULE_SYSTEM_INSTRUCTION,
    build_study_plan_prompt,
    build_revision_schedule_prompt,
)
from app.services.prompts.revision_prompt import (
    REVISION_SYSTEM_INSTRUCTION,
    WEEKLY_FEEDBACK_SYSTEM_INSTRUCTION,
    RESUME_REVIEW_SYSTEM_INSTRUCTION,
    INTERVIEW_PREP_SYSTEM_INSTRUCTION,
    LEARNING_TIPS_SYSTEM_INSTRUCTION,
    build_revision_prompt,
    build_weekly_feedback_prompt,
    build_resume_review_prompt,
    build_interview_prep_prompt,
    build_learning_tips_prompt,
)

logger = logging.getLogger("learnmate.mentor")


# ---------------------------------------------------------------------------
# Student context builder
# ---------------------------------------------------------------------------


def build_student_context(profile: Dict[str, Any]) -> str:
    """Build a formatted student context string from a profile dict.

    Args:
        profile: Student profile dictionary.

    Returns:
        Formatted context string for prompt injection.
    """
    parts = [
        f"Name: {profile.get('name', 'Unknown')}",
        f"Career Goal: {profile.get('career_goal', 'Not set')}",
        f"Skill Level: {profile.get('skill_level', 'beginner')}",
    ]

    skills = profile.get("current_skills", [])
    if skills:
        parts.append(f"Current Skills: {', '.join(skills)}")

    interests = profile.get("interests", [])
    if interests:
        parts.append(f"Interests: {', '.join(interests)}")

    completed = profile.get("completed_topics", [])
    if completed:
        parts.append(f"Completed Topics: {', '.join(completed[-10:])}")

    progress = profile.get("progress_percentage", 0.0)
    parts.append(f"Progress: {progress}%")

    learning_style = profile.get("learning_style")
    if learning_style:
        parts.append(f"Learning Style: {learning_style}")

    hours = profile.get("hours_per_week")
    if hours:
        parts.append(f"Hours/Week: {hours}")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# RAG retrieval
# ---------------------------------------------------------------------------


async def retrieve_resources(
    query: str,
    *,
    n: int = 5,
    resource_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Search RAG for relevant learning resources.

    Args:
        query: Search query.
        n: Number of results to return.
        resource_type: Optional filter by resource type.

    Returns:
        List of RAG search results, or empty list.
    """
    if not RAG_AVAILABLE or rag_service is None:
        return []

    try:
        return await rag_service.search_courses(query, n=n, resource_type=resource_type)
    except Exception as exc:
        logger.error("RAG retrieval failed: %s", exc)
        return []


def format_resources_for_prompt(results: List[Dict[str, Any]]) -> str:
    """Format RAG results into a readable string for prompt injection.

    Args:
        results: RAG search results.

    Returns:
        Formatted resource string.
    """
    if not results:
        return "No specific resources found."

    lines = []
    for i, r in enumerate(results, 1):
        doc = r.get("document", "")[:300]
        score = r.get("score", 0.0)
        resource_type = r.get("metadata", {}).get("resource_type", "resource")
        lines.append(f"{i}. [{resource_type.upper()}] {doc} (relevance: {score:.2f})")

    return "\n".join(lines)


def extract_citations(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract citation information from RAG results.

    Args:
        results: RAG search results.

    Returns:
        List of citation dicts with type, title, and relevance.
    """
    citations = []
    for r in results:
        doc = r.get("document", "")
        metadata = r.get("metadata", {})
        title = ""
        for key in ("Title:", "Name:"):
            if key in doc:
                start = doc.index(key) + len(key)
                end = doc.find("|", start)
                if end == -1:
                    end = len(doc)
                title = doc[start:end].strip()
                break

        citations.append({
            "type": metadata.get("resource_type", "resource"),
            "title": title or doc[:80],
            "relevance": r.get("score", 0.0),
            "domain": metadata.get("domain", ""),
        })

    return citations


# ---------------------------------------------------------------------------
# Explain concept
# ---------------------------------------------------------------------------


async def explain(
    concept: str,
    profile: Dict[str, Any],
    *,
    level: Optional[str] = None,
) -> Dict[str, Any]:
    """Explain a concept personalized to the student.

    Args:
        concept: The concept to explain.
        profile: Student profile dictionary.
        level: Override difficulty level.

    Returns:
        Dict with 'response', 'source', and 'concept'.
    """
    student_level = level or profile.get("skill_level", "intermediate")
    student_context = build_student_context(profile)

    prompt = build_explain_prompt(concept, student_context, student_level)

    if gemini_available:
        response = await gemini_service.generate_response(
            prompt,
            system_instruction=EXPLAIN_SYSTEM_INSTRUCTION,
            max_tokens=1024,
            temperature=0.4,
        )
        source = "gemini"
    else:
        response = gemini_service._fallback_explain(concept)
        source = "fallback"

    return {
        "response": response or f"Sorry, I couldn't explain '{concept}' right now.",
        "source": source,
        "concept": concept,
    }


# ---------------------------------------------------------------------------
# Quiz generation
# ---------------------------------------------------------------------------


async def generate_quiz(
    topic: str,
    profile: Dict[str, Any],
    *,
    num_questions: int = 5,
    difficulty: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a quiz personalized to the student.

    Args:
        topic: Quiz topic.
        profile: Student profile dictionary.
        num_questions: Number of questions.
        difficulty: Override difficulty level.

    Returns:
        Dict with quiz data, source, and citations.
    """
    student_level = difficulty or profile.get("skill_level", "intermediate")
    student_context = build_student_context(profile)

    # RAG for topic-specific resources
    rag_results = await retrieve_resources(topic, n=3)
    citations = extract_citations(rag_results)

    prompt = build_quiz_generation_prompt(topic, num_questions, student_level, student_context)

    if gemini_available:
        response = await gemini_service.generate_response(
            prompt,
            system_instruction=QUIZ_SYSTEM_INSTRUCTION,
            max_tokens=2048,
            temperature=0.6,
        )
        source = "gemini"
    else:
        response = gemini_service._fallback_quiz(topic, num_questions, student_level)
        source = "fallback"

    # Parse quiz JSON
    quiz_data = None
    if response:
        try:
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]
            quiz_data = json.loads(cleaned.strip())
        except json.JSONDecodeError:
            logger.warning("Could not parse quiz JSON")
            quiz_data = {
                "topic": topic,
                "difficulty": student_level,
                "questions": [],
            }

    return {
        "quiz": quiz_data,
        "source": source,
        "citations": citations,
    }


# ---------------------------------------------------------------------------
# Flashcard generation
# ---------------------------------------------------------------------------


async def generate_flashcards(
    topic: str,
    profile: Dict[str, Any],
    *,
    num_cards: int = 10,
) -> Dict[str, Any]:
    """Generate flashcards personalized to the student.

    Args:
        topic: Flashcard topic.
        profile: Student profile dictionary.
        num_cards: Number of flashcards.

    Returns:
        Dict with flashcard data and source.
    """
    student_context = build_student_context(profile)
    prompt = build_flashcard_prompt(topic, num_cards, student_context)

    if gemini_available:
        response = await gemini_service.generate_response(
            prompt,
            system_instruction=FLASHCARD_SYSTEM_INSTRUCTION,
            max_tokens=2048,
            temperature=0.5,
        )
        source = "gemini"
    else:
        response = ""
        source = "fallback"

    flashcard_data = None
    if response:
        try:
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]
            flashcard_data = json.loads(cleaned.strip())
        except json.JSONDecodeError:
            logger.warning("Could not parse flashcard JSON")

    return {
        "flashcards": flashcard_data,
        "source": source,
    }


# ---------------------------------------------------------------------------
# Study plan
# ---------------------------------------------------------------------------


async def generate_study_plan(
    request_context: str,
    profile: Dict[str, Any],
) -> Dict[str, Any]:
    """Generate a personalized daily study plan.

    Args:
        request_context: Details about the plan needed.
        profile: Student profile dictionary.

    Returns:
        Dict with study plan data and source.
    """
    student_context = build_student_context(profile)
    prompt = build_study_plan_prompt(request_context, student_context)

    if gemini_available:
        response = await gemini_service.generate_response(
            prompt,
            system_instruction=STUDY_PLAN_SYSTEM_INSTRUCTION,
            max_tokens=2048,
            temperature=0.5,
        )
        source = "gemini"
    else:
        response = ""
        source = "fallback"

    plan_data = None
    if response:
        try:
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]
            plan_data = json.loads(cleaned.strip())
        except json.JSONDecodeError:
            logger.warning("Could not parse study plan JSON")

    return {
        "study_plan": plan_data,
        "source": source,
    }


# ---------------------------------------------------------------------------
# Revision schedule
# ---------------------------------------------------------------------------


async def generate_revision_schedule(
    topics: List[str],
    exam_date: str,
    profile: Dict[str, Any],
) -> Dict[str, Any]:
    """Generate a personalized revision schedule.

    Args:
        topics: Topics to revise.
        exam_date: Target exam date.
        profile: Student profile dictionary.

    Returns:
        Dict with revision schedule and source.
    """
    student_context = build_student_context(profile)
    prompt = build_revision_schedule_prompt(topics, exam_date, student_context)

    if gemini_available:
        response = await gemini_service.generate_response(
            prompt,
            system_instruction=REVISION_SCHEDULE_SYSTEM_INSTRUCTION,
            max_tokens=2048,
            temperature=0.5,
        )
        source = "gemini"
    else:
        response = ""
        source = "fallback"

    schedule_data = None
    if response:
        try:
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]
            schedule_data = json.loads(cleaned.strip())
        except json.JSONDecodeError:
            logger.warning("Could not parse revision schedule JSON")

    return {
        "revision_schedule": schedule_data,
        "source": source,
    }


# ---------------------------------------------------------------------------
# Career advice
# ---------------------------------------------------------------------------


async def get_career_advice(
    question: str,
    profile: Dict[str, Any],
) -> Dict[str, Any]:
    """Get personalized career advice.

    Args:
        question: Career-related question.
        profile: Student profile dictionary.

    Returns:
        Dict with career advice response and citations.
    """
    student_context = build_student_context(profile)

    rag_results = await retrieve_resources(question, n=5, resource_type="career_pathway")
    resources_text = format_resources_for_prompt(rag_results)
    citations = extract_citations(rag_results)

    prompt = build_career_advice_prompt(question, student_context, resources_text)

    if gemini_available:
        response = await gemini_service.generate_response(
            prompt,
            system_instruction=CAREER_SYSTEM_INSTRUCTION,
            max_tokens=1024,
            temperature=0.5,
        )
        source = "gemini"
    else:
        response = gemini_service._fallback_mentor_response(question)
        source = "fallback"

    return {
        "response": response or "Sorry, I couldn't generate career advice right now.",
        "source": source,
        "citations": citations,
    }


# ---------------------------------------------------------------------------
# Coding challenge
# ---------------------------------------------------------------------------


async def generate_coding_challenge(
    topic: str,
    profile: Dict[str, Any],
    *,
    difficulty: str = "medium",
    language: str = "Python",
) -> Dict[str, Any]:
    """Generate a coding challenge.

    Args:
        topic: Challenge topic/category.
        profile: Student profile dictionary.
        difficulty: Difficulty level.
        language: Programming language.

    Returns:
        Dict with challenge data and source.
    """
    student_context = build_student_context(profile)
    prompt = build_coding_challenge_prompt(topic, difficulty, language, student_context)

    if gemini_available:
        response = await gemini_service.generate_response(
            prompt,
            system_instruction=CODING_CHALLENGE_SYSTEM_INSTRUCTION,
            max_tokens=2048,
            temperature=0.6,
        )
        source = "gemini"
    else:
        response = ""
        source = "fallback"

    challenge_data = None
    if response:
        try:
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]
            challenge_data = json.loads(cleaned.strip())
        except json.JSONDecodeError:
            logger.warning("Could not parse coding challenge JSON")

    return {
        "challenge": challenge_data,
        "source": source,
    }


# ---------------------------------------------------------------------------
# Revision assistance
# ---------------------------------------------------------------------------


async def get_revision_help(
    topic: str,
    profile: Dict[str, Any],
    *,
    focus_areas: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Get revision assistance for a topic.

    Args:
        topic: Topic to revise.
        profile: Student profile dictionary.
        focus_areas: Specific areas to focus on.

    Returns:
        Dict with revision guide and source.
    """
    student_context = build_student_context(profile)
    prompt = build_revision_prompt(topic, student_context, focus_areas)

    if gemini_available:
        response = await gemini_service.generate_response(
            prompt,
            system_instruction=REVISION_SYSTEM_INSTRUCTION,
            max_tokens=1024,
            temperature=0.4,
        )
        source = "gemini"
    else:
        response = gemini_service._fallback_explain(topic)
        source = "fallback"

    return {
        "response": response or f"Sorry, I couldn't generate revision material for '{topic}'.",
        "source": source,
    }


# ---------------------------------------------------------------------------
# Weekly feedback
# ---------------------------------------------------------------------------


async def get_weekly_feedback(
    progress_data: str,
    profile: Dict[str, Any],
) -> Dict[str, Any]:
    """Get personalized weekly progress feedback.

    Args:
        progress_data: Summary of weekly progress.
        profile: Student profile dictionary.

    Returns:
        Dict with feedback and source.
    """
    student_context = build_student_context(profile)
    prompt = build_weekly_feedback_prompt(progress_data, student_context)

    if gemini_available:
        response = await gemini_service.generate_response(
            prompt,
            system_instruction=WEEKLY_FEEDBACK_SYSTEM_INSTRUCTION,
            max_tokens=1024,
            temperature=0.5,
        )
        source = "gemini"
    else:
        response = "I'm currently in offline mode. Please try again later for weekly feedback."
        source = "fallback"

    return {
        "response": response or "Sorry, I couldn't generate feedback right now.",
        "source": source,
    }


# ---------------------------------------------------------------------------
# Resume review
# ---------------------------------------------------------------------------


async def review_resume(
    resume_text: str,
    profile: Dict[str, Any],
    *,
    target_role: str = "",
) -> Dict[str, Any]:
    """Review a resume with personalized feedback.

    Args:
        resume_text: The resume content.
        profile: Student profile dictionary.
        target_role: Target job role.

    Returns:
        Dict with review and source.
    """
    student_context = build_student_context(profile)
    prompt = build_resume_review_prompt(resume_text, student_context, target_role)

    if gemini_available:
        response = await gemini_service.generate_response(
            prompt,
            system_instruction=RESUME_REVIEW_SYSTEM_INSTRUCTION,
            max_tokens=2048,
            temperature=0.4,
        )
        source = "gemini"
    else:
        response = "I'm currently in offline mode. Please try again later for resume review."
        source = "fallback"

    return {
        "response": response or "Sorry, I couldn't review the resume right now.",
        "source": source,
    }


# ---------------------------------------------------------------------------
# Interview preparation
# ---------------------------------------------------------------------------


async def prepare_interview(
    role: str,
    profile: Dict[str, Any],
    *,
    num_questions: int = 5,
    focus: str = "mixed",
) -> Dict[str, Any]:
    """Generate interview preparation questions.

    Args:
        role: Target job role.
        profile: Student profile dictionary.
        num_questions: Number of questions.
        focus: Focus area (technical, behavioral, mixed).

    Returns:
        Dict with interview questions and source.
    """
    student_context = build_student_context(profile)
    prompt = build_interview_prep_prompt(role, student_context, num_questions, focus)

    if gemini_available:
        response = await gemini_service.generate_response(
            prompt,
            system_instruction=INTERVIEW_PREP_SYSTEM_INSTRUCTION,
            max_tokens=2048,
            temperature=0.5,
        )
        source = "gemini"
    else:
        response = "I'm currently in offline mode. Please try again later for interview preparation."
        source = "fallback"

    return {
        "response": response or "Sorry, I couldn't generate interview questions right now.",
        "source": source,
    }


# ---------------------------------------------------------------------------
# Learning tips
# ---------------------------------------------------------------------------


async def get_learning_tips(
    profile: Dict[str, Any],
    *,
    specific_area: str = "",
) -> Dict[str, Any]:
    """Get personalized learning tips.

    Args:
        profile: Student profile dictionary.
        specific_area: Optional area to focus tips on.

    Returns:
        Dict with learning tips and source.
    """
    student_context = build_student_context(profile)
    prompt = build_learning_tips_prompt(student_context, specific_area)

    if gemini_available:
        response = await gemini_service.generate_response(
            prompt,
            system_instruction=LEARNING_TIPS_SYSTEM_INSTRUCTION,
            max_tokens=1024,
            temperature=0.5,
        )
        source = "gemini"
    else:
        response = "I'm currently in offline mode. Please try again later for learning tips."
        source = "fallback"

    return {
        "response": response or "Sorry, I couldn't generate learning tips right now.",
        "source": source,
    }
