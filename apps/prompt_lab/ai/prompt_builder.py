import json

from django.conf import settings


FIELD_KEYS = ("purpose", "role", "context", "task", "process", "format", "constraints")
FIELD_LABELS_ES = {
    "purpose": "Proposito",
    "role": "Rol",
    "context": "Contexto",
    "task": "Tarea",
    "process": "Proceso",
    "format": "Formato",
    "constraints": "Restricciones",
}

FIELD_MIN_LENGTH = {
    "purpose": 40,
    "role": 25,
    "context": 60,
    "task": 60,
    "process": 25,
    "format": 35,
    "constraints": 20,
}

FIELD_EXAMPLES = {
    "purpose": "Ejemplo: Disenar una actividad de analisis de fuentes historicas para fortalecer pensamiento critico en grado 9.",
    "role": "Ejemplo: Actua como asesor pedagogico experto en aprendizaje activo y evaluacion formativa en secundaria.",
    "context": "Ejemplo: Curso de 38 estudiantes de grado 8, nivel heterogeneo, con 50 minutos de clase y acceso limitado a internet.",
    "task": "Ejemplo: Genera una secuencia de 3 actividades, cada una con objetivo, instrucciones y criterio de logro observable.",
    "process": "Ejemplo: 1) Activar saberes previos 2) Modelado guiado 3) Practica colaborativa 4) Cierre metacognitivo.",
    "format": "Ejemplo: Responde en tabla con columnas: fase, objetivo, actividad, evidencia, tiempo, instrumento de evaluacion.",
    "constraints": "Ejemplo: Usa lenguaje claro para secundaria, maximo 450 palabras, incluir al menos 1 estrategia de inclusion.",
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
    heuristic_score, heuristic_feedback = _evaluate_prompt_with_rules(prompt)

    normalized_data = _normalize_input_data(data, prompt)
    ai_result = _evaluate_prompt_with_ai(normalized_data)

    if not ai_result:
        detailed_feedback = _expand_feedback_with_field_guidance(
            heuristic_feedback,
            normalized_data,
            include_strengths=False,
        )
        return heuristic_score, detailed_feedback

    ai_score = max(0.0, min(10.0, float(ai_result.get("score", heuristic_score))))
    quality_ready = bool(ai_result.get("is_quality", ai_score >= 8.0))
    ai_score = _calibrate_ai_score(ai_score, quality_ready, normalized_data)
    overall_feedback = str(ai_result.get("overall_feedback", "")).strip()
    field_feedback = ai_result.get("field_feedback", {}) or {}

    feedback = [
        (
            "El prompt ya tiene calidad para uso docente."
            if quality_ready
            else "El prompt aun no alcanza nivel de calidad. Revisa los campos sugeridos."
        )
    ]

    if overall_feedback:
        feedback.append(f"Retroalimentacion general: {overall_feedback}")

    for field in FIELD_KEYS:
        note = str(field_feedback.get(field, "")).strip()
        if note:
            feedback.append(f"{FIELD_LABELS_ES[field]}: {note}")

    for rule_feedback in heuristic_feedback:
        if rule_feedback not in feedback:
            feedback.append(rule_feedback)

    detailed_feedback = _expand_feedback_with_field_guidance(
        feedback,
        normalized_data,
        include_strengths=True,
    )
    return round(ai_score, 1), detailed_feedback


def _evaluate_prompt_with_rules(prompt):
    feedback = []
    score = 10.0

    lower_prompt = prompt.lower()

    if "purpose:\n" in lower_prompt and len(_extract_section(prompt, "Purpose")) < 20:
        score -= 1.5
        feedback.append("Amplia el proposito para que el objetivo pedagogico quede explicito.")

    if "context:\n" in lower_prompt and len(_extract_section(prompt, "Context")) < 20:
        score -= 2.0
        feedback.append("Agrega mas detalles de contexto sobre grado, tema y condiciones del aula.")

    if "task:\n" in lower_prompt and len(_extract_section(prompt, "Task")) < 20:
        score -= 2.0
        feedback.append("Especifica resultados esperados y criterios de exito para la tarea.")

    if "format:\n" in lower_prompt and len(_extract_section(prompt, "Format")) < 15:
        score -= 1.5
        feedback.append("Aclara el formato de respuesta, la estructura y la extension esperada.")

    if "process:\n\n" in lower_prompt or "constraints:\n\n" in lower_prompt:
        score -= 1.0
        feedback.append("Incluye proceso o restricciones para mejorar el andamiaje y reducir ambiguedad.")

    score = max(0.0, min(10.0, round(score, 1)))

    if not feedback:
        feedback.append("La base del prompt es solida. Continua iterando con ejemplos especificos de la asignatura.")

    return score, feedback


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
        "Evaluate prompt quality by field and return only JSON. "
        "Feedback must be in Spanish and actionable for teachers."
    )

    user_message = f"""
Evalua la calidad del prompt pedagogico por campo.

Campos recibidos:
- purpose: {data.get('purpose', '')}
- role: {data.get('role', '')}
- context: {data.get('context', '')}
- task: {data.get('task', '')}
- process: {data.get('process', '')}
- format: {data.get('format', '')}
- constraints: {data.get('constraints', '')}

Reglas de salida:
1. score: numero entre 0 y 10.
2. is_quality: true si el prompt ya tiene calidad pedagogica util para docente.
3. overall_feedback: texto corto en espanol.
4. field_feedback: objeto con keys purpose, role, context, task, process, format, constraints.
5. Cada valor de field_feedback debe tener recomendacion breve en espanol para mejorar ese campo.
6. Si un campo esta bien, indica que esta correcto y como reforzarlo.
7. Usa toda la escala: 10 solo para excelencia pedagogica real y completa.
8. Asigna 10 si el prompt es claro, especifico, contextualizado, con tarea evaluable,
   andamiaje util y formato/restricciones bien definidos.
9. En cada campo explica: (a) que esta bien, (b) que falta, (c) una mejora concreta en una frase.

Devuelve SOLO JSON valido con esta forma exacta:
{{
  "score": 0,
  "is_quality": false,
  "overall_feedback": "",
  "field_feedback": {{
    "purpose": "",
    "role": "",
    "context": "",
    "task": "",
    "process": "",
    "format": "",
    "constraints": ""
  }}
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

    field_feedback = payload.get("field_feedback") or {}
    normalized_fields = {
        key: str(field_feedback.get(key, "")).strip()
        for key in FIELD_KEYS
    }

    return {
        "score": payload.get("score", 0),
        "is_quality": bool(payload.get("is_quality", False)),
        "overall_feedback": str(payload.get("overall_feedback", "")).strip(),
        "field_feedback": normalized_fields,
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


def _calibrate_ai_score(ai_score, quality_ready, data):
    if not quality_ready:
        return ai_score

    purpose_ok = len(data.get("purpose", "")) >= 40
    role_ok = len(data.get("role", "")) >= 25
    context_ok = len(data.get("context", "")) >= 60
    task_ok = len(data.get("task", "")) >= 60
    format_ok = len(data.get("format", "")) >= 35

    # At least one of these should be detailed for scaffolding quality.
    process_ok = len(data.get("process", "")) >= 25
    constraints_ok = len(data.get("constraints", "")) >= 20

    core_quality = all([purpose_ok, role_ok, context_ok, task_ok, format_ok])
    scaffolding_quality = process_ok or constraints_ok

    if core_quality and scaffolding_quality and ai_score >= 9.2:
        return 10.0

    return ai_score


def _expand_feedback_with_field_guidance(base_feedback, data, include_strengths):
    feedback = list(base_feedback)

    for field in FIELD_KEYS:
        value = str(data.get(field, "")).strip()
        min_len = FIELD_MIN_LENGTH[field]
        label = FIELD_LABELS_ES[field]

        if len(value) < min_len:
            gap = min_len - len(value)
            feedback.append(
                f"Guia de mejora - {label}: este campo esta incompleto (faltan aprox. {gap} caracteres para un nivel robusto). "
                f"Describe con mayor precision el para que, el como y el criterio de calidad esperado."
            )
            feedback.append(FIELD_EXAMPLES[field])
        elif include_strengths:
            feedback.append(
                f"Fortaleza - {label}: la informacion es suficiente. Ahora mejora precision agregando indicadores observables "
                f"(que hara el estudiante, en cuanto tiempo y con que evidencia)."
            )

    return _deduplicate_feedback(feedback)


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
