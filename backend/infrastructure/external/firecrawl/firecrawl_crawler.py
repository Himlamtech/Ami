"""
FireCrawl crawler for extracting web content.
Uses FireCrawl API to crawl and extract content from URLs.
"""

import logging
import time
from typing import Any, Dict, Optional, List

from firecrawl import FirecrawlApp

from app.application.interfaces.processors.web_crawler import IWebCrawler
from app.config import firecrawl_config
from app.config.external import FirecrawlConfig

logger = logging.getLogger(__name__)


class FireCrawlCrawler(IWebCrawler):
    """Crawler using FireCrawl API to extract content from URLs."""

    def __init__(self, config: FirecrawlConfig = None):
        """
        Initialize the crawler.

        Args:
            config: Firecrawl configuration. If None, uses global firecrawl_config.
        """
        self.config = config or firecrawl_config

        if not self.config.api_key:
            raise ValueError("FIRECRAWL_API_KEY is required")

        self.client = FirecrawlApp(api_key=self.config.api_key)
        self.timeout = self.config.timeout
        self.min_content_length = self.config.min_content_length

    async def scrape_url(
        self, url: str, formats: List[str] = None, timeout: int = 60000
    ) -> Dict[str, Any]:
        """
        Scrape a single URL and extract content.

        Args:
            url: URL to scrape
            formats: Output formats (default: ["markdown"])
            timeout: Timeout in milliseconds

        Returns:
            Dictionary with scraped data including markdown content
        """
        start_time = time.time()

        try:
            logger.info(f"Scraping URL: {url}")

            # Scrape using Firecrawl
            result = self.client.scrape(
                url,
                formats=formats or ["markdown"],
                only_main_content=True,
                timeout=timeout,
            )

            duration = time.time() - start_time

            if not result:
                raise Exception("Empty response from Firecrawl")

            # Extract markdown content
            markdown_content = (
                result.markdown
                if hasattr(result, "markdown")
                else result.get("markdown", "")
            )

            # Validate content
            is_valid, error_msg = self.validate_content(markdown_content)
            if not is_valid:
                raise Exception(f"Invalid content: {error_msg}")

            # Clean content
            cleaned_content = self.clean_content(markdown_content)

            logger.info(
                f"Successfully scraped {url} in {duration:.2f}s "
                f"({len(cleaned_content)} chars)"
            )

            metadata = (
                result.metadata
                if hasattr(result, "metadata")
                else result.get("metadata", {})
            )

            return {
                "success": True,
                "url": url,
                "markdown": cleaned_content,
                "metadata": metadata,
                "duration_seconds": duration,
                "content_length": len(cleaned_content),
            }

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to scrape {url}: {str(e)}")

            return {
                "success": False,
                "url": url,
                "error": str(e),
                "duration_seconds": duration,
            }

    async def crawl_website(
        self,
        url: str,
        max_depth: int = 2,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Crawl a URL and its linked pages.

        Args:
            url: Starting URL
            max_depth: Maximum crawl depth
            limit: Maximum number of pages to crawl

        Returns:
            List of scraped pages
        """
        start_time = time.time()

        try:
            logger.info(
                f"Starting crawl from: {url} (max_depth={max_depth}, limit={limit})"
            )

            # Create scrape options
            from firecrawl.v2.types import ScrapeOptions

            scrape_opts = ScrapeOptions(
                formats=["markdown"],
                only_main_content=True,
                timeout=self.timeout,
            )

            # Start crawl job (async mode)
            result = self.client.crawl(
                url,
                limit=limit,
                max_discovery_depth=max_depth,
                scrape_options=scrape_opts,
                poll_interval=5,
            )

            duration = time.time() - start_time

            # Extract pages from result
            if isinstance(result, list):
                pages = result
            elif hasattr(result, "data"):
                pages = result.data
            elif isinstance(result, dict):
                pages = result.get("data", [])
            else:
                pages = []
            total_pages = len(pages)

            logger.info(
                f"Crawl completed in {duration:.2f}s, found {total_pages} pages"
            )

            # Format pages to match interface
            formatted_pages = []
            for page in pages:
                metadata = (
                    page.metadata
                    if hasattr(page, "metadata")
                    else page.get("metadata", {})
                )
                url = ""
                page_url = getattr(page, "url", "")
                if isinstance(page_url, str) and page_url:
                    url = page_url
                elif isinstance(metadata, dict):
                    url = metadata.get("url", "")
                elif metadata:
                    url = getattr(metadata, "url", "")

                formatted_pages.append(
                    {
                        "content": (
                            page.markdown
                            if hasattr(page, "markdown")
                            else page.get("markdown", "")
                        ),
                        "metadata": metadata,
                        "url": url,
                        "success": True,
                    }
                )

            return formatted_pages

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to crawl {url}: {str(e)}")
            return []

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

    async def search_web(
        self,
        query: str,
        max_results: int = 5,
        formats: list[str] = None,
    ) -> Dict[str, Any]:
        """
        Search the web using Firecrawl.

        Args:
            query: Search query
            max_results: Maximum number of results
            formats: Output formats

        Returns:
            Dictionary with search results
        """
        start_time = time.time()

        try:
            logger.info(f"Searching web for: {query}")

            # Create scrape options for search results
            from firecrawl.v2.types import ScrapeOptions

            scrape_opts = ScrapeOptions(
                formats=formats or ["markdown"],
                only_main_content=True,
            )

            # Search using Firecrawl
            result = self.client.search(
                query,
                limit=max_results,
                scrape_options=scrape_opts,
            )

            duration = time.time() - start_time

            if not result:
                raise Exception("No results returned from search")

            # Extract search results (Firecrawl returns web, news, images)
            results = []
            if hasattr(result, "web") and result.web:
                results = result.web
            elif hasattr(result, "news") and result.news:
                results = result.news
            else:
                results = []

            # Process each result
            processed_results = []
            for item in results:
                try:
                    # Extract content
                    if hasattr(item, "markdown"):
                        markdown = item.markdown
                        url = item.url if hasattr(item, "url") else ""
                        title = (
                            item.metadata.title
                            if hasattr(item, "metadata")
                            and hasattr(item.metadata, "title")
                            else ""
                        )
                    else:
                        markdown = item.get("markdown", "")
                        url = item.get("url", "")
                        metadata = item.get("metadata", {})
                        title = (
                            metadata.get("title", "")
                            if isinstance(metadata, dict)
                            else ""
                        )

                    # Validate and clean
                    is_valid, error_msg = self.validate_content(markdown)
                    if not is_valid:
                        continue

                    cleaned = self.clean_content(markdown)

                    processed_results.append(
                        {
                            "url": url,
                            "title": title,
                            "content": cleaned,
                            "length": len(cleaned),
                        }
                    )

                except Exception as e:
                    logger.warning(f"Failed to process search result: {e}")
                    continue

            logger.info(
                f"Search completed in {duration:.2f}s, found {len(processed_results)} valid results"
            )

            return {
                "success": True,
                "query": query,
                "results": processed_results,
                "total_results": len(processed_results),
                "duration_seconds": duration,
            }

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to search web for '{query}': {str(e)}")

            return {
                "success": False,
                "query": query,
                "error": str(e),
                "duration_seconds": duration,
            }

    def clean_content(self, content: str) -> str:
        """Clean and normalize extracted content."""
        if not content:
            return ""

        # Remove excessive whitespace
        lines = content.split("\n")
        cleaned_lines = []

        prev_empty = False
        for line in lines:
            line = line.strip()

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


if __name__ == "__main__":
    import asyncio

    async def test_crawler():
        crawler = FireCrawlCrawler()
        url = "https://www.ptit.edu.vn/"
        result = await crawler.scrape_url(url)
        if result["success"]:
            print(f"Scraped {url}: {len(result['markdown'])} chars")
        else:
            print(f"Failed to scrape {url}: {result['error']}")

        crawl_results = await crawler.crawl_website(url, max_depth=1, limit=5)
        print(f"Crawled {len(crawl_results)} pages from {url}")
        print(
            "First page content length:",
            len(crawl_results[0]["content"]) if crawl_results else 0,
        )
        print(crawl_results[0]["content"][:500] if crawl_results else "")
        search_result = await crawler.search_web("PTIT", max_results=3)
        if search_result["success"]:
            print(f"Search found {search_result['total_results']} results")
        else:
            print(f"Search failed: {search_result['error']}")

    asyncio.run(test_crawler())
