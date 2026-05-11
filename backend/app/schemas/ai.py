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
    prompt_type: str = "comment_reply"  # comment_reply, greeting, complaint, etc.
    system_prompt: str = Field(..., min_length=10, max_length=5000)
    user_prompt_template: Optional[str] = None
    tone: str = "professional"
    language: str = "bn"
    max_length: int = Field(500, ge=50, le=2000)
    temperature: float = Field(0.7, ge=0, le=2)
    is_active: bool = True


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

    prompts: List[AIPromptResponse]
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
    condition_type: str = "keyword"  # keyword, sentiment, intent, regex, all
    condition_value: Optional[str] = None  # keywords, patterns, etc.
    condition_operator: str = "contains"  # contains, equals, matches, greater_than
    action_type: str = "auto_reply"  # auto_reply, skip, flag, escalate, template
    action_value: Optional[str] = None  # template text, webhook URL, etc.
    priority: int = 0
    is_active: bool = True


class ReplyRuleUpdate(BaseModel):
    """Request to update reply rule."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    condition_type: Optional[str] = None
    condition_value: Optional[str] = None
    condition_operator: Optional[str] = None
    action_type: Optional[str] = None
    action_value: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None


class ReplyRuleResponse(BaseModel):
    """Response schema for reply rule."""

    id: UUID
    name: str
    description: Optional[str] = None
    condition_type: str
    condition_value: Optional[str] = None
    condition_operator: str
    action_type: str
    action_value: Optional[str] = None
    priority: int
    is_active: bool
    times_matched: int = 0
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class ReplyRuleListResponse(BaseModel):
    """Response for listing reply rules."""

    rules: List[ReplyRuleResponse]
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
