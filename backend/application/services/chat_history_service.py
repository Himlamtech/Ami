"""Chat history service - Advanced chat operations."""

from datetime import datetime, timedelta
from app.application.interfaces.repositories.chat_repository import IChatRepository
from app.application.interfaces.services.llm_service import ILLMService


class ChatHistoryService:
    """
    Chat history service for advanced chat operations.

    Handles complex chat workflows like bulk operations, analytics.
    """

    def __init__(
        self,
        chat_repository: IChatRepository,
        llm_service: ILLMService = None,
    ):
        self.chat_repo = chat_repository
        self.llm_service = llm_service

    async def archive_old_sessions(
        self,
        user_id: str,
        days_threshold: int = 30,
    ) -> int:
        """
        Archive sessions older than threshold.

        Returns number of sessions archived.
        """
        sessions = await self.chat_repo.list_sessions_by_user(
            user_id=user_id,
            limit=1000,
            include_archived=False,
        )

        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        archived_count = 0

        for session in sessions:
            if session.updated_at < cutoff_date:
                session.archive()
                await self.chat_repo.update_session(session)
                archived_count += 1

        return archived_count

    async def delete_empty_sessions(self, user_id: str) -> int:
        """
        Delete sessions with no messages.

        Returns number of sessions deleted.
        """
        sessions = await self.chat_repo.list_sessions_by_user(
            user_id=user_id,
            limit=1000,
        )

        deleted_count = 0
        for session in sessions:
            if session.is_empty():
                session.delete()
                await self.chat_repo.update_session(session)
                deleted_count += 1

        return deleted_count

    async def get_user_statistics(self, user_id: str) -> dict:
        """Get chat statistics for user."""
        sessions = await self.chat_repo.list_sessions_by_user(
            user_id=user_id,
            limit=1000,
            include_archived=True,
        )

        total_sessions = len(sessions)
        active_sessions = len(
            [s for s in sessions if not s.is_archived and not s.is_deleted]
        )
        archived_sessions = len([s for s in sessions if s.is_archived])
        total_messages = sum(s.message_count for s in sessions)

        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "archived_sessions": archived_sessions,
            "total_messages": total_messages,
            "avg_messages_per_session": (
                total_messages / total_sessions if total_sessions > 0 else 0
            ),
        }

    async def export_session_history(
        self,
        session_id: str,
        format: str = "json",
    ) -> dict:
        """
        Export session history.

        Formats: json, markdown, txt
        """
        session = await self.chat_repo.get_session_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        messages = await self.chat_repo.list_messages_by_session(
            session_id=session_id,
            limit=1000,
        )

        if format == "json":
            return {
                "session": {
                    "id": session.id,
                    "title": session.title,
                    "created_at": session.created_at.isoformat(),
                },
                "messages": [
                    {
                        "role": msg.role.value,
                        "content": msg.content,
                        "created_at": msg.created_at.isoformat(),
                    }
                    for msg in messages
                ],
            }

        elif format == "markdown":
            lines = [
                f"# {session.title}",
                "",
                f"Session ID: {session.id}",
                f"Created: {session.created_at}",
                "",
                "---",
                "",
            ]

            for msg in messages:
                role_name = msg.role.value.capitalize()
                lines.append(f"## {role_name}")
                lines.append(f"{msg.content}")
                lines.append("")

            return {"content": "\n".join(lines)}

        else:
            raise ValueError(f"Unsupported format: {format}")

    async def bulk_generate_titles(self, user_id: str) -> int:
        """
        Generate titles for sessions without custom titles.

        Returns number of titles generated.
        """
        if not self.llm_service:
            return 0

        sessions = await self.chat_repo.list_sessions_by_user(
            user_id=user_id,
            limit=100,
        )

        generated_count = 0
        for session in sessions:
            # Only generate for default titles
            if session.title == "New Conversation" and session.message_count > 0:
                # Get first few messages
                messages = await self.chat_repo.get_recent_messages(
                    session_id=session.id,
                    limit=3,
                )

                if messages:
                    # Build conversation preview
                    preview = "\n".join(
                        [
                            f"{m.role.value}: {m.content[:100]}"
                            for m in reversed(messages)
                        ]
                    )

                    # Generate title
                    prompt = f"Generate a short title (max 10 words) for this conversation:\n\n{preview}\n\nTitle:"
                    title = await self.llm_service.generate(
                        prompt, temperature=0.3, max_tokens=20
                    )
                    title = title.strip().strip("\"'")

                    # Update session
                    session.update_title(title)
                    await self.chat_repo.update_session(session)
                    generated_count += 1

        return generated_count
