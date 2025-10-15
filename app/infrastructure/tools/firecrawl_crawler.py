"""
FireCrawl crawler for extracting web content.
Uses FireCrawl MCP tool to crawl and extract content from URLs.
"""

import logging
import time
from typing import Any, Dict, Optional

from app.core.models import CrawlResult, CrawlStatus, CrawlTask

logger = logging.getLogger(__name__)


class FireCrawlCrawler:
    """Crawler using FireCrawl API to extract content from URLs."""

    def __init__(self):
        """Initialize the crawler."""
        self.timeout = 60000  # 60 seconds
        self.min_content_length = 100
        self.extraction_prompt = (
            "Extract all main content from this page and convert to markdown format. "
            "Include titles, headings, paragraphs, lists, tables, and important information. "
            "Exclude navigation menus, footers, advertisements, and unrelated content. "
            "Focus on the main educational and informational content. "
            "Preserve Vietnamese text correctly."
        )

    async def crawl(self, task: CrawlTask) -> CrawlResult:
        """
        Crawl a single URL and extract content.

        Note: This method is designed to be called from a script that has access
        to MCP tools. The actual MCP tool call should be done by the caller.
        """
        start_time = time.time()

        try:
            logger.info(f"Starting crawl for: {task.url}")

            # This is a placeholder - actual implementation should use MCP tool
            # The script calling this should handle the MCP tool invocation
            raise NotImplementedError(
                "This method should be called from a script with MCP tool access. "
                "Use the crawl_with_mcp function from the crawl script instead."
            )

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to crawl {task.url}: {str(e)}")

            task.status = CrawlStatus.FAILED
            task.error = str(e)

            return CrawlResult(
                task=task, success=False, error=str(e), duration_seconds=duration
            )

    def validate_content(self, content: str) -> tuple[bool, Optional[str]]:
        """
        Validate extracted content.

        Returns:
            (is_valid, error_message)
        """
        if not content:
            return False, "Empty content"

        # Check minimum length
        if len(content) < self.min_content_length:
            return False, f"Content too short ({len(content)} chars)"

        # Check for common error pages
        error_indicators = [
            "404 not found",
            "page not found",
            "access denied",
            "forbidden",
            "error 404",
            "500 internal server error",
        ]

        content_lower = content.lower()
        for indicator in error_indicators:
            if indicator in content_lower[:500]:  # Check first 500 chars
                return False, f"Detected error page: {indicator}"

        return True, None

    def clean_content(self, content: str) -> str:
        """Clean and normalize extracted content."""
        if not content:
            return ""

        # Remove excessive whitespace
        lines = content.split("\n")
        cleaned_lines = []

        prev_empty = False
        for line in lines:
            line = line.rstrip()

            if not line:
                if not prev_empty:
                    cleaned_lines.append("")
                prev_empty = True
            else:
                cleaned_lines.append(line)
                prev_empty = False

        # Join lines
        cleaned = "\n".join(cleaned_lines)

        # Remove more than 2 consecutive newlines
        while "\n\n\n" in cleaned:
            cleaned = cleaned.replace("\n\n\n", "\n\n")

        return cleaned.strip()

    def get_extraction_config(self) -> Dict[str, Any]:
        """Get configuration for FireCrawl extraction."""
        return {
            "prompt": self.extraction_prompt,
            "formats": ["markdown"],
            "timeout": self.timeout,
            "enable_web_search": False,
        }
