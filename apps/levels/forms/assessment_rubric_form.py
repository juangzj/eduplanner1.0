from django import forms

from ..models import AssessmentRubric, GeneratedLevels


class AssessmentRubricCreateForm(forms.ModelForm):

    class Meta:
        model = AssessmentRubric
        fields = ["generated_levels"]
        help_texts = {
            "generated_levels": "Seleccione los niveles generados sobre los cuales desea crear la rúbrica.",
        }
        error_messages = {
            "generated_levels": {
                "required": "Debe seleccionar niveles generados para continuar.",
            },
        }
        widgets = {
            "generated_levels": forms.Select(attrs={
                "class": "form-select",
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user is None or not getattr(user, "is_authenticated", False):
            queryset = GeneratedLevels.objects.none()
        else:
            queryset = (
                GeneratedLevels.objects.filter(
                    performance_template__user=user,
                    performance_template__deleted_at__isnull=True,
                    deleted_at__isnull=True,
                    assessment_rubric__isnull=True,
                )
                .select_related("performance_template")
                .order_by("-created_at")
            )

        self.fields["generated_levels"].queryset = queryset

    def clean_generated_levels(self):
        generated_levels = self.cleaned_data["generated_levels"]

        if generated_levels.deleted_at is not None:
            raise forms.ValidationError("Los niveles generados seleccionados no están disponibles.")

        if generated_levels.performance_template.deleted_at is not None:
            raise forms.ValidationError("La plantilla asociada no está disponible.")

        if AssessmentRubric.objects.filter(generated_levels=generated_levels).exists():
            raise forms.ValidationError("Estos niveles ya tienen una rúbrica de evaluación.")

        return generated_levels


class AssessmentRubricUpdateForm(forms.ModelForm):

    class Meta:
        model = AssessmentRubric
        fields = ["title", "rubric_description", "rubric_content"]
        help_texts = {
            "title": "Edite el título de la rúbrica.",
            "rubric_description": "Edite la descripción general de la rúbrica.",
            "rubric_content": "Edite el contenido detallado de la rúbrica.",
        }
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Título de la rúbrica",
            }),
            "rubric_description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Descripción de la rúbrica",
            }),
            "rubric_content": forms.Textarea(attrs={
                "class": "form-control font-monospace",
                "rows": 14,
                "placeholder": "| Criterio | Nivel Bajo | Nivel Basico | Nivel Alto | Nivel Superior |\n|---|---|---|---|---|\n| ... | ... | ... | ... | ... |",
            }),
        }
