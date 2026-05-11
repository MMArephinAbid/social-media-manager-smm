"""
Database models for AIOSOL SaaS Platform.
Created by: Sadia (Backend Lead)

All models are multi-tenant ready with organization_id.
"""

from .base import Base, TimestampMixin, UUIDMixin, TenantMixin
from .organization import Organization
from .user import User, UserRole
from .facebook_page import FacebookPage
from .comment import Comment, ReplyStatus
from .subscription import (
    Plan,
    Subscription,
    Invoice,
    SubscriptionStatus,
    BillingCycle
)
from .ai_prompt import (
    AIPrompt,
    ReplyRule,
    ToneType,
    RuleActionType
)
from .logs import (
    UsageLog,
    WebhookLog,
    AuditLog,
    SystemLog
)

__all__ = [
    # Base
    "Base",
    "TimestampMixin",
    "UUIDMixin",
    "TenantMixin",

    # Core Models
    "Organization",
    "User",
    "UserRole",

    # Facebook
    "FacebookPage",
    "Comment",
    "ReplyStatus",

    # Billing
    "Plan",
    "Subscription",
    "Invoice",
    "SubscriptionStatus",
    "BillingCycle",

    # AI
    "AIPrompt",
    "ReplyRule",
    "ToneType",
    "RuleActionType",

    # Logs
    "UsageLog",
    "WebhookLog",
    "AuditLog",
    "SystemLog",
]
