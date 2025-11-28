"""Document repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from app.domain.entities.document import Document


class IDocumentRepository(ABC):
    """
    Repository interface for Document entity.
    
    Defines contract for document data access.
    """
    
    @abstractmethod
    async def create(self, document: Document) -> Document:
        """
        Create new document.
        
        Args:
            document: Document entity to create
            
        Returns:
            Created document with generated ID
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, document_id: str) -> Optional[Document]:
        """
        Get document by ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            Document entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def update(self, document: Document) -> Document:
        """
        Update existing document.
        
        Args:
            document: Document entity with updated data
            
        Returns:
            Updated document
        """
        pass
    
    @abstractmethod
    async def delete(self, document_id: str) -> bool:
        """
        Delete document (hard delete).
        
        Args:
            document_id: Document ID
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def list_documents(
        self,
        skip: int = 0,
        limit: int = 100,
        collection: Optional[str] = None,
        is_active: Optional[bool] = None,
        created_by: Optional[str] = None,
    ) -> List[Document]:
        """
        List documents with filters and pagination.
        
        Args:
            skip: Number to skip
            limit: Maximum to return
            collection: Filter by collection
            is_active: Filter by active status
            created_by: Filter by creator user ID
            
        Returns:
            List of documents
        """
        pass
    
    @abstractmethod
    async def count(
        self,
        collection: Optional[str] = None,
        is_active: Optional[bool] = None,
        created_by: Optional[str] = None,
    ) -> int:
        """
        Count documents with filters.
        
        Args:
            collection: Filter by collection
            is_active: Filter by active status
            created_by: Filter by creator
            
        Returns:
            Total count
        """
        pass
    
    @abstractmethod
    async def get_by_collection(self, collection: str) -> List[Document]:
        """
        Get all documents in a collection.
        
        Args:
            collection: Collection name
            
        Returns:
            List of documents in collection
        """
        pass
    
    @abstractmethod
    async def search_by_metadata(
        self,
        metadata_filter: Dict[str, Any],
        collection: Optional[str] = None,
    ) -> List[Document]:
        """
        Search documents by metadata.
        
        Args:
            metadata_filter: Metadata filter criteria
            collection: Optional collection filter
            
        Returns:
            Matching documents
        """
        pass
    
    @abstractmethod
    async def exists(self, document_id: str) -> bool:
        """
        Check if document exists.
        
        Args:
            document_id: Document ID
            
        Returns:
            True if exists, False otherwise
        """
        pass
