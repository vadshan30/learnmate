"""IBM Granite LLM Service for LearnMate AI.

Provides an async wrapper around IBM Watsonx.ai to call the
ibm/granite-13b-instruct-v2 model for roadmap generation,
skill-gap analysis, and mentor chat responses.

Falls back to deterministic responses when the API is
unreachable or credentials are missing.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional dependency detection
# ---------------------------------------------------------------------------

try:
    from ibm_watsonx_ai import Credentials  # noqa: F401
    from ibm_watsonx_ai.foundation_models import Model  # noqa: F401

    _WATSONX_AVAILABLE = True
except ImportError:
    _WATSONX_AVAILABLE = False
    logger.warning(
        "ibm-watsonx-ai is not installed – Granite features are disabled. "
        "Install it with: pip install ibm-watsonx-ai"
    )

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

IBM_API_KEY: str = os.getenv("IBM_API_KEY", "")
IBM_PROJECT_ID: str = os.getenv("IBM_PROJECT_ID", "")
IBM_URL: str = os.getenv("IBM_URL", "https://us-south.ml.cloud.ibm.com")
GRANITE_MODEL_ID: str = os.getenv("GRANITE_MODEL_ID", "ibm/granite-13b-instruct-v2")

# Generation defaults
DEFAULT_MAX_TOKENS: int = 1024
DEFAULT_TEMPERATURE: float = 0.3
DEFAULT_TOP_P: float = 0.9


def _credentials_configured() -> bool:
    """Return True when all required IBM credentials are present."""
    return bool(IBM_API_KEY and IBM_PROJECT_ID and IBM_URL)


# ---------------------------------------------------------------------------
# Synchronous IBM Granite client (lazy initialisation)
# ---------------------------------------------------------------------------

_granite_model = None


def _get_granite_model():
    """Lazily create and cache the IBM Granite Model instance."""
    global _granite_model
    if _granite_model is not None:
        return _granite_model

    if not _WATSONX_AVAILABLE:
        logger.warning("ibm-watsonx-ai package not installed – using fallback responses")
        return None

    if not _credentials_configured():
        logger.warning("IBM credentials not configured – using fallback responses")
        return None

    try:
        from ibm_watsonx_ai import Credentials
        from ibm_watsonx_ai.foundation_models import Model

        credentials = Credentials(url=IBM_URL, api_key=IBM_API_KEY)
        _granite_model = Model(
            model_id=GRANITE_MODEL_ID,
            credentials=credentials,
            project_id=IBM_PROJECT_ID,
        )
        logger.info("IBM Granite model initialised: %s", GRANITE_MODEL_ID)
        return _granite_model
    except Exception as exc:
        logger.error("Failed to initialise IBM Granite model: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Core generation helper
# ---------------------------------------------------------------------------


def _generate_sync(
    prompt: str,
    *,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = DEFAULT_TEMPERATURE,
    top_p: float = DEFAULT_TOP_P,
) -> str:
    """Synchronous text generation via Granite (runs in a thread later)."""
    model = _get_granite_model()
    if model is None:
        return ""

    try:
        response = model.generate_text(
            prompt=prompt,
            params={
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "stop_sequences": ["\n\n\n"],
            },
        )
        return response.strip() if response else ""
    except Exception as exc:
        logger.error("Granite generation failed: %s", exc)
        return ""


# ---------------------------------------------------------------------------
# Public async API
# ---------------------------------------------------------------------------


async def generate_response(
    prompt: str,
    *,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = DEFAULT_TEMPERATURE,
) -> str:
    """Generate a free-form response from Granite."""
    try:
        result = await asyncio.to_thread(
            _generate_sync,
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return result
    except Exception as exc:
        logger.error("generate_response error: %s", exc)
        return ""


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
    """Generate a structured 10-week learning roadmap using Granite."""
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
        f"{system_instruction}\n\n{user_prompt}",
        max_tokens=2048,
        temperature=0.4,
    )

    # Attempt to parse Granite's JSON output
    if raw:
        try:
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]
            return json.loads(cleaned.strip())
        except json.JSONDecodeError:
            logger.warning("Could not parse Granite roadmap JSON – using fallback")

    return _fallback_roadmap(student_name, career_goal, skill_level)


async def mentor_chat(
    user_message: str,
    student_context: str,
    retrieved_resources: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
) -> str:
    """Answer a student's learning question using RAG context + Granite.

    Supports multi-turn conversation by including prior chat turns in the prompt.
    """
    system_instruction = (
        "You are LearnMate AI, a supportive and knowledgeable learning mentor. "
        "Answer the student's question using the provided context about their "
        "profile and relevant learning resources. Be encouraging, specific, "
        "and actionable. If you lack enough information, say so honestly. "
        "Remember previous messages in this conversation to provide contextual, "
        "continuous guidance. Reference prior advice when appropriate."
    )

    # Build conversation history block for multi-turn context
    history_block = ""
    if conversation_history:
        recent = conversation_history[-10:]  # last 10 turns for context window
        turns = []
        for turn in recent:
            role = "Student" if turn.get("role") == "user" else "Mentor"
            turns.append(f"{role}: {turn.get('content', '')}")
        history_block = "\n".join(turns)

    prompt_parts = [
        f"### Student Profile\n{student_context}\n",
        f"### Relevant Learning Resources\n{retrieved_resources}\n",
    ]

    if history_block:
        prompt_parts.append(f"### Conversation History\n{history_block}\n")

    prompt_parts.append(f"### Student Question\n{user_message}\n")
    prompt_parts.append("Provide a helpful, personalised answer:")

    prompt = "\n".join(prompt_parts)

    response = await generate_response(
        f"{system_instruction}\n\n{prompt}",
        max_tokens=1024,
        temperature=0.5,
    )

    if response:
        return response

    return _fallback_mentor_response(user_message)


# ---------------------------------------------------------------------------
# Fallback responses (used when IBM API is unavailable)
# ---------------------------------------------------------------------------


def _fallback_roadmap(
    student_name: str,
    career_goal: str,
    skill_level: str,
) -> Dict[str, Any]:
    """Return a deterministic fallback roadmap when Granite is unreachable."""
    weeks = []
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


granite_available = _WATSONX_AVAILABLE


def _fallback_mentor_response(user_message: str) -> str:
    """Return a generic but helpful fallback for mentor chat."""
    return (
        f"Thank you for your question! I'm currently running in offline mode "
        f"because the IBM Granite API is not available. Here's some general advice:\n\n"
        f"1. Break your learning goal into smaller, manageable milestones.\n"
        f"2. Practice consistently — even 30 minutes daily compounds over time.\n"
        f"3. Build projects that interest you; hands-on experience sticks best.\n"
        f"4. Don't hesitate to revisit foundational concepts when tackling advanced topics.\n\n"
        f"Please try again later when the AI service is online for a more "
        f"personalised response to: \"{user_message}\""
    )
