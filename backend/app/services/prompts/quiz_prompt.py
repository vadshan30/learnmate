"""Quiz generation prompt templates for LearnMate AI.

Provides prompt builders for quizzes, flashcards, and coding challenges.
All prompts instruct Gemini to return structured JSON output.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


QUIZ_SYSTEM_INSTRUCTION = (
    "You are an expert quiz creator for LearnMate AI. "
    "Generate educational quizzes as valid JSON.\n"
    "Return ONLY the JSON object, no markdown fences, no explanations.\n\n"
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

FLASHCARD_SYSTEM_INSTRUCTION = (
    "You are an expert educator creating study flashcards for LearnMate AI.\n"
    "Generate flashcards as valid JSON.\n"
    "Return ONLY the JSON object, no markdown fences.\n\n"
    "REQUIRED JSON SCHEMA:\n"
    "{\n"
    '  "topic": "string",\n'
    '  "flashcards": [\n'
    "    {\n"
    '      "front": "Question or term",\n'
    '      "back": "Answer or definition",\n'
    '      "hint": "Optional hint"\n'
    "    }\n"
    "  ]\n"
    "}"
)

CODING_CHALLENGE_SYSTEM_INSTRUCTION = (
    "You are an expert coding challenge designer for LearnMate AI.\n"
    "Generate coding challenges as valid JSON.\n"
    "Return ONLY the JSON object, no markdown fences.\n\n"
    "REQUIRED JSON SCHEMA:\n"
    "{\n"
    '  "title": "string",\n'
    '  "difficulty": "easy|medium|hard",\n'
    '  "description": "string",\n'
    '  "examples": [{"input": "string", "output": "string", "explanation": "string"}],\n'
    '  "constraints": ["string"],\n'
    '  "hints": ["string"],\n'
    '  "solution_approach": "string"\n'
    "}"
)


def build_quiz_generation_prompt(
    topic: str,
    num_questions: int = 5,
    difficulty: str = "intermediate",
    student_context: str = "",
) -> str:
    """Build a prompt for quiz generation.

    Args:
        topic: The quiz topic.
        num_questions: Number of questions to generate.
        difficulty: Difficulty level.
        student_context: Student profile for personalisation.

    Returns:
        A complete prompt string.
    """
    parts = []
    if student_context:
        parts.append(f"### Student Context\n{student_context}\n")

    parts.append(
        f"### Quiz Requirements\n"
        f"Topic: {topic}\n"
        f"Number of questions: {num_questions}\n"
        f"Difficulty: {difficulty}\n\n"
        f"Generate {num_questions} multiple-choice questions about {topic}.\n"
        f"Each question should have 4 options (A, B, C, D).\n"
        f"Include the correct answer and a brief explanation for each.\n"
        f"Make questions progressively harder within the difficulty level."
    )

    return "\n".join(parts)


def build_flashcard_prompt(
    topic: str,
    num_cards: int = 10,
    student_context: str = "",
) -> str:
    """Build a prompt for flashcard generation.

    Args:
        topic: The flashcard topic.
        num_cards: Number of flashcards to generate.
        student_context: Student profile for personalisation.

    Returns:
        A complete prompt string.
    """
    parts = []
    if student_context:
        parts.append(f"### Student Context\n{student_context}\n")

    parts.append(
        f"### Flashcard Requirements\n"
        f"Topic: {topic}\n"
        f"Number of cards: {num_cards}\n\n"
        f"Generate {num_cards} study flashcards about {topic}.\n"
        f"Each flashcard should have a clear front (question/term) and "
        f"a comprehensive back (answer/definition).\n"
        f"Include helpful hints where appropriate.\n"
        f"Cover key concepts, terminology, and practical applications."
    )

    return "\n".join(parts)


def build_coding_challenge_prompt(
    topic: str,
    difficulty: str = "medium",
    language: str = "Python",
    student_context: str = "",
) -> str:
    """Build a prompt for coding challenge generation.

    Args:
        topic: The coding challenge topic/category.
        difficulty: Difficulty level (easy, medium, hard).
        language: Programming language.
        student_context: Student profile for personalisation.

    Returns:
        A complete prompt string.
    """
    parts = []
    if student_context:
        parts.append(f"### Student Context\n{student_context}\n")

    parts.append(
        f"### Coding Challenge Requirements\n"
        f"Topic: {topic}\n"
        f"Difficulty: {difficulty}\n"
        f"Language: {language}\n\n"
        f"Generate a coding challenge about {topic} in {language}.\n"
        f"Include:\n"
        f"- Clear problem description\n"
        f"- At least 2 examples with input/output\n"
        f"- Constraints and edge cases\n"
        f"- Helpful hints (without giving away the solution)\n"
        f"- A high-level solution approach"
    )

    return "\n".join(parts)
