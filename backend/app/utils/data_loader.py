"""Reusable data loader utility for LearnMate AI.

Loads and validates JSON datasets from the data directory. Each loader
verifies the file exists, parses JSON, validates the schema, and returns
an empty list (instead of crashing) when anything goes wrong.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("learnmate.data_loader")

# Resolve data directory relative to the backend root
_BACKEND_ROOT: Path = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR: Path = _BACKEND_ROOT / "data"


def _load_json_file(filename: str) -> List[Dict[str, Any]]:
    """Load a JSON file from the data directory.

    Returns an empty list if the file is missing or contains invalid JSON.
    """
    path = DATA_DIR / filename
    if not path.exists():
        logger.error("[DATA] File not found: %s", path)
        return []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        logger.error("[DATA] Invalid JSON in %s: %s", path, exc)
        return []
    except OSError as exc:
        logger.error("[DATA] Cannot read %s: %s", path, exc)
        return []

    if not isinstance(data, list):
        logger.error("[DATA] Expected a JSON array in %s, got %s", path, type(data).__name__)
        return []

    return data


def validate_course(item: Dict[str, Any]) -> bool:
    """Validate that a course dict has all required fields.

    Required: id, title, provider, duration, level, description, skills_gained.
    URL is checked and warned about but does NOT fail validation.
    """
    required = ["id", "title", "provider", "duration", "level", "description"]
    for field in required:
        if not item.get(field):
            logger.warning("[DATA] Course missing required field '%s': %s", field, item.get("id", "unknown"))
            return False

    # Skills are required (at least one of skills_gained, required_skills, skills_covered)
    has_skills = any(item.get(k) for k in ("skills_gained", "required_skills", "skills_covered"))
    if not has_skills:
        logger.warning("[DATA] Course has no skills list: %s", item.get("id", "unknown"))
        return False

    # URL is recommended but not required - warn only
    if not item.get("url"):
        logger.warning("[DATA] Course '%s' has no URL - button will show as unavailable", item.get("id", "unknown"))

    return True


def validate_project(item: Dict[str, Any]) -> bool:
    """Validate that a project dict has all required fields."""
    required = ["id", "title"]
    for field in required:
        if not item.get(field):
            logger.warning("[DATA] Project missing required field '%s': %s", field, item.get("id", "unknown"))
            return False
    return True


def validate_certification(item: Dict[str, Any]) -> bool:
    """Validate that a certification dict has all required fields.

    Required: id, name (or title), provider.
    """
    item_id = item.get("id", "unknown")
    if not item.get("id"):
        logger.warning("[DATA] Certification missing 'id': %s", item_id)
        return False
    if not (item.get("name") or item.get("title")):
        logger.warning("[DATA] Certification '%s' missing 'name'/'title' field — SKIPPED", item_id)
        return False
    if not item.get("provider"):
        logger.warning("[DATA] Certification '%s' missing 'provider' field — SKIPPED", item_id)
        return False
    return True


def validate_career_pathway(item: Dict[str, Any]) -> bool:
    """Validate that a career pathway dict has all required fields."""
    required = ["name", "description"]
    for field in required:
        if not item.get(field):
            logger.warning("[DATA] Career pathway missing required field '%s': %s", field, item.get("name", "unknown"))
            return False
    return True


def load_courses() -> List[Dict[str, Any]]:
    """Load and validate courses from courses.json.

    Returns:
        List of validated course dicts. Invalid entries are
        logged and skipped instead of crashing the application.
    """
    raw = _load_json_file("courses.json")
    valid: List[Dict[str, Any]] = []
    skipped: List[str] = []
    for item in raw:
        if validate_course(item):
            valid.append(item)
        else:
            skipped.append(item.get("id", "unknown"))
    logger.info("[DATA] Loaded %d/%d courses", len(valid), len(raw))
    if skipped:
        logger.warning("[DATA] Skipped courses: %s", ", ".join(skipped))
    return valid


def load_projects() -> List[Dict[str, Any]]:
    """Load and validate projects from projects.json.

    Returns:
        List of validated project dicts. Invalid entries are
        logged and skipped instead of crashing the application.
    """
    raw = _load_json_file("projects.json")
    valid: List[Dict[str, Any]] = []
    skipped: List[str] = []
    for item in raw:
        if validate_project(item):
            valid.append(item)
        else:
            skipped.append(item.get("id", "unknown"))
    logger.info("[DATA] Loaded %d/%d projects", len(valid), len(raw))
    if skipped:
        logger.warning("[DATA] Skipped projects: %s", ", ".join(skipped))
    return valid


def load_certifications() -> List[Dict[str, Any]]:
    """Load and validate certifications from certifications.json.

    Returns:
        List of validated certification dicts. Invalid entries are
        logged and skipped instead of crashing the application.
    """
    raw = _load_json_file("certifications.json")
    valid: List[Dict[str, Any]] = []
    skipped: List[str] = []
    for item in raw:
        if validate_certification(item):
            valid.append(item)
        else:
            skipped.append(item.get("id", "unknown"))
    logger.info("[DATA] Loaded %d/%d certifications", len(valid), len(raw))
    if skipped:
        logger.warning("[DATA] Skipped certifications: %s", ", ".join(skipped))
    return valid


def load_career_pathways() -> List[Dict[str, Any]]:
    """Load and validate career pathways from career_pathways.json.

    Returns:
        List of validated career pathway dicts.
    """
    raw = _load_json_file("career_pathways.json")
    valid = [item for item in raw if validate_career_pathway(item)]
    logger.info("[DATA] Loaded %d/%d career pathways", len(valid), len(raw))
    return valid


def load_all_datasets() -> Dict[str, List[Dict[str, Any]]]:
    """Load all datasets and return them as a dictionary.

    Returns:
        Dict with keys: courses, projects, certifications, career_pathways.
    """
    return {
        "courses": load_courses(),
        "projects": load_projects(),
        "certifications": load_certifications(),
        "career_pathways": load_career_pathways(),
    }
