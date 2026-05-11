"""
Comment model for storing Facebook comments and replies.
Created by: Sadia (Backend Lead)
"""
from enum import Enum
from sqlalchemy import Column, String, Boolean, Text, Integer, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import Base, UUIDMixin, TimestampMixin, TenantMixin


class ReplyStatus(str, Enum):
    """Status of reply processing."""
    PENDING = "pending"           # Queued for processing
    PROCESSING = "processing"     # Currently being processed
    REPLIED = "replied"           # Successfully replied
    FAILED = "failed"             # Failed to reply
    SKIPPED = "skipped"           # Skipped (filtered by rules)
    MANUAL = "manual"             # Marked for manual reply


class Comment(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """
    Comment model for storing Facebook comments and their AI replies.
    """
    __tablename__ = 'comments'

    # Page Reference
    page_id = Column(
        UUID(as_uuid=True),
        ForeignKey('facebook_pages.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Facebook Identifiers
    fb_comment_id = Column(String(100), unique=True, nullable=False, index=True)
    fb_post_id = Column(String(100), nullable=False, index=True)
    fb_parent_comment_id = Column(String(100), nullable=True)  # For reply threads

    # Comment Info
    commenter_fb_id = Column(String(100), nullable=True)
    commenter_name = Column(String(255), nullable=True)
    commenter_picture_url = Column(String(500), nullable=True)
    comment_text = Column(Text, nullable=False)
    comment_created_at = Column(String(50), nullable=True)  # Facebook timestamp

    # Post Info (cached)
    post_message = Column(Text, nullable=True)
    post_type = Column(String(50), nullable=True)  # photo, video, link, status

    # AI Analysis
    sentiment = Column(String(20), nullable=True)  # positive, negative, neutral
    language = Column(String(10), nullable=True)   # bn, en, hi, etc.
    intent = Column(String(50), nullable=True)     # question, complaint, praise, etc.
    keywords = Column(JSONB, default=list, nullable=True)

    # Reply Info
    reply_status = Column(
        SQLEnum(ReplyStatus),
        default=ReplyStatus.PENDING,
        nullable=False,
        index=True
    )
    reply_text = Column(Text, nullable=True)
    fb_reply_id = Column(String(100), nullable=True)
    replied_at = Column(String(50), nullable=True)

    # AI Details
    ai_model_used = Column(String(50), nullable=True)  # gpt-4, claude-3, etc.
    tokens_used = Column(Integer, default=0, nullable=False)
    ai_cost = Column(Float, default=0.0, nullable=False)  # Cost in USD
    processing_time_ms = Column(Integer, nullable=True)

    # Rule Matching
    matched_rule_id = Column(UUID(as_uuid=True), nullable=True)
    skip_reason = Column(String(255), nullable=True)

    # Error Tracking
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)

    # Manual Reply Tracking
    is_manual_reply = Column(Boolean, default=False)
    replied_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    skipped_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    skipped_at = Column(String(50), nullable=True)

    # Response Time Tracking
    response_time_seconds = Column(Integer, nullable=True)
    ai_tokens_used = Column(Integer, nullable=True)

    # FB Sender ID
    fb_sender_id = Column(String(100), nullable=True)

    # Metadata
    metadata = Column(JSONB, default=dict, nullable=True)

    # Relationships
    organization = relationship("Organization")
    page = relationship("FacebookPage", back_populates="comments")

    def __repr__(self):
        return f"<Comment(id={self.id}, fb_comment_id='{self.fb_comment_id}', status='{self.reply_status}')>"

    @property
    def is_reply(self) -> bool:
        """Check if this is a reply to another comment."""
        return self.fb_parent_comment_id is not None

    @property
    def can_retry(self) -> bool:
        """Check if we can retry processing."""
        return self.reply_status == ReplyStatus.FAILED and self.retry_count < 3
