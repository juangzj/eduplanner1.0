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


def _coerce_rubric_payload(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value

    if value is None:
        return {}

    raw = str(value).strip()
    if not raw:
        return {}

    parsed: Any = None
    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        try:
            parsed = ast.literal_eval(raw)
        except (ValueError, SyntaxError):
            parsed = None

    if isinstance(parsed, dict):
        return parsed

    return {}


def _is_markdown_separator_row(cells: list[str]) -> bool:
    if not cells:
        return False

    for cell in cells:
        token = cell.replace("-", "").replace(":", "").replace(" ", "")
        if token:
            return False
    return True


def _parse_markdown_rubric_rows(value: Any) -> list[dict[str, str]]:
    if value is None:
        return []

    raw = str(value).strip()
    if not raw or "|" not in raw:
        return []

    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    table_lines = [line for line in lines if "|" in line]
    if len(table_lines) < 3:
        return []

    def parse_row(line: str) -> list[str]:
        cleaned = line.strip().strip("|")
        return [cell.strip() for cell in cleaned.split("|")]

    header_cells = parse_row(table_lines[0])
    header_text = " ".join(header_cells).lower()
    if "criterio" not in header_text or "nivel" not in header_text:
        return []

    rows: list[dict[str, str]] = []

    for line in table_lines[1:]:
        cells = parse_row(line)
        if len(cells) < 5:
            continue
        if _is_markdown_separator_row(cells):
            continue

        rows.append(
            {
                "criterion": cells[0],
                "low": cells[1],
                "basic": cells[2],
                "high": cells[3],
                "superior": cells[4],
            }
        )

    return rows


def _normalize_rubric_rows(payload: dict[str, Any]) -> list[dict[str, str]]:
    criteria = payload.get("Criterios") or payload.get("criterios") or []
    if not isinstance(criteria, list):
        return []

    rows: list[dict[str, str]] = []

    for item in criteria:
        if not isinstance(item, dict):
            continue

        criterion = str(item.get("Criterio") or item.get("criterio") or "").strip()
        levels = item.get("Niveles") or item.get("niveles") or {}
        if not isinstance(levels, dict):
            levels = {}

        rows.append(
            {
                "criterion": criterion,
                "low": str(levels.get("Bajo") or levels.get("bajo") or "").strip(),
                "basic": str(levels.get("Básico") or levels.get("Basico") or levels.get("basico") or "").strip(),
                "high": str(levels.get("Alto") or levels.get("alto") or "").strip(),
                "superior": str(levels.get("Superior") or levels.get("superior") or "").strip(),
            }
        )

    return rows


@register.filter
def level_title(value: Any) -> str:
    return _coerce_level_payload(value)["level_title"]


@register.filter
def level_description(value: Any) -> str:
    return _coerce_level_payload(value)["level_description"]


@register.filter
def rubric_rows(value: Any) -> list[dict[str, str]]:
    payload = _coerce_rubric_payload(value)
    if payload:
        return _normalize_rubric_rows(payload)

    return _parse_markdown_rubric_rows(value)
