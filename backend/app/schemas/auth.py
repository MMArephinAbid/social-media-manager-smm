"""
Authentication schemas for request/response validation.
Created by: Sadia (Backend Lead)
"""
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class RegisterRequest(BaseModel):
    """Request schema for user registration."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    organization_name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v

    @field_validator("first_name", "last_name", "organization_name")
    @classmethod
    def strip_whitespace(cls, v: Optional[str]) -> Optional[str]:
        """Strip whitespace from names."""
        if v:
            return v.strip()
        return v


class LoginRequest(BaseModel):
    """Request schema for login."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response schema for login/refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshTokenRequest(BaseModel):
    """Request schema for token refresh."""

    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    """Request schema for password reset request."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Request schema for password reset."""

    token: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class ChangePasswordRequest(BaseModel):
    """Request schema for changing password."""

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class VerifyEmailRequest(BaseModel):
    """Request schema for email verification."""

    token: str


class UserResponse(BaseModel):
    """Response schema for user data."""

    id: UUID
    email: str
    first_name: str
    last_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    organization_id: Optional[UUID] = None
    created_at: str

    class Config:
        from_attributes = True


class MeResponse(BaseModel):
    """Response schema for current user with organization."""

    user: UserResponse
    organization: Optional[dict] = None
    subscription: Optional[dict] = None


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
    success: bool = True


class UserListResponse(BaseModel):
    """Response for listing users."""

    users: list
    total: int
    page: int
    per_page: int
    pages: int


class UserInviteRequest(BaseModel):
    """Request to invite a new user."""

    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = "org_member"


class UserUpdateRequest(BaseModel):
    """Request to update user profile."""

    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    avatar_url: Optional[str] = None


class UserRoleUpdate(BaseModel):
    """Request to change user role."""

    role: str  # org_admin, org_member


class PasswordChangeRequest(BaseModel):
    """Request to change password."""

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
