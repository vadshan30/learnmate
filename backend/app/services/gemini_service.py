"""Google Gemini AI Service for LearnMate AI.

Provides an async wrapper around the Google GenAI SDK to call Gemini
models for roadmap generation, quizzes, career advice,
and other AI-powered features.

Falls back to deterministic responses when the API is unreachable
or credentials are missing.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional dependency detection
# ---------------------------------------------------------------------------

try:
    from google import genai
    from google.genai import types

    _GEMINI_AVAILABLE = True
except ImportError:
    genai = None  # type: ignore[assignment]
    types = None  # type: ignore[assignment]
    _GEMINI_AVAILABLE = False
    logger.warning(
        "google-genai is not installed – Gemini features are disabled. "
        "Install it with: pip install google-genai"
    )

# ---------------------------------------------------------------------------
# Configuration – read from environment at call time, NOT at import time.
# load_dotenv() in main.py must run before this module is used; however
# the module may be imported early during app bootstrap, so every public
# function re-reads os.getenv() to guarantee the latest value.
# ---------------------------------------------------------------------------

def _get_api_key() -> str:
    """Read GEMINI_API_KEY from the environment (supports live reload)."""
    return os.getenv("GEMINI_API_KEY", "")


def _get_model() -> str:
    """Read GEMINI_MODEL from the environment."""
    return os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


# Generation defaults
DEFAULT_MAX_TOKENS: int = 2048
DEFAULT_TEMPERATURE: float = 0.7


def _credentials_configured() -> bool:
    """Return True when the Gemini API key is present and non-empty."""
    key = _get_api_key()
    if not key:
        logger.warning("GEMINI_API_KEY is not set or empty")
        return False
    if len(key) < 10:
        logger.warning("GEMINI_API_KEY looks too short (%d chars)", len(key))
        return False
    return True


# ---------------------------------------------------------------------------
# Synchronous Gemini client (lazy initialisation)
# ---------------------------------------------------------------------------

_gemini_client: Any = None
_gemini_client_key: str = ""  # track which key the client was created with


def _get_gemini_client():
    """Lazily create and cache the Google GenAI client.

    Recreates the client if the API key changes (e.g. after .env reload).
    """
    global _gemini_client, _gemini_client_key

    if not _GEMINI_AVAILABLE:
        logger.warning("google-genai package not installed – using fallback responses")
        return None

    api_key = _get_api_key()
    model = _get_model()

    if not _credentials_configured():
        return None

    # Return cached client if the key hasn't changed
    if _gemini_client is not None and _gemini_client_key == api_key:
        return _gemini_client

    try:
        _gemini_client = genai.Client(api_key=api_key)
        _gemini_client_key = api_key
        masked = api_key[:6] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        logger.info(
            "Google Gemini client initialised: model=%s, key=%s",
            model,
            masked,
        )
        return _gemini_client
    except Exception as exc:
        logger.error("Failed to initialise Google Gemini client: %s", exc)
        _gemini_client = None
        _gemini_client_key = ""
        return None


# ---------------------------------------------------------------------------
# Error logging helper
# ---------------------------------------------------------------------------


def _log_api_error(context: str, exc: Exception) -> None:
    """Log API errors with actionable details."""
    exc_type = type(exc).__name__
    msg = str(exc)

    if "API_KEY_INVALID" in msg or "api key not valid" in msg.lower():
        logger.error(
            "[Gemini %s] API key rejected by Google. "
            "Check that GEMINI_API_KEY is a valid Google AI Studio key (starts with 'AQ.'). "
            "Detail: %s",
            context,
            msg,
        )
    elif "INVALID_ARGUMENT" in msg:
        logger.error(
            "[Gemini %s] Invalid argument – possibly a bad model name or request format. "
            "Current model=%s. Detail: %s",
            context,
            _get_model(),
            msg,
        )
    elif "PERMISSION_DENIED" in msg:
        logger.error(
            "[Gemini %s] Permission denied – the API key may not have access to this model. "
            "Detail: %s",
            context,
            msg,
        )
    elif "RESOURCE_EXHAUSTED" in msg or "quota" in msg.lower():
        logger.error(
            "[Gemini %s] Rate limit or quota exceeded. Detail: %s",
            context,
            msg,
        )
    else:
        logger.error("[Gemini %s] %s: %s", context, exc_type, msg)


# ---------------------------------------------------------------------------
# Core generation helpers
# ---------------------------------------------------------------------------


async def generate_response(
    prompt: str,
    *,
    system_instruction: Optional[str] = None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = DEFAULT_TEMPERATURE,
) -> str:
    """Generate a free-form response from Gemini.

    Args:
        prompt: The user prompt text.
        system_instruction: Optional system instruction to guide behaviour.
        max_tokens: Maximum output tokens.
        temperature: Sampling temperature (0.0-2.0).

    Returns:
        Generated text, or empty string on failure.
    """
    client = _get_gemini_client()
    if client is None:
        return ""

    try:
        config = types.GenerateContentConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        )
        if system_instruction:
            config.system_instruction = system_instruction

        response = await client.aio.models.generate_content(
            model=_get_model(),
            contents=prompt,
            config=config,
        )
        return response.text if response.text else ""
    except Exception as exc:
        _log_api_error("generate_response", exc)
        return ""


# ---------------------------------------------------------------------------
# Specialized generation methods
# ---------------------------------------------------------------------------


async def summarize_text(
    text: str,
    *,
    max_tokens: int = 1024,
    temperature: float = 0.3,
) -> str:
    """Summarize a given text using Gemini.

    Args:
        text: The text to summarize.
        max_tokens: Maximum output tokens.
        temperature: Sampling temperature.

    Returns:
        Summary text, or fallback message on failure.
    """
    system_instruction = (
        "You are a concise summarization assistant. "
        "Provide a clear, well-structured summary of the given text. "
        "Use bullet points where appropriate. Keep it under 300 words."
    )

    prompt = f"Summarize the following text:\n\n{text}"
    result = await generate_response(
        prompt,
        system_instruction=system_instruction,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return result or _fallback_summarize(text)


async def explain_concept(
    concept: str,
    *,
    level: str = "intermediate",
    max_tokens: int = 1024,
    temperature: float = 0.5,
) -> str:
    """Explain a concept at the specified difficulty level.

    Args:
        concept: The concept to explain.
        level: Difficulty level (beginner, intermediate, advanced).
        max_tokens: Maximum output tokens.
        temperature: Sampling temperature.

    Returns:
        Explanation text, or fallback on failure.
    """
    level_instructions = {
        "beginner": "Explain like the student is brand new. Use simple analogies and everyday examples. Avoid jargon.",
        "intermediate": "Assume the student has basic programming knowledge. Use technical terms but explain them.",
        "advanced": "Provide a deep technical explanation with implementation details and edge cases.",
    }

    system_instruction = (
        "You are LearnMate AI, an expert educator. "
        f"{level_instructions.get(level, level_instructions['intermediate'])} "
        "Use clear structure with headings, examples, and key takeaways. "
        "Include code examples when relevant."
    )

    prompt = f"Explain the concept: {concept}"
    result = await generate_response(
        prompt,
        system_instruction=system_instruction,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return result or _fallback_explain(concept)


async def generate_quiz(
    topic: str,
    *,
    num_questions: int = 5,
    difficulty: str = "intermediate",
    max_tokens: int = 2048,
    temperature: float = 0.6,
) -> str:
    """Generate a quiz on a given topic.

    Args:
        topic: The quiz topic.
        num_questions: Number of questions to generate.
        difficulty: Difficulty level.
        max_tokens: Maximum output tokens.
        temperature: Sampling temperature.

    Returns:
        JSON string containing quiz questions, or fallback on failure.
    """
    system_instruction = (
        "You are an expert quiz creator for LearnMate AI. "
        "Generate quizzes as valid JSON. "
        "Return ONLY the JSON object, no markdown fences.\n\n"
        "REQUIRED JSON SCHEMA:\n"
        "{\n"
        '  "topic": "string",\n'
        '  "difficulty": "string",\n'
        '  "questions": [\n'
        "    {\n"
        '      "question": "string",\n'
        '      "options": ["A", "B", "C", "D"],\n'
        '      "correct_answer": "A",\n'
        '      "explanation": "string"\n'
        "    }\n"
        "  ]\n"
        "}"
    )

    prompt = (
        f"Create a {difficulty} quiz about: {topic}\n"
        f"Generate exactly {num_questions} multiple-choice questions.\n"
        "Each question should have 4 options (A, B, C, D).\n"
        "Include the correct answer and a brief explanation for each."
    )

    result = await generate_response(
        prompt,
        system_instruction=system_instruction,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    if result:
        try:
            cleaned = result.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]
            parsed = json.loads(cleaned.strip())
            if "questions" in parsed:
                return json.dumps(parsed)
        except json.JSONDecodeError:
            logger.warning("Could not parse quiz JSON from Gemini")

    return _fallback_quiz(topic, num_questions, difficulty)


async def improve_learning_plan(
    plan_context: str,
    *,
    student_context: str = "",
    max_tokens: int = 2048,
    temperature: float = 0.5,
) -> str:
    """Improve or generate a learning plan.

    Args:
        plan_context: Context about what plan to generate/improve.
        student_context: Student profile information.
        max_tokens: Maximum output tokens.
        temperature: Sampling temperature.

    Returns:
        Learning plan as JSON string, or fallback on failure.
    """
    system_instruction = (
        "You are an expert learning coach for LearnMate AI. "
        "Generate or improve a structured study plan. "
        "Return ONLY valid JSON, no markdown fences.\n\n"
        "REQUIRED JSON SCHEMA:\n"
        "{\n"
        '  "plan_name": "string",\n'
        '  "duration": "string",\n'
        '  "daily_schedule": [\n'
        "    {\n"
        '      "day": "string",\n'
        '      "activities": [\n'
        "        {\n"
        '          "time": "string",\n'
        '          "task": "string",\n'
        '          "duration": "string",\n'
        '          "type": "study|practice|break|review"\n'
        "        }\n"
        "      ]\n"
        "    }\n"
        "  ],\n"
        '  "goals": ["string"],\n'
        '  "tips": ["string"]\n'
        "}"
    )

    prompt = f"### Student Profile\n{student_context}\n\n### Plan Request\n{plan_context}"

    result = await generate_response(
        prompt,
        system_instruction=system_instruction,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    if result:
        try:
            cleaned = result.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]
            return json.dumps(json.loads(cleaned.strip()))
        except json.JSONDecodeError:
            logger.warning("Could not parse learning plan JSON")

    return json.dumps(_fallback_learning_plan())


# ---------------------------------------------------------------------------
# Roadmap generation (backward compatible with granite_service interface)
# ---------------------------------------------------------------------------


async def generate_roadmap(
    student_name: str,
    career_goal: str,
    current_skills: List[str],
    interests: List[str],
    skill_level: str,
    available_courses: str,
    available_projects: str,
    available_certs: str,
) -> Dict[str, Any]:
    """Generate a structured 10-week learning roadmap using Gemini."""
    system_instruction = (
        "You are an expert learning coach AI. Generate a personalised "
        "10-week learning roadmap as valid JSON. The JSON must contain:\n"
        '- "weeks": an array of 10 objects, each with "week_number" (int), '
        '"title" (string), "topics" (array of strings), '
        '"projects" (array of strings), "assessments" (array of strings), '
        '"estimated_hours" (float)\n'
        '- "certifications": an array of certification name strings\n'
        '- "final_project": a string describing the capstone project\n'
        "Return ONLY the JSON object, no markdown fences."
    )

    user_prompt = (
        f"Student: {student_name}\n"
        f"Career Goal: {career_goal}\n"
        f"Current Skills: {', '.join(current_skills)}\n"
        f"Interests: {', '.join(interests)}\n"
        f"Skill Level: {skill_level}\n\n"
        f"Available Courses:\n{available_courses}\n\n"
        f"Available Projects:\n{available_projects}\n\n"
        f"Available Certifications:\n{available_certs}\n\n"
        "Generate the 10-week personalised learning roadmap."
    )

    raw = await generate_response(
        user_prompt,
        system_instruction=system_instruction,
        max_tokens=2048,
        temperature=0.4,
    )

    if raw:
        try:
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]
            return json.loads(cleaned.strip())
        except json.JSONDecodeError:
            logger.warning("Could not parse Gemini roadmap JSON – using fallback")

    return _fallback_roadmap(student_name, career_goal, skill_level)


# ---------------------------------------------------------------------------
# Fallback responses
# ---------------------------------------------------------------------------


def _fallback_roadmap(
    student_name: str,
    career_goal: str,
    skill_level: str,
) -> Dict[str, Any]:
    """Return a deterministic fallback roadmap."""
    topic_bank = {
        "Beginner": [
            ["Fundamentals & Setup", "Core Concepts Overview"],
            ["Hands-on Practice", "Basic Project Work"],
            ["Intermediate Concepts", "Tooling & Environment"],
            ["Real-world Application", "Collaborative Exercise"],
            ["Advanced Foundations", "Architecture Patterns"],
            ["Deep Dive Topics", "Performance & Optimisation"],
            ["Industry Practices", "Security & Best Practices"],
            ["Capstone Planning", "Integration & Testing"],
            ["Presentation Skills", "Portfolio Development"],
            ["Review & Certification Prep", "Final Project Completion"],
        ],
        "Intermediate": [
            ["Advanced Fundamentals", "Framework Deep Dive"],
            ["System Design Basics", "API Design Patterns"],
            ["Database Optimization", "Caching Strategies"],
            ["Microservices Intro", "Containerization"],
            ["CI/CD Pipelines", "Monitoring & Logging"],
            ["Security Hardening", "Performance Tuning"],
            ["Cloud Deployment", "Scaling Strategies"],
            ["Code Review Practices", "Refactoring Patterns"],
            ["Technical Documentation", "Team Collaboration"],
            ["Certification Prep", "Capstone Project"],
        ],
        "Advanced": [
            ["Architecture Patterns", "Distributed Systems"],
            ["ML/AI Integration", "Model Deployment"],
            ["Infrastructure as Code", "Service Mesh"],
            ["Observability Stack", "Chaos Engineering"],
            ["Advanced Security", "Zero Trust Architecture"],
            ["Performance Engineering", "Load Testing"],
            ["Platform Engineering", "Developer Experience"],
            ["Open Source Contribution", "Technical Leadership"],
            ["Industry Certification", "Conference Speaking"],
            ["Mentoring & Review", "Final Capstone Delivery"],
        ],
    }

    default_topics = topic_bank.get(skill_level, topic_bank["Beginner"])
    weeks = []
    for i in range(1, 11):
        topics = default_topics[i - 1] if i <= len(default_topics) else [
            f"Advanced Topic {i}", f"Practice Module {i}"
        ]
        weeks.append({
            "week_number": i,
            "title": f"Week {i}: {topics[0]}",
            "topics": topics,
            "projects": [f"Mini-project for {topics[0]}"] if i % 2 == 0 else [],
            "assessments": [f"Quiz on {topics[0]}", f"Reflect on {topics[1]}"],
            "estimated_hours": 10.0 + (i * 1.5),
        })

    return {
        "weeks": weeks,
        "certifications": [f"Industry Certification for {career_goal}"],
        "final_project": (
            f"Complete capstone project demonstrating {career_goal} skills "
            f"using techniques learned throughout the 10-week programme."
        ),
    }


def _fallback_mentor_response(user_message: str) -> str:
    """Return a generic but helpful fallback for mentor chat."""
    return (
        f"Thank you for your question! I'm currently running in offline mode "
        f"because the Gemini AI service is not available. Here's some general advice:\n\n"
        f"1. Break your learning goal into smaller, manageable milestones.\n"
        f"2. Practice consistently — even 30 minutes daily compounds over time.\n"
        f"3. Build projects that interest you; hands-on experience sticks best.\n"
        f"4. Don't hesitate to revisit foundational concepts when tackling advanced topics.\n\n"
        f"Please try again later when the AI service is online for a more "
        f"personalised response to: \"{user_message}\""
    )


def _fallback_quiz(topic: str, num_questions: int, difficulty: str) -> str:
    """Return a fallback quiz JSON."""
    questions = []
    for i in range(1, num_questions + 1):
        questions.append({
            "question": f"Question {i} about {topic}",
            "options": [
                f"Option A for question {i}",
                f"Option B for question {i}",
                f"Option C for question {i}",
                f"Option D for question {i}",
            ],
            "correct_answer": "A",
            "explanation": f"Explanation for question {i} about {topic}",
        })
    return json.dumps({
        "topic": topic,
        "difficulty": difficulty,
        "questions": questions,
    })


def _fallback_summarize(text: str) -> str:
    """Return a fallback summary."""
    word_count = len(text.split())
    return (
        f"**Summary**\n\n"
        f"The provided content contains approximately {word_count} words. "
        f"I'm currently running in offline mode, so I cannot provide a detailed summary. "
        f"Please try again later when the AI service is available.\n\n"
        f"**Key points to look for:**\n"
        f"- Main topic or thesis\n"
        f"- Supporting arguments or evidence\n"
        f"- Conclusions or recommendations"
    )


def _fallback_explain(concept: str) -> str:
    """Return a fallback explanation."""
    return (
        f"**{concept}**\n\n"
        f"I'm currently running in offline mode and cannot provide a full explanation. "
        f"Here are some general tips for learning about this concept:\n\n"
        f"1. Start with the fundamentals and build up\n"
        f"2. Look for hands-on tutorials and examples\n"
        f"3. Practice by building small projects\n"
        f"4. Join online communities for discussions\n\n"
        f"Please try again later when the AI service is available for a detailed, "
        f"personalised explanation."
    )


def _fallback_learning_plan() -> Dict[str, Any]:
    """Return a fallback learning plan."""
    return {
        "plan_name": "General Study Plan",
        "duration": "1 week",
        "daily_schedule": [
            {
                "day": day,
                "activities": [
                    {"time": "09:00", "task": "Study new concepts", "duration": "2 hours", "type": "study"},
                    {"time": "11:00", "task": "Practice exercises", "duration": "1 hour", "type": "practice"},
                    {"time": "14:00", "task": "Project work", "duration": "2 hours", "type": "practice"},
                ],
            }
            for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        ],
        "goals": ["Learn core concepts", "Complete practice exercises", "Build a small project"],
        "tips": [
            "Take regular breaks",
            "Review what you learned each day",
            "Practice coding daily",
        ],
    }


# ---------------------------------------------------------------------------
# Feature flag
# ---------------------------------------------------------------------------

gemini_available = _GEMINI_AVAILABLE
