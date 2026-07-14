"""Tests for the Progress Tracking System."""

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
        "total_topics": 0,
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
            {"id": "cert-001", "name": "AWS Cloud", "provider": "AWS"},  # duplicate
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


def test_calculate_progress_empty():
    from app.services.roadmap_generator import RoadmapGenerator

    gen = RoadmapGenerator()
    roadmap = _sample_roadmap()
    progress = gen.calculate_progress(roadmap)

    assert progress["overall_progress"] == 0.0
    assert progress["completed_topics"] == 0
    assert progress["total_topics"] == 5
    assert progress["completion_status"] == "not_started"


def test_calculate_progress_partial():
    from app.services.roadmap_generator import RoadmapGenerator

    gen = RoadmapGenerator()
    roadmap = _sample_roadmap()
    roadmap["completed_topics"] = ["python basics"]

    progress = gen.calculate_progress(roadmap)
    assert progress["completed_topics"] == 1
    assert progress["overall_progress"] > 0.0
    assert progress["completion_status"] == "in_progress"


def test_calculate_progress_complete():
    from app.services.roadmap_generator import RoadmapGenerator

    gen = RoadmapGenerator()
    roadmap = _sample_roadmap()
    roadmap["completed_topics"] = [
        "python basics", "html fundamentals", "git intro",
        "css layouts", "javascript basics"
    ]

    progress = gen.calculate_progress(roadmap)
    assert progress["completed_topics"] == 5
    assert progress["overall_progress"] == 100.0
    assert progress["completion_status"] == "completed"


def test_update_topic_completion():
    from app.services.roadmap_generator import RoadmapGenerator

    gen = RoadmapGenerator()
    roadmap = _sample_roadmap()

    # Mark topic complete
    result = gen.update_topic_completion(roadmap, "Python basics", True)
    assert "python basics" in result["completed_topics"]

    # Mark topic uncomplete
    result = gen.update_topic_completion(roadmap, "Python basics", False)
    assert "python basics" not in result["completed_topics"]


def test_deduplicate_certifications():
    from app.services.roadmap_generator import RoadmapGenerator

    gen = RoadmapGenerator()
    certs = [
        {"id": "cert-001", "name": "AWS Cloud", "provider": "AWS"},
        {"id": "cert-001", "name": "AWS Cloud", "provider": "AWS"},
        {"id": "cert-002", "name": "Azure Fundamentals", "provider": "Microsoft"},
    ]

    result = gen.deduplicate_certifications(certs)
    assert len(result) == 2
    assert result[0]["id"] == "cert-001"
    assert result[1]["id"] == "cert-002"


def test_deduplicate_certifications_by_name():
    from app.services.roadmap_generator import RoadmapGenerator

    gen = RoadmapGenerator()
    certs = [
        {"id": "c1", "name": "AWS Cloud Practitioner"},
        {"id": "c2", "name": "AWS Cloud Practitioner"},
    ]

    result = gen.deduplicate_certifications(certs)
    assert len(result) == 1


def test_week_progress():
    from app.services.roadmap_generator import RoadmapGenerator

    gen = RoadmapGenerator()
    roadmap = _sample_roadmap()
    roadmap["completed_topics"] = ["python basics", "html fundamentals"]

    progress = gen.calculate_progress(roadmap)
    week_progress = progress["week_progress"]
    assert len(week_progress) == 2

    # Week 1: 2/3 topics completed
    w1 = week_progress[0]
    assert w1["total_topics"] == 3
    assert w1["completed_topics_count"] == 2
    assert w1["status"] == "in_progress"

    # Week 2: 0/2 topics completed
    w2 = week_progress[1]
    assert w2["total_topics"] == 2
    assert w2["completed_topics_count"] == 0
    assert w2["status"] == "pending"


if __name__ == "__main__":
    test_calculate_progress_empty()
    test_calculate_progress_partial()
    test_calculate_progress_complete()
    test_update_topic_completion()
    test_deduplicate_certifications()
    test_deduplicate_certifications_by_name()
    test_week_progress()
    print("All progress tests passed!")
