"""MongoDB User Repository implementation."""

from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.domain.entities.user import User
from app.domain.exceptions.user_exceptions import UserAlreadyExistsException
from app.application.interfaces.repositories.user_repository import IUserRepository
from app.infrastructure.db.mongodb.mappers import UserMapper
from app.core.mongodb_models import UserInDB


class MongoDBUserRepository(IUserRepository):
    """MongoDB implementation of User Repository."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["users"]
    
    async def create(self, user: User) -> User:
        """Create new user."""
        # Check if username or email exists
        if await self.exists_by_username(user.username):
            raise UserAlreadyExistsException(username=user.username)
        
        if await self.exists_by_email(user.email):
            raise UserAlreadyExistsException(email=user.email)
        
        # Convert to model
        user_model = UserMapper.to_model(user)
        user_dict = user_model.dict(by_alias=True, exclude={"id"})
        
        # Insert
        result = await self.collection.insert_one(user_dict)
        
        # Return with generated ID
        user.id = str(result.inserted_id)
        return user
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(user_id)})
        except:
            return None
        
        if not doc:
            return None
        
        doc["id"] = str(doc.pop("_id"))
        user_model = UserInDB(**doc)
        return UserMapper.to_entity(user_model)
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        doc = await self.collection.find_one({"username": username})
        if not doc:
            return None
        
        doc["id"] = str(doc.pop("_id"))
        user_model = UserInDB(**doc)
        return UserMapper.to_entity(user_model)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        doc = await self.collection.find_one({"email": email})
        if not doc:
            return None
        
        doc["id"] = str(doc.pop("_id"))
        user_model = UserInDB(**doc)
        return UserMapper.to_entity(user_model)
    
    async def update(self, user: User) -> User:
        """Update user."""
        user_model = UserMapper.to_model(user)
        user_dict = user_model.dict(by_alias=True, exclude={"id"})
        
        await self.collection.update_one(
            {"_id": ObjectId(user.id)},
            {"$set": user_dict}
        )
        
        return user
    
    async def delete(self, user_id: str) -> bool:
        """Delete user."""
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0
    
    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ) -> List[User]:
        """List users with pagination."""
        query = {}
        if is_active is not None:
            query["is_active"] = is_active
        
        cursor = self.collection.find(query).skip(skip).limit(limit)
        users = []
        
        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            user_model = UserInDB(**doc)
            users.append(UserMapper.to_entity(user_model))
        
        return users
    
    async def count(self, is_active: Optional[bool] = None) -> int:
        """Count users."""
        query = {}
        if is_active is not None:
            query["is_active"] = is_active
        
        return await self.collection.count_documents(query)
    
    async def exists_by_username(self, username: str) -> bool:
        """Check if username exists."""
        count = await self.collection.count_documents({"username": username})
        return count > 0
    
    async def exists_by_email(self, email: str) -> bool:
        """Check if email exists."""
        count = await self.collection.count_documents({"email": email})
        return count > 0
