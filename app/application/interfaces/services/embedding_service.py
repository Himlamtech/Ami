"""Embedding service interface."""

from abc import ABC, abstractmethod
from typing import List


class IEmbeddingService(ABC):
    """
    Interface for text embedding providers.

    Renamed from IEmbeddingProvider for consistency.
    """

    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (list of floats)
        """
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batched for efficiency).

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        pass

    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this model.

        Returns:
            Embedding dimension (e.g., 768, 1024, 1536)
        """
        pass
