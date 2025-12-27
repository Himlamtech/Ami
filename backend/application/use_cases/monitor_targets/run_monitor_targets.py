"""Use case for executing monitor targets."""

import logging
from typing import List
from datetime import datetime

from application.interfaces.repositories.monitor_target_repository import (
    IMonitorTargetRepository,
)
from application.interfaces.processors.web_crawler import IWebCrawler
from application.services.document_ingest_service import (
    DocumentIngestService,
    IngestPayload,
)
from domain.enums.data_source import DataCategory

logger = logging.getLogger(__name__)


class RunMonitorTargetsUseCase:
    """Check due monitor targets and ingest content."""

    def __init__(
        self,
        monitor_repository: IMonitorTargetRepository,
        web_crawler: IWebCrawler,
        ingest_service: DocumentIngestService,
    ):
        self.monitor_repo = monitor_repository
        self.web_crawler = web_crawler
        self.ingest_service = ingest_service

    async def execute(self) -> List[str]:
        """Run monitor job, returning list of pending IDs created."""
        pending_ids: List[str] = []
        targets = await self.monitor_repo.get_due_targets()
        if not targets:
            return pending_ids

        for target in targets:
            if not target.should_check():
                continue
            try:
                crawl_result = await self.web_crawler.scrape_url(
                    url=target.url,
                    formats=["markdown"],
                    timeout=30000,
                )
                if not crawl_result.get("success"):
                    raise RuntimeError(crawl_result.get("error", "Unknown crawl error"))

                content = crawl_result.get("content", "")
                if not content:
                    raise RuntimeError("Empty content returned from crawler")

                metadata = crawl_result.get("metadata", {}) or {}
                category_value = metadata.get("category") or target.category
                try:
                    category_enum = DataCategory(category_value)
                except ValueError:
                    category_enum = DataCategory.GENERAL

                payload = IngestPayload(
                    source_id=target.id,
                    title=metadata.get("title") or target.name,
                    content=content,
                    source_url=target.url,
                    collection=target.collection,
                    category=category_enum,
                    metadata={
                        **metadata,
                        "monitor_target_id": target.id,
                        "chunk_size": 800,
                        "chunk_overlap": 120,
                    },
                )
                pending = await self.ingest_service.ingest(payload)
                pending_ids.append(pending.id)
                target.mark_success(content_hash=pending.content_hash)
                await self.monitor_repo.update(target)
            except Exception as e:
                logger.error("Monitor target %s failed: %s", target.url, e)
                target.mark_failure(str(e))
                await self.monitor_repo.update(target)

        return pending_ids
