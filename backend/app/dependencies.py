from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import Request

from app.exceptions import RoadmapNotFoundError, StudentNotFoundError
from app.services.skill_analyzer import SkillGapAnalyzer
from app.services.roadmap_generator import RoadmapGenerator

logger = logging.getLogger("learnmate.di")


class Store:
    """Shared in-memory data store injected via DI."""

    def __init__(self) -> None:
        self.student_profiles: Dict[str, Dict[str, Any]] = {}
        self.loaded_courses: list = []
        self.loaded_certifications: list = []
        self.loaded_projects: list = []
        self.roadmaps: Dict[str, Any] = {}
        self.chat_histories: Dict[str, list] = {}
        self.progress: Dict[str, Dict[str, Any]] = {}


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
