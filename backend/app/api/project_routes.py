"""Project detail and action routes for LearnMate AI.

Provides endpoints for project details, starter kit resources,
smart course recommendations, and project save/complete actions.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import Store, get_store, get_student_or_404
from app.schemas.responses import ErrorResponse, SuccessResponse
from app.services import resource_service

logger = logging.getLogger("learnmate.projects")

router = APIRouter(prefix="/api/projects", tags=["projects"])

# ── Data paths ────────────────────────────────────────────────────────

_BACKEND_ROOT: Path = Path(__file__).resolve().parent.parent.parent.parent
_PROJECT_RESOURCES_PATH: Path = _BACKEND_ROOT / "data" / "project_resources.json"

_project_resources_cache: Optional[Dict[str, Any]] = None


def _load_project_resources() -> Dict[str, Any]:
    """Load project_resources.json (cached in memory)."""
    global _project_resources_cache
    if _project_resources_cache is not None:
        return _project_resources_cache
    if not _PROJECT_RESOURCES_PATH.exists():
        logger.warning("[DATA] project_resources.json not found at %s", _PROJECT_RESOURCES_PATH)
        _project_resources_cache = {}
        return _project_resources_cache
    try:
        with open(_PROJECT_RESOURCES_PATH, "r", encoding="utf-8") as fh:
            _project_resources_cache = json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("[DATA] Failed to load project_resources.json: %s", exc)
        _project_resources_cache = {}
    return _project_resources_cache


def _find_project(project_id: str) -> Optional[Dict[str, Any]]:
    """Find a project by ID from the resource service."""
    projects = resource_service.get_projects()
    for p in projects:
        if p.get("id") == project_id:
            return p
    return None


def _recommend_courses_for_project(project: Dict[str, Any], top_k: int = 5) -> List[Dict[str, Any]]:
    """Smart recommendation: match project required_skills with course skills_gained.

    Returns courses ranked by skill overlap ratio (highest first).
    """
    required = set(s.lower().strip() for s in project.get("skills_required", []))
    if not required:
        return []

    courses = resource_service.get_all_courses()
    scored: List[Dict[str, Any]] = []

    for course in courses:
        course_skills = set(
            s.lower().strip()
            for s in (course.get("skills_gained") or [])
        )
        if not course_skills:
            continue

        overlap = required & course_skills
        if overlap:
            score = len(overlap) / len(required)
            scored.append({
                **course,
                "_match_score": round(score, 3),
                "_matched_skills": sorted(overlap),
            })

    scored.sort(key=lambda x: x["_match_score"], reverse=True)
    return scored[:top_k]


def _determine_project_domain(project: Dict[str, Any]) -> str:
    """Infer the domain for a project based on its skills and technologies."""
    skills = [s.lower() for s in project.get("skills_required", [])]
    techs = [t.lower() for t in project.get("technologies", [])]
    all_terms = skills + techs

    domain_keywords = {
        "Web Development": ["html", "css", "javascript", "react", "fastapi", "rest", "api", "graphql", "flask", "django", "pwa", "service worker"],
        "Full Stack Development": ["react", "node.js", "socket.io", "express", "mongodb", "websockets", "full stack", "collaboration", "media asset"],
        "Data Science": ["pandas", "numpy", "matplotlib", "seaborn", "data analysis", "eda", "jupyter", "plotly", "dash", "visualization"],
        "Data Engineering": ["airflow", "etl", "data pipeline", "data lineage", "data quality", "great expectations", "dbt", "spark", "kafka"],
        "Machine Learning": ["scikit-learn", "tensorflow", "keras", "model", "prediction", "regression", "classification", "cnn", "neural", "recommendation", "pricing"],
        "Deep Learning": ["deep learning", "neural network", "cnn", "lstm", "transformer"],
        "Artificial Intelligence": ["nlp", "sentiment", "bert", "transformer", "rag", "langchain", "llm", "granite", "chatbot", "ai"],
        "NLP": ["nlp", "sentiment", "transformer", "text", "language", "bert", "tokenization", "spacy", "nltk"],
        "Computer Vision": ["opencv", "image", "face", "recognition", "detection", "cnn", "style transfer", "biometric"],
        "Cloud Computing": ["aws", "lambda", "dynamodb", "serverless", "cloud", "s3", "cost", "terraform"],
        "DevOps": ["docker", "kubernetes", "k8s", "ci/cd", "github actions", "helm", "jenkins", "ansible", "elk", "prometheus", "grafana"],
        "Cybersecurity": ["network", "security", "vulnerability", "nmap", "wireshark", "owasp", "hacking", "password", "encryption"],
        "Databases": ["sql", "mongodb", "redis", "database", "postgresql", "elasticsearch", "dynamodb"],
        "Database": ["sql", "mongodb", "cassandra", "redis", "database", "nosql", "elasticsearch", "migration"],
        "Blockchain": ["blockchain", "solidity", "ethereum", "smart contract", "web3", "voting"],
        "IoT": ["iot", "mqtt", "arduino", "sensor", "smart home", "embedded"],
        "Mobile Development": ["flutter", "dart", "firebase", "mobile", "cross-platform"],
        "Algorithmic Trading": ["trading", "cryptocurrency", "ccxt", "ta-lib", "backtest", "algorithmic"],
        "MLOps": ["mlflow", "evidently", "model monitoring", "drift", "mlops"],
        "Architecture": ["microservices", "event-driven", "kafka", "saga", "cqrs", "event sourcing"],
        "Automation": ["scrapy", "selenium", "beautifulsoup", "scraping", "web scraping", "monitoring"],
        "Frontend Development": ["react", "vue", "angular", "javascript", "css", "html", "micro-frontend", "webpack"],
        "RAG": ["rag", "retrieval", "chromadb", "langchain", "vector", "embedding", "document qa"],
        "Generative AI": ["stable diffusion", "image generation", "generative", "prompt"],
        "UI/UX": ["figma", "wireframe", "prototype", "ui", "ux"],
    }

    for domain, keywords in domain_keywords.items():
        if any(kw in term for term in all_terms for kw in keywords):
            return domain
    return ""


# ── Endpoints ─────────────────────────────────────────────────────────


@router.get(
    "/{project_id}",
    response_model=SuccessResponse,
    summary="Get project details",
    description="Returns full project details with inferred domain and recommended courses.",
    responses={200: {"description": "Project found"}, 404: {"description": "Project not found"}},
)
async def get_project_details(project_id: str) -> SuccessResponse:
    project = _find_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")

    # Enrich with domain if missing
    if not project.get("domain"):
        project["domain"] = _determine_project_domain(project)

    # Add recommended courses
    project["recommended_courses"] = _recommend_courses_for_project(project)

    return SuccessResponse(message="Project found", data=project)


@router.get(
    "/{project_id}/resources",
    response_model=SuccessResponse,
    summary="Get project starter kit",
    description="Returns learning resources, documentation, datasets, and best practices for a project.",
    responses={200: {"description": "Resources found"}, 404: {"description": "Project not found"}},
)
async def get_project_resources(project_id: str) -> SuccessResponse:
    project = _find_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")

    resources = _load_project_resources().get(project_id, {})
    return SuccessResponse(
        message="Project resources found" if resources else "No starter kit available for this project",
        data=resources,
    )


@router.get(
    "/{project_id}/recommended-courses",
    response_model=SuccessResponse,
    summary="Get recommended courses for a project",
    description="Returns courses ranked by skill overlap with the project's required skills.",
    responses={200: {"description": "Recommendations found"}, 404: {"description": "Project not found"}},
)
async def get_recommended_courses(
    project_id: str,
    top_k: int = Query(default=5, ge=1, le=10),
) -> SuccessResponse:
    project = _find_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")

    courses = _recommend_courses_for_project(project, top_k=top_k)
    return SuccessResponse(
        message=f"Found {len(courses)} recommended courses",
        data=courses,
    )


@router.post(
    "/{project_id}/save",
    response_model=SuccessResponse,
    summary="Save a project for later",
    description="Saves a project to the student's saved list.",
    responses={200: {"description": "Project saved"}, 404: {"description": "Student or project not found"}},
)
async def save_project(
    project_id: str,
    student_id: str = Query(..., description="Student ID"),
    store: Store = Depends(get_store),
) -> SuccessResponse:
    student = get_student_or_404(student_id, store)

    project = _find_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")

    saved = store.progress.setdefault(student_id, {}).setdefault("saved_projects", [])
    if project_id not in saved:
        saved.append(project_id)

    return SuccessResponse(message=f"Project '{project.get('title', project_id)}' saved", data={"saved_projects": saved})


@router.post(
    "/{project_id}/complete",
    response_model=SuccessResponse,
    summary="Mark a project as completed",
    description="Marks a project as completed and updates the student's progress.",
    responses={200: {"description": "Project completed"}, 404: {"description": "Student or project not found"}},
)
async def complete_project(
    project_id: str,
    student_id: str = Query(..., description="Student ID"),
    store: Store = Depends(get_store),
) -> SuccessResponse:
    student = get_student_or_404(student_id, store)

    project = _find_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")

    progress = store.progress.setdefault(student_id, {})
    completed = progress.setdefault("completed_projects", [])
    if project_id not in completed:
        completed.append(project_id)

    # Add project skills to student's mastered skills if not already present
    student_profile = store.student_profiles.get(student_id, {})
    current_skills = set(student_profile.get("current_skills", []))
    new_skills = set(project.get("skills_required", []))
    if new_skills - current_skills:
        student_profile["current_skills"] = sorted(current_skills | new_skills)

    return SuccessResponse(
        message=f"Project '{project.get('title', project_id)}' marked as completed",
        data={
            "completed_projects": completed,
            "new_skills": sorted(new_skills - current_skills) if new_skills - current_skills else [],
        },
    )


@router.get(
    "/stats/{student_id}",
    response_model=SuccessResponse,
    summary="Get project stats for dashboard",
    description="Returns project-related statistics for the dashboard.",
    responses={200: {"description": "Stats returned"}},
)
async def get_project_stats(
    student_id: str,
    store: Store = Depends(get_store),
) -> SuccessResponse:
    progress = store.progress.get(student_id, {})
    completed_projects = progress.get("completed_projects", [])
    saved_projects = progress.get("saved_projects", [])

    all_projects = resource_service.get_projects()
    total = len(all_projects)

    # Find next recommended project (first not completed)
    next_project = None
    for p in all_projects:
        if p.get("id") not in completed_projects:
            next_project = p
            break

    return SuccessResponse(
        message="Project stats retrieved",
        data={
            "total_projects": total,
            "completed_count": len(completed_projects),
            "saved_count": len(saved_projects),
            "completed_projects": completed_projects,
            "saved_projects": saved_projects,
            "next_project": next_project,
            "completion_percentage": round((len(completed_projects) / total * 100) if total > 0 else 0, 1),
        },
    )
