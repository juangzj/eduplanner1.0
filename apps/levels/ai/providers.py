from __future__ import annotations

import json
from typing import Any

from django.conf import settings
from openai import OpenAI

from .base import AIProvider


class OpenAIProvider(AIProvider):
    """OpenAI-backed implementation for level generation."""

    REQUIRED_KEYS = ("low_level", "basic_level", "high_level", "superior_level")

    def __init__(self) -> None:
        api_key = getattr(settings, "OPENAI_API_KEY", "")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")
        self.client = OpenAI(api_key=api_key)
        self.model = getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")

    def generate_level_content(self, prompt_data: dict[str, Any]) -> dict[str, str]:
        prompt = self._build_prompt(prompt_data)

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.4,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an educational assistant. Return ONLY valid JSON with "
                        "these keys: low_level, basic_level, high_level, superior_level."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )

        raw_content = response.choices[0].message.content or "{}"
        parsed = json.loads(raw_content)
        normalized = self._normalize_response(parsed)
        self._validate_response(normalized)
        return normalized

    def _build_prompt(self, prompt_data: dict[str, Any]) -> str:
        return (
            "Generate 4 performance levels in Spanish for a school rubric. "
            "Use clear and progressive language. Context:\n"
            f"- area: {prompt_data.get('area', '')}\n"
            f"- subject: {prompt_data.get('subject', '')}\n"
            f"- grade: {prompt_data.get('grade', '')}\n"
            f"- academic_period: {prompt_data.get('academic_period', '')}\n"
            f"- competency: {prompt_data.get('competency', '')}\n"
            f"- statement: {prompt_data.get('statement', '')}\n"
            f"- learning_evidence: {prompt_data.get('learning_evidence', '')}\n"
            f"- level_title: {prompt_data.get('level_title', '')}\n"
            f"- level_description: {prompt_data.get('level_description', '')}\n"
            "Output JSON only, no markdown, no extra keys."
        )

    def _normalize_response(self, payload: dict[str, Any]) -> dict[str, str]:
        alias_map = {
            "nivel_bajo": "low_level",
            "nivel_basico": "basic_level",
            "nivel_alto": "high_level",
            "nivel_superior": "superior_level",
        }
        normalized: dict[str, str] = {}

        for key, value in payload.items():
            normalized_key = alias_map.get(key, key)
            if normalized_key in self.REQUIRED_KEYS:
                normalized[normalized_key] = str(value).strip()

        return normalized

    def _validate_response(self, payload: dict[str, str]) -> None:
        missing = [key for key in self.REQUIRED_KEYS if not payload.get(key)]
        if missing:
            raise ValueError(f"AI response is missing required keys: {', '.join(missing)}")

