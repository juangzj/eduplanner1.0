import json
import re

from django.conf import settings


FIELD_KEYS = ("purpose", "role", "context", "task", "process", "format", "constraints")

PROMPT_CANVAS_RUBRIC = {
    "version": "1.0",
    "name": "Prompt Canvas Evaluation Rubric",
    "max_score": 100,
    "dimensions": [
        {
            "id": "persona_rol",
            "name": "Persona / Rol",
            "weight": 10,
            "criteria": [
                {"level": 0, "description": "No define rol o persona"},
                {"level": 1, "description": "Define un rol basico sin detalle"},
                {"level": 2, "description": "Rol claro pero sin alineacion pedagogica"},
                {"level": 3, "description": "Rol claro, especifico y alineado al contexto educativo"},
            ],
        },
        {
            "id": "task_intent",
            "name": "Task / Intent",
            "weight": 20,
            "criteria": [
                {"level": 0, "description": "No hay tarea definida"},
                {"level": 1, "description": "Tarea ambigua o muy general"},
                {"level": 2, "description": "Tarea clara pero sin objetivo pedagogico"},
                {"level": 3, "description": "Tarea clara con objetivo definido"},
                {"level": 4, "description": "Tarea precisa, con objetivo y verbo de accion claro"},
            ],
        },
        {
            "id": "contexto",
            "name": "Contexto",
            "weight": 20,
            "criteria": [
                {"level": 0, "description": "No hay contexto"},
                {"level": 1, "description": "Contexto minimo o irrelevante"},
                {"level": 2, "description": "Contexto basico (nivel, tema o situacion)"},
                {"level": 3, "description": "Contexto adecuado y comprensible"},
                {"level": 4, "description": "Contexto detallado (nivel educativo, area, situacion, objetivos)"},
            ],
        },
        {
            "id": "output",
            "name": "Formato de Salida",
            "weight": 15,
            "criteria": [
                {"level": 0, "description": "No especifica salida"},
                {"level": 1, "description": "Salida muy general (ej: 'explica')"},
                {"level": 2, "description": "Salida definida pero sin estructura"},
                {"level": 3, "description": "Salida estructurada (ej: lista, parrafos)"},
                {"level": 4, "description": "Salida claramente definida con formato (tabla, markdown, pasos, etc)"},
            ],
        },
        {
            "id": "audiencia",
            "name": "Audiencia",
            "weight": 10,
            "criteria": [
                {"level": 0, "description": "No define audiencia"},
                {"level": 1, "description": "Audiencia muy general"},
                {"level": 2, "description": "Audiencia definida (ej: estudiantes)"},
                {"level": 3, "description": "Audiencia especifica (edad, grado o caracteristicas)"},
            ],
        },
        {
            "id": "steps",
            "name": "Paso a Paso",
            "weight": 10,
            "criteria": [
                {"level": 0, "description": "No hay pasos"},
                {"level": 1, "description": "Pasos implicitos o poco claros"},
                {"level": 2, "description": "Pasos definidos pero incompletos"},
                {"level": 3, "description": "Secuencia clara y logica"},
            ],
        },
        {
            "id": "referencias",
            "name": "Referencias",
            "weight": 5,
            "criteria": [
                {"level": 0, "description": "No usa referencias"},
                {"level": 1, "description": "Referencias vagas"},
                {"level": 2, "description": "Referencias utiles o ejemplos concretos"},
            ],
        },
        {
            "id": "tonalidad",
            "name": "Tonalidad",
            "weight": 5,
            "criteria": [
                {"level": 0, "description": "No define tono"},
                {"level": 1, "description": "Tono generico"},
                {"level": 2, "description": "Tono adecuado al contexto educativo"},
            ],
        },
        {
            "id": "tecnicas",
            "name": "Tecnicas de Prompting",
            "weight": 5,
            "criteria": [
                {"level": 0, "description": "No usa tecnicas"},
                {"level": 1, "description": "Uso basico (ej: instrucciones simples)"},
                {"level": 2, "description": "Uso de tecnicas como step by step o delimitadores"},
            ],
        },
    ],
}

RUBRIC_DIMENSION_NAMES = {
    item["id"]: item["name"] for item in PROMPT_CANVAS_RUBRIC["dimensions"]
}

RUBRIC_MAX_LEVELS = {
    item["id"]: max((criterion["level"] for criterion in item["criteria"]), default=0)
    for item in PROMPT_CANVAS_RUBRIC["dimensions"]
}

RUBRIC_WEIGHTS = {
    item["id"]: item["weight"] for item in PROMPT_CANVAS_RUBRIC["dimensions"]
}


def build_prompt(data):
    sections = {
        "Purpose": data.get("purpose", "").strip(),
        "Role": data.get("role", "").strip(),
        "Context": data.get("context", "").strip(),
        "Task": data.get("task", "").strip(),
        "Process": data.get("process", "").strip(),
        "Format": data.get("format", "").strip(),
        "Constraints": data.get("constraints", "").strip(),
    }

    return "\n\n".join(f"{title}:\n{value}" for title, value in sections.items())


def evaluate_prompt(prompt, data=None):
    normalized_data = _normalize_input_data(data, prompt)
    ai_result = _evaluate_prompt_with_ai(normalized_data)

    if ai_result:
        ai_result = _enforce_strict_role_scoring(ai_result, normalized_data)
        ai_score = max(0.0, min(100.0, float(ai_result.get("score", 0))))
        fallback_score, _ = _evaluate_prompt_with_rubric_rules(normalized_data)
        consistency_guard = min(ai_score, fallback_score + 10)
        final_score = _apply_soft_quality_caps(consistency_guard, ai_result.get("dimension_scores") or {})
        ai_result["score"] = final_score
        detailed_feedback = _build_rubric_feedback(ai_result)
        return round(final_score, 1), detailed_feedback

    fallback_score, fallback_feedback = _evaluate_prompt_with_rubric_rules(normalized_data)
    return round(fallback_score, 1), fallback_feedback


def _normalize_input_data(data, prompt):
    if isinstance(data, dict):
        normalized = {key: str(data.get(key, "")).strip() for key in FIELD_KEYS}
        return normalized

    return {
        "purpose": _extract_section(prompt, "Purpose"),
        "role": _extract_section(prompt, "Role"),
        "context": _extract_section(prompt, "Context"),
        "task": _extract_section(prompt, "Task"),
        "process": _extract_section(prompt, "Process"),
        "format": _extract_section(prompt, "Format"),
        "constraints": _extract_section(prompt, "Constraints"),
    }


def _evaluate_prompt_with_ai(data):
    api_key = getattr(settings, "OPENAI_API_KEY", "").strip()
    if not api_key:
        return None

    try:
        from openai import OpenAI
    except Exception:
        return None

    client = OpenAI(api_key=api_key)
    model = getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")

    system_message = (
        "You are an expert in pedagogical prompt engineering for secondary education. "
        "Evaluate prompts using a weighted rubric and return only valid JSON. "
        "All feedback visible to teachers must be in Spanish and actionable."
    )

    rubric_json = json.dumps(PROMPT_CANVAS_RUBRIC, ensure_ascii=False)

    user_message = f"""
Evalua la calidad del prompt pedagogico con la siguiente rubrica exacta y sus pesos.

Rubrica (JSON):
{rubric_json}

Campos recibidos:
- purpose: {data.get('purpose', '')}
- role: {data.get('role', '')}
- context: {data.get('context', '')}
- task: {data.get('task', '')}
- process: {data.get('process', '')}
- format: {data.get('format', '')}
- constraints: {data.get('constraints', '')}

Reglas de salida:
1. score: numero entre 0 y 100.
2. overall_feedback: texto corto en espanol.
3. dimension_scores: objeto con estas keys exactas:
     persona_rol, task_intent, contexto, output, audiencia, steps, referencias, tonalidad, tecnicas.
4. Para cada dimension incluye:
     - level: numero segun niveles definidos en la rubrica.
     - max_level: numero maximo de la dimension.
     - weighted_score: puntaje ponderado de esa dimension (0 al peso de la dimension).
     - feedback: texto breve en espanol que explique que esta bien y que falta.
5. recommendations: arreglo de recomendaciones accionables en espanol (minimo 3, maximo 7).
6. Asegura consistencia: la suma de weighted_score debe ser igual a score (tolerancia decimal de +/-0.2).
7. Usa toda la escala y evita inflar puntajes.

Devuelve SOLO JSON valido con esta forma exacta:
{{
  "score": 0,
  "overall_feedback": "",
    "dimension_scores": {{
        "persona_rol": {{"level": 0, "max_level": 3, "weighted_score": 0, "feedback": ""}},
        "task_intent": {{"level": 0, "max_level": 4, "weighted_score": 0, "feedback": ""}},
        "contexto": {{"level": 0, "max_level": 4, "weighted_score": 0, "feedback": ""}},
        "output": {{"level": 0, "max_level": 4, "weighted_score": 0, "feedback": ""}},
        "audiencia": {{"level": 0, "max_level": 3, "weighted_score": 0, "feedback": ""}},
        "steps": {{"level": 0, "max_level": 3, "weighted_score": 0, "feedback": ""}},
        "referencias": {{"level": 0, "max_level": 2, "weighted_score": 0, "feedback": ""}},
        "tonalidad": {{"level": 0, "max_level": 2, "weighted_score": 0, "feedback": ""}},
        "tecnicas": {{"level": 0, "max_level": 2, "weighted_score": 0, "feedback": ""}}
    }},
    "recommendations": ["", "", ""]
}}
"""

    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
        )
    except Exception:
        return None

    raw_content = response.choices[0].message.content if response.choices else None
    if not raw_content:
        return None

    try:
        payload = json.loads(raw_content)
    except json.JSONDecodeError:
        return None

    raw_dimension_scores = payload.get("dimension_scores") or {}
    normalized_dimension_scores = {}

    for dimension_id in RUBRIC_DIMENSION_NAMES.keys():
        source = raw_dimension_scores.get(dimension_id) or {}
        max_level = RUBRIC_MAX_LEVELS[dimension_id]
        level = _to_int(source.get("level", 0), min_value=0, max_value=max_level)
        weight = RUBRIC_WEIGHTS[dimension_id]
        weighted_score = round((level / max_level) * weight, 1) if max_level else 0.0

        normalized_dimension_scores[dimension_id] = {
            "level": level,
            "max_level": _to_int(source.get("max_level", max_level), min_value=0, max_value=max_level),
            "weighted_score": weighted_score,
            "feedback": str(source.get("feedback", "")).strip(),
        }

    recommendations = payload.get("recommendations") or []
    normalized_recommendations = [
        str(item).strip() for item in recommendations if str(item).strip()
    ]

    computed_total = round(
        sum(item["weighted_score"] for item in normalized_dimension_scores.values()),
        1,
    )
    final_total = computed_total

    return {
        "score": final_total,
        "overall_feedback": str(payload.get("overall_feedback", "")).strip(),
        "dimension_scores": normalized_dimension_scores,
        "recommendations": normalized_recommendations,
    }


def generate_quality_prompt(data, feedback_history=None):
    normalized = {key: str(data.get(key, "")).strip() for key in FIELD_KEYS}
    feedback_history = feedback_history or []

    api_key = getattr(settings, "OPENAI_API_KEY", "").strip()
    if not api_key:
        return {
            **normalized,
            "full_prompt": build_prompt(normalized),
        }

    try:
        from openai import OpenAI
    except Exception:
        return {
            **normalized,
            "full_prompt": build_prompt(normalized),
        }

    client = OpenAI(api_key=api_key)
    model = getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")

    feedback_text = "\n".join(f"- {item}" for item in feedback_history if item)

    system_message = (
        "You are an expert pedagogical prompt engineer. "
        "Rewrite the teacher prompt to a high-quality version following Prompt Canvas and cognitive scaffolding. "
        "Return only valid JSON and keep the final content in Spanish."
    )

    user_message = f"""
Toma el ultimo intento del docente y mejora el prompt con calidad pedagogica.

Campos del ultimo intento:
- purpose: {normalized.get('purpose', '')}
- role: {normalized.get('role', '')}
- context: {normalized.get('context', '')}
- task: {normalized.get('task', '')}
- process: {normalized.get('process', '')}
- format: {normalized.get('format', '')}
- constraints: {normalized.get('constraints', '')}

Retroalimentacion acumulada:
{feedback_text or '- Sin retroalimentacion previa'}

Reglas:
1. Mejora todos los campos para que queden claros, especificos y aplicables en secundaria.
2. Mantener coherencia entre objetivo, tarea, proceso, formato y restricciones.
3. Incluir andamiaje cognitivo en process.
4. full_prompt debe seguir esta estructura exacta:
Purpose:\n...\n\nRole:\n...\n\nContext:\n...\n\nTask:\n...\n\nProcess:\n...\n\nFormat:\n...\n\nConstraints:\n...

Devuelve SOLO JSON valido con esta estructura exacta:
{{
  "purpose": "",
  "role": "",
  "context": "",
  "task": "",
  "process": "",
  "format": "",
  "constraints": "",
  "full_prompt": ""
}}
"""

    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0.3,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
        )
    except Exception:
        return {
            **normalized,
            "full_prompt": build_prompt(normalized),
        }

    raw_content = response.choices[0].message.content if response.choices else None
    if not raw_content:
        return {
            **normalized,
            "full_prompt": build_prompt(normalized),
        }

    try:
        payload = json.loads(raw_content)
    except json.JSONDecodeError:
        return {
            **normalized,
            "full_prompt": build_prompt(normalized),
        }

    improved = {
        key: str(payload.get(key, normalized.get(key, ""))).strip()
        for key in FIELD_KEYS
    }

    full_prompt = str(payload.get("full_prompt", "")).strip() or build_prompt(improved)
    improved["full_prompt"] = full_prompt
    return improved


def _extract_section(prompt, section_name):
    marker = f"{section_name}:\n"
    start = prompt.find(marker)
    if start == -1:
        return ""

    start += len(marker)
    remaining = prompt[start:]
    next_break = remaining.find("\n\n")

    if next_break == -1:
        return remaining.strip()

    return remaining[:next_break].strip()


def _evaluate_prompt_with_rubric_rules(data):
    dimensions = {
        "persona_rol": _score_persona_role(data),
        "task_intent": _score_task_intent(data),
        "contexto": _score_context(data),
        "output": _score_output_format(data),
        "audiencia": _score_audience(data),
        "steps": _score_steps(data),
        "referencias": _score_references(data),
        "tonalidad": _score_tonality(data),
        "tecnicas": _score_prompting_techniques(data),
    }

    total_score = 0.0
    feedback = []

    for dimension_id, level in dimensions.items():
        max_level = RUBRIC_MAX_LEVELS[dimension_id]
        weight = RUBRIC_WEIGHTS[dimension_id]
        weighted_score = round((level / max_level) * weight, 1) if max_level else 0.0
        total_score += weighted_score

        feedback.append(
            f"{RUBRIC_DIMENSION_NAMES[dimension_id]}: Nivel {level}/{max_level}. "
            f"Puntaje {weighted_score}/{weight}."
        )

    feedback.insert(0, f"Puntaje total: {round(total_score, 1)}/100")

    if total_score >= 85:
        feedback.insert(0, "Estado de calidad: El prompt ya tiene calidad para uso docente.")
    else:
        feedback.insert(0, "Estado de calidad: El prompt aun no alcanza nivel de calidad. Revisa las recomendaciones.")

    feedback.extend(_build_rule_recommendations(data, dimensions))
    return total_score, _deduplicate_feedback(feedback)


def _build_rubric_feedback(ai_result):
    total_score = round(max(0.0, min(100.0, float(ai_result.get("score", 0)))), 1)
    overall_feedback = str(ai_result.get("overall_feedback", "")).strip()
    dimension_scores = ai_result.get("dimension_scores") or {}
    recommendations = ai_result.get("recommendations") or []

    feedback = []
    if total_score >= 85:
        feedback.append("Estado de calidad: El prompt ya tiene calidad para uso docente.")
    else:
        feedback.append("Estado de calidad: El prompt aun no alcanza nivel de calidad. Revisa las recomendaciones.")

    feedback.append(f"Puntaje total: {total_score}/100")

    if overall_feedback:
        feedback.append(f"Retroalimentacion general: {overall_feedback}")

    for dimension_id in RUBRIC_DIMENSION_NAMES.keys():
        detail = dimension_scores.get(dimension_id) or {}
        level = _to_int(detail.get("level", 0), min_value=0, max_value=RUBRIC_MAX_LEVELS[dimension_id])
        max_level = _to_int(detail.get("max_level", RUBRIC_MAX_LEVELS[dimension_id]), min_value=0, max_value=RUBRIC_MAX_LEVELS[dimension_id])
        weighted_score = round(_to_float(detail.get("weighted_score", 0), min_value=0, max_value=RUBRIC_WEIGHTS[dimension_id]), 1)
        note = str(detail.get("feedback", "")).strip()

        dimension_line = (
            f"{RUBRIC_DIMENSION_NAMES[dimension_id]}: Nivel {level}/{max_level}. "
            f"Puntaje {weighted_score}/{RUBRIC_WEIGHTS[dimension_id]}."
        )
        if note:
            dimension_line = f"{dimension_line} {note}"

        feedback.append(dimension_line)

    for recommendation in recommendations:
        feedback.append(f"Recomendaciones: {recommendation}")

    return _deduplicate_feedback(feedback)


def _to_float(value, min_value=0.0, max_value=100.0):
    try:
        result = float(value)
    except (TypeError, ValueError):
        result = min_value
    return max(min_value, min(max_value, result))


def _to_int(value, min_value=0, max_value=4):
    try:
        result = int(value)
    except (TypeError, ValueError):
        result = min_value
    return max(min_value, min(max_value, result))


def _matches_any_pattern(text, patterns):
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def _count_pattern_matches(text, patterns):
    return sum(1 for pattern in patterns if re.search(pattern, text, flags=re.IGNORECASE))


def _apply_soft_quality_caps(score, dimension_scores):
    final_score = max(0.0, min(100.0, float(score)))

    role_level = _to_int((dimension_scores.get("persona_rol") or {}).get("level", 0), min_value=0, max_value=3)
    task_level = _to_int((dimension_scores.get("task_intent") or {}).get("level", 0), min_value=0, max_value=4)
    context_level = _to_int((dimension_scores.get("contexto") or {}).get("level", 0), min_value=0, max_value=4)
    output_level = _to_int((dimension_scores.get("output") or {}).get("level", 0), min_value=0, max_value=4)

    # Soft caps only for clearly weak pedagogical structure to avoid overly punitive scoring.
    if role_level == 0:
        final_score = min(final_score, 68.0)
    elif role_level == 1:
        final_score = min(final_score, 80.0)
    if task_level <= 1:
        final_score = min(final_score, 72.0)
    if context_level <= 1:
        final_score = min(final_score, 74.0)
    if output_level <= 1:
        final_score = min(final_score, 76.0)

    return round(final_score, 1)


def _enforce_strict_role_scoring(ai_result, data):
    result = dict(ai_result or {})
    dimension_scores = dict(result.get("dimension_scores") or {})

    role_level = _score_persona_role(data)
    role_max_level = RUBRIC_MAX_LEVELS["persona_rol"]
    role_weight = RUBRIC_WEIGHTS["persona_rol"]
    role_weighted_score = round((role_level / role_max_level) * role_weight, 1) if role_max_level else 0.0

    role_detail = dict(dimension_scores.get("persona_rol") or {})
    role_detail["level"] = role_level
    role_detail["max_level"] = role_max_level
    role_detail["weighted_score"] = role_weighted_score
    role_detail["feedback"] = _build_role_feedback_message(role_level)

    dimension_scores["persona_rol"] = role_detail
    result["dimension_scores"] = dimension_scores

    recomputed_total = round(
        sum(
            round(
                _to_float((dimension_scores.get(dimension_id) or {}).get("weighted_score", 0), min_value=0, max_value=RUBRIC_WEIGHTS[dimension_id]),
                1,
            )
            for dimension_id in RUBRIC_DIMENSION_NAMES.keys()
        ),
        1,
    )
    result["score"] = recomputed_total

    return result


def _build_role_feedback_message(level):
    if level <= 0:
        return (
            "No se definio un rol docente claro. Indica un rol especifico, por ejemplo: "
            "docente de matematicas de grado 10 con enfoque en didactica."
        )
    if level == 1:
        return (
            "El rol es generico. Para mejorarlo, agrega area disciplinar, nivel educativo "
            "y un enfoque pedagogico concreto."
        )
    if level == 2:
        return (
            "El rol incluye area, pero aun puede fortalecerse. Agrega nivel educativo "
            "y enfoque pedagogico para mayor precision."
        )
    return "El rol esta bien definido y alineado al contexto educativo."


def _score_persona_role(data):
    role = data.get("role", "")
    role_text = role.strip()

    if not role_text:
        return 0

    generic_role_patterns = [
        r"\b(profesor|profesora|teacher|experto|experta|especialista)\b",
        r"\b(actua\s+como|haz\s+de)\s+(profesor|profesora|experto|experta)\b",
    ]
    area_patterns = [
        r"\bmatematicas?\b", r"\blengua(?:je)?\b", r"\bciencias?\b", r"\bfisica\b",
        r"\bquimica\b", r"\bhistoria\b", r"\bgeografia\b", r"\bbiologia\b",
        r"\bingles\b", r"\btecnologia\b", r"\bartes?\b", r"\bfilosofia\b",
    ]
    educational_level_patterns = [
        r"\bgrado\s*\d+\b", r"\bsecundaria\b", r"\bbachillerato\b", r"\bprimaria\b",
        r"\bmedia\b", r"\b(9|10|11)(?:o|ro|do)?\b",
    ]
    pedagogical_approach_patterns = [
        r"\benfoque\b", r"\bevaluacion\s+formativa\b", r"\baprendizaje\s+basado\b",
        r"\bconstructiv\w*\b", r"\bdidact\w*\b", r"\bandamiaje\b", r"\binclusi\w*\b",
        r"\bdiferenciad\w*\b", r"\bmetacogn\w*\b",
    ]

    has_area = _matches_any_pattern(role_text, area_patterns)
    has_educational_level = _matches_any_pattern(role_text, educational_level_patterns)
    has_pedagogical_approach = _matches_any_pattern(role_text, pedagogical_approach_patterns)
    has_generic_role = _matches_any_pattern(role_text, generic_role_patterns)

    signal_groups = [has_area, has_educational_level, has_pedagogical_approach]
    matched_groups = sum(1 for flag in signal_groups if flag)

    # Nivel 3: rol completo con al menos 2 grupos de senales pedagogicas.
    if matched_groups >= 2:
        return 3

    # Nivel 2: rol con area disciplinar explicita.
    if has_area:
        return 2

    # Nivel 1: rol generico o demasiado corto/sin especificidad.
    if has_generic_role or len(role_text.split()) <= 2 or len(role_text) < 20:
        return 1

    return 1


def _score_task_intent(data):
    task_text = f"{data.get('purpose', '')} {data.get('task', '')}".strip()
    task_lower = task_text.lower()

    if not data.get("task", "").strip():
        return 0
    if len(task_text) < 40:
        return 1

    objective_signals = ["objetivo", "meta", "logro", "aprendiz", "competencia"]
    action_verbs = [
        "disena", "crea", "genera", "elabora", "analiza", "compara", "explica", "resuelve", "construye",
    ]

    has_objective = any(token in task_lower for token in objective_signals)
    has_action = any(token in task_lower for token in action_verbs)

    if has_objective and has_action and len(task_text) >= 80:
        return 4
    if has_objective:
        return 3
    return 2


def _score_context(data):
    context = data.get("context", "")
    context_lower = context.lower()

    if not context:
        return 0
    if len(context) < 30:
        return 1

    context_signals = [
        "grado", "curso", "nivel", "edad", "area", "asignatura", "tema", "objetivo", "situacion"
    ]
    signal_count = sum(1 for token in context_signals if token in context_lower)

    if len(context) >= 90 and signal_count >= 4:
        return 4
    if len(context) >= 60 and signal_count >= 2:
        return 3
    return 2


def _score_output_format(data):
    output_text = data.get("format", "")
    format_text = output_text.strip()

    if not format_text:
        return 0

    specific_format_patterns = [
        r"\btabla\b", r"\bmarkdown\b", r"\bjson\b", r"\bcsv\b", r"\byaml\b",
        r"\brubrica\b", r"\bchecklist\b", r"\bhtml\b",
    ]
    structured_text_patterns = [
        r"\blista(?:\s+numerada)?\b", r"\bseccion(?:es)?\b", r"\bsubtitulo(?:s)?\b",
        r"\bcolumna(?:s)?\b", r"\bencabezado(?:s)?\b", r"(?m)^\s*(?:\d+[\).]|[-*])\s+",
    ]
    simple_text_patterns = [
        r"\btexto\b", r"\bparrafo(?:s)?\b", r"\bexplicacion\b", r"\bresumen\b",
    ]

    if _matches_any_pattern(format_text, specific_format_patterns):
        return 4
    if _matches_any_pattern(format_text, structured_text_patterns):
        return 3
    if _matches_any_pattern(format_text, simple_text_patterns):
        return 2
    if len(format_text) < 20:
        return 1
    return 2


def _score_audience(data):
    combined = " ".join([
        data.get("context", ""),
        data.get("task", ""),
        data.get("role", ""),
    ]).lower()

    if not combined.strip():
        return 0

    specific_signals = ["grado", "edad", "anos", "secundaria", "primaria", "bachillerato", "estudiantes"]
    if "estudiantes" not in combined and all(token not in combined for token in specific_signals):
        return 0

    if any(token in combined for token in ["grado", "edad", "anos"]):
        return 3
    if "estudiantes" in combined:
        return 2
    return 1


def _score_steps(data):
    process_text = data.get("process", "").strip()
    task_text = data.get("task", "").strip()

    if not process_text and not task_text:
        return 0

    numbered_step_patterns = [
        r"(?m)^\s*\d+[\).:-]\s+",
        r"(?m)^\s*(paso|fase|etapa)\s*\d+\b",
    ]
    logical_sequence_patterns = [
        r"\bprimero\b", r"\bsegundo\b", r"\btercero\b", r"\bluego\b",
        r"\ba\s+continuacion\b", r"\bdespues\b", r"\bfinalmente\b", r"\bpor\s+ultimo\b",
    ]
    step_presence_patterns = [
        r"\bpasos?\b", r"\bfases?\b", r"\bsecuencia\b",
        r"(?m)^\s*[-*]\s+",
    ]

    has_numbered_steps = _matches_any_pattern(process_text, numbered_step_patterns)
    sequence_markers = _count_pattern_matches(process_text, logical_sequence_patterns)
    has_step_presence = _matches_any_pattern(process_text, step_presence_patterns)
    mentions_step_by_step = _matches_any_pattern(process_text, [r"\bpaso\s+a\s+paso\b", r"\bstep\s+by\s+step\b"])

    if has_numbered_steps or sequence_markers >= 3:
        return 3
    if mentions_step_by_step:
        return 1
    if has_step_presence:
        return 2
    if _matches_any_pattern(task_text, [r"\bpaso\s+a\s+paso\b", r"\bsecuencia\b"]):
        return 1
    return 0


def _score_references(data):
    combined = " ".join([
        data.get("context", ""),
        data.get("task", ""),
        data.get("constraints", ""),
    ]).lower()

    if not combined.strip():
        return 0

    reference_signals = ["ejemplo", "referencia", "fuente", "caso", "texto", "lectura", "modelo"]
    has_references = any(token in combined for token in reference_signals)
    return 2 if has_references else 0


def _score_tonality(data):
    combined = " ".join([
        data.get("role", ""),
        data.get("format", ""),
        data.get("constraints", ""),
    ]).lower()

    if not combined.strip():
        return 0

    tone_signals = ["tono", "claro", "amable", "didactico", "formal", "motivador", "lenguaje"]
    has_tone = any(token in combined for token in tone_signals)
    return 2 if has_tone else 1


def _score_prompting_techniques(data):
    combined_text = " ".join([
        data.get("task", ""),
        data.get("process", ""),
        data.get("format", ""),
        data.get("constraints", ""),
    ]).strip()

    if not combined_text:
        return 0

    numbered_list_patterns = [r"(?m)^\s*\d+[\).:-]\s+"]
    delimiter_patterns = [r"###", r"---", r"```"]
    example_patterns = [r"\bejemplo(?:s)?\b", r"\bentrada\s*/\s*salida\b", r"\bcaso\s+de\s+uso\b"]
    meta_instruction_patterns = [
        r"\brazona\b", r"\banaliza\b", r"\bpiensa\b", r"\bjustifica\b",
        r"\bantes\s+de\s+responder\b", r"\bverifica\b",
    ]
    basic_instruction_patterns = [r"\bindica\b", r"\bdebe\b", r"\busa\b", r"\bsigue\b"]

    technique_count = 0
    technique_count += 1 if _matches_any_pattern(combined_text, numbered_list_patterns) else 0
    technique_count += 1 if _matches_any_pattern(combined_text, delimiter_patterns) else 0
    technique_count += 1 if _matches_any_pattern(combined_text, example_patterns) else 0
    technique_count += 1 if _matches_any_pattern(combined_text, meta_instruction_patterns) else 0

    if technique_count >= 2:
        return 2
    if technique_count == 1:
        return 1
    if _matches_any_pattern(combined_text, basic_instruction_patterns):
        return 1
    return 0


def _build_rule_recommendations(data, dimensions):
    recommendations = []

    if dimensions.get("persona_rol", 0) < 3:
        recommendations.append(
            "Recomendaciones: Define un rol docente especifico y alineado al area (por ejemplo, tutor de ciencias con enfoque en evaluacion formativa)."
        )

    if dimensions.get("task_intent", 0) < 4:
        recommendations.append(
            "Recomendaciones: Formula la tarea con un verbo de accion y objetivo pedagogico explicito (que se espera lograr y como se evidenciara)."
        )

    if dimensions.get("contexto", 0) < 4:
        recommendations.append(
            "Recomendaciones: Agrega contexto educativo completo: grado, asignatura, tema, tiempo disponible y necesidad del grupo."
        )

    if dimensions.get("output", 0) < 4:
        recommendations.append(
            "Recomendaciones: Especifica un formato de salida concreto, por ejemplo tabla en markdown con columnas y orden de secciones."
        )

    if dimensions.get("steps", 0) < 3:
        recommendations.append(
            "Recomendaciones: Incluye una secuencia paso a paso con fases claras para guiar la respuesta del modelo."
        )

    if dimensions.get("tecnicas", 0) < 2:
        recommendations.append(
            "Recomendaciones: Integra tecnicas de prompting (paso a paso, delimitadores o criterios explicitos de evaluacion)."
        )

    if not recommendations:
        recommendations.append(
            "Recomendaciones: El prompt esta bien logrado; fortalece aun mas con ejemplos de entrada/salida y criterios de calidad medibles."
        )

    return recommendations[:7]


def _deduplicate_feedback(items):
    cleaned = []
    seen = set()

    for item in items:
        text = str(item).strip()
        if not text:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(text)

    return cleaned
