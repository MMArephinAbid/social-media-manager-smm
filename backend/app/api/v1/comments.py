"""
Comments API Routes
Created by: Sadia (Backend Lead)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID

from app.database import get_db
from app.api.deps import get_current_user, get_current_organization
from app.models.user import User
from app.models.organization import Organization
from app.models.facebook_page import FacebookPage
from app.models.comment import Comment, ReplyStatus
from app.services.facebook_service import FacebookService
from app.services.ai_service import AIService
from app.schemas.facebook import (
    CommentResponse,
    CommentListResponse,
    ManualReplyRequest,
    RetryReplyRequest,
)

router = APIRouter(prefix="/comments", tags=["Comments"])


@router.get("", response_model=CommentListResponse)
async def list_comments(
    page_id: Optional[UUID] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    sentiment: Optional[str] = None,
    search: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """List comments with filters and pagination"""
    # Base query - join with pages to filter by organization
    query = (
        select(Comment)
        .join(FacebookPage, Comment.page_id == FacebookPage.id)
        .where(FacebookPage.organization_id == organization.id)
    )

    # Apply filters
    if page_id:
        query = query.where(Comment.page_id == page_id)

    if status_filter:
        try:
            reply_status = ReplyStatus(status_filter)
            query = query.where(Comment.reply_status == reply_status)
        except ValueError:
            pass

    if sentiment:
        query = query.where(Comment.sentiment == sentiment)

    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Comment.comment_text.ilike(search_term),
                Comment.commenter_name.ilike(search_term),
            )
        )

    if date_from:
        query = query.where(Comment.created_at >= date_from)

    if date_to:
        query = query.where(Comment.created_at <= date_to)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    query = query.order_by(desc(Comment.created_at))
    query = query.offset((page - 1) * per_page).limit(per_page)

    result = await db.execute(query)
    comments = result.scalars().all()

    return {
        "items": comments,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
    }


@router.get("/stats")
async def get_comment_stats(
    page_id: Optional[UUID] = None,
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Get comment statistics"""
    since = datetime.utcnow() - timedelta(days=days)

    # Base filter
    base_filter = [
        FacebookPage.organization_id == organization.id,
        Comment.created_at >= since,
    ]

    if page_id:
        base_filter.append(Comment.page_id == page_id)

    # Total comments
    total_query = (
        select(func.count(Comment.id))
        .join(FacebookPage, Comment.page_id == FacebookPage.id)
        .where(and_(*base_filter))
    )
    total = (await db.execute(total_query)).scalar() or 0

    # By status
    status_counts = {}
    for reply_status in ReplyStatus:
        status_query = (
            select(func.count(Comment.id))
            .join(FacebookPage, Comment.page_id == FacebookPage.id)
            .where(and_(*base_filter, Comment.reply_status == reply_status))
        )
        status_counts[reply_status.value] = (await db.execute(status_query)).scalar() or 0

    # By sentiment
    sentiment_query = (
        select(Comment.sentiment, func.count(Comment.id))
        .join(FacebookPage, Comment.page_id == FacebookPage.id)
        .where(and_(*base_filter))
        .group_by(Comment.sentiment)
    )
    sentiment_result = await db.execute(sentiment_query)
    sentiment_counts = {row[0] or "unknown": row[1] for row in sentiment_result.all()}

    # Average response time (for replied comments)
    avg_response_query = (
        select(func.avg(Comment.response_time_seconds))
        .join(FacebookPage, Comment.page_id == FacebookPage.id)
        .where(
            and_(
                *base_filter,
                Comment.reply_status == ReplyStatus.REPLIED,
                Comment.response_time_seconds.isnot(None),
            )
        )
    )
    avg_response_time = (await db.execute(avg_response_query)).scalar()

    return {
        "period_days": days,
        "total_comments": total,
        "by_status": status_counts,
        "by_sentiment": sentiment_counts,
        "avg_response_time_seconds": round(avg_response_time, 2) if avg_response_time else None,
        "reply_rate": round((status_counts.get("replied", 0) / total * 100), 2) if total > 0 else 0,
    }


@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(
    comment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Get a single comment by ID"""
    result = await db.execute(
        select(Comment)
        .join(FacebookPage, Comment.page_id == FacebookPage.id)
        .where(
            and_(
                Comment.id == comment_id,
                FacebookPage.organization_id == organization.id,
            )
        )
    )
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    return comment


@router.post("/{comment_id}/reply")
async def manual_reply(
    comment_id: UUID,
    request: ManualReplyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Manually reply to a comment"""
    # Get comment
    result = await db.execute(
        select(Comment)
        .join(FacebookPage, Comment.page_id == FacebookPage.id)
        .where(
            and_(
                Comment.id == comment_id,
                FacebookPage.organization_id == organization.id,
            )
        )
    )
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    # Get page for access token
    page_result = await db.execute(
        select(FacebookPage).where(FacebookPage.id == comment.page_id)
    )
    page = page_result.scalar_one()

    # Post reply to Facebook
    fb_service = FacebookService()
    try:
        reply_id = await fb_service.post_reply(
            comment_id=comment.fb_comment_id,
            reply_text=request.reply_text,
            access_token=page.access_token,
        )

        # Update comment
        comment.reply_text = request.reply_text
        comment.reply_status = ReplyStatus.REPLIED
        comment.replied_at = datetime.utcnow()
        comment.fb_reply_id = reply_id
        comment.is_manual_reply = True
        comment.replied_by = current_user.id

        # Calculate response time
        if comment.comment_created_at:
            delta = datetime.utcnow() - comment.comment_created_at
            comment.response_time_seconds = int(delta.total_seconds())

        await db.commit()

        return {
            "message": "Reply posted successfully",
            "reply_id": reply_id,
            "comment_id": str(comment_id),
        }

    except Exception as e:
        comment.reply_status = ReplyStatus.FAILED
        comment.error_message = str(e)
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to post reply: {str(e)}"
        )


@router.post("/{comment_id}/retry")
async def retry_ai_reply(
    comment_id: UUID,
    request: RetryReplyRequest = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Retry AI-generated reply for a comment"""
    # Get comment
    result = await db.execute(
        select(Comment)
        .join(FacebookPage, Comment.page_id == FacebookPage.id)
        .where(
            and_(
                Comment.id == comment_id,
                FacebookPage.organization_id == organization.id,
            )
        )
    )
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    # Get page
    page_result = await db.execute(
        select(FacebookPage).where(FacebookPage.id == comment.page_id)
    )
    page = page_result.scalar_one()

    # Generate AI reply
    ai_service = AIService()
    try:
        reply_result = await ai_service.generate_reply(
            comment_text=comment.comment_text,
            post_context=comment.post_message,
            organization=organization,
            prompt_id=request.prompt_id if request else None,
        )

        # Post to Facebook
        fb_service = FacebookService()
        reply_id = await fb_service.post_reply(
            comment_id=comment.fb_comment_id,
            reply_text=reply_result["reply_text"],
            access_token=page.access_token,
        )

        # Update comment
        comment.reply_text = reply_result["reply_text"]
        comment.reply_status = ReplyStatus.REPLIED
        comment.replied_at = datetime.utcnow()
        comment.fb_reply_id = reply_id
        comment.ai_model_used = reply_result.get("model")
        comment.ai_tokens_used = reply_result.get("tokens_used")
        comment.ai_cost = reply_result.get("cost")
        comment.sentiment = reply_result.get("sentiment")
        comment.is_manual_reply = False
        comment.error_message = None

        if comment.comment_created_at:
            delta = datetime.utcnow() - comment.comment_created_at
            comment.response_time_seconds = int(delta.total_seconds())

        await db.commit()

        return {
            "message": "AI reply generated and posted",
            "reply_id": reply_id,
            "reply_text": reply_result["reply_text"],
            "sentiment": reply_result.get("sentiment"),
        }

    except Exception as e:
        comment.reply_status = ReplyStatus.FAILED
        comment.error_message = str(e)
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate/post reply: {str(e)}"
        )


@router.post("/{comment_id}/skip")
async def skip_comment(
    comment_id: UUID,
    reason: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Skip a comment (don't reply)"""
    result = await db.execute(
        select(Comment)
        .join(FacebookPage, Comment.page_id == FacebookPage.id)
        .where(
            and_(
                Comment.id == comment_id,
                FacebookPage.organization_id == organization.id,
            )
        )
    )
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    comment.reply_status = ReplyStatus.SKIPPED
    comment.skip_reason = reason
    comment.skipped_by = current_user.id
    comment.skipped_at = datetime.utcnow()

    await db.commit()

    return {
        "message": "Comment skipped",
        "comment_id": str(comment_id),
    }


@router.post("/{comment_id}/generate-preview")
async def generate_reply_preview(
    comment_id: UUID,
    prompt_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Generate an AI reply preview without posting"""
    result = await db.execute(
        select(Comment)
        .join(FacebookPage, Comment.page_id == FacebookPage.id)
        .where(
            and_(
                Comment.id == comment_id,
                FacebookPage.organization_id == organization.id,
            )
        )
    )
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    ai_service = AIService()
    try:
        reply_result = await ai_service.generate_reply(
            comment_text=comment.comment_text,
            post_context=comment.post_message,
            organization=organization,
            prompt_id=prompt_id,
        )

        return {
            "preview": True,
            "reply_text": reply_result["reply_text"],
            "sentiment": reply_result.get("sentiment"),
            "model": reply_result.get("model"),
            "tokens_used": reply_result.get("tokens_used"),
            "estimated_cost": reply_result.get("cost"),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate preview: {str(e)}"
        )


@router.delete("/{comment_id}/reply")
async def delete_reply(
    comment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Delete a reply from Facebook"""
    result = await db.execute(
        select(Comment)
        .join(FacebookPage, Comment.page_id == FacebookPage.id)
        .where(
            and_(
                Comment.id == comment_id,
                FacebookPage.organization_id == organization.id,
            )
        )
    )
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    if not comment.fb_reply_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No reply to delete"
        )

    # Get page for access token
    page_result = await db.execute(
        select(FacebookPage).where(FacebookPage.id == comment.page_id)
    )
    page = page_result.scalar_one()

    # Delete from Facebook
    fb_service = FacebookService()
    try:
        await fb_service.delete_comment(
            comment_id=comment.fb_reply_id,
            access_token=page.access_token,
        )

        # Update local record
        comment.fb_reply_id = None
        comment.reply_text = None
        comment.reply_status = ReplyStatus.PENDING
        comment.replied_at = None

        await db.commit()

        return {"message": "Reply deleted successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete reply: {str(e)}"
        )


@router.post("/bulk/skip")
async def bulk_skip_comments(
    comment_ids: List[UUID],
    reason: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Skip multiple comments at once"""
    result = await db.execute(
        select(Comment)
        .join(FacebookPage, Comment.page_id == FacebookPage.id)
        .where(
            and_(
                Comment.id.in_(comment_ids),
                FacebookPage.organization_id == organization.id,
            )
        )
    )
    comments = result.scalars().all()

    skipped_count = 0
    for comment in comments:
        if comment.reply_status == ReplyStatus.PENDING:
            comment.reply_status = ReplyStatus.SKIPPED
            comment.skip_reason = reason
            comment.skipped_by = current_user.id
            comment.skipped_at = datetime.utcnow()
            skipped_count += 1

    await db.commit()

    return {
        "message": f"Skipped {skipped_count} comments",
        "skipped_count": skipped_count,
    }
