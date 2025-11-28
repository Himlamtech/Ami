"""Query with RAG use case."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from app.domain.value_objects.rag_config import RAGConfig
from app.domain.value_objects.generation_config import GenerationConfig
from app.application.interfaces.services.embedding_service import IEmbeddingService
from app.application.interfaces.services.vector_store_service import IVectorStoreService
from app.application.interfaces.services.llm_service import ILLMService


@dataclass
class QueryWithRAGInput:
    """Input for query with RAG use case."""
    query: str
    collection: Optional[str] = "default"
    rag_config: Optional[RAGConfig] = None
    generation_config: Optional[GenerationConfig] = None
    system_prompt: Optional[str] = None


@dataclass
class QueryWithRAGOutput:
    """Output from query with RAG use case."""
    answer: str
    sources: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class QueryWithRAGUseCase:
    """
    Use Case: Query with Retrieval-Augmented Generation.
    
    Business Rules:
    1. If RAG enabled:
       - Generate query embedding
       - Search vector store for relevant documents
       - Build context from retrieved documents
    2. Generate answer with LLM using context
    3. Return answer with sources
    
    Single Responsibility: RAG query workflow
    """
    
    def __init__(
        self,
        embedding_service: IEmbeddingService,
        vector_store_service: IVectorStoreService,
        llm_service: ILLMService,
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store_service
        self.llm_service = llm_service
    
    async def execute(self, input_data: QueryWithRAGInput) -> QueryWithRAGOutput:
        """
        Execute RAG query.
        
        Args:
            input_data: Query and configuration
            
        Returns:
            QueryWithRAGOutput with answer and sources
        """
        # Use defaults if not provided
        rag_config = input_data.rag_config or RAGConfig()
        gen_config = input_data.generation_config or GenerationConfig.balanced()
        
        sources = []
        context = ""
        
        # Perform RAG retrieval if enabled
        if rag_config.enabled:
            # 1. Generate query embedding
            query_embedding = await self.embedding_service.embed_text(input_data.query)
            
            # 2. Search vector store
            search_results = await self.vector_store.search(
                query_embedding=query_embedding,
                top_k=rag_config.top_k,
                collection=input_data.collection,
                metadata_filter=rag_config.metadata_filter,
                similarity_threshold=rag_config.similarity_threshold,
            )
            
            sources = search_results
            
            # 3. Build context from results
            if search_results and rag_config.include_sources:
                context = self._build_context(search_results)
        
        # 4. Build full prompt
        full_prompt = self._build_prompt(
            query=input_data.query,
            context=context,
            system_prompt=input_data.system_prompt,
        )
        
        # 5. Generate answer with LLM
        answer = await self.llm_service.generate(
            prompt=full_prompt,
            temperature=gen_config.temperature,
            max_tokens=gen_config.max_tokens,
            top_p=gen_config.top_p,
            frequency_penalty=gen_config.frequency_penalty,
            presence_penalty=gen_config.presence_penalty,
        )
        
        return QueryWithRAGOutput(
            answer=answer,
            sources=sources,
            metadata={
                "rag_enabled": rag_config.enabled,
                "sources_count": len(sources),
                "collection": input_data.collection,
                "temperature": gen_config.temperature,
            },
        )
    
    def _build_context(self, search_results: List[Dict[str, Any]]) -> str:
        """Build context string from search results."""
        context_parts = []
        for i, result in enumerate(search_results, 1):
            content = result.get("content", "")
            score = result.get("score", 0.0)
            context_parts.append(f"[Source {i}] (Relevance: {score:.2f})\n{content}")
        
        return "\n\n".join(context_parts)
    
    def _build_prompt(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str],
    ) -> str:
        """Build full prompt for LLM."""
        parts = []
        
        if system_prompt:
            parts.append(f"System: {system_prompt}\n")
        
        if context:
            parts.append(f"Relevant Information:\n{context}\n")
            parts.append("Based on the information above, please answer the question.")
        
        parts.append(f"Question: {query}")
        
        return "\n\n".join(parts)
