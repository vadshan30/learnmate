from __future__ import annotations

import logging
import traceback
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("learnmate.errors")


class LearnMateError(Exception):
    """Base exception for LearnMate domain errors."""

    def __init__(self, message: str, error_code: str = "UNKNOWN_ERROR", status_code: int = 500, details: Any = None):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class StudentNotFoundError(LearnMateError):
    def __init__(self, student_id: str):
        super().__init__(
            message=f"Student '{student_id}' not found",
            error_code="STUDENT_NOT_FOUND",
            status_code=404,
        )


class RoadmapNotFoundError(LearnMateError):
    def __init__(self, student_id: str):
        super().__init__(
            message=f"No roadmap found for student '{student_id}'",
            error_code="ROADMAP_NOT_FOUND",
            status_code=404,
        )


class StudySessionNotFoundError(LearnMateError):
    def __init__(self, session_id: str):
        super().__init__(
            message=f"Study session '{session_id}' not found",
            error_code="STUDY_SESSION_NOT_FOUND",
            status_code=404,
        )


class ServiceUnavailableError(LearnMateError):
    def __init__(self, service_name: str):
        super().__init__(
            message=f"Service '{service_name}' is currently unavailable",
            error_code="SERVICE_UNAVAILABLE",
            status_code=503,
        )


class UnauthorizedError(LearnMateError):
    def __init__(self, message: str = "Not authenticated"):
        super().__init__(
            message=message,
            error_code="UNAUTHORIZED",
            status_code=401,
        )


class ForbiddenError(LearnMateError):
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            error_code="FORBIDDEN",
            status_code=403,
        )


def _error_response(status_code: int, message: str, error_code: str, details: Any = None) -> JSONResponse:
    body: dict[str, Any] = {
        "success": False,
        "message": message,
        "error_code": error_code,
    }
    if details is not None:
        body["details"] = details
    return JSONResponse(status_code=status_code, content=body)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(LearnMateError)
    async def learnmate_error_handler(_req: Request, exc: LearnMateError) -> JSONResponse:
        logger.warning("Domain error [%s]: %s", exc.error_code, exc.message)
        return _error_response(exc.status_code, exc.message, exc.error_code, exc.details)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_req: Request, exc: RequestValidationError) -> JSONResponse:
        errors = exc.errors()
        message = "Request validation failed"
        if errors:
            first = errors[0]
            loc = " -> ".join(str(p) for p in first.get("loc", []))
            msg = first.get("msg", "")
            message = f"{loc}: {msg}" if loc else msg
        logger.warning("Validation error: %s", message)
        return _error_response(422, message, "VALIDATION_ERROR", details=errors)

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_req: Request, exc: Exception) -> JSONResponse:
        logger.error("Unhandled error: %s\n%s", exc, traceback.format_exc())
        return _error_response(500, "Internal server error", "INTERNAL_ERROR")
