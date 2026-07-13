"""RAG Service for LearnMate AI.

Manages the Retrieval-Augmented Generation pipeline using ChromaDB
for vector storage and SentenceTransformer embeddings for semantic
search over courses, projects, and certifications.

On startup the service ingests all learning resources from the JSON
datasets into a ChromaDB collection so they can be retrieved by
similarity at query time.

This module gracefully handles missing optional dependencies
(chromadb, sentence-transformers).  When the packages are not
installed the module-level ``rag_service`` singleton will be
``None`` and every public method will raise or return empty results.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

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
        "chromadb is not installed – RAG features are disabled. "
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
            "sentence-transformers is not installed – RAG features are disabled. "
            "Install it with: pip install sentence-transformers"
        )

RAG_AVAILABLE: bool = _CHROMADB_AVAILABLE and _SENTENCE_TRANSFORMERS_AVAILABLE

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
EMBEDDING_MODEL_NAME: str = os.getenv(
    "EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2"
)
COLLECTION_NAME: str = "learning_resources"

# Resolve the backend data directory relative to this file's location
_BACKEND_ROOT: Path = Path(__file__).resolve().parent.parent.parent.parent
_DATA_DIR: Path = _BACKEND_ROOT / "data"


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

        self._embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        self._chroma_client: chromadb.ClientAPI = chromadb.PersistentClient(
            path=CHROMA_DB_PATH,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = self._chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        self._initialised: bool = False

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    async def initialise(self) -> None:
        """Load datasets into ChromaDB if the collection is empty."""
        if self._initialised:
            return

        if self._collection.count() > 0:
            logger.info(
                "Collection '%s' already has %d documents – skipping load",
                COLLECTION_NAME,
                self._collection.count(),
            )
            self._initialised = True
            return

        loaded = 0
        loaded += self._load_courses()
        loaded += self._load_projects()
        loaded += self._load_certifications()

        self._initialised = True
        logger.info("RAG service initialised – %d resources indexed", loaded)

    def _load_json(self, filename: str) -> List[Dict[str, Any]]:
        """Load and return a JSON file from the data directory."""
        path = _DATA_DIR / filename
        if not path.exists():
            logger.warning("Dataset file not found: %s", path)
            return []
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)

    def _build_document(self, item: Dict[str, Any], resource_type: str) -> str:
        """Build a searchable text document from a resource dict.

        Combines key fields into a single string that the embedding model
        can encode for semantic similarity search.
        """
        parts = [f"Type: {resource_type}"]

        if "title" in item:
            parts.append(f"Title: {item['title']}")
        if "name" in item:
            parts.append(f"Name: {item['name']}")
        if "domain" in item:
            parts.append(f"Domain: {item['domain']}")
        if "description" in item:
            parts.append(f"Description: {item['description']}")
        if "level" in item:
            parts.append(f"Level: {item['level']}")
        if "skills_gained" in item:
            parts.append(f"Skills gained: {', '.join(item['skills_gained'])}")
        if "skills_covered" in item:
            parts.append(f"Skills covered: {', '.join(item['skills_covered'])}")
        if "tags" in item:
            parts.append(f"Tags: {', '.join(item['tags'])}")
        if "technologies" in item:
            parts.append(f"Technologies: {', '.join(item['technologies'])}")
        if "provider" in item:
            parts.append(f"Provider: {item['provider']}")
        if "difficulty" in item:
            parts.append(f"Difficulty: {item['difficulty']}")
        if "learning_outcomes" in item:
            parts.append(
                f"Learning outcomes: {', '.join(item['learning_outcomes'])}"
            )

        return " | ".join(parts)

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
            doc_id = item.get("id") or item.get("name", "")
            if not doc_id:
                continue
            doc_id = f"{resource_type}:{doc_id}"

            document = self._build_document(item, resource_type)
            ids.append(doc_id)
            documents.append(document)
            metadatas.append({"resource_type": resource_type})

        if not ids:
            return 0

        embeddings = self._embedding_model.encode(documents).tolist()

        self._collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        return len(ids)

    def _load_courses(self) -> int:
        """Load courses from courses.json into ChromaDB."""
        items = self._load_json("courses.json")
        count = self._add_documents_batch(items, "course")
        logger.info("Loaded %d courses into ChromaDB", count)
        return count

    def _load_projects(self) -> int:
        """Load projects from projects.json into ChromaDB."""
        items = self._load_json("projects.json")
        count = self._add_documents_batch(items, "project")
        logger.info("Loaded %d projects into ChromaDB", count)
        return count

    def _load_certifications(self) -> int:
        """Load certifications from certifications.json into ChromaDB."""
        items = self._load_json("certifications.json")
        count = self._add_documents_batch(items, "certification")
        logger.info("Loaded %d certifications into ChromaDB", count)
        return count

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
            formatted.append({
                "id": ids[i],
                "document": documents[i] if i < len(documents) else "",
                "metadata": metadatas[i] if i < len(metadatas) else {},
                "score": round(1.0 - distances[i], 4)
                if i < len(distances)
                else 0.0,
            })
        return formatted

    async def search_courses(
        self,
        query: str,
        n: int = 5,
    ) -> List[Dict[str, Any]]:
        """Search for courses matching a natural-language query."""
        if not query.strip():
            return []

        query_embedding = self._encode_query(query)
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=n,
            include=["documents", "metadatas", "distances"],
        )
        return self._format_results(results, n)

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
        doc_id = resource.get("id") or resource.get("name", "")
        if not doc_id:
            logger.warning("Cannot add resource without an id or name")
            return False

        doc_id = f"{resource_type}:{doc_id}"
        document = self._build_document(resource, resource_type)
        embedding = self._encode_query(document)

        self._collection.upsert(
            ids=[doc_id],
            documents=[document],
            embeddings=[embedding],
            metadatas=[{"resource_type": resource_type}],
        )
        logger.info("Added resource '%s' to ChromaDB", doc_id)
        return True

    async def get_collection_stats(self) -> Dict[str, Any]:
        """Return statistics about the ChromaDB collection."""
        return {
            "collection": COLLECTION_NAME,
            "total_documents": self._collection.count(),
            "embedding_model": EMBEDDING_MODEL_NAME,
            "chroma_db_path": CHROMA_DB_PATH,
        }


# ---------------------------------------------------------------------------
# Module-level singleton (imported by main.py and other services)
# ---------------------------------------------------------------------------

rag_service: Optional[RAGService] = None

if RAG_AVAILABLE:
    try:
        rag_service = RAGService()
    except Exception as exc:
        logger.error("Failed to initialise RAG service: %s", exc)
        rag_service = None
