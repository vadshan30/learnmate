"""Mentor prompt templates for LearnMate AI.

Provides system instructions and prompt builders for concept
explanation and general mentor features.
"""

from __future__ import annotations


EXPLAIN_SYSTEM_INSTRUCTION = (
    "You are LearnMate AI, an expert educator and technical communicator. "
    "Your role is to explain concepts at the student's level, using clear "
    "language, relevant examples, and practical applications.\n\n"
    "EXPLANATION GUIDELINES:\n"
    "- Start with a brief, clear definition.\n"
    "- Use analogies and real-world examples.\n"
    "- Include code examples when relevant (use proper Markdown code blocks).\n"
    "- Break complex ideas into smaller, digestible parts.\n"
    "- End with key takeaways or a summary.\n"
    "- Adapt your depth to the student's skill level.\n"
    "- Use Markdown formatting (headers, code blocks, lists) for clarity."
)


def build_explain_prompt(
    concept: str,
    student_context: str = "",
    level: str = "intermediate",
) -> str:
    """Build a prompt for concept explanation.

    Args:
        concept: The concept to explain.
        student_context: Student profile for personalisation.
        level: Difficulty level (beginner, intermediate, advanced).

    Returns:
        A complete prompt string.
    """
    level_guide = {
        "beginner": "Use simple analogies, everyday examples, and avoid jargon. Explain as if teaching someone completely new.",
        "intermediate": "Assume basic programming knowledge. Use technical terms but explain them. Include some code examples.",
        "advanced": "Provide deep technical details, implementation patterns, edge cases, and performance considerations.",
    }

    parts = [f"### Concept to Explain\n{concept}\n"]
    parts.append(f"### Difficulty Level: {level}")
    parts.append(f"### Level Guide: {level_guide.get(level, level_guide['intermediate'])}\n")

    if student_context:
        parts.append(f"### Student Context\n{student_context}\n")

    parts.append("Provide a clear, well-structured explanation:")

    return "\n".join(parts)
