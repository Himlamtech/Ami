"""
OpenAI embedding provider implementation.
Uses OpenAI's text-embedding models with batching and error handling.
"""

import asyncio
import logging
from typing import List

from openai import APIError, APITimeoutError, AsyncOpenAI, RateLimitError

from app.core.interfaces import IEmbeddingProvider

logger = logging.getLogger(__name__)


class OpenAIEmbeddings(IEmbeddingProvider):
    """OpenAI embedding provider with batch optimization and retry logic."""

    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        batch_size: int = 2048,
        max_retries: int = 3,
    ):
        self.client = AsyncOpenAI(
            api_key=api_key, max_retries=max_retries, timeout=60.0
        )
        self.model = model
        self.batch_size = batch_size
        self.dimension = 1536 if "3-small" in model else 3072  # For validation
        logger.info(
            f"Initialized OpenAIEmbeddings with model: {model}, dimension: {self.dimension}"
        )

    async def embed_text(self, text: str) -> List[float]:
        """
        Embed single text with error handling.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        try:
            if not text or not text.strip():
                logger.warning(
                    "Empty text provided for embedding, returning zero vector"
                )
                return [0.0] * self.dimension

            response = await self.client.embeddings.create(input=text, model=self.model)

            embedding = response.data[0].embedding

            # Validate dimension
            if len(embedding) != self.dimension:
                logger.warning(
                    f"Unexpected embedding dimension: {len(embedding)} vs {self.dimension}"
                )

            logger.debug(
                f"Embedded text ({len(text)} chars) -> {len(embedding)}D vector"
            )
            return embedding

        except RateLimitError as e:
            logger.error(f"OpenAI embedding rate limit: {e}")
            await asyncio.sleep(2)  # Wait before retry
            raise RuntimeError("Rate limit exceeded for embeddings")
        except APITimeoutError as e:
            logger.error(f"OpenAI embedding timeout: {e}")
            raise RuntimeError("Embedding request timeout")
        except APIError as e:
            logger.error(f"OpenAI embedding API error: {e}")
            raise RuntimeError(f"Embedding API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in embed_text: {e}")
            raise RuntimeError(f"Failed to embed text: {str(e)}")

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Embed batch of texts with chunking for large batches.
        OpenAI limit is 2048 inputs per request.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        # Filter out empty texts but remember their positions
        text_indices = [
            (i, text) for i, text in enumerate(texts) if text and text.strip()
        ]
        filtered_texts = [text for _, text in text_indices]

        if not filtered_texts:
            logger.warning("All texts are empty, returning zero vectors")
            return [[0.0] * self.dimension] * len(texts)

        try:
            all_embeddings = []

            # Process in chunks of batch_size
            for i in range(0, len(filtered_texts), self.batch_size):
                chunk = filtered_texts[i : i + self.batch_size]
                logger.debug(
                    f"Processing embedding batch {i // self.batch_size + 1}: {len(chunk)} texts"
                )

                try:
                    response = await self.client.embeddings.create(
                        input=chunk, model=self.model
                    )

                    chunk_embeddings = [item.embedding for item in response.data]
                    all_embeddings.extend(chunk_embeddings)

                except RateLimitError as e:
                    logger.warning(
                        f"Rate limit in batch {i // self.batch_size + 1}, retrying after delay"
                    )
                    await asyncio.sleep(5)
                    # Retry this chunk
                    response = await self.client.embeddings.create(
                        input=chunk, model=self.model
                    )
                    chunk_embeddings = [item.embedding for item in response.data]
                    all_embeddings.extend(chunk_embeddings)

            # Reconstruct full list with zero vectors for empty texts
            result = []
            embedding_idx = 0
            for i in range(len(texts)):
                if i in [idx for idx, _ in text_indices]:
                    result.append(all_embeddings[embedding_idx])
                    embedding_idx += 1
                else:
                    result.append([0.0] * self.dimension)

            logger.info(f"Successfully embedded batch of {len(texts)} texts")
            return result

        except Exception as e:
            logger.error(f"Failed to embed batch: {e}")
            raise RuntimeError(f"Batch embedding failed: {str(e)}")
