"""
API dependencies for dependency injection.
Created by: Sadia (Backend Lead)
"""
from typing import AsyncGenerator, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models import User, Organization, Subscription
from ..core.security import verify_access_token
from ..core.middleware import set_current_tenant_id
from ..core.exceptions import (
    InvalidTokenException,
    TokenExpiredException,
    UserInactiveException,
    UserNotVerifiedException,
    SubscriptionRequiredException,
    PlanLimitExceededException,
)


# Bearer token security
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.

    Raises:
        InvalidTokenException: If token is invalid
        TokenExpiredException: If token has expired
        UserInactiveException: If user is inactive
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = verify_access_token(token)

    if not payload:
        raise InvalidTokenException()

    user_id = payload.get("sub")
    if not user_id:
        raise InvalidTokenException()

    # Get user from database
    result = await db.execute(
        select(User).where(User.id == UUID(user_id))
    )
    user = result.scalar_one_or_none()

    if not user:
        raise InvalidTokenException()

    if not user.is_active:
        raise UserInactiveException()

    # Set tenant context for multi-tenant queries
    if user.organization_id:
        set_current_tenant_id(str(user.organization_id))

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active and verified user."""
    if not current_user.is_active:
        raise UserInactiveException()
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current verified user."""
    if not current_user.is_verified:
        raise UserNotVerifiedException()
    return current_user


async def get_current_organization(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Organization:
    """Get current user's organization."""
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )

    result = await db.execute(
        select(Organization).where(
            Organization.id == current_user.organization_id
        )
    )
    organization = result.scalar_one_or_none()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    if not organization.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization is deactivated"
        )

    return organization


async def get_current_subscription(
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
) -> Subscription:
    """Get current organization's active subscription."""
    result = await db.execute(
        select(Subscription)
        .where(Subscription.organization_id == organization.id)
        .where(Subscription.status.in_(['active', 'trialing']))
        .order_by(Subscription.created_at.desc())
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise SubscriptionRequiredException()

    return subscription


async def check_reply_limit(
    subscription: Subscription = Depends(get_current_subscription),
) -> Subscription:
    """Check if organization has reached reply limit."""
    if not subscription.can_reply():
        raise PlanLimitExceededException(limit_type="replies")
    return subscription


async def check_page_limit(
    subscription: Subscription = Depends(get_current_subscription),
) -> Subscription:
    """Check if organization has reached page limit."""
    if not subscription.can_add_page():
        raise PlanLimitExceededException(limit_type="pages")
    return subscription


class RoleChecker:
    """
    Dependency for checking user roles.

    Usage:
        @router.get("/admin")
        async def admin_route(
            _: bool = Depends(RoleChecker(["super_admin", "org_owner"]))
        ):
            ...
    """

    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        current_user: User = Depends(get_current_user)
    ) -> bool:
        if current_user.role.value not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role.value}' is not allowed. Required: {self.allowed_roles}"
            )
        return True


# Common dependency combinations
def get_org_admin_user():
    """Get user with org admin or higher role."""
    return Depends(RoleChecker(["super_admin", "org_owner", "org_admin"]))


def get_org_owner_user():
    """Get user with org owner or higher role."""
    return Depends(RoleChecker(["super_admin", "org_owner"]))


def get_super_admin_user():
    """Get super admin user."""
    return Depends(RoleChecker(["super_admin"]))


def require_permission(permission: str):
    """
    Dependency for checking specific permissions.

    Usage:
        @router.delete("/item/{id}")
        async def delete_item(
            _: bool = Depends(require_permission("items:delete"))
        ):
            ...
    """
    async def check_permission(
        current_user: User = Depends(get_current_user)
    ) -> bool:
        # For now, check role-based permissions
        # Can be extended to check granular permissions
        role_permissions = {
            "super_admin": ["*"],
            "org_owner": ["*"],
            "org_admin": [
                "users:read", "users:invite", "users:update",
                "pages:*", "comments:*", "settings:*", "analytics:read",
            ],
            "org_member": [
                "pages:read", "comments:read", "comments:reply",
                "analytics:read",
            ],
        }

        user_permissions = role_permissions.get(current_user.role.value, [])

        # Check for wildcard or specific permission
        if "*" in user_permissions:
            return True

        # Check exact match or category wildcard
        permission_parts = permission.split(":")
        category = permission_parts[0]

        if f"{category}:*" in user_permissions:
            return True

        if permission in user_permissions:
            return True

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission '{permission}' required"
        )

    return Depends(check_permission)
