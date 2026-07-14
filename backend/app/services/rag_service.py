"""RAG Service for LearnMate AI.

Manages the Retrieval-Augmented Generation pipeline using ChromaDB
for vector storage and SentenceTransformer embeddings for semantic
search over courses, projects, certifications, and career pathways.

On startup the service ingests all learning resources from the JSON
datasets into a ChromaDB collection so they can be retrieved by
similarity at query time.

This module gracefully handles missing optional dependencies
(chromadb, sentence-transformers).  When the packages are not
installed the module-level ``rag_service`` singleton will be
``None`` and every public method will raise or return empty results.
"""

from __future__ import annotations

import hashlib
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("learnmate.rag")

# ---------------------------------------------------------------------------
# Optional dependency detection
# ---------------------------------------------------------------------------

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings

    _CHROMADB_AVAILABLE = True
except ImportError:
    chromadb = None  # type: ignore[assignment]
    ChromaSettings = None  # type: ignore[assignment,misc]
    _CHROMADB_AVAILABLE = False
    logger.warning(
        "[RAG] chromadb is not installed – RAG features are disabled. "
        "Install it with: pip install chromadb"
    )

try:
    from sentence_transformers import SentenceTransformer

    _SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SentenceTransformer = None  # type: ignore[assignment,misc]
    _SENTENCE_TRANSFORMERS_AVAILABLE = False
    if _CHROMADB_AVAILABLE:
        logger.warning(
            "[RAG] sentence-transformers is not installed – RAG features are disabled. "
            "Install it with: pip install sentence-transformers"
        )

RAG_AVAILABLE: bool = _CHROMADB_AVAILABLE and _SENTENCE_TRANSFORMERS_AVAILABLE

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
COLLECTION_NAME: str = "learning_resources"

# Resolve paths relative to this file for reliable dataset loading
_BACKEND_ROOT: Path = Path(__file__).resolve().parent.parent.parent.parent
_DATA_DIR: Path = _BACKEND_ROOT / "data"


# ---------------------------------------------------------------------------
# Deterministic ID helper
# ---------------------------------------------------------------------------

def _make_deterministic_id(resource_type: str, resource_id: str) -> str:
    """Create a deterministic, collision-free document ID."""
    raw = f"{resource_type}:{resource_id}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# RAG Service class
# ---------------------------------------------------------------------------


class RAGService:
    """Singleton-style RAG service managing ChromaDB and embeddings.

    When optional dependencies are missing the constructor raises
    :class:`ImportError` so callers can detect the unavailability.
    """

    def __init__(self) -> None:
        if not RAG_AVAILABLE:
            raise ImportError(
                "RAG dependencies are not installed. "
                "Install chromadb and sentence-transformers."
            )

        # Ensure the ChromaDB directory exists
        chroma_path = Path(CHROMA_DB_PATH)
        chroma_path.mkdir(parents=True, exist_ok=True)
        logger.info("[RAG] ChromaDB path: %s", chroma_path.resolve())

        self._embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        logger.info("[RAG] Embedding model loaded: %s", EMBEDDING_MODEL_NAME)

        self._chroma_client: chromadb.ClientAPI = chromadb.PersistentClient(
            path=str(chroma_path),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = self._chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        self._initialised: bool = False
        self._last_loaded: Optional[str] = None
        self._doc_counts: Dict[str, int] = {}

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    async def initialise(self) -> None:
        """Load datasets into ChromaDB if the collection is empty."""
        if self._initialised:
            return

        existing_count = self._collection.count()
        if existing_count > 0:
            logger.info(
                "[RAG] Collection '%s' already has %d documents – skipping load",
                COLLECTION_NAME,
                existing_count,
            )
            self._initialised = True
            self._last_loaded = datetime.now(timezone.utc).isoformat()
            return

        await self.reload_all()

    async def reload_all(self) -> Dict[str, int]:
        """Reload all datasets from JSON files into ChromaDB.

        Returns:
            Dict with counts per resource type and total.
        """
        logger.info("[RAG] Loading datasets...")

        from app.utils.data_loader import (
            load_courses,
            load_certifications,
            load_career_pathways,
            load_projects,
        )

        courses = load_courses()
        projects = load_projects()
        certifications = load_certifications()
        career_pathways = load_career_pathways()

        logger.info("[RAG] Loaded %d Courses", len(courses))
        logger.info("[RAG] Loaded %d Projects", len(projects))
        logger.info("[RAG] Loaded %d Certifications", len(certifications))
        logger.info("[RAG] Loaded %d Career Pathways", len(career_pathways))

        logger.info("[RAG] Creating embeddings...")
        counts = {
            "courses": self._add_documents_batch(courses, "course"),
            "projects": self._add_documents_batch(projects, "project"),
            "certifications": self._add_documents_batch(certifications, "certification"),
            "career_pathways": self._add_documents_batch(career_pathways, "career_pathway"),
        }
        total = sum(counts.values())
        counts["total"] = total

        self._doc_counts = counts
        self._last_loaded = datetime.now(timezone.utc).isoformat()
        self._initialised = True

        logger.info("[RAG] Indexed %d Documents", total)
        logger.info("[RAG] RAG Ready")

        return counts

    def _load_json(self, filename: str) -> List[Dict[str, Any]]:
        """Load and return a JSON file from the data directory."""
        path = _DATA_DIR / filename
        if not path.exists():
            logger.error("[RAG ERROR] File not found: %s", path)
            return []
        try:
            import json

            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if not isinstance(data, list):
                logger.error("[RAG ERROR] Expected array in %s, got %s", path, type(data).__name__)
                return []
            return data
        except Exception as exc:
            logger.error("[RAG ERROR] Failed to load %s: %s", path, exc)
            return []

    def _build_document(self, item: Dict[str, Any], resource_type: str) -> str:
        """Build a searchable text document from a resource dict.

        Combines key fields into a single string that the embedding model
        can encode for semantic similarity search.
        """
        parts = [f"Type: {resource_type}"]

        for field, label in [
            ("title", "Title"),
            ("name", "Name"),
            ("domain", "Domain"),
            ("description", "Description"),
            ("level", "Level"),
            ("difficulty", "Difficulty"),
            ("provider", "Provider"),
            ("duration", "Duration"),
        ]:
            if field in item and item[field]:
                parts.append(f"{label}: {item[field]}")

        for field, label in [
            ("skills_gained", "Skills gained"),
            ("skills_covered", "Skills covered"),
            ("required_skills", "Required skills"),
            ("tags", "Tags"),
            ("technologies", "Technologies"),
            ("learning_outcomes", "Learning outcomes"),
        ]:
            if field in item and item[field]:
                if isinstance(item[field], list):
                    parts.append(f"{label}: {', '.join(str(s) for s in item[field])}")
                else:
                    parts.append(f"{label}: {item[field]}")

        return " | ".join(parts)

    def _build_metadata(self, item: Dict[str, Any], resource_type: str) -> Dict[str, str]:
        """Build rich metadata for a resource for filtering."""
        meta: Dict[str, str] = {"resource_type": resource_type}

        for field in ["domain", "provider", "category"]:
            if field in item and item[field]:
                meta[field] = str(item[field])

        level = item.get("level") or item.get("difficulty") or ""
        if isinstance(level, dict):
            level = level.get("value", "")
        if level:
            meta["level"] = str(level)

        skills = item.get("skills_gained") or item.get("skills_covered") or item.get("required_skills") or []
        if isinstance(skills, list) and skills:
            meta["skills"] = ", ".join(str(s) for s in skills)

        tags = item.get("tags") or []
        if isinstance(tags, list) and tags:
            meta["tags"] = ", ".join(str(t) for t in tags)

        return meta

    def _add_documents_batch(
        self,
        items: List[Dict[str, Any]],
        resource_type: str,
    ) -> int:
        """Encode and upsert a batch of resources into ChromaDB.

        Returns:
            Number of documents successfully added.
        """
        if not items:
            return 0

        ids: List[str] = []
        documents: List[str] = []
        metadatas: List[Dict[str, str]] = []

        for item in items:
            raw_id = item.get("id") or item.get("name", "")
            if not raw_id:
                continue
            doc_id = _make_deterministic_id(resource_type, raw_id)

            document = self._build_document(item, resource_type)
            metadata = self._build_metadata(item, resource_type)

            ids.append(doc_id)
            documents.append(document)
            metadatas.append(metadata)

        if not ids:
            return 0

        try:
            embeddings = self._embedding_model.encode(documents, show_progress_bar=False).tolist()
        except Exception as exc:
            logger.error("[RAG ERROR] Embedding failed for %s: %s", resource_type, exc)
            return 0

        try:
            self._collection.upsert(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
            )
        except Exception as exc:
            logger.error("[RAG ERROR] ChromaDB upsert failed for %s: %s", resource_type, exc)
            return 0

        return len(ids)

    # ------------------------------------------------------------------
    # Public query methods
    # ------------------------------------------------------------------

    def _encode_query(self, text: str) -> List[float]:
        """Encode a text query into an embedding vector."""
        return self._embedding_model.encode(text).tolist()

    def _format_results(
        self,
        results: Dict[str, Any],
        n: int,
    ) -> List[Dict[str, Any]]:
        """Transform raw ChromaDB results into a clean list of dicts."""
        formatted: List[Dict[str, Any]] = []
        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for i in range(min(n, len(ids))):
            entry: Dict[str, Any] = {
                "id": ids[i],
                "document": documents[i] if i < len(documents) else "",
                "metadata": metadatas[i] if i < len(metadatas) else {},
            }
            if i < len(distances):
                # Cosine distance: 0 = identical, 2 = opposite
                # Convert to similarity score: 1 = identical, 0 = opposite
                entry["score"] = round(max(0.0, 1.0 - distances[i]), 4)
            else:
                entry["score"] = 0.0
            formatted.append(entry)
        return formatted

    async def search_courses(
        self,
        query: str,
        n: int = 5,
        resource_type: Optional[str] = None,
        level: Optional[str] = None,
        max_retries: int = 3,
    ) -> List[Dict[str, Any]]:
        """Search for resources matching a natural-language query.

        Includes automatic retry logic for transient failures.

        Args:
            query: Natural-language search query.
            n: Maximum number of results.
            resource_type: Optional filter by resource type (course, project, certification, career_pathway).
            level: Optional filter by difficulty level (Beginner, Intermediate, Advanced).
            max_retries: Number of retry attempts on failure.
        """
        if not query or not query.strip():
            return []

        query_embedding = self._encode_query(query)

        where_filter: Optional[Dict[str, Any]] = None
        conditions: List[Dict[str, Any]] = []

        if resource_type:
            conditions.append({"resource_type": resource_type})
        if level:
            conditions.append({"level": level})

        if len(conditions) == 1:
            where_filter = conditions[0]
        elif len(conditions) > 1:
            where_filter = {"$and": conditions}

        last_error: Optional[Exception] = None
        for attempt in range(max_retries):
            try:
                # Validate collection before querying
                doc_count = self._collection.count()
                if doc_count == 0:
                    logger.warning("[RAG] Collection is empty – search will return no results")
                    return []

                query_kwargs: Dict[str, Any] = {
                    "query_embeddings": [query_embedding],
                    "n_results": min(n, max(1, doc_count)),
                    "include": ["documents", "metadatas", "distances"],
                }
                if where_filter:
                    query_kwargs["where"] = where_filter

                results = self._collection.query(**query_kwargs)
                return self._format_results(results, n)

            except Exception as exc:
                last_error = exc
                logger.warning(
                    "[RAG] Search attempt %d/%d failed: %s",
                    attempt + 1,
                    max_retries,
                    exc,
                )
                if attempt < max_retries - 1:
                    import asyncio
                    await asyncio.sleep(0.5 * (attempt + 1))

        logger.error("[RAG ERROR] Search query failed after %d retries: %s", max_retries, last_error)
        return []

    async def search_by_skills(
        self,
        skills: List[str],
        n: int = 5,
    ) -> List[Dict[str, Any]]:
        """Search for resources that teach or cover given skills."""
        if not skills:
            return []

        query = f"Learn or improve skills: {', '.join(skills)}"
        return await self.search_courses(query, n=n)

    async def add_learning_resource(
        self,
        resource: Dict[str, Any],
        resource_type: str = "course",
    ) -> bool:
        """Add a new learning resource to the vector database."""
        raw_id = resource.get("id") or resource.get("name", "")
        if not raw_id:
            logger.warning("[RAG] Cannot add resource without an id or name")
            return False

        doc_id = _make_deterministic_id(resource_type, raw_id)
        document = self._build_document(resource, resource_type)
        metadata = self._build_metadata(resource, resource_type)
        embedding = self._encode_query(document)

        try:
            self._collection.upsert(
                ids=[doc_id],
                documents=[document],
                embeddings=[embedding],
                metadatas=[metadata],
            )
        except Exception as exc:
            logger.error("[RAG ERROR] Failed to add resource '%s': %s", doc_id, exc)
            return False

        logger.info("[RAG] Added resource '%s' to ChromaDB", doc_id)
        return True

    async def get_collection_stats(self) -> Dict[str, Any]:
        """Return statistics about the ChromaDB collection."""
        count = 0
        try:
            count = self._collection.count()
        except Exception:
            pass

        is_healthy = RAG_AVAILABLE and count > 0

        return {
            "available": RAG_AVAILABLE,
            "status": "healthy" if is_healthy else ("degraded" if RAG_AVAILABLE else "unavailable"),
            "documents": count,
            "collection": COLLECTION_NAME,
            "total_documents": count,
            "embedding_model": EMBEDDING_MODEL_NAME,
            "database": "Persistent",
            "chroma_db_path": str(Path(CHROMA_DB_PATH).resolve()),
            "last_loaded": self._last_loaded,
            "document_counts": self._doc_counts,
            "synchronized": self._initialised,
        }


# ---------------------------------------------------------------------------
# Module-level singleton (imported by main.py and other services)
# ---------------------------------------------------------------------------

rag_service: Optional[RAGService] = None

if RAG_AVAILABLE:
    try:
        rag_service = RAGService()
        logger.info("[RAG] RAG service instance created")
    except Exception as exc:
        logger.error("[RAG ERROR] Failed to create RAG service: %s", exc)
        rag_service = None
