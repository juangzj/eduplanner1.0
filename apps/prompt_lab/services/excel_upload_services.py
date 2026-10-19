from apps.levels.services import ExcelUploadError, ExcelUploadService


# Campos del formulario de Prompt Lab que la IA debe identificar en el Excel
PROMPT_EXCEL_FIELDS_SCHEMA = [
    {
        "name": "purpose",
        "label": "Propósito",
        "help_text": "Objetivo de aprendizaje que debe apoyar el prompt.",
    },
    {
        "name": "role",
        "label": "Rol",
        "help_text": "Cómo debe comportarse la IA: perfil pedagógico y área.",
    },
    {
        "name": "context",
        "label": "Contexto",
        "help_text": "Grado, área, tema, tiempo, recursos y características del grupo.",
    },
    {
        "name": "task",
        "label": "Tarea",
        "help_text": "Tarea concreta que debe realizar la IA y producto esperado.",
    },
    {
        "name": "process",
        "label": "Proceso",
        "help_text": "Pasos opcionales para guiar la respuesta.",
    },
    {
        "name": "format",
        "label": "Formato",
        "help_text": "Estructura exacta de la salida (tabla, rúbrica, pasos, etc.).",
    },
    {
        "name": "constraints",
        "label": "Restricciones",
        "help_text": "Límites opcionales: tono, extensión, exclusiones, idioma.",
    },
]


def extract_prompt_data_from_excel_service(excel_file):
    """
    Lee el archivo Excel y la IA identifica los campos definidos en
    PROMPT_EXCEL_FIELDS_SCHEMA para precargar el formulario
    de Prompt Lab. No crea ningún registro.
    """
    data = ExcelUploadService.extract_fields_with_ai(
        excel_file=excel_file,
        fields_schema=PROMPT_EXCEL_FIELDS_SCHEMA,
    )

    if not any(data.values()):
        raise ExcelUploadError("No se encontró información del prompt en el archivo.")

    return data
