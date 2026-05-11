"""
API v1 Router - combines all route modules.
Created by: Sadia (Backend Lead)
"""
from fastapi import APIRouter

from .auth import router as auth_router
from .pages import router as pages_router
from .comments import router as comments_router
from .billing import router as billing_router
from .webhooks import router as webhooks_router
from .settings import router as settings_router
from .analytics import router as analytics_router
from .users import router as users_router


# Create main v1 router
api_router = APIRouter(prefix="/api/v1")

# Include all routers
api_router.include_router(auth_router)
api_router.include_router(pages_router)
api_router.include_router(comments_router)
api_router.include_router(billing_router)
api_router.include_router(webhooks_router)
api_router.include_router(settings_router)
api_router.include_router(analytics_router)
api_router.include_router(users_router)


# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "aiosol-api"
    }


# API Info endpoint
@api_router.get("/info")
async def api_info():
    """API information endpoint."""
    return {
        "name": "AIOSOL API",
        "version": "1.0.0",
        "description": "AI-Powered Facebook Comment Auto-Reply Platform",
        "endpoints": {
            "auth": "/api/v1/auth/*",
            "pages": "/api/v1/pages/*",
            "comments": "/api/v1/comments/*",
            "billing": "/api/v1/billing/*",
            "webhooks": "/api/v1/webhooks/*",
            "settings": "/api/v1/settings/*",
            "analytics": "/api/v1/analytics/*",
            "users": "/api/v1/users/*",
        },
        "docs": "/docs",
        "redoc": "/redoc",
    }
