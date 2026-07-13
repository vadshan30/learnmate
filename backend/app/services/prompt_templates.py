"""Granite Prompt Templates for LearnMate AI.

Provides reusable prompt builders for roadmap generation, mentor chat,
and skill analysis. Each template constructs a system+user prompt pair
that instructs IBM Granite to produce structured, deterministic output.

All prompts enforce:
- JSON-only responses (no markdown fences, no prose)
- Explicit schema instructions
- Context-aware student profiling
- Deterministic structure for reliable parsing
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Roadmap Generation Prompt
# ---------------------------------------------------------------------------


def build_roadmap_prompt(
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

    Constructs a system+user prompt pair that instructs Granite to produce
    a 10-week personalised learning roadmap as a valid JSON object.

    Args:
        student_name: Name of the student.
        career_goal: Target career role.
        current_skills: Skills the student already possesses.
        interests: Domain interests of the student.
        skill_level: Self-assessed proficiency level.
        missing_skills: Skills identified as gaps by the analyzer.
        coverage_percentage: Career readiness percentage.
        courses: Serialised course catalog for context.
        projects: Serialised project list for context.
        certifications: Serialised certification list for context.

    Returns:
        A complete prompt string ready to send to Granite.
    """
    system_instruction = (
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
        "- Include a meaningful assessment and 2-3 learning outcomes per "
        "week.\n\n"
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

    skills_str = ", ".join(current_skills) if current_skills else "None"
    interests_str = ", ".join(interests) if interests else "None"
    missing_str = ", ".join(missing_skills) if missing_skills else "None"

    user_content = (
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

    return f"{system_instruction}\n\n{user_content}"


# ---------------------------------------------------------------------------
# Mentor Chat Prompt
# ---------------------------------------------------------------------------


def build_mentor_prompt(
    user_message: str,
    student_context: str,
    retrieved_resources: str,
) -> str:
    """Build a prompt for the AI learning mentor.

    Constructs a context-rich prompt that enables Granite to provide
    supportive, accurate, and actionable learning guidance.

    Args:
        user_message: The student's question or message.
        student_context: Summarised student profile and progress.
        retrieved_resources: Relevant courses/resources from RAG search.

    Returns:
        A complete prompt string ready to send to Granite.
    """
    system_instruction = (
        "You are LearnMate AI, a supportive and knowledgeable learning "
        "mentor. Your role is to help students achieve their learning "
        "goals through clear, actionable guidance.\n\n"
        "GUIDELINES:\n"
        "- Be encouraging, positive, and empathetic.\n"
        "- Explain concepts clearly with practical examples.\n"
        "- Recommend specific courses ONLY from the provided resources.\n"
        "- Suggest hands-on projects when appropriate.\n"
        "- Never hallucinate course names or resources not provided.\n"
        "- If you lack enough information, say so honestly.\n"
        "- Keep responses concise (under 300 words) and actionable.\n"
        "- Use numbered lists for recommendations.\n"
        "- Encourage hands-on learning and consistent practice."
    )

    user_content = (
        f"### Student Profile\n{student_context}\n\n"
        f"### Relevant Learning Resources\n{retrieved_resources}\n\n"
        f"### Student Question\n{user_message}\n\n"
        "Provide a helpful, personalised response:"
    )

    return f"{system_instruction}\n\n{user_content}"


# ---------------------------------------------------------------------------
# Skill Analysis Prompt
# ---------------------------------------------------------------------------


def build_skill_analysis_prompt(
    student_name: str,
    current_skills: List[str],
    interests: List[str],
    career_goal: str,
    skill_level: str,
    completed_topics: List[str],
    required_skills: List[str],
    career_description: str,
) -> str:
    """Build a prompt for AI-powered skill gap analysis.

    Instructs Granite to evaluate student readiness, identify weaknesses,
    and suggest improvements in a structured JSON format.

    Args:
        student_name: Name of the student.
        current_skills: Skills the student already has.
        interests: Domain interests.
        career_goal: Target career role.
        skill_level: Self-assessed proficiency level.
        completed_topics: Topics already completed.
        required_skills: Skills required by the career path.
        career_description: Description of the career pathway.

    Returns:
        A complete prompt string ready to send to Granite.
    """
    system_instruction = (
        "You are an expert career advisor and learning analyst for "
        "LearnMate AI. Evaluate the student's readiness for their "
        "target career role.\n\n"
        "RULES:\n"
        "- Return ONLY valid JSON. No markdown, no explanations.\n"
        "- Be honest and specific about gaps.\n"
        "- Prioritise skills that are foundational prerequisites.\n"
        "- Consider the student's current level when suggesting "
        "improvements.\n\n"
        "REQUIRED JSON SCHEMA:\n"
        "{\n"
        '  "readiness_score": 0-100,\n'
        '  "strengths": ["skill1", "skill2"],\n'
        '  "weaknesses": ["skill1", "skill2"],\n'
        '  "priority_order": ["skill1", "skill2"],\n'
        '  "recommendations": ["advice1", "advice2"]\n'
        "}"
    )

    skills_str = ", ".join(current_skills) if current_skills else "None"
    interests_str = ", ".join(interests) if interests else "None"
    topics_str = ", ".join(completed_topics) if completed_topics else "None"
    required_str = ", ".join(required_skills)

    user_content = (
        f"### Student: {student_name}\n"
        f"Skill Level: {skill_level}\n"
        f"Current Skills: {skills_str}\n"
        f"Interests: {interests_str}\n"
        f"Completed Topics: {topics_str}\n\n"
        f"### Target Career: {career_goal}\n"
        f"Description: {career_description}\n"
        f"Required Skills: {required_str}\n\n"
        "Evaluate readiness and identify gaps:"
    )

    return f"{system_instruction}\n\n{user_content}"


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------


def serialize_courses_for_prompt(
    courses: List[Dict[str, Any]],
) -> str:
    """Serialize a list of course dicts into a readable prompt string.

    Args:
        courses: List of course dictionaries with keys like
                 title, domain, level, skills_gained.

    Returns:
        A formatted string summarising each course.
    """
    if not courses:
        return "No courses available."

    lines = []
    for i, course in enumerate(courses, 1):
        title = course.get("title", course.get("name", "Unknown"))
        domain = course.get("domain", "")
        level = course.get("level", "")
        skills = course.get("skills_gained", course.get("skills", []))
        skills_str = ", ".join(skills) if skills else "N/A"

        lines.append(
            f"{i}. {title} ({domain}, {level}) - Skills: {skills_str}"
        )

    return "\n".join(lines)


def serialize_projects_for_prompt(
    projects: List[Dict[str, Any]],
) -> str:
    """Serialize a list of project dicts into a readable prompt string.

    Args:
        projects: List of project dictionaries with keys like
                  title, difficulty, skills_required, technologies.

    Returns:
        A formatted string summarising each project.
    """
    if not projects:
        return "No projects available."

    lines = []
    for i, project in enumerate(projects, 1):
        title = project.get("title", "Unknown")
        difficulty = project.get("difficulty", "")
        skills = project.get("skills_required", project.get("skills", []))
        skills_str = ", ".join(skills) if skills else "N/A"

        lines.append(
            f"{i}. {title} ({difficulty}) - Skills: {skills_str}"
        )

    return "\n".join(lines)


def serialize_certifications_for_prompt(
    certifications: List[Dict[str, Any]],
) -> str:
    """Serialize certification dicts into a readable prompt string.

    Args:
        certifications: List of certification dictionaries with keys like
                        name, provider, level, skills_covered.

    Returns:
        A formatted string summarising each certification.
    """
    if not certifications:
        return "No certifications available."

    lines = []
    for i, cert in enumerate(certifications, 1):
        name = cert.get("name", "Unknown")
        provider = cert.get("provider", "")
        level = cert.get("level", "")
        skills = cert.get("skills_covered", cert.get("skills", []))
        skills_str = ", ".join(skills) if skills else "N/A"

        lines.append(
            f"{i}. {name} ({provider}, {level}) - Skills: {skills_str}"
        )

    return "\n".join(lines)
