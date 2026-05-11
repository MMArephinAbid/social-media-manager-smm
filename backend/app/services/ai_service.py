"""
AI Service for generating intelligent replies.
Created by: Tanvir (AI Engineer)

Supports:
- OpenAI GPT-4
- Anthropic Claude
"""
import time
from typing import Optional, Dict, Any, Tuple
from enum import Enum
import httpx

from ..config import settings
from ..core.exceptions import AIException, AIRateLimitException, AIContentFilterException


class AIProvider(str, Enum):
    """Supported AI providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class AIService:
    """Service for AI-powered reply generation."""

    def __init__(self):
        self.openai_api_key = settings.OPENAI_API_KEY
        self.anthropic_api_key = settings.ANTHROPIC_API_KEY
        self.default_provider = AIProvider.OPENAI

    async def generate_reply(
        self,
        comment_text: str,
        system_prompt: str,
        provider: AIProvider = None,
        model: str = None,
        max_tokens: int = None,
        temperature: float = 0.7,
        context: Dict[str, Any] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate an AI reply to a comment.

        Args:
            comment_text: The comment to reply to
            system_prompt: System prompt for the AI
            provider: AI provider to use (openai, anthropic)
            model: Specific model to use
            max_tokens: Maximum tokens in response
            temperature: Creativity parameter (0-1)
            context: Additional context (post content, previous comments, etc.)

        Returns:
            Tuple of (reply_text, metadata)
            metadata includes: tokens_used, model, processing_time_ms, cost
        """
        provider = provider or self.default_provider
        start_time = time.time()

        if provider == AIProvider.OPENAI:
            reply, metadata = await self._generate_openai(
                comment_text=comment_text,
                system_prompt=system_prompt,
                model=model or settings.OPENAI_MODEL,
                max_tokens=max_tokens or settings.OPENAI_MAX_TOKENS,
                temperature=temperature,
                context=context,
            )
        elif provider == AIProvider.ANTHROPIC:
            reply, metadata = await self._generate_anthropic(
                comment_text=comment_text,
                system_prompt=system_prompt,
                model=model or settings.ANTHROPIC_MODEL,
                max_tokens=max_tokens or settings.ANTHROPIC_MAX_TOKENS,
                temperature=temperature,
                context=context,
            )
        else:
            raise AIException(f"Unsupported AI provider: {provider}")

        # Add processing time
        metadata["processing_time_ms"] = int((time.time() - start_time) * 1000)

        return reply, metadata

    async def _generate_openai(
        self,
        comment_text: str,
        system_prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        context: Dict[str, Any] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate reply using OpenAI API."""

        # Build messages
        messages = [
            {"role": "system", "content": system_prompt}
        ]

        # Add context if provided
        if context:
            if context.get("post_content"):
                messages.append({
                    "role": "user",
                    "content": f"[Post Content]: {context['post_content']}"
                })
            if context.get("previous_comments"):
                messages.append({
                    "role": "user",
                    "content": f"[Previous Comments]: {context['previous_comments']}"
                })

        # Add the comment
        messages.append({
            "role": "user",
            "content": f"Please reply to this comment: \"{comment_text}\""
        })

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
                timeout=60.0
            )

            data = response.json()

            if response.status_code == 429:
                raise AIRateLimitException(provider="OpenAI")

            if response.status_code != 200:
                error_msg = data.get("error", {}).get("message", "Unknown error")
                raise AIException(
                    message=f"OpenAI API error: {error_msg}",
                    provider="openai",
                    details=data
                )

            # Check for content filter
            choice = data["choices"][0]
            if choice.get("finish_reason") == "content_filter":
                raise AIContentFilterException()

            reply = choice["message"]["content"].strip()
            usage = data.get("usage", {})

            # Calculate cost (approximate)
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = prompt_tokens + completion_tokens

            # GPT-4 pricing (approximate)
            cost = (prompt_tokens * 0.00003) + (completion_tokens * 0.00006)

            return reply, {
                "provider": "openai",
                "model": model,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "cost": cost,
            }

    async def _generate_anthropic(
        self,
        comment_text: str,
        system_prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        context: Dict[str, Any] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate reply using Anthropic Claude API."""

        # Build user message
        user_content = ""
        if context:
            if context.get("post_content"):
                user_content += f"[Post Content]: {context['post_content']}\n\n"
            if context.get("previous_comments"):
                user_content += f"[Previous Comments]: {context['previous_comments']}\n\n"

        user_content += f"Please reply to this comment: \"{comment_text}\""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "max_tokens": max_tokens,
                    "system": system_prompt,
                    "messages": [
                        {"role": "user", "content": user_content}
                    ],
                },
                timeout=60.0
            )

            data = response.json()

            if response.status_code == 429:
                raise AIRateLimitException(provider="Anthropic")

            if response.status_code != 200:
                error_msg = data.get("error", {}).get("message", "Unknown error")
                raise AIException(
                    message=f"Anthropic API error: {error_msg}",
                    provider="anthropic",
                    details=data
                )

            # Extract reply
            content = data.get("content", [])
            reply = ""
            for block in content:
                if block.get("type") == "text":
                    reply = block.get("text", "").strip()
                    break

            usage = data.get("usage", {})
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
            total_tokens = input_tokens + output_tokens

            # Claude pricing (approximate)
            cost = (input_tokens * 0.000003) + (output_tokens * 0.000015)

            return reply, {
                "provider": "anthropic",
                "model": model,
                "prompt_tokens": input_tokens,
                "completion_tokens": output_tokens,
                "total_tokens": total_tokens,
                "cost": cost,
            }

    async def analyze_sentiment(
        self,
        text: str,
        provider: AIProvider = None,
    ) -> Dict[str, Any]:
        """
        Analyze sentiment of a text.

        Args:
            text: Text to analyze
            provider: AI provider to use

        Returns:
            Dict with sentiment (positive/negative/neutral), confidence, intent
        """
        provider = provider or self.default_provider

        system_prompt = """You are a sentiment analyzer. Analyze the given text and respond with ONLY a JSON object in this exact format:
{
    "sentiment": "positive" or "negative" or "neutral",
    "confidence": 0.0 to 1.0,
    "intent": "question" or "complaint" or "praise" or "suggestion" or "general",
    "language": "en" or "bn" or "hi" etc
}

Do not include any other text, just the JSON object."""

        try:
            reply, _ = await self.generate_reply(
                comment_text=text,
                system_prompt=system_prompt,
                provider=provider,
                max_tokens=100,
                temperature=0.3,
            )

            # Parse JSON response
            import json
            # Clean up the response
            reply = reply.strip()
            if reply.startswith("```"):
                reply = reply.split("```")[1]
                if reply.startswith("json"):
                    reply = reply[4:]

            return json.loads(reply)

        except Exception as e:
            # Return default on failure
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "intent": "general",
                "language": "en",
            }

    def build_default_prompt(
        self,
        company_name: str = "AIOSOL",
        tone: str = "professional",
        language: str = "bn",
        max_words: int = 100,
        include_greeting: bool = True,
    ) -> str:
        """Build a default system prompt for reply generation."""

        tone_instructions = {
            "professional": "Be professional, courteous, and helpful.",
            "friendly": "Be warm, friendly, and approachable.",
            "casual": "Be casual and conversational.",
            "formal": "Be formal and respectful.",
            "empathetic": "Show empathy and understanding.",
            "diplomatic": "Be diplomatic and balanced in your response.",
        }

        language_names = {
            "bn": "Bengali",
            "en": "English",
            "hi": "Hindi",
        }

        prompt = f"""You are a customer service representative for {company_name}.

Your task is to reply to Facebook comments on behalf of the company.

Guidelines:
- {tone_instructions.get(tone, tone_instructions['professional'])}
- Respond in {language_names.get(language, 'Bengali')} language.
- Keep your response under {max_words} words.
- Address the customer's concern or question directly.
- {"Start with a greeting." if include_greeting else "Do not include a greeting."}
- Never mention competitor products.
- If you don't know something, offer to help find the information.
- Be genuine and avoid generic responses.
- Do not use excessive emojis or exclamation marks.

Remember: You are representing the company, so maintain the brand voice."""

        return prompt


# Singleton instance
ai_service = AIService()
