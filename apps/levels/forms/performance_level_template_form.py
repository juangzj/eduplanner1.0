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
            "learning": "Aprendizaje esperado para la unidad o clase.",
            "didactic_resources": (
                "Puede incluir como guía: recursos didácticos, materiales y actividades pedagógicas. "
                "Esta información va dentro del campo de recursos didácticos."
            ),
            "learning_evidence": "Evidencias de aprendizaje.",
            "evaluation_criteria": (
                "Puede incluir como guía: qué se evalúa, cuándo se evalúa y cómo se evalúa. "
                "Esta información va dentro del mismo campo."
            ),
            "assessment_instrument": "Instrumento de evaluación sugerido (rúbrica, lista de chequeo, etc.).",
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
            "learning": {
                "required": "Debe escribir el aprendizaje.",
            },
            "didactic_resources": {
                "required": "Debe escribir los recursos didácticos.",
            },
            "learning_evidence": {
                "required": "Debe escribir las evidencias de aprendizaje.",
            },
            "evaluation_criteria": {
                "required": "Debe escribir los criterios de evaluación.",
            },
            "assessment_instrument": {
                "required": "Debe escribir el instrumento de evaluación.",
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

            "learning": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Aprendizaje"
            }),

            "didactic_resources": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Recursos didácticos"
            }),

            "learning_evidence": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Evidencias de aprendizaje"
            }),

            "evaluation_criteria": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Criterios de evaluación"
            }),

            "assessment_instrument": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Instrumento de evaluación"
            }),

            # PERIODO ACADÉMICO COMO SELECT
            "academic_period": forms.Select(attrs={
                "class": "form-select"
            }),
        }