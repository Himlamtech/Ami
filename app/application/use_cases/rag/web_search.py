"""Web Search use case - Search web for real-time information."""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from app.application.interfaces.services.web_search_service import (
    IWebSearchService,
)
from app.application.interfaces.services.llm_service import ILLMService


@dataclass
class WebSearchInput:
    """Input for web search use case."""

    query: str
    num_results: int = 5

    # Optional: enhance answer with LLM
    enhance_with_llm: bool = True
    system_prompt: Optional[str] = None


@dataclass
class WebSearchOutput:
    """Output from web search use case."""

    query: str
    answer: str
    sources: List[Dict[str, Any]]

    # Metadata
    enhanced: bool = False
    search_provider: str = ""


class WebSearchUseCase:
    """
    Use Case: Search the web for real-time information.

    Uses web search service (Gemini with Google Search grounding)
    to find current information not available in knowledge base.

    Pipeline:
    1. Search web with query
    2. (Optional) Enhance answer with LLM for better formatting

    Single Responsibility: Web search for current information
    """

    def __init__(
        self,
        web_search_service: IWebSearchService,
        llm_service: Optional[ILLMService] = None,
    ):
        self.web_search = web_search_service
        self.llm_service = llm_service

    async def execute(self, input_data: WebSearchInput) -> WebSearchOutput:
        """
        Execute web search.

        Args:
            input_data: Search query and options

        Returns:
            WebSearchOutput with answer and sources
        """
        # 1. Perform web search
        search_result = await self.web_search.search(
            query=input_data.query,
            num_results=input_data.num_results,
        )

        answer = search_result.answer
        sources = [
            {
                "title": s.title,
                "url": s.url,
                "snippet": s.snippet,
            }
            for s in search_result.sources
        ]

        # 2. Optionally enhance with LLM
        enhanced = False
        if input_data.enhance_with_llm and self.llm_service and answer:
            try:
                system_prompt = (
                    input_data.system_prompt or self._default_system_prompt()
                )
                enhanced_answer = await self.llm_service.generate(
                    prompt=f"Based on this search result, provide a helpful answer:\n\n{answer}",
                    context=None,
                    system_prompt=system_prompt,
                )
                answer = enhanced_answer
                enhanced = True
            except Exception:
                # Fall back to original answer
                pass

        return WebSearchOutput(
            query=input_data.query,
            answer=answer,
            sources=sources,
            enhanced=enhanced,
            search_provider="gemini_google_search",
        )

    def _default_system_prompt(self) -> str:
        """Default system prompt for answer enhancement."""
        return """Bạn là trợ lý AI hữu ích. Hãy trả lời câu hỏi dựa trên thông tin tìm kiếm được.
        
Quy tắc:
- Trả lời ngắn gọn, chính xác
- Nếu thông tin không đủ, hãy nói rõ
- Sử dụng tiếng Việt
- Không bịa đặt thông tin"""
