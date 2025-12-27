"""Tool executor service interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any

from domain.entities.tool_call import ToolCall
from domain.enums.tool_type import ToolType


class IToolExecutorService(ABC):
    """
    Interface for Tool Executor.

    Executes individual tools based on ToolCall entities from the orchestrator.
    Each tool has specific logic and may interact with different services.

    Tool Types:
    - use_rag_context: Use retrieved documents to answer
    - search_web: Search external web for latest info
    - answer_directly: Answer without RAG (general knowledge)
    - fill_form: Generate pre-filled forms from templates + user data
    - clarify_question: Ask user for clarification
    - analyze_image: Analyze image artifacts with Vision
    """

    @abstractmethod
    async def execute(self, tool_call: ToolCall) -> Dict[str, Any]:
        """
        Execute a tool and return result.

        Args:
            tool_call: ToolCall entity with tool type and arguments

        Returns:
            Tool execution result as dictionary.
            Structure varies by tool type:

            use_rag_context:
                {
                    "answer": str,
                    "sources": List[Dict],
                    "confidence": str
                }

            search_web:
                {
                    "results": List[Dict],
                    "query_used": str,
                    "source_urls": List[str]
                }

            answer_directly:
                {
                    "answer": str,
                    "reasoning": str
                }

            fill_form:
                {
                    "form_markdown": str,
                    "form_type": str,
                    "pre_filled_fields": List[str],
                    "missing_fields": List[str]
                }

            clarify_question:
                {
                    "clarification_prompt": str,
                    "suggestions": List[str]
                }

            analyze_image:
                {
                    "description": str,
                    "response": str,
                    "extracted_text": str | None,
                    "detected_objects": List[str],
                    "related_documents": List[Dict]
                }

        Raises:
            ToolExecutionError: If tool execution fails
        """
        pass

    @abstractmethod
    def supports_tool(self, tool_type: ToolType) -> bool:
        """
        Check if this executor supports a tool type.

        Args:
            tool_type: The tool type to check

        Returns:
            True if supported, False otherwise
        """
        pass


class IToolHandler(ABC):
    """
    Interface for individual tool handlers.

    Each tool type has its own handler implementing this interface.
    """

    @property
    @abstractmethod
    def tool_type(self) -> ToolType:
        """Get the tool type this handler supports."""
        pass

    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool with given arguments.

        Args:
            arguments: Tool-specific arguments

        Returns:
            Tool execution result
        """
        pass

    @abstractmethod
    def validate_arguments(self, arguments: Dict[str, Any]) -> bool:
        """
        Validate tool arguments.

        Args:
            arguments: Arguments to validate

        Returns:
            True if valid, False otherwise
        """
        pass
