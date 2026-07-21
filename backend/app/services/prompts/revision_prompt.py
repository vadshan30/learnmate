"""Revision and AI features prompt templates for LearnMate AI.

Provides prompt builders for revision assistance, weekly feedback,
resume review, interview preparation, and learning tips.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


REVISION_SYSTEM_INSTRUCTION = (
    "You are LearnMate AI, an expert revision assistant. "
    "Help students review and reinforce their learning through "
    "structured revision techniques.\n\n"
    "GUIDELINES:\n"
    "- Use evidence-based study techniques (spaced repetition, active recall).\n"
    "- Create clear, organized revision materials.\n"
    "- Include key formulas, concepts, and patterns.\n"
    "- Provide practice questions where appropriate.\n"
    "- Use Markdown formatting for clarity.\n"
    "- Adapt to the student's learning style and level."
)

WEEKLY_FEEDBACK_SYSTEM_INSTRUCTION = (
    "You are LearnMate AI, an expert learning analytics coach. "
    "Analyze the student's weekly progress and provide constructive feedback.\n\n"
    "GUIDELINES:\n"
    "- Be specific about what went well and what needs improvement.\n"
    "- Provide actionable recommendations for the next week.\n"
    "- Celebrate achievements and milestones.\n"
    "- Identify patterns in learning behavior.\n"
    "- Use Markdown formatting with clear sections."
)

RESUME_REVIEW_SYSTEM_INSTRUCTION = (
    "You are LearnMate AI, an expert career coach and resume reviewer. "
    "Provide detailed, actionable feedback on resumes.\n\n"
    "GUIDELINES:\n"
    "- Check for clarity, relevance, and impact of each section.\n"
    "- Suggest specific improvements with examples.\n"
    "- Highlight strengths and areas for improvement.\n"
    "- Consider ATS (Applicant Tracking System) optimization.\n"
    "- Use Markdown formatting with clear sections and bullet points."
)

INTERVIEW_PREP_SYSTEM_INSTRUCTION = (
    "You are LearnMate AI, an expert interview coach. "
    "Help students prepare for technical and behavioral interviews.\n\n"
    "GUIDELINES:\n"
    "- Provide realistic interview questions.\n"
    "- Give structured answer frameworks (STAR method for behavioral).\n"
    "- Include follow-up questions and edge cases.\n"
    "- Adapt questions to the student's career goal and skill level.\n"
    "- Use Markdown formatting for clarity."
)

LEARNING_TIPS_SYSTEM_INSTRUCTION = (
    "You are LearnMate AI, an expert in learning science and "
    "educational psychology. Provide evidence-based learning tips.\n\n"
    "GUIDELINES:\n"
    "- Base tips on cognitive science research.\n"
    "- Make tips practical and immediately actionable.\n"
    "- Adapt to the student's learning style and goals.\n"
    "- Use Markdown formatting with clear, concise tips."
)


def build_revision_prompt(
    topic: str,
    student_context: str = "",
    focus_areas: Optional[List[str]] = None,
) -> str:
    """Build a prompt for revision assistance.

    Args:
        topic: The topic to revise.
        student_context: Student profile for personalisation.
        focus_areas: Specific areas to focus revision on.

    Returns:
        A complete prompt string.
    """
    parts = []
    if student_context:
        parts.append(f"### Student Context\n{student_context}\n")

    parts.append(f"### Revision Topic\n{topic}\n")

    if focus_areas:
        parts.append(f"### Focus Areas\n{', '.join(focus_areas)}\n")

    parts.append(
        "Create a comprehensive revision guide including:\n"
        "1. Key concepts and definitions\n"
        "2. Important formulas or patterns\n"
        "3. Common mistakes to avoid\n"
        "4. Practice questions with answers\n"
        "5. Quick reference summary"
    )

    return "\n".join(parts)


def build_weekly_feedback_prompt(
    progress_data: str,
    student_context: str,
) -> str:
    """Build a prompt for weekly progress feedback.

    Args:
        progress_data: Summary of weekly progress data.
        student_context: Student profile information.

    Returns:
        A complete prompt string.
    """
    parts = [
        f"### Student Profile\n{student_context}\n",
        f"### Weekly Progress Data\n{progress_data}\n",
        "Provide constructive weekly feedback including:\n"
        "1. Achievements and milestones\n"
        "2. Areas that need more attention\n"
        "3. Specific recommendations for next week\n"
        "4. Motivation and encouragement",
    ]

    return "\n".join(parts)


def build_resume_review_prompt(
    resume_text: str,
    student_context: str = "",
    target_role: str = "",
) -> str:
    """Build a prompt for resume review.

    Args:
        resume_text: The resume content to review.
        student_context: Student profile for context.
        target_role: Target job role for tailoring.

    Returns:
        A complete prompt string.
    """
    parts = []
    if student_context:
        parts.append(f"### Student Profile\n{student_context}\n")
    if target_role:
        parts.append(f"### Target Role: {target_role}\n")

    parts.append(
        f"### Resume to Review\n{resume_text}\n\n"
        "Provide a detailed resume review:\n"
        "1. Overall impression and score (1-10)\n"
        "2. Strengths\n"
        "3. Areas for improvement (with specific suggestions)\n"
        "4. ATS optimization tips\n"
        "5. Section-by-section feedback\n"
        "6. Action items to improve the resume"
    )

    return "\n".join(parts)


def build_interview_prep_prompt(
    role: str,
    student_context: str = "",
    num_questions: int = 5,
    focus: str = "mixed",
) -> str:
    """Build a prompt for interview preparation.

    Args:
        role: The job role to prepare for.
        student_context: Student profile for personalisation.
        num_questions: Number of questions to generate.
        focus: Focus area (technical, behavioral, mixed).

    Returns:
        A complete prompt string.
    """
    parts = []
    if student_context:
        parts.append(f"### Student Profile\n{student_context}\n")

    parts.append(
        f"### Interview Preparation\n"
        f"Role: {role}\n"
        f"Number of questions: {num_questions}\n"
        f"Focus: {focus}\n\n"
        f"Generate {num_questions} interview questions for a {role} position.\n"
        f"For each question:\n"
        f"- Provide the question\n"
        f"- Give a strong sample answer\n"
        f"- List key points the answer should cover\n"
        f"- Include common follow-up questions\n"
    )

    if focus == "behavioral" or focus == "mixed":
        parts.append("Use the STAR method for behavioral questions.")

    return "\n".join(parts)


def build_learning_tips_prompt(
    student_context: str = "",
    specific_area: str = "",
) -> str:
    """Build a prompt for personalized learning tips.

    Args:
        student_context: Student profile for personalisation.
        specific_area: Specific area to focus tips on.

    Returns:
        A complete prompt string.
    """
    parts = []
    if student_context:
        parts.append(f"### Student Profile\n{student_context}\n")
    if specific_area:
        parts.append(f"### Focus Area: {specific_area}\n")

    parts.append(
        "Provide personalized learning tips:\n"
        "1. Study techniques that match the student's learning style\n"
        "2. Time management strategies\n"
        "3. Memory and retention techniques\n"
        "4. Practice and application methods\n"
        "5. Motivation and consistency tips\n\n"
        "Make tips specific, actionable, and backed by learning science."
    )

    return "\n".join(parts)
