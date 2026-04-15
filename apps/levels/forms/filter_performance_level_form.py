from django import forms
from ..models.performance_level_template_model import GRADOS_OPCIONES, AREAS_OPCIONES, PERIODO_ACADEMICO_OPCIONES


class PerformanceLevelFilterForm(forms.Form):

    area = forms.ChoiceField(
        choices=[('', 'Todas las áreas')] + AREAS_OPCIONES,
        required=False,
        label="Área",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    grade = forms.ChoiceField(
        choices=[('', 'Todos los grados')] + GRADOS_OPCIONES,
        required=False,
        label="Grado",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    academic_period = forms.ChoiceField(
        choices=[('', 'Todos los periodos')] + PERIODO_ACADEMICO_OPCIONES,
        required=False,
        label="Periodo académico",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    search = forms.CharField(
        required=False,
        label="Buscar",
        widget=forms.TextInput(attrs={
            'placeholder': 'Buscar por título, aprendizaje, recursos o evidencias...',
            'class': 'form-control'
        })
    )