"""RAG generation endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.api.schemas.document_dto import QueryRequest, QueryResponse
from app.application.use_cases.rag import QueryWithRAGUseCase, QueryWithRAGInput
from app.domain.value_objects.rag_config import RAGConfig
from app.domain.value_objects.generation_config import GenerationConfig
from app.config.services import ServiceRegistry


router = APIRouter(prefix="/generate", tags=["generation"])


@router.post("/query", response_model=QueryResponse)
async def query_with_rag(request: QueryRequest):
    """Query with RAG (non-streaming)."""
    try:
        embedding_service = ServiceRegistry.get_embedding()
        vector_store = ServiceRegistry.get_vector_store()
        llm_service = ServiceRegistry.get_llm()

        if not all([embedding_service, vector_store, llm_service]):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Required services not available",
            )

        use_case = QueryWithRAGUseCase(
            embedding_service=embedding_service,
            vector_store_service=vector_store,
            llm_service=llm_service,
        )

        result = await use_case.execute(
            QueryWithRAGInput(
                query=request.query,
                collection=request.collection,
                rag_config=RAGConfig(
                    enabled=True,
                    top_k=request.top_k,
                    similarity_threshold=request.similarity_threshold,
                    include_sources=request.include_sources,
                ),
                generation_config=GenerationConfig.balanced(),
            )
        )

        return QueryResponse(
            answer=result.answer,
            sources=result.sources,
            metadata=result.metadata,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query failed: {str(e)}",
        )


@router.post("/query/stream")
async def query_with_rag_stream(request: QueryRequest):
    """Placeholder for streaming RAG."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Streaming not yet implemented in refactored version",
    )


__all__ = ["router"]
