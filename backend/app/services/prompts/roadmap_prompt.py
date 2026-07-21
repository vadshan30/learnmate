"""Roadmap and study plan prompt templates for LearnMate AI.

Provides prompt builders for roadmap generation, study plans,
and revision schedules.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


ROADMAP_SYSTEM_INSTRUCTION = (
    "You are an expert learning roadmap designer for the LearnMate AI "
    "platform. Generate a personalised 10-week learning roadmap.\n\n"
    "RULES:\n"
    "- Return ONLY valid JSON. No markdown fences, no explanations.\n"
    "- Generate exactly 10 weeks.\n"
    "- Teach prerequisites first, then intermediate, then advanced.\n"
    "- Include 2-4 topics per week.\n"
    "- Include 1-2 courses per week when available.\n"
    "- Include a project every 2-3 weeks.\n"
    "- Place certification preparation in week 9.\n"
    "- Place the capstone project in week 10.\n"
    "- Estimated hours should be realistic (8-15 per week).\n"
    "- Include a meaningful assessment and 2-3 learning outcomes per week.\n\n"
    "REQUIRED JSON SCHEMA:\n"
    "{\n"
    '  "weeks": [\n'
    "    {\n"
    '      "week_number": 1,\n'
    '      "goal": "Learning objective for the week",\n'
    '      "topics": ["topic1", "topic2"],\n'
    '      "courses": ["Course Title"],\n'
    '      "projects": ["Project Name"],\n'
    '      "hours": 10,\n'
    '      "assessment": "Description of assessment",\n'
    '      "learning_outcomes": ["outcome1", "outcome2"]\n'
    "    }\n"
    "  ]\n"
    "}"
)

STUDY_PLAN_SYSTEM_INSTRUCTION = (
    "You are an expert learning coach for LearnMate AI. "
    "Generate a structured daily study plan as valid JSON.\n"
    "Return ONLY the JSON object, no markdown fences.\n\n"
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

REVISION_SCHEDULE_SYSTEM_INSTRUCTION = (
    "You are an expert study planner for LearnMate AI. "
    "Generate a revision schedule as valid JSON.\n"
    "Return ONLY the JSON object, no markdown fences.\n\n"
    "REQUIRED JSON SCHEMA:\n"
    "{\n"
    '  "schedule_name": "string",\n'
    '  "duration": "string",\n'
    '  "revision_blocks": [\n'
    "    {\n"
    '      "day": "string",\n'
    '      "topics": ["string"],\n'
    '      "activities": [\n'
    "        {\n"
    '          "time": "string",\n'
    '          "task": "string",\n'
    '          "technique": "spaced_repetition|active_recall|practice_test|mind_map|flashcards"\n'
    "        }\n"
    "      ]\n"
    "    }\n"
    "  ],\n"
    '  "tips": ["string"]\n'
    "}"
)


def build_roadmap_generation_prompt(
    student_name: str,
    career_goal: str,
    current_skills: List[str],
    interests: List[str],
    skill_level: str,
    missing_skills: List[str],
    coverage_percentage: float,
    courses: str,
    projects: str,
    certifications: str,
) -> str:
    """Build a comprehensive prompt for AI roadmap generation.

    Args:
        student_name: Name of the student.
        career_goal: Target career role.
        current_skills: Skills the student already possesses.
        interests: Domain interests.
        skill_level: Self-assessed proficiency level.
        missing_skills: Skills identified as gaps.
        coverage_percentage: Career readiness percentage.
        courses: Serialised course catalog.
        projects: Serialised project list.
        certifications: Serialised certification list.

    Returns:
        A complete prompt string.
    """
    skills_str = ", ".join(current_skills) if current_skills else "None"
    interests_str = ", ".join(interests) if interests else "None"
    missing_str = ", ".join(missing_skills) if missing_skills else "None"

    return (
        f"### Student Profile\n"
        f"Name: {student_name}\n"
        f"Career Goal: {career_goal}\n"
        f"Current Skills: {skills_str}\n"
        f"Interests: {interests_str}\n"
        f"Skill Level: {skill_level}\n"
        f"Career Readiness: {coverage_percentage:.1f}%\n"
        f"Missing Skills to Learn: {missing_str}\n\n"
        f"### Available Courses\n{courses}\n\n"
        f"### Available Projects\n{projects}\n\n"
        f"### Available Certifications\n{certifications}\n\n"
        "### Week Structure Guide\n"
        "- Weeks 1-2: Prerequisites and foundational concepts\n"
        "- Weeks 3-5: Core intermediate skills\n"
        "- Weeks 6-8: Advanced topics and applied projects\n"
        "- Week 9: Certification preparation\n"
        "- Week 10: Capstone project and final review\n\n"
        "Return ONLY the JSON object:"
    )


def build_study_plan_prompt(
    request_context: str,
    student_context: str,
) -> str:
    """Build a prompt for daily study plan generation.

    Args:
        request_context: Details about what plan to create.
        student_context: Student profile information.

    Returns:
        A complete prompt string.
    """
    parts = [f"### Student Profile\n{student_context}\n"]
    parts.append(f"### Study Plan Request\n{request_context}\n")
    parts.append(
        "Create a detailed daily study plan that:\n"
        "1. Fits the student's available hours per week\n"
        "2. Balances theory, practice, and breaks\n"
        "3. Includes review sessions for retention\n"
        "4. Aligns with their career goal and current level\n"
        "Return ONLY the JSON object:"
    )
    return "\n".join(parts)


def build_revision_schedule_prompt(
    topics_to_revise: List[str],
    exam_date: str,
    student_context: str,
) -> str:
    """Build a prompt for revision schedule generation.

    Args:
        topics_to_revise: List of topics that need revision.
        exam_date: Target exam/assessment date.
        student_context: Student profile information.

    Returns:
        A complete prompt string.
    """
    topics_str = ", ".join(topics_to_revise) if topics_to_revise else "All learned topics"

    parts = [f"### Student Profile\n{student_context}\n"]
    parts.append(
        f"### Revision Schedule Request\n"
        f"Topics to revise: {topics_str}\n"
        f"Target date: {exam_date}\n\n"
        "Create a revision schedule that:\n"
        "1. Uses spaced repetition for better retention\n"
        "2. Includes active recall exercises\n"
        "3. Balances revision across all topics\n"
        "4. Incorporates practice tests\n"
        "5. Prioritizes weaker areas\n"
        "Return ONLY the JSON object:"
    )
    return "\n".join(parts)
