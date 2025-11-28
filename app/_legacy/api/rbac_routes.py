"""
RBAC (Role-Based Access Control) API routes.
Admin-only endpoints for managing roles, permissions, and user access.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.auth_dependencies import get_current_admin_user
from app.application.factory import ProviderFactory
from app.application.rbac_service import RBACService
from app.core.mongodb_models import UserInDB
from app.core.rbac_models import (
    Permission,
    Role,
    RoleCreate,
    RoleListResponse,
    RoleUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/rbac", tags=["rbac"])


# ============= Permission Endpoints =============

@router.get("/permissions", response_model=List[Permission])
async def list_permissions(
    current_admin: UserInDB = Depends(get_current_admin_user),
):
    """
    List all available permissions.
    Admin only.
    """
    try:
        mongodb = await ProviderFactory.get_mongodb_client()
        rbac_service = RBACService(mongodb)
        
        permissions = await rbac_service.get_all_permissions()
        logger.info(f"Admin {current_admin.username} listed {len(permissions)} permissions")
        
        return permissions
        
    except Exception as e:
        logger.error(f"Failed to list permissions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve permissions: {str(e)}"
        )


@router.get("/permissions/{permission_id}", response_model=Permission)
async def get_permission(
    permission_id: str,
    current_admin: UserInDB = Depends(get_current_admin_user),
):
    """
    Get a specific permission by ID.
    Admin only.
    """
    try:
        mongodb = await ProviderFactory.get_mongodb_client()
        rbac_service = RBACService(mongodb)
        
        permission = await rbac_service.get_permission_by_id(permission_id)
        
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission {permission_id} not found"
            )
        
        return permission
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get permission {permission_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve permission: {str(e)}"
        )


# ============= Role Endpoints =============

@router.get("/roles", response_model=RoleListResponse)
async def list_roles(
    current_admin: UserInDB = Depends(get_current_admin_user),
):
    """
    List all roles.
    Admin only.
    """
    try:
        mongodb = await ProviderFactory.get_mongodb_client()
        rbac_service = RBACService(mongodb)
        
        roles = await rbac_service.list_roles()
        logger.info(f"Admin {current_admin.username} listed {len(roles)} roles")
        
        return RoleListResponse(
            roles=roles,
            total=len(roles)
        )
        
    except Exception as e:
        logger.error(f"Failed to list roles: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve roles: {str(e)}"
        )


@router.get("/roles/{role_id}", response_model=Role)
async def get_role(
    role_id: str,
    current_admin: UserInDB = Depends(get_current_admin_user),
):
    """
    Get a specific role by ID.
    Admin only.
    """
    try:
        mongodb = await ProviderFactory.get_mongodb_client()
        rbac_service = RBACService(mongodb)
        
        role = await rbac_service.get_role_by_id(role_id)
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role {role_id} not found"
            )
        
        return role
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get role {role_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve role: {str(e)}"
        )


@router.post("/roles", response_model=Role, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_create: RoleCreate,
    current_admin: UserInDB = Depends(get_current_admin_user),
):
    """
    Create a new custom role.
    Admin only.
    
    System roles cannot be created via API.
    """
    try:
        mongodb = await ProviderFactory.get_mongodb_client()
        rbac_service = RBACService(mongodb)
        
        # Check if role name already exists
        existing_roles = await rbac_service.list_roles()
        if any(r.name.lower() == role_create.name.lower() for r in existing_roles):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role with name '{role_create.name}' already exists"
            )
        
        role = await rbac_service.create_role(role_create, current_admin.id)
        logger.info(f"Admin {current_admin.username} created role: {role.name}")
        
        return role
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create role: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create role: {str(e)}"
        )


@router.put("/roles/{role_id}", response_model=Role)
async def update_role(
    role_id: str,
    role_update: RoleUpdate,
    current_admin: UserInDB = Depends(get_current_admin_user),
):
    """
    Update an existing role.
    Admin only.
    
    System roles cannot be modified.
    """
    try:
        mongodb = await ProviderFactory.get_mongodb_client()
        rbac_service = RBACService(mongodb)
        
        role = await rbac_service.update_role(role_id, role_update)
        logger.info(f"Admin {current_admin.username} updated role: {role_id}")
        
        return role
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to update role {role_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update role: {str(e)}"
        )


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: str,
    current_admin: UserInDB = Depends(get_current_admin_user),
):
    """
    Delete a custom role.
    Admin only.
    
    System roles cannot be deleted.
    This will remove the role from all users who have it assigned.
    """
    try:
        mongodb = await ProviderFactory.get_mongodb_client()
        rbac_service = RBACService(mongodb)
        
        await rbac_service.delete_role(role_id)
        logger.info(f"Admin {current_admin.username} deleted role: {role_id}")
        
        return None
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to delete role {role_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete role: {str(e)}"
        )


# ============= User Role Assignment =============

@router.put("/users/{user_id}/roles")
async def assign_roles_to_user(
    user_id: str,
    role_ids: List[str],
    current_admin: UserInDB = Depends(get_current_admin_user),
):
    """
    Assign roles to a user.
    Admin only.
    
    This replaces all existing roles for the user.
    """
    try:
        mongodb = await ProviderFactory.get_mongodb_client()
        rbac_service = RBACService(mongodb)
        
        # Validate user exists
        user = await mongodb.db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )
        
        await rbac_service.assign_roles_to_user(user_id, role_ids)
        logger.info(f"Admin {current_admin.username} assigned roles {role_ids} to user {user_id}")
        
        return {"message": "Roles assigned successfully", "user_id": user_id, "role_ids": role_ids}
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to assign roles to user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign roles: {str(e)}"
        )


@router.get("/users/{user_id}/permissions")
async def get_user_permissions(
    user_id: str,
    current_admin: UserInDB = Depends(get_current_admin_user),
):
    """
    Get all effective permissions for a user.
    Admin only.
    
    Returns aggregated permissions from all assigned roles.
    """
    try:
        mongodb = await ProviderFactory.get_mongodb_client()
        rbac_service = RBACService(mongodb)
        
        # Get user
        user_data = await mongodb.db.users.find_one({"id": user_id})
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )
        
        user = UserInDB(**user_data)
        permissions = await rbac_service.get_user_permissions(user)
        
        logger.info(f"Admin {current_admin.username} viewed permissions for user {user_id}")
        
        return {
            "user_id": user_id,
            "role_ids": user.role_ids,
            "permissions": permissions,
            "total_permissions": len(permissions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get permissions for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user permissions: {str(e)}"
        )


# ============= RBAC Initialization =============

@router.post("/initialize", status_code=status.HTTP_201_CREATED)
async def initialize_rbac(
    current_admin: UserInDB = Depends(get_current_admin_user),
):
    """
    Initialize RBAC system with predefined roles and permissions.
    Admin only.
    
    Safe to run multiple times - will skip if already initialized.
    """
    try:
        mongodb = await ProviderFactory.get_mongodb_client()
        rbac_service = RBACService(mongodb)
        
        await rbac_service.initialize()
        logger.info(f"Admin {current_admin.username} initialized RBAC system")
        
        return {"message": "RBAC system initialized successfully"}
        
    except Exception as e:
        logger.error(f"Failed to initialize RBAC: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize RBAC system: {str(e)}"
        )
