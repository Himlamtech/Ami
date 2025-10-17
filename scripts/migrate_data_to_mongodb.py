"""
Migration script to import existing documents from data.json and markdown files
into MongoDB and Qdrant vector store.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.application.factory import ProviderFactory
from app.application.services import DocumentService, RAGService


async def migrate_documents():
    """Migrate documents from assets/raw/ to MongoDB and Qdrant."""
    try:
        print("🚀 Starting migration...")
        
        # Get clients and services
        mongodb = await ProviderFactory.get_mongodb_client()
        vector_store = await ProviderFactory.get_vector_store()
        embedding = ProviderFactory.get_embedding_provider()
        llm = ProviderFactory.get_llm_provider()
        cache = await ProviderFactory.get_redis_client()
        processor = ProviderFactory.get_document_processor()
        
        doc_service = DocumentService(processor)
        rag_service = RAGService(embedding, llm, vector_store, doc_service, cache)
        
        # Load existing data.json for metadata (if available)
        data_json_path = project_root / "assets" / "data.json"
        existing_metadata = {}
        if data_json_path.exists():
            print(f"📖 Loading existing metadata from {data_json_path}")
            with open(data_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    # Assuming data.json is a list of document metadata
                    for item in data:
                        if "filename" in item:
                            existing_metadata[item["filename"]] = item
        
        # Get all markdown files from assets/raw/
        raw_dir = project_root / "assets" / "raw"
        if not raw_dir.exists():
            print(f"❌ Directory not found: {raw_dir}")
            return
        
        markdown_files = list(raw_dir.glob("*.md"))
        print(f"📁 Found {len(markdown_files)} markdown files")
        
        if not markdown_files:
            print("⚠️  No markdown files found in assets/raw/")
            return
        
        # Migrate each file
        migrated_count = 0
        skipped_count = 0
        error_count = 0
        
        for md_file in markdown_files:
            try:
                filename = md_file.name
                print(f"\n📄 Processing: {filename}")
                
                # Check if already migrated
                existing_doc = await mongodb.db.documents.find_one({"filename": filename})
                if existing_doc:
                    print(f"   ⏭️  Already migrated, skipping...")
                    skipped_count += 1
                    continue
                
                # Get metadata from data.json if available
                file_metadata = existing_metadata.get(filename, {})
                collection = file_metadata.get("collection", "ptit_docs")
                
                # Prepare metadata
                metadata = {
                    "filename": filename,
                    "collection": collection,
                    "uploaded_by": "migration_script",
                    "source": "assets/raw",
                }
                
                # Ingest file to vector store
                result = await rag_service.ingest_file(str(md_file), metadata)
                
                # Create document record in MongoDB
                doc_data = {
                    "filename": filename,
                    "collection": collection,
                    "file_path": str(md_file),
                    "file_size": md_file.stat().st_size,
                    "mime_type": "text/markdown",
                    "vector_id": result["doc_ids"][0] if result["doc_ids"] else None,
                    "chunk_count": result["chunk_count"],
                    "metadata": metadata,
                    "is_active": True,
                    "uploaded_by": "migration_script",
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                }
                
                doc_id = await mongodb.create_document(doc_data)
                
                # Create vector mappings
                for vector_id in result["doc_ids"]:
                    await mongodb.create_vector_mapping(
                        vector_id=vector_id,
                        document_id=doc_id,
                        collection=collection,
                    )
                
                print(f"   ✅ Migrated successfully!")
                print(f"      - Document ID: {doc_id}")
                print(f"      - Chunks: {result['chunk_count']}")
                print(f"      - Collection: {collection}")
                migrated_count += 1
                
            except Exception as e:
                print(f"   ❌ Error migrating {md_file.name}: {e}")
                error_count += 1
                continue
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 MIGRATION SUMMARY")
        print("=" * 60)
        print(f"✅ Successfully migrated: {migrated_count}")
        print(f"⏭️  Skipped (already exists): {skipped_count}")
        print(f"❌ Errors: {error_count}")
        print(f"📁 Total files processed: {len(markdown_files)}")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
    finally:
        await ProviderFactory.cleanup()


if __name__ == "__main__":
    asyncio.run(migrate_documents())

