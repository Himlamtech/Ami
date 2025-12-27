"""Admin vector store routes - protected by admin API key."""

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from typing import Optional

from api.schemas.document_dto import (
    DocumentResponse,
    DocumentListResponse,
)
from api.dependencies.auth import verify_admin_api_key
from application.use_cases.documents import (
    UploadDocumentInput,
    ListDocumentsInput,
    DeleteDocumentInput,
)
from domain.value_objects.chunk_config import ChunkConfig
from domain.exceptions.document_exceptions import DocumentNotFoundException
from config.services import ServiceRegistry


router = APIRouter(
    prefix="/admin/vector-store",
    tags=["admin-vector-store"],
    dependencies=[Depends(verify_admin_api_key)],
)


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    collection: str = Form("default"),
    chunk_size: int = Form(512),
):
    """Upload and index document."""
    from application.use_cases.documents import UploadDocumentUseCase

    try:
        # Get services
        doc_repo = ServiceRegistry.get_document_repository()
        embedding_service = ServiceRegistry.get_embedding()
        vector_store = ServiceRegistry.get_vector_store()

        # Simple text chunker (can be improved)
        from application.interfaces.processors.text_chunker import ITextChunker

        class SimpleChunker(ITextChunker):
            def chunk_text(
                self, text, chunk_size=512, chunk_overlap=50, strategy="fixed"
            ):
                chunks = []
                for i in range(0, len(text), chunk_size - chunk_overlap):
                    chunks.append(text[i : i + chunk_size])
                return chunks

            def estimate_chunks(self, text, chunk_size):
                return len(text) // chunk_size + 1

        chunker = SimpleChunker()

        # Read file content
        content = await file.read()
        text_content = content.decode("utf-8")

        # Create use case
        use_case = UploadDocumentUseCase(
            document_repository=doc_repo,
            embedding_service=embedding_service,
            vector_store_service=vector_store,
            document_chunker=chunker,
        )

        # Execute
        result = await use_case.execute(
            UploadDocumentInput(
                title=file.filename,
                file_name=file.filename,
                content=text_content,
                collection=collection,
                chunk_config=ChunkConfig(chunk_size=chunk_size),
            )
        )

        return DocumentResponse(
            id=result.document.id,
            title=result.document.title,
            file_name=result.document.file_name,
            collection=result.document.collection,
            chunk_count=result.chunk_count,
            is_active=result.document.is_active,
            created_at=result.document.created_at,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}",
        )


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    collection: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
):
    """List documents (admin-only view)."""
    from application.use_cases.documents import ListDocumentsUseCase

    doc_repo = ServiceRegistry.get_document_repository()
    use_case = ListDocumentsUseCase(doc_repo)

    result = await use_case.execute(
        ListDocumentsInput(
            skip=skip,
            limit=limit,
            collection=collection,
        )
    )

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
            )
            for doc in result.documents
        ],
        total=result.total,
        skip=result.skip,
        limit=result.limit,
    )


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
):
    """Delete document (admin only)."""
    from application.use_cases.documents import DeleteDocumentUseCase

    try:
        doc_repo = ServiceRegistry.get_document_repository()
        vector_store = ServiceRegistry.get_vector_store()

        use_case = DeleteDocumentUseCase(
            document_repository=doc_repo,
            vector_store_service=vector_store,
        )

        result = await use_case.execute(DeleteDocumentInput(document_id=document_id))

        return {
            "success": result.success,
            "vectors_deleted": result.vectors_deleted,
        }

    except DocumentNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
