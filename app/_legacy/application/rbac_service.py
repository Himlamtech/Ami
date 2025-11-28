"""
RBAC Service - Business logic for role and permission management.
"""

import logging
from typing import List, Optional

from app.core.mongodb_models import UserInDB
from app.core.rbac_models import (
    PREDEFINED_PERMISSIONS,
    PREDEFINED_ROLES,
    Permission,
    Role,
    RoleCreate,
    RoleUpdate,
)
from app.infrastructure.databases.mongodb_client import MongoDBClient

logger = logging.getLogger(__name__)


class RBACService:
    """Service for role-based access control operations."""
    
    def __init__(self, mongodb: MongoDBClient):
        self.mongodb = mongodb
        self.db = mongodb.db
        
    async def initialize(self):
        """Initialize RBAC system with predefined roles and permissions."""
        logger.info("Initializing RBAC system...")
        
        # Create permissions collection if not exists
        collections = await self.db.list_collection_names()
        if "permissions" not in collections:
            await self.db.create_collection("permissions")
            logger.info("Created permissions collection")
            
        if "roles" not in collections:
            await self.db.create_collection("roles")
            logger.info("Created roles collection")
            
        # Insert predefined permissions
        existing_perms = await self.db.permissions.count_documents({})
        if existing_perms == 0:
            perm_docs = [p.dict() for p in PREDEFINED_PERMISSIONS]
            await self.db.permissions.insert_many(perm_docs)
            logger.info(f"Inserted {len(perm_docs)} predefined permissions")
        
        # Insert predefined roles
        existing_roles = await self.db.roles.count_documents({})
        if existing_roles == 0:
            role_docs = [r.dict() for r in PREDEFINED_ROLES]
            await self.db.roles.insert_many(role_docs)
            logger.info(f"Inserted {len(role_docs)} predefined roles")
            
        logger.info("✓ RBAC system initialized")
        
    # ============= Permission Methods =============
    
    async def get_all_permissions(self) -> List[Permission]:
        """Get all permissions."""
        cursor = self.db.permissions.find()
        perms_data = await cursor.to_list(length=None)
        return [Permission(**p) for p in perms_data]
    
    async def get_permission_by_id(self, permission_id: str) -> Optional[Permission]:
        """Get permission by ID."""
        perm_data = await self.db.permissions.find_one({"id": permission_id})
        if perm_data:
            return Permission(**perm_data)
        return None
    
    # ============= Role Methods =============
    
    async def list_roles(self) -> List[Role]:
        """List all roles."""
        cursor = self.db.roles.find()
        roles_data = await cursor.to_list(length=None)
        return [Role(**r) for r in roles_data]
    
    async def get_role_by_id(self, role_id: str) -> Optional[Role]:
        """Get role by ID."""
        role_data = await self.db.roles.find_one({"id": role_id})
        if role_data:
            return Role(**role_data)
        return None
    
    async def create_role(self, role_create: RoleCreate, created_by: str) -> Role:
        """Create a new custom role."""
        from datetime import datetime
        import uuid
        
        # Validate permissions exist
        for perm_id in role_create.permissions:
            perm = await self.get_permission_by_id(perm_id)
            if not perm:
                raise ValueError(f"Permission {perm_id} does not exist")
        
        role = Role(
            id=f"role_{uuid.uuid4().hex[:8]}",
            name=role_create.name,
            description=role_create.description,
            permissions=role_create.permissions,
            is_system_role=False,
            created_by=created_by,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        await self.db.roles.insert_one(role.dict())
        logger.info(f"Created role: {role.name} (ID: {role.id})")
        return role
    
    async def update_role(self, role_id: str, role_update: RoleUpdate) -> Role:
        \"\"\"Update existing role.\"\"\"
        from datetime import datetime
        
        role = await self.get_role_by_id(role_id)
        if not role:
            raise ValueError(f"Role {role_id} not found")
            
        if role.is_system_role:
            raise ValueError("Cannot update system roles")
        
        # Validate permissions if being updated
        if role_update.permissions is not None:
            for perm_id in role_update.permissions:
                perm = await self.get_permission_by_id(perm_id)
                if not perm:
                    raise ValueError(f"Permission {perm_id} does not exist")
        
        # Build update dict
        update_data = {}
        if role_update.name is not None:
            update_data["name"] = role_update.name
        if role_update.description is not None:
            update_data["description"] = role_update.description
        if role_update.permissions is not None:
            update_data["permissions"] = role_update.permissions
        update_data["updated_at"] = datetime.now()
        
        await self.db.roles.update_one(
            {"id": role_id},
            {"$set": update_data}
        )
        
        # Fetch updated role
        updated_role = await self.get_role_by_id(role_id)
        logger.info(f"Updated role: {role_id}")
        return updated_role
    
    async def delete_role(self, role_id: str):
        \"\"\"Delete a custom role.\"\"\"
        role = await self.get_role_by_id(role_id)
        if not role:
            raise ValueError(f"Role {role_id} not found")
            
        if role.is_system_role:
            raise ValueError("Cannot delete system roles")
        
        # Remove role from all users
        await self.db.users.update_many(
            {"role_ids": role_id},
            {"$pull": {"role_ids": role_id}}
        )
        
        await self.db.roles.delete_one({"id": role_id})
        logger.info(f"Deleted role: {role_id}")
    
    # ============= User Permission Methods =============
    
    async def assign_roles_to_user(self, user_id: str, role_ids: List[str]):
        \"\"\"Assign roles to a user.\"\"\"
        from datetime import datetime
        
        # Validate roles exist
        for role_id in role_ids:
            role = await self.get_role_by_id(role_id)
            if not role:
                raise ValueError(f"Role {role_id} does not exist")
        
        await self.db.users.update_one(
            {"id": user_id},
            {
                "$set": {
                    "role_ids": role_ids,
                    "updated_at": datetime.now()
                }
            }
        )
        logger.info(f"Assigned roles {role_ids} to user {user_id}")
    
    async def get_user_permissions(self, user: UserInDB) -> List[str]:
        \"\"\"Get all permissions for a user based on their roles.\"\"\"
        if not user.role_ids:
            return []
        
        all_permissions = set()
        
        for role_id in user.role_ids:
            role = await self.get_role_by_id(role_id)
            if role:
                # Handle wildcard permission
                if "*" in role.permissions:
                    # Get all permission IDs
                    all_perms = await self.get_all_permissions()
                    all_permissions.update([p.id for p in all_perms])
                else:
                    all_permissions.update(role.permissions)
        
        return list(all_permissions)
    
    async def has_permission(self, user: UserInDB, permission_id: str) -> bool:
        \"\"\"Check if user has a specific permission.\"\"\"
        # Super admin bypass (if is_admin flag is still used)
        if user.is_admin:
            return True
            
        user_permissions = await self.get_user_permissions(user)
        return permission_id in user_permissions
    
    async def has_any_permission(self, user: UserInDB, permission_ids: List[str]) -> bool:
        \"\"\"Check if user has any of the specified permissions.\"\"\"
        user_permissions = await self.get_user_permissions(user)
        return any(p in user_permissions for p in permission_ids)
    
    async def has_all_permissions(self, user: UserInDB, permission_ids: List[str]) -> bool:
        \"\"\"Check if user has all of the specified permissions.\"\"\"
        user_permissions = await self.get_user_permissions(user)
        return all(p in user_permissions for p in permission_ids)
