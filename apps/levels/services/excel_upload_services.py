from __future__ import annotations

import unicodedata
from zipfile import BadZipFile
from typing import Any

from django.db import transaction
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

from ..forms import PerformanceLevelTemplateCreateForm
from ..models import PerformanceLevelTemplate
from ..models.performance_level_template_model import (
    AREAS_OPCIONES,
    GRADOS_OPCIONES,
    PERIODO_ACADEMICO_OPCIONES,
)


class ExcelUploadError(Exception):
    """
    Error de negocio al procesar el archivo Excel.
    """


# Celda del Excel -> campo del modelo PerformanceLevelTemplate
EXCEL_CELL_MAPPING = {
    "A2": "area",
    "B2": "grade",
    "C2": "level_title",
    "D2": "level_description",
    "E2": "learning",
    "F2": "didactic_resources",
    "G2": "learning_evidence",
    "H2": "evaluation_criteria",
    "I2": "assessment_instrument",
    "J2": "academic_period",
}


class ExcelUploadService:

    @staticmethod
    @transaction.atomic
    def create_performance_level_from_excel_service(*, excel_file, user) -> PerformanceLevelTemplate:
        """
        Lee el archivo Excel, extrae las celdas definidas en EXCEL_CELL_MAPPING
        y crea la plantilla de nivel de desempeño para el usuario.
        """
        data = ExcelUploadService._extract_data(excel_file)
        data = ExcelUploadService._normalize_choices(data)

        # Se reutiliza el formulario de creación para validar los datos
        form = PerformanceLevelTemplateCreateForm(data=data)
        if not form.is_valid():
            raise ExcelUploadError(ExcelUploadService._format_errors(form))

        performance_level = form.save(commit=False)
        performance_level.user = user
        performance_level.save()

        return performance_level

    @staticmethod
    def _extract_data(excel_file) -> dict[str, Any]:
        try:
            workbook = load_workbook(excel_file, read_only=True, data_only=True)
        except (InvalidFileException, BadZipFile, KeyError, OSError, ValueError) as exc:
            raise ExcelUploadError("No se pudo leer el archivo. Verifique que sea un Excel válido.") from exc

        try:
            sheet = workbook.active
            data = {}
            for cell, field in EXCEL_CELL_MAPPING.items():
                value = sheet[cell].value
                data[field] = "" if value is None else str(value).strip()
            return data
        finally:
            workbook.close()

    @staticmethod
    def _normalize_choices(data: dict[str, Any]) -> dict[str, Any]:
        """
        Ajusta los valores del Excel a las opciones del modelo
        (ignora mayúsculas y tildes; el grado acepta número o nombre).
        """
        data["area"] = ExcelUploadService._match_choice(data["area"], AREAS_OPCIONES)
        data["academic_period"] = ExcelUploadService._match_choice(
            data["academic_period"], PERIODO_ACADEMICO_OPCIONES
        )

        grade = data["grade"]
        if grade.endswith(".0"):
            grade = grade[:-2]
        data["grade"] = ExcelUploadService._match_choice(grade, GRADOS_OPCIONES)

        return data

    @staticmethod
    def _match_choice(value: str, choices: list[tuple[str, str]]) -> str:
        normalized_value = ExcelUploadService._normalize_text(value)
        for key, label in choices:
            if normalized_value in (
                ExcelUploadService._normalize_text(key),
                ExcelUploadService._normalize_text(label),
            ):
                return key
        return value

    @staticmethod
    def _normalize_text(value: str) -> str:
        value = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode("ascii")
        return " ".join(value.lower().split())

    @staticmethod
    def _format_errors(form) -> str:
        cell_by_field = {field: cell for cell, field in EXCEL_CELL_MAPPING.items()}
        errors = []
        for field, field_errors in form.errors.items():
            label = form.fields[field].label if field in form.fields else field
            cell = cell_by_field.get(field, "")
            errors.append(f"{label} ({cell}): {' '.join(field_errors)}")
        return " | ".join(errors)
