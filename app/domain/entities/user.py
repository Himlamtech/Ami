"""User domain entity - Pure business logic."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class User:
    """
    Pure domain user entity - no framework dependencies.
    
    This represents a user in the business domain with all business rules
    and invariants. No persistence or infrastructure concerns.
    """
    
    # Identity
    id: str
    username: str
    email: str
    hashed_password: str
    
    # Profile
    full_name: Optional[str] = None
    department: Optional[str] = None
    organization: Optional[str] = None
    avatar_url: Optional[str] = None
    
    # Status
    is_active: bool = True
    is_admin: bool = False  # Deprecated: use role_ids
    
    # RBAC
    role_ids: List[str] = field(default_factory=list)
    
    # Localization
    timezone: str = "UTC"
    language: str = "vi"
    
    # Preferences & Usage
    preferences: Dict[str, Any] = field(default_factory=dict)
    usage_quota: Optional[Dict[str, Any]] = None
    
    # Security
    two_factor_enabled: bool = False
    
    # Tracking
    last_login: Optional[datetime] = None
    login_count: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Business Logic Methods
    
    def has_role(self, role_id: str) -> bool:
        """Check if user has a specific role."""
        return role_id in self.role_ids
    
    def has_admin_privileges(self) -> bool:
        """Check if user has admin privileges (legacy or RBAC)."""
        return self.is_admin or "admin" in self.role_ids
    
    def can_access_resource(self, resource: str, action: str) -> bool:
        """
        Business logic: Check if user can access a resource with given action.
        
        Args:
            resource: Resource identifier (e.g., "documents", "users")
            action: Action to perform (e.g., "read", "write", "delete")
            
        Returns:
            True if user has permission, False otherwise
        """
        # Admins have full access
        if self.has_admin_privileges():
            return True
        
        # TODO: Implement role-based permission checking
        # This would query the RBAC system based on role_ids
        return False
    
    def activate(self) -> None:
        """Activate user account."""
        self.is_active = True
        self.updated_at = datetime.now()
    
    def deactivate(self) -> None:
        """Deactivate user account."""
        self.is_active = False
        self.updated_at = datetime.now()
    
    def record_login(self) -> None:
        """Record a successful login."""
        self.last_login = datetime.now()
        self.login_count += 1
        self.updated_at = datetime.now()
    
    def update_profile(
        self,
        full_name: Optional[str] = None,
        department: Optional[str] = None,
        organization: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> None:
        """Update user profile information."""
        if full_name is not None:
            self.full_name = full_name
        if department is not None:
            self.department = department
        if organization is not None:
            self.organization = organization
        if avatar_url is not None:
            self.avatar_url = avatar_url
        
        self.updated_at = datetime.now()
    
    def add_role(self, role_id: str) -> None:
        """Add a role to user."""
        if role_id not in self.role_ids:
            self.role_ids.append(role_id)
            self.updated_at = datetime.now()
    
    def remove_role(self, role_id: str) -> None:
        """Remove a role from user."""
        if role_id in self.role_ids:
            self.role_ids.remove(role_id)
            self.updated_at = datetime.now()
    
    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username}, email={self.email})"
