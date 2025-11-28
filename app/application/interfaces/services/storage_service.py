"""Storage service interface."""

from abc import ABC, abstractmethod
from typing import Optional


class IStorageService(ABC):
    """
    Interface for file storage providers (S3, MinIO, etc.).
    
    Renamed from IStorageProvider for consistency.
    """
    
    @abstractmethod
    async def upload_file(
        self,
        file_data: bytes,
        filename: str,
        content_type: str,
        path_prefix: Optional[str] = None,
    ) -> str:
        """
        Upload file and return URL.
        
        Args:
            file_data: File bytes
            filename: Filename
            content_type: MIME type
            path_prefix: Optional path prefix (e.g., "avatars/", "uploads/")
            
        Returns:
            Public URL to uploaded file
        """
        pass
    
    @abstractmethod
    async def get_presigned_url(
        self,
        object_name: str,
        expires_seconds: int = 3600
    ) -> str:
        """
        Get temporary signed URL for private file access.
        
        Args:
            object_name: Object key/name in storage
            expires_seconds: URL expiration time
            
        Returns:
            Presigned URL
        """
        pass
    
    @abstractmethod
    async def delete_file(self, object_name: str) -> bool:
        """
        Delete file from storage.
        
        Args:
            object_name: Object key/name
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def file_exists(self, object_name: str) -> bool:
        """
        Check if file exists.
        
        Args:
            object_name: Object key/name
            
        Returns:
            True if exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_file_size(self, object_name: str) -> Optional[int]:
        """
        Get file size in bytes.
        
        Args:
            object_name: Object key/name
            
        Returns:
            File size in bytes, None if not found
        """
        pass
