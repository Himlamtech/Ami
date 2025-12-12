"""Web Search service interface."""

from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass


@dataclass
class SearchResult:
    """A single search result."""

    title: str
    url: str
    snippet: str


@dataclass
class WebSearchResponse:
    """Web search response with answer and sources."""

    answer: str
    sources: List[SearchResult]
    query: str


class IWebSearchService(ABC):
    """
    Interface for Web Search providers.

    Provides web search with grounding - returns answers with sources.
    """

    @abstractmethod
    async def search(
        self, query: str, num_results: int = 5, **kwargs
    ) -> WebSearchResponse:
        """
        Search the web and return grounded answer with sources.

        Args:
            query: Search query
            num_results: Maximum number of results to return
            **kwargs: Additional search parameters

        Returns:
            WebSearchResponse with answer and source URLs
        """
        pass

    async def search_and_summarize(self, query: str, **kwargs) -> str:
        """
        Search and return a summarized answer (convenience method).

        Args:
            query: Search query
            **kwargs: Additional parameters

        Returns:
            Summarized answer string
        """
        response = await self.search(query, **kwargs)
        return response.answer
