"""
HuggingFace embedding provider implementation.
Uses sentence-transformers models with local caching and batch processing.
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional

import torch
from sentence_transformers import SentenceTransformer

from app.config import embedding_config
from app.config.ai import EmbeddingConfig
from app.application.interfaces.services.embedding_service import IEmbeddingService

logger = logging.getLogger(__name__)


class HuggingFaceEmbeddings(IEmbeddingService):
    """HuggingFace embedding provider using sentence-transformers with async wrapper."""

    def __init__(
        self,
        config: EmbeddingConfig = None,
        batch_size: int = 32,
        device: Optional[torch.device] = None,
    ):
        """
        Initialize HuggingFace embeddings.

        Args:
            config: Embedding configuration. If None, uses global embedding_config.
            batch_size: Batch size for encoding
            device: Device to run model on. If None, auto-detect.
        """
        self.config = config or embedding_config
        model_name = self.config.model

        if device is None:
            device = torch.device(self.config.device)

        logger.info(f"Loading HuggingFace model: {model_name}")
        # Load model with trust_remote_code for custom models
        self.model = SentenceTransformer(
            model_name, device=device.type, trust_remote_code=True
        )
        self.model_name = model_name
        self.batch_size = batch_size
        self.dimension = self.model.get_sentence_embedding_dimension()
        self._executor = ThreadPoolExecutor(max_workers=1)  # For async wrapper
        logger.info(
            f"Loaded {model_name}, dimension: {self.dimension}, device: {device.type}"
        )

    async def embed_text(self, text: str) -> List[float]:
        """
        Embed single text using async wrapper around sync model.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        try:
            if not text or not text.strip():
                logger.warning("Empty text for embedding, returning zero vector")
                return [0.0] * self.dimension

            # Run in thread pool to avoid blocking event loop
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                self._executor, lambda: self.model.encode(text, convert_to_numpy=True)
            )

            result = embedding.tolist()
            logger.debug(f"Embedded text ({len(text)} chars) -> {len(result)}D vector")
            return result

        except Exception as e:
            logger.error(f"HuggingFace embedding error: {e}")
            raise RuntimeError(f"Failed to embed text: {str(e)}")

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Embed batch of texts efficiently.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        try:
            # Filter empty texts but remember positions
            text_indices = [
                (i, text) for i, text in enumerate(texts) if text and text.strip()
            ]
            filtered_texts = [text for _, text in text_indices]

            if not filtered_texts:
                logger.warning("All texts empty, returning zero vectors")
                return [[0.0] * self.dimension] * len(texts)

            logger.debug(f"Embedding batch of {len(filtered_texts)} texts")

            # Run in thread pool
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                self._executor,
                lambda: self.model.encode(
                    filtered_texts,
                    batch_size=self.batch_size,
                    show_progress_bar=False,
                    convert_to_numpy=True,
                ),
            )

            # Convert to list
            embeddings_list = embeddings.tolist()

            # Reconstruct with zero vectors for empty texts
            result = []
            embedding_idx = 0
            for i in range(len(texts)):
                if i in [idx for idx, _ in text_indices]:
                    result.append(embeddings_list[embedding_idx])
                    embedding_idx += 1
                else:
                    result.append([0.0] * self.dimension)

            logger.info(f"Successfully embedded batch of {len(texts)} texts")
            return result

        except Exception as e:
            logger.error(f"HuggingFace batch embedding error: {e}")
            raise RuntimeError(f"Batch embedding failed: {str(e)}")

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.

        Returns:
            Dimension as integer
        """
        return self.dimension

    def __del__(self):
        """Cleanup thread pool on deletion."""
        if hasattr(self, "_executor"):
            self._executor.shutdown(wait=False)


if __name__ == "__main__":
    # Simple test
    async def test():
        embedder = HuggingFaceEmbeddings()
        print(f"Embedding Model: {embedder.model_name}")
        print(f"Embedding Device: {embedder.model.device}")
        texts = [
            "Hello, world!",
            "This is a test sentence.",
            "",
            "Another text to embed.",
        ]
        embeddings = await embedder.embed_batch(texts)
        for i, emb in enumerate(embeddings):
            print(f"Text {i}: {texts[i]} -> Embedding length: {len(emb)}")

    asyncio.run(test())