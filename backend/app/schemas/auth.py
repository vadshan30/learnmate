"""Auth request/response schemas for LearnMate AI."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from app.utils.security import validate_password_strength


class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., max_length=200)
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("full_name")
    @classmethod
    def name_must_be_non_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Name cannot be empty")
        return stripped

    @field_validator("username")
    @classmethod
    def username_must_be_valid(cls, v: str) -> str:
        stripped = v.strip()
        if not re.match(r"^[a-zA-Z0-9_-]+$", stripped):
            raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")
        return stripped.lower()

    @field_validator("email")
    @classmethod
    def email_must_be_valid(cls, v: str) -> str:
        stripped = v.strip().lower()
        if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", stripped):
            raise ValueError("Invalid email format")
        return stripped

    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, v: str) -> str:
        errors = validate_password_strength(v)
        if errors:
            raise ValueError("; ".join(errors))
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_must_match(cls, v: str, info) -> str:
        password = info.data.get("password")
        if password and v != password:
            raise ValueError("Passwords do not match")
        return v


class LoginRequest(BaseModel):
    email_or_username: str = Field(..., min_length=1, max_length=200)
    password: str = Field(..., min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Access token expiry in seconds")
    user: "UserInfo"


class UserInfo(BaseModel):
    id: str
    full_name: str
    username: str
    email: str
    profile_image: Optional[str] = None
    created_at: datetime


class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., max_length=200)

    @field_validator("email")
    @classmethod
    def email_must_be_valid(cls, v: str) -> str:
        stripped = v.strip().lower()
        if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", stripped):
            raise ValueError("Invalid email format")
        return stripped


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=1, max_length=200)
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def password_must_be_strong(cls, v: str) -> str:
        errors = validate_password_strength(v)
        if errors:
            raise ValueError("; ".join(errors))
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_must_match(cls, v: str, info) -> str:
        password = info.data.get("new_password")
        if password and v != password:
            raise ValueError("Passwords do not match")
        return v


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1, max_length=128)
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def password_must_be_strong(cls, v: str) -> str:
        errors = validate_password_strength(v)
        if errors:
            raise ValueError("; ".join(errors))
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_must_match(cls, v: str, info) -> str:
        password = info.data.get("new_password")
        if password and v != password:
            raise ValueError("Passwords do not match")
        return v


class GuestMigrationRequest(BaseModel):
    profile: Optional[Dict[str, Any]] = None
    roadmap: Optional[Dict[str, Any]] = None
    progress: Optional[Dict[str, Any]] = None
    study_sessions: Optional[List[Dict[str, Any]]] = None
    study_goal: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    message: str
