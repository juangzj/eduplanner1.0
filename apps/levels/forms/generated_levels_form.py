import uuid

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
        selected_template_id = kwargs.pop("selected_template_id", None)
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
        self.selected_template = None

        if not selected_template_id:
            return

        try:
            parsed_template_id = uuid.UUID(str(selected_template_id))
        except (TypeError, ValueError):
            return

        locked_template = qs.filter(id=parsed_template_id).first()
        if locked_template is None:
            return

        self.fields["performance_template"].queryset = qs.filter(id=locked_template.id)
        self.initial["performance_template"] = locked_template.id
        self.fields["performance_template"].widget = forms.HiddenInput()
        self.selected_template = locked_template

    def clean_performance_template(self):
        template = self.cleaned_data["performance_template"]
        if template.deleted_at is not None:
            raise forms.ValidationError("La plantilla seleccionada no está disponible.")
        if GeneratedLevels.objects.filter(performance_template=template).exists():
            raise forms.ValidationError("Esta plantilla ya tiene niveles generados.")
        return template


class GeneratedLevelsUpdateForm(forms.ModelForm):

    class Meta:
        model = GeneratedLevels
        fields = ["low_level", "basic_level", "high_level", "superior_level"]
        help_texts = {
            "low_level": "Edite la descripción del nivel bajo.",
            "basic_level": "Edite la descripción del nivel básico.",
            "high_level": "Edite la descripción del nivel alto.",
            "superior_level": "Edite la descripción del nivel superior.",
        }
        widgets = {
            "low_level": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Nivel bajo",
            }),
            "basic_level": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Nivel básico",
            }),
            "high_level": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Nivel alto",
            }),
            "superior_level": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Nivel superior",
            }),
        }