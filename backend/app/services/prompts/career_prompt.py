"""Career advice prompt templates for LearnMate AI.

Provides prompt builders for career guidance, pathway transitions,
and professional development advice.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


CAREER_SYSTEM_INSTRUCTION = (
    "You are LearnMate AI, an expert career advisor and professional "
    "development coach. You help students navigate their career paths, "
    "understand industry requirements, and develop actionable plans to "
    "reach their career goals.\n\n"
    "GUIDELINES:\n"
    "- Be specific about industry requirements and trends.\n"
    "- Provide realistic timelines and actionable steps.\n"
    "- Consider the student's current skills and experience level.\n"
    "- Recommend specific certifications, courses, and projects.\n"
    "- Use Markdown formatting for clarity.\n"
    "- Be encouraging but honest about the effort required.\n"
    "- Include salary ranges and job market insights when relevant.\n"
    "- Suggest networking and portfolio-building strategies."
)


def build_career_advice_prompt(
    question: str,
    student_context: str,
    retrieved_resources: str = "",
) -> str:
    """Build a prompt for career advice.

    Args:
        question: The student's career-related question.
        student_context: Student profile information.
        retrieved_resources: Relevant career pathway data from RAG.

    Returns:
        A complete prompt string.
    """
    parts = []
    if student_context:
        parts.append(f"### Student Profile\n{student_context}\n")
    if retrieved_resources:
        parts.append(f"### Career Pathway Data\n{retrieved_resources}\n")
    parts.append(f"### Career Question\n{question}\n")
    parts.append("Provide detailed career advice:")

    return "\n".join(parts)


def build_career_transition_prompt(
    current_role: str,
    target_role: str,
    student_context: str,
    skill_analysis: str = "",
) -> str:
    """Build a prompt for career transition advice.

    Args:
        current_role: The student's current role/skill level.
        target_role: The desired career role.
        student_context: Student profile information.
        skill_analysis: Skill gap analysis results.

    Returns:
        A complete prompt string.
    """
    parts = [
        f"### Student Profile\n{student_context}\n",
        f"### Career Transition Request",
        f"From: {current_role}",
        f"To: {target_role}\n",
    ]

    if skill_analysis:
        parts.append(f"### Skill Gap Analysis\n{skill_analysis}\n")

    parts.append(
        "Provide a detailed transition plan including:\n"
        "1. Skills to learn (prioritized)\n"
        "2. Recommended certifications\n"
        "3. Portfolio projects to build\n"
        "4. Timeline estimate\n"
        "5. Job market insights"
    )

    return "\n".join(parts)
