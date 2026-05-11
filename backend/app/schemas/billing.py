"""
Billing and subscription schemas.
Created by: Sadia (Backend Lead)
"""
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field


class PlanFeatures(BaseModel):
    """Schema for plan features."""

    custom_prompts: bool = False
    analytics: bool = False
    api_access: bool = False
    white_label: bool = False
    priority_support: bool = False
    custom_ai_model: bool = False
    webhook_notifications: bool = False
    export_data: bool = False
    team_members: bool = False
    custom_domain: bool = False


class PlanResponse(BaseModel):
    """Response schema for subscription plan."""

    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    price_monthly: float
    price_yearly: float
    max_pages: int
    max_replies_per_month: int
    max_users: int
    max_rules: int
    features: Dict[str, Any]
    is_active: bool
    is_featured: bool

    class Config:
        from_attributes = True


class PlanListResponse(BaseModel):
    """Response for listing plans."""

    plans: List[PlanResponse]
    total: int


class CreateSubscriptionRequest(BaseModel):
    """Request to create a subscription."""

    plan_id: UUID
    billing_cycle: str = "monthly"  # monthly, yearly


class RazorpayOrderResponse(BaseModel):
    """Response for Razorpay order creation."""

    order_id: str
    amount: int
    currency: str
    key_id: str
    plan_name: str
    organization_name: str
    user_email: str
    user_name: str


class VerifyPaymentRequest(BaseModel):
    """Request to verify payment."""

    order_id: str
    payment_id: str
    signature: str


class SubscriptionResponse(BaseModel):
    """Response schema for subscription."""

    id: UUID
    plan: PlanResponse
    status: str
    billing_cycle: str
    current_period_start: Optional[str] = None
    current_period_end: Optional[str] = None
    trial_end: Optional[str] = None
    cancelled_at: Optional[str] = None
    replies_used: int
    pages_used: int
    payment_method: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class SubscriptionWithUsage(SubscriptionResponse):
    """Subscription with usage percentages."""

    usage_percentage: Dict[str, float] = {}
    days_remaining: int = 0


class CheckoutRequest(BaseModel):
    """Request to create checkout session."""

    plan_id: UUID
    billing_cycle: str = "monthly"  # monthly, yearly
    payment_method: str = "razorpay"  # razorpay, stripe
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class CheckoutResponse(BaseModel):
    """Response for checkout session."""

    checkout_url: Optional[str] = None
    session_id: Optional[str] = None
    order_id: Optional[str] = None  # For Razorpay
    subscription_id: Optional[str] = None


class RazorpayVerifyRequest(BaseModel):
    """Request to verify Razorpay payment."""

    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str
    razorpay_subscription_id: Optional[str] = None


class CancelSubscriptionRequest(BaseModel):
    """Request to cancel subscription."""

    reason: Optional[str] = None
    feedback: Optional[str] = None
    cancel_immediately: bool = False


class InvoiceResponse(BaseModel):
    """Response schema for invoice."""

    id: UUID
    invoice_number: str
    amount: float
    currency: str
    tax_amount: float
    total_amount: float
    status: str
    paid_at: Optional[str] = None
    payment_method: Optional[str] = None
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    pdf_url: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class InvoiceListResponse(BaseModel):
    """Response for listing invoices."""

    items: List[InvoiceResponse]
    total: int
    page: int
    per_page: int


class UsageResponse(BaseModel):
    """Response for usage statistics."""

    replies_used: int
    replies_limit: int
    replies_percentage: float
    pages_used: int
    pages_limit: int
    pages_percentage: float
    current_period_start: Optional[str] = None
    current_period_end: Optional[str] = None
    days_remaining: int


class UsageHistoryItem(BaseModel):
    """Single item in usage history."""

    date: str
    replies: int
    tokens: int
    cost: float


class UsageHistoryResponse(BaseModel):
    """Response for usage history."""

    items: List[UsageHistoryItem]
    total_replies: int
    total_tokens: int
    total_cost: float
