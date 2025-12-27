"""Tool call domain entity for query orchestration."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
from app.domain.enums.tool_type import ToolType, ToolExecutionStatus


@dataclass
class ToolArguments:
    """
    Value object for tool arguments.

    Type-safe container for tool-specific arguments.
    """

    raw_args: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """Get argument value."""
        return self.raw_args.get(key, default)

    def has(self, key: str) -> bool:
        """Check if argument exists."""
        return key in self.raw_args

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.raw_args.copy()


@dataclass
class ToolCall:
    """
    Domain Entity: Represents a tool invocation decision by the orchestrator.

    Business Rules:
    1. Tool type must be valid (from ToolType enum)
    2. Arguments must match tool schema
    3. Execution status tracks lifecycle: pending → running → success/failed
    4. Execution time is tracked for performance monitoring

    Note: The orchestrator (LLM) decides which tools to call based on:
    - Query intent analysis
    - Vector search results (as REFERENCE, not hard rule)
    - User context and conversation history
    """

    # Identity
    id: str

    # Tool specification
    tool_type: ToolType
    arguments: ToolArguments = field(default_factory=ToolArguments)

    # Orchestrator reasoning (why this tool was chosen)
    reasoning: str = ""

    # Execution lifecycle
    execution_status: ToolExecutionStatus = ToolExecutionStatus.PENDING
    execution_result: Optional[Dict[str, Any]] = None
    execution_time_ms: Optional[int] = None
    error_message: Optional[str] = None

    # Audit timestamps
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Business Logic Methods

    def start_execution(self) -> None:
        """
        Mark tool execution as started.

        Business Rule: Can only start from PENDING status.
        """
        if self.execution_status != ToolExecutionStatus.PENDING:
            raise ValueError(
                f"Cannot start execution from status: {self.execution_status}"
            )

        self.execution_status = ToolExecutionStatus.RUNNING
        self.started_at = datetime.now()

    def mark_success(self, result: Dict[str, Any]) -> None:
        """
        Mark tool execution as successful.

        Args:
            result: The result data from tool execution

        Business Rule: Automatically calculates execution time.
        """
        if self.execution_status != ToolExecutionStatus.RUNNING:
            raise ValueError(
                f"Cannot mark success from status: {self.execution_status}"
            )

        self.execution_status = ToolExecutionStatus.SUCCESS
        self.execution_result = result
        self.completed_at = datetime.now()

        if self.started_at:
            delta = self.completed_at - self.started_at
            self.execution_time_ms = int(delta.total_seconds() * 1000)

    def mark_failed(self, error: str) -> None:
        """
        Mark tool execution as failed.

        Args:
            error: Error message describing the failure
        """
        self.execution_status = ToolExecutionStatus.FAILED
        self.error_message = error
        self.completed_at = datetime.now()

        if self.started_at:
            delta = self.completed_at - self.started_at
            self.execution_time_ms = int(delta.total_seconds() * 1000)

    def mark_skipped(self, reason: str) -> None:
        """
        Mark tool as skipped (not executed).

        Used when orchestrator decides to skip a planned tool.
        """
        self.execution_status = ToolExecutionStatus.SKIPPED
        self.error_message = reason
        self.completed_at = datetime.now()

    # Query methods

    def is_pending(self) -> bool:
        """Check if tool is pending execution."""
        return self.execution_status == ToolExecutionStatus.PENDING

    def is_running(self) -> bool:
        """Check if tool is currently executing."""
        return self.execution_status == ToolExecutionStatus.RUNNING

    def is_completed(self) -> bool:
        """Check if tool execution is completed (success or failed)."""
        return self.execution_status in (
            ToolExecutionStatus.SUCCESS,
            ToolExecutionStatus.FAILED,
            ToolExecutionStatus.SKIPPED,
        )

    def is_success(self) -> bool:
        """Check if tool executed successfully."""
        return self.execution_status == ToolExecutionStatus.SUCCESS

    def is_failed(self) -> bool:
        """Check if tool execution failed."""
        return self.execution_status == ToolExecutionStatus.FAILED

    def has_result(self) -> bool:
        """Check if tool has execution result."""
        return self.execution_result is not None

    def get_result_value(self, key: str, default: Any = None) -> Any:
        """Get a value from execution result."""
        if self.execution_result is None:
            return default
        return self.execution_result.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "tool_type": self.tool_type.value,
            "arguments": self.arguments.to_dict(),
            "reasoning": self.reasoning,
            "execution_status": self.execution_status.value,
            "execution_result": self.execution_result,
            "execution_time_ms": self.execution_time_ms,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToolCall":
        """Create ToolCall from dictionary."""
        return cls(
            id=data["id"],
            tool_type=ToolType(data["tool_type"]),
            arguments=ToolArguments(raw_args=data.get("arguments", {})),
            reasoning=data.get("reasoning", ""),
            execution_status=ToolExecutionStatus(
                data.get("execution_status", "pending")
            ),
            execution_result=data.get("execution_result"),
            execution_time_ms=data.get("execution_time_ms"),
            error_message=data.get("error_message"),
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if data.get("created_at")
                else datetime.now()
            ),
            started_at=(
                datetime.fromisoformat(data["started_at"])
                if data.get("started_at")
                else None
            ),
            completed_at=(
                datetime.fromisoformat(data["completed_at"])
                if data.get("completed_at")
                else None
            ),
        )

    def __repr__(self) -> str:
        return f"ToolCall(tool={self.tool_type.value}, status={self.execution_status.value})"
