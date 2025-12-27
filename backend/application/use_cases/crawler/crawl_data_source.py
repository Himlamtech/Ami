"""Crawl data source use case."""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

from application.interfaces.processors.web_crawler import IWebCrawler
from application.interfaces.processors.document_processor import IDocumentProcessor
from application.interfaces.services.embedding_service import IEmbeddingService
from application.interfaces.services.vector_store_service import IVectorStoreService
from application.interfaces.repositories.data_source_repository import (
    IDataSourceRepository,
)
from application.interfaces.repositories.document_repository import (
    IDocumentRepository,
)


@dataclass
class CrawlDataSourceInput:
    """Input for crawl data source use case."""

    data_source_id: str

    # Override options (optional, uses data source config if not provided)
    max_pages: Optional[int] = None
    max_depth: Optional[int] = None

    # Force crawl even if recently crawled
    force: bool = False


@dataclass
class CrawlResult:
    """Result for single page crawl."""

    url: str
    success: bool
    chunks_created: int = 0
    error: Optional[str] = None


@dataclass
class CrawlDataSourceOutput:
    """Output from crawl data source use case."""

    success: bool
    data_source_id: str
    data_source_name: str

    # Statistics
    pages_crawled: int = 0
    pages_success: int = 0
    pages_failed: int = 0
    total_chunks: int = 0

    # Details
    results: List[CrawlResult] = field(default_factory=list)

    # Timing
    duration_seconds: float = 0

    # Error (if entire job failed)
    error: Optional[str] = None


class CrawlDataSourceUseCase:
    """
    Use Case: Crawl all URLs from a configured data source.

    Pipeline:
    1. Load data source configuration
    2. Crawl website based on config (sitemap, links, or specific URLs)
    3. Process and index each page
    4. Update data source statistics

    Single Responsibility: Data source → indexed documents
    """

    def __init__(
        self,
        web_crawler: IWebCrawler,
        document_processor: IDocumentProcessor,
        embedding_service: IEmbeddingService,
        vector_store: IVectorStoreService,
        data_source_repo: IDataSourceRepository,
        document_repo: IDocumentRepository,
    ):
        self.crawler = web_crawler
        self.processor = document_processor
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.data_source_repo = data_source_repo
        self.document_repo = document_repo

    async def execute(self, input_data: CrawlDataSourceInput) -> CrawlDataSourceOutput:
        """
        Crawl data source and index all content.

        Args:
            input_data: Data source ID and options

        Returns:
            CrawlDataSourceOutput with results
        """
        start_time = datetime.now()

        # 1. Load data source
        data_source = await self.data_source_repo.get_by_id(input_data.data_source_id)
        if not data_source:
            return CrawlDataSourceOutput(
                success=False,
                data_source_id=input_data.data_source_id,
                data_source_name="Unknown",
                error="Data source not found",
            )

        # Check if active
        if not data_source.is_active:
            return CrawlDataSourceOutput(
                success=False,
                data_source_id=data_source.id,
                data_source_name=data_source.name,
                error="Data source is not active",
            )

        try:
            # 2. Crawl website
            max_depth = input_data.max_depth or data_source.crawl_config.get(
                "max_depth", 2
            )
            max_pages = input_data.max_pages or data_source.crawl_config.get(
                "max_pages", 50
            )

            pages = await self.crawler.crawl_website(
                url=data_source.base_url,
                max_depth=max_depth,
                limit=max_pages,
            )

            # 3. Process each page
            results: List[CrawlResult] = []
            total_chunks = 0

            for page in pages:
                page_url = page.get("url", "")
                content = page.get("content", "")

                if not content:
                    results.append(
                        CrawlResult(
                            url=page_url,
                            success=False,
                            error="No content",
                        )
                    )
                    continue

                try:
                    # Process and chunk
                    chunks = await self.processor.process_text(
                        text=content,
                        chunk_size=data_source.crawl_config.get("chunk_size", 1000),
                        chunk_overlap=data_source.crawl_config.get(
                            "chunk_overlap", 200
                        ),
                        metadata={
                            "source_url": page_url,
                            "source_id": data_source.id,
                            "source_name": data_source.name,
                            "category": (
                                data_source.category.value
                                if data_source.category
                                else None
                            ),
                            "crawled_at": datetime.now().isoformat(),
                        },
                    )

                    if chunks:
                        # Embed and store
                        texts = [c["text"] for c in chunks]
                        embeddings = await self.embedding_service.embed_batch(texts)

                        await self.vector_store.upsert(
                            collection=data_source.collection or "default",
                            embeddings=embeddings,
                            documents=texts,
                            metadatas=[c.get("metadata", {}) for c in chunks],
                        )

                        total_chunks += len(chunks)
                        results.append(
                            CrawlResult(
                                url=page_url,
                                success=True,
                                chunks_created=len(chunks),
                            )
                        )
                    else:
                        results.append(
                            CrawlResult(
                                url=page_url,
                                success=False,
                                error="No chunks created",
                            )
                        )

                except Exception as e:
                    results.append(
                        CrawlResult(
                            url=page_url,
                            success=False,
                            error=str(e),
                        )
                    )

            # 4. Update data source statistics
            pages_success = sum(1 for r in results if r.success)
            pages_failed = sum(1 for r in results if not r.success)

            await self.data_source_repo.update_crawl_stats(
                source_id=data_source.id,
                success=pages_success > 0,
                docs_count=total_chunks,
            )

            duration = (datetime.now() - start_time).total_seconds()

            return CrawlDataSourceOutput(
                success=True,
                data_source_id=data_source.id,
                data_source_name=data_source.name,
                pages_crawled=len(pages),
                pages_success=pages_success,
                pages_failed=pages_failed,
                total_chunks=total_chunks,
                results=results,
                duration_seconds=duration,
            )

        except Exception as e:
            # Update stats with failure
            await self.data_source_repo.update_crawl_stats(
                source_id=data_source.id,
                success=False,
                error=str(e),
            )

            duration = (datetime.now() - start_time).total_seconds()

            return CrawlDataSourceOutput(
                success=False,
                data_source_id=data_source.id,
                data_source_name=data_source.name,
                error=str(e),
                duration_seconds=duration,
            )
