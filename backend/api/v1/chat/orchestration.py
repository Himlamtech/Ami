"""Orchestration routes for query routing with LLM function calling."""

import base64
import logging
import uuid
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, BackgroundTasks

from app.application.use_cases.orchestration.orchestrate_query import (
    OrchestrateQueryUseCase,
    OrchestrateQueryInput,
    OrchestrateQueryOutput,
)
from app.application.use_cases.personalization import (
    ExtractProfileMemoryUseCase,
    ProfileMemoryExtractionInput,
)
from app.application.use_cases.chat import (
    CreateSessionUseCase,
    CreateSessionInput,
    SendMessageUseCase,
    SendMessageInput,
)
from app.domain.enums.chat_message_role import ChatMessageRole
from app.domain.enums.llm_mode import LLMMode
from app.config import ServiceRegistry


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


class OrchestrationRequest:
    """Request model for orchestration endpoint."""

    def __init__(
        self,
        query: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ):
        self.query = query
        self.session_id = session_id
        self.user_id = user_id


class OrchestrationResponse:
    """Response model for orchestration endpoint."""

    def __init__(self, data: dict):
        self.query = data.get("query", "")
        self.tool_calls = data.get("tool_calls", [])
        self.primary_tool = data.get("primary_tool")
        self.final_answer = data.get("final_answer")
        self.vector_reference = data.get("vector_reference")
        self.metrics = data.get("metrics")
        self.success = data.get("success", True)
        self.error = data.get("error")

    def dict(self):
        return {
            "query": self.query,
            "tool_calls": self.tool_calls,
            "primary_tool": self.primary_tool,
            "final_answer": self.final_answer,
            "vector_reference": self.vector_reference,
            "metrics": self.metrics,
            "success": self.success,
            "error": self.error,
        }


@router.post("/orchestrate", response_model=dict)
async def orchestrate_query(request_data: dict, background_tasks: BackgroundTasks):
    """
    Orchestrate a query using LLM function calling.

    Request body:
    {
        "query": "User question",
        "session_id": "optional session ID",
        "user_id": "optional user ID"
    }

    Returns:
    {
        "query": "User question",
        "tool_calls": [
            {
                "tool_type": "use_rag_context",
                "arguments": {...},
                "execution_status": "completed",
                "result": {...}
            }
        ],
        "primary_tool": "use_rag_context",
        "final_answer": "Generated response",
        "vector_reference": {
            "top_score": 0.95,
            "avg_score": 0.88,
            "chunk_count": 5
        },
        "metrics": {
            "decision_time_ms": 150,
            "tool_execution_time_ms": 500,
            "synthesis_time_ms": 200,
            "total_time_ms": 850,
            "tokens_used": 450
        },
        "success": true
    }
    """
    try:
        provided_session_id = request_data.get("session_id")
        session_id = provided_session_id or f"session_{uuid.uuid4()}"
        message_id = request_data.get("message_id") or f"msg_{uuid.uuid4()}"
        request_id = f"req_{uuid.uuid4()}"
        # Validate input
        query = request_data.get("query", "").strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        user_id = request_data.get("user_id")
        vector_results = request_data.get("vector_results", {})
        user_context = request_data.get("user_context", {})
        conversation_history = request_data.get("conversation_history", [])
        image_url = request_data.get("image_url")
        image_base64 = request_data.get("image_base64")
        image_format = request_data.get("image_format")

        if user_id and not user_context:
            user_context = {"user_id": user_id}

        # Get use case
        use_case = ServiceRegistry.get_orchestrate_query_use_case()
        if not use_case:
            raise HTTPException(
                status_code=500,
                detail="Orchestration service not initialized",
            )

        # Execute
        image_bytes = None
        if image_url or image_base64:
            image_bytes, image_format = await _load_image_payload(
                image_url=image_url,
                image_base64=image_base64,
                image_format=image_format,
            )

        input_data = OrchestrateQueryInput(
            query=query,
            session_id=session_id,
            message_id=message_id,
            vector_results=vector_results,
            user_context=user_context,
            conversation_history=conversation_history,
            image_bytes=image_bytes,
            image_format=image_format,
        )

        output = await use_case.execute(input_data)
        result = output.result

        # Convert to response
        successful_tools = result.get_successful_tools()
        primary_tool = None
        if successful_tools:
            primary_tool = successful_tools[0].tool_type.value
        elif result.tools_called:
            primary_tool = result.tools_called[0].tool_type.value

        persisted_session_id = session_id
        assistant_message_id = None
        if user_id:
            persisted_session_id, _, assistant_message_id = await _persist_chat_history(
                user_id=user_id,
                session_id=session_id,
                user_message=query,
                assistant_message=result.final_answer,
                request_id=request_id,
            )

        response_data = {
            "query": result.query,
            "answer": result.final_answer,
            "request_id": request_id,
            "message_id": assistant_message_id or message_id,
            "session_id": persisted_session_id,
            "primary_tool": primary_tool,
            "tools": [
                {
                    "type": tc.tool_type.value,
                    "status": tc.execution_status.value,
                    "reasoning": tc.reasoning,
                    "result": tc.execution_result,
                    "error": tc.error_message,
                }
                for tc in result.tools_called
            ],
            "metrics": (
                {
                    "decision_time_ms": result.metrics.orchestrator_decision_time_ms,
                    "tool_execution_time_ms": result.metrics.tools_execution_time_ms,
                    "synthesis_time_ms": result.metrics.synthesis_time_ms,
                    "total_time_ms": result.metrics.total_time_ms,
                }
                if result.metrics
                else None
            ),
            "success": not result.any_tool_failed(),
            "error": None if not result.any_tool_failed() else "tool_execution_failed",
        }

        if user_id or persisted_session_id:
            background_tasks.add_task(
                _run_profile_memory_extraction,
                user_id=user_id,
                session_id=persisted_session_id,
                user_message=query,
                assistant_message=result.final_answer,
                conversation_history=conversation_history,
            )

        # Log result
        logger.info(
            f"✅ Orchestration success: query='{query[:50]}' "
            f"primary_tool={primary_tool} "
            f"time={result.metrics.total_time_ms if result.metrics else 0}ms"
        )

        return response_data

    except HTTPException as exc:
        detail = exc.detail
        if isinstance(detail, dict):
            detail = {
                **detail,
                "request_id": request_id,
                "session_id": session_id,
                "message_id": message_id,
            }
        else:
            detail = {
                "error": detail,
                "request_id": request_id,
                "session_id": session_id,
                "message_id": message_id,
            }
        raise HTTPException(status_code=exc.status_code, detail=detail)
    except Exception as e:
        logger.error(f"❌ Orchestration error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "request_id": request_id,
                "session_id": session_id,
                "message_id": message_id,
            },
        )


async def _load_image_payload(
    image_url: Optional[str],
    image_base64: Optional[str],
    image_format: Optional[str],
) -> tuple[bytes, str]:
    supported = {"jpg", "jpeg", "png", "webp", "gif"}

    if image_base64:
        if image_base64.startswith("data:image/"):
            header, encoded = image_base64.split(",", 1)
            image_base64 = encoded
            if not image_format and ";" in header:
                image_format = header.split("/")[1].split(";")[0]
        image_bytes = base64.b64decode(image_base64)
    else:
        headers = {"User-Agent": "AMI-Orchestrator/1.0"}
        async with httpx.AsyncClient(timeout=10, headers=headers) as client:
            response = await client.get(image_url)
            response.raise_for_status()
            image_bytes = response.content
            if not image_format:
                content_type = response.headers.get("content-type", "")
                if "image/" in content_type:
                    image_format = content_type.split("image/")[1].split(";")[0]

    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400, detail="Image too large. Maximum size: 10MB"
        )

    if image_format:
        image_format = image_format.lower()
        if image_format == "jpg":
            image_format = "jpeg"
    else:
        image_format = "jpeg"

    if image_format not in supported:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image format: {image_format}. Supported: {', '.join(sorted(supported))}",
        )

    return image_bytes, image_format


async def _run_profile_memory_extraction(
    user_id: Optional[str],
    session_id: Optional[str],
    user_message: str,
    assistant_message: str,
    conversation_history: list,
) -> None:
    try:
        profile_repo = ServiceRegistry.get_student_profile_repository()
        chat_repo = ServiceRegistry.get_chat_repository()
        llm_service = ServiceRegistry.get_llm(mode=LLMMode.QA)
        if not profile_repo:
            return
        use_case = ExtractProfileMemoryUseCase(
            profile_repository=profile_repo,
            llm_service=llm_service,
            chat_repository=chat_repo,
        )
        await use_case.execute(
            ProfileMemoryExtractionInput(
                user_id=user_id,
                session_id=session_id,
                user_message=user_message,
                assistant_message=assistant_message,
                conversation_history=conversation_history or [],
            )
        )
    except Exception as exc:
        logger.warning("Profile memory extraction failed: %s", exc)


async def _persist_chat_history(
    user_id: str,
    session_id: str,
    user_message: str,
    assistant_message: str,
    request_id: str,
) -> tuple[str, Optional[str], Optional[str]]:
    try:
        chat_repo = ServiceRegistry.get_chat_repository()
        if not chat_repo:
            return session_id, None, None

        session = await chat_repo.get_session_by_id(session_id)
        if not session:
            create_use_case = CreateSessionUseCase(chat_repo)
            created = await create_use_case.execute(
                CreateSessionInput(
                    user_id=user_id,
                    session_id=session_id,
                    title="New Conversation",
                )
            )
            session_id = created.session.id

        send_use_case = SendMessageUseCase(chat_repo)
        user_message_id = None
        assistant_message_id = None
        if user_message:
            result = await send_use_case.execute(
                SendMessageInput(
                    session_id=session_id,
                    role=ChatMessageRole.USER,
                    content=user_message,
                    metadata={"source": "orchestrate", "request_id": request_id},
                )
            )
            user_message_id = result.message.id
        if assistant_message:
            result = await send_use_case.execute(
                SendMessageInput(
                    session_id=session_id,
                    role=ChatMessageRole.ASSISTANT,
                    content=assistant_message,
                    metadata={"source": "orchestrate", "request_id": request_id},
                )
            )
            assistant_message_id = result.message.id

        return session_id, user_message_id, assistant_message_id
    except Exception as exc:
        logger.warning("Chat persistence failed: %s", exc)
        return session_id, None, None
