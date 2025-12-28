"""
Gemini-based Orchestrator Service.

Uses Gemini's function calling to intelligently decide which tools to use.
Reads config from gemini_config (NOT hardcoded).
"""

import json
import logging
import uuid
from typing import List, Dict, Any

import google.genai as genai
from google.genai import types

from config import gemini_config
from config.ai import GeminiConfig
from domain.entities.tool_call import ToolCall, ToolArguments
from domain.enums.tool_type import ToolType
from application.interfaces.services.orchestrator_service import (
    IOrchestratorService,
)
from .tool_definitions import TOOL_DEFINITIONS, ORCHESTRATOR_SYSTEM_PROMPT


logger = logging.getLogger(__name__)


class GeminiOrchestratorService(IOrchestratorService):
    """
    Gemini-based Query Orchestrator.

    Uses Gemini's function calling capability to decide which tools to use.

    Key Features:
    - Reads model from config (gemini_config.model_reasoning)
    - Vector scores are REFERENCE, not hard rules
    - LLM makes intelligent decisions based on full context
    - Can call multiple tools if needed
    """

    def __init__(self, config: GeminiConfig = None):
        """
        Initialize Gemini Orchestrator.

        Args:
            config: Gemini configuration. If None, uses global gemini_config.
        """
        self.config = config or gemini_config
        self._client = genai.Client(api_key=self.config.api_key)

        # Use reasoning model for orchestration decisions
        self._orchestrator_model = self.config.model_reasoning

        # Build function declarations for Gemini
        self._tools = self._build_tool_declarations()

        logger.info(
            f"Gemini Orchestrator initialized with model: {self._orchestrator_model}"
        )

    def _build_tool_declarations(self) -> List[types.Tool]:
        """
        Build Gemini tool declarations from TOOL_DEFINITIONS.

        Converts our tool schemas to Gemini's FunctionDeclaration format.
        """
        function_declarations = []

        for tool_def in TOOL_DEFINITIONS:
            func_decl = types.FunctionDeclaration(
                name=tool_def["name"],
                description=tool_def["description"],
                parameters=tool_def["parameters"],
            )
            function_declarations.append(func_decl)

        return [types.Tool(function_declarations=function_declarations)]

    def _build_system_prompt(
        self,
        query: str,
        vector_results: Dict[str, Any],
        user_context: Dict[str, Any],
        conversation_history: List[Dict[str, Any]],
        image_info: Dict[str, Any],
    ) -> str:
        """
        Build system prompt with all context for the orchestrator.

        Emphasizes that vector scores are REFERENCE only.
        """
        # Extract vector info
        max_score = vector_results.get("max_score", 0.0)
        top_chunks = vector_results.get("top_chunks", [])
        chunk_contents = vector_results.get("chunk_contents", [])

        # Build chunks preview
        chunks_preview = ""
        for i, chunk in enumerate(chunk_contents[:3]):  # First 3 chunks
            content = chunk.get("content", "")[:200]  # First 200 chars
            title = chunk.get("title", "Unknown")
            chunks_preview += f"\n  [{i+1}] {title}: {content}..."

        if not chunks_preview:
            chunks_preview = "\n  (No relevant chunks found)"

        # Format conversation history
        history_str = ""
        for msg in conversation_history[-5:]:  # Last 5 messages
            role = msg.get("role", "unknown")
            content = msg.get("content", "")[:100]
            history_str += f"\n  {role}: {content}..."

        if not history_str:
            history_str = "\n  (No previous messages)"

        return ORCHESTRATOR_SYSTEM_PROMPT.format(
            query=query,
            name=user_context.get("name", "Unknown"),
            student_id=user_context.get("student_id", "Unknown"),
            major=user_context.get("major", "Unknown"),
            year=user_context.get("year", "Unknown"),
            class_name=user_context.get("class_name", "Unknown"),
            faculty=user_context.get("faculty", "Unknown"),
            language=user_context.get("language", "vi"),
            max_score=f"{max_score:.2f}",
            top_chunks_preview=chunks_preview,
            conversation_history=history_str,
            image_present=image_info.get("present", False),
            image_format=image_info.get("format", "none"),
            image_size=image_info.get("size_bytes", 0),
        )

    async def decide_tools(
        self,
        query: str,
        vector_results: Dict[str, Any],
        user_context: Dict[str, Any],
        conversation_history: List[Dict[str, Any]],
        image_info: Dict[str, Any] = None,
    ) -> List[ToolCall]:
        """
        Use Gemini function calling to decide which tools to use.

        Args:
            query: User's query
            vector_results: Vector search results (REFERENCE only)
            user_context: User profile info
            conversation_history: Recent messages

        Returns:
            List of ToolCall entities to execute
        """
        try:
            # Build system prompt with all context
            system_prompt = self._build_system_prompt(
                query,
                vector_results,
                user_context,
                conversation_history,
                image_info or {"present": False},
            )

            logger.debug(
                f"Orchestrator prompt built, calling {self._orchestrator_model}"
            )

            # Call Gemini with function calling
            response = await self._client.aio.models.generate_content(
                model=self._orchestrator_model,
                contents=[
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=system_prompt)],
                    ),
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=f"User query: {query}")],
                    ),
                ],
                config=types.GenerateContentConfig(
                    temperature=0.0,  # Deterministic decisions
                    tools=self._tools,
                    tool_config=types.ToolConfig(
                        function_calling_config=types.FunctionCallingConfig(
                            mode="AUTO"  # Let Gemini decide when to call functions
                        )
                    ),
                ),
            )

            # Parse function calls from response
            tool_calls = self._parse_function_calls(response)

            if not tool_calls:
                # If no tools called, default to answer_directly
                logger.warning(
                    "No tools called by orchestrator, defaulting to answer_directly"
                )
                tool_calls = [
                    ToolCall(
                        id=str(uuid.uuid4()),
                        tool_type=ToolType.ANSWER_DIRECTLY,
                        arguments=ToolArguments(
                            raw_args={
                                "answer": "",  # Will be filled by executor
                                "reason": "Orchestrator did not select specific tools",
                            }
                        ),
                        reasoning="Default fallback - orchestrator did not call any tools",
                    )
                ]

            logger.info(
                f"Orchestrator decided {len(tool_calls)} tools: "
                f"{[t.tool_type.value for t in tool_calls]}"
            )

            return tool_calls

        except Exception as e:
            logger.error(f"Orchestrator error: {e}")

            # Fallback to RAG if orchestrator fails
            return [
                ToolCall(
                    id=str(uuid.uuid4()),
                    tool_type=ToolType.USE_RAG_CONTEXT,
                    arguments=ToolArguments(
                        raw_args={
                            "chunk_ids": vector_results.get("top_chunks", [])[:3],
                            "confidence": "low",
                            "reason": f"Fallback due to orchestrator error: {str(e)}",
                        }
                    ),
                    reasoning=f"Fallback due to error: {str(e)}",
                )
            ]

    def _parse_function_calls(self, response) -> List[ToolCall]:
        """
        Parse Gemini response to extract function calls.

        Returns list of ToolCall entities.
        """
        tool_calls = []

        try:
            # Check if response has candidates with function calls
            if not response.candidates:
                return tool_calls

            for candidate in response.candidates:
                if not candidate.content or not candidate.content.parts:
                    continue

                for part in candidate.content.parts:
                    # Check for function call
                    if hasattr(part, "function_call") and part.function_call:
                        func_call = part.function_call

                        # Get tool type
                        try:
                            tool_type = ToolType(func_call.name)
                        except ValueError:
                            logger.warning(f"Unknown tool type: {func_call.name}")
                            continue

                        # Extract arguments
                        args = {}
                        if func_call.args:
                            # Convert MapComposite to dict
                            args = dict(func_call.args)

                        tool_call = ToolCall(
                            id=str(uuid.uuid4()),
                            tool_type=tool_type,
                            arguments=ToolArguments(raw_args=args),
                            reasoning=args.get("reason", ""),
                        )

                        tool_calls.append(tool_call)

                        logger.debug(
                            f"Parsed tool call: {tool_type.value} with args: {args}"
                        )

        except Exception as e:
            logger.error(f"Error parsing function calls: {e}")

        return tool_calls

    async def synthesize_response(
        self,
        query: str,
        tool_results: List[ToolCall],
        user_context: Dict[str, Any],
    ) -> str:
        """
        Synthesize final answer from tool results.

        Uses Gemini to combine outputs from all tools into a coherent answer.
        """
        try:
            # Build synthesis prompt
            results_summary = ""
            for tool in tool_results:
                if tool.is_success() and tool.execution_result:
                    results_summary += f"\n\n**{tool.tool_type.value}:**\n"

                    # Format based on tool type
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
                        results_summary += tool.execution_result.get(
                            "form_markdown", ""
                        )

                    elif tool.tool_type == ToolType.CLARIFY_QUESTION:
                        results_summary += tool.execution_result.get(
                            "clarification_prompt", ""
                        )
                        suggestions = tool.execution_result.get("suggestions", [])
                        if suggestions:
                            results_summary += f"\nGợi ý: {suggestions}"

            if not results_summary:
                return "Xin lỗi, không thể xử lý câu hỏi của bạn. Vui lòng thử lại."

            # Synthesis prompt
            synthesis_prompt = f"""Based on the tool results below, provide a final answer to the user's question.

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

            # Call Gemini for synthesis
            response = await self._client.aio.models.generate_content(
                model=self.config.model_qa,  # Use QA model for synthesis (faster)
                contents=synthesis_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=4096,
                ),
            )

            return response.text or "Không thể tổng hợp câu trả lời."

        except Exception as e:
            logger.error(f"Synthesis error: {e}")

            # Return the first successful tool result as fallback
            for tool in tool_results:
                if tool.is_success() and tool.execution_result:
                    if "answer" in tool.execution_result:
                        return tool.execution_result["answer"]
                    if "form_markdown" in tool.execution_result:
                        return tool.execution_result["form_markdown"]

            return f"Đã xảy ra lỗi khi xử lý: {str(e)}"
