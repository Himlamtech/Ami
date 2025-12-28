"""Orchestrate query use case - Core orchestration logic with function calling."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable, Awaitable
import uuid
import asyncio
import logging

from domain.entities.tool_call import ToolCall
from domain.entities.orchestration_result import (
    OrchestrationResult,
    VectorSearchReference,
    OrchestrationMetrics,
)
from domain.enums.tool_type import ToolType
from domain.enums.llm_mode import LLMMode
from application.interfaces.services.llm_service import ILLMService
from application.interfaces.services.orchestrator_service import (
    IOrchestratorService,
)
from application.interfaces.services.tool_executor_service import (
    IToolExecutorService,
)


logger = logging.getLogger(__name__)


@dataclass
class OrchestrateQueryInput:
    """Input for orchestrate query use case."""

    # Query info
    query: str
    session_id: str
    message_id: str

    # Vector search results (REFERENCE, not hard rules)
    vector_results: Dict[str, Any] = field(default_factory=dict)
    # Expected format:
    # {
    #     "max_score": float,
    #     "top_chunks": List[str],
    #     "chunk_contents": List[Dict],
    #     "search_time_ms": int
    # }

    # User context for personalization
    user_context: Dict[str, Any] = field(default_factory=dict)
    # Expected format:
    # {
    #     "major": str,
    #     "year": int,
    #     "language": str,
    #     "student_id": str (optional)
    # }

    # Conversation history for context
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    # Expected format:
    # [{"role": "user/assistant", "content": str}, ...]

    # Optional image artifact (for multimodal orchestration)
    image_bytes: Optional[bytes] = None
    image_format: Optional[str] = None


@dataclass
class OrchestrateQueryOutput:
    """Output from orchestrate query use case."""

    result: OrchestrationResult

    # Convenience accessors
    @property
    def final_answer(self) -> str:
        return self.result.final_answer

    @property
    def tools_used(self) -> List[str]:
        return [t.tool_type.value for t in self.result.get_successful_tools()]

    @property
    def confidence(self) -> str:
        return self.result.confidence_level

    @property
    def sources(self) -> List[str]:
        return self.result.sources_used


class OrchestrateQueryUseCase:
    """
    Use Case: Orchestrate query processing with intelligent tool selection.

    Business Flow:
    1. Receive query + vector search results (as reference)
    2. Ask orchestrator (LLM with function calling) to decide tools
    3. Execute decided tools (can be parallel if independent)
    4. Synthesize final answer from tool results
    5. Return OrchestrationResult with full audit trail

    Key Design Decisions:
    - Vector scores are REFERENCE for LLM, not hard thresholds
    - LLM makes intelligent decisions based on full context
    - Tools can be combined (RAG + Web search)
    - All decisions are logged for analytics

    Clean Architecture:
    - Depends only on interfaces (IOrchestratorService, IToolExecutorService)
    - Uses domain entities only
    - No infrastructure details leak into this layer
    """

    def __init__(
        self,
        orchestrator: IOrchestratorService,
        tool_executor: IToolExecutorService,
        synthesis_llm: Optional[ILLMService] = None,
    ):
        self.orchestrator = orchestrator
        self.tool_executor = tool_executor
        self.synthesis_llm = synthesis_llm

    async def execute(
        self,
        input_data: OrchestrateQueryInput,
        event_handler: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
    ) -> OrchestrateQueryOutput:
        """
        Execute query orchestration.

        Args:
            input_data: Query, vector results, user context, history

        Returns:
            OrchestrateQueryOutput with full orchestration result

        Flow:
        1. Create OrchestrationResult entity
        2. LLM decides which tools to call
        3. Execute tools (sequentially or parallel)
        4. LLM synthesizes final answer
        5. Mark completed and return
        """
        start_time = datetime.now()
        self._current_query = input_data.query
        self._current_vector_results = input_data.vector_results
        self._current_image_bytes = input_data.image_bytes
        self._current_image_format = input_data.image_format

        # 1. Initialize orchestration result
        result = OrchestrationResult(
            id=str(uuid.uuid4()),
            session_id=input_data.session_id,
            message_id=input_data.message_id,
            query=input_data.query,
            user_context=input_data.user_context,
            vector_reference=VectorSearchReference(
                max_score=input_data.vector_results.get("max_score", 0.0),
                top_chunks=input_data.vector_results.get("top_chunks", []),
                chunk_contents=input_data.vector_results.get("chunk_contents", []),
                search_time_ms=input_data.vector_results.get("search_time_ms", 0),
            ),
            created_at=start_time,
        )

        async def emit(payload: Dict[str, Any]) -> None:
            if event_handler:
                await event_handler(payload)

        try:
            # 2. Ask orchestrator to decide tools
            decision_start = datetime.now()
            await emit({"type": "status", "stage": "deciding_tools"})

            image_info = {
                "present": bool(input_data.image_bytes),
                "format": input_data.image_format or "none",
                "size_bytes": len(input_data.image_bytes or b""),
            }

            tools_to_call = await self.orchestrator.decide_tools(
                query=input_data.query,
                vector_results=input_data.vector_results,
                user_context=input_data.user_context,
                conversation_history=input_data.conversation_history,
                image_info=image_info,
            )

            decision_time = int(
                (datetime.now() - decision_start).total_seconds() * 1000
            )
            result.metrics.orchestrator_decision_time_ms = decision_time

            logger.info(
                f"Orchestrator decided {len(tools_to_call)} tools: "
                f"{[t.tool_type.value for t in tools_to_call]}"
            )
            await emit(
                {
                    "type": "tools_decided",
                    "tools": [
                        {
                            "id": tool.id,
                            "type": tool.tool_type.value,
                            "reasoning": tool.reasoning,
                        }
                        for tool in tools_to_call
                    ],
                }
            )

            # 3. Execute tools
            tools_start = datetime.now()
            await emit({"type": "status", "stage": "executing_tools"})

            for tool_call in tools_to_call:
                result.add_tool_call(tool_call)
                await emit(
                    {
                        "type": "tool_start",
                        "tool": {
                            "id": tool_call.id,
                            "type": tool_call.tool_type.value,
                            "reasoning": tool_call.reasoning,
                        },
                    }
                )
                await self._execute_tool(tool_call)
                await emit(
                    {
                        "type": "tool_end",
                        "tool": {
                            "id": tool_call.id,
                            "type": tool_call.tool_type.value,
                            "reasoning": tool_call.reasoning,
                            "status": tool_call.execution_status.value,
                            "error": tool_call.error_message,
                        },
                        "result": self._summarize_tool_result(tool_call),
                    }
                )

            tools_time = int((datetime.now() - tools_start).total_seconds() * 1000)
            result.metrics.tools_execution_time_ms = tools_time

            # 4. Synthesize final answer
            synthesis_start = datetime.now()
            await emit({"type": "status", "stage": "synthesizing"})

            final_answer = ""
            if event_handler and self.synthesis_llm:
                prompt = self._build_synthesis_prompt(
                    query=input_data.query,
                    tool_results=tools_to_call,
                    user_context=input_data.user_context,
                )
                chunks = []
                async for chunk in self.synthesis_llm.stream_generate(
                    prompt=prompt,
                    mode=LLMMode.QA,
                ):
                    if not chunk:
                        continue
                    chunks.append(chunk)
                    await emit({"type": "answer_chunk", "content": chunk})
                final_answer = "".join(chunks).strip()
            else:
                final_answer = await self.orchestrator.synthesize_response(
                    query=input_data.query,
                    tool_results=tools_to_call,
                    user_context=input_data.user_context,
                )

            synthesis_time = int(
                (datetime.now() - synthesis_start).total_seconds() * 1000
            )
            result.metrics.synthesis_time_ms = synthesis_time

            # 5. Determine confidence and sources
            confidence = self._assess_confidence(tools_to_call)
            sources = self._extract_sources(tools_to_call)

            result.set_final_answer(
                answer=final_answer,
                confidence=confidence,
                sources=sources,
            )
            await emit(
                {
                    "type": "status",
                    "stage": "completed",
                    "confidence": confidence,
                    "sources": sources,
                }
            )

            # 6. Mark completed
            result.mark_completed()

            logger.info(
                f"Orchestration completed in {result.metrics.total_time_ms}ms, "
                f"confidence={confidence}, sources={sources}"
            )

            return OrchestrateQueryOutput(result=result)

        except Exception as e:
            logger.error(f"Orchestration failed: {str(e)}")

            # Set error state
            result.set_final_answer(
                answer=f"Xin lỗi, đã xảy ra lỗi khi xử lý câu hỏi của bạn: {str(e)}",
                confidence="low",
                sources=["error"],
            )
            result.mark_completed()
            await emit({"type": "error", "error": str(e)})

            return OrchestrateQueryOutput(result=result)

    async def _execute_tool(self, tool_call: ToolCall) -> None:
        """
        Execute a single tool.

        Updates tool_call in place with execution result or error.
        """
        try:
            # Inject common context into tool arguments when missing
            if not tool_call.arguments.has("query"):
                tool_call.arguments.raw_args["query"] = self._current_query
            if tool_call.tool_type == ToolType.USE_RAG_CONTEXT:
                if not tool_call.arguments.has("chunk_contents"):
                    tool_call.arguments.raw_args["chunk_contents"] = (
                        self._current_vector_results.get("chunk_contents", [])
                    )
            if tool_call.tool_type == ToolType.ANALYZE_IMAGE:
                if self._current_image_bytes and not tool_call.arguments.has(
                    "image_bytes"
                ):
                    tool_call.arguments.raw_args["image_bytes"] = (
                        self._current_image_bytes
                    )
                if self._current_image_format and not tool_call.arguments.has(
                    "image_format"
                ):
                    tool_call.arguments.raw_args["image_format"] = (
                        self._current_image_format
                    )
                if not tool_call.arguments.has("question"):
                    tool_call.arguments.raw_args["question"] = self._current_query

            tool_call.start_execution()

            result = await self.tool_executor.execute(tool_call)

            tool_call.mark_success(result)

            logger.debug(
                f"Tool {tool_call.tool_type.value} completed in "
                f"{tool_call.execution_time_ms}ms"
            )

        except Exception as e:
            tool_call.mark_failed(str(e))

            logger.error(f"Tool {tool_call.tool_type.value} failed: {str(e)}")

    def _assess_confidence(self, tools: List[ToolCall]) -> str:
        """
        Assess overall confidence based on tool execution.

        Business Rules:
        - All tools success + high score RAG → high
        - Some tools success OR medium score → medium
        - Many failures OR low score RAG → low
        """
        if not tools:
            return "low"

        successful = [t for t in tools if t.is_success()]
        failed = [t for t in tools if t.is_failed()]

        # If any critical tool failed
        if failed:
            return "low"

        # Check RAG tool confidence if used
        rag_tool = next(
            (t for t in successful if t.tool_type == ToolType.USE_RAG_CONTEXT), None
        )

        if rag_tool and rag_tool.has_result():
            rag_confidence = rag_tool.get_result_value("confidence", "medium")
            if rag_confidence == "high":
                return "high"
            elif rag_confidence == "low":
                return "low"

        # Default assessment based on tool success rate
        success_rate = len(successful) / len(tools)

        if success_rate >= 0.9:
            return "high"
        elif success_rate >= 0.5:
            return "medium"
        else:
            return "low"

    def _extract_sources(self, tools: List[ToolCall]) -> List[str]:
        """
        Extract sources used from tool calls.

        Maps tool types to source names for transparency.
        """
        sources = []

        tool_to_source = {
            ToolType.USE_RAG_CONTEXT: "rag",
            ToolType.SEARCH_WEB: "web",
            ToolType.ANSWER_DIRECTLY: "direct",
            ToolType.FILL_FORM: "form",
            ToolType.CLARIFY_QUESTION: "clarification",
        }

        for tool in tools:
            if tool.is_success():
                source = tool_to_source.get(tool.tool_type, tool.tool_type.value)
                if source not in sources:
                    sources.append(source)

        return sources

    @staticmethod
    def _build_synthesis_prompt(
        query: str,
        tool_results: List[ToolCall],
        user_context: Dict[str, Any],
    ) -> str:
        results_summary = ""
        for tool in tool_results:
            if tool.is_success() and tool.execution_result:
                results_summary += f"\n\n**{tool.tool_type.value}:**\n"

                if tool.tool_type == ToolType.USE_RAG_CONTEXT:
                    results_summary += tool.execution_result.get("answer", "")
                    sources = tool.execution_result.get("sources", [])
                    if sources:
                        results_summary += f"\nSources: {sources}"

                elif tool.tool_type == ToolType.SEARCH_WEB:
                    results_summary += tool.execution_result.get("summary", "")
                    urls = tool.execution_result.get("source_urls", [])
                    if urls:
                        results_summary += f"\nURLs: {urls[:3]}"

                elif tool.tool_type == ToolType.ANSWER_DIRECTLY:
                    results_summary += tool.execution_result.get("answer", "")

                elif tool.tool_type == ToolType.FILL_FORM:
                    results_summary += tool.execution_result.get("form_markdown", "")

                elif tool.tool_type == ToolType.CLARIFY_QUESTION:
                    results_summary += tool.execution_result.get(
                        "clarification_prompt", ""
                    )
                    suggestions = tool.execution_result.get("suggestions", [])
                    if suggestions:
                        results_summary += f"\nGợi ý: {suggestions}"

        if not results_summary:
            return "Xin lỗi, không thể xử lý câu hỏi của bạn. Vui lòng thử lại."

        return f"""Based on the tool results below, provide a final answer to the user's question.

**User Question:** {query}

**User Context:**
- Name: {user_context.get('name', 'Unknown')}
- Student ID: {user_context.get('student_id', 'Unknown')}
- Major: {user_context.get('major', 'Unknown')}
- Year: {user_context.get('year', 'Unknown')}
- Class: {user_context.get('class_name', 'Unknown')}
- Faculty: {user_context.get('faculty', 'Unknown')}
- Language preference: {user_context.get('language', 'vi')}

**Tool Results:**
{results_summary}

**Instructions:**
1. Combine information from all tools coherently
2. Use the user's preferred language (Vietnamese if 'vi')
3. If form was generated, include it in the response
4. Add relevant citations if available
5. Be helpful and professional

**Your Final Answer:**"""

    @staticmethod
    def _summarize_tool_result(tool_call: ToolCall) -> Optional[Dict[str, Any]]:
        if not tool_call.execution_result:
            return None

        result = tool_call.execution_result
        if tool_call.tool_type == ToolType.USE_RAG_CONTEXT:
            return {"sources": result.get("sources", [])}
        if tool_call.tool_type == ToolType.SEARCH_WEB:
            return {"source_urls": result.get("source_urls", [])}
        if tool_call.tool_type == ToolType.FILL_FORM:
            return {"form_title": result.get("form_title")}
        if tool_call.tool_type == ToolType.CLARIFY_QUESTION:
            return {"suggestions": result.get("suggestions", [])}
        if tool_call.tool_type == ToolType.ANSWER_DIRECTLY:
            return {"reasoning": result.get("reasoning")}
        return {"result": result}
