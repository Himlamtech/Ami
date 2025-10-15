#!/usr/bin/env python3
"""
Data ingestion script for RAG system.
Ingests markdown files from assets/raw/ into the vector database.
"""
import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.application.factory import ProviderFactory
from app.application.ingestion_service import IngestionService
from app.config.settings import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Main ingestion process."""
    start_time = datetime.now()

    print("\n" + "=" * 70)
    print("📥 RAG SYSTEM DATA INGESTION")
    print("=" * 70 + "\n")

    try:
        # Load data.json
        data_path = Path("assets/data.json")
        if not data_path.exists():
            logger.error(f"Data file not found: {data_path}")
            return

        with open(data_path, "r", encoding="utf-8") as f:
            documents_data = json.load(f)

        logger.info(f"Loaded {len(documents_data)} documents from data.json")

        # Initialize services
        logger.info("Initializing services...")

        embedding_provider = ProviderFactory.get_embedding_provider(
            settings.default_embedding_provider
        )

        vector_store = await ProviderFactory.get_vector_store(
            settings.default_vector_store
        )

        redis_client = await ProviderFactory.get_redis_client()
        postgres_client = await ProviderFactory.get_postgres_client()

        ingestion_service = IngestionService(
            embedding_provider=embedding_provider,
            vector_store=vector_store,
            redis_client=redis_client,
            postgres_client=postgres_client,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )

        logger.info("✓ Services initialized")
        print(f"\n📊 Configuration:")
        print(f"   - Embedding Provider: {settings.default_embedding_provider}")
        print(f"   - Vector Store: {settings.default_vector_store}")
        print(f"   - Chunk Size: {settings.chunk_size}")
        print(f"   - Chunk Overlap: {settings.chunk_overlap}")
        print(f"   - Collection: ptit_knowledge")
        print()

        # Process each document
        total_docs = len(documents_data)
        successful = 0
        failed = 0
        total_chunks = 0

        for i, doc_data in enumerate(documents_data, 1):
            title = doc_data.get("title", "Untitled")
            file_name = doc_data.get("file_name", "")

            if not file_name:
                logger.warning(f"[{i}/{total_docs}] No file_name in data.json entry")
                failed += 1
                continue

            file_path = Path("assets/raw") / file_name

            if not file_path.exists():
                logger.warning(f"[{i}/{total_docs}] File not found: {file_path}")
                failed += 1
                continue

            print(f"[{i}/{total_docs}] Processing: {title[:60]}...")

            try:
                metadata = {
                    "title": title,
                    "file_name": file_name,
                    "source": doc_data.get("metadata", "Unknown"),
                    "collection": "ptit_knowledge",
                    "doc_id": doc_data.get("id", i),
                }

                result = await ingestion_service.ingest_document(
                    file_path=str(file_path), metadata=metadata
                )

                if result["success"]:
                    successful += 1
                    total_chunks += result["chunk_count"]
                    print(f"         ✅ {result['chunk_count']} chunks ingested")
                else:
                    failed += 1
                    print(f"         ❌ Failed: {result.get('error', 'Unknown error')}")

            except Exception as e:
                failed += 1
                logger.error(f"         ❌ Error: {e}")

        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print("\n" + "=" * 70)
        print("📊 INGESTION SUMMARY")
        print("=" * 70)
        print(f"Total documents processed: {total_docs}")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📦 Total chunks created: {total_chunks}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"⚡ Average: {total_chunks/duration:.2f} chunks/second")
        print("=" * 70 + "\n")

        # Get stats from vector store
        try:
            stats = await vector_store.get_stats(collection="ptit_knowledge")
            print(f"📈 Vector Store Stats:")
            print(f"   - Total documents: {stats.get('total_documents', 0)}")
            print(f"   - Total chunks: {stats.get('total_chunks', 0)}")
            print()
        except Exception as e:
            logger.warning(f"Could not get vector store stats: {e}")

        # Cleanup
        await ProviderFactory.cleanup()
        logger.info("✓ Cleanup complete")

        print("✅ Ingestion complete!\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Ingestion interrupted by user")
        await ProviderFactory.cleanup()
    except Exception as e:
        logger.error(f"Fatal error during ingestion: {e}", exc_info=True)
        await ProviderFactory.cleanup()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
