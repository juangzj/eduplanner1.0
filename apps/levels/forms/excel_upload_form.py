import os

from django import forms
from django.contrib.auth import get_user_model


# Tamaño máximo permitido para el archivo Excel (5 MB)
EXCEL_MAX_SIZE_MB = 5
EXCEL_ALLOWED_EXTENSIONS = (".xlsx", ".xlsm")


class ExcelUploadForm(forms.Form):
    """
    Formulario para subir un archivo Excel con la información de la plantilla.
    """

    excel_file = forms.FileField(
        label="Archivo Excel",
        help_text=f"Solo archivos .xlsx o .xlsm (máximo {EXCEL_MAX_SIZE_MB} MB).",
        error_messages={
            "required": "Debe seleccionar un archivo Excel.",
        },
        widget=forms.ClearableFileInput(attrs={
            "class": "form-control",
            "accept": ".xlsx,.xlsm,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }),
    )

    def clean_excel_file(self):
        excel_file = self.cleaned_data["excel_file"]

        extension = os.path.splitext(excel_file.name)[1].lower()
        if extension not in EXCEL_ALLOWED_EXTENSIONS:
            raise forms.ValidationError("Solo se permiten archivos Excel (.xlsx o .xlsm).")

        if excel_file.size > EXCEL_MAX_SIZE_MB * 1024 * 1024:
            raise forms.ValidationError(f"El archivo supera el tamaño máximo de {EXCEL_MAX_SIZE_MB} MB.")

        return excel_file


class AdminExcelUploadForm(ExcelUploadForm):
    """
    Formulario para que el administrador suba un Excel a nombre de un docente.
    """

    teacher = forms.ModelChoiceField(
        queryset=get_user_model().objects.filter(is_active=True).order_by("first_name", "last_name"),
        label="Docente",
        empty_label="Seleccione un docente",
        help_text="La plantilla se creará a nombre de este docente.",
        error_messages={
            "required": "Debe seleccionar un docente.",
            "invalid_choice": "El docente seleccionado no es válido.",
        },
    )

    field_order = ["teacher", "excel_file"]
