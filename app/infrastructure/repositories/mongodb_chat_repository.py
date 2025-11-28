"""MongoDB Chat Repository implementation."""

from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.domain.entities.chat_session import ChatSession
from app.domain.entities.chat_message import ChatMessage
from app.application.interfaces.repositories.chat_repository import IChatRepository
from app.infrastructure.db.mongodb.mappers import ChatSessionMapper, ChatMessageMapper
from app.core.mongodb_models import ChatSessionInDB, ChatMessageInDB


class MongoDBChatRepository(IChatRepository):
    """MongoDB implementation of Chat Repository."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.sessions_collection = db["chat_sessions"]
        self.messages_collection = db["chat_messages"]
    
    # ===== Session Methods =====
    
    async def create_session(self, session: ChatSession) -> ChatSession:
        """Create new chat session."""
        session_model = ChatSessionMapper.to_model(session)
        session_dict = session_model.dict(by_alias=True, exclude={"id"})
        
        result = await self.sessions_collection.insert_one(session_dict)
        session.id = str(result.inserted_id)
        return session
    
    async def get_session_by_id(self, session_id: str) -> Optional[ChatSession]:
        """Get chat session by ID."""
        try:
            doc = await self.sessions_collection.find_one({"_id": ObjectId(session_id)})
        except:
            return None
        
        if not doc:
            return None
        
        doc["id"] = str(doc.pop("_id"))
        session_model = ChatSessionInDB(**doc)
        return ChatSessionMapper.to_entity(session_model)
    
    async def update_session(self, session: ChatSession) -> ChatSession:
        """Update chat session."""
        session_model = ChatSessionMapper.to_model(session)
        session_dict = session_model.dict(by_alias=True, exclude={"id"})
        
        await self.sessions_collection.update_one(
            {"_id": ObjectId(session.id)},
            {"$set": session_dict}
        )
        
        return session
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete chat session (soft delete)."""
        result = await self.sessions_collection.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"is_deleted": True}}
        )
        return result.modified_count > 0
    
    async def list_sessions_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        include_archived: bool = False,
    ) -> List[ChatSession]:
        """List sessions by user."""
        query = {"user_id": user_id, "is_deleted": False}
        if not include_archived:
            query["is_archived"] = False
        
        cursor = self.sessions_collection.find(query).sort("updated_at", -1).skip(skip).limit(limit)
        sessions = []
        
        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            session_model = ChatSessionInDB(**doc)
            sessions.append(ChatSessionMapper.to_entity(session_model))
        
        return sessions
    
    async def count_sessions_by_user(
        self,
        user_id: str,
        include_archived: bool = False,
    ) -> int:
        """Count sessions by user."""
        query = {"user_id": user_id, "is_deleted": False}
        if not include_archived:
            query["is_archived"] = False
        
        return await self.sessions_collection.count_documents(query)
    
    # ===== Message Methods =====
    
    async def create_message(self, message: ChatMessage) -> ChatMessage:
        """Create new chat message."""
        message_model = ChatMessageMapper.to_model(message)
        message_dict = message_model.dict(by_alias=True, exclude={"id"})
        
        result = await self.messages_collection.insert_one(message_dict)
        message.id = str(result.inserted_id)
        return message
    
    async def get_message_by_id(self, message_id: str) -> Optional[ChatMessage]:
        """Get message by ID."""
        try:
            doc = await self.messages_collection.find_one({"_id": ObjectId(message_id)})
        except:
            return None
        
        if not doc:
            return None
        
        doc["id"] = str(doc.pop("_id"))
        message_model = ChatMessageInDB(**doc)
        return ChatMessageMapper.to_entity(message_model)
    
    async def update_message(self, message: ChatMessage) -> ChatMessage:
        """Update message."""
        message_model = ChatMessageMapper.to_model(message)
        message_dict = message_model.dict(by_alias=True, exclude={"id"})
        
        await self.messages_collection.update_one(
            {"_id": ObjectId(message.id)},
            {"$set": message_dict}
        )
        
        return message
    
    async def delete_message(self, message_id: str) -> bool:
        """Delete message (soft delete)."""
        result = await self.messages_collection.update_one(
            {"_id": ObjectId(message_id)},
            {"$set": {"is_deleted": True}}
        )
        return result.modified_count > 0
    
    async def list_messages_by_session(
        self,
        session_id: str,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> List[ChatMessage]:
        """List messages by session."""
        query = {"session_id": session_id}
        if not include_deleted:
            query["is_deleted"] = False
        
        cursor = self.messages_collection.find(query).sort("created_at", 1).skip(skip).limit(limit)
        messages = []
        
        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            message_model = ChatMessageInDB(**doc)
            messages.append(ChatMessageMapper.to_entity(message_model))
        
        return messages
    
    async def count_messages_by_session(
        self,
        session_id: str,
        include_deleted: bool = False,
    ) -> int:
        """Count messages in session."""
        query = {"session_id": session_id}
        if not include_deleted:
            query["is_deleted"] = False
        
        return await self.messages_collection.count_documents(query)
    
    async def get_recent_messages(
        self,
        session_id: str,
        limit: int = 10,
    ) -> List[ChatMessage]:
        """Get recent messages from session."""
        cursor = self.messages_collection.find(
            {"session_id": session_id, "is_deleted": False}
        ).sort("created_at", -1).limit(limit)
        
        messages = []
        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            message_model = ChatMessageInDB(**doc)
            messages.append(ChatMessageMapper.to_entity(message_model))
        
        return messages
