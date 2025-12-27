"""
Direct Answer Tool Handler - Answer without RAG.
"""

import logging
from typing import Dict, Any, Optional

from domain.enums.tool_type import ToolType
from application.interfaces.services.tool_executor_service import IToolHandler
from application.interfaces.services.llm_service import ILLMService


logger = logging.getLogger(__name__)


class DirectAnswerToolHandler(IToolHandler):
    """
    Handler for answer_directly tool.

    Answers questions directly without using RAG or web search.
    Used for general knowledge, greetings, etc.
    """

    def __init__(self, llm_service: Optional[ILLMService] = None):
        """
        Initialize direct answer tool handler.

        Args:
            llm_service: LLM service for generation (optional, can use pre-filled answer)
        """
        self._llm = llm_service

    @property
    def tool_type(self) -> ToolType:
        return ToolType.ANSWER_DIRECTLY

    def validate_arguments(self, arguments: Dict[str, Any]) -> bool:
        """Validate tool arguments."""
        required = ["reason"]
        return all(key in arguments for key in required)

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute direct answer tool.

        If orchestrator provided an answer, use it.
        Otherwise, generate one using LLM.

        Args:
            arguments:
                - answer: Pre-generated answer (optional)
                - reason: Why direct answer is appropriate
                - query: Original query (for LLM generation)

        Returns:
            {
                "answer": str,
                "reasoning": str
            }
        """
        pre_answer = arguments.get("answer", "")
        reason = arguments.get("reason", "")
        query = arguments.get("query", "")

        logger.info(f"Direct answer tool executing, reason: {reason}")

        # If orchestrator provided answer, use it
        if pre_answer:
            return {"answer": pre_answer, "reasoning": reason}

        # Otherwise, generate answer using LLM
        if self._llm and query:
            try:
                prompt = f"""Answer this general question directly and concisely.

Question: {query}

Instructions:
1. This is a general knowledge question, no specific context needed
2. Be helpful and accurate
3. Keep the answer concise
4. Use Vietnamese if the question is in Vietnamese

Answer:"""

                answer = await self._llm.generate(prompt=prompt)

                return {"answer": answer, "reasoning": reason}

            except Exception as e:
                logger.error(f"LLM generation failed: {e}")
                return {
                    "answer": "Xin lỗi, không thể trả lời câu hỏi này.",
                    "reasoning": f"Error: {str(e)}",
                }

        return {
            "answer": "Xin lỗi, không có đủ thông tin để trả lời.",
            "reasoning": reason,
        }
