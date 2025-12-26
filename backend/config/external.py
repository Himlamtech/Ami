"""
External services configuration - Third-party APIs.
Includes Firecrawl and other external integrations.

Note: pydantic-settings automatically maps environment variables to field names
(case-insensitive). For example, field `firecrawl_api_key` maps to env var `FIRECRAWL_API_KEY`.
"""

from pydantic import Field
from .base import BaseConfig


class FirecrawlConfig(BaseConfig):
    """Firecrawl web scraping service configuration."""

    firecrawl_api_key: str = Field(default="")
    firecrawl_timeout: int = Field(default=60000, ge=1000)  # milliseconds
    firecrawl_min_content_length: int = Field(default=10, ge=1)

    # Convenience properties
    @property
    def api_key(self) -> str:
        return self.firecrawl_api_key

    @property
    def timeout(self) -> int:
        return self.firecrawl_timeout

    @property
    def min_content_length(self) -> int:
        return self.firecrawl_min_content_length


# Singleton instances
firecrawl_config = FirecrawlConfig()
