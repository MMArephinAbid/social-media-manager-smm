"""
FastAPI Application Entry Point.
Created by: Sadia (Backend Lead)

AIOSOL - AI-powered Facebook Comment Auto-Reply SaaS Platform
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from .config import settings
from .api import api_router
from .core.middleware import (
    RequestIDMiddleware,
    TimingMiddleware,
    TenantMiddleware,
    SecurityHeadersMiddleware,
)
from .core.exceptions import AIOSOLException


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Runs on startup and shutdown.
    """
    # Startup
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📍 Environment: {settings.ENVIRONMENT}")
    print(f"🔧 Debug mode: {settings.DEBUG}")

    # TODO: Initialize database connection pool
    # TODO: Initialize Redis connection
    # TODO: Start Celery workers

    yield

    # Shutdown
    print(f"👋 Shutting down {settings.APP_NAME}")
    # TODO: Close database connections
    # TODO: Close Redis connections


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)


# ============== Middleware ==============

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Custom middleware (order matters - last added runs first)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(TenantMiddleware)
app.add_middleware(TimingMiddleware)
app.add_middleware(RequestIDMiddleware)


# ============== Exception Handlers ==============

@app.exception_handler(AIOSOLException)
async def aiosol_exception_handler(request: Request, exc: AIOSOLException):
    """Handle custom AIOSOL exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {"errors": errors},
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    # Log the error
    print(f"Unexpected error: {exc}")

    # In production, don't expose error details
    if settings.ENVIRONMENT == "production":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                }
            }
        )

    # In development, show error details
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(exc),
                "type": type(exc).__name__,
            }
        }
    )


# ============== Include Routers ==============

app.include_router(api_router)


# ============== Root Endpoint ==============

@app.get("/")
async def root():
    """Root endpoint - API info."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "docs": "/docs" if settings.DEBUG else "Disabled in production",
        "health": "/api/v1/health",
    }


# ============== Run with Uvicorn ==============

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        workers=1 if settings.RELOAD else settings.WORKERS,
    )
