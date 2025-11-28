"""
RBAC (Role-Based Access Control) models.
Defines roles, permissions, and access control structures.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PermissionAction(str, Enum):
    """Standard CRUD actions for permissions."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"  # For special actions
    

class PermissionResource(str, Enum):
    """System resources that can be protected."""
    USERS = "users"
    ROLES = "roles"
    DOCUMENTS = "documents"
    COLLECTIONS = "collections"
    CHAT_SESSIONS = "chat_sessions"
    CHAT_MESSAGES = "chat_messages"
    ANALYTICS = "analytics"
    SETTINGS = "settings"
    LOGS = "logs"
    INTEGRATIONS = "integrations"
    PROMPTS = "prompts"
    KNOWLEDGE_BASE = "knowledge_base"


class Permission(BaseModel):
    """
    Permission model defining what action can be performed on what resource.
    
    Format: {resource}:{action}
    Examples: "users:create", "documents:delete", "analytics:read"
    """
    id: str = Field(..., description="Unique permission ID")
    name: str = Field(..., description="Human-readable permission name")
    resource: PermissionResource
    action: PermissionAction
    description: str = Field(..., description="What this permission allows")
    
    @property
    def permission_string(self) -> str:
        """Get permission in format: resource:action"""
        return f"{self.resource.value}:{self.action.value}"
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "perm_users_create",
                "name": "Create Users",
                "resource": "users",
                "action": "create",
                "description": "Allows creating new user accounts"
            }
        }


class Role(BaseModel):
    """
    Role model defining a set of permissions.
    Users are assigned roles to grant them access.
    """
    id: str = Field(..., description="Unique role ID")
    name: str = Field(..., description="Role name")
    description: Optional[str] = Field(None, description="Role description")
    permissions: List[str] = Field(default_factory=list, description="List of permission IDs")
    is_system_role: bool = Field(default=False, description="System roles cannot be deleted")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[str] = Field(None, description="User ID who created this role")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "role_admin",
                "name": "Administrator",
                "description": "Full system access",
                "permissions": ["*"],  # Wildcard for all permissions
                "is_system_role": True,
                "created_at": "2025-11-19T00:00:00",
                "updated_at": "2025-11-19T00:00:00"
            }
        }


class RoleCreate(BaseModel):
    """Request model for creating a new role."""
    name: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    permissions: List[str] = Field(default_factory=list)
    

class RoleUpdate(BaseModel):
    """Request model for updating a role."""
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = None
    permissions: Optional[List[str]] = None


class RoleListResponse(BaseModel):
    """Response model for listing roles."""
    roles: List[Role]
    total: int


class UserRoleAssignment(BaseModel):
    """Model for assigning roles to users."""
    user_id: str
    role_ids: List[str]
    assigned_by: str
    assigned_at: datetime = Field(default_factory=datetime.now)


# ============= PREDEFINED PERMISSIONS =============

PREDEFINED_PERMISSIONS = [
    # User Management
    Permission(
        id="perm_users_create",
        name="Create Users",
        resource=PermissionResource.USERS,
        action=PermissionAction.CREATE,
        description="Create new user accounts"
    ),
    Permission(
        id="perm_users_read",
        name="View Users",
        resource=PermissionResource.USERS,
        action=PermissionAction.READ,
        description="View user information"
    ),
    Permission(
        id="perm_users_update",
        name="Update Users",
        resource=PermissionResource.USERS,
        action=PermissionAction.UPDATE,
        description="Update user accounts"
    ),
    Permission(
        id="perm_users_delete",
        name="Delete Users",
        resource=PermissionResource.USERS,
        action=PermissionAction.DELETE,
        description="Delete user accounts"
    ),
    
    # Role Management
    Permission(
        id="perm_roles_create",
        name="Create Roles",
        resource=PermissionResource.ROLES,
        action=PermissionAction.CREATE,
        description="Create new roles"
    ),
    Permission(
        id="perm_roles_read",
        name="View Roles",
        resource=PermissionResource.ROLES,
        action=PermissionAction.READ,
        description="View role information"
    ),
    Permission(
        id="perm_roles_update",
        name="Update Roles",
        resource=PermissionResource.ROLES,
        action=PermissionAction.UPDATE,
        description="Update role permissions"
    ),
    Permission(
        id="perm_roles_delete",
        name="Delete Roles",
        resource=PermissionResource.ROLES,
        action=PermissionAction.DELETE,
        description="Delete roles"
    ),
    
    # Document Management
    Permission(
        id="perm_documents_create",
        name="Upload Documents",
        resource=PermissionResource.DOCUMENTS,
        action=PermissionAction.CREATE,
        description="Upload new documents"
    ),
    Permission(
        id="perm_documents_read",
        name="View Documents",
        resource=PermissionResource.DOCUMENTS,
        action=PermissionAction.READ,
        description="View documents"
    ),
    Permission(
        id="perm_documents_update",
        name="Update Documents",
        resource=PermissionResource.DOCUMENTS,
        action=PermissionAction.UPDATE,
        description="Update document metadata"
    ),
    Permission(
        id="perm_documents_delete",
        name="Delete Documents",
        resource=PermissionResource.DOCUMENTS,
        action=PermissionAction.DELETE,
        description="Delete documents"
    ),
    
    # Chat Management
    Permission(
        id="perm_chat_create",
        name="Create Chat Sessions",
        resource=PermissionResource.CHAT_SESSIONS,
        action=PermissionAction.CREATE,
        description="Start new chat sessions"
    ),
    Permission(
        id="perm_chat_read_own",
        name="View Own Chats",
        resource=PermissionResource.CHAT_SESSIONS,
        action=PermissionAction.READ,
        description="View own chat sessions"
    ),
    Permission(
        id="perm_chat_read_all",
        name="View All Chats",
        resource=PermissionResource.CHAT_SESSIONS,
        action=PermissionAction.EXECUTE,
        description="View all users' chat sessions (Admin)"
    ),
    Permission(
        id="perm_chat_delete",
        name="Delete Chat Sessions",
        resource=PermissionResource.CHAT_SESSIONS,
        action=PermissionAction.DELETE,
        description="Delete chat sessions"
    ),
    
    # Analytics
    Permission(
        id="perm_analytics_read",
        name="View Analytics",
        resource=PermissionResource.ANALYTICS,
        action=PermissionAction.READ,
        description="View usage analytics and reports"
    ),
    
    # Settings
    Permission(
        id="perm_settings_read",
        name="View Settings",
        resource=PermissionResource.SETTINGS,
        action=PermissionAction.READ,
        description="View system settings"
    ),
    Permission(
        id="perm_settings_update",
        name="Update Settings",
        resource=PermissionResource.SETTINGS,
        action=PermissionAction.UPDATE,
        description="Update system settings"
    ),
    
    # Logs
    Permission(
        id="perm_logs_read",
        name="View Logs",
        resource=PermissionResource.LOGS,
        action=PermissionAction.READ,
        description="View system logs and audit trails"
    ),
]


# ============= PREDEFINED ROLES =============

PREDEFINED_ROLES = [
    Role(
        id="role_super_admin",
        name="Super Administrator",
        description="Full system access - all permissions",
        permissions=["*"],  # Wildcard for all permissions
        is_system_role=True
    ),
    Role(
        id="role_admin",
        name="Administrator",
        description="Manage users, content, and view analytics",
        permissions=[
            "perm_users_create", "perm_users_read", "perm_users_update", "perm_users_delete",
            "perm_roles_read",
            "perm_documents_create", "perm_documents_read", "perm_documents_update", "perm_documents_delete",
            "perm_chat_read_all", "perm_chat_delete",
            "perm_analytics_read",
            "perm_settings_read",
            "perm_logs_read"
        ],
        is_system_role=True
    ),
    Role(
        id="role_power_user",
        name="Power User",
        description="Full chat access, document upload, view own analytics",
        permissions=[
            "perm_users_read",  # Can view users
            "perm_documents_create", "perm_documents_read", "perm_documents_update",
            "perm_chat_create", "perm_chat_read_own",
        ],
        is_system_role=True
    ),
    Role(
        id="role_analyst",
        name="Analyst",
        description="View analytics and reports, read-only access to data",
        permissions=[
            "perm_users_read",
            "perm_documents_read",
            "perm_chat_read_all",
            "perm_analytics_read",
            "perm_logs_read"
        ],
        is_system_role=True
    ),
    Role(
        id="role_user",
        name="User",
        description="Basic chat access and limited document upload",
        permissions=[
            "perm_documents_read",
            "perm_chat_create", "perm_chat_read_own",
        ],
        is_system_role=True
    ),
    Role(
        id="role_viewer",
        name="Viewer",
        description="Read-only access to chat and documents",
        permissions=[
            "perm_documents_read",
            "perm_chat_read_own",
        ],
        is_system_role=True
    ),
]
