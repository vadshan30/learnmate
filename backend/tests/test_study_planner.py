"""Tests for the Study Planner feature.

Verifies session CRUD, goal management, streak calculation,
analytics computation, and calendar formatting.
"""

import sys
import os
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ---------------------------------------------------------------------------
# Service-level tests
# ---------------------------------------------------------------------------

def test_streak_calculation_empty():
    from app.services.study_planner_service import calculate_streak
    current, longest = calculate_streak([])
    assert current == 0
    assert longest == 0


def test_streak_calculation_single_day():
    from app.services.study_planner_service import calculate_streak
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    sessions = [{"status": "completed", "date": today}]
    current, longest = calculate_streak(sessions)
    assert current == 1
    assert longest == 1


def test_streak_calculation_consecutive_days():
    from app.services.study_planner_service import calculate_streak
    today = datetime.now(timezone.utc).date()
    sessions = []
    for i in range(5):
        d = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        sessions.append({"status": "completed", "date": d})
    current, longest = calculate_streak(sessions)
    assert current == 5
    assert longest == 5


def test_streak_calculation_gap_breaks_streak():
    from app.services.study_planner_service import calculate_streak
    today = datetime.now(timezone.utc).date()
    sessions = []
    # 3 days of study
    for i in range(3):
        d = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        sessions.append({"status": "completed", "date": d})
    # Gap day
    # Another 3 days (before the gap)
    for i in range(5, 8):
        d = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        sessions.append({"status": "completed", "date": d})
    current, longest = calculate_streak(sessions)
    assert current == 3
    assert longest == 3


def test_streak_non_completed_ignored():
    from app.services.study_planner_service import calculate_streak
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    sessions = [
        {"status": "completed", "date": today},
        {"status": "scheduled", "date": today},
        {"status": "missed", "date": today},
    ]
    current, longest = calculate_streak(sessions)
    assert current == 1


def test_analytics_empty():
    from app.services.study_planner_service import compute_analytics
    result = compute_analytics([])
    assert result["total_sessions"] == 0
    assert result["completed_sessions"] == 0
    assert result["completion_rate"] == 0.0
    assert result["weekly_hours"] == 0.0


def test_analytics_with_sessions():
    from app.services.study_planner_service import compute_analytics
    today = datetime.now(timezone.utc)
    monday = today - timedelta(days=today.weekday())
    sessions = [
        {
            "status": "completed",
            "date": monday.strftime("%Y-%m-%d"),
            "duration": 2.0,
            "start_time": "18:00",
            "topic": "Python",
        },
        {
            "status": "completed",
            "date": (monday + timedelta(days=2)).strftime("%Y-%m-%d"),
            "duration": 1.5,
            "start_time": "19:00",
            "topic": "Python",
        },
        {
            "status": "scheduled",
            "date": (monday + timedelta(days=4)).strftime("%Y-%m-%d"),
            "duration": 2.0,
            "start_time": "17:00",
            "topic": "SQL",
        },
    ]
    result = compute_analytics(sessions)
    assert result["total_sessions"] == 3
    assert result["completed_sessions"] == 2
    assert result["weekly_hours"] == 3.5
    assert result["most_studied_topic"] == "Python"
    assert result["favorite_study_time"] == "evening"
    assert result["current_streak"] >= 0


def test_weekly_sessions_grouping():
    from app.services.study_planner_service import get_weekly_sessions
    today = datetime.now(timezone.utc)
    monday = today - timedelta(days=today.weekday())
    sessions = [
        {"date": monday.strftime("%Y-%m-%d"), "start_time": "18:00", "title": "Mon session"},
        {"date": (monday + timedelta(days=2)).strftime("%Y-%m-%d"), "start_time": "17:00", "title": "Wed session"},
        {"date": (monday + timedelta(days=10)).strftime("%Y-%m-%d"), "start_time": "18:00", "title": "Next week"},
    ]
    weekly = get_weekly_sessions(sessions, today)
    assert len(weekly["Monday"]) == 1
    assert len(weekly["Wednesday"]) == 1
    assert len(weekly["Tuesday"]) == 0
    assert weekly["Monday"][0]["title"] == "Mon session"


def test_calendar_events_format():
    from app.services.study_planner_service import format_calendar_events
    sessions = [
        {
            "id": "test-1",
            "title": "Python Functions",
            "date": "2025-07-14",
            "start_time": "18:00",
            "end_time": "20:00",
            "status": "scheduled",
            "priority": "high",
            "topic": "Python",
        }
    ]
    events = format_calendar_events(sessions)
    assert len(events) == 1
    assert events[0]["title"] == "Python Functions"
    assert "T18:00" in events[0]["start"]
    assert "T20:00" in events[0]["end"]


def test_weekly_summary():
    from app.services.study_planner_service import get_weekly_summary
    today = datetime.now(timezone.utc)
    monday = today - timedelta(days=today.weekday())
    sessions = [
        {"date": monday.strftime("%Y-%m-%d"), "duration": 2.0, "status": "completed"},
        {"date": (monday + timedelta(days=1)).strftime("%Y-%m-%d"), "duration": 3.0, "status": "scheduled"},
    ]
    summary = get_weekly_summary(sessions, goal_hours=10.0)
    assert summary["planned_hours_this_week"] == 5.0
    assert summary["weekly_goal_hours"] == 10.0
    assert summary["sessions_total"] == 2


# ---------------------------------------------------------------------------
# Database tests
# ---------------------------------------------------------------------------

def test_study_session_crud():
    from app.database import get_db_manager
    import uuid

    try:
        db = get_db_manager()
    except Exception:
        print("  SKIP: test_study_session_crud (DB unavailable)")
        return

    session_id = str(uuid.uuid4())
    user_id = "test-user-study-planner"

    # Create
    data = {
        "user_id": user_id,
        "title": "Test Session",
        "description": "Testing",
        "topic": "Python",
        "date": "2025-07-14",
        "start_time": "18:00",
        "end_time": "20:00",
        "duration": 2.0,
        "status": "scheduled",
        "priority": "medium",
        "difficulty": "medium",
        "course_id": None,
        "project_id": None,
        "repeat_type": "none",
        "reminder_minutes": 15,
        "completed_at": None,
    }
    db.save_study_session(session_id, data)

    # Read
    loaded = db.load_study_session(session_id)
    assert loaded is not None
    assert loaded["title"] == "Test Session"
    assert loaded["duration"] == 2.0

    # Load all for user
    all_sessions = db.load_study_sessions(user_id)
    assert len(all_sessions) >= 1

    # Delete
    db.delete_study_session(session_id)
    deleted = db.load_study_session(session_id)
    assert deleted is None

    # Cleanup
    db.delete_all_study_sessions(user_id)


def test_study_goal_crud():
    from app.database import get_db_manager

    try:
        db = get_db_manager()
    except Exception:
        print("  SKIP: test_study_goal_crud (DB unavailable)")
        return

    user_id = "test-user-study-goal"

    # Create
    goal_data = {
        "weekly_goal_hours": 15.0,
        "daily_goal_minutes": 120,
        "preferred_study_time": "evening",
        "preferred_days": ["Monday", "Wednesday", "Friday"],
    }
    db.save_study_goal(user_id, goal_data)

    # Read
    loaded = db.load_study_goal(user_id)
    assert loaded is not None
    assert loaded["weekly_goal_hours"] == 15.0
    assert loaded["preferred_study_time"] == "evening"

    # Update
    goal_data["weekly_goal_hours"] = 20.0
    db.save_study_goal(user_id, goal_data)
    updated = db.load_study_goal(user_id)
    assert updated["weekly_goal_hours"] == 20.0

    # Delete
    db.delete_study_goal(user_id)
    deleted = db.load_study_goal(user_id)
    assert deleted is None


# ---------------------------------------------------------------------------
# Pydantic schema tests
# ---------------------------------------------------------------------------

def test_session_create_schema():
    from app.models.study_planner import StudySessionCreate

    session = StudySessionCreate(
        title="Python Functions",
        date="2025-07-14",
        start_time="18:00",
        end_time="20:00",
    )
    assert session.title == "Python Functions"
    assert session.duration == 2.0
    assert session.status.value == "scheduled"
    assert session.priority.value == "medium"


def test_session_create_auto_duration():
    from app.models.study_planner import StudySessionCreate

    session = StudySessionCreate(
        title="Short Session",
        date="2025-07-14",
        start_time="14:00",
        end_time="15:30",
    )
    assert session.duration == 1.5


def test_goal_update_schema():
    from app.models.study_planner import StudyGoalUpdate

    goal = StudyGoalUpdate(
        weekly_goal_hours=20.0,
        preferred_study_time="evening",
        preferred_days=["Monday", "Friday"],
    )
    assert goal.weekly_goal_hours == 20.0


# ---------------------------------------------------------------------------
# Router endpoint tests (basic import + setup)
# ---------------------------------------------------------------------------

def test_study_planner_router_exists():
    from app.api.study_planner_routes import router
    assert router.prefix == "/api/study-planner"
    assert "study-planner" in router.tags


def test_study_planner_in_all_routers():
    from app.api import ALL_ROUTERS
    prefixes = [r.prefix for r in ALL_ROUTERS]
    assert "/api/study-planner" in prefixes


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        test_streak_calculation_empty,
        test_streak_calculation_single_day,
        test_streak_calculation_consecutive_days,
        test_streak_calculation_gap_breaks_streak,
        test_streak_non_completed_ignored,
        test_analytics_empty,
        test_analytics_with_sessions,
        test_weekly_sessions_grouping,
        test_calendar_events_format,
        test_weekly_summary,
        test_study_session_crud,
        test_study_goal_crud,
        test_session_create_schema,
        test_session_create_auto_duration,
        test_goal_update_schema,
        test_study_planner_router_exists,
        test_study_planner_in_all_routers,
    ]
    for test in tests:
        test()
        print(f"  PASS: {test.__name__}")
    print(f"\nAll {len(tests)} study planner tests passed!")
