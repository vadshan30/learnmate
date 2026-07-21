"""Resource Service for LearnMate AI.

Provides a unified interface for accessing courses, projects,
certifications, and career pathways from JSON datasets. Includes
filtering, search, and recommendation capabilities.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.utils.data_loader import (
    load_courses,
    load_projects,
    load_certifications,
    load_career_pathways,
    load_books,
)

logger = logging.getLogger("learnmate.resources")


def get_all_courses() -> List[Dict[str, Any]]:
    """Get all courses from the dataset.

    Returns:
        List of course dicts.
    """
    return load_courses()


def get_course(course_id: str) -> Optional[Dict[str, Any]]:
    """Get a single course by ID.

    Args:
        course_id: The course identifier.

    Returns:
        Course dict if found, None otherwise.
    """
    courses = load_courses()
    for c in courses:
        if c.get("id") == course_id:
            return c
    return None


def get_projects() -> List[Dict[str, Any]]:
    """Get all projects from the dataset.

    Returns:
        List of project dicts.
    """
    return load_projects()


def get_certifications() -> List[Dict[str, Any]]:
    """Get all certifications from the dataset.

    Returns:
        List of certification dicts.
    """
    return load_certifications()


def get_career_pathways() -> List[Dict[str, Any]]:
    """Get all career pathways from the dataset.

    Returns:
        List of career pathway dicts.
    """
    return load_career_pathways()


def get_all_books() -> List[Dict[str, Any]]:
    """Get all books from the dataset.

    Returns:
        List of book dicts.
    """
    return load_books()


def get_book(book_id: str) -> Optional[Dict[str, Any]]:
    """Get a single book by ID.

    Args:
        book_id: The book identifier.

    Returns:
        Book dict if found, None otherwise.
    """
    books = load_books()
    for b in books:
        if b.get("id") == book_id:
            return b
    return None


def search_resources(
    query: str,
    top_k: int = 10,
    difficulty: Optional[str] = None,
    domain: Optional[str] = None,
    provider: Optional[str] = None,
    skills: Optional[List[str]] = None,
    resource_type: Optional[str] = None,
    free: Optional[bool] = None,
) -> List[Dict[str, Any]]:
    """Search across all resource types.

    Args:
        query: Search query string.
        top_k: Maximum results to return.
        difficulty: Filter by difficulty level.
        domain: Filter by domain/category.
        provider: Filter by provider.
        skills: Filter by required skills.
        resource_type: Filter by type (course, project, certification).
        free: Filter by free status (True = free only, False = paid only, None = all).

    Returns:
        List of matching resource dicts with relevance scoring.
    """
    results: List[Dict[str, Any]] = []
    query_lower = query.lower().strip()

    # Load all resources (copy to avoid mutating source data)
    if resource_type is None or resource_type == "course":
        for item in get_all_courses():
            results.append({**item, "_type": "course"})

    if resource_type is None or resource_type == "project":
        for item in get_projects():
            results.append({**item, "_type": "project"})

    if resource_type is None or resource_type == "certification":
        for item in get_certifications():
            results.append({**item, "_type": "certification"})

    if resource_type is None or resource_type == "book":
        for item in get_all_books():
            results.append({**item, "_type": "book"})

    # Score each result
    scored: List[Dict[str, Any]] = []
    for item in results:
        score = _score_item(item, query_lower)
        if score > 0:
            item["relevance_score"] = score
            scored.append(item)

    # Apply filters
    if difficulty:
        scored = [
            item for item in scored
            if _matches_difficulty(item, difficulty)
        ]

    if domain:
        domain_lower = domain.lower().strip()
        scored = [
            item for item in scored
            if domain_lower in (item.get("domain", "") or "").lower()
            or domain_lower in (item.get("category", "") or "").lower()
        ]

    if provider:
        provider_lower = provider.lower().strip()
        scored = [
            item for item in scored
            if provider_lower in (item.get("provider", "") or "").lower()
        ]

    if skills:
        skills_lower = {s.lower().strip() for s in skills}
        scored = [
            item for item in scored
            if _has_matching_skill(item, skills_lower)
        ]

    if free is not None:
        scored = [
            item for item in scored
            if item.get("free", False) == free
        ]

    # Sort by score descending
    scored.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

    return scored[:top_k]


def get_recommended_courses(
    student_id: Optional[str] = None,
    skills: Optional[List[str]] = None,
    career_goal: Optional[str] = None,
    top_k: int = 10,
) -> List[Dict[str, Any]]:
    """Get recommended courses based on skills or career goal.

    Args:
        student_id: Optional student ID for profile lookup.
        skills: Skills to match against.
        career_goal: Career goal to search for.
        top_k: Maximum results.

    Returns:
        List of recommended course dicts.
    """
    query_parts = []
    if skills:
        query_parts.extend(skills[:5])
    if career_goal:
        query_parts.append(career_goal)

    if not query_parts:
        return get_all_courses()[:top_k]

    query = " ".join(query_parts)
    return search_resources(query, top_k=top_k, resource_type="course")


def filter_by_domain(domain: str) -> List[Dict[str, Any]]:
    """Filter all resources by domain.

    Args:
        domain: Domain/category to filter by.

    Returns:
        List of matching resources.
    """
    all_resources = (
        get_all_courses() + get_projects() + get_certifications() + get_all_books()
    )
    domain_lower = domain.lower().strip()
    return [
        r for r in all_resources
        if domain_lower in (r.get("domain", "") or "").lower()
        or domain_lower in (r.get("category", "") or "").lower()
    ]


def filter_by_difficulty(difficulty: str) -> List[Dict[str, Any]]:
    """Filter all resources by difficulty level.

    Args:
        difficulty: Difficulty level to filter by.

    Returns:
        List of matching resources.
    """
    all_resources = (
        get_all_courses() + get_projects() + get_certifications() + get_all_books()
    )
    return [
        r for r in all_resources
        if _matches_difficulty(r, difficulty)
    ]


# ── Internal helpers ──────────────────────────────────────────────────


def _score_item(item: Dict[str, Any], query_lower: str) -> float:
    """Score a resource item against a query.

    Higher score = more relevant.

    Args:
        item: Resource dict.
        query_lower: Lowercased query string.

    Returns:
        Relevance score (0.0 to 1.0).
    """
    score = 0.0
    query_words = query_lower.split()

    # Check title/name (certifications use 'name', courses/projects use 'title')
    title = (item.get("name") or item.get("title") or "").lower()
    if query_lower in title:
        score += 0.5
    elif any(w in title for w in query_words):
        score += 0.3

    # Check description
    desc = (item.get("description") or "").lower()
    if any(w in desc for w in query_words):
        score += 0.2

    # Check skills (certifications use 'skills_covered', others vary)
    skills = (
        item.get("skills_gained")
        or item.get("skills_covered")
        or item.get("required_skills")
        or item.get("skills")
        or []
    )
    skills_str = " ".join(str(s).lower() for s in skills)
    if any(w in skills_str for w in query_words):
        score += 0.2

    # Check tags
    tags = item.get("tags") or []
    tags_str = " ".join(str(t).lower() for t in tags)
    if any(w in tags_str for w in query_words):
        score += 0.15

    # Check domain/category
    domain = (item.get("domain") or item.get("category") or "").lower()
    if any(w in domain for w in query_words):
        score += 0.1

    # Check provider
    provider = (item.get("provider") or "").lower()
    if any(w in provider for w in query_words):
        score += 0.05

    return min(score, 1.0)


def _matches_difficulty(item: Dict[str, Any], difficulty: str) -> bool:
    """Check if an item matches a difficulty filter.

    Args:
        item: Resource dict.
        difficulty: Difficulty string to match.

    Returns:
        True if the item matches.
    """
    level = item.get("level") or item.get("difficulty") or ""
    if isinstance(level, dict):
        level = level.get("value", "")
    level_str = str(level).lower().strip()
    diff_lower = difficulty.lower().strip()

    # Support aliases
    alias_map = {
        "easy": "beginner",
        "medium": "intermediate",
        "hard": "advanced",
    }
    target = alias_map.get(diff_lower, diff_lower)

    return target in level_str


def _has_matching_skill(
    item: Dict[str, Any], skills_lower: set[str]
) -> bool:
    """Check if an item has any of the required skills.

    Args:
        item: Resource dict.
        skills_lower: Set of lowercased skill names.

    Returns:
        True if any skill matches.
    """
    item_skills = (
        item.get("skills_gained")
        or item.get("skills_covered")
        or item.get("required_skills")
        or item.get("skills")
        or []
    )
    item_skills_lower = {str(s).lower().strip() for s in item_skills}
    return bool(skills_lower & item_skills_lower)
