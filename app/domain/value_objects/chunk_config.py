"""Chunk configuration value object."""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class ChunkConfig:
    """
    Immutable configuration for document chunking.

    Value object that encapsulates chunking strategy and parameters.
    """

    chunk_size: int = 512
    chunk_overlap: int = 50
    strategy: Literal["fixed", "semantic", "sentence"] = "fixed"

    def __post_init__(self):
        """Validate chunk configuration."""
        if not 100 <= self.chunk_size <= 4000:
            raise ValueError("chunk_size must be between 100 and 4000")

        if not 0 <= self.chunk_overlap <= 500:
            raise ValueError("chunk_overlap must be between 0 and 500")

        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")

        if self.strategy not in ("fixed", "semantic", "sentence"):
            raise ValueError(f"Invalid strategy: {self.strategy}")

    def is_fixed_strategy(self) -> bool:
        """Check if using fixed chunking strategy."""
        return self.strategy == "fixed"

    def is_semantic_strategy(self) -> bool:
        """Check if using semantic chunking strategy."""
        return self.strategy == "semantic"

    def is_sentence_strategy(self) -> bool:
        """Check if using sentence-based chunking strategy."""
        return self.strategy == "sentence"

    @classmethod
    def default(cls) -> "ChunkConfig":
        """Create default chunk configuration."""
        return cls()

    @classmethod
    def for_small_documents(cls) -> "ChunkConfig":
        """Create config optimized for small documents."""
        return cls(chunk_size=256, chunk_overlap=25)

    @classmethod
    def for_large_documents(cls) -> "ChunkConfig":
        """Create config optimized for large documents."""
        return cls(chunk_size=1024, chunk_overlap=100)
