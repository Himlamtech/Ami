"""Generate (RAG) routes - Refactored."""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from app.api.schemas.document_dto import QueryRequest, QueryResponse
from app.application.use_cases.rag import QueryWithRAGInput
from app.domain.value_objects.rag_config import RAGConfig
from app.domain.value_objects.generation_config import GenerationConfig
from app.infrastructure.factory import get_factory


router = APIRouter(prefix="/generate", tags=["generation"])


@router.post("/query", response_model=QueryResponse)
async def query_with_rag(request: QueryRequest):
    """Query with RAG."""
    from app.application.use_cases.rag import QueryWithRAGUseCase
    
    try:
        factory = get_factory()
        
        # Get services
        embedding_service = factory.get_embedding_service()
        vector_store = factory.get_vector_store()
        llm_service = factory.get_llm_service()
        
        if not all([embedding_service, vector_store, llm_service]):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Required services not available"
            )
        
        # Create use case
        use_case = QueryWithRAGUseCase(
            embedding_service=embedding_service,
            vector_store_service=vector_store,
            llm_service=llm_service,
        )
        
        # Execute
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
            detail=f"Query failed: {str(e)}"
        )


@router.post("/query/stream")
async def query_with_rag_stream(request: QueryRequest):
    """Query with RAG (streaming)."""
    # TODO: Implement streaming version
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Streaming not yet implemented in refactored version"
    )
