"""External third-party integrations."""

from .firecrawl import FireCrawlCrawler
from .web_search import GeminiWebSearchService

__all__ = ["FireCrawlCrawler", "GeminiWebSearchService"]
