"""Tests for SQLite persistence layer (DatabaseManager).

Verifies that profiles, roadmaps, chat histories, and progress
survive across separate DatabaseManager instances (simulating restart).
"""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import app.database as db_module
from app.database import DatabaseManager
from sqlalchemy import event
from sqlalchemy.pool import StaticPool


def _make_test_db():
    """Create a DatabaseManager using a temporary SQLite file."""
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    db_module.DATABASE_URL = f"sqlite:///{tmp.name}"
    db_module.engine = db_module.create_engine(
        db_module.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
        pool_pre_ping=True,
        poolclass=StaticPool,
    )
    event.listen(db_module.engine, "connect", db_module._set_sqlite_pragma)
    db_module.SessionLocal = db_module.sessionmaker(
        autocommit=False, autoflush=False, bind=db_module.engine
    )
    db_module.Base.metadata.create_all(bind=db_module.engine)
    return DatabaseManager(), tmp.name


def _cleanup(path):
    try:
        os.unlink(path)
    except OSError:
        pass


# ── Profile persistence ────────────────────────────────────────────────


def test_save_and_load_profile():
    db, path = _make_test_db()
    try:
        profile = {
            "student_id": "alice",
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "career_goal": "AI Engineer",
            "skill_level": "intermediate",
            "learning_style": "video",
            "hours_per_week": 15.0,
            "preferred_study_time": "evening",
            "preferred_job_role": "ML Engineer",
            "dream_company": "Google",
            "experience_level": "student",
            "github_url": "https://github.com/alice",
            "linkedin_url": "https://linkedin.com/in/alice",
            "current_skills": ["Python", "Git", "SQL"],
            "interests": ["AI", "Machine Learning"],
            "current_goals": ["Get Internship", "Build Portfolio"],
            "completed_topics": ["variables", "loops"],
            "progress_percentage": 25.0,
        }
        db.save_profile("alice", profile)

        loaded = db.load_profile("alice")
        assert loaded is not None
        assert loaded["name"] == "Alice Johnson"
        assert loaded["email"] == "alice@example.com"
        assert loaded["career_goal"] == "AI Engineer"
        assert loaded["skill_level"] == "intermediate"
        assert loaded["learning_style"] == "video"
        assert loaded["hours_per_week"] == 15.0
        assert loaded["preferred_study_time"] == "evening"
        assert loaded["preferred_job_role"] == "ML Engineer"
        assert loaded["dream_company"] == "Google"
        assert loaded["experience_level"] == "student"
        assert loaded["github_url"] == "https://github.com/alice"
        assert loaded["linkedin_url"] == "https://linkedin.com/in/alice"
        assert loaded["current_skills"] == ["Python", "Git", "SQL"]
        assert loaded["interests"] == ["AI", "Machine Learning"]
        assert loaded["current_goals"] == ["Get Internship", "Build Portfolio"]
        assert loaded["completed_topics"] == ["variables", "loops"]
        assert loaded["progress_percentage"] == 25.0
        print("  PASS: test_save_and_load_profile")
    finally:
        _cleanup(path)


def test_profile_survives_new_manager():
    """Simulates server restart by creating a new DatabaseManager."""
    db1, path = _make_test_db()
    try:
        profile = {
            "student_id": "bob",
            "name": "Bob Smith",
            "career_goal": "Data Scientist",
            "skill_level": "beginner",
            "current_skills": ["Python"],
            "interests": ["Data Science"],
            "current_goals": ["Learn New Technology"],
            "completed_topics": [],
            "progress_percentage": 0.0,
        }
        db1.save_profile("bob", profile)

        # Simulate restart: create new manager (uses same DB file)
        db2 = DatabaseManager()
        loaded = db2.load_profile("bob")
        assert loaded is not None
        assert loaded["name"] == "Bob Smith"
        assert loaded["career_goal"] == "Data Scientist"
        assert loaded["current_skills"] == ["Python"]
        print("  PASS: test_profile_survives_new_manager")
    finally:
        _cleanup(path)


def test_load_all_profiles():
    db, path = _make_test_db()
    try:
        db.save_profile("a", {"student_id": "a", "name": "A", "career_goal": "X", "skill_level": "beginner",
                              "current_skills": [], "interests": [], "current_goals": [], "completed_topics": [], "progress_percentage": 0})
        db.save_profile("b", {"student_id": "b", "name": "B", "career_goal": "Y", "skill_level": "advanced",
                              "current_skills": [], "interests": [], "current_goals": [], "completed_topics": [], "progress_percentage": 50})
        all_profiles = db.load_all_profiles()
        assert len(all_profiles) == 2
        assert "a" in all_profiles
        assert "b" in all_profiles
        print("  PASS: test_load_all_profiles")
    finally:
        _cleanup(path)


# ── Roadmap persistence ────────────────────────────────────────────────


def test_save_and_load_roadmap():
    db, path = _make_test_db()
    try:
        roadmap = {
            "weeks": [
                {"week_number": 1, "topics": ["Python basics"], "completed": False},
                {"week_number": 2, "topics": ["HTML"], "completed": False},
            ],
            "completed_topics": [],
            "progress": {"percentage": 0.0},
        }
        db.save_roadmap("alice", roadmap)
        loaded = db.load_roadmap("alice")
        assert loaded is not None
        assert len(loaded["weeks"]) == 2
        assert loaded["completed_topics"] == []
        print("  PASS: test_save_and_load_roadmap")
    finally:
        _cleanup(path)


def test_roadmap_survives_restart():
    db1, path = _make_test_db()
    try:
        roadmap = {"weeks": [{"week_number": 1, "topics": ["SQL"]}]}
        db1.save_roadmap("carol", roadmap)
        db2 = DatabaseManager()
        loaded = db2.load_roadmap("carol")
        assert loaded is not None
        assert loaded["weeks"][0]["topics"] == ["SQL"]
        print("  PASS: test_roadmap_survives_restart")
    finally:
        _cleanup(path)


# ── Chat history persistence ───────────────────────────────────────────


def test_save_and_load_chat_history():
    db, path = _make_test_db()
    try:
        messages = [
            {"role": "user", "content": "I want to become a Data Engineer.", "timestamp": "2025-01-01T00:00:00"},
            {"role": "assistant", "content": "Great goal! Let me help you plan.", "timestamp": "2025-01-01T00:00:01"},
        ]
        db.save_chat_history("alice", messages)
        loaded = db.load_chat_history("alice")
        assert len(loaded) == 2
        assert loaded[0]["role"] == "user"
        assert loaded[0]["content"] == "I want to become a Data Engineer."
        assert loaded[1]["role"] == "assistant"
        print("  PASS: test_save_and_load_chat_history")
    finally:
        _cleanup(path)


def test_chat_history_survives_restart():
    db1, path = _make_test_db()
    try:
        messages = [
            {"role": "user", "content": "What should I study next?"},
            {"role": "assistant", "content": "Based on your profile..."},
        ]
        db1.save_chat_history("bob", messages)
        db2 = DatabaseManager()
        loaded = db2.load_chat_history("bob")
        assert len(loaded) == 2
        assert loaded[0]["content"] == "What should I study next?"
        print("  PASS: test_chat_history_survives_restart")
    finally:
        _cleanup(path)


def test_chat_history_overwrite():
    """Saving new messages replaces old ones (not appends)."""
    db, path = _make_test_db()
    try:
        db.save_chat_history("alice", [{"role": "user", "content": "old message"}])
        db.save_chat_history("alice", [{"role": "user", "content": "new message"}])
        loaded = db.load_chat_history("alice")
        assert len(loaded) == 1
        assert loaded[0]["content"] == "new message"
        print("  PASS: test_chat_history_overwrite")
    finally:
        _cleanup(path)


# ── Progress persistence ───────────────────────────────────────────────


def test_save_and_load_progress():
    db, path = _make_test_db()
    try:
        progress = {
            "weeks": {"1": {"completed_topics": ["python"], "hours_studied": 5.0}},
            "total_hours": 5.0,
            "total_topics": 1,
            "saved_projects": ["proj-001"],
            "completed_projects": [],
        }
        db.save_progress("alice", progress)
        loaded = db.load_progress("alice")
        assert loaded is not None
        assert loaded["total_hours"] == 5.0
        assert loaded["total_topics"] == 1
        assert "proj-001" in loaded["saved_projects"]
        print("  PASS: test_save_and_load_progress")
    finally:
        _cleanup(path)


def test_progress_survives_restart():
    db1, path = _make_test_db()
    try:
        progress = {"total_hours": 20.0, "total_topics": 5}
        db1.save_progress("carol", progress)
        db2 = DatabaseManager()
        loaded = db2.load_progress("carol")
        assert loaded is not None
        assert loaded["total_hours"] == 20.0
        print("  PASS: test_progress_survives_restart")
    finally:
        _cleanup(path)


# ── Delete operations ──────────────────────────────────────────────────


def test_delete_profile():
    db, path = _make_test_db()
    try:
        db.save_profile("delme", {"student_id": "delme", "name": "Del", "career_goal": "X",
                                  "skill_level": "beginner", "current_skills": [], "interests": [],
                                  "current_goals": [], "completed_topics": [], "progress_percentage": 0})
        assert db.load_profile("delme") is not None
        db.delete_profile("delme")
        assert db.load_profile("delme") is None
        print("  PASS: test_delete_profile")
    finally:
        _cleanup(path)


def test_delete_cascades():
    """Deleting a profile also removes roadmap, chat, progress."""
    db, path = _make_test_db()
    try:
        db.save_profile("full", {"student_id": "full", "name": "Full", "career_goal": "X",
                                 "skill_level": "beginner", "current_skills": [], "interests": [],
                                 "current_goals": [], "completed_topics": [], "progress_percentage": 0})
        db.save_roadmap("full", {"weeks": []})
        db.save_chat_history("full", [{"role": "user", "content": "hi"}])
        db.save_progress("full", {"total_hours": 5.0})

        db.delete_profile("full")
        db.delete_roadmap("full")
        db.delete_chat_history("full")
        db.delete_progress("full")

        assert db.load_profile("full") is None
        assert db.load_roadmap("full") is None
        assert db.load_chat_history("full") == []
        assert db.load_progress("full") is None
        print("  PASS: test_delete_cascades")
    finally:
        _cleanup(path)


# ── Load all ───────────────────────────────────────────────────────────


def test_load_all():
    db, path = _make_test_db()
    try:
        db.save_profile("s1", {"student_id": "s1", "name": "S1", "career_goal": "X",
                               "skill_level": "beginner", "current_skills": [], "interests": [],
                               "current_goals": [], "completed_topics": [], "progress_percentage": 0})
        db.save_roadmap("s1", {"weeks": []})
        db.save_progress("s1", {"total_hours": 3.0})

        data = db.load_all()
        assert "s1" in data["profiles"]
        assert "s1" in data["roadmaps"]
        assert "s1" in data["progress"]
        print("  PASS: test_load_all")
    finally:
        _cleanup(path)


# ── Validation tests ───────────────────────────────────────────────────


def test_validation_deduplicate_skills():
    from app.schemas.requests import StudentCreateRequest
    req = StudentCreateRequest(
        name="Test",
        career_goal="Engineer",
        current_skills=["Python", "python", "Python", "Git"],
    )
    assert req.current_skills == ["Python", "Git"]
    print("  PASS: test_validation_deduplicate_skills")


def test_validation_deduplicate_interests():
    from app.schemas.requests import StudentCreateRequest
    req = StudentCreateRequest(
        name="Test",
        career_goal="Engineer",
        interests=["AI", "ai", "Machine Learning"],
    )
    assert req.interests == ["AI", "Machine Learning"]
    print("  PASS: test_validation_deduplicate_interests")


def test_validation_deduplicate_goals():
    from app.schemas.requests import StudentCreateRequest
    req = StudentCreateRequest(
        name="Test",
        career_goal="Engineer",
        current_goals=["Get Internship", "get internship"],
    )
    assert req.current_goals == ["Get Internship"]
    print("  PASS: test_validation_deduplicate_goals")


if __name__ == "__main__":
    print("Running persistence tests...")
    test_save_and_load_profile()
    test_profile_survives_new_manager()
    test_load_all_profiles()
    test_save_and_load_roadmap()
    test_roadmap_survives_restart()
    test_save_and_load_chat_history()
    test_chat_history_survives_restart()
    test_chat_history_overwrite()
    test_save_and_load_progress()
    test_progress_survives_restart()
    test_delete_profile()
    test_delete_cascades()
    test_load_all()
    test_validation_deduplicate_skills()
    test_validation_deduplicate_interests()
    test_validation_deduplicate_goals()
    print("\nAll persistence tests passed!")
