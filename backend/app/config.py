"""
Application configuration using Pydantic Settings.
Created by: Sadia (Backend Lead)
"""
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # ============== Application ==============
    APP_NAME: str = "AIOSOL"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI-powered Facebook Comment Auto-Reply SaaS Platform"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production

    # ============== Server ==============
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    RELOAD: bool = True

    # ============== CORS ==============
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # ============== Database ==============
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/aiosol"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # ============== Redis ==============
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PREFIX: str = "aiosol:"

    # ============== JWT ==============
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ============== Password Hashing ==============
    PASSWORD_HASH_ROUNDS: int = 12

    # ============== Facebook ==============
    FACEBOOK_APP_ID: str = ""
    FACEBOOK_APP_SECRET: str = ""
    FACEBOOK_WEBHOOK_VERIFY_TOKEN: str = "aiosol_webhook_verify_token"
    FACEBOOK_API_VERSION: str = "v19.0"
    FACEBOOK_GRAPH_URL: str = "https://graph.facebook.com"

    # ============== OpenAI ==============
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_MAX_TOKENS: int = 500
    OPENAI_TEMPERATURE: float = 0.7

    # ============== Anthropic (Claude) ==============
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"
    ANTHROPIC_MAX_TOKENS: int = 500

    # ============== Razorpay ==============
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    RAZORPAY_WEBHOOK_SECRET: str = ""

    # ============== Stripe ==============
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # ============== Email (SendGrid/Resend) ==============
    EMAIL_PROVIDER: str = "resend"  # sendgrid, resend
    SENDGRID_API_KEY: str = ""
    RESEND_API_KEY: str = ""
    EMAIL_FROM_ADDRESS: str = "noreply@aiosol.com"
    EMAIL_FROM_NAME: str = "AIOSOL"

    # ============== Encryption ==============
    ENCRYPTION_KEY: str = "your-32-byte-encryption-key-here"

    # ============== Rate Limiting ==============
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000
    WEBHOOK_RATE_LIMIT_PER_MINUTE: int = 10000

    # ============== File Upload ==============
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_UPLOAD_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "gif", "pdf"]

    # ============== Celery ==============
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ============== Sentry (Error Monitoring) ==============
    SENTRY_DSN: str = ""
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1

    # ============== Frontend URL ==============
    FRONTEND_URL: str = "http://localhost:5173"

    # ============== Super Admin ==============
    SUPER_ADMIN_EMAIL: str = "admin@aiosol.com"
    SUPER_ADMIN_PASSWORD: str = "change-this-password"

    @property
    def async_database_url(self) -> str:
        """Get async database URL."""
        return self.DATABASE_URL

    @property
    def sync_database_url(self) -> str:
        """Get sync database URL for Alembic."""
        return self.DATABASE_URL.replace("+asyncpg", "")

    @property
    def facebook_graph_api_url(self) -> str:
        """Get full Facebook Graph API URL."""
        return f"{self.FACEBOOK_GRAPH_URL}/{self.FACEBOOK_API_VERSION}"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    """
    return Settings()


# Global settings instance
settings = get_settings()
