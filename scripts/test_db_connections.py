#!/usr/bin/env python3
"""
Test script for database connections.
Verifies PostgreSQL (with pgvector), Redis, and ChromaDB connectivity.
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config.settings import settings
from app.infrastructure.databases.chroma_client import ChromaClient
from app.infrastructure.databases.postgres_client import PostgresClient
from app.infrastructure.databases.redis_client import RedisClient

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_postgres():
    """Test PostgreSQL connection and pgvector."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing PostgreSQL Connection")
    logger.info("=" * 60)

    try:
        client = PostgresClient(
            host=settings.postgres_host,
            port=settings.postgres_port,
            user=settings.postgres_user,
            password=settings.postgres_password,
            database=settings.postgres_db,
            min_pool_size=settings.postgres_min_pool_size,
            max_pool_size=settings.postgres_max_pool_size,
        )

        async with client:
            # Test basic query
            result = await client.fetch_val("SELECT version()")
            logger.info(f"✓ PostgreSQL Version: {result[:50]}...")

            # Verify pgvector
            pgvector_ok = await client.verify_pgvector()
            if pgvector_ok:
                logger.info("✓ pgvector extension is installed and ready")

            # Test tables exist
            tables = await client.fetch_many(
                """
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY tablename
            """
            )
            logger.info(f"✓ Found {len(tables)} tables:")
            for table in tables:
                logger.info(f"  - {table['tablename']}")

            # Test vector operations if embeddings table exists
            if any(t["tablename"] == "embeddings" for t in tables):
                count = await client.fetch_val("SELECT COUNT(*) FROM embeddings")
                logger.info(f"✓ Embeddings table has {count} rows")

        logger.info("✅ PostgreSQL test PASSED\n")
        return True

    except Exception as e:
        logger.error(f"❌ PostgreSQL test FAILED: {e}\n")
        return False


async def test_redis():
    """Test Redis connection."""
    logger.info("=" * 60)
    logger.info("Testing Redis Connection")
    logger.info("=" * 60)

    try:
        client = RedisClient(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            db=settings.redis_db,
            max_connections=settings.redis_max_connections,
        )

        async with client:
            # Test ping
            pong = await client.ping()
            logger.info(f"✓ Redis PING: {pong}")

            # Test basic operations
            test_key = "test:connection"
            test_value = {"status": "connected", "test": True}

            await client.set(test_key, test_value, ttl=10)
            logger.info("✓ SET operation successful")

            retrieved = await client.get(test_key)
            logger.info(f"✓ GET operation successful: {retrieved}")

            exists = await client.exists(test_key)
            logger.info(f"✓ EXISTS check: {exists}")

            ttl = await client.ttl(test_key)
            logger.info(f"✓ TTL: {ttl} seconds")

            await client.delete(test_key)
            logger.info("✓ DELETE operation successful")

            # Test caching methods
            test_text = "This is a test embedding"
            test_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]

            await client.cache_embedding(
                text=test_text,
                embedding=test_embedding,
                provider="test",
                model="test-model",
                ttl=10,
            )
            logger.info("✓ Embedding cache successful")

            cached = await client.get_cached_embedding(
                text=test_text, provider="test", model="test-model"
            )
            logger.info(f"✓ Retrieved cached embedding: {len(cached)} dimensions")

        logger.info("✅ Redis test PASSED\n")
        return True

    except Exception as e:
        logger.error(f"❌ Redis test FAILED: {e}\n")
        return False


async def test_chromadb():
    """Test ChromaDB connection."""
    logger.info("=" * 60)
    logger.info("Testing ChromaDB Connection")
    logger.info("=" * 60)

    try:
        client = ChromaClient(
            host=settings.chroma_host,
            port=settings.chroma_port,
            persist_dir=settings.chroma_persist_dir,
        )

        async with client:
            # Health check
            healthy = await client.health_check()
            logger.info(f"✓ ChromaDB health: {healthy}")

            # Create test collection
            test_collection = "test_collection"
            collection = client.create_collection(
                name=test_collection, get_or_create=True
            )
            logger.info(f"✓ Created/got collection: {test_collection}")

            # Add test documents
            test_ids = ["doc1", "doc2"]
            test_embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
            test_documents = ["Test document 1", "Test document 2"]
            test_metadatas = [
                {"type": "test", "index": 1},
                {"type": "test", "index": 2},
            ]

            success = client.add_documents(
                collection_name=test_collection,
                ids=test_ids,
                embeddings=test_embeddings,
                documents=test_documents,
                metadatas=test_metadatas,
            )
            logger.info(f"✓ Added test documents: {success}")

            # Count documents
            count = client.count_documents(test_collection)
            logger.info(f"✓ Document count: {count}")

            # Query
            results = client.query(
                collection_name=test_collection,
                query_embeddings=[[0.15, 0.25, 0.35]],
                n_results=2,
            )
            logger.info(f"✓ Query returned {len(results['ids'][0])} results")

            # List collections
            collections = client.list_collections()
            logger.info(f"✓ Total collections: {len(collections)}")

            # Cleanup
            client.delete_collection(test_collection)
            logger.info(f"✓ Cleaned up test collection")

        logger.info("✅ ChromaDB test PASSED\n")
        return True

    except Exception as e:
        logger.error(f"❌ ChromaDB test FAILED: {e}\n")
        return False


async def main():
    """Run all database connection tests."""
    logger.info("\n" + "🔍 DATABASE CONNECTION TESTS 🔍".center(60))
    logger.info("=" * 60 + "\n")

    results = {
        "PostgreSQL": await test_postgres(),
        "Redis": await test_redis(),
        "ChromaDB": await test_chromadb(),
    }

    # Summary
    logger.info("=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)

    passed = sum(results.values())
    total = len(results)

    for db, status in results.items():
        status_icon = "✅" if status else "❌"
        logger.info(f"{status_icon} {db}: {'PASSED' if status else 'FAILED'}")

    logger.info("=" * 60)
    logger.info(f"Result: {passed}/{total} tests passed")
    logger.info("=" * 60 + "\n")

    if passed == total:
        logger.info("🎉 All database connections are working!")
        sys.exit(0)
    else:
        logger.error("⚠️  Some database connections failed. Please check configuration.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
