"""
Gemini Web Search implementation using Google Search grounding.
Uses Google's generative AI with built-in web search capability.
"""

import logging
import re
from typing import List, Optional

import google.genai as genai
from google.genai import types

from application.interfaces.services.web_search_service import (
    IWebSearchService,
    WebSearchResponse,
    SearchResult,
)
from config import gemini_config
from config.ai import GeminiConfig

logger = logging.getLogger(__name__)


class GeminiWebSearchService(IWebSearchService):
    """
    Web Search using Gemini with Google Search grounding.

    This leverages Google's built-in search capability to provide
    accurate, up-to-date answers with source citations.
    """

    def __init__(
        self,
        config: Optional[GeminiConfig] = None,
    ):
        """
        Initialize Gemini Web Search service.

        Args:
            config: Gemini configuration. If None, uses global gemini_config.
        """
        self.config = config or gemini_config
        self._client = genai.Client(api_key=self.config.api_key)
        self._model = self.config.model_web_search

        # Configure grounding tool
        self._grounding_tool = types.Tool(google_search=types.GoogleSearch())

        logger.info(f"Initialized GeminiWebSearchService with model: {self._model}")

    async def search(
        self, query: str, num_results: int = 5, **kwargs
    ) -> WebSearchResponse:
        """
        Search the web using Gemini with Google Search grounding.

        Args:
            query: Search query
            num_results: Maximum number of source results to extract
            **kwargs: Additional parameters

        Returns:
            WebSearchResponse with answer and sources
        """
        try:
            logger.debug(f"Web search query: {query}")

            # Configure generation with grounding
            config = types.GenerateContentConfig(
                tools=[self._grounding_tool],
                temperature=kwargs.pop("temperature", 0.7),
                max_output_tokens=kwargs.pop("max_tokens", 4096),
            )

            # Generate response with web search
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents=query,
                config=config,
            )

            # Extract answer
            answer = response.text if response.text else ""

            # Extract sources from grounding metadata
            sources = self._extract_sources(response, num_results)

            logger.info(
                f"Web search completed: {len(answer)} chars, {len(sources)} sources"
            )

            return WebSearchResponse(
                answer=answer,
                sources=sources,
                query=query,
            )

        except Exception as e:
            logger.error(f"Error in Gemini web search: {e}")
            raise RuntimeError(f"Web search failed: {str(e)}")

    def _extract_sources(self, response, max_sources: int = 5) -> List[SearchResult]:
        """
        Extract source URLs from Gemini response grounding metadata.

        Args:
            response: Gemini API response
            max_sources: Maximum number of sources to return

        Returns:
            List of SearchResult objects
        """
        sources = []

        try:
            # Check if response has grounding metadata
            if not hasattr(response, "candidates") or not response.candidates:
                return sources

            candidate = response.candidates[0]

            # Try to get grounding metadata
            if (
                hasattr(candidate, "grounding_metadata")
                and candidate.grounding_metadata
            ):
                metadata = candidate.grounding_metadata

                # Extract from grounding_chunks if available
                if hasattr(metadata, "grounding_chunks"):
                    for chunk in metadata.grounding_chunks[:max_sources]:
                        if hasattr(chunk, "web") and chunk.web:
                            sources.append(
                                SearchResult(
                                    title=getattr(chunk.web, "title", "Unknown"),
                                    url=getattr(chunk.web, "uri", ""),
                                    snippet=(
                                        getattr(chunk, "text", "")[:200]
                                        if hasattr(chunk, "text")
                                        else ""
                                    ),
                                )
                            )

                # Extract from search_entry_point if available
                if (
                    hasattr(metadata, "search_entry_point")
                    and metadata.search_entry_point
                ):
                    if hasattr(metadata.search_entry_point, "rendered_content"):
                        # Parse rendered HTML for links
                        rendered = metadata.search_entry_point.rendered_content
                        urls = self._extract_urls_from_html(rendered)
                        for url in urls[: max_sources - len(sources)]:
                            if not any(s.url == url for s in sources):
                                sources.append(
                                    SearchResult(
                                        title="Search Result",
                                        url=url,
                                        snippet="",
                                    )
                                )

        except Exception as e:
            logger.warning(f"Failed to extract sources: {e}")

        return sources[:max_sources]

    def _extract_urls_from_html(self, html: str) -> List[str]:
        """Extract URLs from HTML content."""
        url_pattern = r'https?://[^\s<>"\']+[^\s<>"\'\.]'
        urls = re.findall(url_pattern, html)
        # Filter out Google URLs and duplicates
        unique_urls = []
        for url in urls:
            if "google.com" not in url and url not in unique_urls:
                unique_urls.append(url)
        return unique_urls


if __name__ == "__main__":
    import asyncio

    async def test():
        service = GeminiWebSearchService()
        response = await service.search(
            "Điểm chuẩn PTIT 2025 và năm trước đó là bao nhiêu?"
        )
        print(f"Answer: {response.answer}")
        print(f"\nSources ({len(response.sources)}):")
        for src in response.sources:
            print(f"  - {src.title}: {src.url}")

    asyncio.run(test())
