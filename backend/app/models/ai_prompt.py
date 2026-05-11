"""
AI Prompt and Reply Rule models.
Created by: Sadia (Backend Lead) + Tanvir (AI Engineer)
"""
from enum import Enum
from sqlalchemy import Column, String, Boolean, Integer, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from .base import Base, UUIDMixin, TimestampMixin, TenantMixin


class ToneType(str, Enum):
    """AI response tone options."""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    CASUAL = "casual"
    FORMAL = "formal"
    EMPATHETIC = "empathetic"
    HUMOROUS = "humorous"
    DIPLOMATIC = "diplomatic"


class RuleActionType(str, Enum):
    """Actions for reply rules."""
    AUTO_REPLY = "auto_reply"         # Use AI to reply
    TEMPLATE_REPLY = "template_reply" # Use fixed template
    SKIP = "skip"                     # Don't reply
    FLAG = "flag"                     # Flag for manual review
    ESCALATE = "escalate"             # Notify team


class AIPrompt(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """
    Custom AI prompts for generating replies.
    Each organization can have multiple prompts.
    """
    __tablename__ = 'ai_prompts'

    # Basic Info
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # System Prompt
    system_prompt = Column(Text, nullable=False)
    """
    Example system prompt:
    "You are a helpful customer service representative for {company_name}.
    Your responses should be:
    - Professional and courteous
    - In {language}
    - Under {max_words} words
    - Address the customer's concern directly

    Company context: {company_description}

    Never mention competitor products.
    Always end with a positive note or offer further assistance."
    """

    # Tone & Language
    tone = Column(
        SQLEnum(ToneType),
        default=ToneType.PROFESSIONAL,
        nullable=False
    )
    language = Column(String(10), default='bn', nullable=False)  # bn, en, hi

    # Constraints
    max_words = Column(Integer, default=100, nullable=False)
    include_greeting = Column(Boolean, default=True, nullable=False)
    include_signature = Column(Boolean, default=False, nullable=False)
    signature_text = Column(String(255), nullable=True)

    # Variables (placeholders in prompt)
    variables = Column(JSONB, default=dict, nullable=True)
    """
    Example variables:
    {
        "company_name": "AIOSOL",
        "company_description": "AI-powered automation platform",
        "support_email": "support@aiosol.com",
        "support_phone": "+91-123-456-7890"
    }
    """

    # Status
    is_default = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Usage Stats
    times_used = Column(Integer, default=0, nullable=False)
    avg_satisfaction = Column(Integer, nullable=True)  # 1-5 rating

    # Relationships
    organization = relationship("Organization", back_populates="ai_prompts")

    def __repr__(self):
        return f"<AIPrompt(id={self.id}, name='{self.name}', tone='{self.tone}')>"

    def render_prompt(self, extra_vars: dict = None) -> str:
        """Render the system prompt with variables."""
        prompt = self.system_prompt
        all_vars = {**(self.variables or {}), **(extra_vars or {})}

        for key, value in all_vars.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))

        return prompt


class ReplyRule(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """
    Rules for handling different types of comments.
    """
    __tablename__ = 'reply_rules'

    # Page Reference (optional - if None, applies to all pages)
    page_id = Column(
        UUID(as_uuid=True),
        ForeignKey('facebook_pages.id', ondelete='CASCADE'),
        nullable=True,
        index=True
    )

    # Basic Info
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Matching Criteria
    rule_type = Column(String(50), nullable=False)  # keyword, sentiment, intent, regex

    # Keywords to match
    keywords = Column(ARRAY(String), default=list, nullable=True)
    """Example: ["price", "cost", "expensive", "cheap"]"""

    # Sentiment to match (if rule_type is 'sentiment')
    match_sentiment = Column(String(20), nullable=True)  # positive, negative, neutral

    # Intent to match (if rule_type is 'intent')
    match_intent = Column(String(50), nullable=True)  # question, complaint, praise, etc.

    # Regex pattern (if rule_type is 'regex')
    regex_pattern = Column(String(500), nullable=True)

    # Action
    action = Column(
        SQLEnum(RuleActionType),
        default=RuleActionType.AUTO_REPLY,
        nullable=False
    )

    # Template (for template_reply action)
    reply_template = Column(Text, nullable=True)
    """
    Example template:
    "Hi {commenter_name}! Thanks for your interest.
    Our prices start from ₹499. Visit our website for more details.
    - {company_name} Team"
    """

    # AI Prompt to use (for auto_reply action)
    prompt_id = Column(
        UUID(as_uuid=True),
        ForeignKey('ai_prompts.id', ondelete='SET NULL'),
        nullable=True
    )

    # Escalation (for escalate action)
    escalate_to_email = Column(String(255), nullable=True)
    escalate_to_webhook = Column(String(500), nullable=True)

    # Priority (higher = checked first)
    priority = Column(Integer, default=0, nullable=False)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Stats
    times_matched = Column(Integer, default=0, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="reply_rules")
    page = relationship("FacebookPage", back_populates="reply_rules")
    prompt = relationship("AIPrompt")

    def __repr__(self):
        return f"<ReplyRule(id={self.id}, name='{self.name}', action='{self.action}')>"

    def matches(self, comment_text: str, sentiment: str = None, intent: str = None) -> bool:
        """Check if this rule matches a comment."""
        comment_lower = comment_text.lower()

        if self.rule_type == 'keyword' and self.keywords:
            return any(kw.lower() in comment_lower for kw in self.keywords)

        elif self.rule_type == 'sentiment' and self.match_sentiment:
            return sentiment == self.match_sentiment

        elif self.rule_type == 'intent' and self.match_intent:
            return intent == self.match_intent

        elif self.rule_type == 'regex' and self.regex_pattern:
            import re
            try:
                return bool(re.search(self.regex_pattern, comment_text, re.IGNORECASE))
            except:
                return False

        return False
