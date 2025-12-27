"""
Web Search Tool Handler - Search external web for information.
"""

import logging
from typing import Dict, Any, List, Optional

from app.domain.enums.tool_type import ToolType
from app.application.interfaces.services.tool_executor_service import IToolHandler
from app.application.interfaces.services.web_search_service import IWebSearchService


logger = logging.getLogger(__name__)


class WebSearchToolHandler(IToolHandler):
    """
    Handler for search_web tool.

    Uses web search to find external information.
    """

    def __init__(self, web_search_service: Optional[IWebSearchService] = None):
        """
        Initialize web search tool handler.

        Args:
            web_search_service: Web search service implementation
        """
        self._search = web_search_service

    @property
    def tool_type(self) -> ToolType:
        return ToolType.SEARCH_WEB

    def validate_arguments(self, arguments: Dict[str, Any]) -> bool:
        """Validate tool arguments."""
        required = ["query", "reason"]
        return all(key in arguments for key in required)

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute web search tool.

        Args:
            arguments:
                - query: Search query
                - domain_filter: Optional domain filter (e.g., 'ptit.edu.vn')
                - reason: Why web search is needed

        Returns:
            {
                "results": List[Dict],
                "query_used": str,
                "source_urls": List[str],
                "summary": str
            }
        """
        query = arguments.get("query", "")
        domain_filter = arguments.get("domain_filter", "")
        reason = arguments.get("reason", "")

        logger.info(f"Web search tool executing: '{query}' (domain: {domain_filter})")

        # Add domain filter to query if specified
        search_query = query
        if domain_filter:
            search_query = f"{query} site:{domain_filter}"

        if not self._search:
            logger.warning("No web search service configured, returning empty results")
            return {
                "results": [],
                "query_used": search_query,
                "source_urls": [],
                "summary": "Web search service not configured.",
            }

        try:
            response = await self._search.search(search_query)

            results = []
            source_urls = []

            for result in response.sources[:5]:
                results.append(
                    {
                        "title": result.title,
                        "snippet": result.snippet,
                        "url": result.url,
                    }
                )
                source_urls.append(result.url)

            summary = response.answer or self._build_summary(results)

            return {
                "results": results,
                "query_used": search_query,
                "source_urls": source_urls,
                "summary": summary,
            }

        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return {
                "results": [],
                "query_used": search_query,
                "source_urls": [],
                "summary": f"Web search failed: {str(e)}",
            }

    def _build_summary(self, results: List[Dict[str, Any]]) -> str:
        """Build summary from search results."""
        if not results:
            return "Không tìm thấy kết quả từ web."

        summary_parts = []
        for i, result in enumerate(results, 1):
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            summary_parts.append(f"{i}. {title}: {snippet}")

        return "\n".join(summary_parts)
