"""Delete document use case."""

from dataclasses import dataclass
from domain.exceptions.document_exceptions import DocumentNotFoundException
from application.interfaces.repositories.document_repository import (
    IDocumentRepository,
)
from application.interfaces.services.vector_store_service import IVectorStoreService


@dataclass
class DeleteDocumentInput:
    """Input for delete document use case."""

    document_id: str


@dataclass
class DeleteDocumentOutput:
    """Output from delete document use case."""

    success: bool
    vectors_deleted: int


class DeleteDocumentUseCase:
    """
    Use Case: Delete document and its vectors.

    Business Rules:
    1. Document must exist
    2. Delete vectors from vector database
    3. Delete document metadata

    Single Responsibility: Document deletion workflow
    """

    def __init__(
        self,
        document_repository: IDocumentRepository,
        vector_store_service: IVectorStoreService,
    ):
        self.doc_repo = document_repository
        self.vector_store = vector_store_service

    async def execute(self, input_data: DeleteDocumentInput) -> DeleteDocumentOutput:
        """
        Delete document.

        Args:
            input_data: Delete parameters

        Returns:
            DeleteDocumentOutput with deletion results

        Raises:
            DocumentNotFoundException: Document doesn't exist
        """
        # 1. Get document
        document = await self.doc_repo.get_by_id(input_data.document_id)
        if not document:
            raise DocumentNotFoundException(document_id=input_data.document_id)

        # 2. Delete vectors from vector store
        vectors_deleted = 0
        if document.vector_ids:
            await self.vector_store.delete(document.vector_ids)
            vectors_deleted = len(document.vector_ids)

        # 3. Delete document
        await self.doc_repo.delete(input_data.document_id)

        return DeleteDocumentOutput(
            success=True,
            vectors_deleted=vectors_deleted,
        )
