"""
Organization schemas for request/response validation.
Created by: Sadia (Backend Lead)
"""
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import re


class OrganizationSettings(BaseModel):
    """Schema for organization settings."""

    timezone: str = "Asia/Kolkata"
    language: str = "bn"
    currency: str = "INR"
    reply_delay_min: int = 30
    reply_delay_max: int = 120
    working_hours: Optional[Dict[str, Any]] = None
    auto_reply_enabled: bool = True
    notification_email: Optional[str] = None
    ai_provider: str = "openai"
    default_tone: str = "professional"


class OrganizationCreate(BaseModel):
    """Request schema for creating organization."""

    name: str = Field(..., min_length=2, max_length=255)
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "India"
    postal_code: Optional[str] = None
    settings: Optional[OrganizationSettings] = None

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip()


class OrganizationUpdate(BaseModel):
    """Request schema for updating organization."""

    name: Optional[str] = Field(None, min_length=2, max_length=255)
    logo_url: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class OrganizationResponse(BaseModel):
    """Response schema for organization."""

    id: UUID
    name: str
    slug: str
    logo_url: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str
    postal_code: Optional[str] = None
    settings: Dict[str, Any]
    is_active: bool
    is_verified: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class OrganizationWithStats(OrganizationResponse):
    """Organization with usage statistics."""

    users_count: int = 0
    pages_count: int = 0
    replies_this_month: int = 0
    subscription_status: Optional[str] = None
    plan_name: Optional[str] = None


class OrganizationListResponse(BaseModel):
    """Response for listing organizations."""

    items: List[OrganizationResponse]
    total: int
    page: int
    per_page: int
    pages: int
