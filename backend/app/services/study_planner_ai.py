"""AI-powered Study Planner service for LearnMate AI.

Uses Gemini to generate optimized schedules from roadmaps,
recommend study times, suggest breaks, and provide daily tips.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from app.services.gemini_service import generate_response, gemini_available

logger = logging.getLogger("learnmate.study_planner_ai")


async def generate_sessions_from_roadmap(
    roadmap: Dict[str, Any],
    weekly_hours: float = 10.0,
    preferred_days: Optional[List[str]] = None,
    start_date: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Generate study sessions from a roadmap using Gemini.

    Distributes roadmap topics across the preferred days and hours.
    """
    if preferred_days is None:
        preferred_days = ["Monday", "Wednesday", "Friday"]

    weeks = roadmap.get("weeks", [])
    if not weeks:
        return []

    if gemini_available:
        system_instruction = (
            "You are an expert learning scheduler for LearnMate AI. "
            "Generate study sessions as valid JSON.\n\n"
            "Return ONLY a JSON array of session objects, no markdown fences.\n\n"
            "Each session object must have:\n"
            '- "title": string (concise session title)\n'
            '- "topic": string (specific topic)\n'
            '- "day": string (day of week)\n'
            '- "date": string (YYYY-MM-DD)\n'
            '- "start_time": string (HH:MM, 24-hour)\n'
            '- "end_time": string (HH:MM)\n'
            '- "duration": number (hours)\n'
            '- "priority": "low" | "medium" | "high"\n'
            '- "difficulty": "easy" | "medium" | "hard"\n\n'
            "Distribute topics evenly. Use realistic study times (e.g. 18:00-20:00 for evenings). "
            "Include short breaks between long sessions. "
            "Match difficulty to week number (early=easy, late=hard)."
        )

        topics_text = ""
        for w in weeks[:6]:  # Limit to first 6 weeks
            topics_text += f"Week {w.get('week_number', '?')}: {w.get('title', '')} — Topics: {', '.join(w.get('topics', []))}\n"

        prompt = (
            f"Weekly study budget: {weekly_hours} hours\n"
            f"Preferred days: {', '.join(preferred_days)}\n"
            f"Start date: {start_date or 'next Monday'}\n\n"
            f"Roadmap topics:\n{topics_text}\n"
            "Generate the study sessions."
        )

        raw = await generate_response(
            prompt,
            system_instruction=system_instruction,
            max_tokens=4096,
            temperature=0.4,
        )

        if raw:
            try:
                cleaned = raw.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("\n", 1)[1]
                if cleaned.endswith("```"):
                    cleaned = cleaned.rsplit("```", 1)[0]
                parsed = json.loads(cleaned.strip())
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                logger.warning("Could not parse AI schedule JSON — using fallback")

    return _fallback_generate_sessions(roadmap, weekly_hours, preferred_days, start_date)


async def optimize_schedule(
    sessions: List[Dict[str, Any]],
    goal_hours: float,
    student_context: str = "",
) -> str:
    """Get AI recommendations for optimizing the study schedule."""
    if not gemini_available:
        return (
            "Based on your current schedule, here are some tips:\n"
            "1. Try to study at the same time each day for consistency.\n"
            "2. Take a 5-10 minute break every 45-50 minutes.\n"
            "3. Tackle harder topics when you're most alert.\n"
            "4. Review completed material before starting new topics."
        )

    sessions_summary = ""
    for s in sessions[:10]:
        sessions_summary += f"- {s.get('date', '')} {s.get('start_time', '')}-{s.get('end_time', '')}: {s.get('title', '')} ({s.get('status', '')})\n"

    system_instruction = (
        "You are an expert study coach for LearnMate AI. "
        "Analyze the student's schedule and provide 3-5 specific, actionable "
        "recommendations to optimize their study time. "
        "Be encouraging and specific. Use Markdown formatting."
    )

    prompt = (
        f"Student context: {student_context or 'No additional context'}\n"
        f"Weekly goal: {goal_hours} hours\n"
        f"Current sessions:\n{sessions_summary}\n\n"
        "Provide optimization recommendations:"
    )

    result = await generate_response(
        prompt,
        system_instruction=system_instruction,
        max_tokens=1024,
        temperature=0.5,
    )
    return result or "No recommendations available at this time."


async def get_daily_recommendation(
    student_profile: Dict[str, Any],
    progress: Optional[Dict[str, Any]],
    upcoming_sessions: List[Dict[str, Any]],
) -> str:
    """Get a daily learning recommendation from Gemini."""
    if not gemini_available:
        return (
            "Today's recommendation: Start with a review of what you learned yesterday, "
            "then dive into new material. Remember to take breaks every 45 minutes. "
            "Good luck with your studies!"
        )

    sessions_info = ""
    for s in upcoming_sessions[:3]:
        sessions_info += f"- {s.get('title', '')} ({s.get('topic', 'general')}) at {s.get('start_time', 'TBD')}\n"

    system_instruction = (
        "You are LearnMate AI, a supportive learning mentor. "
        "Provide a brief, motivating daily study recommendation. "
        "Keep it under 100 words. Be specific and actionable."
    )

    prompt = (
        f"Student: {student_profile.get('name', 'Student')}\n"
        f"Career goal: {student_profile.get('career_goal', 'N/A')}\n"
        f"Progress: {progress.get('overall_progress', 0) if progress else 0}%\n"
        f"Today's sessions:\n{sessions_info or 'No sessions scheduled'}\n\n"
        "Provide today's learning recommendation:"
    )

    result = await generate_response(
        prompt,
        system_instruction=system_instruction,
        max_tokens=256,
        temperature=0.7,
    )
    return result or "Keep up the great work! Today is a great day to learn something new."


# ---------------------------------------------------------------------------
# Fallback (offline) generators
# ---------------------------------------------------------------------------

def _fallback_generate_sessions(
    roadmap: Dict[str, Any],
    weekly_hours: float,
    preferred_days: Optional[List[str]],
    start_date: Optional[str],
) -> List[Dict[str, Any]]:
    """Deterministically generate sessions from roadmap without AI."""
    import calendar
    from datetime import datetime, timedelta, timezone

    if not preferred_days:
        preferred_days = ["Monday", "Wednesday", "Friday"]

    day_name_to_num = {
        "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
        "Friday": 4, "Saturday": 5, "Sunday": 6,
    }

    # Determine start date
    if start_date:
        try:
            current = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            current = datetime.now(timezone.utc)
    else:
        today = datetime.now(timezone.utc)
        days_ahead = (7 - today.weekday()) % 7 or 7
        current = today + timedelta(days=days_ahead)
        current = current.replace(hour=18, minute=0, second=0, microsecond=0)

    sessions = []
    session_id_counter = 0
    hours_per_day = weekly_hours / len(preferred_days)
    hours_per_session = min(hours_per_day, 3.0)

    weeks = roadmap.get("weeks", [])
    session_times = [
        ("18:00", "20:00"),
        ("17:00", "19:00"),
        ("19:00", "21:00"),
        ("20:00", "22:00"),
        ("16:00", "18:00"),
    ]

    for week in weeks[:6]:
        topics = week.get("topics", [])
        week_num = week.get("week_number", 0)

        for day_name in preferred_days:
            if not topics:
                break
            topic = topics.pop(0)
            time_slot = session_times[session_id_counter % len(session_times)]

            # Find the next occurrence of this day
            target_day = day_name_to_num.get(day_name, 0)
            days_ahead = (target_day - current.weekday()) % 7
            if days_ahead == 0 and current.weekday() != target_day:
                days_ahead = 7
            session_date = current + timedelta(days=days_ahead)

            priority = "high" if week_num >= len(weeks) * 0.7 else "medium"
            difficulty = "hard" if week_num >= len(weeks) * 0.6 else "medium" if week_num >= len(weeks) * 0.3 else "easy"

            sessions.append({
                "title": f"{topic}",
                "topic": topic,
                "day": day_name,
                "date": session_date.strftime("%Y-%m-%d"),
                "start_time": time_slot[0],
                "end_time": time_slot[1],
                "duration": hours_per_session,
                "priority": priority,
                "difficulty": difficulty,
            })
            session_id_counter += 1
            current = session_date + timedelta(days=1)

    return sessions
