"""RAG service - Orchestration for RAG operations."""

from typing import List, Dict, Any, Optional
from app.application.interfaces.services.embedding_service import IEmbeddingService
from app.application.interfaces.services.vector_store_service import IVectorStoreService
from app.application.interfaces.services.llm_service import ILLMService
from app.domain.value_objects.rag_config import RAGConfig
from app.domain.value_objects.generation_config import GenerationConfig


class RAGService:
    """
    RAG service for advanced RAG operations.
    
    Handles complex RAG workflows beyond simple query.
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
    
    async def hybrid_search(
        self,
        query: str,
        collection: str,
        rag_config: RAGConfig,
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search (vector + keyword).
        
        Currently implements vector search only.
        Can be extended to combine with BM25/keyword search.
        """
        # Generate query embedding
        query_embedding = await self.embedding_service.embed_text(query)
        
        # Vector search
        results = await self.vector_store.search(
            query_embedding=query_embedding,
            top_k=rag_config.top_k,
            collection=collection,
            similarity_threshold=rag_config.similarity_threshold,
        )
        
        return results
    
    async def rerank_results(
        self,
        query: str,
        results: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Rerank search results using cross-encoder or LLM.
        
        Currently returns top results as-is.
        Can be enhanced with actual reranking model.
        """
        # Simple implementation: return top_k results sorted by score
        sorted_results = sorted(
            results,
            key=lambda x: x.get("score", 0),
            reverse=True
        )
        
        return sorted_results[:top_k]
    
    async def generate_with_citations(
        self,
        query: str,
        context: str,
        sources: List[Dict[str, Any]],
        gen_config: GenerationConfig,
    ) -> Dict[str, Any]:
        """
        Generate answer with inline citations.
        
        Asks LLM to include [1], [2] style citations.
        """
        # Build prompt with numbered sources
        numbered_sources = []
        for i, source in enumerate(sources, 1):
            content = source.get("content", "")
            numbered_sources.append(f"[{i}] {content}")
        
        context_with_numbers = "\n\n".join(numbered_sources)
        
        prompt = f"""Answer the question based on the provided sources. 
Include citations using [1], [2] format when referencing sources.

Sources:
{context_with_numbers}

Question: {query}

Answer with citations:"""
        
        answer = await self.llm_service.generate(
            prompt=prompt,
            temperature=gen_config.temperature,
            max_tokens=gen_config.max_tokens,
        )
        
        return {
            "answer": answer,
            "sources": sources,
            "has_citations": "[1]" in answer or "[2]" in answer,
        }
    
    def build_context_window(
        self,
        results: List[Dict[str, Any]],
        max_tokens: int = 3000,
    ) -> str:
        """
        Build context window from search results.
        
        Ensures context fits within token limit.
        """
        context_parts = []
        total_chars = 0
        # Rough estimate: 1 token ≈ 4 characters
        max_chars = max_tokens * 4
        
        for i, result in enumerate(results, 1):
            content = result.get("content", "")
            score = result.get("score", 0.0)
            
            part = f"[Source {i}] (Relevance: {score:.2f})\n{content}\n"
            part_chars = len(part)
            
            if total_chars + part_chars > max_chars:
                break
            
            context_parts.append(part)
            total_chars += part_chars
        
        return "\n".join(context_parts)
