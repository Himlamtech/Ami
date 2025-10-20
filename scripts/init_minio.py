"""
MinIO Initialization Script
Creates buckets and sets up initial configuration.
Run with: python scripts/init_minio.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.infrastructure.storage.minio_storage import MinIOStorage
from app.config.settings import settings

async def init_minio():
    """Initialize MinIO storage."""
    print("\n" + "="*60)
    print("MinIO Initialization")
    print("="*60)
    
    try:
        # Initialize MinIO client
        print(f"\n📦 Connecting to MinIO...")
        print(f"   Endpoint: {settings.minio_endpoint}")
        print(f"   Bucket: {settings.minio_bucket}")
        
        storage = MinIOStorage(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            bucket=settings.minio_bucket,
            secure=settings.minio_secure,
        )
        
        print(f"✅ Connected to MinIO successfully!")
        
        # Health check
        print(f"\n🔍 Performing health check...")
        health = await storage.health_check()
        
        if health["status"] == "healthy":
            print(f"✅ MinIO is healthy")
            print(f"   Bucket exists: {health.get('bucket_exists')}")
            print(f"   Can list objects: {health.get('can_list')}")
        else:
            print(f"❌ MinIO is unhealthy: {health.get('error')}")
            return False
        
        # Get bucket stats
        print(f"\n📊 Bucket Statistics:")
        stats = await storage.get_bucket_stats()
        print(f"   Bucket: {stats['bucket']}")
        print(f"   Total files: {stats['total_files']}")
        print(f"   Total size: {stats['total_size_formatted']}")
        
        # Upload test file
        print(f"\n🧪 Testing file upload...")
        test_content = b"MinIO Test File - This is a test upload from init script."
        test_filename = "test_init.txt"
        
        url = await storage.upload_file(
            file_data=test_content,
            filename=test_filename,
            content_type="text/plain",
            path_prefix="test"
        )
        
        print(f"✅ Test file uploaded successfully!")
        print(f"   URL: {url}")
        
        # Verify file exists
        object_name = storage.get_object_name_from_url(url)
        if object_name:
            exists = await storage.file_exists(object_name)
            print(f"   File exists: {exists}")
            
            # Get file info
            info = await storage.get_file_info(object_name)
            if info:
                print(f"   Size: {info['size']} bytes")
                print(f"   Content Type: {info['content_type']}")
        
        # Clean up test file
        print(f"\n🧹 Cleaning up test file...")
        if object_name:
            deleted = await storage.delete_file(object_name)
            if deleted:
                print(f"✅ Test file deleted successfully")
        
        print("\n" + "="*60)
        print("✅ MinIO initialization completed successfully!")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ MinIO initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(init_minio())
    sys.exit(0 if success else 1)



