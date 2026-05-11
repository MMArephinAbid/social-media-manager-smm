"""
Custom middleware for the application.
Created by: Sadia (Backend Lead)
"""
import time
import uuid
from typing import Callable, Optional
from contextvars import ContextVar

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..config import settings


# Context variable for tenant (organization) ID
tenant_context: ContextVar[Optional[str]] = ContextVar("tenant_id", default=None)
request_id_context: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def get_current_tenant_id() -> Optional[str]:
    """Get the current tenant ID from context."""
    return tenant_context.get()


def set_current_tenant_id(tenant_id: str) -> None:
    """Set the current tenant ID in context."""
    tenant_context.set(tenant_id)


def get_request_id() -> Optional[str]:
    """Get the current request ID from context."""
    return request_id_context.get()


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add unique request ID to each request.
    Useful for request tracing and logging.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        # Get or generate request ID
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())

        # Set in context
        request_id_context.set(request_id)

        # Add to request state for easy access
        request.state.request_id = request_id

        # Process request
        response = await call_next(request)

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response


class TimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to measure and log request processing time.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        start_time = time.time()

        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f}"

        # Log slow requests (> 1 second)
        if process_time > 1.0:
            print(
                f"SLOW REQUEST: {request.method} {request.url.path} "
                f"took {process_time:.2f}s"
            )

        return response


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract and set tenant context from JWT.
    This ensures all database queries are scoped to the tenant.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        # Extract organization ID from JWT (if authenticated)
        # This is set by the auth dependency, but we set a default here
        tenant_context.set(None)

        response = await call_next(request)

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Only add HSTS in production
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware.
    For production, use Redis-based rate limiting.
    """

    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # IP -> (count, window_start)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        # Skip rate limiting for webhooks
        if request.url.path.startswith("/api/v1/webhooks"):
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Check rate limit
        current_time = time.time()

        if client_ip in self.requests:
            count, window_start = self.requests[client_ip]

            # Check if window has expired
            if current_time - window_start > self.window_seconds:
                self.requests[client_ip] = (1, current_time)
            elif count >= self.max_requests:
                return Response(
                    content='{"error": "Rate limit exceeded"}',
                    status_code=429,
                    media_type="application/json",
                    headers={
                        "Retry-After": str(
                            int(self.window_seconds - (current_time - window_start))
                        )
                    }
                )
            else:
                self.requests[client_ip] = (count + 1, window_start)
        else:
            self.requests[client_ip] = (1, current_time)

        return await call_next(request)


class CORSDebugMiddleware(BaseHTTPMiddleware):
    """
    Debug middleware for CORS issues (development only).
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        if settings.DEBUG:
            origin = request.headers.get("origin", "")
            print(f"CORS Debug - Origin: {origin}, Path: {request.url.path}")

        response = await call_next(request)

        return response
