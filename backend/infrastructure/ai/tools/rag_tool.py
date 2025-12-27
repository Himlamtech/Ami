"""
RAG Tool Handler - Uses retrieved documents to answer questions.
"""

import logging
from typing import Dict, Any, List, Optional

from app.domain.enums.tool_type import ToolType
from app.application.interfaces.services.tool_executor_service import IToolHandler
from app.application.interfaces.services.llm_service import ILLMService


logger = logging.getLogger(__name__)


class RAGToolHandler(IToolHandler):
    """
    Handler for use_rag_context tool.

    Uses retrieved chunks from vector search to generate answers.
    """

    def __init__(
        self,
        llm_service: ILLMService,
        chunk_store: Optional[Any] = None,  # For fetching chunk content
    ):
        """
        Initialize RAG tool handler.

        Args:
            llm_service: LLM service for generation
            chunk_store: Store to fetch chunk content by ID (optional)
        """
        self._llm = llm_service
        self._chunk_store = chunk_store

    @property
    def tool_type(self) -> ToolType:
        return ToolType.USE_RAG_CONTEXT

    def validate_arguments(self, arguments: Dict[str, Any]) -> bool:
        """Validate tool arguments."""
        required = ["chunk_ids", "confidence", "reason"]
        return all(key in arguments for key in required)

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute RAG tool.

        Args:
            arguments:
                - chunk_ids: List of chunk IDs to use
                - confidence: Confidence level (high/medium/low)
                - reason: Why RAG is being used
                - query: Original query (injected by orchestrator)
                - chunk_contents: Chunk contents (optional, pre-fetched)

        Returns:
            {
                "answer": str,
                "sources": List[Dict],
                "confidence": str
            }
        """
        chunk_ids = arguments.get("chunk_ids", [])
        confidence = arguments.get("confidence", "medium")
        query = arguments.get("query", "")
        chunk_contents = arguments.get("chunk_contents", [])

        logger.info(
            f"RAG tool executing with {len(chunk_ids)} chunks, confidence={confidence}"
        )

        # Get chunk contents if not provided
        if not chunk_contents and self._chunk_store:
            chunk_contents = await self._fetch_chunks(chunk_ids)

        if not chunk_contents:
            return {
                "answer": "Không tìm thấy thông tin liên quan trong cơ sở dữ liệu.",
                "sources": [],
                "confidence": "low",
            }

        # Build context from chunks
        context = self._build_context(chunk_contents)

        # Generate answer using LLM
        prompt = f"""Based on the following context, answer the user's question.

**Context:**
{context}

**Question:** {query}

**Instructions:**
1. Only use information from the provided context
2. If context doesn't contain the answer, say so
3. Cite sources when possible
4. Be concise and helpful

**Answer:**"""

        answer = await self._llm.generate(prompt=prompt)

        # Extract sources
        sources = self._extract_sources(chunk_contents)

        return {"answer": answer, "sources": sources, "confidence": confidence}

    async def _fetch_chunks(self, chunk_ids: List[str]) -> List[Dict[str, Any]]:
        """Fetch chunk contents from store."""
        if not self._chunk_store:
            return []

        chunks = []
        for chunk_id in chunk_ids:
            try:
                chunk = await self._chunk_store.get(chunk_id)
                if chunk:
                    chunks.append(chunk)
            except Exception as e:
                logger.warning(f"Failed to fetch chunk {chunk_id}: {e}")

        return chunks

    def _build_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Build context string from chunks."""
        context_parts = []

        for i, chunk in enumerate(chunks, 1):
            content = chunk.get("content", "")
            title = chunk.get("title", chunk.get("source", f"Source {i}"))

            context_parts.append(f"[{i}] {title}:\n{content}\n")

        return "\n".join(context_parts)

    def _extract_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract source information from chunks."""
        sources = []

        for chunk in chunks:
            source = {
                "id": chunk.get("id", ""),
                "title": chunk.get("title", chunk.get("source", "")),
                "score": chunk.get("score", 0.0),
            }
            sources.append(source)

        return sources
