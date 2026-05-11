"""
API v1 Router - combines all route modules.
Created by: Sadia (Backend Lead)
"""
from fastapi import APIRouter

from .auth import router as auth_router
# These will be imported as we create them
# from .organizations import router as organizations_router
# from .pages import router as pages_router
# from .comments import router as comments_router
# from .prompts import router as prompts_router
# from .rules import router as rules_router
# from .billing import router as billing_router
# from .webhooks import router as webhooks_router
# from .admin import router as admin_router


# Create main v1 router
api_router = APIRouter(prefix="/api/v1")

# Include all routers
api_router.include_router(auth_router)
# api_router.include_router(organizations_router)
# api_router.include_router(pages_router)
# api_router.include_router(comments_router)
# api_router.include_router(prompts_router)
# api_router.include_router(rules_router)
# api_router.include_router(billing_router)
# api_router.include_router(webhooks_router)
# api_router.include_router(admin_router)


# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "aiosol-api"
    }
