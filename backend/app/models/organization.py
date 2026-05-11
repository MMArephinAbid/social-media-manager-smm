"""
Organization model - Core multi-tenant entity.
Created by: Sadia (Backend Lead)
"""
from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import Base, UUIDMixin, TimestampMixin


class Organization(Base, UUIDMixin, TimestampMixin):
    """
    Organization model for multi-tenant SaaS.
    Each organization can have multiple users, pages, and settings.
    """
    __tablename__ = 'organizations'

    # Basic Info
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    logo_url = Column(String(500), nullable=True)

    # Contact Info
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    website = Column(String(255), nullable=True)

    # Address
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), default='India')
    postal_code = Column(String(20), nullable=True)

    # Settings (flexible JSON)
    settings = Column(JSONB, default=dict, nullable=False)
    """
    Example settings:
    {
        "timezone": "Asia/Kolkata",
        "language": "bn",
        "currency": "INR",
        "reply_delay_min": 30,
        "reply_delay_max": 120,
        "working_hours": {
            "enabled": true,
            "start": "09:00",
            "end": "21:00",
            "timezone": "Asia/Kolkata"
        },
        "auto_reply_enabled": true,
        "notification_email": "alerts@company.com",
        "ai_provider": "openai",
        "default_tone": "professional"
    }
    """

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    facebook_pages = relationship("FacebookPage", back_populates="organization", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="organization", cascade="all, delete-orphan")
    ai_prompts = relationship("AIPrompt", back_populates="organization", cascade="all, delete-orphan")
    reply_rules = relationship("ReplyRule", back_populates="organization", cascade="all, delete-orphan")
    usage_logs = relationship("UsageLog", back_populates="organization", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="organization", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}', slug='{self.slug}')>"

    @property
    def is_trial(self) -> bool:
        """Check if organization is on trial."""
        active_sub = next(
            (s for s in self.subscriptions if s.status == 'active'),
            None
        )
        return active_sub.plan.name.lower() == 'free' if active_sub else True

    def get_setting(self, key: str, default=None):
        """Get a setting value with default."""
        return self.settings.get(key, default)

    def update_setting(self, key: str, value):
        """Update a setting value."""
        if self.settings is None:
            self.settings = {}
        self.settings[key] = value
