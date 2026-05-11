"""
Analytics API Routes - Dashboard statistics and reports
Created by: Sadia (Backend Lead)
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, extract, case
from typing import Optional, List
from datetime import datetime, timedelta
from uuid import UUID

from app.database import get_db
from app.api.deps import get_current_user, get_current_organization
from app.models.user import User
from app.models.organization import Organization
from app.models.facebook_page import FacebookPage, PageStatus
from app.models.comment import Comment, ReplyStatus
from app.models.subscription import Subscription, SubscriptionStatus

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview")
async def get_overview(
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Get dashboard overview statistics"""
    since = datetime.utcnow() - timedelta(days=days)

    # Total pages
    pages_result = await db.execute(
        select(func.count(FacebookPage.id)).where(
            and_(
                FacebookPage.organization_id == organization.id,
                FacebookPage.status == PageStatus.ACTIVE,
            )
        )
    )
    total_pages = pages_result.scalar() or 0

    # Total comments in period
    comments_result = await db.execute(
        select(func.count(Comment.id))
        .join(FacebookPage, Comment.page_id == FacebookPage.id)
        .where(
            and_(
                FacebookPage.organization_id == organization.id,
                Comment.created_at >= since,
            )
        )
    )
    total_comments = comments_result.scalar() or 0

    # Replied comments
    replied_result = await db.execute(
        select(func.count(Comment.id))
        .join(FacebookPage, Comment.page_id == FacebookPage.id)
        .where(
            and_(
                FacebookPage.organization_id == organization.id,
                Comment.created_at >= since,
                Comment.reply_status == ReplyStatus.REPLIED,
            )
        )
    )
    replied_comments = replied_result.scalar() or 0

    # Pending comments
    pending_result = await db.execute(
        select(func.count(Comment.id))
        .join(FacebookPage, Comment.page_id == FacebookPage.id)
        .where(
            and_(
                FacebookPage.organization_id == organization.id,
                Comment.reply_status == ReplyStatus.PENDING,
            )
        )
    )
    pending_comments = pending_result.scalar() or 0

    # Failed comments
    failed_result = await db.execute(
        select(func.count(Comment.id))
        .join(FacebookPage, Comment.page_id == FacebookPage.id)
        .where(
            and_(
                FacebookPage.organization_id == organization.id,
                Comment.created_at >= since,
                Comment.reply_status == ReplyStatus.FAILED,
            )
        )
    )
    failed_comments = failed_result.scalar() or 0

    # Average response time (in seconds)
    avg_response_result = await db.execute(
        select(func.avg(Comment.response_time_seconds))
        .join(FacebookPage, Comment.page_id == FacebookPage.id)
        .where(
            and_(
                FacebookPage.organization_id == organization.id,
                Comment.created_at >= since,
                Comment.reply_status == ReplyStatus.REPLIED,
                Comment.response_time_seconds.isnot(None),
            )
        )
    )
    avg_response_time = avg_response_result.scalar()

    # AI cost in period
    cost_result = await db.execute(
        select(func.sum(Comment.ai_cost))
        .join(FacebookPage, Comment.page_id == FacebookPage.id)
        .where(
            and_(
                FacebookPage.organization_id == organization.id,
                Comment.created_at >= since,
                Comment.ai_cost.isnot(None),
            )
        )
    )
    total_ai_cost = cost_result.scalar() or 0

    # Get subscription info
    sub_result = await db.execute(
        select(Subscription).where(
            and_(
                Subscription.organization_id == organization.id,
                Subscription.status == SubscriptionStatus.ACTIVE,
            )
        )
    )
    subscription = sub_result.scalar_one_or_none()

    return {
        "period_days": days,
        "pages": {
            "total": total_pages,
            "active": total_pages,
        },
        "comments": {
            "total": total_comments,
            "replied": replied_comments,
            "pending": pending_comments,
            "failed": failed_comments,
            "skipped": total_comments - replied_comments - pending_comments - failed_comments,
        },
        "reply_rate": round((replied_comments / total_comments * 100), 2) if total_comments > 0 else 0,
        "avg_response_time_seconds": round(avg_response_time, 2) if avg_response_time else None,
        "avg_response_time_formatted": format_duration(avg_response_time) if avg_response_time else None,
        "ai_cost": round(total_ai_cost, 4),
        "subscription": {
            "plan": subscription.plan.name if subscription and subscription.plan else "Free",
            "replies_used": subscription.replies_used if subscription else 0,
            "replies_limit": subscription.plan.replies_limit if subscription and subscription.plan else 50,
        } if subscription else {
            "plan": "Free",
            "replies_used": replied_comments,
            "replies_limit": 50,
        },
    }


@router.get("/comments/timeline")
async def get_comments_timeline(
    days: int = Query(default=30, ge=1, le=365),
    page_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Get comments timeline for charts"""
    since = datetime.utcnow() - timedelta(days=days)

    # Base query
    query = (
        select(
            func.date(Comment.created_at).label("date"),
            func.count(Comment.id).label("total"),
            func.sum(case((Comment.reply_status == ReplyStatus.REPLIED, 1), else_=0)).label("replied"),
            func.sum(case((Comment.reply_status == ReplyStatus.FAILED, 1), else_=0)).label("failed"),
        )
        .join(FacebookPage, Comment.page_id == FacebookPage.id)
        .where(
            and_(
                FacebookPage.organization_id == organization.id,
                Comment.created_at >= since,
            )
        )
        .group_by(func.date(Comment.created_at))
        .order_by(func.date(Comment.created_at))
    )

    if page_id:
        query = query.where(Comment.page_id == page_id)

    result = await db.execute(query)
    rows = result.all()

    timeline = []
    for row in rows:
        timeline.append({
            "date": row.date.isoformat() if row.date else None,
            "total": row.total or 0,
            "replied": row.replied or 0,
            "failed": row.failed or 0,
        })

    return {"timeline": timeline, "period_days": days}


@router.get("/sentiment")
async def get_sentiment_breakdown(
    days: int = Query(default=30, ge=1, le=365),
    page_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Get sentiment breakdown of comments"""
    since = datetime.utcnow() - timedelta(days=days)

    query = (
        select(
            Comment.sentiment,
            func.count(Comment.id).label("count"),
        )
        .join(FacebookPage, Comment.page_id == FacebookPage.id)
        .where(
            and_(
                FacebookPage.organization_id == organization.id,
                Comment.created_at >= since,
                Comment.sentiment.isnot(None),
            )
        )
        .group_by(Comment.sentiment)
    )

    if page_id:
        query = query.where(Comment.page_id == page_id)

    result = await db.execute(query)
    rows = result.all()

    sentiment_data = {}
    total = 0
    for row in rows:
        sentiment_data[row.sentiment or "unknown"] = row.count
        total += row.count

    # Calculate percentages
    breakdown = []
    for sentiment, count in sentiment_data.items():
        breakdown.append({
            "sentiment": sentiment,
            "count": count,
            "percentage": round((count / total * 100), 2) if total > 0 else 0,
        })

    return {
        "breakdown": breakdown,
        "total": total,
        "period_days": days,
    }


@router.get("/pages/performance")
async def get_pages_performance(
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Get performance metrics for each connected page"""
    since = datetime.utcnow() - timedelta(days=days)

    # Get all active pages
    pages_result = await db.execute(
        select(FacebookPage).where(
            and_(
                FacebookPage.organization_id == organization.id,
                FacebookPage.status == PageStatus.ACTIVE,
            )
        )
    )
    pages = pages_result.scalars().all()

    performance = []
    for page in pages:
        # Get stats for this page
        total_result = await db.execute(
            select(func.count(Comment.id)).where(
                and_(
                    Comment.page_id == page.id,
                    Comment.created_at >= since,
                )
            )
        )
        total_comments = total_result.scalar() or 0

        replied_result = await db.execute(
            select(func.count(Comment.id)).where(
                and_(
                    Comment.page_id == page.id,
                    Comment.created_at >= since,
                    Comment.reply_status == ReplyStatus.REPLIED,
                )
            )
        )
        replied_comments = replied_result.scalar() or 0

        avg_time_result = await db.execute(
            select(func.avg(Comment.response_time_seconds)).where(
                and_(
                    Comment.page_id == page.id,
                    Comment.created_at >= since,
                    Comment.reply_status == ReplyStatus.REPLIED,
                    Comment.response_time_seconds.isnot(None),
                )
            )
        )
        avg_response_time = avg_time_result.scalar()

        performance.append({
            "page_id": str(page.id),
            "page_name": page.page_name,
            "fb_page_id": page.page_id,
            "total_comments": total_comments,
            "replied_comments": replied_comments,
            "reply_rate": round((replied_comments / total_comments * 100), 2) if total_comments > 0 else 0,
            "avg_response_time_seconds": round(avg_response_time, 2) if avg_response_time else None,
        })

    # Sort by total comments
    performance.sort(key=lambda x: x["total_comments"], reverse=True)

    return {"pages": performance, "period_days": days}


@router.get("/hourly-distribution")
async def get_hourly_distribution(
    days: int = Query(default=30, ge=1, le=365),
    page_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Get hourly distribution of comments"""
    since = datetime.utcnow() - timedelta(days=days)

    query = (
        select(
            extract("hour", Comment.comment_created_at).label("hour"),
            func.count(Comment.id).label("count"),
        )
        .join(FacebookPage, Comment.page_id == FacebookPage.id)
        .where(
            and_(
                FacebookPage.organization_id == organization.id,
                Comment.created_at >= since,
                Comment.comment_created_at.isnot(None),
            )
        )
        .group_by(extract("hour", Comment.comment_created_at))
        .order_by(extract("hour", Comment.comment_created_at))
    )

    if page_id:
        query = query.where(Comment.page_id == page_id)

    result = await db.execute(query)
    rows = result.all()

    # Fill in all 24 hours
    hourly_data = {i: 0 for i in range(24)}
    for row in rows:
        if row.hour is not None:
            hourly_data[int(row.hour)] = row.count

    distribution = [
        {"hour": hour, "count": count}
        for hour, count in hourly_data.items()
    ]

    # Find peak hours
    peak_hour = max(distribution, key=lambda x: x["count"])

    return {
        "distribution": distribution,
        "peak_hour": peak_hour["hour"],
        "peak_count": peak_hour["count"],
        "period_days": days,
    }


@router.get("/ai-usage")
async def get_ai_usage(
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Get AI usage statistics"""
    since = datetime.utcnow() - timedelta(days=days)

    # Total tokens used
    tokens_result = await db.execute(
        select(func.sum(Comment.ai_tokens_used))
        .join(FacebookPage, Comment.page_id == FacebookPage.id)
        .where(
            and_(
                FacebookPage.organization_id == organization.id,
                Comment.created_at >= since,
                Comment.ai_tokens_used.isnot(None),
            )
        )
    )
    total_tokens = tokens_result.scalar() or 0

    # Total cost
    cost_result = await db.execute(
        select(func.sum(Comment.ai_cost))
        .join(FacebookPage, Comment.page_id == FacebookPage.id)
        .where(
            and_(
                FacebookPage.organization_id == organization.id,
                Comment.created_at >= since,
                Comment.ai_cost.isnot(None),
            )
        )
    )
    total_cost = cost_result.scalar() or 0

    # By model
    model_result = await db.execute(
        select(
            Comment.ai_model_used,
            func.count(Comment.id).label("count"),
            func.sum(Comment.ai_tokens_used).label("tokens"),
            func.sum(Comment.ai_cost).label("cost"),
        )
        .join(FacebookPage, Comment.page_id == FacebookPage.id)
        .where(
            and_(
                FacebookPage.organization_id == organization.id,
                Comment.created_at >= since,
                Comment.ai_model_used.isnot(None),
            )
        )
        .group_by(Comment.ai_model_used)
    )
    model_rows = model_result.all()

    by_model = []
    for row in model_rows:
        by_model.append({
            "model": row.ai_model_used,
            "replies": row.count or 0,
            "tokens": row.tokens or 0,
            "cost": round(row.cost or 0, 4),
        })

    # Daily usage
    daily_result = await db.execute(
        select(
            func.date(Comment.created_at).label("date"),
            func.sum(Comment.ai_tokens_used).label("tokens"),
            func.sum(Comment.ai_cost).label("cost"),
        )
        .join(FacebookPage, Comment.page_id == FacebookPage.id)
        .where(
            and_(
                FacebookPage.organization_id == organization.id,
                Comment.created_at >= since,
            )
        )
        .group_by(func.date(Comment.created_at))
        .order_by(func.date(Comment.created_at))
    )
    daily_rows = daily_result.all()

    daily_usage = []
    for row in daily_rows:
        daily_usage.append({
            "date": row.date.isoformat() if row.date else None,
            "tokens": row.tokens or 0,
            "cost": round(row.cost or 0, 4),
        })

    return {
        "total_tokens": total_tokens,
        "total_cost": round(total_cost, 4),
        "by_model": by_model,
        "daily_usage": daily_usage,
        "period_days": days,
    }


@router.get("/response-times")
async def get_response_times(
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Get response time analytics"""
    since = datetime.utcnow() - timedelta(days=days)

    # Average, min, max response times
    stats_result = await db.execute(
        select(
            func.avg(Comment.response_time_seconds).label("avg"),
            func.min(Comment.response_time_seconds).label("min"),
            func.max(Comment.response_time_seconds).label("max"),
            func.count(Comment.id).label("count"),
        )
        .join(FacebookPage, Comment.page_id == FacebookPage.id)
        .where(
            and_(
                FacebookPage.organization_id == organization.id,
                Comment.created_at >= since,
                Comment.reply_status == ReplyStatus.REPLIED,
                Comment.response_time_seconds.isnot(None),
            )
        )
    )
    stats = stats_result.one()

    # Distribution buckets (in seconds)
    buckets = [
        (0, 60, "< 1 min"),
        (60, 300, "1-5 mins"),
        (300, 900, "5-15 mins"),
        (900, 3600, "15-60 mins"),
        (3600, 86400, "1-24 hours"),
        (86400, float("inf"), "> 24 hours"),
    ]

    distribution = []
    for min_val, max_val, label in buckets:
        if max_val == float("inf"):
            count_result = await db.execute(
                select(func.count(Comment.id))
                .join(FacebookPage, Comment.page_id == FacebookPage.id)
                .where(
                    and_(
                        FacebookPage.organization_id == organization.id,
                        Comment.created_at >= since,
                        Comment.reply_status == ReplyStatus.REPLIED,
                        Comment.response_time_seconds >= min_val,
                    )
                )
            )
        else:
            count_result = await db.execute(
                select(func.count(Comment.id))
                .join(FacebookPage, Comment.page_id == FacebookPage.id)
                .where(
                    and_(
                        FacebookPage.organization_id == organization.id,
                        Comment.created_at >= since,
                        Comment.reply_status == ReplyStatus.REPLIED,
                        Comment.response_time_seconds >= min_val,
                        Comment.response_time_seconds < max_val,
                    )
                )
            )
        count = count_result.scalar() or 0
        distribution.append({
            "label": label,
            "count": count,
            "percentage": round((count / stats.count * 100), 2) if stats.count > 0 else 0,
        })

    return {
        "average_seconds": round(stats.avg, 2) if stats.avg else None,
        "average_formatted": format_duration(stats.avg) if stats.avg else None,
        "min_seconds": stats.min,
        "max_seconds": stats.max,
        "total_replies": stats.count,
        "distribution": distribution,
        "period_days": days,
    }


def format_duration(seconds: float) -> str:
    """Format seconds into human readable duration"""
    if seconds is None:
        return None

    seconds = int(seconds)

    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}d {hours}h"
