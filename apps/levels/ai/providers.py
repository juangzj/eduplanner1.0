from __future__ import annotations

import json
from typing import Any

from django.conf import settings
from openai import OpenAI

from .base import AIProvider
from .prompts import LevelPrompt, AssessmentPrompt


class OpenAIProvider(AIProvider):
    """OpenAI-backed implementation for level generation and assessment rubrics."""

    REQUIRED_KEYS = ("low_level", "basic_level", "high_level", "superior_level")
    ASSESSMENT_REQUIRED_KEYS = ("title", "rubric_description", "rubric_content")

    def __init__(self) -> None:
        api_key = getattr(settings, "OPENAI_API_KEY", "")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")
        self.client = OpenAI(api_key=api_key)
        self.model = getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")

    def generate_level_content(self, prompt_data: dict[str, Any]) -> dict[str, str]:
        prompt = LevelPrompt.build_prompt(prompt_data)

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

    def generate_assessment_content(self, prompt_data: dict[str, Any]) -> dict[str, str]:
        prompt = AssessmentPrompt.build_prompt(prompt_data)

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.4,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert educational pedagogue specialized in assessment rubric design. "
                        "You generate coherent assessment rubrics aligned with evidence and performance levels. "
                        "Return ONLY valid JSON with these keys: "
                        "title, rubric_description, rubric_content. "
                        "Write all content in Spanish. "
                        "rubric_content must be a markdown table with columns: "
                        "Criterio, Nivel Bajo, Nivel Básico, Nivel Alto, Nivel Superior."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )

        raw_content = response.choices[0].message.content or "{}"
        parsed = json.loads(raw_content)
        normalized = self._normalize_assessment_response(parsed)
        self._validate_assessment_response(normalized)
        return normalized

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

    def _normalize_assessment_response(self, payload: dict[str, Any]) -> dict[str, str]:
        alias_map = {
            "titulo": "title",
            "descripcion_rubrica": "rubric_description",
            "contenido_rubrica": "rubric_content",
        }

        normalized: dict[str, str] = {}

        for key, value in payload.items():
            normalized_key = alias_map.get(key, key)
            if normalized_key in self.ASSESSMENT_REQUIRED_KEYS:
                normalized[normalized_key] = str(value).strip()

        return normalized

    def _validate_assessment_response(self, payload: dict[str, str]) -> None:
        missing = [key for key in self.ASSESSMENT_REQUIRED_KEYS if not payload.get(key)]
        if missing:
            raise ValueError(f"AI response is missing required keys: {', '.join(missing)}")