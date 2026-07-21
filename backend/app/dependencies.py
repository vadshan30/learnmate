from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

from fastapi import Request

from app.exceptions import RoadmapNotFoundError, StudentNotFoundError, StudySessionNotFoundError
from app.services.skill_analyzer import SkillGapAnalyzer
from app.services.roadmap_generator import RoadmapGenerator

logger = logging.getLogger("learnmate.di")


class Store:
    """Shared data store injected via DI.

    Backed by SQLite via DatabaseManager for persistence across restarts.
    In-memory dicts are kept for fast reads; explicit save_* methods
    must be called after mutations to persist changes to disk.
    """

    def __init__(self) -> None:
        self.student_profiles: Dict[str, Dict[str, Any]] = {}
        self.loaded_courses: list = []
        self.loaded_certifications: list = []
        self.loaded_projects: list = []
        self.loaded_books: list = []
        self.roadmaps: Dict[str, Any] = {}
        self.progress: Dict[str, Dict[str, Any]] = {}
        self.study_sessions: Dict[str, list] = {}  # user_id -> list of session dicts
        self.study_goals: Dict[str, Dict[str, Any]] = {}  # user_id -> goal dict
        self.career_test_history: Dict[str, list] = {}  # user_id -> list of test results
        self._db = None

    def set_db(self, db_manager) -> None:
        self._db = db_manager

    # ── Persistence helpers ─────────────────────────────────────────────

    def save_student_profile(self, student_id: str) -> None:
        if self._db and student_id in self.student_profiles:
            t0 = time.monotonic()
            try:
                self._db.save_profile(student_id, self.student_profiles[student_id])
                elapsed = (time.monotonic() - t0) * 1000
                logger.info("[DB] save_profile '%s' %.1fms", student_id, elapsed)
            except Exception:
                elapsed = (time.monotonic() - t0) * 1000
                logger.error("[DB] save_profile '%s' FAILED after %.1fms", student_id, elapsed, exc_info=True)

    def save_roadmap(self, student_id: str) -> None:
        if self._db and student_id in self.roadmaps:
            t0 = time.monotonic()
            try:
                self._db.save_roadmap(student_id, self.roadmaps[student_id])
                elapsed = (time.monotonic() - t0) * 1000
                logger.info("[DB] save_roadmap '%s' %.1fms", student_id, elapsed)
            except Exception:
                elapsed = (time.monotonic() - t0) * 1000
                logger.error("[DB] save_roadmap '%s' FAILED after %.1fms", student_id, elapsed, exc_info=True)

    def save_progress(self, student_id: str) -> None:
        if self._db and student_id in self.progress:
            t0 = time.monotonic()
            try:
                self._db.save_progress(student_id, self.progress[student_id])
                elapsed = (time.monotonic() - t0) * 1000
                logger.info("[DB] save_progress '%s' %.1fms", student_id, elapsed)
            except Exception:
                elapsed = (time.monotonic() - t0) * 1000
                logger.error("[DB] save_progress '%s' FAILED after %.1fms", student_id, elapsed, exc_info=True)

    def delete_student_profile(self, student_id: str) -> None:
        if self._db:
            t0 = time.monotonic()
            try:
                self._db.delete_profile(student_id)
                self._db.delete_roadmap(student_id)
                self._db.delete_progress(student_id)
                elapsed = (time.monotonic() - t0) * 1000
                logger.info("[DB] delete_all '%s' %.1fms", student_id, elapsed)
            except Exception:
                elapsed = (time.monotonic() - t0) * 1000
                logger.error("[DB] delete_all '%s' FAILED after %.1fms", student_id, elapsed, exc_info=True)

    def delete_roadmap(self, student_id: str) -> None:
        if self._db:
            t0 = time.monotonic()
            try:
                self._db.delete_roadmap(student_id)
                elapsed = (time.monotonic() - t0) * 1000
                logger.info("[DB] delete_roadmap '%s' %.1fms", student_id, elapsed)
            except Exception:
                elapsed = (time.monotonic() - t0) * 1000
                logger.error("[DB] delete_roadmap '%s' FAILED after %.1fms", student_id, elapsed, exc_info=True)

    # ── Study Sessions ─────────────────────────────────────────────────

    def save_study_sessions(self, user_id: str) -> None:
        if self._db and user_id in self.study_sessions:
            try:
                self._db.delete_all_study_sessions(user_id)
                for s in self.study_sessions[user_id]:
                    self._db.save_study_session(s["id"], s)
            except Exception:
                logger.error("[DB] save_study_sessions '%s' FAILED", user_id, exc_info=True)

    def save_single_study_session(self, session_data: Dict[str, Any]) -> None:
        if self._db:
            try:
                self._db.save_study_session(session_data["id"], session_data)
            except Exception:
                logger.error("[DB] save_single_study_session FAILED", exc_info=True)

    def delete_study_session(self, session_id: str) -> None:
        if self._db:
            try:
                self._db.delete_study_session(session_id)
            except Exception:
                logger.error("[DB] delete_study_session FAILED", exc_info=True)

    # ── Study Goals ────────────────────────────────────────────────────

    def save_study_goal(self, user_id: str) -> None:
        if self._db and user_id in self.study_goals:
            try:
                self._db.save_study_goal(user_id, self.study_goals[user_id])
            except Exception:
                logger.error("[DB] save_study_goal '%s' FAILED", user_id, exc_info=True)

    def load_from_db(self) -> None:
        if not self._db:
            return
        data = self._db.load_all()
        self.student_profiles.update(data["profiles"])
        self.roadmaps.update(data["roadmaps"])
        self.progress.update(data["progress"])
        # Load all study sessions and goals
        for sid in self.student_profiles:
            sessions = self._db.load_study_sessions(sid)
            if sessions:
                self.study_sessions[sid] = sessions
            goal = self._db.load_study_goal(sid)
            if goal:
                self.study_goals[sid] = goal
        logger.info(
            "Loaded from database: %d profiles, %d roadmaps, %d progress records, %d study session sets, %d study goals",
            len(self.student_profiles),
            len(self.roadmaps),
            len(self.progress),
            len(self.study_sessions),
            len(self.study_goals),
        )


_store: Optional[Store] = None


def get_store(request: Request) -> Store:
    """FastAPI dependency that returns the shared Store instance."""
    global _store
    if _store is None:
        _store = Store()
    return _store


def get_student_or_404(student_id: str, store: Store) -> Dict[str, Any]:
    profile = store.student_profiles.get(student_id)
    if profile is None:
        raise StudentNotFoundError(student_id)
    return profile


def get_roadmap_or_404(student_id: str, store: Store) -> Any:
    roadmap = store.roadmaps.get(student_id)
    if roadmap is None:
        raise RoadmapNotFoundError(student_id)
    return roadmap


def get_skill_analyzer() -> SkillGapAnalyzer:
    return SkillGapAnalyzer()


def get_roadmap_generator() -> RoadmapGenerator:
    return RoadmapGenerator()


def init_store() -> Store:
    global _store
    _store = Store()
    return _store


def get_store_direct() -> Store:
    global _store
    if _store is None:
        _store = Store()
    return _store
