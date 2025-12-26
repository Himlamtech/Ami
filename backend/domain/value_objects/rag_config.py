"""RAG configuration value object."""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass(frozen=True)
class RAGConfig:
    """
    Immutable configuration for RAG retrieval.

    Value object that encapsulates RAG search parameters.
    """

    enabled: bool = True
    top_k: int = 5
    similarity_threshold: float = 0.0
    rerank: bool = False
    include_sources: bool = True
    metadata_filter: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate RAG configuration."""
        if not 1 <= self.top_k <= 50:
            raise ValueError("top_k must be between 1 and 50")

        if not 0.0 <= self.similarity_threshold <= 1.0:
            raise ValueError("similarity_threshold must be between 0.0 and 1.0")

    def is_strict_matching(self) -> bool:
        """Check if using strict similarity matching."""
        return self.similarity_threshold > 0.7

    def has_metadata_filter(self) -> bool:
        """Check if metadata filtering is enabled."""
        return self.metadata_filter is not None and len(self.metadata_filter) > 0

    @classmethod
    def disabled(cls) -> "RAGConfig":
        """Create disabled RAG config."""
        return cls(enabled=False)

    @classmethod
    def strict(cls) -> "RAGConfig":
        """Create strict matching config."""
        return cls(
            enabled=True,
            top_k=3,
            similarity_threshold=0.75,
            rerank=True,
            include_sources=True,
        )

    @classmethod
    def relaxed(cls) -> "RAGConfig":
        """Create relaxed matching config."""
        return cls(
            enabled=True,
            top_k=10,
            similarity_threshold=0.3,
            rerank=False,
            include_sources=True,
        )
