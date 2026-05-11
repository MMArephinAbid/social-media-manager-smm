"""
Subscription and Plan models for billing.
Created by: Sadia (Backend Lead)
"""
from enum import Enum
from sqlalchemy import Column, String, Boolean, Integer, Float, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import Base, UUIDMixin, TimestampMixin, TenantMixin


class SubscriptionStatus(str, Enum):
    """Subscription status."""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"
    PAUSED = "paused"
    EXPIRED = "expired"


class BillingCycle(str, Enum):
    """Billing cycle options."""
    MONTHLY = "monthly"
    YEARLY = "yearly"


class Plan(Base, UUIDMixin, TimestampMixin):
    """
    Subscription plans available in the system.
    """
    __tablename__ = 'plans'

    # Plan Info
    name = Column(String(100), nullable=False)  # Free, Starter, Pro, Business
    slug = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    # Pricing (in INR)
    price_monthly = Column(Float, default=0.0, nullable=False)
    price_yearly = Column(Float, default=0.0, nullable=False)

    # Limits
    max_pages = Column(Integer, default=1, nullable=False)
    max_replies_per_month = Column(Integer, default=100, nullable=False)
    max_users = Column(Integer, default=1, nullable=False)
    max_rules = Column(Integer, default=5, nullable=False)

    # Features (flexible JSON)
    features = Column(JSONB, default=dict, nullable=False)
    """
    Example features:
    {
        "custom_prompts": true,
        "analytics": true,
        "api_access": false,
        "white_label": false,
        "priority_support": false,
        "custom_ai_model": false,
        "webhook_notifications": false,
        "export_data": true,
        "team_members": true,
        "custom_domain": false
    }
    """

    # Payment Gateway IDs
    razorpay_plan_id_monthly = Column(String(100), nullable=True)
    razorpay_plan_id_yearly = Column(String(100), nullable=True)
    stripe_price_id_monthly = Column(String(100), nullable=True)
    stripe_price_id_yearly = Column(String(100), nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)  # Highlighted plan
    sort_order = Column(Integer, default=0, nullable=False)

    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")

    def __repr__(self):
        return f"<Plan(id={self.id}, name='{self.name}', price_monthly={self.price_monthly})>"

    def has_feature(self, feature: str) -> bool:
        """Check if plan has a feature."""
        return self.features.get(feature, False)


class Subscription(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """
    Organization subscriptions.
    """
    __tablename__ = 'subscriptions'

    # Plan Reference
    plan_id = Column(
        UUID(as_uuid=True),
        ForeignKey('plans.id'),
        nullable=False
    )

    # Status
    status = Column(
        SQLEnum(SubscriptionStatus),
        default=SubscriptionStatus.TRIALING,
        nullable=False,
        index=True
    )
    billing_cycle = Column(
        SQLEnum(BillingCycle),
        default=BillingCycle.MONTHLY,
        nullable=False
    )

    # Period
    current_period_start = Column(String(50), nullable=True)
    current_period_end = Column(String(50), nullable=True)
    trial_end = Column(String(50), nullable=True)
    cancelled_at = Column(String(50), nullable=True)

    # Payment Gateway References
    razorpay_subscription_id = Column(String(100), nullable=True)
    razorpay_customer_id = Column(String(100), nullable=True)
    stripe_subscription_id = Column(String(100), nullable=True)
    stripe_customer_id = Column(String(100), nullable=True)

    # Payment Method
    payment_method = Column(String(50), nullable=True)  # razorpay, stripe

    # Usage (current period)
    replies_used = Column(Integer, default=0, nullable=False)
    pages_used = Column(Integer, default=0, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")
    invoices = relationship("Invoice", back_populates="subscription", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Subscription(id={self.id}, status='{self.status}', plan='{self.plan.name if self.plan else None}')>"

    @property
    def is_active(self) -> bool:
        """Check if subscription is active."""
        return self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]

    def can_add_page(self) -> bool:
        """Check if organization can add more pages."""
        return self.pages_used < self.plan.max_pages

    def can_reply(self) -> bool:
        """Check if organization can send more replies."""
        return self.replies_used < self.plan.max_replies_per_month

    def get_usage_percentage(self) -> dict:
        """Get usage percentages."""
        return {
            'pages': (self.pages_used / self.plan.max_pages) * 100 if self.plan.max_pages > 0 else 0,
            'replies': (self.replies_used / self.plan.max_replies_per_month) * 100 if self.plan.max_replies_per_month > 0 else 0
        }


class Invoice(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """
    Invoice records for billing history.
    """
    __tablename__ = 'invoices'

    # Subscription Reference
    subscription_id = Column(
        UUID(as_uuid=True),
        ForeignKey('subscriptions.id', ondelete='SET NULL'),
        nullable=True
    )

    # Invoice Details
    invoice_number = Column(String(50), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default='INR', nullable=False)
    tax_amount = Column(Float, default=0.0, nullable=False)
    total_amount = Column(Float, nullable=False)

    # Status
    status = Column(String(20), default='pending', nullable=False)  # pending, paid, failed, refunded
    paid_at = Column(String(50), nullable=True)

    # Payment Info
    payment_method = Column(String(50), nullable=True)
    razorpay_payment_id = Column(String(100), nullable=True)
    stripe_payment_intent_id = Column(String(100), nullable=True)

    # Period
    period_start = Column(String(50), nullable=True)
    period_end = Column(String(50), nullable=True)

    # PDF
    pdf_url = Column(String(500), nullable=True)

    # Relationships
    organization = relationship("Organization")
    subscription = relationship("Subscription", back_populates="invoices")

    def __repr__(self):
        return f"<Invoice(id={self.id}, number='{self.invoice_number}', amount={self.amount})>"
