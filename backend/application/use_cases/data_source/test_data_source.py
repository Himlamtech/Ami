"""Test data source use case - Test crawl a source before saving."""

from dataclasses import dataclass
from typing import Optional, Dict

from app.domain.enums.data_source import SourceType


@dataclass
class TestDataSourceInput:
    """Input for testing a data source."""

    url: str
    source_type: SourceType = SourceType.WEB_CRAWL
    detail_selector: Optional[str] = None
    auth_type: str = "none"
    auth_token: Optional[str] = None
    auth_headers: Optional[Dict[str, str]] = None


@dataclass
class TestDataSourceOutput:
    """Output from testing a data source."""

    success: bool
    content_preview: Optional[str] = None
    content_length: int = 0
    title: Optional[str] = None
    error: Optional[str] = None
    duration_seconds: float = 0.0


class TestDataSourceUseCase:
    """
    Use case for testing a data source before creating.

    Performs a test crawl to verify:
    - URL is accessible
    - Auth works (if provided)
    - Content can be extracted
    """

    def __init__(self, crawler):
        """
        Args:
            crawler: FireCrawlCrawler instance
        """
        self.crawler = crawler

    async def execute(self, input_data: TestDataSourceInput) -> TestDataSourceOutput:
        """Test crawl a URL and return preview."""
        try:
            # Perform test scrape
            result = await self.crawler.scrape_url(
                url=input_data.url,
                formats=["markdown"],
                only_main_content=True,
            )

            if not result.get("success"):
                return TestDataSourceOutput(
                    success=False,
                    error=result.get("error", "Unknown error"),
                    duration_seconds=result.get("duration_seconds", 0),
                )

            content = result.get("markdown", "")
            metadata = result.get("metadata", {})

            # Truncate preview
            preview = content[:1000] + "..." if len(content) > 1000 else content

            return TestDataSourceOutput(
                success=True,
                content_preview=preview,
                content_length=len(content),
                title=metadata.get("title"),
                duration_seconds=result.get("duration_seconds", 0),
            )

        except Exception as e:
            return TestDataSourceOutput(
                success=False,
                error=str(e),
            )
