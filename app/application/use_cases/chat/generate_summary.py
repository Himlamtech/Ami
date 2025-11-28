"""Generate chat summary use case."""

from dataclasses import dataclass
from typing import List
from app.domain.entities.chat_session import ChatSession
from app.domain.entities.chat_message import ChatMessage
from app.domain.exceptions.chat_exceptions import ChatSessionNotFoundException
from app.application.interfaces.repositories.chat_repository import IChatRepository
from app.application.interfaces.services.llm_service import ILLMService


@dataclass
class GenerateSummaryInput:
    """Input for generate summary use case."""
    session_id: str
    max_length: int = 200


@dataclass
class GenerateSummaryOutput:
    """Output from generate summary use case."""
    session: ChatSession
    summary: str
    title: str


class GenerateSummaryUseCase:
    """
    Use Case: Generate AI summary for chat session.
    
    Business Rules:
    1. Session must exist and have messages
    2. Use recent messages for context
    3. Generate both title and summary
    4. Update session with generated summary
    
    Single Responsibility: Generate and save chat summary
    """
    
    def __init__(
        self,
        chat_repository: IChatRepository,
        llm_service: ILLMService,
    ):
        self.chat_repo = chat_repository
        self.llm_service = llm_service
    
    async def execute(self, input_data: GenerateSummaryInput) -> GenerateSummaryOutput:
        """
        Generate summary for session.
        
        Args:
            input_data: Summary generation parameters
            
        Returns:
            GenerateSummaryOutput with updated session and summary
            
        Raises:
            ChatSessionNotFoundException: Session doesn't exist
        """
        # 1. Get session
        session = await self.chat_repo.get_session_by_id(input_data.session_id)
        if not session:
            raise ChatSessionNotFoundException(session_id=input_data.session_id)
        
        # 2. Get recent messages (last 10)
        messages = await self.chat_repo.get_recent_messages(
            session_id=input_data.session_id,
            limit=10,
        )
        
        if not messages:
            # No messages to summarize
            return GenerateSummaryOutput(
                session=session,
                summary="",
                title=session.title,
            )
        
        # 3. Build conversation context
        conversation = self._build_conversation_text(messages)
        
        # 4. Generate title (short summary for title)
        title_prompt = f"""Generate a SHORT title (max 10 words) for this conversation:

{conversation}

Title:"""
        
        title = await self.llm_service.generate(
            prompt=title_prompt,
            temperature=0.3,
            max_tokens=50,
        )
        title = title.strip().strip('"\'')
        
        # 5. Generate summary
        summary_prompt = f"""Summarize the following conversation in {input_data.max_length} characters or less:

{conversation}

Summary:"""
        
        summary = await self.llm_service.generate(
            prompt=summary_prompt,
            temperature=0.3,
            max_tokens=input_data.max_length,
        )
        summary = summary.strip()
        
        # 6. Update session with summary (business logic)
        session.update_title(title)
        session.update_summary(summary)
        
        # 7. Persist updates
        updated_session = await self.chat_repo.update_session(session)
        
        return GenerateSummaryOutput(
            session=updated_session,
            summary=summary,
            title=title,
        )
    
    def _build_conversation_text(self, messages: List[ChatMessage]) -> str:
        """Build conversation text from messages."""
        lines = []
        for msg in reversed(messages):  # Reverse to chronological order
            role_name = msg.role.value.capitalize()
            lines.append(f"{role_name}: {msg.content}")
        return "\n".join(lines)
