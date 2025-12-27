"""List documents use case."""

from dataclasses import dataclass
from typing import List, Optional
from domain.entities.document import Document
from application.interfaces.repositories.document_repository import (
    IDocumentRepository,
)


@dataclass
class ListDocumentsInput:
    """Input for list documents use case."""

    skip: int = 0
    limit: int = 100
    collection: Optional[str] = None
    is_active: Optional[bool] = True
    created_by: Optional[str] = None


@dataclass
class ListDocumentsOutput:
    """Output from list documents use case."""

    documents: List[Document]
    total: int
    skip: int
    limit: int


class ListDocumentsUseCase:
    """
    Use Case: List documents with filters and pagination.

    Business Rules:
    1. Support pagination
    2. Filter by collection, status, owner
    3. Return total count

    Single Responsibility: Document listing
    """

    def __init__(self, document_repository: IDocumentRepository):
        self.doc_repo = document_repository

    async def execute(self, input_data: ListDocumentsInput) -> ListDocumentsOutput:
        """
        List documents.

        Args:
            input_data: List parameters

        Returns:
            ListDocumentsOutput with documents and total count
        """
        # Get documents
        documents = await self.doc_repo.list_documents(
            skip=input_data.skip,
            limit=input_data.limit,
            collection=input_data.collection,
            is_active=input_data.is_active,
            created_by=input_data.created_by,
        )

        # Get total count
        total = await self.doc_repo.count(
            collection=input_data.collection,
            is_active=input_data.is_active,
            created_by=input_data.created_by,
        )

        return ListDocumentsOutput(
            documents=documents,
            total=total,
            skip=input_data.skip,
            limit=input_data.limit,
        )
