"""
Facebook Page model for connected pages.
Created by: Sadia (Backend Lead)
"""
from sqlalchemy import Column, String, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import Base, UUIDMixin, TimestampMixin, TenantMixin


class FacebookPage(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """
    Facebook Page model for storing connected pages.
    Each organization can connect multiple Facebook pages.
    """
    __tablename__ = 'facebook_pages'

    # Facebook Identifiers
    fb_page_id = Column(String(100), unique=True, nullable=False, index=True)
    fb_user_id = Column(String(100), nullable=True)  # User who connected

    # Page Info (from Facebook)
    page_name = Column(String(255), nullable=False)
    page_category = Column(String(100), nullable=True)
    page_picture_url = Column(String(500), nullable=True)
    page_url = Column(String(500), nullable=True)
    followers_count = Column(String(20), nullable=True)

    # Access Token (encrypted at rest)
    access_token = Column(Text, nullable=False)
    token_expires_at = Column(String(50), nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_webhook_active = Column(Boolean, default=False, nullable=False)
    last_synced_at = Column(String(50), nullable=True)

    # Page-specific Settings
    settings = Column(JSONB, default=dict, nullable=False)
    """
    Example settings:
    {
        "auto_reply_enabled": true,
        "tone": "professional",
        "language": "bn",
        "reply_delay_min": 30,
        "reply_delay_max": 120,
        "working_hours_only": false,
        "custom_system_prompt": "You are a helpful assistant...",
        "excluded_keywords": ["spam", "hate"],
        "ai_model": "gpt-4",
        "max_reply_length": 500,
        "reply_to_mentions": true,
        "reply_to_tags": false
    }
    """

    # Relationships
    organization = relationship("Organization", back_populates="facebook_pages")
    comments = relationship("Comment", back_populates="page", cascade="all, delete-orphan")
    reply_rules = relationship("ReplyRule", back_populates="page", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FacebookPage(id={self.id}, fb_page_id='{self.fb_page_id}', name='{self.page_name}')>"

    def get_setting(self, key: str, default=None):
        """Get a page setting with fallback to org settings."""
        if self.settings and key in self.settings:
            return self.settings[key]
        if self.organization and self.organization.settings:
            return self.organization.settings.get(key, default)
        return default

    @property
    def is_token_valid(self) -> bool:
        """Check if access token is still valid."""
        if not self.token_expires_at:
            return True  # Long-lived tokens don't expire
        from datetime import datetime
        try:
            expires = datetime.fromisoformat(self.token_expires_at)
            return datetime.utcnow() < expires
        except:
            return False
