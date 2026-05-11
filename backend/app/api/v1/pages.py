"""
Facebook Pages API Routes
Created by: Sadia (Backend Lead)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.api.deps import get_current_user, get_current_organization
from app.models.user import User
from app.models.organization import Organization
from app.models.facebook_page import FacebookPage, PageStatus
from app.models.comment import Comment, ReplyStatus
from app.services.facebook_service import FacebookService
from app.schemas.facebook import (
    FacebookPageResponse,
    FacebookPageListResponse,
    ConnectPageRequest,
    PageStatsResponse,
    FacebookOAuthURLResponse,
)

router = APIRouter(prefix="/pages", tags=["Facebook Pages"])


@router.get("/oauth/url", response_model=FacebookOAuthURLResponse)
async def get_oauth_url(
    current_user: User = Depends(get_current_user),
):
    """Get Facebook OAuth URL for connecting pages"""
    fb_service = FacebookService()
    oauth_url = fb_service.get_oauth_url()
    return {"oauth_url": oauth_url}


@router.post("/oauth/callback")
async def oauth_callback(
    code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Handle Facebook OAuth callback and get user pages"""
    fb_service = FacebookService()

    # Exchange code for access token
    token_data = await fb_service.exchange_code_for_token(code)
    user_access_token = token_data["access_token"]

    # Get available pages
    pages = await fb_service.get_user_pages(user_access_token)

    return {
        "pages": pages,
        "user_token": user_access_token,  # Temporary, for page selection
    }


@router.post("/connect", response_model=FacebookPageResponse)
async def connect_page(
    request: ConnectPageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Connect a Facebook page to the organization"""
    fb_service = FacebookService()

    # Check if page already connected
    existing = await db.execute(
        select(FacebookPage).where(
            and_(
                FacebookPage.page_id == request.page_id,
                FacebookPage.organization_id == organization.id,
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page already connected to this organization"
        )

    # Check organization's page limit
    page_count = await db.execute(
        select(func.count(FacebookPage.id)).where(
            FacebookPage.organization_id == organization.id
        )
    )
    current_pages = page_count.scalar() or 0

    # TODO: Check against subscription limit
    # For now, allow up to 10 pages
    if current_pages >= 10:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Page limit reached. Please upgrade your plan."
        )

    # Get long-lived page access token
    page_token = await fb_service.get_page_access_token(
        request.user_access_token,
        request.page_id
    )

    # Subscribe to webhooks
    await fb_service.subscribe_to_webhooks(request.page_id, page_token)

    # Create page record
    new_page = FacebookPage(
        organization_id=organization.id,
        page_id=request.page_id,
        page_name=request.page_name,
        access_token=page_token,  # Will be encrypted by model
        status=PageStatus.ACTIVE,
        connected_by=current_user.id,
    )

    db.add(new_page)
    await db.commit()
    await db.refresh(new_page)

    return new_page


@router.get("", response_model=FacebookPageListResponse)
async def list_pages(
    status_filter: Optional[PageStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """List all connected Facebook pages"""
    query = select(FacebookPage).where(
        FacebookPage.organization_id == organization.id
    )

    if status_filter:
        query = query.where(FacebookPage.status == status_filter)

    query = query.order_by(FacebookPage.created_at.desc())

    result = await db.execute(query)
    pages = result.scalars().all()

    return {"pages": pages, "total": len(pages)}


@router.get("/{page_id}", response_model=FacebookPageResponse)
async def get_page(
    page_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Get a specific Facebook page"""
    result = await db.execute(
        select(FacebookPage).where(
            and_(
                FacebookPage.id == page_id,
                FacebookPage.organization_id == organization.id,
            )
        )
    )
    page = result.scalar_one_or_none()

    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found"
        )

    return page


@router.delete("/{page_id}")
async def disconnect_page(
    page_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Disconnect a Facebook page"""
    result = await db.execute(
        select(FacebookPage).where(
            and_(
                FacebookPage.id == page_id,
                FacebookPage.organization_id == organization.id,
            )
        )
    )
    page = result.scalar_one_or_none()

    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found"
        )

    # Unsubscribe from webhooks
    fb_service = FacebookService()
    try:
        await fb_service.unsubscribe_from_webhooks(page.page_id, page.access_token)
    except Exception:
        pass  # Continue even if unsubscribe fails

    # Soft delete - mark as disconnected
    page.status = PageStatus.DISCONNECTED
    page.disconnected_at = datetime.utcnow()

    await db.commit()

    return {"message": "Page disconnected successfully"}


@router.post("/{page_id}/reconnect", response_model=FacebookPageResponse)
async def reconnect_page(
    page_id: str,
    request: ConnectPageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Reconnect a disconnected page with new token"""
    result = await db.execute(
        select(FacebookPage).where(
            and_(
                FacebookPage.id == page_id,
                FacebookPage.organization_id == organization.id,
            )
        )
    )
    page = result.scalar_one_or_none()

    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found"
        )

    fb_service = FacebookService()

    # Get new page token
    page_token = await fb_service.get_page_access_token(
        request.user_access_token,
        page.page_id
    )

    # Re-subscribe to webhooks
    await fb_service.subscribe_to_webhooks(page.page_id, page_token)

    # Update page
    page.access_token = page_token
    page.status = PageStatus.ACTIVE
    page.token_expires_at = datetime.utcnow() + timedelta(days=60)
    page.disconnected_at = None

    await db.commit()
    await db.refresh(page)

    return page


@router.get("/{page_id}/stats", response_model=PageStatsResponse)
async def get_page_stats(
    page_id: str,
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Get statistics for a Facebook page"""
    # Verify page belongs to organization
    result = await db.execute(
        select(FacebookPage).where(
            and_(
                FacebookPage.id == page_id,
                FacebookPage.organization_id == organization.id,
            )
        )
    )
    page = result.scalar_one_or_none()

    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found"
        )

    since = datetime.utcnow() - timedelta(days=days)

    # Total comments
    total_comments = await db.execute(
        select(func.count(Comment.id)).where(
            and_(
                Comment.page_id == page_id,
                Comment.created_at >= since,
            )
        )
    )

    # Replied comments
    replied_comments = await db.execute(
        select(func.count(Comment.id)).where(
            and_(
                Comment.page_id == page_id,
                Comment.created_at >= since,
                Comment.reply_status == ReplyStatus.REPLIED,
            )
        )
    )

    # Pending comments
    pending_comments = await db.execute(
        select(func.count(Comment.id)).where(
            and_(
                Comment.page_id == page_id,
                Comment.created_at >= since,
                Comment.reply_status == ReplyStatus.PENDING,
            )
        )
    )

    # Failed comments
    failed_comments = await db.execute(
        select(func.count(Comment.id)).where(
            and_(
                Comment.page_id == page_id,
                Comment.created_at >= since,
                Comment.reply_status == ReplyStatus.FAILED,
            )
        )
    )

    total = total_comments.scalar() or 0
    replied = replied_comments.scalar() or 0
    pending = pending_comments.scalar() or 0
    failed = failed_comments.scalar() or 0

    return {
        "page_id": page_id,
        "page_name": page.page_name,
        "period_days": days,
        "total_comments": total,
        "replied_comments": replied,
        "pending_comments": pending,
        "failed_comments": failed,
        "reply_rate": round((replied / total * 100), 2) if total > 0 else 0,
    }


@router.post("/{page_id}/sync")
async def sync_page_comments(
    page_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Manually sync comments from a Facebook page"""
    result = await db.execute(
        select(FacebookPage).where(
            and_(
                FacebookPage.id == page_id,
                FacebookPage.organization_id == organization.id,
            )
        )
    )
    page = result.scalar_one_or_none()

    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found"
        )

    if page.status != PageStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page is not active"
        )

    # TODO: Trigger Celery task for background sync
    # For now, return acknowledgment
    return {
        "message": "Comment sync initiated",
        "page_id": page_id,
        "status": "processing"
    }
