"""Admin routes - Protected by Admin API Key."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional

from app.api.dependencies.auth import verify_admin_api_key
from app.api.schemas.document_dto import (
    DocumentResponse,
    DocumentListResponse,
)
from app.config.services import ServiceRegistry


router = APIRouter(prefix="/admin", tags=["admin"])


# ===== Document Management (Admin Only) =====


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    collection: Optional[str] = None,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """List all documents (admin only)."""
    doc_repo = ServiceRegistry.get_document_repository()

    documents = await doc_repo.list_documents(
        skip=skip,
        limit=limit,
        collection=collection,
    )
    total = await doc_repo.count(collection=collection)

    return DocumentListResponse(
        documents=[
            DocumentResponse(
                id=doc.id,
                title=doc.title,
                file_name=doc.file_name,
                collection=doc.collection,
                chunk_count=doc.chunk_count,
                is_active=doc.is_active,
                created_at=doc.created_at,
                updated_at=doc.updated_at,
            )
            for doc in documents
        ],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """Delete a document (admin only)."""
    doc_repo = ServiceRegistry.get_document_repository()

    doc = await doc_repo.get_by_id(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    await doc_repo.delete(document_id)
    return None


# ===== System Stats (Admin Only) =====


@router.get("/stats")
async def get_stats(is_admin: bool = Depends(verify_admin_api_key)):
    """Get system statistics (admin only)."""
    doc_repo = ServiceRegistry.get_document_repository()
    chat_repo = ServiceRegistry.get_chat_repository()

    total_docs = await doc_repo.count()
    total_sessions = await chat_repo.count_all_sessions()

    # Calculate total chunks from all documents
    documents = await doc_repo.list_documents(skip=0, limit=1000)
    total_chunks = sum(doc.chunk_count for doc in documents)

    return {
        "total_documents": total_docs,
        "total_chat_sessions": total_sessions,
        "total_chunks": total_chunks,
        "version": "2.0.0-refactored",
        "architecture": "Clean Architecture",
    }
