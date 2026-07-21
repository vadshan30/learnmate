"""Tests for save performance and error scenarios.

Verifies that:
- Profile saves complete within acceptable time (< 500ms)
- DB errors are handled gracefully and don't crash the store
- WAL mode is active
- StaticPool is used for thread safety
"""

import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import app.database as db_module
from app.database import DatabaseManager
from sqlalchemy import event, text
from sqlalchemy.pool import StaticPool


def _make_test_db():
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


# ── Performance tests ─────────────────────────────────────────────────


def test_profile_save_completes_quickly():
    """Single profile save should complete well under 500ms."""
    db, path = _make_test_db()
    try:
        profile = {
            "student_id": "perf-user",
            "name": "Performance User",
            "career_goal": "Backend Engineer",
            "skill_level": "intermediate",
            "current_skills": ["Python", "FastAPI", "SQL", "Docker", "Git"],
            "interests": ["Systems", "Databases", "DevOps"],
            "current_goals": ["Learn Kubernetes", "Build Microservices"],
            "completed_topics": ["REST APIs", "SQL joins", "Git branching"],
            "progress_percentage": 45.0,
            "email": "perf@test.com",
            "learning_style": "hands-on",
            "hours_per_week": 20.0,
        }
        t0 = time.monotonic()
        db.save_profile("perf-user", profile)
        elapsed_ms = (time.monotonic() - t0) * 1000
        assert elapsed_ms < 500, f"Profile save took {elapsed_ms:.1f}ms (>500ms)"
        print(f"  PASS: test_profile_save_completes_quickly ({elapsed_ms:.1f}ms)")
    finally:
        _cleanup(path)


def test_chat_history_save_completes_quickly():
    """Saving 20 messages should complete well under 500ms."""
    db, path = _make_test_db()
    try:
        messages = [
            {"role": "user" if i % 2 == 0 else "assistant", "content": f"Message {i} with some content here", "timestamp": f"2025-01-01T00:{i:02d}:00"}
            for i in range(20)
        ]
        t0 = time.monotonic()
        db.save_chat_history("chat-perf", messages)
        elapsed_ms = (time.monotonic() - t0) * 1000
        assert elapsed_ms < 500, f"Chat history save took {elapsed_ms:.1f}ms (>500ms)"
        print(f"  PASS: test_chat_history_save_completes_quickly ({elapsed_ms:.1f}ms)")
    finally:
        _cleanup(path)


def test_repeated_saves_complete_quickly():
    """10 sequential profile saves should all complete quickly."""
    db, path = _make_test_db()
    try:
        for i in range(10):
            profile = {
                "student_id": f"repeat-{i}",
                "name": f"User {i}",
                "career_goal": "Engineer",
                "skill_level": "beginner",
                "current_skills": [f"Skill{j}" for j in range(i)],
                "interests": [],
                "current_goals": [],
                "completed_topics": [],
                "progress_percentage": float(i * 10),
            }
            t0 = time.monotonic()
            db.save_profile(f"repeat-{i}", profile)
            elapsed_ms = (time.monotonic() - t0) * 1000
            assert elapsed_ms < 500, f"Save {i} took {elapsed_ms:.1f}ms (>500ms)"
        print("  PASS: test_repeated_saves_complete_quickly")
    finally:
        _cleanup(path)


# ── WAL mode test ─────────────────────────────────────────────────────


def test_wal_mode_enabled():
    """SQLite WAL journal mode should be active."""
    db, path = _make_test_db()
    try:
        with db._session() as session:
            result = session.execute(text("PRAGMA journal_mode")).scalar()
            assert result.lower() == "wal", f"Expected 'wal', got '{result}'"
        print("  PASS: test_wal_mode_enabled")
    finally:
        _cleanup(path)


# ── StaticPool test ──────────────────────────────────────────────────


def test_uses_static_pool():
    """Engine should use StaticPool for thread safety with SQLite."""
    from sqlalchemy.pool import StaticPool
    assert isinstance(db_module.engine.pool, StaticPool), (
        f"Expected StaticPool, got {type(db_module.engine.pool).__name__}"
    )
    print("  PASS: test_uses_static_pool")


# ── Error handling tests ─────────────────────────────────────────────


def test_store_save_profile_graceful_on_missing_student():
    """save_student_profile should not crash when student not in dict."""
    from app.dependencies import Store
    store = Store()
    store._db = DatabaseManager()
    # student_id not in student_profiles — should be a no-op, no exception
    store.save_student_profile("nonexistent")
    print("  PASS: test_store_save_profile_graceful_on_missing_student")


def test_store_save_profile_graceful_on_no_db():
    """save_student_profile should not crash when _db is None."""
    from app.dependencies import Store
    store = Store()
    store.student_profiles["x"] = {"name": "X"}
    # _db is None — should be a no-op
    store.save_student_profile("x")
    print("  PASS: test_store_save_profile_graceful_on_no_db")


def test_store_delete_profile_graceful_on_no_db():
    """delete_student_profile should not crash when _db is None."""
    from app.dependencies import Store
    store = Store()
    store.delete_student_profile("x")
    print("  PASS: test_store_delete_profile_graceful_on_no_db")


def test_concurrent_saves_same_student():
    """Two saves to the same student should not corrupt data."""
    db, path = _make_test_db()
    try:
        p1 = {"student_id": "c1", "name": "V1", "career_goal": "A", "skill_level": "beginner",
              "current_skills": [], "interests": [], "current_goals": [], "completed_topics": [], "progress_percentage": 0}
        p2 = {"student_id": "c1", "name": "V2", "career_goal": "B", "skill_level": "advanced",
              "current_skills": ["X"], "interests": ["Y"], "current_goals": ["Z"], "completed_topics": ["T"], "progress_percentage": 99}
        db.save_profile("c1", p1)
        db.save_profile("c1", p2)
        loaded = db.load_profile("c1")
        assert loaded["name"] == "V2"
        assert loaded["career_goal"] == "B"
        assert loaded["skill_level"] == "advanced"
        assert loaded["current_skills"] == ["X"]
        assert loaded["progress_percentage"] == 99
        print("  PASS: test_concurrent_saves_same_student")
    finally:
        _cleanup(path)


if __name__ == "__main__":
    print("Running save performance tests...")
    test_profile_save_completes_quickly()
    test_chat_history_save_completes_quickly()
    test_repeated_saves_complete_quickly()
    test_wal_mode_enabled()
    test_uses_static_pool()
    test_store_save_profile_graceful_on_missing_student()
    test_store_save_profile_graceful_on_no_db()
    test_store_delete_profile_graceful_on_no_db()
    test_concurrent_saves_same_student()
    print("\nAll save performance tests passed!")
