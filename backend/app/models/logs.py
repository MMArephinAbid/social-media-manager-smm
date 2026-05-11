"""
Logging models for usage, webhooks, and audits.
Created by: Sadia (Backend Lead)
"""
from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import Base, UUIDMixin, TimestampMixin, TenantMixin


class UsageLog(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """
    Track AI usage and costs per organization.
    Used for billing and analytics.
    """
    __tablename__ = 'usage_logs'

    # Action Type
    action_type = Column(String(50), nullable=False)  # ai_reply, sentiment_analysis, etc.

    # AI Details
    ai_provider = Column(String(50), nullable=True)  # openai, anthropic
    ai_model = Column(String(50), nullable=True)     # gpt-4, claude-3

    # Token Usage
    prompt_tokens = Column(Integer, default=0, nullable=False)
    completion_tokens = Column(Integer, default=0, nullable=False)
    total_tokens = Column(Integer, default=0, nullable=False)

    # Cost (in USD)
    cost = Column(Float, default=0.0, nullable=False)

    # Reference
    reference_type = Column(String(50), nullable=True)  # comment, batch
    reference_id = Column(UUID(as_uuid=True), nullable=True)

    # Metadata
    metadata = Column(JSONB, default=dict, nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="usage_logs")

    def __repr__(self):
        return f"<UsageLog(id={self.id}, action='{self.action_type}', tokens={self.total_tokens})>"


class WebhookLog(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """
    Log all incoming webhooks for debugging and auditing.
    """
    __tablename__ = 'webhook_logs'

    # Webhook Source
    source = Column(String(50), nullable=False)  # facebook, razorpay, stripe
    event_type = Column(String(100), nullable=True)  # e.g., feed, messages

    # Request Details
    http_method = Column(String(10), default='POST', nullable=False)
    headers = Column(JSONB, default=dict, nullable=True)
    payload = Column(JSONB, nullable=True)

    # Processing
    status = Column(String(20), default='received', nullable=False)  # received, processed, failed
    processed_at = Column(String(50), nullable=True)
    processing_time_ms = Column(Integer, nullable=True)

    # Error (if failed)
    error_message = Column(Text, nullable=True)

    # Relationships
    organization = relationship("Organization")

    def __repr__(self):
        return f"<WebhookLog(id={self.id}, source='{self.source}', status='{self.status}')>"


class AuditLog(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """
    Audit trail for all important actions.
    """
    __tablename__ = 'audit_logs'

    # User who performed action
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )

    # Action Details
    action = Column(String(100), nullable=False)  # create, update, delete, login, etc.
    entity_type = Column(String(50), nullable=False)  # user, page, subscription, etc.
    entity_id = Column(UUID(as_uuid=True), nullable=True)

    # Change Details
    old_values = Column(JSONB, nullable=True)
    new_values = Column(JSONB, nullable=True)

    # Request Info
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(String(500), nullable=True)

    # Additional Context
    description = Column(Text, nullable=True)
    metadata = Column(JSONB, default=dict, nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', entity='{self.entity_type}')>"


class SystemLog(Base, UUIDMixin, TimestampMixin):
    """
    System-level logs (not tenant-specific).
    For platform-wide events and errors.
    """
    __tablename__ = 'system_logs'

    # Log Level
    level = Column(String(20), default='info', nullable=False)  # debug, info, warning, error, critical

    # Log Details
    source = Column(String(100), nullable=False)  # module/service name
    message = Column(Text, nullable=False)

    # Context
    context = Column(JSONB, default=dict, nullable=True)

    # Error Details (if applicable)
    exception_type = Column(String(100), nullable=True)
    exception_message = Column(Text, nullable=True)
    stack_trace = Column(Text, nullable=True)

    def __repr__(self):
        return f"<SystemLog(id={self.id}, level='{self.level}', source='{self.source}')>"
