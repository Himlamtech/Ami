"""Document management use cases."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from app.application.interfaces.services.vector_store_service import IVectorStoreService


# ===== Scroll Documents =====
@dataclass
class ScrollDocumentsInput:
    collection_name: Optional[str] = None
    limit: int = 20
    offset: Optional[str] = None
    with_payload: bool = True
    with_vectors: bool = False


@dataclass
class ScrollDocumentsOutput:
    documents: List[Dict[str, Any]]
    next_offset: Optional[str]
    total: int


class ScrollDocumentsUseCase:
    """Scroll through documents with pagination."""

    def __init__(self, vector_store: IVectorStoreService):
        self.vector_store = vector_store

    def execute(self, input_data: ScrollDocumentsInput) -> ScrollDocumentsOutput:
        documents, next_offset = self.vector_store.scroll(
            collection=input_data.collection_name,
            limit=input_data.limit,
            offset=input_data.offset,
        )

        return ScrollDocumentsOutput(
            documents=documents,
            next_offset=str(next_offset) if next_offset else None,
            total=len(documents),
        )


# ===== Get Document =====
@dataclass
class GetDocumentInput:
    document_id: str
    collection_name: Optional[str] = None


@dataclass
class GetDocumentOutput:
    found: bool
    document: Optional[Dict[str, Any]]


class GetDocumentUseCase:
    """Get a specific document by ID."""

    def __init__(self, vector_store: IVectorStoreService):
        self.vector_store = vector_store

    def execute(self, input_data: GetDocumentInput) -> GetDocumentOutput:
        document = self.vector_store.get_by_id(
            point_id=input_data.document_id, collection=input_data.collection_name
        )

        return GetDocumentOutput(found=document is not None, document=document)


# ===== Update Document Metadata =====
@dataclass
class UpdateDocumentMetadataInput:
    document_id: str
    metadata: Dict[str, Any]
    collection_name: Optional[str] = None


@dataclass
class UpdateDocumentMetadataOutput:
    success: bool
    document_id: str
    message: str


class UpdateDocumentMetadataUseCase:
    """Update document metadata."""

    def __init__(self, vector_store: IVectorStoreService):
        self.vector_store = vector_store

    def execute(
        self, input_data: UpdateDocumentMetadataInput
    ) -> UpdateDocumentMetadataOutput:
        # Check if document exists
        existing = self.vector_store.get_by_id(
            point_id=input_data.document_id, collection=input_data.collection_name
        )

        if not existing:
            return UpdateDocumentMetadataOutput(
                success=False,
                document_id=input_data.document_id,
                message="Document not found",
            )

        success = self.vector_store.update_metadata(
            point_id=input_data.document_id,
            metadata=input_data.metadata,
            collection=input_data.collection_name,
        )

        return UpdateDocumentMetadataOutput(
            success=success,
            document_id=input_data.document_id,
            message=(
                "Metadata updated successfully"
                if success
                else "Failed to update metadata"
            ),
        )


# ===== Delete Documents by Filter =====
@dataclass
class DeleteDocumentsByFilterInput:
    filter_conditions: Dict[str, Any]
    collection_name: Optional[str] = None


@dataclass
class DeleteDocumentsByFilterOutput:
    success: bool
    deleted_count: int
    message: str


class DeleteDocumentsByFilterUseCase:
    """Delete documents matching filter conditions."""

    def __init__(self, vector_store: IVectorStoreService):
        self.vector_store = vector_store

    def execute(
        self, input_data: DeleteDocumentsByFilterInput
    ) -> DeleteDocumentsByFilterOutput:
        success = self.vector_store.delete_by_filter(
            metadata_filter=input_data.filter_conditions,
            collection=input_data.collection_name,
        )

        return DeleteDocumentsByFilterOutput(
            success=success,
            deleted_count=0,  # Qdrant doesn't return count
            message="Delete completed" if success else "Delete failed",
        )
