"""
RAG (Retrieval-Augmented Generation) Domain Models.
Core value objects and entities for the RAG pipeline.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class ChunkingStrategy(str, Enum):
    """Strategy for splitting text into chunks."""

    FIXED = "fixed"  # Fixed character size
    SEMANTIC = "semantic"  # Split by semantic units (paragraphs)
    SENTENCE = "sentence"  # Split by sentences
    RECURSIVE = "recursive"  # Recursive splitting (langchain-style)
    MARKDOWN = "markdown"  # Respect markdown headers


class SearchType(str, Enum):
    """Type of vector search."""

    SIMILARITY = "similarity"  # Basic cosine similarity
    MMR = "mmr"  # Maximal Marginal Relevance (diversity)
    HYBRID = "hybrid"  # Vector + keyword search


@dataclass(frozen=True)
class ChunkMetadata:
    """Metadata for a text chunk."""

    source_id: str  # Document ID this chunk belongs to
    chunk_index: int  # Position in original document
    total_chunks: int  # Total chunks from this document

    # Source info
    source_url: Optional[str] = None
    source_title: Optional[str] = None
    source_type: Optional[str] = None  # pdf, web, markdown, etc.

    # Location in original
    start_char: Optional[int] = None
    end_char: Optional[int] = None

    # Additional metadata
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "source_id": self.source_id,
            "chunk_index": self.chunk_index,
            "total_chunks": self.total_chunks,
            "source_url": self.source_url,
            "source_title": self.source_title,
            "source_type": self.source_type,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "category": self.category,
            "tags": list(self.tags) if self.tags else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChunkMetadata":
        """Create from dictionary."""
        created_at = None
        if data.get("created_at"):
            created_at = datetime.fromisoformat(data["created_at"])

        return cls(
            source_id=data.get("source_id", ""),
            chunk_index=data.get("chunk_index", 0),
            total_chunks=data.get("total_chunks", 1),
            source_url=data.get("source_url"),
            source_title=data.get("source_title"),
            source_type=data.get("source_type"),
            start_char=data.get("start_char"),
            end_char=data.get("end_char"),
            category=data.get("category"),
            tags=data.get("tags", []),
            created_at=created_at,
        )


@dataclass
class TextChunk:
    """A chunk of text ready for embedding."""

    id: Optional[str] = None  # Vector store point ID
    content: str = ""  # The text content
    metadata: Optional[ChunkMetadata] = None
    embedding: Optional[List[float]] = None

    @property
    def char_count(self) -> int:
        return len(self.content)

    @property
    def word_count(self) -> int:
        return len(self.content.split())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for vector store."""
        return {
            "content": self.content,
            "metadata": self.metadata.to_dict() if self.metadata else {},
        }


@dataclass
class SearchResult:
    """Result from vector search."""

    id: str
    content: str
    score: float  # Similarity score (0-1 for cosine)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Convenience accessors
    @property
    def source_title(self) -> str:
        return self.metadata.get("source_title", "Unknown")

    @property
    def source_url(self) -> Optional[str]:
        return self.metadata.get("source_url")

    @property
    def source_id(self) -> str:
        return self.metadata.get("source_id", "")

    def is_relevant(self, threshold: float = 0.5) -> bool:
        """Check if result is above relevance threshold."""
        return self.score >= threshold


@dataclass(frozen=True)
class RAGSearchConfig:
    """Configuration for RAG search operation."""

    # Basic search params
    top_k: int = 5
    score_threshold: float = 0.0  # Minimum score (0 = no filtering)

    # Search type
    search_type: SearchType = SearchType.SIMILARITY
    mmr_diversity: float = 0.5  # For MMR: 0=max relevance, 1=max diversity

    # Filtering
    collection: str = "default"
    metadata_filter: Optional[Dict[str, Any]] = None

    # Post-processing
    rerank: bool = False
    rerank_model: Optional[str] = None
    deduplicate: bool = True  # Remove similar chunks from same source

    def __post_init__(self):
        if not 1 <= self.top_k <= 100:
            raise ValueError("top_k must be between 1 and 100")
        if not 0.0 <= self.score_threshold <= 1.0:
            raise ValueError("score_threshold must be between 0.0 and 1.0")
        if not 0.0 <= self.mmr_diversity <= 1.0:
            raise ValueError("mmr_diversity must be between 0.0 and 1.0")


@dataclass(frozen=True)
class ChunkingConfig:
    """Configuration for text chunking."""

    strategy: ChunkingStrategy = ChunkingStrategy.RECURSIVE
    chunk_size: int = 1000  # Target chunk size in characters
    chunk_overlap: int = 200  # Overlap between chunks

    # Strategy-specific options
    separators: List[str] = field(default_factory=lambda: ["\n\n", "\n", ". ", " "])
    min_chunk_size: int = 100  # Minimum chunk size
    respect_sentence_boundary: bool = True

    def __post_init__(self):
        if self.chunk_size < self.min_chunk_size:
            raise ValueError("chunk_size must be >= min_chunk_size")
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be < chunk_size")


@dataclass
class RAGContext:
    """Context built from RAG search for LLM."""

    query: str
    results: List[SearchResult]

    # Aggregated info
    total_results: int = 0
    avg_score: float = 0.0
    unique_sources: int = 0

    def __post_init__(self):
        self.total_results = len(self.results)
        if self.results:
            self.avg_score = sum(r.score for r in self.results) / len(self.results)
            self.unique_sources = len(set(r.source_id for r in self.results))

    def build_context_string(self, max_length: int = 4000) -> str:
        """Build context string for LLM prompt."""
        if not self.results:
            return ""

        parts = []
        current_length = 0

        for i, result in enumerate(self.results, 1):
            source_info = (
                f"[{result.source_title}]" if result.source_title else f"[Source {i}]"
            )
            chunk = f"{source_info}\n{result.content}\n"

            if current_length + len(chunk) > max_length:
                break

            parts.append(chunk)
            current_length += len(chunk)

        return "\n".join(parts)

    def has_relevant_results(self, threshold: float = 0.5) -> bool:
        """Check if any results are above threshold."""
        return any(r.is_relevant(threshold) for r in self.results)

    def get_source_references(self) -> List[Dict[str, Any]]:
        """Get unique source references for citation."""
        seen = set()
        refs = []

        for result in self.results:
            source_id = result.source_id
            if source_id and source_id not in seen:
                seen.add(source_id)
                refs.append(
                    {
                        "id": source_id,
                        "title": result.source_title,
                        "url": result.source_url,
                        "score": result.score,
                    }
                )

        return refs
