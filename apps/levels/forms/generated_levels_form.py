from django import forms

from ..models import GeneratedLevels, PerformanceLevelTemplate


class GeneratedLevelsCreateForm(forms.ModelForm):

    class Meta:
        model = GeneratedLevels
        fields = ["performance_template"]

        # ---------------- HELP TEXTS ----------------
        help_texts = {
            "performance_template": "Seleccione la plantilla de desempeño a la que pertenecen estos niveles.",
        }

        # ---------------- ERROR MESSAGES ----------------
        error_messages = {
            "performance_template": {
                "required": "Debe seleccionar una plantilla de desempeño.",
            },
        }

        # ---------------- WIDGETS ----------------
        widgets = {

            # RELACIÓN (SELECT)
            "performance_template": forms.Select(attrs={
                "class": "form-select",
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