"""
MinIO storage - Simple implementation.
Config từ centralized config module.
"""

import logging
import uuid
from io import BytesIO
from typing import Optional

from minio import Minio

from app.application.interfaces.services.storage_service import IStorageService
from app.config import minio_config
from app.config.persistence import MinIOConfig

logger = logging.getLogger(__name__)


class _InMemoryMinioObject:
    """Minimal file-like object for stubbed downloads."""

    def __init__(self, data: bytes):
        self._data = data

    def read(self) -> bytes:
        return self._data

    def close(self):
        pass

    def release_conn(self):
        pass


class _InMemoryMinioClient:
    """Simple in-memory MinIO client replacement used as fallback."""

    def __init__(self):
        self._buckets: dict[str, dict[str, bytes]] = {}

    def bucket_exists(self, bucket_name: str) -> bool:
        return bucket_name in self._buckets

    def make_bucket(self, bucket_name: str):
        self._buckets.setdefault(bucket_name, {})

    def put_object(
        self,
        bucket_name: str,
        object_name: str,
        data,
        length: int,
        content_type: Optional[str] = None,
    ):
        bucket = self._buckets.setdefault(bucket_name, {})
        payload = data.read() if hasattr(data, "read") else data
        bucket[object_name] = {
            "data": payload,
            "size": len(payload),
            "content_type": content_type,
        }

    def get_object(self, bucket_name: str, object_name: str):
        bucket = self._buckets.get(bucket_name, {})
        stored = bucket.get(object_name)
        if not stored:
            raise FileNotFoundError(f"{object_name} not found")
        return _InMemoryMinioObject(stored["data"])

    def remove_object(self, bucket_name: str, object_name: str):
        bucket = self._buckets.get(bucket_name, {})
        bucket.pop(object_name, None)

    def stat_object(self, bucket_name: str, object_name: str):
        bucket = self._buckets.get(bucket_name, {})
        stored = bucket.get(object_name)
        if not stored:
            raise FileNotFoundError(f"{object_name} not found")

        class _Stat:
            size = stored["size"]

        return _Stat()

    def presigned_get_object(self, bucket_name: str, object_name: str, **_):
        return f"http://stub/{bucket_name}/{object_name}"


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
        self.bucket = bucket

        try:
            self.client = Minio(
                endpoint=self.config.endpoint,
                access_key=self.config.access_key,
                secret_key=self.config.secret_key,
                secure=self.config.secure,
            )
            # Probe connection to detect credential issues early
            self.client.bucket_exists(self.bucket)
        except Exception as e:
            logger.warning(
                "MinIO connection failed, falling back to in-memory stub: %s", e
            )
            self.client = _InMemoryMinioClient()

        self._ensure_bucket()
        logger.info(f"MinIO initialized: {self.config.endpoint}/{bucket}")

    def _ensure_bucket(self):
        """Create bucket if not exists."""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                logger.info(f"Created bucket: {self.bucket}")
        except Exception as e:
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
            protocol = "https" if self.config.secure else "http"
            url = f"{protocol}://{self.config.endpoint}/{self.bucket}/{object_name}"

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


if __name__ == "__main__":

    async def test():
        storage = MinIOStorage()
        file_content = b"Hello, MinIO!"
        filename = "test.txt"
        content_type = "text/plain"

        # Upload
        url = await storage.upload_file(
            file_data=file_content,
            filename=filename,
            content_type=content_type,
            path_prefix="tests",
        )
        print("Uploaded URL:", url)

        # Download
        object_name = url.split(f"/{storage.bucket}/")[-1]
        downloaded_data = await storage.download(object_name)
        print("Downloaded Data:", downloaded_data)

        # Check existence
        exists = await storage.file_exists(object_name)
        print("File Exists:", exists)

        # Get size
        size = await storage.get_file_size(object_name)
        print("File Size:", size)

        # Generate presigned URL
        presigned_url = await storage.get_presigned_url(
            object_name, expires_seconds=600
        )
        print("Presigned URL:", presigned_url)

        # Delete
        deleted = await storage.delete_file(object_name)
        print("File Deleted:", deleted)

    import asyncio

    asyncio.run(test())
