"""
Custom exceptions for the application.
Created by: Sadia (Backend Lead)
"""
from typing import Any, Dict, Optional


class AIOSOLException(Exception):
    """Base exception for all AIOSOL exceptions."""

    def __init__(
        self,
        message: str = "An error occurred",
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


# ============== Authentication Exceptions ==============

class AuthenticationException(AIOSOLException):
    """Base authentication exception."""

    def __init__(
        self,
        message: str = "Authentication failed",
        code: str = "AUTH_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=code,
            status_code=401,
            details=details
        )


class InvalidCredentialsException(AuthenticationException):
    """Invalid email or password."""

    def __init__(self):
        super().__init__(
            message="Invalid email or password",
            code="INVALID_CREDENTIALS"
        )


class TokenExpiredException(AuthenticationException):
    """JWT token has expired."""

    def __init__(self):
        super().__init__(
            message="Token has expired",
            code="TOKEN_EXPIRED"
        )


class InvalidTokenException(AuthenticationException):
    """JWT token is invalid."""

    def __init__(self):
        super().__init__(
            message="Invalid token",
            code="INVALID_TOKEN"
        )


class UserNotVerifiedException(AuthenticationException):
    """User email not verified."""

    def __init__(self):
        super().__init__(
            message="Please verify your email address",
            code="EMAIL_NOT_VERIFIED"
        )


class UserInactiveException(AuthenticationException):
    """User account is inactive."""

    def __init__(self):
        super().__init__(
            message="Your account has been deactivated",
            code="USER_INACTIVE"
        )


# ============== Authorization Exceptions ==============

class AuthorizationException(AIOSOLException):
    """Base authorization exception."""

    def __init__(
        self,
        message: str = "Access denied",
        code: str = "FORBIDDEN",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=code,
            status_code=403,
            details=details
        )


class PermissionDeniedException(AuthorizationException):
    """User doesn't have required permission."""

    def __init__(self, permission: str = None):
        message = "You don't have permission to perform this action"
        if permission:
            message = f"Missing permission: {permission}"
        super().__init__(message=message, code="PERMISSION_DENIED")


class TenantAccessDeniedException(AuthorizationException):
    """User trying to access another tenant's data."""

    def __init__(self):
        super().__init__(
            message="You cannot access this organization's data",
            code="TENANT_ACCESS_DENIED"
        )


# ============== Resource Exceptions ==============

class ResourceNotFoundException(AIOSOLException):
    """Resource not found."""

    def __init__(
        self,
        resource: str = "Resource",
        identifier: str = None
    ):
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with ID '{identifier}' not found"
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404
        )


class ResourceAlreadyExistsException(AIOSOLException):
    """Resource already exists."""

    def __init__(
        self,
        resource: str = "Resource",
        field: str = None,
        value: str = None
    ):
        message = f"{resource} already exists"
        if field and value:
            message = f"{resource} with {field} '{value}' already exists"
        super().__init__(
            message=message,
            code="ALREADY_EXISTS",
            status_code=409
        )


# ============== Validation Exceptions ==============

class ValidationException(AIOSOLException):
    """Validation error."""

    def __init__(
        self,
        message: str = "Validation error",
        errors: Dict[str, Any] = None
    ):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details={"errors": errors or {}}
        )


# ============== Rate Limiting Exceptions ==============

class RateLimitExceededException(AIOSOLException):
    """Rate limit exceeded."""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            message=f"Rate limit exceeded. Try again in {retry_after} seconds",
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details={"retry_after": retry_after}
        )


# ============== Billing Exceptions ==============

class BillingException(AIOSOLException):
    """Base billing exception."""

    def __init__(
        self,
        message: str = "Billing error",
        code: str = "BILLING_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=code,
            status_code=402,
            details=details
        )


class SubscriptionRequiredException(BillingException):
    """Active subscription required."""

    def __init__(self):
        super().__init__(
            message="An active subscription is required",
            code="SUBSCRIPTION_REQUIRED"
        )


class PlanLimitExceededException(BillingException):
    """Plan limit exceeded."""

    def __init__(self, limit_type: str = "usage"):
        super().__init__(
            message=f"You have exceeded your plan's {limit_type} limit. Please upgrade.",
            code="PLAN_LIMIT_EXCEEDED",
            details={"limit_type": limit_type}
        )


class PaymentFailedException(BillingException):
    """Payment failed."""

    def __init__(self, reason: str = None):
        message = "Payment failed"
        if reason:
            message = f"Payment failed: {reason}"
        super().__init__(message=message, code="PAYMENT_FAILED")


# ============== Facebook Exceptions ==============

class FacebookException(AIOSOLException):
    """Base Facebook API exception."""

    def __init__(
        self,
        message: str = "Facebook API error",
        code: str = "FACEBOOK_ERROR",
        fb_error_code: int = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if fb_error_code:
            details["fb_error_code"] = fb_error_code
        super().__init__(
            message=message,
            code=code,
            status_code=502,
            details=details
        )


class FacebookTokenExpiredException(FacebookException):
    """Facebook access token expired."""

    def __init__(self, page_name: str = None):
        message = "Facebook access token has expired"
        if page_name:
            message = f"Facebook access token for '{page_name}' has expired. Please reconnect."
        super().__init__(message=message, code="FB_TOKEN_EXPIRED")


class FacebookRateLimitException(FacebookException):
    """Facebook rate limit hit."""

    def __init__(self):
        super().__init__(
            message="Facebook API rate limit reached. Please try again later.",
            code="FB_RATE_LIMIT"
        )


# ============== AI Exceptions ==============

class AIException(AIOSOLException):
    """Base AI service exception."""

    def __init__(
        self,
        message: str = "AI service error",
        code: str = "AI_ERROR",
        provider: str = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if provider:
            details["provider"] = provider
        super().__init__(
            message=message,
            code=code,
            status_code=502,
            details=details
        )


class AIRateLimitException(AIException):
    """AI API rate limit hit."""

    def __init__(self, provider: str = "AI"):
        super().__init__(
            message=f"{provider} API rate limit reached. Please try again later.",
            code="AI_RATE_LIMIT",
            provider=provider
        )


class AIContentFilterException(AIException):
    """AI content was filtered."""

    def __init__(self):
        super().__init__(
            message="The AI response was filtered due to content policy",
            code="AI_CONTENT_FILTERED"
        )
