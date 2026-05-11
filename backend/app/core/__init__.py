"""
Core utilities for AIOSOL SaaS Platform.
Created by: Sadia (Backend Lead)
"""

from .security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_access_token,
    verify_refresh_token,
    encrypt_string,
    decrypt_string,
    generate_random_token,
    generate_verification_code,
    verify_facebook_signature,
    verify_razorpay_signature,
)

from .exceptions import (
    AIOSOLException,
    AuthenticationException,
    InvalidCredentialsException,
    TokenExpiredException,
    InvalidTokenException,
    AuthorizationException,
    PermissionDeniedException,
    TenantAccessDeniedException,
    ResourceNotFoundException,
    ResourceAlreadyExistsException,
    ValidationException,
    RateLimitExceededException,
    BillingException,
    SubscriptionRequiredException,
    PlanLimitExceededException,
    PaymentFailedException,
    FacebookException,
    FacebookTokenExpiredException,
    AIException,
)

from .permissions import (
    Permission,
    has_permission,
    has_any_permission,
    has_all_permissions,
    PermissionChecker,
    require_permission,
    require_roles,
    is_super_admin,
    is_org_owner_or_above,
    is_org_admin_or_above,
)

from .middleware import (
    get_current_tenant_id,
    set_current_tenant_id,
    get_request_id,
    RequestIDMiddleware,
    TimingMiddleware,
    TenantMiddleware,
    SecurityHeadersMiddleware,
)

__all__ = [
    # Security
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "verify_access_token",
    "verify_refresh_token",
    "encrypt_string",
    "decrypt_string",
    "generate_random_token",
    "generate_verification_code",
    "verify_facebook_signature",
    "verify_razorpay_signature",

    # Exceptions
    "AIOSOLException",
    "AuthenticationException",
    "InvalidCredentialsException",
    "TokenExpiredException",
    "InvalidTokenException",
    "AuthorizationException",
    "PermissionDeniedException",
    "TenantAccessDeniedException",
    "ResourceNotFoundException",
    "ResourceAlreadyExistsException",
    "ValidationException",
    "RateLimitExceededException",
    "BillingException",
    "SubscriptionRequiredException",
    "PlanLimitExceededException",
    "PaymentFailedException",
    "FacebookException",
    "FacebookTokenExpiredException",
    "AIException",

    # Permissions
    "Permission",
    "has_permission",
    "has_any_permission",
    "has_all_permissions",
    "PermissionChecker",
    "require_permission",
    "require_roles",
    "is_super_admin",
    "is_org_owner_or_above",
    "is_org_admin_or_above",

    # Middleware
    "get_current_tenant_id",
    "set_current_tenant_id",
    "get_request_id",
    "RequestIDMiddleware",
    "TimingMiddleware",
    "TenantMiddleware",
    "SecurityHeadersMiddleware",
]
