"""
MinIO storage - Simple implementation.
Config từ centralized config module.
"""

import logging
import uuid
from io import BytesIO
from typing import Optional

from minio import Minio
from minio.error import S3Error

from app.application.interfaces.services.storage_service import IStorageService
from app.config import minio_config
from app.config.persistence import MinIOConfig

logger = logging.getLogger(__name__)


class MinIOStorage(IStorageService):
    """MinIO storage for file uploads."""

    def __init__(self, config: MinIOConfig = None, bucket: str = "ami-uploads"):
        """
        Initialize MinIO storage.
        
        Args:
            config: MinIO configuration. If None, uses global minio_config.
            bucket: Default bucket name.
        """
        self.config = config or minio_config
        self.client = Minio(
            endpoint=self.config.endpoint,
            access_key=self.config.access_key,
            secret_key=self.config.secret_key,
            secure=self.config.secure,
        )
        self.bucket = bucket
        self._ensure_bucket()
        logger.info(f"MinIO initialized: {self.config.endpoint}/{bucket}")

    def _ensure_bucket(self):
        """Create bucket if not exists."""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                logger.info(f"Created bucket: {self.bucket}")
        except S3Error as e:
            logger.error(f"Bucket error: {e}")

    async def upload_file(
        self,
        file_data: bytes,
        filename: str,
        content_type: str,
        path_prefix: Optional[str] = None,
    ) -> str:
        """
        Upload file to MinIO.
        
        Returns: URL to uploaded file
        """
        try:
            # Generate unique filename
            unique_id = uuid.uuid4().hex[:12]
            unique_filename = f"{unique_id}_{filename}"
            
            # Build path
            if path_prefix:
                object_name = f"{path_prefix.strip('/')}/{unique_filename}"
            else:
                object_name = unique_filename

            # Upload
            self.client.put_object(
                bucket_name=self.bucket,
                object_name=object_name,
                data=BytesIO(file_data),
                length=len(file_data),
                content_type=content_type,
            )

            # Return URL
            protocol = "https" if self.settings.minio_secure else "http"
            url = f"{protocol}://{self.settings.minio_endpoint}/{self.bucket}/{object_name}"
            
            logger.info(f"Uploaded: {object_name} ({len(file_data)} bytes)")
            return url

        except Exception as e:
            logger.error(f"Upload failed: {e}")
            raise RuntimeError(f"Upload failed: {str(e)}")

    async def download(self, object_name: str) -> Optional[bytes]:
        """Download file from MinIO."""
        try:
            response = self.client.get_object(self.bucket, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return None

    async def delete_file(self, object_name: str) -> bool:
        """Delete file from MinIO."""
        try:
            self.client.remove_object(self.bucket, object_name)
            logger.info(f"Deleted: {object_name}")
            return True
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return False

    async def file_exists(self, object_name: str) -> bool:
        """Check if file exists."""
        try:
            self.client.stat_object(self.bucket, object_name)
            return True
        except:
            return False

    async def get_file_size(self, object_name: str) -> Optional[int]:
        """Get file size in bytes."""
        try:
            stat = self.client.stat_object(self.bucket, object_name)
            return stat.size
        except Exception as e:
            logger.error(f"Get file size failed: {e}")
            return None

    async def get_presigned_url(
        self,
        object_name: str,
        expires_seconds: int = 3600,
    ) -> str:
        """
        Generate pre-signed URL for file download.
        
        Args:
            object_name: Object key/path
            expires_seconds: URL expiration time in seconds
            
        Returns:
            Pre-signed URL string
        """
        from datetime import timedelta
        
        try:
            url = self.client.presigned_get_object(
                bucket_name=self.bucket,
                object_name=object_name,
                expires=timedelta(seconds=expires_seconds),
            )
            return url
        except Exception as e:
            logger.error(f"Generate presigned URL failed: {e}")
            raise RuntimeError(f"Generate presigned URL failed: {str(e)}")
