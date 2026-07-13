"""Services package for LearnMate AI.

Exposes the IBM Granite LLM service, the ChromaDB RAG service,
the Skill Gap Analyzer, and the Roadmap Generator as importable
singletons for use throughout the application.

Optional AI dependencies (chromadb, sentence-transformers,
ibm-watsonx-ai) are imported lazily.  The application starts
successfully even when these packages are missing.
"""

from app.services.granite_service import (
    generate_response,
    generate_roadmap,
    granite_available,
    mentor_chat,
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
from app.services.prompt_templates import (
    build_roadmap_prompt,
    build_mentor_prompt,
    build_skill_analysis_prompt,
)

__all__ = [
    # Granite service
    "generate_response",
    "generate_roadmap",
    "granite_available",
    "mentor_chat",
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
    # Prompt templates
    "build_roadmap_prompt",
    "build_mentor_prompt",
    "build_skill_analysis_prompt",
]
