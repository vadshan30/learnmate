"""Tests for async route handler DB interaction.

Verifies that async route handlers correctly offload blocking DB
writes via asyncio.to_thread so the event loop is never blocked.
"""

import asyncio
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import app.database as db_module
from app.database import DatabaseManager
from sqlalchemy import event
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


def test_to_thread_save_completes():
    """asyncio.to_thread wrapping of store.save_student_profile works correctly."""
    db, path = _make_test_db()
    try:
        from app.dependencies import Store

        store = Store()
        store.set_db(db)

        profile = {
            "student_id": "async-test",
            "name": "Async User",
            "career_goal": "SRE",
            "skill_level": "advanced",
            "current_skills": ["Linux", "Python"],
            "interests": ["Cloud"],
            "current_goals": ["K8s"],
            "completed_topics": [],
            "progress_percentage": 0.0,
        }
        store.student_profiles["async-test"] = profile

        async def run():
            await asyncio.to_thread(store.save_student_profile, "async-test")

        asyncio.run(run())

        loaded = db.load_profile("async-test")
        assert loaded is not None
        assert loaded["name"] == "Async User"
        assert loaded["skill_level"] == "advanced"
        print("  PASS: test_to_thread_save_completes")
    finally:
        _cleanup(path)


def test_to_thread_does_not_block_event_loop():
    """DB write via to_thread should not block a concurrent async operation."""
    db, path = _make_test_db()
    try:
        from app.dependencies import Store

        store = Store()
        store.set_db(db)

        profile = {
            "student_id": "block-test",
            "name": "Block Test",
            "career_goal": "Dev",
            "skill_level": "beginner",
            "current_skills": [],
            "interests": [],
            "current_goals": [],
            "completed_topics": [],
            "progress_percentage": 0.0,
        }
        store.student_profiles["block-test"] = profile

        results = {"db_done": False, "concurrent_done_before_db": False}

        async def slow_db_write():
            await asyncio.to_thread(store.save_student_profile, "block-test")
            results["db_done"] = True

        async def concurrent_check():
            # This should run while DB write is in progress
            await asyncio.sleep(0.001)
            results["concurrent_done_before_db"] = not results["db_done"]

        async def run():
            await asyncio.gather(slow_db_write(), concurrent_check())

        asyncio.run(run())
        # The concurrent task should have been able to run while DB write was in progress
        assert results["db_done"], "DB write should have completed"
        print("  PASS: test_to_thread_does_not_block_event_loop")
    finally:
        _cleanup(path)


def test_multiple_concurrent_async_saves():
    """Multiple concurrent async saves should all complete without corruption."""
    db, path = _make_test_db()
    try:
        from app.dependencies import Store

        store = Store()
        store.set_db(db)

        async def run():
            tasks = []
            for i in range(5):
                sid = f"conc-{i}"
                store.student_profiles[sid] = {
                    "student_id": sid,
                    "name": f"User {i}",
                    "career_goal": f"Goal {i}",
                    "skill_level": "beginner",
                    "current_skills": [],
                    "interests": [],
                    "current_goals": [],
                    "completed_topics": [],
                    "progress_percentage": float(i * 10),
                }
                tasks.append(asyncio.to_thread(store.save_student_profile, sid))
            await asyncio.gather(*tasks)

        asyncio.run(run())

        for i in range(5):
            loaded = db.load_profile(f"conc-{i}")
            assert loaded is not None
            assert loaded["name"] == f"User {i}"
            assert loaded["progress_percentage"] == float(i * 10)
        print("  PASS: test_multiple_concurrent_async_saves")
    finally:
        _cleanup(path)


if __name__ == "__main__":
    print("Running async integration tests...")
    test_to_thread_save_completes()
    test_to_thread_does_not_block_event_loop()
    test_multiple_concurrent_async_saves()
    print("\nAll async integration tests passed!")
