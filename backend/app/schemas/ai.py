"""
AI and reply rule schemas.
Created by: Sadia (Backend Lead) + Tanvir (AI Engineer)
"""
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field


class AIPromptCreate(BaseModel):
    """Request to create AI prompt."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    system_prompt: str = Field(..., min_length=10, max_length=5000)
    tone: str = "professional"
    language: str = "bn"
    max_words: int = Field(100, ge=10, le=500)
    include_greeting: bool = True
    include_signature: bool = False
    signature_text: Optional[str] = None
    variables: Optional[Dict[str, str]] = None
    is_default: bool = False


class AIPromptUpdate(BaseModel):
    """Request to update AI prompt."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    system_prompt: Optional[str] = Field(None, min_length=10, max_length=5000)
    tone: Optional[str] = None
    language: Optional[str] = None
    max_words: Optional[int] = Field(None, ge=10, le=500)
    include_greeting: Optional[bool] = None
    include_signature: Optional[bool] = None
    signature_text: Optional[str] = None
    variables: Optional[Dict[str, str]] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class AIPromptResponse(BaseModel):
    """Response schema for AI prompt."""

    id: UUID
    name: str
    description: Optional[str] = None
    system_prompt: str
    tone: str
    language: str
    max_words: int
    include_greeting: bool
    include_signature: bool
    signature_text: Optional[str] = None
    variables: Dict[str, str]
    is_default: bool
    is_active: bool
    times_used: int
    avg_satisfaction: Optional[int] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class AIPromptListResponse(BaseModel):
    """Response for listing AI prompts."""

    items: List[AIPromptResponse]
    total: int


class TestPromptRequest(BaseModel):
    """Request to test an AI prompt."""

    system_prompt: str = Field(..., min_length=10)
    sample_comment: str = Field(..., min_length=1)
    tone: str = "professional"
    language: str = "bn"
    max_words: int = 100
    variables: Optional[Dict[str, str]] = None


class TestPromptResponse(BaseModel):
    """Response for prompt test."""

    generated_reply: str
    tokens_used: int
    model_used: str
    processing_time_ms: int


# ============== Reply Rule Schemas ==============

class ReplyRuleCreate(BaseModel):
    """Request to create reply rule."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    page_id: Optional[UUID] = None  # None = all pages
    rule_type: str = Field(..., pattern="^(keyword|sentiment|intent|regex)$")
    keywords: Optional[List[str]] = None
    match_sentiment: Optional[str] = None
    match_intent: Optional[str] = None
    regex_pattern: Optional[str] = None
    action: str = Field(..., pattern="^(auto_reply|template_reply|skip|flag|escalate)$")
    reply_template: Optional[str] = None
    prompt_id: Optional[UUID] = None
    escalate_to_email: Optional[str] = None
    escalate_to_webhook: Optional[str] = None
    priority: int = 0
    is_active: bool = True


class ReplyRuleUpdate(BaseModel):
    """Request to update reply rule."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    page_id: Optional[UUID] = None
    rule_type: Optional[str] = None
    keywords: Optional[List[str]] = None
    match_sentiment: Optional[str] = None
    match_intent: Optional[str] = None
    regex_pattern: Optional[str] = None
    action: Optional[str] = None
    reply_template: Optional[str] = None
    prompt_id: Optional[UUID] = None
    escalate_to_email: Optional[str] = None
    escalate_to_webhook: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None


class ReplyRuleResponse(BaseModel):
    """Response schema for reply rule."""

    id: UUID
    name: str
    description: Optional[str] = None
    page_id: Optional[UUID] = None
    rule_type: str
    keywords: Optional[List[str]] = None
    match_sentiment: Optional[str] = None
    match_intent: Optional[str] = None
    regex_pattern: Optional[str] = None
    action: str
    reply_template: Optional[str] = None
    prompt_id: Optional[UUID] = None
    escalate_to_email: Optional[str] = None
    escalate_to_webhook: Optional[str] = None
    priority: int
    is_active: bool
    times_matched: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ReplyRuleListResponse(BaseModel):
    """Response for listing reply rules."""

    items: List[ReplyRuleResponse]
    total: int


class TestRuleRequest(BaseModel):
    """Request to test a rule against sample text."""

    rule_type: str
    keywords: Optional[List[str]] = None
    match_sentiment: Optional[str] = None
    match_intent: Optional[str] = None
    regex_pattern: Optional[str] = None
    sample_comment: str


class TestRuleResponse(BaseModel):
    """Response for rule test."""

    matches: bool
    matched_keywords: Optional[List[str]] = None
    detected_sentiment: Optional[str] = None
    detected_intent: Optional[str] = None
