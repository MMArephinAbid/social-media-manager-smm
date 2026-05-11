"""
Permission checking utilities for RBAC.
Created by: Sadia (Backend Lead)
"""
from enum import Enum
from functools import wraps
from typing import Callable, List, Optional

from fastapi import Depends, HTTPException, status

from ..models.user import UserRole


class Permission(str, Enum):
    """All available permissions in the system."""

    # Organization
    ORG_READ = "org:read"
    ORG_WRITE = "org:write"
    ORG_DELETE = "org:delete"

    # Users
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"

    # Pages
    PAGE_READ = "page:read"
    PAGE_WRITE = "page:write"
    PAGE_DELETE = "page:delete"

    # Comments
    COMMENT_READ = "comment:read"
    COMMENT_WRITE = "comment:write"

    # Settings
    SETTINGS_READ = "settings:read"
    SETTINGS_WRITE = "settings:write"

    # Billing
    BILLING_READ = "billing:read"
    BILLING_WRITE = "billing:write"

    # Analytics
    ANALYTICS_READ = "analytics:read"

    # Admin
    ADMIN_ACCESS = "admin:access"


# Role to permissions mapping
ROLE_PERMISSIONS = {
    UserRole.SUPER_ADMIN: [
        Permission.ORG_READ, Permission.ORG_WRITE, Permission.ORG_DELETE,
        Permission.USER_READ, Permission.USER_WRITE, Permission.USER_DELETE,
        Permission.PAGE_READ, Permission.PAGE_WRITE, Permission.PAGE_DELETE,
        Permission.COMMENT_READ, Permission.COMMENT_WRITE,
        Permission.SETTINGS_READ, Permission.SETTINGS_WRITE,
        Permission.BILLING_READ, Permission.BILLING_WRITE,
        Permission.ANALYTICS_READ,
        Permission.ADMIN_ACCESS,
    ],
    UserRole.ORG_OWNER: [
        Permission.ORG_READ, Permission.ORG_WRITE, Permission.ORG_DELETE,
        Permission.USER_READ, Permission.USER_WRITE, Permission.USER_DELETE,
        Permission.PAGE_READ, Permission.PAGE_WRITE, Permission.PAGE_DELETE,
        Permission.COMMENT_READ, Permission.COMMENT_WRITE,
        Permission.SETTINGS_READ, Permission.SETTINGS_WRITE,
        Permission.BILLING_READ, Permission.BILLING_WRITE,
        Permission.ANALYTICS_READ,
    ],
    UserRole.ORG_ADMIN: [
        Permission.ORG_READ,
        Permission.USER_READ, Permission.USER_WRITE,
        Permission.PAGE_READ, Permission.PAGE_WRITE,
        Permission.COMMENT_READ, Permission.COMMENT_WRITE,
        Permission.SETTINGS_READ, Permission.SETTINGS_WRITE,
        Permission.ANALYTICS_READ,
    ],
    UserRole.ORG_MEMBER: [
        Permission.ORG_READ,
        Permission.PAGE_READ,
        Permission.COMMENT_READ, Permission.COMMENT_WRITE,
        Permission.ANALYTICS_READ,
    ],
    UserRole.ORG_VIEWER: [
        Permission.ORG_READ,
        Permission.PAGE_READ,
        Permission.COMMENT_READ,
        Permission.ANALYTICS_READ,
    ],
}


def has_permission(role: UserRole, permission: Permission) -> bool:
    """Check if a role has a specific permission."""
    role_perms = ROLE_PERMISSIONS.get(role, [])
    return permission in role_perms


def has_any_permission(role: UserRole, permissions: List[Permission]) -> bool:
    """Check if a role has any of the specified permissions."""
    role_perms = ROLE_PERMISSIONS.get(role, [])
    return any(perm in role_perms for perm in permissions)


def has_all_permissions(role: UserRole, permissions: List[Permission]) -> bool:
    """Check if a role has all of the specified permissions."""
    role_perms = ROLE_PERMISSIONS.get(role, [])
    return all(perm in role_perms for perm in permissions)


class PermissionChecker:
    """
    Permission checker dependency for FastAPI routes.

    Usage:
        @router.get("/pages")
        async def get_pages(
            current_user: User = Depends(get_current_user),
            _: bool = Depends(PermissionChecker([Permission.PAGE_READ]))
        ):
            ...
    """

    def __init__(
        self,
        required_permissions: List[Permission],
        require_all: bool = True
    ):
        self.required_permissions = required_permissions
        self.require_all = require_all

    async def __call__(self, current_user=None) -> bool:
        """Check if current user has required permissions."""
        # Import here to avoid circular imports
        from ..api.deps import get_current_user

        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )

        if self.require_all:
            has_perms = has_all_permissions(
                current_user.role,
                self.required_permissions
            )
        else:
            has_perms = has_any_permission(
                current_user.role,
                self.required_permissions
            )

        if not has_perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission(s): {', '.join(p.value for p in self.required_permissions)}"
            )

        return True


def require_permission(permission: Permission):
    """
    Decorator to require a specific permission.

    Usage:
        @router.get("/pages")
        @require_permission(Permission.PAGE_READ)
        async def get_pages(current_user: User = Depends(get_current_user)):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current_user from kwargs
            current_user = kwargs.get("current_user")
            if current_user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            if not has_permission(current_user.role, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permission: {permission.value}"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_roles(allowed_roles: List[UserRole]):
    """
    Decorator to require specific roles.

    Usage:
        @router.delete("/org/{org_id}")
        @require_roles([UserRole.SUPER_ADMIN, UserRole.ORG_OWNER])
        async def delete_org(current_user: User = Depends(get_current_user)):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if current_user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"This action requires one of these roles: {', '.join(r.value for r in allowed_roles)}"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def is_super_admin(role: UserRole) -> bool:
    """Check if role is super admin."""
    return role == UserRole.SUPER_ADMIN


def is_org_owner_or_above(role: UserRole) -> bool:
    """Check if role is org owner or above."""
    return role in [UserRole.SUPER_ADMIN, UserRole.ORG_OWNER]


def is_org_admin_or_above(role: UserRole) -> bool:
    """Check if role is org admin or above."""
    return role in [UserRole.SUPER_ADMIN, UserRole.ORG_OWNER, UserRole.ORG_ADMIN]


def can_manage_users(role: UserRole) -> bool:
    """Check if role can manage users."""
    return has_permission(role, Permission.USER_WRITE)


def can_manage_billing(role: UserRole) -> bool:
    """Check if role can manage billing."""
    return has_permission(role, Permission.BILLING_WRITE)
