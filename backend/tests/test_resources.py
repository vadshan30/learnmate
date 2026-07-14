"""Tests for the Resource Service."""

import sys
import os

# Ensure backend is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_load_courses():
    from app.services.resource_service import get_all_courses

    courses = get_all_courses()
    assert len(courses) >= 20, f"Expected 20+ courses, got {len(courses)}"
    for c in courses:
        assert "id" in c, f"Course missing 'id': {c}"
        assert "title" in c, f"Course missing 'title': {c}"
        assert "domain" in c, f"Course missing 'domain': {c}"
        assert "provider" in c, f"Course missing 'provider': {c}"


def test_load_projects():
    from app.services.resource_service import get_projects

    projects = get_projects()
    assert len(projects) >= 10, f"Expected 10+ projects, got {len(projects)}"


def test_load_certifications():
    from app.services.resource_service import get_certifications

    certs = get_certifications()
    assert len(certs) >= 8, f"Expected 8+ certifications, got {len(certs)}"


def test_load_career_pathways():
    from app.services.resource_service import get_career_pathways

    pathways = get_career_pathways()
    assert len(pathways) >= 5, f"Expected 5+ career pathways, got {len(pathways)}"


def test_get_course_by_id():
    from app.services.resource_service import get_course

    course = get_course("course-001")
    assert course is not None
    assert course["title"] == "Python Fundamentals"

    missing = get_course("nonexistent")
    assert missing is None


def test_search_courses():
    from app.services.resource_service import search_resources

    results = search_resources("python", top_k=5)
    assert len(results) > 0, "Search for 'python' should return results"
    assert any("python" in str(r.get("title", "")).lower() or "python" in str(r.get("skills_gained", [])).lower() for r in results)


def test_search_by_difficulty():
    from app.services.resource_service import search_resources

    results = search_resources("web", difficulty="beginner")
    for r in results:
        level = str(r.get("level", "") or r.get("difficulty", "")).lower()
        assert "beginner" in level or "easy" in level


def test_search_by_domain():
    from app.services.resource_service import search_resources

    results = search_resources("development", domain="Data Science")
    for r in results:
        domain = str(r.get("domain", "") or r.get("category", "")).lower()
        assert "data science" in domain


def test_filter_by_domain():
    from app.services.resource_service import filter_by_domain

    results = filter_by_domain("DevOps")
    assert len(results) > 0
    for r in results:
        domain = str(r.get("domain", "") or r.get("category", "")).lower()
        assert "devops" in domain


def test_filter_by_difficulty():
    from app.services.resource_service import filter_by_difficulty

    results = filter_by_difficulty("Advanced")
    assert len(results) > 0
    for r in results:
        level = str(r.get("level", r.get("difficulty", ""))).lower()
        assert "advanced" in level or "hard" in level


if __name__ == "__main__":
    test_load_courses()
    test_load_projects()
    test_load_certifications()
    test_load_career_pathways()
    test_get_course_by_id()
    test_search_courses()
    test_search_by_difficulty()
    test_search_by_domain()
    test_filter_by_domain()
    test_filter_by_difficulty()
    print("All resource tests passed!")
