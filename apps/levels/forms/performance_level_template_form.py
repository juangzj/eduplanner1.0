from django import forms
from ..models import PerformanceLevelTemplate


class PerformanceLevelTemplateCreateForm(forms.ModelForm):

    class Meta:
        model = PerformanceLevelTemplate

        # Quitamos completamente los campos que no deben aparecer en el formulario
        exclude = [
            "id",                 # UUID automático
            "generated_level_id", # se genera internamente
            "user",               # se asigna desde la vista
            "created_at",
            "updated_at",
            "deleted_at",
        ]

        # ---------------- HELP TEXTS ----------------
        help_texts = {
            "area": "Seleccione el área académica.",
            "level_title": "Título opcional del nivel de desempeño.",
            "level_description": "Descripción general del nivel.",
            "grade": "Seleccione el grado académico.",
            "subject": "Seleccione la asignatura correspondiente.",
            "competency": "Competencia que se desea evaluar.",
            "statement": "Afirmación de desempeño.",
            "learning_evidence": "Evidencia de aprendizaje esperada.",
            "academic_period": "Seleccione el periodo académico.",
        }

        # ---------------- ERROR MESSAGES ----------------
        error_messages = {
            "area": {
                "required": "Debe seleccionar el área académica.",
            },
            "grade": {
                "required": "Debe seleccionar el grado.",
            },
            "subject": {
                "required": "Debe seleccionar la asignatura.",
            },
            "competency": {
                "required": "Debe ingresar la competencia.",
            },
            "statement": {
                "required": "Debe escribir la afirmación.",
            },
            "learning_evidence": {
                "required": "Debe escribir la evidencia de aprendizaje.",
            },
            "academic_period": {
                "required": "Debe seleccionar el periodo académico.",
            },
        }

        # ---------------- WIDGETS ----------------
        widgets = {

            "area": forms.Select(attrs={
                "class": "form-select",
            }),

            "level_title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Título del nivel (opcional)"
            }),

            "level_description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Descripción del nivel"
            }),

            # GRADO COMO SELECT
            "grade": forms.Select(attrs={
                "class": "form-select"
            }),

            # ASIGNATURA COMO SELECT
            "subject": forms.Select(attrs={
                "class": "form-select"
            }),

            "competency": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Competencia"
            }),

            "statement": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Afirmación de desempeño"
            }),

            "learning_evidence": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Evidencia de aprendizaje"
            }),

            # PERIODO ACADÉMICO COMO SELECT
            "academic_period": forms.Select(attrs={
                "class": "form-select"
            }),
        }