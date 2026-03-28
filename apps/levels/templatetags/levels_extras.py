from __future__ import annotations

import ast
import json
from typing import Any

from django import template

register = template.Library()


def _coerce_level_payload(value: Any) -> dict[str, str]:
    if isinstance(value, dict):
        title = str(value.get("level_title") or value.get("title") or "").strip()
        description = str(
            value.get("level_description")
            or value.get("description")
            or value.get("content")
            or ""
        ).strip()
        return {"level_title": title, "level_description": description}

    if value is None:
        return {"level_title": "", "level_description": ""}

    raw = str(value).strip()
    if not raw:
        return {"level_title": "", "level_description": ""}

    parsed: Any = None
    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        try:
            parsed = ast.literal_eval(raw)
        except (ValueError, SyntaxError):
            parsed = None

    if isinstance(parsed, dict):
        return _coerce_level_payload(parsed)

    return {"level_title": "", "level_description": raw}


@register.filter
def level_title(value: Any) -> str:
    return _coerce_level_payload(value)["level_title"]


@register.filter
def level_description(value: Any) -> str:
    return _coerce_level_payload(value)["level_description"]
