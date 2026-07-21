"""Study Planner business logic for LearnMate AI.

Provides streak calculation, analytics computation, calendar event
formatting, session status management, and weekly/hour aggregation.
"""

from __future__ import annotations

import logging
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("learnmate.study_planner")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_date(date_str: str) -> Optional[datetime]:
    """Parse YYYY-MM-DD string to datetime."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def _get_week_bounds(ref_date: Optional[datetime] = None) -> Tuple[str, str]:
    """Return (monday, sunday) date strings for the week containing ref_date."""
    today = ref_date or datetime.now(timezone.utc)
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return monday.strftime("%Y-%m-%d"), sunday.strftime("%Y-%m-%d")


def _get_month_bounds(ref_date: Optional[datetime] = None) -> Tuple[str, str]:
    """Return (first_day, last_day) date strings for the month containing ref_date."""
    today = ref_date or datetime.now(timezone.utc)
    first = today.replace(day=1)
    if today.month == 12:
        last = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        last = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    return first.strftime("%Y-%m-%d"), last.strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Streak calculation
# ---------------------------------------------------------------------------

def calculate_streak(sessions: List[Dict[str, Any]]) -> Tuple[int, int]:
    """Calculate current and longest streaks from session data.

    A streak is a consecutive sequence of days with at least one completed session.
    Works backward from today for current streak.

    Returns:
        (current_streak, longest_streak)
    """
    completed_dates = set()
    for s in sessions:
        if s.get("status") == "completed":
            date_str = s.get("date", "")
            if date_str:
                completed_dates.add(date_str)

    if not completed_dates:
        return 0, 0

    sorted_dates = sorted(completed_dates)
    parsed = []
    for d in sorted_dates:
        dt = _parse_date(d)
        if dt:
            parsed.append(dt.date())

    if not parsed:
        return 0, 0

    # Current streak: count backward from today
    today = datetime.now(timezone.utc).date()
    current_streak = 0
    check_date = today
    while check_date in parsed:
        current_streak += 1
        check_date -= timedelta(days=1)

    # Longest streak: scan all dates
    longest_streak = 0
    streak = 1
    for i in range(1, len(parsed)):
        if (parsed[i] - parsed[i - 1]).days == 1:
            streak += 1
        else:
            longest_streak = max(longest_streak, streak)
            streak = 1
    longest_streak = max(longest_streak, streak)

    return current_streak, longest_streak


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------

def compute_analytics(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute comprehensive analytics from all sessions for a user."""
    today = datetime.now(timezone.utc)
    today_str = today.strftime("%Y-%m-%d")
    monday_str, sunday_str = _get_week_bounds(today)
    first_month_str, last_month_str = _get_month_bounds(today)

    total = len(sessions)
    completed = [s for s in sessions if s.get("status") == "completed"]
    completed_count = len(completed)
    completion_rate = (completed_count / total * 100) if total > 0 else 0.0

    # Total hours
    total_hours = sum(s.get("duration", 0) for s in sessions)

    # Weekly hours (current week)
    weekly_hours = sum(
        s.get("duration", 0) for s in sessions
        if monday_str <= s.get("date", "") <= sunday_str and s.get("status") == "completed"
    )

    # Monthly hours
    monthly_hours = sum(
        s.get("duration", 0) for s in sessions
        if first_month_str <= s.get("date", "") <= last_month_str and s.get("status") == "completed"
    )

    # Average session length
    avg_length = (total_hours / total) if total > 0 else 0.0

    # Most studied topic
    topic_counter = Counter()
    for s in sessions:
        topic = s.get("topic")
        if topic and s.get("status") == "completed":
            topic_counter[topic] += 1
    most_studied = topic_counter.most_common(1)[0][0] if topic_counter else None

    # Favorite study time
    time_counter = Counter()
    for s in sessions:
        if s.get("status") == "completed":
            start = s.get("start_time", "")
            if start:
                try:
                    hour = int(start.split(":")[0])
                    if 5 <= hour < 12:
                        time_counter["morning"] += 1
                    elif 12 <= hour < 17:
                        time_counter["afternoon"] += 1
                    elif 17 <= hour < 21:
                        time_counter["evening"] += 1
                    else:
                        time_counter["night"] += 1
                except (ValueError, IndexError):
                    pass
    favorite_time = time_counter.most_common(1)[0][0] if time_counter else None

    # Streaks
    current_streak, longest_streak = calculate_streak(sessions)

    # Status distribution
    status_dist = Counter(s.get("status", "scheduled") for s in sessions)

    # Weekly hours history (last 8 weeks)
    weekly_history = []
    for i in range(7, -1, -1):
        week_start = today - timedelta(weeks=i, days=today.weekday())
        week_end = week_start + timedelta(days=6)
        ws_str = week_start.strftime("%Y-%m-%d")
        we_str = week_end.strftime("%Y-%m-%d")
        wh = sum(
            s.get("duration", 0) for s in sessions
            if ws_str <= s.get("date", "") <= we_str and s.get("status") == "completed"
        )
        weekly_history.append({
            "week": week_start.strftime("%b %d"),
            "hours": round(wh, 1),
        })

    # Monthly hours history (last 6 months)
    monthly_history = []
    for i in range(5, -1, -1):
        month_date = today.month - i
        year = today.year
        while month_date <= 0:
            month_date += 12
            year -= 1
        m_first = datetime(year, month_date, 1, tzinfo=timezone.utc)
        if month_date == 12:
            m_last = datetime(year + 1, 1, 1, tzinfo=timezone.utc) - timedelta(days=1)
        else:
            m_last = datetime(year, month_date + 1, 1, tzinfo=timezone.utc) - timedelta(days=1)
        mf_str = m_first.strftime("%Y-%m-%d")
        ml_str = m_last.strftime("%Y-%m-%d")
        mh = sum(
            s.get("duration", 0) for s in sessions
            if mf_str <= s.get("date", "") <= ml_str and s.get("status") == "completed"
        )
        monthly_history.append({
            "month": m_first.strftime("%b %Y"),
            "hours": round(mh, 1),
        })

    return {
        "weekly_hours": round(weekly_hours, 1),
        "monthly_hours": round(monthly_hours, 1),
        "average_session_length": round(avg_length, 1),
        "completion_rate": round(completion_rate, 1),
        "most_studied_topic": most_studied,
        "favorite_study_time": favorite_time,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "total_sessions": total,
        "completed_sessions": completed_count,
        "weekly_hours_history": weekly_history,
        "monthly_hours_history": monthly_history,
        "status_distribution": dict(status_dist),
    }


# ---------------------------------------------------------------------------
# Weekly planner data
# ---------------------------------------------------------------------------

def get_weekly_sessions(sessions: List[Dict[str, Any]], ref_date: Optional[datetime] = None) -> Dict[str, List[Dict[str, Any]]]:
    """Group sessions by day of week for the current week."""
    today = ref_date or datetime.now(timezone.utc)
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    monday_str = monday.strftime("%Y-%m-%d")
    sunday_str = sunday.strftime("%Y-%m-%d")

    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    result: Dict[str, List[Dict[str, Any]]] = {day: [] for day in day_names}

    for s in sessions:
        s_date = s.get("date", "")
        if monday_str <= s_date <= sunday_str:
            dt = _parse_date(s_date)
            if dt:
                day_name = day_names[dt.weekday()]
                result[day_name].append(s)

    # Sort each day by start_time
    for day in day_names:
        result[day].sort(key=lambda x: x.get("start_time", "00:00"))

    return result


# ---------------------------------------------------------------------------
# Calendar events
# ---------------------------------------------------------------------------

def format_calendar_events(sessions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert study sessions to calendar event format."""
    events = []
    for s in sessions:
        date_str = s.get("date", "")
        start_time = s.get("start_time", "00:00")
        end_time = s.get("end_time", "23:59")
        try:
            start_dt = datetime.strptime(f"{date_str} {start_time}", "%Y-%m-%d %H:%M")
            end_dt = datetime.strptime(f"{date_str} {end_time}", "%Y-%m-%d %H:%M")
        except ValueError:
            continue

        events.append({
            "id": s.get("id", ""),
            "title": s.get("title", ""),
            "start": start_dt.isoformat(),
            "end": end_dt.isoformat(),
            "status": s.get("status", "scheduled"),
            "priority": s.get("priority", "medium"),
            "topic": s.get("topic"),
        })
    return events


# ---------------------------------------------------------------------------
# Session summary
# ---------------------------------------------------------------------------

def get_weekly_summary(sessions: List[Dict[str, Any]], goal_hours: float = 10.0) -> Dict[str, Any]:
    """Get a summary card for the planner dashboard."""
    today = datetime.now(timezone.utc)
    monday_str, sunday_str = _get_week_bounds(today)
    today_str = today.strftime("%Y-%m-%d")

    week_sessions = [
        s for s in sessions
        if monday_str <= s.get("date", "") <= sunday_str
    ]
    completed_week = [s for s in week_sessions if s.get("status") == "completed"]
    today_sessions = [s for s in sessions if s.get("date", "") == today_str and s.get("status") != "completed"]

    planned_hours = sum(s.get("duration", 0) for s in week_sessions)
    completed_hours = sum(s.get("duration", 0) for s in completed_week)
    goal_progress = (completed_hours / goal_hours * 100) if goal_hours > 0 else 0.0
    current_streak, _ = calculate_streak(sessions)

    # Upcoming: next 5 non-completed sessions from today onward
    upcoming = [
        s for s in sessions
        if s.get("date", "") >= today_str and s.get("status") not in ("completed", "missed", "skipped")
    ]
    upcoming.sort(key=lambda x: (x.get("date", ""), x.get("start_time", "")))

    return {
        "planned_hours_this_week": round(planned_hours, 1),
        "weekly_goal_hours": goal_hours,
        "weekly_goal_progress": round(min(goal_progress, 100.0), 1),
        "current_streak": current_streak,
        "sessions_completed": len(completed_week),
        "sessions_total": len(week_sessions),
        "today_sessions": today_sessions[:5],
        "upcoming_sessions": upcoming[:5],
    }
