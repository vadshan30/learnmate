"""Auth API routes for LearnMate AI."""

from __future__ import annotations

import asyncio
import logging
import os

from fastapi import APIRouter, Depends, Header, HTTPException

from app.dependencies import Store, get_store
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    GuestMigrationRequest,
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserInfo,
)
from app.schemas.responses import ErrorResponse, SuccessResponse
from app.services import auth_service
from app.utils.jwt import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    create_refresh_token,
    decode_token,
)

logger = logging.getLogger("learnmate.api.auth")

router = APIRouter(prefix="/api/auth", tags=["auth"])

ACCESS_TOKEN_EXPIRE_SECONDS = ACCESS_TOKEN_EXPIRE_MINUTES * 60
APP_ENV = os.getenv("APP_ENV", "development")


async def get_current_user(authorization: str = Header(None)) -> dict:
    """FastAPI dependency that extracts and validates the JWT from the Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        from app.exceptions import UnauthorizedError
        raise UnauthorizedError("Missing or invalid authorization header")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        from app.exceptions import UnauthorizedError
        raise UnauthorizedError("Invalid or expired token")
    user = auth_service.get_user_by_id(payload["sub"])
    if not user:
        from app.exceptions import UnauthorizedError
        raise UnauthorizedError("User not found")
    return user


@router.post(
    "/register",
    status_code=201,
    summary="Register a new user",
    responses={
        201: {"description": "User registered successfully"},
        409: {"model": ErrorResponse, "description": "Email or username already exists"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
)
async def register(body: RegisterRequest, store: Store = Depends(get_store)) -> TokenResponse:
    try:
        user = await asyncio.to_thread(
            auth_service.create_user,
            body.full_name, body.username, body.email, body.password,
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    student_id = user["id"]
    profile = {
        "name": body.full_name,
        "student_id": student_id,
        "email": body.email,
        "current_skills": [],
        "interests": [],
        "career_goal": "",
        "skill_level": "beginner",
        "completed_topics": [],
        "progress_percentage": 0.0,
    }
    store.student_profiles[student_id] = profile
    await asyncio.to_thread(store.save_student_profile, student_id)

    access_token = create_access_token(user["id"], user["username"])
    refresh_token = create_refresh_token(user["id"], user["username"])

    logger.info("User registered: %s (%s)", user["username"], user["id"])

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_SECONDS,
        user=UserInfo(**user),
    )


@router.post(
    "/login",
    summary="Login with email/username and password",
    responses={
        200: {"description": "Login successful"},
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
        429: {"model": ErrorResponse, "description": "Too many login attempts"},
    },
)
async def login(body: LoginRequest) -> TokenResponse:
    try:
        user = await asyncio.to_thread(
            auth_service.authenticate_user,
            body.email_or_username, body.password,
        )
    except PermissionError as e:
        raise HTTPException(status_code=429, detail=str(e))

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(user["id"], user["username"])
    refresh_token = create_refresh_token(user["id"], user["username"])

    logger.info("User logged in: %s", user["username"])

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_SECONDS,
        user=UserInfo(**user),
    )


@router.post(
    "/refresh",
    summary="Refresh access token",
    responses={
        200: {"description": "Token refreshed"},
        401: {"model": ErrorResponse, "description": "Invalid refresh token"},
    },
)
async def refresh_token(body: RefreshRequest) -> TokenResponse:
    payload = decode_token(body.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user = auth_service.get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    access_token = create_access_token(user["id"], user["username"])
    new_refresh_token = create_refresh_token(user["id"], user["username"])

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_SECONDS,
        user=UserInfo(**user),
    )


@router.get(
    "/me",
    summary="Get current user info",
    responses={
        200: {"description": "User info"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
async def get_me(user: dict = Depends(get_current_user)) -> UserInfo:
    return UserInfo(**user)


@router.post(
    "/forgot-password",
    summary="Request a password reset link",
    response_model=MessageResponse,
    responses={
        200: {"description": "If the account exists, a reset link has been sent"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
)
async def forgot_password(body: ForgotPasswordRequest) -> MessageResponse:
    raw_token = await asyncio.to_thread(auth_service.create_forgot_password_token, body.email)

    if APP_ENV == "development" and raw_token:
        reset_link = f"http://localhost:5173/reset-password?token={raw_token}"
        return MessageResponse(
            message=f"If the account exists, a reset link has been sent to your email. "
                    f"[DEV MODE] Reset link: {reset_link}"
        )

    return MessageResponse(
        message="If the account exists, a reset link has been sent to your email."
    )


@router.post(
    "/reset-password",
    summary="Reset password using token",
    response_model=MessageResponse,
    responses={
        200: {"description": "Password reset successfully"},
        400: {"model": ErrorResponse, "description": "Invalid or expired token"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
)
async def reset_password(body: ResetPasswordRequest) -> MessageResponse:
    try:
        await asyncio.to_thread(auth_service.reset_password, body.token, body.new_password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return MessageResponse(message="Password has been reset successfully.")


@router.post(
    "/change-password",
    summary="Change password for authenticated user",
    response_model=MessageResponse,
    responses={
        200: {"description": "Password changed successfully"},
        400: {"model": ErrorResponse, "description": "Current password is incorrect"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
)
async def change_password(
    body: ChangePasswordRequest,
    user: dict = Depends(get_current_user),
) -> MessageResponse:
    try:
        await asyncio.to_thread(
            auth_service.change_password,
            user["id"], body.current_password, body.new_password,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return MessageResponse(message="Password has been changed successfully.")


@router.post(
    "/migrate-guest",
    summary="Import guest data into user account",
    response_model=MessageResponse,
    responses={
        200: {"description": "Guest data imported"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
async def migrate_guest(
    body: GuestMigrationRequest,
    user: dict = Depends(get_current_user),
) -> MessageResponse:
    guest_data = {}
    if body.profile:
        guest_data["profile"] = body.profile
    if body.roadmap:
        guest_data["roadmap"] = body.roadmap
    if body.progress:
        guest_data["progress"] = body.progress
    if body.study_sessions:
        guest_data["study_sessions"] = body.study_sessions
    if body.study_goal:
        guest_data["study_goal"] = body.study_goal

    if not guest_data:
        return MessageResponse(message="No guest data to import.")

    imported = await asyncio.to_thread(auth_service.migrate_guest_data, user["id"], guest_data)

    summary_parts = []
    if imported.get("profile"):
        summary_parts.append("profile")
    if imported.get("roadmap"):
        summary_parts.append("roadmap")
    if imported.get("progress"):
        summary_parts.append("progress")
    if imported.get("study_sessions"):
        summary_parts.append(f"{imported['study_sessions']} study sessions")
    if imported.get("study_goal"):
        summary_parts.append("study goal")

    msg = f"Imported: {', '.join(summary_parts)}." if summary_parts else "No guest data to import."
    logger.info("Guest migration for user %s: %s", user["id"], msg)
    return MessageResponse(message=msg)
