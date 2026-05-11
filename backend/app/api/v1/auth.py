"""
Authentication API routes.
Created by: Sadia (Backend Lead)
"""
from datetime import datetime, timedelta
from uuid import UUID
import re

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ...database import get_db
from ...models import User, Organization, Subscription, Plan, UserRole
from ...schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    UserResponse,
    MeResponse,
    MessageResponse,
)
from ...core import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    generate_random_token,
    InvalidCredentialsException,
    ResourceAlreadyExistsException,
    ResourceNotFoundException,
)
from ...config import settings
from ..deps import get_current_user, get_current_organization


router = APIRouter(prefix="/auth", tags=["Authentication"])


def generate_slug(name: str) -> str:
    """Generate URL-friendly slug from name."""
    slug = name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    slug = slug.strip('-')
    return slug


@router.post("/register", response_model=TokenResponse)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user and organization.

    Creates:
    - New organization
    - New user (as org_owner)
    - Free subscription
    """
    # Check if email exists
    result = await db.execute(
        select(User).where(func.lower(User.email) == request.email.lower())
    )
    if result.scalar_one_or_none():
        raise ResourceAlreadyExistsException("User", "email", request.email)

    # Generate unique slug
    base_slug = generate_slug(request.organization_name)
    slug = base_slug
    counter = 1
    while True:
        result = await db.execute(
            select(Organization).where(Organization.slug == slug)
        )
        if not result.scalar_one_or_none():
            break
        slug = f"{base_slug}-{counter}"
        counter += 1

    # Create organization
    organization = Organization(
        name=request.organization_name,
        slug=slug,
        email=request.email,
        phone=request.phone,
        settings={
            "timezone": "Asia/Kolkata",
            "language": "bn",
            "currency": "INR",
            "auto_reply_enabled": True,
        }
    )
    db.add(organization)
    await db.flush()

    # Create user
    user = User(
        organization_id=organization.id,
        email=request.email.lower(),
        password_hash=hash_password(request.password),
        first_name=request.first_name,
        last_name=request.last_name,
        phone=request.phone,
        role=UserRole.ORG_OWNER,
        is_active=True,
        is_verified=False,  # Email verification required
    )
    db.add(user)
    await db.flush()

    # Get free plan
    result = await db.execute(
        select(Plan).where(Plan.slug == "free")
    )
    free_plan = result.scalar_one_or_none()

    # Create subscription if free plan exists
    if free_plan:
        subscription = Subscription(
            organization_id=organization.id,
            plan_id=free_plan.id,
            status="trialing",
            billing_cycle="monthly",
            current_period_start=datetime.utcnow().isoformat(),
            current_period_end=(datetime.utcnow() + timedelta(days=14)).isoformat(),
            trial_end=(datetime.utcnow() + timedelta(days=14)).isoformat(),
        )
        db.add(subscription)

    await db.commit()

    # Generate tokens
    access_token = create_access_token(
        subject=str(user.id),
        organization_id=organization.id,
        role=user.role.value
    )
    refresh_token = create_refresh_token(subject=str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with email and password.
    """
    # Find user
    result = await db.execute(
        select(User).where(func.lower(User.email) == request.email.lower())
    )
    user = result.scalar_one_or_none()

    if not user:
        raise InvalidCredentialsException()

    if not verify_password(request.password, user.password_hash):
        raise InvalidCredentialsException()

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated"
        )

    # Generate tokens
    access_token = create_access_token(
        subject=str(user.id),
        organization_id=user.organization_id,
        role=user.role.value
    )
    refresh_token = create_refresh_token(subject=str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    """
    payload = verify_refresh_token(request.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id = payload.get("sub")

    # Get user
    result = await db.execute(
        select(User).where(User.id == UUID(user_id))
    )
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Generate new tokens
    access_token = create_access_token(
        subject=str(user.id),
        organization_id=user.organization_id,
        role=user.role.value
    )
    new_refresh_token = create_refresh_token(subject=str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Logout user.
    In a production system, you would blacklist the token here.
    """
    # TODO: Add token to blacklist in Redis
    return MessageResponse(message="Successfully logged out")


@router.get("/me", response_model=MeResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user profile with organization and subscription.
    """
    user_data = UserResponse(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        phone=current_user.phone,
        avatar_url=current_user.avatar_url,
        role=current_user.role.value,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        organization_id=current_user.organization_id,
        created_at=current_user.created_at.isoformat() if current_user.created_at else ""
    )

    org_data = None
    sub_data = None

    if current_user.organization_id:
        # Get organization
        result = await db.execute(
            select(Organization).where(Organization.id == current_user.organization_id)
        )
        org = result.scalar_one_or_none()
        if org:
            org_data = {
                "id": str(org.id),
                "name": org.name,
                "slug": org.slug,
                "logo_url": org.logo_url,
                "settings": org.settings,
            }

        # Get subscription
        result = await db.execute(
            select(Subscription)
            .where(Subscription.organization_id == current_user.organization_id)
            .where(Subscription.status.in_(['active', 'trialing']))
        )
        sub = result.scalar_one_or_none()
        if sub:
            # Load plan
            result = await db.execute(
                select(Plan).where(Plan.id == sub.plan_id)
            )
            plan = result.scalar_one_or_none()
            sub_data = {
                "id": str(sub.id),
                "status": sub.status.value,
                "plan_name": plan.name if plan else "Unknown",
                "replies_used": sub.replies_used,
                "replies_limit": plan.max_replies_per_month if plan else 0,
                "pages_used": sub.pages_used,
                "pages_limit": plan.max_pages if plan else 0,
            }

    return MeResponse(
        user=user_data,
        organization=org_data,
        subscription=sub_data
    )


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Request password reset email.
    """
    # Find user
    result = await db.execute(
        select(User).where(func.lower(User.email) == request.email.lower())
    )
    user = result.scalar_one_or_none()

    # Always return success to prevent email enumeration
    if user and user.is_active:
        # Generate reset token
        reset_token = generate_random_token()
        user.reset_token = reset_token
        user.reset_token_expires = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        await db.commit()

        # TODO: Send email in background
        # background_tasks.add_task(send_password_reset_email, user.email, reset_token)

    return MessageResponse(
        message="If the email exists, a password reset link has been sent"
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Reset password using token from email.
    """
    # Find user with valid token
    result = await db.execute(
        select(User).where(User.reset_token == request.token)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Check if token expired
    if user.reset_token_expires:
        expires = datetime.fromisoformat(user.reset_token_expires)
        if datetime.utcnow() > expires:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired"
            )

    # Update password
    user.password_hash = hash_password(request.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    await db.commit()

    return MessageResponse(message="Password has been reset successfully")


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change password for logged in user.
    """
    # Verify current password
    if not verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Update password
    current_user.password_hash = hash_password(request.new_password)
    await db.commit()

    return MessageResponse(message="Password changed successfully")
