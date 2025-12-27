"""Hybrid Query use case - RAG + Web Search fallback."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum

from domain.value_objects.rag_config import RAGConfig
from application.interfaces.services.embedding_service import IEmbeddingService
from application.interfaces.services.vector_store_service import IVectorStoreService
from application.interfaces.services.llm_service import ILLMService
from application.interfaces.services.web_search_service import IWebSearchService


class QuerySource(str, Enum):
    """Source of the answer."""

    KNOWLEDGE_BASE = "knowledge_base"
    WEB_SEARCH = "web_search"
    HYBRID = "hybrid"
    LLM_ONLY = "llm_only"


@dataclass
class HybridQueryInput:
    """Input for hybrid query use case."""

    query: str
    collection: str = "default"

    # RAG options
    use_rag: bool = True
    rag_config: Optional[RAGConfig] = None
    rag_threshold: float = 0.6  # Min relevance score to use RAG

    # Web search options
    use_web_search: bool = True
    web_search_fallback: bool = True  # Use web if RAG not confident

    # System prompt
    system_prompt: Optional[str] = None


@dataclass
class HybridQueryOutput:
    """Output from hybrid query use case."""

    answer: str
    source: QuerySource

    # Knowledge base sources
    kb_sources: List[Dict[str, Any]] = field(default_factory=list)
    kb_confidence: float = 0.0

    # Web search sources
    web_sources: List[Dict[str, Any]] = field(default_factory=list)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


class HybridQueryUseCase:
    """
    Use Case: Hybrid Query with RAG + Web Search.

    Decision Logic:
    1. First try RAG search in knowledge base
    2. If RAG confidence < threshold, fallback to web search
    3. Combine results if both have relevant info
    4. Generate final answer with LLM

    Use Cases:
    - Questions about PTIT → RAG (knowledge base)
    - Current events, news → Web Search
    - Mixed questions → Hybrid

    Single Responsibility: Intelligent query routing
    """

    DEFAULT_SYSTEM_PROMPT = """Bạn là AMI - trợ lý thông minh của Học viện PTIT.
    
Nguồn thông tin:
- Kiến thức nội bộ PTIT (knowledge base)  
- Tìm kiếm web cho thông tin cập nhật

Quy tắc:
1. Ưu tiên thông tin từ knowledge base cho câu hỏi về PTIT
2. Dùng web search cho thông tin thời sự, cập nhật
3. Trả lời ngắn gọn, chính xác
4. Nói rõ nguồn thông tin khi cần thiết"""

    def __init__(
        self,
        embedding_service: IEmbeddingService,
        vector_store: IVectorStoreService,
        llm_service: ILLMService,
        web_search_service: Optional[IWebSearchService] = None,
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.llm_service = llm_service
        self.web_search = web_search_service

    async def execute(self, input_data: HybridQueryInput) -> HybridQueryOutput:
        """
        Execute hybrid query with intelligent routing.

        Args:
            input_data: Query and options

        Returns:
            HybridQueryOutput with answer and sources
        """
        kb_sources = []
        kb_confidence = 0.0
        web_sources = []
        kb_context = ""
        web_context = ""
        source = QuerySource.LLM_ONLY

        # 1. Try RAG search
        if input_data.use_rag:
            rag_config = input_data.rag_config or RAGConfig()

            query_embedding = await self.embedding_service.embed_text(input_data.query)

            search_results = await self.vector_store.search(
                query_embedding=query_embedding,
                top_k=rag_config.top_k,
                collection=input_data.collection,
                score_threshold=rag_config.similarity_threshold,  # Map domain to interface name
            )

            if search_results:
                # Calculate average confidence
                scores = [r.get("score", 0) for r in search_results]
                kb_confidence = sum(scores) / len(scores) if scores else 0

                kb_sources = search_results
                kb_context = self._build_context(search_results)

                if kb_confidence >= input_data.rag_threshold:
                    source = QuerySource.KNOWLEDGE_BASE

        # 2. Fallback or supplement with web search
        needs_web_search = (
            input_data.use_web_search
            and self.web_search
            and (
                not input_data.web_search_fallback  # Always use web
                or kb_confidence < input_data.rag_threshold  # Fallback
            )
        )

        if needs_web_search:
            try:
                web_result = await self.web_search.search(
                    query=input_data.query,
                    num_results=5,
                )

                if web_result.sources:
                    web_sources = [
                        {
                            "title": s.title,
                            "url": s.url,
                            "snippet": s.snippet,
                        }
                        for s in web_result.sources
                    ]
                    web_context = web_result.answer

                    if source == QuerySource.KNOWLEDGE_BASE:
                        source = QuerySource.HYBRID
                    else:
                        source = QuerySource.WEB_SEARCH

            except Exception:
                # Web search failed, continue with RAG only
                pass

        # 3. Build final context
        final_context = self._combine_contexts(
            kb_context=kb_context,
            web_context=web_context,
            source=source,
        )

        # 4. Generate answer
        system_prompt = input_data.system_prompt or self.DEFAULT_SYSTEM_PROMPT

        if final_context:
            prompt = f"""Dựa trên thông tin sau, hãy trả lời câu hỏi.

{final_context}

Câu hỏi: {input_data.query}"""
        else:
            prompt = input_data.query

        answer = await self.llm_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
        )

        return HybridQueryOutput(
            answer=answer,
            source=source,
            kb_sources=kb_sources,
            kb_confidence=kb_confidence,
            web_sources=web_sources,
            metadata={
                "used_rag": input_data.use_rag and len(kb_sources) > 0,
                "used_web": len(web_sources) > 0,
            },
        )

    def _build_context(self, search_results: List[Dict[str, Any]]) -> str:
        """Build context from search results."""
        if not search_results:
            return ""

        context_parts = []
        for i, result in enumerate(search_results[:5], 1):
            text = result.get("text", result.get("content", ""))
            source = result.get("metadata", {}).get("source", "")
            context_parts.append(f"[{i}] {text}")
            if source:
                context_parts.append(f"    Nguồn: {source}")

        return "\n".join(context_parts)

    def _combine_contexts(
        self,
        kb_context: str,
        web_context: str,
        source: QuerySource,
    ) -> str:
        """Combine contexts from different sources."""
        parts = []

        if kb_context and source in [QuerySource.KNOWLEDGE_BASE, QuerySource.HYBRID]:
            parts.append("--- Từ Knowledge Base PTIT ---")
            parts.append(kb_context)

        if web_context and source in [QuerySource.WEB_SEARCH, QuerySource.HYBRID]:
            parts.append("\n--- Từ Web Search ---")
            parts.append(web_context)

        return "\n".join(parts)
