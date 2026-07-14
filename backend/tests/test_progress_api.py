"""Tests for the Progress API endpoints.

Verifies the full flow of topic completion including the critical
sync/async fix for update_roadmap and update_topic_completion.
"""

import sys
import os

# Ensure backend is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _sample_roadmap():
    return {
        "roadmap_id": "test-roadmap-001",
        "student_name": "Test Student",
        "career_goal": "Full Stack Developer",
        "total_duration": "10 weeks",
        "completed_topics": [],
        "total_topics": 5,
        "weeks": [
            {
                "week_number": 1,
                "title": "Week 1: Fundamentals",
                "topics": ["Python basics", "HTML fundamentals", "Git intro"],
                "projects": [],
                "assessments": ["Quiz 1"],
                "estimated_hours": 10.0,
                "completion_status": "pending",
                "completed": False,
            },
            {
                "week_number": 2,
                "title": "Week 2: Core Skills",
                "topics": ["CSS layouts", "JavaScript basics"],
                "projects": ["Mini project"],
                "assessments": ["Quiz 2"],
                "estimated_hours": 12.0,
                "completion_status": "pending",
                "completed": False,
            },
        ],
        "certifications": [
            {"id": "cert-001", "name": "AWS Cloud", "provider": "AWS"},
            {"id": "cert-002", "name": "Azure Fundamentals", "provider": "Microsoft"},
        ],
        "progress": {
            "completed_weeks": 0,
            "total_weeks": 2,
            "percentage": 0.0,
            "current_week": 1,
            "total_topics": 5,
            "completed_topics_count": 0,
            "week_progress": [],
            "completion_status": "not_started",
        },
        "skill_analysis": {
            "coverage_percentage": 30.0,
            "missing_skills": ["React", "Node.js", "SQL"],
            "matched_skills": ["Python", "Git"],
            "categorized_skills": {},
            "prerequisites": [],
        },
        "recommendations": [],
    }


def test_update_roadmap_returns_dict_not_coroutine():
    """CRITICAL: update_roadmap must return a dict, not a coroutine.

    This test verifies the fix for the 500 Internal Server Error where
    update_topic_completion (sync) called update_roadmap (async) without
    await, returning a coroutine object instead of the updated roadmap dict.
    """
    from app.services.roadmap_generator import RoadmapGenerator
    import asyncio

    gen = RoadmapGenerator()
    roadmap = _sample_roadmap()

    # update_roadmap is now sync — must return a dict directly
    result = gen.update_roadmap(roadmap, ["python basics"])

    assert isinstance(result, dict), (
        f"update_roadmap returned {type(result).__name__}, expected dict. "
        "The method may still be async or returning a coroutine."
    )
    assert "python basics" in result["completed_topics"]
    assert result["progress"]["completed_topics_count"] == 1
    assert result["progress"]["percentage"] > 0.0


def test_update_topic_completion_returns_dict_not_coroutine():
    """update_topic_completion must also return a dict (it delegates to update_roadmap)."""
    from app.services.roadmap_generator import RoadmapGenerator

    gen = RoadmapGenerator()
    roadmap = _sample_roadmap()

    result = gen.update_topic_completion(roadmap, "Python basics", True)

    assert isinstance(result, dict), (
        f"update_topic_completion returned {type(result).__name__}, expected dict."
    )
    assert "python basics" in result["completed_topics"]


def test_module_level_update_roadmap_is_sync():
    """The module-level convenience function must be sync (not async)."""
    import inspect
    from app.services.roadmap_generator import update_roadmap

    assert not inspect.iscoroutinefunction(update_roadmap), (
        "Module-level update_roadmap should not be a coroutine function"
    )


def test_update_roadmap_completes_week_when_all_topics_done():
    """Completing all topics in a week should mark the week as completed."""
    from app.services.roadmap_generator import RoadmapGenerator

    gen = RoadmapGenerator()
    roadmap = _sample_roadmap()

    # Complete all topics in week 1
    result = gen.update_roadmap(roadmap, [
        "python basics", "html fundamentals", "git intro"
    ])

    week1 = result["weeks"][0]
    assert week1["completion_status"] == "completed", (
        f"Week 1 should be completed, got '{week1['completion_status']}'"
    )


def test_update_roadmap_progress_percentage():
    """Progress percentage should update correctly after completing topics."""
    from app.services.roadmap_generator import RoadmapGenerator

    gen = RoadmapGenerator()
    roadmap = _sample_roadmap()

    # Complete 2 of 5 topics
    result = gen.update_roadmap(roadmap, ["python basics", "html fundamentals"])

    expected_pct = (2 / 5) * 100.0  # 40.0
    assert result["progress"]["percentage"] == expected_pct, (
        f"Expected {expected_pct}%, got {result['progress']['percentage']}%"
    )
    assert result["progress"]["completion_status"] == "in_progress"


def test_update_roadmap_100_percent():
    """Completing all topics should set progress to 100%."""
    from app.services.roadmap_generator import RoadmapGenerator

    gen = RoadmapGenerator()
    roadmap = _sample_roadmap()

    result = gen.update_roadmap(roadmap, [
        "python basics", "html fundamentals", "git intro",
        "css layouts", "javascript basics"
    ])

    assert result["progress"]["percentage"] == 100.0
    assert result["progress"]["completion_status"] == "completed"
    # Week 1 is fully complete (all topics done); Week 2 has an uncompleted
    # project ("Mini project") so it stays in_progress — this is expected.
    assert result["progress"]["completed_weeks"] >= 1


def test_progress_service_sync_call():
    """progress_service functions must work synchronously with the fixed roadmap."""
    from app.services.progress_service import (
        get_progress_summary,
        calculate_estimated_hours,
        calculate_remaining_hours,
    )

    roadmap = _sample_roadmap()
    roadmap["completed_topics"] = ["python basics"]

    summary = get_progress_summary(roadmap, student_skills=["Python", "Git"])
    assert isinstance(summary, dict)
    assert "overall_progress" in summary
    assert "estimated_hours" in summary
    assert "skill_mastery" in summary

    hours = calculate_estimated_hours(roadmap)
    assert isinstance(hours, float)
    assert hours >= 0

    remaining = calculate_remaining_hours(roadmap)
    assert remaining == hours


def test_full_topic_complete_flow():
    """Simulate the complete flow: create profile, generate roadmap, complete topics."""
    from app.services.roadmap_generator import RoadmapGenerator
    from app.services.progress_service import get_progress_summary

    gen = RoadmapGenerator()
    roadmap = _sample_roadmap()

    # Step 1: Initial progress
    progress = gen.calculate_progress(roadmap)
    assert progress["completed_topics"] == 0
    assert progress["overall_progress"] == 0.0

    # Step 2: Complete first topic
    roadmap = gen.update_topic_completion(roadmap, "Python basics", True)
    progress = gen.calculate_progress(roadmap)
    assert progress["completed_topics"] == 1

    # Step 3: Complete second topic
    roadmap = gen.update_topic_completion(roadmap, "HTML fundamentals", True)
    progress = gen.calculate_progress(roadmap)
    assert progress["completed_topics"] == 2

    # Step 4: Uncomplete first topic
    roadmap = gen.update_topic_completion(roadmap, "Python basics", False)
    progress = gen.calculate_progress(roadmap)
    assert progress["completed_topics"] == 1

    # Step 5: Get summary via progress_service
    summary = get_progress_summary(roadmap, student_skills=["Python"])
    assert isinstance(summary, dict)
    assert summary["completed_topics"] == 1


def test_update_roadmap_preserves_existing_completed():
    """update_roadmap should merge new topics with existing completed ones."""
    from app.services.roadmap_generator import RoadmapGenerator

    gen = RoadmapGenerator()
    roadmap = _sample_roadmap()
    roadmap["completed_topics"] = ["python basics"]

    result = gen.update_roadmap(roadmap, ["html fundamentals"])

    assert "python basics" in result["completed_topics"]
    assert "html fundamentals" in result["completed_topics"]
    assert result["progress"]["completed_topics_count"] == 2


if __name__ == "__main__":
    test_update_roadmap_returns_dict_not_coroutine()
    test_update_topic_completion_returns_dict_not_coroutine()
    test_module_level_update_roadmap_is_sync()
    test_update_roadmap_completes_week_when_all_topics_done()
    test_update_roadmap_progress_percentage()
    test_update_roadmap_100_percent()
    test_progress_service_sync_call()
    test_full_topic_complete_flow()
    test_update_roadmap_preserves_existing_completed()
    print("All progress API tests passed!")
