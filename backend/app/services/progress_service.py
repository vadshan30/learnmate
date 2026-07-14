"""Progress Tracking Service for LearnMate AI.

Provides functions for calculating, updating, and querying learning
progress across roadmaps, weeks, topics, and skills. Works with the
in-memory Store and the RoadmapGenerator to keep progress in sync.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("learnmate.progress")


def calculate_overall_progress(
    roadmap: Dict[str, Any],
) -> Dict[str, Any]:
    """Calculate overall progress from a roadmap dictionary.

    Args:
        roadmap: The student's roadmap dictionary.

    Returns:
        Dict with overall_progress, completed_topics, total_topics,
        weekly_progress, and completion_status.
    """
    from app.services.roadmap_generator import RoadmapGenerator

    generator = RoadmapGenerator()
    return generator.calculate_progress(roadmap)


def get_weekly_progress(
    roadmap: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Get per-week progress breakdown.

    Args:
        roadmap: The student's roadmap dictionary.

    Returns:
        List of week progress dicts.
    """
    from app.services.roadmap_generator import RoadmapGenerator

    generator = RoadmapGenerator()
    progress = generator.calculate_progress(roadmap)
    return progress.get("week_progress", [])


def get_skill_mastery_progress(
    roadmap: Dict[str, Any],
    student_skills: List[str],
) -> Dict[str, Any]:
    """Calculate skill mastery progress based on roadmap and student skills.

    Args:
        roadmap: The student's roadmap dictionary.
        student_skills: List of skills the student currently has.

    Returns:
        Dict with total_required, mastered, in_progress, not_started,
        and a list of skill details.
    """
    skill_analysis = roadmap.get("skill_analysis", {})
    required_skills = skill_analysis.get("missing_skills", []) + skill_analysis.get("matched_skills", [])
    matched = skill_analysis.get("matched_skills", [])
    missing = skill_analysis.get("missing_skills", [])

    # Check which missing skills are now in the student's skill list
    student_lower = {s.lower().strip() for s in student_skills}
    newly_mastered = [
        s for s in missing
        if s.lower().strip() in student_lower
    ]
    still_missing = [
        s for s in missing
        if s.lower().strip() not in student_lower
    ]

    total = len(required_skills)
    mastered = len(matched) + len(newly_mastered)
    not_started = len(still_missing)
    in_progress = 0

    # Consider skills in completed weeks as "in_progress"
    completed_topics = {t.lower().strip() for t in roadmap.get("completed_topics", [])}
    for skill in still_missing:
        skill_lower = skill.lower().strip()
        if any(skill_lower in ct for ct in completed_topics):
            in_progress += 1
            not_started -= 1

    percentage = (mastered / total * 100.0) if total > 0 else 0.0

    return {
        "total_required": total,
        "mastered": mastered,
        "in_progress": in_progress,
        "not_started": not_started,
        "percentage": round(percentage, 1),
        "skills": [
            {"name": s, "status": "mastered" if s.lower().strip() in student_lower else "pending"}
            for s in required_skills
        ],
    }


def update_topic_completion(
    roadmap: Dict[str, Any],
    topic_name: str,
    completed: bool = True,
) -> Dict[str, Any]:
    """Mark a single topic as completed or uncompleted.

    Args:
        roadmap: The roadmap dictionary to update.
        topic_name: The topic name to toggle.
        completed: Whether to mark as completed.

    Returns:
        Updated roadmap dictionary.
    """
    from app.services.roadmap_generator import RoadmapGenerator

    generator = RoadmapGenerator()
    return generator.update_topic_completion(roadmap, topic_name, completed)


def calculate_estimated_hours(roadmap: Dict[str, Any]) -> float:
    """Calculate total estimated study hours for remaining work.

    Args:
        roadmap: The student's roadmap dictionary.

    Returns:
        Total estimated hours for incomplete weeks.
    """
    total = 0.0
    for week in roadmap.get("weeks", []):
        if week.get("completion_status") != "completed":
            total += week.get("estimated_hours", 10.0)
    return total


def calculate_remaining_hours(roadmap: Dict[str, Any]) -> float:
    """Alias for calculate_estimated_hours (remaining hours = estimated hours)."""
    return calculate_estimated_hours(roadmap)


def get_progress_summary(
    roadmap: Dict[str, Any],
    student_skills: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Get a comprehensive progress summary.

    Args:
        roadmap: The student's roadmap dictionary.
        student_skills: Optional list of student's current skills.

    Returns:
        Full progress summary dictionary.
    """
    progress = calculate_overall_progress(roadmap)
    estimated_hours = calculate_estimated_hours(roadmap)
    remaining_hours = calculate_remaining_hours(roadmap)

    result = {
        **progress,
        "estimated_hours": estimated_hours,
        "remaining_hours": remaining_hours,
    }

    if student_skills is not None:
        result["skill_mastery"] = get_skill_mastery_progress(
            roadmap, student_skills
        )

    return result
