from __future__ import annotations

from django.conf import settings

from .base import AIProvider
from .providers import OpenAIProvider


def get_ai_client() -> AIProvider:
    provider = getattr(settings, "AI_PROVIDER", "openai").lower().strip()

    if provider == "openai":
        return OpenAIProvider()

    raise ValueError(f"Unsupported AI provider configured: {provider}")

