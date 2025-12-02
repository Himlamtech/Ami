"""Change detector use case for content change tracking."""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
import hashlib
import logging

from app.application.interfaces.repositories.document_repository import IDocumentRepository

logger = logging.getLogger(__name__)


@dataclass
class ChangeDetectionResult:
    """Result from change detection."""
    is_new: bool = False
    is_modified: bool = False
    is_unchanged: bool = False
    previous_hash: Optional[str] = None
    current_hash: Optional[str] = None
    document_id: Optional[str] = None


class ChangeDetectorUseCase:
    """
    Use Case: Detect content changes using content hashing.
    
    Business Rules:
    1. New content: no existing document with matching source_url
    2. Modified: same source_url but different content hash
    3. Unchanged: same source_url and same content hash
    4. Uses SHA-256 for reliable hash comparison
    
    Single Responsibility: Content change detection
    """
    
    def __init__(self, document_repository: IDocumentRepository):
        self.document_repo = document_repository
    
    async def detect_change(
        self,
        content: str,
        source_url: str,
        data_source_id: str,
    ) -> ChangeDetectionResult:
        """
        Detect if content has changed.
        
        Args:
            content: The content to check
            source_url: URL/path identifying the content
            data_source_id: ID of the data source
            
        Returns:
            ChangeDetectionResult with detection info
        """
        # 1. Compute current content hash
        current_hash = self._compute_hash(content)
        
        # 2. Find existing document by source_url
        existing_docs = await self.document_repo.search_by_metadata(
            metadata_filter={
                "source_url": source_url,
                "data_source_id": data_source_id,
            }
        )
        
        if not existing_docs:
            # New content
            return ChangeDetectionResult(
                is_new=True,
                current_hash=current_hash,
            )
        
        # 3. Compare hashes
        existing_doc = existing_docs[0]
        previous_hash = existing_doc.metadata.get("content_hash")
        
        if previous_hash == current_hash:
            # Unchanged
            return ChangeDetectionResult(
                is_unchanged=True,
                previous_hash=previous_hash,
                current_hash=current_hash,
                document_id=existing_doc.id,
            )
        
        # Modified
        return ChangeDetectionResult(
            is_modified=True,
            previous_hash=previous_hash,
            current_hash=current_hash,
            document_id=existing_doc.id,
        )
    
    async def batch_detect_changes(
        self,
        items: list[Dict[str, Any]],
        data_source_id: str,
    ) -> Dict[str, list]:
        """
        Batch detect changes for multiple items.
        
        Args:
            items: List of {"content": str, "source_url": str}
            data_source_id: ID of the data source
            
        Returns:
            Dict with lists of new, modified, unchanged items
        """
        results = {
            "new": [],
            "modified": [],
            "unchanged": [],
        }
        
        for item in items:
            result = await self.detect_change(
                content=item["content"],
                source_url=item["source_url"],
                data_source_id=data_source_id,
            )
            
            if result.is_new:
                results["new"].append({**item, "hash": result.current_hash})
            elif result.is_modified:
                results["modified"].append({
                    **item,
                    "hash": result.current_hash,
                    "document_id": result.document_id,
                })
            else:
                results["unchanged"].append({
                    **item,
                    "document_id": result.document_id,
                })
        
        return results
    
    async def detect_deletions(
        self,
        current_urls: list[str],
        data_source_id: str,
    ) -> list[str]:
        """
        Detect documents that have been deleted from source.
        
        Args:
            current_urls: List of URLs currently in source
            data_source_id: ID of the data source
            
        Returns:
            List of document IDs that should be deleted
        """
        # Get all documents for this data source
        all_docs = await self.document_repo.search_by_metadata(
            metadata_filter={"data_source_id": data_source_id}
        )
        
        deleted_doc_ids = []
        current_urls_set = set(current_urls)
        
        for doc in all_docs:
            source_url = doc.metadata.get("source_url")
            if source_url and source_url not in current_urls_set:
                deleted_doc_ids.append(doc.id)
        
        return deleted_doc_ids
    
    def _compute_hash(self, content: str) -> str:
        """Compute SHA-256 hash of content."""
        # Normalize content (strip whitespace, lowercase for comparison)
        normalized = content.strip()
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
    
    @staticmethod
    def compute_content_hash(content: str) -> str:
        """Static method to compute hash (for use elsewhere)."""
        normalized = content.strip()
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
