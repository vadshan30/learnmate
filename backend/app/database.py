"""SQLite persistence layer for LearnMate AI.

Provides SQLAlchemy ORM models and a DatabaseManager for storing
student profiles, roadmaps, chat histories, progress, and project
actions in a SQLite database that survives server restarts.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    event,
    text,
)
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

logger = logging.getLogger("learnmate.database")

DB_DIR: Path = Path(__file__).parent.parent / "data"
DB_PATH: Path = DB_DIR / "learnmate.db"
DATABASE_URL: str = f"sqlite:///{DB_PATH}"


def _set_sqlite_pragma(dbapi_conn, _connection_record):
    """Enable WAL mode and foreign keys for every new SQLite connection."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
    pool_pre_ping=True,
    poolclass=StaticPool,
)
event.listen(engine, "connect", _set_sqlite_pragma)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ---------------------------------------------------------------------------
# ORM Models
# ---------------------------------------------------------------------------


class StudentProfileRow(Base):
    __tablename__ = "student_profiles"

    student_id = Column(String(200), primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(200), nullable=True)
    career_goal = Column(String(200), nullable=False, default="")
    skill_level = Column(String(50), nullable=False, default="beginner")
    learning_style = Column(String(50), nullable=True)
    hours_per_week = Column(Float, nullable=True)
    preferred_study_time = Column(String(50), nullable=True)
    preferred_job_role = Column(String(200), nullable=True)
    dream_company = Column(String(200), nullable=True)
    experience_level = Column(String(50), nullable=True)
    github_url = Column(String(500), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    current_skills = Column(Text, nullable=False, default="[]")
    interests = Column(Text, nullable=False, default="[]")
    current_goals = Column(Text, nullable=False, default="[]")
    completed_topics = Column(Text, nullable=False, default="[]")
    progress_percentage = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class RoadmapRow(Base):
    __tablename__ = "roadmaps"

    student_id = Column(String(200), primary_key=True)
    roadmap_data = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ProgressRow(Base):
    __tablename__ = "progress"

    student_id = Column(String(200), primary_key=True)
    progress_data = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class UserRow(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    full_name = Column(String(100), nullable=False)
    username = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(200), nullable=False, unique=True, index=True)
    password_hash = Column(String(200), nullable=False)
    is_active = Column(Integer, nullable=False, default=1)
    profile_image = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime, nullable=True)


class PasswordResetTokenRow(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    hashed_token = Column(String(200), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    used = Column(Integer, nullable=False, default=0)


class StudySessionRow(Base):
    __tablename__ = "study_sessions"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True, default="")
    topic = Column(String(200), nullable=True)
    date = Column(String(10), nullable=False)
    start_time = Column(String(5), nullable=False)
    end_time = Column(String(5), nullable=False)
    duration = Column(Float, nullable=False, default=1.0)
    status = Column(String(20), nullable=False, default="scheduled")
    priority = Column(String(10), nullable=False, default="medium")
    difficulty = Column(String(10), nullable=True)
    course_id = Column(String(100), nullable=True)
    project_id = Column(String(100), nullable=True)
    repeat_type = Column(String(20), nullable=True, default="none")
    reminder_minutes = Column(Integer, nullable=True, default=15)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class StudyGoalRow(Base):
    __tablename__ = "study_goals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), nullable=False, unique=True, index=True)
    weekly_goal_hours = Column(Float, nullable=False, default=10.0)
    daily_goal_minutes = Column(Integer, nullable=True)
    preferred_study_time = Column(String(20), nullable=True)
    preferred_days = Column(Text, nullable=True, default="[]")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class CareerTestResultRow(Base):
    __tablename__ = "career_test_results"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(200), nullable=False, index=True)
    top_careers = Column(Text, nullable=False, default="[]")
    all_scores = Column(Text, nullable=False, default="[]")
    answers = Column(Text, nullable=False, default="{}")
    ai_explanation = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# Database Manager
# ---------------------------------------------------------------------------


class DatabaseManager:
    """Manages all SQLite persistence operations for LearnMate AI."""

    def __init__(self) -> None:
        DB_DIR.mkdir(parents=True, exist_ok=True)
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized at %s", DB_PATH)

    def _session(self) -> Session:
        return SessionLocal()

    # ── Student Profiles ────────────────────────────────────────────────

    def save_profile(self, student_id: str, profile: Dict[str, Any]) -> None:
        with self._session() as session:
            row = session.get(StudentProfileRow, student_id)
            if row is None:
                row = StudentProfileRow(student_id=student_id)
                session.add(row)

            row.name = profile.get("name", "")
            row.email = profile.get("email")
            row.career_goal = profile.get("career_goal", "")
            row.skill_level = profile.get("skill_level", "beginner")
            row.learning_style = profile.get("learning_style")
            row.hours_per_week = profile.get("hours_per_week")
            row.preferred_study_time = profile.get("preferred_study_time")
            row.preferred_job_role = profile.get("preferred_job_role")
            row.dream_company = profile.get("dream_company")
            row.experience_level = profile.get("experience_level")
            row.github_url = profile.get("github_url")
            row.linkedin_url = profile.get("linkedin_url")
            row.current_skills = json.dumps(profile.get("current_skills", []))
            row.interests = json.dumps(profile.get("interests", []))
            row.current_goals = json.dumps(profile.get("current_goals", []))
            row.completed_topics = json.dumps(profile.get("completed_topics", []))
            row.progress_percentage = profile.get("progress_percentage", 0.0)
            row.updated_at = datetime.now(timezone.utc)
            session.commit()
            logger.debug("Saved profile for student '%s'", student_id)

    def load_profile(self, student_id: str) -> Optional[Dict[str, Any]]:
        with self._session() as session:
            row = session.get(StudentProfileRow, student_id)
            if row is None:
                return None
            return self._row_to_profile(row)

    def load_all_profiles(self) -> Dict[str, Dict[str, Any]]:
        with self._session() as session:
            rows = session.query(StudentProfileRow).all()
            return {row.student_id: self._row_to_profile(row) for row in rows}

    def delete_profile(self, student_id: str) -> None:
        with self._session() as session:
            row = session.get(StudentProfileRow, student_id)
            if row:
                session.delete(row)
                session.commit()
                logger.debug("Deleted profile for student '%s'", student_id)

    @staticmethod
    def _row_to_profile(row: StudentProfileRow) -> Dict[str, Any]:
        return {
            "student_id": row.student_id,
            "name": row.name,
            "email": row.email,
            "career_goal": row.career_goal,
            "skill_level": row.skill_level,
            "learning_style": row.learning_style,
            "hours_per_week": row.hours_per_week,
            "preferred_study_time": row.preferred_study_time,
            "preferred_job_role": row.preferred_job_role,
            "dream_company": row.dream_company,
            "experience_level": row.experience_level,
            "github_url": row.github_url,
            "linkedin_url": row.linkedin_url,
            "current_skills": json.loads(row.current_skills) if row.current_skills else [],
            "interests": json.loads(row.interests) if row.interests else [],
            "current_goals": json.loads(row.current_goals) if row.current_goals else [],
            "completed_topics": json.loads(row.completed_topics) if row.completed_topics else [],
            "progress_percentage": row.progress_percentage or 0.0,
        }

    # ── Roadmaps ────────────────────────────────────────────────────────

    def save_roadmap(self, student_id: str, roadmap: Dict[str, Any]) -> None:
        with self._session() as session:
            row = session.get(RoadmapRow, student_id)
            if row is None:
                row = RoadmapRow(student_id=student_id)
                session.add(row)
            row.roadmap_data = json.dumps(roadmap)
            row.updated_at = datetime.now(timezone.utc)
            session.commit()
            logger.debug("Saved roadmap for student '%s'", student_id)

    def load_roadmap(self, student_id: str) -> Optional[Dict[str, Any]]:
        with self._session() as session:
            row = session.get(RoadmapRow, student_id)
            if row is None:
                return None
            return json.loads(row.roadmap_data)

    def load_all_roadmaps(self) -> Dict[str, Any]:
        with self._session() as session:
            rows = session.query(RoadmapRow).all()
            return {row.student_id: json.loads(row.roadmap_data) for row in rows}

    def delete_roadmap(self, student_id: str) -> None:
        with self._session() as session:
            row = session.get(RoadmapRow, student_id)
            if row:
                session.delete(row)
                session.commit()
                logger.debug("Deleted roadmap for student '%s'", student_id)

    # ── Progress ────────────────────────────────────────────────────────

    def save_progress(self, student_id: str, progress: Dict[str, Any]) -> None:
        with self._session() as session:
            row = session.get(ProgressRow, student_id)
            if row is None:
                row = ProgressRow(student_id=student_id)
                session.add(row)
            row.progress_data = json.dumps(progress)
            row.updated_at = datetime.now(timezone.utc)
            session.commit()
            logger.debug("Saved progress for student '%s'", student_id)

    def load_progress(self, student_id: str) -> Optional[Dict[str, Any]]:
        with self._session() as session:
            row = session.get(ProgressRow, student_id)
            if row is None:
                return None
            return json.loads(row.progress_data)

    def load_all_progress(self) -> Dict[str, Dict[str, Any]]:
        with self._session() as session:
            rows = session.query(ProgressRow).all()
            return {row.student_id: json.loads(row.progress_data) for row in rows}

    def delete_progress(self, student_id: str) -> None:
        with self._session() as session:
            row = session.get(ProgressRow, student_id)
            if row:
                session.delete(row)
                session.commit()
                logger.debug("Deleted progress for student '%s'", student_id)

    # ── Study Sessions ─────────────────────────────────────────────────

    def save_study_session(self, session_id: str, data: Dict[str, Any]) -> None:
        with self._session() as session:
            row = session.get(StudySessionRow, session_id)
            if row is None:
                row = StudySessionRow(id=session_id)
                session.add(row)
            row.user_id = data.get("user_id", "")
            row.title = data.get("title", "")
            row.description = data.get("description", "")
            row.topic = data.get("topic")
            row.date = data.get("date", "")
            row.start_time = data.get("start_time", "")
            row.end_time = data.get("end_time", "")
            row.duration = data.get("duration", 1.0)
            row.status = data.get("status", "scheduled")
            row.priority = data.get("priority", "medium")
            row.difficulty = data.get("difficulty")
            row.course_id = data.get("course_id")
            row.project_id = data.get("project_id")
            row.repeat_type = data.get("repeat_type", "none")
            row.reminder_minutes = data.get("reminder_minutes", 15)
            row.completed_at = data.get("completed_at")
            row.updated_at = datetime.now(timezone.utc)
            session.commit()

    def load_study_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        with self._session() as session:
            rows = (
                session.query(StudySessionRow)
                .filter(StudySessionRow.user_id == user_id)
                .order_by(StudySessionRow.date, StudySessionRow.start_time)
                .all()
            )
            return [self._row_to_study_session(r) for r in rows]

    def load_study_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._session() as session:
            row = session.get(StudySessionRow, session_id)
            if row is None:
                return None
            return self._row_to_study_session(row)

    def delete_study_session(self, session_id: str) -> None:
        with self._session() as session:
            row = session.get(StudySessionRow, session_id)
            if row:
                session.delete(row)
                session.commit()

    def delete_all_study_sessions(self, user_id: str) -> None:
        with self._session() as session:
            session.query(StudySessionRow).filter(
                StudySessionRow.user_id == user_id
            ).delete()
            session.commit()

    @staticmethod
    def _row_to_study_session(row: StudySessionRow) -> Dict[str, Any]:
        return {
            "id": row.id,
            "user_id": row.user_id,
            "title": row.title,
            "description": row.description or "",
            "topic": row.topic,
            "date": row.date,
            "start_time": row.start_time,
            "end_time": row.end_time,
            "duration": row.duration,
            "status": row.status,
            "priority": row.priority,
            "difficulty": row.difficulty,
            "course_id": row.course_id,
            "project_id": row.project_id,
            "repeat_type": row.repeat_type or "none",
            "reminder_minutes": row.reminder_minutes,
            "completed_at": row.completed_at.isoformat() if row.completed_at else None,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        }

    # ── Study Goals ────────────────────────────────────────────────────

    def save_study_goal(self, user_id: str, data: Dict[str, Any]) -> None:
        with self._session() as session:
            row = session.query(StudyGoalRow).filter(StudyGoalRow.user_id == user_id).first()
            if row is None:
                row = StudyGoalRow(user_id=user_id)
                session.add(row)
            row.weekly_goal_hours = data.get("weekly_goal_hours", 10.0)
            row.daily_goal_minutes = data.get("daily_goal_minutes")
            row.preferred_study_time = data.get("preferred_study_time")
            row.preferred_days = json.dumps(data.get("preferred_days", []))
            row.updated_at = datetime.now(timezone.utc)
            session.commit()

    def load_study_goal(self, user_id: str) -> Optional[Dict[str, Any]]:
        with self._session() as session:
            row = session.query(StudyGoalRow).filter(StudyGoalRow.user_id == user_id).first()
            if row is None:
                return None
            return {
                "id": row.id,
                "user_id": row.user_id,
                "weekly_goal_hours": row.weekly_goal_hours,
                "daily_goal_minutes": row.daily_goal_minutes,
                "preferred_study_time": row.preferred_study_time,
                "preferred_days": json.loads(row.preferred_days) if row.preferred_days else [],
            }

    def delete_study_goal(self, user_id: str) -> None:
        with self._session() as session:
            row = session.query(StudyGoalRow).filter(StudyGoalRow.user_id == user_id).first()
            if row:
                session.delete(row)
                session.commit()

    # ── Career Test Results ────────────────────────────────────────────

    def save_career_test_result(self, result_id: str, data: Dict[str, Any]) -> None:
        with self._session() as session:
            row = session.get(CareerTestResultRow, result_id)
            if row is None:
                row = CareerTestResultRow(id=result_id)
                session.add(row)
            row.user_id = data.get("user_id", "")
            row.top_careers = json.dumps(data.get("top_careers", []))
            row.all_scores = json.dumps(data.get("all_scores", []))
            row.answers = json.dumps(data.get("answers", {}))
            row.ai_explanation = json.dumps(data.get("ai_explanation", {}))
            session.commit()

    def load_career_test_results(self, user_id: str) -> List[Dict[str, Any]]:
        with self._session() as session:
            rows = (
                session.query(CareerTestResultRow)
                .filter(CareerTestResultRow.user_id == user_id)
                .order_by(CareerTestResultRow.created_at.desc())
                .all()
            )
            return [self._row_to_career_result(r) for r in rows]

    @staticmethod
    def _row_to_career_result(row: CareerTestResultRow) -> Dict[str, Any]:
        return {
            "id": row.id,
            "user_id": row.user_id,
            "top_careers": json.loads(row.top_careers) if row.top_careers else [],
            "all_scores": json.loads(row.all_scores) if row.all_scores else [],
            "answers": json.loads(row.answers) if row.answers else {},
            "ai_explanation": json.loads(row.ai_explanation) if row.ai_explanation else {},
            "created_at": row.created_at.isoformat() if row.created_at else "",
        }

    def delete_career_test_results(self, user_id: str) -> None:
        with self._session() as session:
            session.query(CareerTestResultRow).filter(
                CareerTestResultRow.user_id == user_id
            ).delete()
            session.commit()

    # ── Bulk load (startup) ────────────────────────────────────────────

    def load_all(self) -> Dict[str, Dict[str, Any]]:
        return {
            "profiles": self.load_all_profiles(),
            "roadmaps": self.load_all_roadmaps(),
            "progress": self.load_all_progress(),
        }


# Singleton
_db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
