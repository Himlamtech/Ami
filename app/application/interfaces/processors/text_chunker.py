"""Text chunker interface."""

from abc import ABC, abstractmethod
from typing import List


class ITextChunker(ABC):
    """
    Interface for text chunking strategies.

    Splits text into chunks for embedding.
    """

    @abstractmethod
    def chunk_text(
        self,
        text: str,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        strategy: str = "fixed",
    ) -> List[str]:
        """
        Chunk text into smaller pieces.

        Args:
            text: Text to chunk
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks
            strategy: Chunking strategy ("fixed", "semantic", "sentence")

        Returns:
            List of text chunks
        """
        pass

    @abstractmethod
    def estimate_chunks(self, text: str, chunk_size: int) -> int:
        """
        Estimate number of chunks.

        Args:
            text: Text to estimate
            chunk_size: Chunk size

        Returns:
            Estimated chunk count
        """
        pass
