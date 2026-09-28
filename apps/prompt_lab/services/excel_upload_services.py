from apps.levels.services import ExcelUploadError, ExcelUploadService


# Celda del Excel -> campo del formulario de Prompt Lab
PROMPT_EXCEL_CELL_MAPPING = {
    "A2": "purpose",
    "B2": "role",
    "C2": "context",
    "D2": "task",
    "E2": "process",
    "F2": "format",
    "G2": "constraints",
}


def extract_prompt_data_from_excel_service(excel_file):
    """
    Lee el archivo Excel y extrae las celdas definidas en
    PROMPT_EXCEL_CELL_MAPPING para precargar el formulario
    de Prompt Lab. No crea ningún registro.
    """
    data = ExcelUploadService._extract_data(excel_file, PROMPT_EXCEL_CELL_MAPPING)

    if not any(data.values()):
        raise ExcelUploadError("El archivo no contiene información en las celdas A2 a G2.")

    return data
