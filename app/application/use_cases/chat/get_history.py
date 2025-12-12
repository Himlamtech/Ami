"""Get chat history use case."""

from dataclasses import dataclass
from typing import List
from app.domain.entities.chat_session import ChatSession
from app.domain.entities.chat_message import ChatMessage
from app.domain.exceptions.chat_exceptions import ChatSessionNotFoundException
from app.application.interfaces.repositories.chat_repository import IChatRepository


@dataclass
class GetHistoryInput:
    """Input for get history use case."""

    session_id: str
    limit: int = 50
    skip: int = 0


@dataclass
class GetHistoryOutput:
    """Output from get history use case."""

    session: ChatSession
    messages: List[ChatMessage]
    total_messages: int


class GetHistoryUseCase:
    """
    Use Case: Get chat history for a session.

    Business Rules:
    1. Session must exist
    2. Return messages with pagination
    3. Exclude deleted messages by default

    Single Responsibility: Retrieve chat history
    """

    def __init__(self, chat_repository: IChatRepository):
        self.chat_repo = chat_repository

    async def execute(self, input_data: GetHistoryInput) -> GetHistoryOutput:
        """
        Get chat history.

        Args:
            input_data: History request parameters

        Returns:
            GetHistoryOutput with session and messages

        Raises:
            ChatSessionNotFoundException: Session doesn't exist
        """
        # 1. Get session
        session = await self.chat_repo.get_session_by_id(input_data.session_id)
        if not session:
            raise ChatSessionNotFoundException(session_id=input_data.session_id)

        # 2. Get messages with pagination
        messages = await self.chat_repo.list_messages_by_session(
            session_id=input_data.session_id,
            skip=input_data.skip,
            limit=input_data.limit,
            include_deleted=False,
        )

        # 3. Get total count
        total_count = await self.chat_repo.count_messages_by_session(
            session_id=input_data.session_id,
            include_deleted=False,
        )

        return GetHistoryOutput(
            session=session,
            messages=messages,
            total_messages=total_count,
        )
