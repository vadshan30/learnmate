"""Services package for LearnMate AI.

Exposes the Google Gemini AI service, the ChromaDB RAG service,
the Skill Gap Analyzer, the Roadmap Generator, and the AI Mentor
Service as importable singletons for use throughout the application.

Optional AI dependencies (chromadb, sentence-transformers,
google-genai) are imported lazily. The application starts
successfully even when these packages are missing.
"""

from app.services.gemini_service import (
    generate_response,
    generate_roadmap,
    gemini_available,
)
from app.services.rag_service import rag_service, RAG_AVAILABLE
from app.services.skill_analyzer import (
    SkillGapAnalyzer,
    SkillAnalysisResult,
    analyze_skill_gap,
    categorize_skill,
)
from app.services.roadmap_generator import (
    RoadmapGenerator,
    generate_roadmap as generate_personalised_roadmap,
    update_roadmap,
)
from app.services import mentor_service

__all__ = [
    # Gemini service
    "generate_response",
    "generate_roadmap",
    "gemini_available",
    # RAG service
    "rag_service",
    "RAG_AVAILABLE",
    # Skill analyzer
    "SkillGapAnalyzer",
    "SkillAnalysisResult",
    "analyze_skill_gap",
    "categorize_skill",
    # Roadmap generator
    "RoadmapGenerator",
    "generate_personalised_roadmap",
    "update_roadmap",
    # Mentor service
    "mentor_service",
]
