"""
Users API Routes - Team management and user administration
Created by: Sadia (Backend Lead)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import Optional, List
from datetime import datetime, timedelta
from uuid import UUID, uuid4
import secrets

from app.database import get_db
from app.api.deps import get_current_user, get_current_organization, require_permission
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.core.security import get_password_hash, verify_password
from app.config import settings
from app.schemas.auth import (
    UserResponse,
    UserListResponse,
    UserInviteRequest,
    UserUpdateRequest,
    UserRoleUpdate,
    PasswordChangeRequest,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=UserListResponse)
async def list_users(
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """List users in the organization"""
    query = select(User).where(User.organization_id == organization.id)

    if role:
        query = query.where(User.role == role)

    if is_active is not None:
        query = query.where(User.is_active == is_active)

    if search:
        search_term = f"%{search}%"
        query = query.where(
            User.email.ilike(search_term) |
            User.first_name.ilike(search_term) |
            User.last_name.ilike(search_term)
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate
    query = query.order_by(User.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)

    result = await db.execute(query)
    users = result.scalars().all()

    return {
        "users": users,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """Get current user's profile"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    request: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update current user's profile"""
    update_data = request.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field != "password":  # Don't update password here
            setattr(current_user, field, value)

    current_user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(current_user)

    return current_user


@router.post("/me/change-password")
async def change_password(
    request: PasswordChangeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Change current user's password"""
    # Verify current password
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Update password
    current_user.hashed_password = get_password_hash(request.new_password)
    current_user.updated_at = datetime.utcnow()

    await db.commit()

    return {"message": "Password changed successfully"}


@router.post("/invite", response_model=UserResponse)
async def invite_user(
    request: UserInviteRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Invite a new user to the organization"""
    # Check if current user has permission (must be owner or admin)
    if current_user.role not in [UserRole.ORG_OWNER, UserRole.ORG_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and admins can invite users"
        )

    # Check if email already exists
    existing = await db.execute(
        select(User).where(User.email == request.email)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists"
        )

    # Check user limit based on subscription
    user_count = await db.execute(
        select(func.count(User.id)).where(
            and_(
                User.organization_id == organization.id,
                User.is_active == True,
            )
        )
    )
    current_users = user_count.scalar() or 0

    # TODO: Check against subscription limit
    max_users = 10  # Default limit
    if current_users >= max_users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User limit reached. Please upgrade your plan."
        )

    # Generate invite token
    invite_token = secrets.token_urlsafe(32)

    # Create user with pending status
    new_user = User(
        email=request.email,
        first_name=request.first_name or "",
        last_name=request.last_name or "",
        role=request.role or UserRole.ORG_MEMBER,
        organization_id=organization.id,
        is_active=False,  # Will be activated on accepting invite
        is_verified=False,
        invite_token=invite_token,
        invite_sent_at=datetime.utcnow(),
        invited_by=current_user.id,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Send invite email (background task)
    # background_tasks.add_task(send_invite_email, new_user.email, invite_token, organization.name)

    return new_user


@router.post("/accept-invite")
async def accept_invite(
    token: str,
    password: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Accept an invitation and set password"""
    result = await db.execute(
        select(User).where(
            and_(
                User.invite_token == token,
                User.is_active == False,
            )
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired invite token"
        )

    # Check if invite is still valid (7 days)
    if user.invite_sent_at:
        if datetime.utcnow() - user.invite_sent_at > timedelta(days=7):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invite has expired"
            )

    # Activate user
    user.hashed_password = get_password_hash(password)
    user.is_active = True
    user.is_verified = True
    user.invite_token = None
    user.invite_accepted_at = datetime.utcnow()

    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name

    await db.commit()

    return {"message": "Invitation accepted successfully"}


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Get a specific user"""
    result = await db.execute(
        select(User).where(
            and_(
                User.id == user_id,
                User.organization_id == organization.id,
            )
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    request: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Update a user (admin only)"""
    # Check permission
    if current_user.role not in [UserRole.ORG_OWNER, UserRole.ORG_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and admins can update users"
        )

    result = await db.execute(
        select(User).where(
            and_(
                User.id == user_id,
                User.organization_id == organization.id,
            )
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Can't modify owner
    if user.role == UserRole.ORG_OWNER and current_user.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify organization owner"
        )

    update_data = request.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(user, field, value)

    user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)

    return user


@router.put("/{user_id}/role")
async def change_user_role(
    user_id: UUID,
    request: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Change a user's role"""
    # Only owner can change roles
    if current_user.role != UserRole.ORG_OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization owner can change roles"
        )

    result = await db.execute(
        select(User).where(
            and_(
                User.id == user_id,
                User.organization_id == organization.id,
            )
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Can't change owner's role
    if user.role == UserRole.ORG_OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change organization owner's role"
        )

    # Can't promote to owner
    if request.role == UserRole.ORG_OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot promote user to owner. Use transfer ownership instead."
        )

    user.role = request.role
    user.updated_at = datetime.utcnow()

    await db.commit()

    return {"message": f"User role changed to {request.role.value}"}


@router.delete("/{user_id}")
async def remove_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Remove a user from the organization"""
    if current_user.role not in [UserRole.ORG_OWNER, UserRole.ORG_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and admins can remove users"
        )

    result = await db.execute(
        select(User).where(
            and_(
                User.id == user_id,
                User.organization_id == organization.id,
            )
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Can't remove owner
    if user.role == UserRole.ORG_OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove organization owner"
        )

    # Can't remove yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove yourself"
        )

    # Soft delete - deactivate user
    user.is_active = False
    user.deactivated_at = datetime.utcnow()
    user.deactivated_by = current_user.id

    await db.commit()

    return {"message": "User removed successfully"}


@router.post("/{user_id}/reactivate")
async def reactivate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Reactivate a deactivated user"""
    if current_user.role not in [UserRole.ORG_OWNER, UserRole.ORG_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and admins can reactivate users"
        )

    result = await db.execute(
        select(User).where(
            and_(
                User.id == user_id,
                User.organization_id == organization.id,
                User.is_active == False,
            )
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or already active"
        )

    user.is_active = True
    user.deactivated_at = None
    user.deactivated_by = None

    await db.commit()

    return {"message": "User reactivated successfully"}


@router.post("/{user_id}/resend-invite")
async def resend_invite(
    user_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Resend invitation email to a pending user"""
    if current_user.role not in [UserRole.ORG_OWNER, UserRole.ORG_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and admins can resend invites"
        )

    result = await db.execute(
        select(User).where(
            and_(
                User.id == user_id,
                User.organization_id == organization.id,
                User.is_active == False,
                User.invite_token.isnot(None),
            )
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pending user not found"
        )

    # Generate new token
    user.invite_token = secrets.token_urlsafe(32)
    user.invite_sent_at = datetime.utcnow()

    await db.commit()

    # Send invite email
    # background_tasks.add_task(send_invite_email, user.email, user.invite_token, organization.name)

    return {"message": "Invite resent successfully"}


@router.post("/transfer-ownership")
async def transfer_ownership(
    new_owner_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Transfer organization ownership to another user"""
    if current_user.role != UserRole.ORG_OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can transfer ownership"
        )

    result = await db.execute(
        select(User).where(
            and_(
                User.id == new_owner_id,
                User.organization_id == organization.id,
                User.is_active == True,
            )
        )
    )
    new_owner = result.scalar_one_or_none()

    if not new_owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if new_owner.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already the owner"
        )

    # Transfer ownership
    new_owner.role = UserRole.ORG_OWNER
    current_user.role = UserRole.ORG_ADMIN

    await db.commit()

    return {
        "message": f"Ownership transferred to {new_owner.email}",
        "new_owner": new_owner.email,
    }
