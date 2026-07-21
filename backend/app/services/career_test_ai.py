"""Career Aptitude Test AI Service for LearnMate AI.

Uses Gemini to generate explanations for career test results.
Gemini NEVER decides the career -- it only explains the calculated results.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger("learnmate.career_test_ai")

try:
    from google import genai
    from google.genai import types

    _GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    types = None
    _GEMINI_AVAILABLE = False


def _get_api_key() -> str:
    return os.getenv("GEMINI_API_KEY", "")


def _get_model() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


async def generate_career_explanation(
    top_careers: List[Dict[str, Any]],
    answers: Dict[str, str],
    questions: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Generate AI explanation for career test results.

    Args:
        top_careers: Top 3 career results with scores.
        answers: User's answers (question_id -> answer_id).
        questions: Full question list for context.

    Returns:
        Dictionary with explanation fields.
    """
    if not _GEMINI_AVAILABLE or not _get_api_key():
        return _fallback_explanation(top_careers)

    career_summary = "\n".join(
        f"- {c['career_name']}: {c['percentage']:.0f}% match"
        for c in top_careers
    )

    answer_summary = []
    for q in questions:
        qid = str(q["id"])
        aid = answers.get(qid, "")
        for opt in q.get("options", []):
            if opt["id"] == aid:
                answer_summary.append(f"Q{qid}: {opt['text']}")
                break

    prompt = f"""You are an expert career counselor AI. A student completed a career aptitude test.

TOP 3 CAREER MATCHES:
{career_summary}

STUDENT ANSWERS:
{chr(10).join(answer_summary[:10])}

Generate a JSON response with exactly this structure (no markdown, no code fences):
{{
  "career_explanations": {{
    "<career_id>": {{
      "explanation": "Why this career matches (2-3 sentences)",
      "strengths": ["strength1", "strength2", "strength3"],
      "weaknesses": ["area1", "area2"],
      "learning_advice": "Specific advice for this path (2-3 sentences)",
      "future_opportunities": ["opportunity1", "opportunity2", "opportunity3"],
      "suggested_technologies": ["tech1", "tech2", "tech3"],
      "suggested_roadmap": "Brief learning roadmap (2-3 steps)"
    }}
  }},
  "personality_summary": "Overall personality/type description based on answers",
  "skill_match": "Analysis of how skills align with top careers"
}}

IMPORTANT: Only explain the results. Do NOT recommend careers. The scoring is already done."""

    try:
        client = genai.Client(api_key=_get_api_key())
        response = await client.aio.models.generate_content(
            model=_get_model(),
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=2048,
            ),
        )
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(text)
    except Exception as exc:
        logger.error("Gemini career explanation failed: %s", exc)
        return _fallback_explanation(top_careers)


def _fallback_explanation(top_careers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Deterministic fallback when Gemini is unavailable."""
    explanations = {}
    for c in top_careers:
        cid = c.get("career_id", "")
        name = c.get("career_name", "Career")
        explanations[cid] = {
            "explanation": f"Based on your responses, {name} aligns well with your interests and skills.",
            "strengths": ["Analytical thinking", "Problem solving", "Continuous learning"],
            "weaknesses": ["May need to develop specific technical skills"],
            "learning_advice": f"Focus on building foundational skills for {name}. Start with online courses and hands-on projects.",
            "future_opportunities": ["Growth potential", "Industry demand", "Remote work options"],
            "suggested_technologies": ["Relevant tools and frameworks"],
            "suggested_roadmap": f"Start with fundamentals, then progress to advanced {name} topics.",
        }
    return {
        "career_explanations": explanations,
        "personality_summary": "You show a balanced mix of analytical and creative thinking.",
        "skill_match": "Your skills align well with technical career paths.",
    }
