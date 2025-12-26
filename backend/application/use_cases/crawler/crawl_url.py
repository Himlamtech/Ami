"""Crawl single URL use case."""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

from app.application.interfaces.processors.web_crawler import IWebCrawler
from app.application.interfaces.processors.document_processor import IDocumentProcessor
from app.application.interfaces.services.embedding_service import IEmbeddingService
from app.application.interfaces.services.vector_store_service import IVectorStoreService
from app.application.interfaces.repositories.document_repository import (
    IDocumentRepository,
)


@dataclass
class CrawlURLInput:
    """Input for crawl URL use case."""

    url: str
    collection: str = "default"

    # Crawl options
    formats: List[str] = field(default_factory=lambda: ["markdown"])
    timeout_ms: int = 30000

    # Processing options
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # Metadata
    source_name: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class CrawlURLOutput:
    """Output from crawl URL use case."""

    success: bool
    url: str
    document_id: Optional[str] = None
    chunks_created: int = 0

    # Content info
    title: Optional[str] = None
    content_length: int = 0

    # Timing
    crawl_time_ms: float = 0
    process_time_ms: float = 0

    # Errors
    error: Optional[str] = None


class CrawlURLUseCase:
    """
    Use Case: Crawl single URL and index content.

    Pipeline:
    1. Scrape URL content (IWebCrawler)
    2. Process and chunk content (IDocumentProcessor)
    3. Generate embeddings (IEmbeddingService)
    4. Store in vector database (IVectorStoreService)
    5. Save document metadata (IDocumentRepository)

    Single Responsibility: URL → indexed document
    """

    def __init__(
        self,
        web_crawler: IWebCrawler,
        document_processor: IDocumentProcessor,
        embedding_service: IEmbeddingService,
        vector_store: IVectorStoreService,
        document_repository: IDocumentRepository,
    ):
        self.crawler = web_crawler
        self.processor = document_processor
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.document_repo = document_repository

    async def execute(self, input_data: CrawlURLInput) -> CrawlURLOutput:
        """
        Crawl URL and index content.

        Args:
            input_data: URL and processing options

        Returns:
            CrawlURLOutput with results
        """
        start_time = datetime.now()

        try:
            # 1. Scrape URL
            crawl_start = datetime.now()
            scrape_result = await self.crawler.scrape_url(
                url=input_data.url,
                formats=input_data.formats,
                timeout=input_data.timeout_ms,
            )
            crawl_time = (datetime.now() - crawl_start).total_seconds() * 1000

            if not scrape_result.get("success", False):
                return CrawlURLOutput(
                    success=False,
                    url=input_data.url,
                    error=scrape_result.get("error", "Failed to crawl URL"),
                    crawl_time_ms=crawl_time,
                )

            content = scrape_result.get("content", "")
            metadata = scrape_result.get("metadata", {})
            title = metadata.get("title", input_data.url)

            if not content:
                return CrawlURLOutput(
                    success=False,
                    url=input_data.url,
                    error="No content extracted from URL",
                    crawl_time_ms=crawl_time,
                )

            # 2. Process and chunk content
            process_start = datetime.now()
            chunks = await self.processor.process_text(
                text=content,
                chunk_size=input_data.chunk_size,
                chunk_overlap=input_data.chunk_overlap,
                metadata={
                    "source_url": input_data.url,
                    "title": title,
                    "source_name": input_data.source_name or title,
                    "category": input_data.category,
                    "tags": input_data.tags,
                    "crawled_at": datetime.now().isoformat(),
                },
            )

            if not chunks:
                return CrawlURLOutput(
                    success=False,
                    url=input_data.url,
                    title=title,
                    content_length=len(content),
                    error="No chunks created from content",
                    crawl_time_ms=crawl_time,
                )

            # 3. Generate embeddings
            texts = [chunk["text"] for chunk in chunks]
            embeddings = await self.embedding_service.embed_batch(texts)

            # 4. Store in vector database
            ids = await self.vector_store.upsert(
                collection=input_data.collection,
                embeddings=embeddings,
                documents=texts,
                metadatas=[chunk.get("metadata", {}) for chunk in chunks],
            )

            # 5. Save document metadata
            doc_id = await self.document_repo.create(
                {
                    "url": input_data.url,
                    "title": title,
                    "collection": input_data.collection,
                    "chunk_ids": ids,
                    "chunks_count": len(chunks),
                    "content_length": len(content),
                    "source_name": input_data.source_name,
                    "category": input_data.category,
                    "tags": input_data.tags,
                    "crawled_at": datetime.now(),
                }
            )

            process_time = (datetime.now() - process_start).total_seconds() * 1000

            return CrawlURLOutput(
                success=True,
                url=input_data.url,
                document_id=doc_id,
                chunks_created=len(chunks),
                title=title,
                content_length=len(content),
                crawl_time_ms=crawl_time,
                process_time_ms=process_time,
            )

        except Exception as e:
            total_time = (datetime.now() - start_time).total_seconds() * 1000
            return CrawlURLOutput(
                success=False,
                url=input_data.url,
                error=str(e),
                crawl_time_ms=total_time,
            )
