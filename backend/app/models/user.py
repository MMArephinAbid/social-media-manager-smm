"""
User model with RBAC support.
Created by: Sadia (Backend Lead)
"""
from enum import Enum
from sqlalchemy import Column, String, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, UUIDMixin, TimestampMixin


class UserRole(str, Enum):
    """User roles for RBAC."""
    SUPER_ADMIN = "super_admin"      # Platform admin (us)
    ORG_OWNER = "org_owner"          # Organization owner
    ORG_ADMIN = "org_admin"          # Can manage org settings
    ORG_MEMBER = "org_member"        # Can view and reply
    ORG_VIEWER = "org_viewer"        # View only


class User(Base, UUIDMixin, TimestampMixin):
    """
    User model with multi-tenant support.
    Users belong to organizations with role-based access.
    """
    __tablename__ = 'users'

    # Organization (tenant)
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey('organizations.id', ondelete='CASCADE'),
        nullable=True,  # Nullable for super_admin
        index=True
    )

    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # Profile
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    avatar_url = Column(String(500), nullable=True)

    # Role & Status
    role = Column(
        SQLEnum(UserRole),
        default=UserRole.ORG_MEMBER,
        nullable=False
    )
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Password Reset
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(String(255), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission."""
        permissions_map = {
            UserRole.SUPER_ADMIN: ['*'],  # All permissions
            UserRole.ORG_OWNER: [
                'org:read', 'org:write', 'org:delete',
                'user:read', 'user:write', 'user:delete',
                'page:read', 'page:write', 'page:delete',
                'comment:read', 'comment:write',
                'settings:read', 'settings:write',
                'billing:read', 'billing:write',
                'analytics:read'
            ],
            UserRole.ORG_ADMIN: [
                'org:read',
                'user:read', 'user:write',
                'page:read', 'page:write',
                'comment:read', 'comment:write',
                'settings:read', 'settings:write',
                'analytics:read'
            ],
            UserRole.ORG_MEMBER: [
                'org:read',
                'page:read',
                'comment:read', 'comment:write',
                'analytics:read'
            ],
            UserRole.ORG_VIEWER: [
                'org:read',
                'page:read',
                'comment:read',
                'analytics:read'
            ]
        }

        user_permissions = permissions_map.get(self.role, [])
        return '*' in user_permissions or permission in user_permissions

    def is_org_admin_or_above(self) -> bool:
        """Check if user is org admin or higher."""
        return self.role in [
            UserRole.SUPER_ADMIN,
            UserRole.ORG_OWNER,
            UserRole.ORG_ADMIN
        ]
