"""
Comprehensive API routes with extensive configuration options.
Organized into generate/ and vectordb/ namespaces.
"""

import json
import os
import tempfile
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse

from app.application.factory import ProviderFactory
from app.application.services import DocumentService, RAGService
from app.config.settings import settings
from app.core.models import (
    ChatRequest,
    ChatResponse,
    DatabaseStats,
    DeleteResponse,
    ListDocumentsRequest,
    ListDocumentsResponse,
    Message,
    ModelInfo,
    ProviderStatus,
    SearchRequest,
    SearchResponse,
    UploadRequest,
    UploadResponse,
)

router = APIRouter()


async def get_rag_service_from_request(
    llm_provider: Optional[str] = None,
    embedding_provider: Optional[str] = None,
    vector_store: Optional[str] = None,
) -> RAGService:
    """Create RAG service based on request parameters."""
    try:
        llm_provider = llm_provider or settings.default_llm_provider
        embedding_provider = embedding_provider or settings.default_embedding_provider
        vector_store = vector_store or settings.default_vector_store

        embedding = ProviderFactory.get_embedding_provider(embedding_provider)
        llm = ProviderFactory.get_llm_provider(llm_provider)
        vector = await ProviderFactory.get_vector_store(vector_store)
        processor = ProviderFactory.get_document_processor()
        doc_service = DocumentService(processor)

        # Get Redis client for caching
        cache_client = (
            await ProviderFactory.get_redis_client() if settings.enable_cache else None
        )

        return RAGService(embedding, llm, vector, doc_service, cache_client)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to initialize service: {str(e)}"
        )


# ============================================================================
# GENERATE ENDPOINTS
# ============================================================================


@router.post("/generate/chat", response_model=ChatResponse, tags=["generate"])
async def generate_chat(request: ChatRequest):
    """
    Generate chat response with comprehensive options.

    Options:
    - model: LLM provider (openai, gemini, anthropic)
    - thinking_mode: Enable reasoning modes
    - rag_config: Control retrieval settings
    - generation_config: Fine-tune generation (temperature, top_p, etc.)
    - system_prompt: Custom system instructions
    """
    try:
        rag_service = await get_rag_service_from_request(
            llm_provider=request.model,
            embedding_provider=request.embedding_provider,
            vector_store=request.vector_store,
        )

        # Get the last user message
        user_query = next(
            (m.content for m in reversed(request.messages) if m.role == "user"), ""
        )
        if not user_query:
            raise HTTPException(status_code=400, detail="No user message found")

        # Build system prompt with thinking mode
        system_prompt = request.system_prompt or ""
        if request.thinking_mode.value != "disabled":
            thinking_instructions = {
                "chain_of_thought": "Think step by step before answering. Show your reasoning.",
                "step_by_step": "Break down your answer into clear steps.",
                "reasoning": "Provide detailed reasoning for your answer.",
            }
            system_prompt += (
                f"\n\n{thinking_instructions.get(request.thinking_mode.value, '')}"
            )

        # Prepare generation kwargs
        gen_kwargs = {
            "temperature": request.generation_config.temperature,
            "max_tokens": request.generation_config.max_tokens,
            "top_p": request.generation_config.top_p,
            "frequency_penalty": request.generation_config.frequency_penalty,
            "presence_penalty": request.generation_config.presence_penalty,
        }
        if request.generation_config.stop_sequences:
            gen_kwargs["stop"] = request.generation_config.stop_sequences

        # Query with RAG if enabled
        if request.rag_config.enabled:
            result = await rag_service.query(
                query=user_query,
                top_k=request.rag_config.top_k,
                collection=(
                    request.collection if request.collection != "default" else None
                ),
                metadata_filter=request.rag_config.metadata_filter,
                similarity_threshold=request.rag_config.similarity_threshold,
                **gen_kwargs,
            )

            return ChatResponse(
                message=Message(role="assistant", content=result["answer"]),
                sources=(
                    result["sources"] if request.rag_config.include_sources else None
                ),
                metadata={
                    "rag_enabled": True,
                    "thinking_mode": request.thinking_mode.value,
                    "model": request.model or settings.default_llm_provider,
                },
            )
        else:
            # Direct generation without RAG
            context = system_prompt if system_prompt else None
            answer = await rag_service.llm_provider.generate(
                prompt=user_query, context=context, **gen_kwargs
            )

            return ChatResponse(
                message=Message(role="assistant", content=answer),
                sources=None,
                metadata={
                    "rag_enabled": False,
                    "thinking_mode": request.thinking_mode.value,
                    "model": request.model or settings.default_llm_provider,
                },
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/stream", tags=["generate"])
async def generate_stream(request: ChatRequest):
    """
    Stream chat response with real-time chunks in Server-Sent Events format.
    Same options as /generate/chat but returns streaming response.
    """
    try:
        if not request.stream:
            request.stream = True

        rag_service = await get_rag_service_from_request(
            llm_provider=request.model,
            embedding_provider=request.embedding_provider,
            vector_store=request.vector_store,
        )

        user_query = next(
            (m.content for m in reversed(request.messages) if m.role == "user"), ""
        )
        if not user_query:
            raise HTTPException(status_code=400, detail="No user message found")

        gen_kwargs = {
            "temperature": request.generation_config.temperature,
            "max_tokens": request.generation_config.max_tokens,
        }

        async def event_stream():
            try:
                if request.rag_config.enabled:
                    async for chunk in rag_service.stream_query(
                        user_query,
                        top_k=request.rag_config.top_k,
                        collection=(
                            request.collection
                            if request.collection != "default"
                            else None
                        ),
                        **gen_kwargs,
                    ):
                        # Server-Sent Events format
                        yield f"data: {json.dumps({'content': chunk})}\n\n"
                else:
                    async for chunk in rag_service.llm_provider.stream_generate(
                        user_query, **gen_kwargs
                    ):
                        yield f"data: {json.dumps({'content': chunk})}\n\n"

                # Send done signal
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# VECTORDB ENDPOINTS
# ============================================================================


@router.post("/vectordb/upload", response_model=UploadResponse, tags=["vectordb"])
async def vectordb_upload(request: UploadRequest):
    """
    Upload documents to vector database.

    Options:
    - collection: Organize documents in collections
    - chunk_config: Control chunking strategy and size
    - embedding_provider: Choose embedding model
    - vector_store: Target vector database
    - metadata: Custom metadata for filtering
    """
    try:
        rag_service = await get_rag_service_from_request(
            embedding_provider=request.embedding_provider,
            vector_store=request.vector_store,
        )

        # Override chunk settings
        rag_service.document_service.chunk_size = request.chunk_config.chunk_size
        rag_service.document_service.chunk_overlap = request.chunk_config.chunk_overlap

        # Add collection to metadata
        metadata = {**request.metadata, "collection": request.collection}

        if request.content:
            result = await rag_service.ingest_text(request.content, metadata)
        elif request.file_path:
            result = await rag_service.ingest_file(request.file_path, metadata)
        else:
            raise HTTPException(
                status_code=400, detail="Either content or file_path must be provided"
            )

        return UploadResponse(
            doc_ids=result["doc_ids"],
            chunk_count=result["chunk_count"],
            collection=request.collection,
            message=f"Successfully uploaded {result['chunk_count']} chunks to collection '{request.collection}'",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vectordb/upload/file", response_model=UploadResponse, tags=["vectordb"])
async def vectordb_upload_file(
    file: UploadFile = File(...),
    collection: str = Query(default="default"),
    chunk_size: int = Query(default=512, ge=100, le=4000),
    chunk_overlap: int = Query(default=50, ge=0, le=500),
    embedding_provider: Optional[str] = Query(default=None),
    vector_store: Optional[str] = Query(default=None),
):
    """Upload file directly to vector database."""
    try:
        rag_service = await get_rag_service_from_request(
            embedding_provider=embedding_provider, vector_store=vector_store
        )

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=os.path.splitext(file.filename)[1]
        ) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        metadata = {
            "filename": file.filename,
            "content_type": file.content_type,
            "collection": collection,
        }

        result = await rag_service.ingest_file(tmp_path, metadata)
        os.unlink(tmp_path)

        return UploadResponse(
            doc_ids=result["doc_ids"],
            chunk_count=result["chunk_count"],
            collection=collection,
            message=f"File '{file.filename}' uploaded successfully",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vectordb/search", response_model=SearchResponse, tags=["vectordb"])
async def vectordb_search(request: SearchRequest):
    """
    Search vector database with filters.

    Options:
    - collection: Search specific collection
    - similarity_threshold: Minimum similarity score
    - metadata_filter: Filter by document metadata
    - embedding_provider: Choose embedding model
    """
    try:
        rag_service = await get_rag_service_from_request(
            embedding_provider=request.embedding_provider,
            vector_store=request.vector_store,
        )

        # Get query embedding
        query_embedding = await rag_service.embedding_provider.embed_text(request.query)

        # Search
        results = await rag_service.vector_store.search(
            query_embedding=query_embedding, top_k=request.top_k
        )

        # Filter by collection and threshold
        filtered_results = [
            r
            for r in results
            if r.get("metadata", {}).get("collection") == request.collection
            and r.get("similarity", 0) >= request.similarity_threshold
        ]

        # Apply metadata filter if provided
        if request.metadata_filter:
            filtered_results = [
                r
                for r in filtered_results
                if all(
                    r.get("metadata", {}).get(k) == v
                    for k, v in request.metadata_filter.items()
                )
            ]

        return SearchResponse(
            results=filtered_results,
            count=len(filtered_results),
            metadata={
                "collection": request.collection,
                "top_k": request.top_k,
                "threshold": request.similarity_threshold,
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vectordb/list", response_model=ListDocumentsResponse, tags=["vectordb"])
async def vectordb_list(
    collection: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    vector_store: Optional[str] = Query(default=None),
):
    """List documents in vector database with pagination."""
    try:
        # This is a simplified version - would need actual implementation in vector stores
        return ListDocumentsResponse(
            documents=[], total_count=0, limit=limit, offset=offset
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/vectordb/{doc_id}", response_model=DeleteResponse, tags=["vectordb"])
async def vectordb_delete(
    doc_id: str, vector_store: Optional[str] = Query(default=None)
):
    """Delete document by ID."""
    try:
        vector = await ProviderFactory.get_vector_store(
            vector_store or settings.default_vector_store
        )
        await vector.delete([doc_id])

        return DeleteResponse(
            deleted_count=1, message=f"Document {doc_id} deleted successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vectordb/collections", response_model=List[str], tags=["vectordb"])
async def vectordb_collections(vector_store: Optional[str] = Query(default=None)):
    """List all collections from vector store."""
    try:
        store = await ProviderFactory.get_vector_store(
            vector_store or settings.default_vector_store
        )
        collections = await store.get_collections()
        return collections
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list collections: {str(e)}"
        )


@router.get("/vectordb/stats", response_model=DatabaseStats, tags=["vectordb"])
async def vectordb_stats(
    collection: Optional[str] = Query(default=None),
    vector_store: Optional[str] = Query(default=None),
):
    """Get database statistics with actual counts."""
    try:
        store = await ProviderFactory.get_vector_store(
            vector_store or settings.default_vector_store
        )

        # Get stats
        stats = await store.get_stats(collection=collection)

        # Get collections list
        collections = await store.get_collections()

        return DatabaseStats(
            total_documents=stats.get("total_documents", 0),
            total_chunks=stats.get("total_chunks", 0),
            collections=collections,
            vector_store=vector_store or settings.default_vector_store,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


# ============================================================================
# CONFIG ENDPOINTS
# ============================================================================


@router.get("/config/models", response_model=List[ModelInfo], tags=["config"])
async def config_models():
    """List all available models and their status."""
    models = [
        ModelInfo(name="openai", type="llm", available=bool(settings.openai_api_key)),
        ModelInfo(name="gemini", type="llm", available=bool(settings.gemini_api_key)),
        ModelInfo(
            name="anthropic", type="llm", available=bool(settings.anthropic_api_key)
        ),
        ModelInfo(
            name="openai", type="embedding", available=bool(settings.openai_api_key)
        ),
        ModelInfo(name="huggingface", type="embedding", available=True),
        ModelInfo(name="pgvector", type="vector_store", available=True),
        ModelInfo(name="chroma", type="vector_store", available=True),
    ]
    return models


@router.get("/config/providers", response_model=ProviderStatus, tags=["config"])
async def config_providers():
    """Get provider status and defaults."""
    return ProviderStatus(
        providers={
            "llm": [
                ModelInfo(
                    name="openai", type="llm", available=bool(settings.openai_api_key)
                ),
                ModelInfo(
                    name="gemini", type="llm", available=bool(settings.gemini_api_key)
                ),
                ModelInfo(
                    name="anthropic",
                    type="llm",
                    available=bool(settings.anthropic_api_key),
                ),
            ],
            "embedding": [
                ModelInfo(
                    name="openai",
                    type="embedding",
                    available=bool(settings.openai_api_key),
                ),
                ModelInfo(name="huggingface", type="embedding", available=True),
            ],
            "vector_store": [
                ModelInfo(name="pgvector", type="vector_store", available=True),
                ModelInfo(name="chroma", type="vector_store", available=True),
            ],
        },
        default_providers={
            "llm": settings.default_llm_provider,
            "embedding": settings.default_embedding_provider,
            "vector_store": settings.default_vector_store,
        },
    )


@router.get("/config/health", tags=["config"])
async def config_health():
    """Detailed health check with actual database connection tests."""
    health_status = {
        "status": "healthy",
        "providers": {
            "openai": bool(settings.openai_api_key),
            "gemini": bool(settings.gemini_api_key),
            "anthropic": bool(settings.anthropic_api_key),
        },
        "databases": {"postgres": "unknown", "redis": "unknown", "chroma": "unknown"},
        "vector_store": settings.default_vector_store,
    }

    # Check PostgreSQL
    try:
        postgres_client = await ProviderFactory.get_postgres_client()
        await postgres_client.fetch_val("SELECT 1")
        health_status["databases"]["postgres"] = "ok"
    except Exception as e:
        health_status["databases"]["postgres"] = f"error: {str(e)[:50]}"
        health_status["status"] = "degraded"

    # Check Redis
    try:
        redis_client = await ProviderFactory.get_redis_client()
        await redis_client.ping()
        health_status["databases"]["redis"] = "ok"
    except Exception as e:
        health_status["databases"]["redis"] = f"error: {str(e)[:50]}"
        health_status["status"] = "degraded"

    # Check ChromaDB
    try:
        chroma_client = await ProviderFactory.get_chroma_client()
        await chroma_client.heartbeat()
        health_status["databases"]["chroma"] = "ok"
    except Exception as e:
        health_status["databases"]["chroma"] = f"error: {str(e)[:50]}"
        # ChromaDB is optional, don't mark as degraded

    return health_status
