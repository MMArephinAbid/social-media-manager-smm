"""
Facebook Webhooks API - Handle incoming Facebook events
Created by: Sadia (Backend Lead)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional
from datetime import datetime
import json
import hashlib
import hmac

from app.database import get_db
from app.models.facebook_page import FacebookPage, PageStatus
from app.models.comment import Comment, ReplyStatus
from app.models.organization import Organization
from app.services.facebook_service import FacebookService
from app.services.ai_service import AIService
from app.config import settings

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.get("/facebook")
async def verify_facebook_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
):
    """
    Facebook webhook verification endpoint.
    Facebook sends a GET request to verify the webhook URL.
    """
    if hub_mode != "subscribe":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid hub.mode"
        )

    if hub_verify_token != settings.FACEBOOK_WEBHOOK_VERIFY_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid verify token"
        )

    # Return the challenge to confirm verification
    return int(hub_challenge)


@router.post("/facebook")
async def handle_facebook_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Handle incoming Facebook webhook events.
    Processes new comments and triggers AI reply generation.
    """
    body = await request.body()

    # Verify signature
    signature = request.headers.get("X-Hub-Signature-256")
    if signature:
        expected_signature = "sha256=" + hmac.new(
            settings.FACEBOOK_APP_SECRET.encode(),
            body,
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_signature):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid signature"
            )

    payload = json.loads(body)

    # Handle different object types
    object_type = payload.get("object")

    if object_type == "page":
        await process_page_events(payload, db)
    elif object_type == "instagram":
        await process_instagram_events(payload, db)

    # Always return 200 OK to Facebook
    return {"status": "ok"}


async def process_page_events(payload: dict, db: AsyncSession):
    """Process Facebook page events (comments, mentions, etc.)"""
    entries = payload.get("entry", [])

    for entry in entries:
        page_id = entry.get("id")

        # Find the page in our database
        result = await db.execute(
            select(FacebookPage).where(
                and_(
                    FacebookPage.page_id == page_id,
                    FacebookPage.status == PageStatus.ACTIVE,
                )
            )
        )
        page = result.scalar_one_or_none()

        if not page:
            continue

        # Process changes
        changes = entry.get("changes", [])

        for change in changes:
            field = change.get("field")
            value = change.get("value", {})

            if field == "feed":
                # New comment or reaction
                item = value.get("item")

                if item == "comment":
                    await handle_new_comment(page, value, db)
                elif item == "reaction":
                    await handle_reaction(page, value, db)
                elif item == "post":
                    # New post - might want to track
                    pass

            elif field == "mention":
                # Page was mentioned
                await handle_mention(page, value, db)


async def handle_new_comment(page: FacebookPage, data: dict, db: AsyncSession):
    """Handle a new comment on a page post"""
    verb = data.get("verb")

    # Only process new comments (add), not edits or deletes
    if verb not in ["add"]:
        return

    comment_id = data.get("comment_id")
    post_id = data.get("post_id")
    sender_id = data.get("sender_id")
    sender_name = data.get("sender_name")
    message = data.get("message", "")
    created_time = data.get("created_time")

    # Don't reply to page's own comments
    if sender_id == page.page_id:
        return

    # Check if comment already exists
    existing = await db.execute(
        select(Comment).where(Comment.fb_comment_id == comment_id)
    )
    if existing.scalar_one_or_none():
        return

    # Get post context from Facebook
    fb_service = FacebookService()
    try:
        post_data = await fb_service.get_post(post_id, page.access_token)
        post_message = post_data.get("message", "")
        post_type = post_data.get("type", "status")
    except Exception:
        post_message = ""
        post_type = "unknown"

    # Parse timestamp
    try:
        comment_created_at = datetime.fromisoformat(created_time.replace("Z", "+00:00"))
    except Exception:
        comment_created_at = datetime.utcnow()

    # Create comment record
    comment = Comment(
        page_id=page.id,
        organization_id=page.organization_id,
        fb_comment_id=comment_id,
        fb_post_id=post_id,
        fb_sender_id=sender_id,
        commenter_name=sender_name,
        comment_text=message,
        comment_created_at=comment_created_at,
        post_message=post_message,
        post_type=post_type,
        reply_status=ReplyStatus.PENDING,
    )

    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    # Get organization settings
    org_result = await db.execute(
        select(Organization).where(Organization.id == page.organization_id)
    )
    organization = org_result.scalar_one()

    # Check if auto-reply is enabled
    page_settings = page.settings or {}
    org_settings = organization.settings or {}

    auto_reply_enabled = page_settings.get(
        "auto_reply_enabled",
        org_settings.get("auto_reply_enabled", True)
    )

    if not auto_reply_enabled:
        return

    # Check for excluded keywords
    excluded_keywords = page_settings.get("excluded_keywords", [])
    message_lower = message.lower()

    for keyword in excluded_keywords:
        if keyword.lower() in message_lower:
            comment.reply_status = ReplyStatus.SKIPPED
            comment.skip_reason = f"Contains excluded keyword: {keyword}"
            await db.commit()
            return

    # TODO: Queue for background processing with delay
    # For now, process immediately (should use Celery in production)
    await process_comment_reply(comment, page, organization, db)


async def process_comment_reply(
    comment: Comment,
    page: FacebookPage,
    organization: Organization,
    db: AsyncSession
):
    """Generate AI reply and post to Facebook"""
    comment.reply_status = ReplyStatus.PROCESSING
    await db.commit()

    ai_service = AIService()
    fb_service = FacebookService()

    try:
        # Generate AI reply
        reply_result = await ai_service.generate_reply(
            comment_text=comment.comment_text,
            post_context=comment.post_message,
            organization=organization,
        )

        reply_text = reply_result["reply_text"]

        # Post reply to Facebook
        reply_id = await fb_service.post_reply(
            comment_id=comment.fb_comment_id,
            reply_text=reply_text,
            access_token=page.access_token,
        )

        # Update comment record
        comment.reply_text = reply_text
        comment.reply_status = ReplyStatus.REPLIED
        comment.replied_at = datetime.utcnow()
        comment.fb_reply_id = reply_id
        comment.ai_model_used = reply_result.get("model")
        comment.ai_tokens_used = reply_result.get("tokens_used")
        comment.ai_cost = reply_result.get("cost")
        comment.sentiment = reply_result.get("sentiment")

        # Calculate response time
        if comment.comment_created_at:
            delta = datetime.utcnow() - comment.comment_created_at
            comment.response_time_seconds = int(delta.total_seconds())

        await db.commit()

        # Update subscription usage
        # TODO: Increment replies_used in subscription

    except Exception as e:
        comment.reply_status = ReplyStatus.FAILED
        comment.error_message = str(e)
        await db.commit()


async def handle_reaction(page: FacebookPage, data: dict, db: AsyncSession):
    """Handle reactions on posts/comments (optional tracking)"""
    # Can be used for engagement analytics
    pass


async def handle_mention(page: FacebookPage, data: dict, db: AsyncSession):
    """Handle page mentions"""
    # Similar to comments, but for mentions
    pass


async def process_instagram_events(payload: dict, db: AsyncSession):
    """Process Instagram events (future expansion)"""
    # Similar structure to Facebook page events
    pass


# ============== Webhook Management ==============

@router.post("/facebook/test")
async def test_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Test endpoint to simulate a webhook event"""
    if not settings.DEBUG:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only available in debug mode"
        )

    body = await request.json()

    # Simulate processing
    return {
        "status": "ok",
        "received": body,
        "message": "Test webhook processed"
    }


@router.get("/facebook/status")
async def webhook_status():
    """Check webhook configuration status"""
    fb_service = FacebookService()

    try:
        # Try to get app subscriptions
        subscriptions = await fb_service.get_app_subscriptions()
        return {
            "status": "configured",
            "subscriptions": subscriptions,
            "verify_token_set": bool(settings.FACEBOOK_WEBHOOK_VERIFY_TOKEN),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "verify_token_set": bool(settings.FACEBOOK_WEBHOOK_VERIFY_TOKEN),
        }
