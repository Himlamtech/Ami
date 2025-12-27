"""Tool type enumeration for query orchestration."""

from enum import Enum


class ToolType(str, Enum):
    """
    Available tools for query orchestration.

    These tools are called by the LLM orchestrator to handle different query types.
    The orchestrator decides which tool(s) to use based on:
    - Query intent analysis
    - Vector search results (as reference, not hard rule)
    - User context and conversation history
    """

    # Use retrieved documents from vector search
    USE_RAG_CONTEXT = "use_rag_context"

    # Search external web (when internal docs insufficient)
    SEARCH_WEB = "search_web"

    # Answer directly without RAG (general knowledge, math, etc.)
    ANSWER_DIRECTLY = "answer_directly"

    # Generate pre-filled forms from templates + user data
    FILL_FORM = "fill_form"

    # Ask user for clarification when query is unclear
    CLARIFY_QUESTION = "clarify_question"

    # Analyze image artifacts and answer image-based queries
    ANALYZE_IMAGE = "analyze_image"


class ToolExecutionStatus(str, Enum):
    """Status of tool execution."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"  # When LLM decides to skip a planned tool
