"""File upload service - Handle file uploads."""

from typing import Optional
from datetime import datetime
from app.domain.entities.file_metadata import FileMetadata
from app.domain.enums.file_type import FileType
from app.application.interfaces.repositories.file_repository import IFileRepository
from app.application.interfaces.services.storage_service import IStorageService


class FileUploadService:
    """
    File upload service for handling file operations.

    Orchestrates file upload, storage, and metadata management.
    """

    def __init__(
        self,
        file_repository: IFileRepository,
        storage_service: IStorageService,
    ):
        self.file_repo = file_repository
        self.storage = storage_service

    async def upload_file(
        self,
        user_id: str,
        file_bytes: bytes,
        filename: str,
        mime_type: str,
        file_type: FileType = FileType.UPLOADED,
        session_id: Optional[str] = None,
    ) -> FileMetadata:
        """
        Upload file and create metadata.

        Workflow:
        1. Upload to storage (MinIO/S3)
        2. Create metadata record
        3. Return file metadata
        """
        # Upload to storage
        url = await self.storage.upload_file(
            file_data=file_bytes,
            filename=filename,
            content_type=mime_type,
            path_prefix=f"uploads/{user_id}/",
        )

        # Create metadata
        file_metadata = FileMetadata(
            id="",
            user_id=user_id,
            filename=filename,
            original_name=filename,
            mime_type=mime_type,
            size=len(file_bytes),
            url=url,
            file_type=file_type,
            session_id=session_id,
            status="processed",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Save metadata
        created_file = await self.file_repo.create(file_metadata)

        return created_file

    async def delete_file(self, file_id: str) -> bool:
        """
        Delete file and its metadata.

        Returns True if deleted successfully.
        """
        # Get metadata
        file_metadata = await self.file_repo.get_by_id(file_id)
        if not file_metadata:
            return False

        # Delete from storage
        # Extract object name from URL
        # Simplified: assumes URL format like "http://minio/bucket/path/file.ext"
        object_name = file_metadata.url.split("/")[-1] if file_metadata.url else ""

        if object_name:
            try:
                await self.storage.delete_file(object_name)
            except:
                pass  # Continue even if storage deletion fails

        # Delete metadata
        await self.file_repo.delete(file_id)

        return True

    async def get_user_storage_usage(self, user_id: str) -> dict:
        """Get storage usage statistics for user."""
        total_size = await self.file_repo.get_total_size_by_user(user_id)
        file_count = await self.file_repo.count_by_user(user_id)

        return {
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "file_count": file_count,
            "avg_file_size_mb": (
                (total_size / file_count / (1024 * 1024)) if file_count > 0 else 0
            ),
        }

    async def cleanup_orphaned_files(self, user_id: str) -> int:
        """
        Clean up files not associated with any session.

        Returns number of files deleted.
        """
        files = await self.file_repo.list_by_user(user_id, limit=1000)

        deleted_count = 0
        for file in files:
            # Delete files without session (orphaned)
            if not file.session_id:
                await self.delete_file(file.id)
                deleted_count += 1

        return deleted_count
