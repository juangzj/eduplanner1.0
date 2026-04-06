from django import forms

from ..models import GeneratedClassPlan


class GeneratedClassPlanUpdateForm(forms.ModelForm):

    class Meta:
        model = GeneratedClassPlan
        fields = ["generated_content"]
        help_texts = {
            "generated_content": "Edite el contenido generado. Se guardará en Markdown desde un editor visual.",
        }
        widgets = {
            "generated_content": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 18,
                "placeholder": "Contenido generado por IA",
            }),
        }