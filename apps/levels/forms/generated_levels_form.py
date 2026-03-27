from django import forms

from ..models import GeneratedLevels, PerformanceLevelTemplate


class GeneratedLevelsCreateForm(forms.ModelForm):

    class Meta:
        model = GeneratedLevels

        # Campos que NO deben mostrarse en el formulario
        exclude = [
            "id",            # UUID automático
            "created_at",
            "updated_at",
            "deleted_at",
        ]

        # ---------------- HELP TEXTS ----------------
        help_texts = {
            "performance_template": "Seleccione la plantilla de desempeño a la que pertenecen estos niveles.",
            "low_level": "Descripción del nivel bajo.",
            "basic_level": "Descripción del nivel básico.",
            "high_level": "Descripción del nivel alto.",
            "superior_level": "Descripción del nivel superior.",
        }

        # ---------------- ERROR MESSAGES ----------------
        error_messages = {
            "performance_template": {
                "required": "Debe seleccionar una plantilla de desempeño.",
            },
            "low_level": {
                "required": "Debe escribir el nivel bajo.",
            },
            "basic_level": {
                "required": "Debe escribir el nivel básico.",
            },
            "high_level": {
                "required": "Debe escribir el nivel alto.",
            },
            "superior_level": {
                "required": "Debe escribir el nivel superior.",
            },
        }

        # ---------------- WIDGETS ----------------
        widgets = {

            # RELACIÓN (SELECT)
            "performance_template": forms.Select(attrs={
                "class": "form-select"
            }),

            # NIVELES
            "low_level": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Nivel bajo"
            }),

            "basic_level": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Nivel básico"
            }),

            "high_level": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Nivel alto"
            }),

            "superior_level": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Nivel superior"
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user is None or not getattr(user, "is_authenticated", False):
            qs = PerformanceLevelTemplate.objects.none()
        else:
            qs = (
                PerformanceLevelTemplate.objects.filter(
                    user=user,
                    deleted_at__isnull=True,
                    generated_levels__isnull=True,
                )
                .order_by("-created_at")
            )
        self.fields["performance_template"].queryset = qs

    def clean_performance_template(self):
        template = self.cleaned_data["performance_template"]
        if template.deleted_at is not None:
            raise forms.ValidationError("La plantilla seleccionada no está disponible.")
        if GeneratedLevels.objects.filter(performance_template=template).exists():
            raise forms.ValidationError("Esta plantilla ya tiene niveles generados.")
        return template