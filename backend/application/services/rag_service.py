"""
RAG Service Implementation.
Unified facade for RAG operations: indexing, search, and context building.
"""

import logging
import uuid
from typing import List, Optional
from datetime import datetime

from domain.value_objects.rag_models import (
    TextChunk,
    ChunkMetadata,
    SearchResult,
    RAGContext,
    RAGSearchConfig,
    ChunkingConfig,
    ChunkingStrategy,
    SearchType,
)
from application.interfaces.services.rag_service import (
    IRAGService,
    IndexDocumentInput,
    IndexDocumentOutput,
)
from application.interfaces.services.embedding_service import IEmbeddingService
from application.interfaces.services.vector_store_service import IVectorStoreService

logger = logging.getLogger(__name__)


class RAGService(IRAGService):
    """
    Unified RAG Service implementation.

    Combines:
    - Text chunking
    - Embedding generation
    - Vector storage/search
    - Context building
    """

    def __init__(
        self,
        embedding_service: IEmbeddingService,
        vector_store: IVectorStoreService,
        default_chunking: Optional[ChunkingConfig] = None,
        default_search: Optional[RAGSearchConfig] = None,
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.default_chunking = default_chunking or ChunkingConfig()
        self.default_search = default_search or RAGSearchConfig()

        logger.info("RAGService initialized")

    # =============================================
    # INDEXING
    # =============================================

    async def index_document(
        self,
        input_data: IndexDocumentInput,
    ) -> IndexDocumentOutput:
        """Index a document: chunk → embed → store."""
        config = input_data.chunking_config or self.default_chunking

        # 1. Chunk the document
        chunks = self._chunk_text(
            text=input_data.content,
            source_id=input_data.source_id,
            source_title=input_data.source_title,
            source_url=input_data.source_url,
            source_type=input_data.source_type,
            category=input_data.category,
            tags=input_data.tags or [],
            config=config,
        )

        if not chunks:
            logger.warning(f"No chunks created for document {input_data.source_id}")
            return IndexDocumentOutput(
                source_id=input_data.source_id,
                chunks_created=0,
                chunk_ids=[],
                collection=input_data.collection,
            )

        # 2. Index chunks
        chunk_ids = await self.index_chunks(chunks, input_data.collection)

        logger.info(
            f"Indexed document {input_data.source_id}: "
            f"{len(chunk_ids)} chunks in '{input_data.collection}'"
        )

        return IndexDocumentOutput(
            source_id=input_data.source_id,
            chunks_created=len(chunk_ids),
            chunk_ids=chunk_ids,
            collection=input_data.collection,
        )

    async def index_chunks(
        self,
        chunks: List[TextChunk],
        collection: str = "default",
    ) -> List[str]:
        """Index pre-chunked text: embed → store."""
        if not chunks:
            return []

        # 1. Generate embeddings
        texts = [chunk.content for chunk in chunks]
        embeddings = await self.embedding_service.embed_batch(texts)

        # 2. Prepare documents for vector store
        documents = []
        for chunk in chunks:
            documents.append(
                {
                    "content": chunk.content,
                    "metadata": chunk.metadata.to_dict() if chunk.metadata else {},
                }
            )

        # 3. Store in vector database
        chunk_ids = await self.vector_store.add_documents(
            documents=documents,
            embeddings=embeddings,
            collection=collection,
        )

        logger.debug(f"Indexed {len(chunk_ids)} chunks to '{collection}'")
        return chunk_ids

    async def delete_document(
        self,
        source_id: str,
        collection: str = "default",
    ) -> int:
        """Delete all chunks for a document."""
        try:
            # Delete by source_id filter
            success = self.vector_store.delete_by_filter(
                metadata_filter={"source_id": source_id},
                collection=collection,
            )

            if success:
                logger.info(f"Deleted chunks for document {source_id}")
                return 1  # We don't know exact count
            return 0

        except Exception as e:
            logger.error(f"Failed to delete document {source_id}: {e}")
            return 0

    # =============================================
    # SEARCH
    # =============================================

    async def search(
        self,
        query: str,
        config: Optional[RAGSearchConfig] = None,
    ) -> List[SearchResult]:
        """Search for relevant chunks."""
        cfg = config or self.default_search

        # 1. Embed query
        query_embedding = await self.embedding_service.embed_text(query)

        # 2. Search
        return await self.search_with_embedding(query_embedding, cfg)

    async def search_with_embedding(
        self,
        query_embedding: List[float],
        config: Optional[RAGSearchConfig] = None,
    ) -> List[SearchResult]:
        """Search with pre-computed embedding."""
        cfg = config or self.default_search

        # Perform vector search
        raw_results = await self.vector_store.search(
            query_embedding=query_embedding,
            top_k=(
                cfg.top_k * 2 if cfg.deduplicate else cfg.top_k
            ),  # Get extra for dedup
            collection=cfg.collection,
            score_threshold=cfg.score_threshold,
            metadata_filter=cfg.metadata_filter,
        )

        # Convert to SearchResult objects
        results = [
            SearchResult(
                id=r["id"],
                content=r.get("content", ""),
                score=r.get("score", 0.0),
                metadata=r.get("metadata", {}),
            )
            for r in raw_results
        ]

        # Apply post-processing
        if cfg.deduplicate:
            results = self._deduplicate_results(results)

        if cfg.search_type == SearchType.MMR:
            results = self._apply_mmr(results, query_embedding, cfg.mmr_diversity)

        # Limit to top_k
        results = results[: cfg.top_k]

        logger.debug(f"Search returned {len(results)} results")
        return results

    # =============================================
    # CONTEXT BUILDING
    # =============================================

    async def build_context(
        self,
        query: str,
        config: Optional[RAGSearchConfig] = None,
    ) -> RAGContext:
        """Build RAG context for LLM."""
        results = await self.search(query, config)

        context = RAGContext(
            query=query,
            results=results,
        )

        logger.debug(
            f"Built context: {context.total_results} results, "
            f"avg_score={context.avg_score:.3f}, "
            f"{context.unique_sources} unique sources"
        )

        return context

    # =============================================
    # UTILITIES
    # =============================================

    async def embed_text(self, text: str) -> List[float]:
        """Get embedding for text."""
        return await self.embedding_service.embed_text(text)

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for batch of texts."""
        return await self.embedding_service.embed_batch(texts)

    def chunk_text(
        self,
        text: str,
        config: Optional[ChunkingConfig] = None,
    ) -> List[TextChunk]:
        """Chunk text without indexing."""
        cfg = config or self.default_chunking
        return self._chunk_text(
            text=text,
            source_id=str(uuid.uuid4()),
            config=cfg,
        )

    def get_embedding_dimension(self) -> int:
        """Get embedding vector dimension."""
        return self.embedding_service.get_embedding_dimension()

    # =============================================
    # PRIVATE METHODS
    # =============================================

    def _chunk_text(
        self,
        text: str,
        source_id: str,
        source_title: Optional[str] = None,
        source_url: Optional[str] = None,
        source_type: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        config: Optional[ChunkingConfig] = None,
    ) -> List[TextChunk]:
        """
        Chunk text with metadata.

        Implements recursive text splitting strategy.
        """
        cfg = config or self.default_chunking

        if not text or not text.strip():
            return []

        # Split text into chunks
        if cfg.strategy == ChunkingStrategy.FIXED:
            raw_chunks = self._fixed_chunk(text, cfg.chunk_size, cfg.chunk_overlap)
        elif cfg.strategy == ChunkingStrategy.SENTENCE:
            raw_chunks = self._sentence_chunk(text, cfg.chunk_size, cfg.chunk_overlap)
        elif cfg.strategy == ChunkingStrategy.MARKDOWN:
            raw_chunks = self._markdown_chunk(text, cfg.chunk_size, cfg.chunk_overlap)
        else:
            # Default: recursive
            raw_chunks = self._recursive_chunk(text, cfg)

        # Filter small chunks
        raw_chunks = [c for c in raw_chunks if len(c.strip()) >= cfg.min_chunk_size]

        # Create TextChunk objects with metadata
        chunks = []
        total = len(raw_chunks)
        char_offset = 0

        for i, chunk_text in enumerate(raw_chunks):
            metadata = ChunkMetadata(
                source_id=source_id,
                chunk_index=i,
                total_chunks=total,
                source_url=source_url,
                source_title=source_title,
                source_type=source_type,
                start_char=char_offset,
                end_char=char_offset + len(chunk_text),
                category=category,
                tags=tags or [],
                created_at=datetime.now(),
            )

            chunks.append(
                TextChunk(
                    content=chunk_text.strip(),
                    metadata=metadata,
                )
            )

            char_offset += len(chunk_text)

        return chunks

    def _recursive_chunk(
        self,
        text: str,
        config: ChunkingConfig,
    ) -> List[str]:
        """Recursive text splitting (langchain-style)."""
        separators = list(config.separators)

        def _split_text(text: str, separators: List[str]) -> List[str]:
            if not separators:
                return [text]

            separator = separators[0]
            splits = text.split(separator)

            chunks = []
            current_chunk = ""

            for split in splits:
                if (
                    len(current_chunk) + len(split) + len(separator)
                    <= config.chunk_size
                ):
                    current_chunk += (separator if current_chunk else "") + split
                else:
                    if current_chunk:
                        chunks.append(current_chunk)

                    if len(split) > config.chunk_size:
                        # Recursively split with next separator
                        sub_chunks = _split_text(split, separators[1:])
                        chunks.extend(sub_chunks)
                        current_chunk = ""
                    else:
                        current_chunk = split

            if current_chunk:
                chunks.append(current_chunk)

            return chunks

        raw_chunks = _split_text(text, separators)

        # Apply overlap
        if config.chunk_overlap > 0:
            overlapped = []
            for i, chunk in enumerate(raw_chunks):
                if i > 0 and len(raw_chunks[i - 1]) > config.chunk_overlap:
                    # Add overlap from previous chunk
                    overlap = raw_chunks[i - 1][-config.chunk_overlap :]
                    chunk = overlap + chunk
                overlapped.append(chunk)
            raw_chunks = overlapped

        return raw_chunks

    def _fixed_chunk(
        self,
        text: str,
        chunk_size: int,
        overlap: int,
    ) -> List[str]:
        """Simple fixed-size chunking."""
        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start = end - overlap

        return chunks

    def _sentence_chunk(
        self,
        text: str,
        chunk_size: int,
        overlap: int,
    ) -> List[str]:
        """Chunk by sentences."""
        import re

        sentences = re.split(r"(?<=[.!?])\s+", text)

        chunks = []
        current = ""

        for sentence in sentences:
            if len(current) + len(sentence) <= chunk_size:
                current += " " + sentence if current else sentence
            else:
                if current:
                    chunks.append(current)
                current = sentence

        if current:
            chunks.append(current)

        return chunks

    def _markdown_chunk(
        self,
        text: str,
        chunk_size: int,
        overlap: int,
    ) -> List[str]:
        """Chunk respecting markdown headers."""
        import re

        # Split by headers
        sections = re.split(r"\n(#{1,6}\s+[^\n]+)\n", text)

        chunks = []
        current_header = ""
        current_content = ""

        for section in sections:
            if re.match(r"^#{1,6}\s+", section):
                # This is a header
                if current_content.strip():
                    chunk = (
                        f"{current_header}\n{current_content}"
                        if current_header
                        else current_content
                    )
                    if len(chunk) > chunk_size:
                        # Split large sections
                        sub_chunks = self._fixed_chunk(chunk, chunk_size, overlap)
                        chunks.extend(sub_chunks)
                    else:
                        chunks.append(chunk)
                current_header = section
                current_content = ""
            else:
                current_content += section

        # Don't forget the last section
        if current_content.strip():
            chunk = (
                f"{current_header}\n{current_content}"
                if current_header
                else current_content
            )
            if len(chunk) > chunk_size:
                sub_chunks = self._fixed_chunk(chunk, chunk_size, overlap)
                chunks.extend(sub_chunks)
            else:
                chunks.append(chunk)

        return chunks

    def _deduplicate_results(
        self,
        results: List[SearchResult],
    ) -> List[SearchResult]:
        """Remove duplicate chunks from same source."""
        seen_sources = {}
        deduped = []

        for result in results:
            source_id = result.source_id
            if source_id:
                if source_id not in seen_sources:
                    seen_sources[source_id] = 1
                    deduped.append(result)
                elif seen_sources[source_id] < 2:  # Allow max 2 chunks per source
                    seen_sources[source_id] += 1
                    deduped.append(result)
            else:
                deduped.append(result)

        return deduped

    def _apply_mmr(
        self,
        results: List[SearchResult],
        query_embedding: List[float],
        diversity: float,
    ) -> List[SearchResult]:
        """
        Apply Maximal Marginal Relevance for diversity.

        MMR = λ * sim(doc, query) - (1-λ) * max(sim(doc, selected_docs))
        """
        if not results or diversity == 0:
            return results

        # Simple implementation: just reorder based on diversity
        # Full MMR would require embeddings of all documents
        # For now, interleave results from different sources

        by_source = {}
        for r in results:
            source = r.source_id or "unknown"
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(r)

        # Round-robin from each source
        reordered = []
        while any(by_source.values()):
            for source in list(by_source.keys()):
                if by_source[source]:
                    reordered.append(by_source[source].pop(0))
                if not by_source[source]:
                    del by_source[source]

        return reordered
