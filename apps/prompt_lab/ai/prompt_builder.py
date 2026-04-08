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


def evaluate_prompt(prompt):
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
