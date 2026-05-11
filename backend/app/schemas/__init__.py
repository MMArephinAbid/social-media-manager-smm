"""
Pydantic schemas for request/response validation.
Created by: Sadia (Backend Lead)
"""

from .auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    VerifyEmailRequest,
    UserResponse,
    MeResponse,
    MessageResponse,
)

from .organization import (
    OrganizationSettings,
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationWithStats,
    OrganizationListResponse,
)

from .facebook import (
    PageSettings,
    FacebookAuthURLResponse,
    FacebookCallbackRequest,
    FacebookPageInfo,
    ConnectPageRequest,
    PageResponse,
    PageUpdateRequest,
    PageListResponse,
    AvailablePageResponse,
    CommentResponse,
    CommentListResponse,
    CommentFilters,
    ManualReplyRequest,
    RetryReplyRequest,
    FacebookWebhookVerification,
    FacebookWebhookPayload,
)

from .billing import (
    PlanFeatures,
    PlanResponse,
    PlanListResponse,
    SubscriptionResponse,
    SubscriptionWithUsage,
    CheckoutRequest,
    CheckoutResponse,
    RazorpayVerifyRequest,
    CancelSubscriptionRequest,
    InvoiceResponse,
    InvoiceListResponse,
    UsageResponse,
    UsageHistoryResponse,
)

from .ai import (
    AIPromptCreate,
    AIPromptUpdate,
    AIPromptResponse,
    AIPromptListResponse,
    TestPromptRequest,
    TestPromptResponse,
    ReplyRuleCreate,
    ReplyRuleUpdate,
    ReplyRuleResponse,
    ReplyRuleListResponse,
    TestRuleRequest,
    TestRuleResponse,
)

__all__ = [
    # Auth
    "RegisterRequest",
    "LoginRequest",
    "TokenResponse",
    "RefreshTokenRequest",
    "ForgotPasswordRequest",
    "ResetPasswordRequest",
    "ChangePasswordRequest",
    "VerifyEmailRequest",
    "UserResponse",
    "MeResponse",
    "MessageResponse",

    # Organization
    "OrganizationSettings",
    "OrganizationCreate",
    "OrganizationUpdate",
    "OrganizationResponse",
    "OrganizationWithStats",
    "OrganizationListResponse",

    # Facebook
    "PageSettings",
    "FacebookAuthURLResponse",
    "FacebookCallbackRequest",
    "FacebookPageInfo",
    "ConnectPageRequest",
    "PageResponse",
    "PageUpdateRequest",
    "PageListResponse",
    "AvailablePageResponse",
    "CommentResponse",
    "CommentListResponse",
    "CommentFilters",
    "ManualReplyRequest",
    "RetryReplyRequest",
    "FacebookWebhookVerification",
    "FacebookWebhookPayload",

    # Billing
    "PlanFeatures",
    "PlanResponse",
    "PlanListResponse",
    "SubscriptionResponse",
    "SubscriptionWithUsage",
    "CheckoutRequest",
    "CheckoutResponse",
    "RazorpayVerifyRequest",
    "CancelSubscriptionRequest",
    "InvoiceResponse",
    "InvoiceListResponse",
    "UsageResponse",
    "UsageHistoryResponse",

    # AI
    "AIPromptCreate",
    "AIPromptUpdate",
    "AIPromptResponse",
    "AIPromptListResponse",
    "TestPromptRequest",
    "TestPromptResponse",
    "ReplyRuleCreate",
    "ReplyRuleUpdate",
    "ReplyRuleResponse",
    "ReplyRuleListResponse",
    "TestRuleRequest",
    "TestRuleResponse",
]
