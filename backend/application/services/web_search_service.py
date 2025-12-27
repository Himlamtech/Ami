"""Web search service - Integration with web search APIs."""

from typing import List, Dict, Any, Optional
from application.interfaces.processors.web_crawler import IWebCrawler
from application.interfaces.services.llm_service import ILLMService


class WebSearchService:
    """
    Web search service for combining web search with RAG.

    Integrates web crawling for real-time information retrieval.
    """

    def __init__(
        self,
        web_crawler: IWebCrawler,
        llm_service: ILLMService,
    ):
        self.crawler = web_crawler
        self.llm_service = llm_service

    async def search_and_summarize(
        self,
        query: str,
        max_results: int = 3,
    ) -> Dict[str, Any]:
        """
        Search web and create summary.

        Workflow:
        1. Extract search query from user question
        2. Perform web search
        3. Scrape top results
        4. Summarize findings
        """
        # For now, return placeholder
        # Real implementation would use Firecrawl or similar

        return {
            "query": query,
            "results": [],
            "summary": "Web search not yet fully implemented",
            "sources": [],
        }

    async def scrape_url_and_extract(
        self,
        url: str,
        question: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Scrape URL and extract relevant information.

        Args:
            url: URL to scrape
            question: Optional specific question to answer from the page

        Returns:
            Scraped content and optional answer
        """
        # Scrape URL
        result = await self.crawler.scrape_url(
            url=url,
            formats=["markdown"],
            timeout=30000,
        )

        if not result.get("success"):
            return {
                "success": False,
                "error": "Failed to scrape URL",
            }

        content = result.get("content", "")

        # If question provided, use LLM to extract answer
        answer = None
        if question and self.llm_service:
            prompt = f"""Based on the following web page content, answer the question.

Content:
{content[:3000]}  # Limit context size

Question: {question}

Answer:"""

            answer = await self.llm_service.generate(
                prompt=prompt,
                temperature=0.3,
                max_tokens=500,
            )

        return {
            "success": True,
            "url": url,
            "content": content,
            "answer": answer,
            "metadata": result.get("metadata", {}),
        }

    async def batch_scrape_urls(
        self,
        urls: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Scrape multiple URLs.

        Returns list of scrape results.
        """
        results = []

        for url in urls:
            try:
                result = await self.crawler.scrape_url(
                    url=url,
                    formats=["markdown"],
                )
                results.append(
                    {
                        "url": url,
                        "success": result.get("success", False),
                        "content": result.get("content", ""),
                    }
                )
            except Exception as e:
                results.append(
                    {
                        "url": url,
                        "success": False,
                        "error": str(e),
                    }
                )

        return results

    def build_search_context(
        self,
        search_results: List[Dict[str, Any]],
    ) -> str:
        """
        Build context from search results.

        Formats search results into readable context for LLM.
        """
        context_parts = []

        for i, result in enumerate(search_results, 1):
            if result.get("success"):
                url = result.get("url", "")
                content = result.get("content", "")[:500]  # Limit per result

                context_parts.append(f"[Source {i}] {url}\n{content}\n")

        return "\n\n".join(context_parts)
