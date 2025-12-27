"""Batch crawl multiple URLs use case."""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import asyncio

from application.use_cases.crawler.crawl_url import (
    CrawlURLUseCase,
    CrawlURLInput,
    CrawlURLOutput,
)


@dataclass
class BatchCrawlInput:
    """Input for batch crawl use case."""

    urls: List[str]
    collection: str = "default"

    # Processing options
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # Concurrency
    max_concurrent: int = 5

    # Metadata
    source_name: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class BatchCrawlOutput:
    """Output from batch crawl use case."""

    total_urls: int
    success_count: int
    failed_count: int
    total_chunks: int

    # Details
    results: List[CrawlURLOutput] = field(default_factory=list)

    # Timing
    duration_seconds: float = 0


class BatchCrawlUseCase:
    """
    Use Case: Crawl multiple URLs concurrently.

    Uses CrawlURLUseCase for each URL with concurrency control.

    Single Responsibility: Batch URL crawling with parallelism
    """

    def __init__(self, crawl_url_use_case: CrawlURLUseCase):
        self.crawl_url = crawl_url_use_case

    async def execute(self, input_data: BatchCrawlInput) -> BatchCrawlOutput:
        """
        Crawl multiple URLs with concurrency control.

        Args:
            input_data: URLs and options

        Returns:
            BatchCrawlOutput with aggregated results
        """
        start_time = datetime.now()

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(input_data.max_concurrent)

        async def crawl_with_limit(url: str) -> CrawlURLOutput:
            async with semaphore:
                return await self.crawl_url.execute(
                    CrawlURLInput(
                        url=url,
                        collection=input_data.collection,
                        chunk_size=input_data.chunk_size,
                        chunk_overlap=input_data.chunk_overlap,
                        source_name=input_data.source_name,
                        category=input_data.category,
                        tags=input_data.tags,
                    )
                )

        # Execute all crawls concurrently
        tasks = [crawl_with_limit(url) for url in input_data.urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        crawl_results: List[CrawlURLOutput] = []
        success_count = 0
        failed_count = 0
        total_chunks = 0

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                crawl_results.append(
                    CrawlURLOutput(
                        success=False,
                        url=input_data.urls[i],
                        error=str(result),
                    )
                )
                failed_count += 1
            else:
                crawl_results.append(result)
                if result.success:
                    success_count += 1
                    total_chunks += result.chunks_created
                else:
                    failed_count += 1

        duration = (datetime.now() - start_time).total_seconds()

        return BatchCrawlOutput(
            total_urls=len(input_data.urls),
            success_count=success_count,
            failed_count=failed_count,
            total_chunks=total_chunks,
            results=crawl_results,
            duration_seconds=duration,
        )
