"""Smart Query routes with artifact support."""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import Optional

from app.api.schemas.smart_query_dto import (
    SmartQueryRequest,
    SmartQueryResponse,
    SmartQueryMetadata,
    ArtifactDTO,
    SourceReferenceDTO,
    ResponseIntentDTO,
    SourceTypeDTO,
    ArtifactDownloadResponse,
)
from app.application.use_cases.rag import SmartQueryWithRAGUseCase, SmartQueryInput
from app.domain.value_objects.rag_config import RAGConfig
from app.domain.value_objects.generation_config import GenerationConfig
from app.infrastructure.factory import get_factory


router = APIRouter(prefix="/smart-query", tags=["smart-query"])


@router.post("", response_model=SmartQueryResponse)
async def smart_query(request: SmartQueryRequest):
    """
    Smart query with artifact detection and rich response.
    
    This endpoint intelligently detects user intent and returns:
    - Text response from RAG
    - Downloadable artifacts (forms, documents, templates)
    - Source references
    
    Example queries:
    - "Cho mình xin mẫu đơn nghỉ học" → Returns form artifact
    - "Học phí kỳ này bao nhiêu?" → Returns text answer
    - "Cách đăng ký học lại?" → Returns procedure guide + form if available
    """
    try:
        factory = get_factory()
        
        # Get services
        embedding_service = factory.get_embedding_service()
        vector_store = factory.get_vector_store()
        llm_service = factory.get_llm_service()
        document_repo = factory.document_repository
        
        if not all([embedding_service, vector_store, llm_service, document_repo]):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Required services not available"
            )
        
        # Create use case (type: ignore for interface compatibility)
        use_case = SmartQueryWithRAGUseCase(
            embedding_service=embedding_service,  # type: ignore
            vector_store_service=vector_store,  # type: ignore
            llm_service=llm_service,  # type: ignore
            document_repository=document_repo,
        )
        
        # Build input
        input_data = SmartQueryInput(
            query=request.query,
            session_id=request.session_id,
            user_info=request.user_info,
            collection=request.collection,
            rag_config=RAGConfig(
                enabled=request.enable_rag,
                top_k=request.top_k,
                similarity_threshold=request.similarity_threshold,
                include_sources=True,
            ),
            generation_config=GenerationConfig(
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            ),
        )
        
        # Execute
        result = await use_case.execute(input_data)
        
        # Convert to response DTO
        artifacts = [
            ArtifactDTO(
                artifact_id=a.artifact_id,
                document_id=a.document_id,
                file_name=a.file_name,
                artifact_type=a.artifact_type,
                download_url=f"/api/v1/files/{a.document_id}/download/{a.artifact_id}",
                preview_url=a.preview_url,
                size_bytes=a.size_bytes,
                size_display=a.size_display,
                is_fillable=a.is_fillable,
                fill_fields=a.fill_fields,
            )
            for a in result.artifacts
        ]
        
        sources = [
            SourceReferenceDTO(
                source_type=SourceTypeDTO(s.source_type.value),
                document_id=s.document_id,
                title=s.title,
                url=s.url,
                chunk_text=s.chunk_text,
                relevance_score=s.relevance_score,
            )
            for s in result.sources
        ]
        
        return SmartQueryResponse(
            content=result.content,
            intent=ResponseIntentDTO(result.intent.value),
            artifacts=artifacts,
            sources=sources,
            metadata=SmartQueryMetadata(
                model_used=result.model_used,
                processing_time_ms=result.processing_time_ms,
                tokens_used=result.tokens_used,
                sources_count=len(sources),
                artifacts_count=len(artifacts),
                has_fillable_form=result.has_fillable_form(),
            ),
            created_at=result.created_at,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Smart query failed: {str(e)}"
        )


@router.get("/files/{document_id}/download/{artifact_id}")
async def download_artifact(document_id: str, artifact_id: str):
    """
    Download a specific artifact from a document.
    
    Returns pre-signed URL for file download from MinIO.
    """
    try:
        factory = get_factory()
        document_repo = factory.document_repository
        storage = factory.get_storage_service()
        
        if not document_repo or not storage:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Required services not available"
            )
        
        # Get document
        document = await document_repo.get_by_id(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )
        
        # Find artifact
        artifact = None
        for idx, a in enumerate(document.artifacts):
            if artifact_id == f"{document_id}_artifact_{idx}":
                artifact = a
                break
        
        if not artifact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artifact {artifact_id} not found"
            )
        
        # Generate pre-signed download URL
        # Use default bucket "data" for artifacts
        download_url = await storage.generate_presigned_url(
            bucket="data",
            key=artifact.url,
            expires_in=3600,  # 1 hour
        )
        
        return ArtifactDownloadResponse(
            download_url=download_url,
            file_name=artifact.file_name,
            mime_type=artifact.mime_type,
            size_bytes=artifact.size_bytes,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Download failed: {str(e)}"
        )


@router.get("/files/{document_id}/preview/{artifact_id}")
async def preview_artifact(document_id: str, artifact_id: str):
    """
    Get preview URL for an artifact.
    
    Returns pre-signed URL for preview (for previewable file types).
    """
    try:
        factory = get_factory()
        document_repo = factory.document_repository
        storage = factory.get_storage_service()
        
        if not document_repo or not storage:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Required services not available"
            )
        
        # Get document
        document = await document_repo.get_by_id(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )
        
        # Find artifact
        artifact = None
        for idx, a in enumerate(document.artifacts):
            if artifact_id == f"{document_id}_artifact_{idx}":
                artifact = a
                break
        
        if not artifact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artifact {artifact_id} not found"
            )
        
        if not artifact.is_previewable():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {artifact.mime_type} is not previewable"
            )
        
        # Use preview URL if available, otherwise generate from storage
        if artifact.preview_url:
            preview_url = artifact.preview_url
        else:
            preview_url = await storage.generate_presigned_url(
                bucket="data",
                key=artifact.url,
                expires_in=3600,
            )
        
        return {
            "preview_url": preview_url,
            "file_name": artifact.file_name,
            "mime_type": artifact.mime_type,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Preview failed: {str(e)}"
        )
