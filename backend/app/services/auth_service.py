"""Auth service for LearnMate AI – registration, login, tokens, password reset, guest migration."""

from __future__ import annotations

import hashlib
import logging
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import or_

from app.database import PasswordResetTokenRow, SessionLocal, UserRow
from app.utils.security import hash_password, verify_password

logger = logging.getLogger("learnmate.auth")

RESET_TOKEN_EXPIRE_MINUTES = 15

# Simple in-memory rate limiter for login attempts
_login_attempts: Dict[str, List[datetime]] = {}
MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_MINUTES = 15


def _check_rate_limit(identifier: str) -> bool:
    """Returns True if the request is allowed, False if rate-limited."""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=LOGIN_LOCKOUT_MINUTES)
    attempts = _login_attempts.get(identifier, [])
    _login_attempts[identifier] = [a for a in attempts if a > cutoff]
    if len(_login_attempts[identifier]) >= MAX_LOGIN_ATTEMPTS:
        return False
    return True


def _record_login_attempt(identifier: str) -> None:
    _login_attempts.setdefault(identifier, []).append(datetime.now(timezone.utc))


def _clear_login_attempts(identifier: str) -> None:
    _login_attempts.pop(identifier, None)


def create_user(full_name: str, username: str, email: str, password: str) -> dict:
    """Create a new user. Raises ValueError on duplicate email/username."""
    with SessionLocal() as session:
        existing = session.query(UserRow).filter(
            or_(UserRow.email == email, UserRow.username == username)
        ).first()
        if existing:
            if existing.email == email:
                raise ValueError("Email already registered")
            raise ValueError("Username already taken")

        now = datetime.now(timezone.utc)
        user = UserRow(
            id=str(uuid.uuid4()),
            full_name=full_name,
            username=username,
            email=email,
            password_hash=hash_password(password),
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        logger.info("Created user '%s' (%s)", username, user.id)
        return _user_to_dict(user)


def authenticate_user(email_or_username: str, password: str) -> Optional[dict]:
    """Authenticate by email/username + password. Returns user dict or None."""
    identifier = email_or_username.lower().strip()

    if not _check_rate_limit(identifier):
        raise PermissionError("Too many login attempts. Please try again in 15 minutes.")

    with SessionLocal() as session:
        user = session.query(UserRow).filter(
            or_(UserRow.email == identifier, UserRow.username == identifier)
        ).first()
        if not user or not user.is_active:
            _record_login_attempt(identifier)
            return None
        if not verify_password(password, user.password_hash):
            _record_login_attempt(identifier)
            return None

        _clear_login_attempts(identifier)
        user.last_login = datetime.now(timezone.utc)
        session.commit()
        return _user_to_dict(user)


def get_user_by_id(user_id: str) -> Optional[dict]:
    """Fetch a user by UUID."""
    with SessionLocal() as session:
        user = session.get(UserRow, user_id)
        if not user or not user.is_active:
            return None
        return _user_to_dict(user)


def get_user_by_email(email: str) -> Optional[dict]:
    """Fetch a user by email."""
    with SessionLocal() as session:
        user = session.query(UserRow).filter(UserRow.email == email.lower().strip()).first()
        if not user or not user.is_active:
            return None
        return _user_to_dict(user)


def create_forgot_password_token(email: str) -> Optional[str]:
    """Generate a password reset token for the given email.

    Returns the raw token string (to be sent via email).
    Always returns the same message regardless of whether the email exists.
    Returns None if the email does not exist (but still returns token for response).
    """
    raw_token = secrets.token_urlsafe(48)
    hashed_token = hashlib.sha256(raw_token.encode()).hexdigest()

    with SessionLocal() as session:
        user = session.query(UserRow).filter(
            UserRow.email == email.lower().strip()
        ).first()

        if user:
            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)

            reset_row = PasswordResetTokenRow(
                user_id=user.id,
                hashed_token=hashed_token,
                expires_at=expires_at,
                used=0,
            )
            session.add(reset_row)
            session.commit()

            reset_link = f"http://localhost:5173/reset-password?token={raw_token}"
            logger.info("Password reset link for %s: %s", email, reset_link)
            return raw_token
        else:
            logger.info("Password reset requested for non-existent email: %s", email)
            return None


def reset_password(token: str, new_password: str) -> bool:
    """Reset a user's password using a valid reset token.

    Returns True on success, raises ValueError on failure.
    """
    hashed_token = hashlib.sha256(token.encode()).hexdigest()
    now = datetime.now(timezone.utc)

    with SessionLocal() as session:
        reset_row = session.query(PasswordResetTokenRow).filter(
            PasswordResetTokenRow.hashed_token == hashed_token,
            PasswordResetTokenRow.used == 0,
        ).first()

        if not reset_row:
            raise ValueError("Invalid or already used reset token")

        expires_at = reset_row.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < now:
            raise ValueError("Reset token has expired")

        user = session.get(UserRow, reset_row.user_id)
        if not user or not user.is_active:
            raise ValueError("User account not found or inactive")

        user.password_hash = hash_password(new_password)
        user.updated_at = now
        reset_row.used = 1
        session.commit()

        logger.info("Password reset completed for user %s", user.id)
        return True


def change_password(user_id: str, current_password: str, new_password: str) -> bool:
    """Change a user's password after verifying the current password.

    Returns True on success, raises ValueError on failure.
    """
    with SessionLocal() as session:
        user = session.get(UserRow, user_id)
        if not user or not user.is_active:
            raise ValueError("User account not found or inactive")

        if not verify_password(current_password, user.password_hash):
            raise ValueError("Current password is incorrect")

        user.password_hash = hash_password(new_password)
        user.updated_at = datetime.now(timezone.utc)
        session.commit()

        logger.info("Password changed for user %s", user_id)
        return True


def migrate_guest_data(user_id: str, guest_data: dict) -> dict:
    """Import guest progress into a newly registered user account.

    Args:
        user_id: The user ID to import data into.
        guest_data: Dict with optional keys: profile, roadmap, progress, study_sessions, study_goal.

    Returns:
        Dict with summary of what was imported.
    """
    from app.database import get_db_manager
    db = get_db_manager()
    imported = {}

    profile = guest_data.get("profile")
    if profile and isinstance(profile, dict):
        profile["student_id"] = user_id
        db.save_profile(user_id, profile)
        imported["profile"] = True
        logger.info("Migrated guest profile for user %s", user_id)

    roadmap = guest_data.get("roadmap")
    if roadmap and isinstance(roadmap, dict):
        db.save_roadmap(user_id, roadmap)
        imported["roadmap"] = True
        logger.info("Migrated guest roadmap for user %s", user_id)

    progress = guest_data.get("progress")
    if progress and isinstance(progress, dict):
        db.save_progress(user_id, progress)
        imported["progress"] = True
        logger.info("Migrated guest progress for user %s", user_id)

    study_sessions = guest_data.get("study_sessions")
    if study_sessions and isinstance(study_sessions, list):
        for session_data in study_sessions:
            if isinstance(session_data, dict):
                session_data["user_id"] = user_id
                db.save_study_session(session_data.get("id", str(uuid.uuid4())), session_data)
        imported["study_sessions"] = len(study_sessions)
        logger.info("Migrated %d guest study sessions for user %s", len(study_sessions), user_id)

    study_goal = guest_data.get("study_goal")
    if study_goal and isinstance(study_goal, dict):
        db.save_study_goal(user_id, study_goal)
        imported["study_goal"] = True
        logger.info("Migrated guest study goal for user %s", user_id)

    return imported


def _user_to_dict(user: UserRow) -> dict:
    """Convert a UserRow ORM object to a dict for API responses."""
    return {
        "id": user.id,
        "full_name": user.full_name,
        "username": user.username,
        "email": user.email,
        "profile_image": user.profile_image,
        "created_at": user.created_at.isoformat() if user.created_at else "",
    }
