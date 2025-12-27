"""
Tool Executor Service - Routes tool calls to appropriate handlers.
"""

import logging
from typing import Dict, Any, List

from app.domain.entities.tool_call import ToolCall
from app.domain.enums.tool_type import ToolType
from app.application.interfaces.services.tool_executor_service import (
    IToolExecutorService,
    IToolHandler,
)


logger = logging.getLogger(__name__)


class ToolExecutorService(IToolExecutorService):
    """
    Tool Executor implementation.

    Routes tool calls to the appropriate handler based on tool type.
    Each tool has its own handler implementing IToolHandler.
    """

    def __init__(self, handlers: List[IToolHandler] = None):
        """
        Initialize with tool handlers.

        Args:
            handlers: List of tool handlers. If None, no handlers registered.
        """
        self._handlers: Dict[ToolType, IToolHandler] = {}

        if handlers:
            for handler in handlers:
                self.register_handler(handler)

    def register_handler(self, handler: IToolHandler) -> None:
        """
        Register a tool handler.

        Args:
            handler: Handler implementing IToolHandler
        """
        self._handlers[handler.tool_type] = handler
        logger.debug(f"Registered handler for tool: {handler.tool_type.value}")

    def supports_tool(self, tool_type: ToolType) -> bool:
        """Check if a tool type is supported."""
        return tool_type in self._handlers

    async def execute(self, tool_call: ToolCall) -> Dict[str, Any]:
        """
        Execute a tool call.

        Routes to the appropriate handler based on tool type.

        Args:
            tool_call: ToolCall entity with type and arguments

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool type not supported
            RuntimeError: If tool execution fails
        """
        if not self.supports_tool(tool_call.tool_type):
            raise ValueError(
                f"No handler registered for tool: {tool_call.tool_type.value}"
            )

        handler = self._handlers[tool_call.tool_type]

        # Validate arguments
        if not handler.validate_arguments(tool_call.arguments.to_dict()):
            raise ValueError(f"Invalid arguments for tool {tool_call.tool_type.value}")

        logger.info(f"Executing tool: {tool_call.tool_type.value}")

        try:
            result = await handler.execute(tool_call.arguments.to_dict())

            logger.debug(f"Tool {tool_call.tool_type.value} completed successfully")

            return result

        except Exception as e:
            logger.error(f"Tool {tool_call.tool_type.value} failed: {str(e)}")
            raise RuntimeError(f"Tool execution failed: {str(e)}")

    def get_registered_tools(self) -> List[ToolType]:
        """Get list of registered tool types."""
        return list(self._handlers.keys())
