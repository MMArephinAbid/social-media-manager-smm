"""
Facebook-related schemas.
Created by: Sadia (Backend Lead)
"""
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field


class PageSettings(BaseModel):
    """Schema for page-specific settings."""

    auto_reply_enabled: bool = True
    tone: str = "professional"
    language: str = "bn"
    reply_delay_min: int = 30
    reply_delay_max: int = 120
    working_hours_only: bool = False
    custom_system_prompt: Optional[str] = None
    excluded_keywords: List[str] = []
    ai_model: str = "gpt-4"
    max_reply_length: int = 500
    reply_to_mentions: bool = True
    reply_to_tags: bool = False


class FacebookAuthURLResponse(BaseModel):
    """Response for Facebook OAuth URL."""

    auth_url: str
    state: str


class FacebookOAuthURLResponse(BaseModel):
    """Response for Facebook OAuth URL (simplified)."""

    oauth_url: str


class FacebookCallbackRequest(BaseModel):
    """Request from Facebook OAuth callback."""

    code: str
    state: str


class FacebookPageInfo(BaseModel):
    """Facebook page information from API."""

    id: str
    name: str
    category: Optional[str] = None
    picture_url: Optional[str] = None
    access_token: str
    followers_count: Optional[int] = None


class ConnectPageRequest(BaseModel):
    """Request to connect a Facebook page."""

    page_id: str
    user_access_token: str
    page_name: str
    page_category: Optional[str] = None
    page_picture_url: Optional[str] = None


class FacebookPageResponse(BaseModel):
    """Response schema for a Facebook page."""

    id: UUID
    page_id: str
    page_name: str
    status: str
    category: Optional[str] = None
    picture_url: Optional[str] = None
    followers_count: Optional[int] = None
    is_webhook_active: bool = True
    settings: Dict[str, Any] = {}
    connected_at: Optional[str] = None
    last_synced_at: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class FacebookPageListResponse(BaseModel):
    """Response for listing Facebook pages."""

    pages: List["FacebookPageResponse"]
    total: int


class PageStatsResponse(BaseModel):
    """Statistics for a Facebook page."""

    page_id: str
    page_name: str
    period_days: int
    total_comments: int
    replied_comments: int
    pending_comments: int
    failed_comments: int
    reply_rate: float


class PageResponse(BaseModel):
    """Response schema for connected page."""

    id: UUID
    fb_page_id: str
    page_name: str
    page_category: Optional[str] = None
    page_picture_url: Optional[str] = None
    page_url: Optional[str] = None
    followers_count: Optional[str] = None
    is_active: bool
    is_webhook_active: bool
    settings: Dict[str, Any]
    last_synced_at: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class PageUpdateRequest(BaseModel):
    """Request to update page settings."""

    is_active: Optional[bool] = None
    settings: Optional[PageSettings] = None


class PageListResponse(BaseModel):
    """Response for listing pages."""

    items: List[PageResponse]
    total: int


class AvailablePageResponse(BaseModel):
    """Response for available pages to connect."""

    pages: List[FacebookPageInfo]
    total: int


# ============== Comment Schemas ==============

class CommentResponse(BaseModel):
    """Response schema for a comment."""

    id: UUID
    fb_comment_id: str
    fb_post_id: str
    commenter_name: Optional[str] = None
    commenter_picture_url: Optional[str] = None
    comment_text: str
    comment_created_at: Optional[str] = None
    post_message: Optional[str] = None
    post_type: Optional[str] = None
    sentiment: Optional[str] = None
    language: Optional[str] = None
    reply_status: str
    reply_text: Optional[str] = None
    replied_at: Optional[str] = None
    ai_model_used: Optional[str] = None
    error_message: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class CommentListResponse(BaseModel):
    """Response for listing comments."""

    items: List[CommentResponse]
    total: int
    page: int
    per_page: int
    pages: int


class CommentFilters(BaseModel):
    """Filters for comment listing."""

    page_id: Optional[UUID] = None
    status: Optional[str] = None  # pending, replied, failed, skipped
    sentiment: Optional[str] = None
    search: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None


class ManualReplyRequest(BaseModel):
    """Request to manually reply to a comment."""

    reply_text: str = Field(..., min_length=1, max_length=2000)


class RetryReplyRequest(BaseModel):
    """Request to retry AI reply for a comment."""

    prompt_id: Optional[UUID] = None  # Use specific prompt


# ============== Webhook Schemas ==============

class FacebookWebhookVerification(BaseModel):
    """Query params for webhook verification."""

    hub_mode: str = Field(..., alias="hub.mode")
    hub_verify_token: str = Field(..., alias="hub.verify_token")
    hub_challenge: str = Field(..., alias="hub.challenge")

    class Config:
        populate_by_name = True


class FacebookWebhookEntry(BaseModel):
    """Single entry in webhook payload."""

    id: str
    time: int
    changes: Optional[List[Dict[str, Any]]] = None
    messaging: Optional[List[Dict[str, Any]]] = None


class FacebookWebhookPayload(BaseModel):
    """Facebook webhook payload."""

    object: str
    entry: List[FacebookWebhookEntry]
