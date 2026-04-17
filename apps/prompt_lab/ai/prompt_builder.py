import json

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
        final_score = max(0.0, min(100.0, float(ai_result.get("score", 0))))
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
        weighted_score = _to_float(source.get("weighted_score", 0), min_value=0, max_value=RUBRIC_WEIGHTS[dimension_id])

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
    model_total = _to_float(payload.get("score", computed_total), min_value=0, max_value=100)

    if abs(model_total - computed_total) <= 0.2:
        final_total = model_total
    else:
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


def _score_persona_role(data):
    role = data.get("role", "")
    role_lower = role.lower()

    if not role:
        return 0
    if len(role) < 20:
        return 1

    pedagogical_signals = [
        "docente", "pedagog", "educa", "didact", "aprendiz", "evaluacion", "secundaria", "primaria"
    ]
    has_pedagogical_alignment = any(token in role_lower for token in pedagogical_signals)
    return 3 if has_pedagogical_alignment else 2


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
    output_lower = output_text.lower()

    if not output_text:
        return 0
    if len(output_text) < 20:
        return 1

    structure_signals = ["lista", "parrafo", "seccion", "estructura", "columnas", "pasos"]
    formatted_signals = ["tabla", "markdown", "json", "csv", "rubrica", "checklist"]

    has_structure = any(token in output_lower for token in structure_signals)
    has_formatted = any(token in output_lower for token in formatted_signals)

    if has_formatted:
        return 4
    if has_structure:
        return 3
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
    process = data.get("process", "").lower()
    task = data.get("task", "").lower()

    if not process and not task:
        return 0

    explicit_steps = ["1)", "2)", "3)", "paso", "fase", "secuencia"]
    if process and any(token in process for token in explicit_steps):
        return 3
    if process:
        return 2
    if any(token in task for token in ["paso", "secuencia"]):
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
    combined = " ".join([
        data.get("task", ""),
        data.get("process", ""),
        data.get("format", ""),
        data.get("constraints", ""),
    ]).lower()

    if not combined.strip():
        return 0

    advanced_signals = ["step by step", "paso a paso", "delimitador", "```", "json", "rubrica", "criterio"]
    basic_signals = ["instruccion", "indica", "debe", "usa"]

    if any(token in combined for token in advanced_signals):
        return 2
    if any(token in combined for token in basic_signals):
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
