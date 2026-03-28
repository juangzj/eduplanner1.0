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
                        "You are an expert educational pedagogue specialized in competency-based assessment "
                        "and Bloom's Taxonomy. You generate academic rubric performance levels. "
                        "Return ONLY valid JSON with these keys: "
                        "low_level, basic_level, high_level, superior_level."
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
        return f"""
    You are an expert educational pedagogue specialized in competency-based assessment and Bloom's Taxonomy.

    Your task is to generate performance levels for a school rubric used in academic evaluation.

    The rubric must follow these rules:

    1. The four levels must be clearly progressive and based on Bloom's Taxonomy:

    Low Level → Recognizes but presents difficulties
    Basic Level → Identifies and describes
    High Level → Analyzes and applies correctly
    Superior Level → Evaluates, justifies or proposes connections

    2. The levels MUST be aligned directly with the learning evidence.
    Do NOT generate generic levels.
    Each level must describe what the student does specifically in relation to the evidence.

    3. The descriptions must:
    - Be written in Spanish
    - Be concise (1–2 sentences per level)
    - Describe observable student performance
    - Use clear academic language
    - Avoid repeating the same structure in all levels
    - Show clear progression from weak performance to excellent performance

    4. The Low Level must describe difficulties related to the evidence (not only recognition of concepts).

    5. The Superior Level must improve the quality of the work (analysis, justification, connections, evaluation, or deeper understanding), not just repeat the same action.

    Context:

    Area: {prompt_data.get('area', '')}
    Subject: {prompt_data.get('subject', '')}
    Grade: {prompt_data.get('grade', '')}
    Academic Period: {prompt_data.get('academic_period', '')}
    Competency: {prompt_data.get('competency', '')}
    Learning Statement: {prompt_data.get('statement', '')}
    Learning Evidence: {prompt_data.get('learning_evidence', '')}
    Level Title: {prompt_data.get('level_title', '')}
    Level Description: {prompt_data.get('level_description', '')}

    Generate the four performance levels in Spanish with strong pedagogical coherence.

    Return ONLY a valid JSON object with these keys:

    low_level
    basic_level
    high_level
    superior_level

    Do not include explanations.
    Do not include markdown.
    Do not include extra keys.
    """

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