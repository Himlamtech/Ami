"""Orchestrator service interface."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from app.domain.entities.tool_call import ToolCall


class IOrchestratorService(ABC):
    """
    Interface for Query Orchestrator.

    The orchestrator analyzes user queries and decides which tool(s) to call.
    It uses LLM function calling to make intelligent decisions based on:
    - Query intent analysis
    - Vector search results (as REFERENCE, not hard rules)
    - User context and conversation history

    Key Design Principles:
    1. Vector scores are SIGNALS, not thresholds
    2. LLM has full context to make intelligent decisions
    3. Can call 0, 1, or multiple tools
    4. Decisions are explainable (reasoning field)
    """

    @abstractmethod
    async def decide_tools(
        self,
        query: str,
        vector_results: Dict[str, Any],
        user_context: Dict[str, Any],
        conversation_history: List[Dict[str, Any]],
        image_info: Optional[Dict[str, Any]] = None,
    ) -> List[ToolCall]:
        """
        Analyze query and decide which tools to call.

        Args:
            query: User's natural language query
            vector_results: Vector search results as REFERENCE
                {
                    "max_score": float,  # Highest similarity score
                    "top_chunks": List[str],  # Chunk IDs
                    "chunk_contents": List[Dict],  # Chunk data
                    "search_time_ms": int
                }
            user_context: User profile information
                {
                    "major": str,
                    "year": int,
                    "language": str,
                    "student_id": str (optional)
                }
            conversation_history: Recent messages for context
                [{"role": "user/assistant", "content": str}, ...]

        Returns:
            List of ToolCall entities to execute.
            Can be empty (LLM handles directly), single, or multiple tools.

        Notes:
            - Vector scores are REFERENCE only - LLM makes final decision
            - High score (0.9) on form template → fill_form (not RAG)
            - Low score but general question → answer_directly
            - Medium score + time-sensitive → RAG + web_search
        """
        pass

    @abstractmethod
    async def synthesize_response(
        self,
        query: str,
        tool_results: List[ToolCall],
        user_context: Dict[str, Any],
    ) -> str:
        """
        Synthesize final answer from tool results.

        Args:
            query: Original user query
            tool_results: Executed tool calls with results
            user_context: User profile for personalization

        Returns:
            Final synthesized answer combining all tool outputs.
        """
        pass
