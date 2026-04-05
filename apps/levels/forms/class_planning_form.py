from django import forms
from django.core.exceptions import ObjectDoesNotExist

from ..models import ClassPlanning, PerformanceLevelTemplate


class ClassPlanningCreateForm(forms.ModelForm):

	class Meta:
		model = ClassPlanning
		fields = [
			"performance_template",
			"topic",
			"subtopic",
			"class_objective",
			"duration_minutes",
			"prompt",
			"methodology",
			"resources",
		]
		help_texts = {
			"performance_template": "Seleccione la plantilla de desempeño base para generar la planeación.",
			"topic": "Tema principal de la clase.",
			"subtopic": "Subtema o enfoque específico.",
			"class_objective": "Objetivo pedagógico de la sesión.",
			"duration_minutes": "Duración estimada de la clase en minutos.",
			"prompt": "Indicación docente que orienta la generación de la planeación.",
			"methodology": "Metodología sugerida para el desarrollo de la clase.",
			"resources": "Recursos o materiales necesarios.",
		}
		error_messages = {
			"performance_template": {"required": "Debe seleccionar una plantilla de desempeño."},
			"topic": {"required": "Debe indicar el tema de la clase."},
			"class_objective": {"required": "Debe indicar el objetivo de la clase."},
			"duration_minutes": {"required": "Debe indicar la duración de la clase."},
			"prompt": {"required": "Debe escribir el prompt del docente."},
		}
		widgets = {
			"performance_template": forms.Select(attrs={"class": "form-select"}),
			"topic": forms.TextInput(attrs={"class": "form-control", "placeholder": "Tema de la clase"}),
			"subtopic": forms.TextInput(attrs={"class": "form-control", "placeholder": "Subtema opcional"}),
			"class_objective": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Objetivo de la clase"}),
			"duration_minutes": forms.NumberInput(attrs={"class": "form-control", "min": 1, "placeholder": "Duración en minutos"}),
			"prompt": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Prompt del docente para generar la planeación"}),
			"methodology": forms.TextInput(attrs={"class": "form-control", "placeholder": "Metodología"}),
			"resources": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Recursos y materiales"}),
		}

	def __init__(self, *args, **kwargs):
		user = kwargs.pop("user", None)
		super().__init__(*args, **kwargs)

		if user is None or not getattr(user, "is_authenticated", False):
			queryset = PerformanceLevelTemplate.objects.none()
		else:
			queryset = (
				PerformanceLevelTemplate.objects.filter(
					user=user,
					deleted_at__isnull=True,
					generated_levels__isnull=False,
					generated_levels__deleted_at__isnull=True,
					generated_levels__assessment_rubric__isnull=False,
					generated_levels__assessment_rubric__deleted_at__isnull=True,
				)
				.select_related("generated_levels", "generated_levels__assessment_rubric")
				.order_by("-created_at")
			)

		self.fields["performance_template"].queryset = queryset

		selected_template_id = self.initial.get("performance_template") or self.data.get("performance_template")
		self.selected_template = None

		if selected_template_id:
			try:
				self.selected_template = queryset.get(id=selected_template_id)
				self.fields["performance_template"].widget = forms.HiddenInput()
			except (PerformanceLevelTemplate.DoesNotExist, ObjectDoesNotExist):
				self.selected_template = None

	def clean_performance_template(self):
		template = self.cleaned_data["performance_template"]

		if template.deleted_at is not None:
			raise forms.ValidationError("La plantilla seleccionada no está disponible.")

		try:
			generated_levels = template.generated_levels
		except ObjectDoesNotExist:
			generated_levels = None

		if generated_levels is None or generated_levels.deleted_at is not None:
			raise forms.ValidationError("La plantilla no tiene niveles generados disponibles.")

		try:
			assessment_rubric = generated_levels.assessment_rubric
		except ObjectDoesNotExist:
			assessment_rubric = None

		if assessment_rubric is None or assessment_rubric.deleted_at is not None:
			raise forms.ValidationError("La plantilla no tiene rúbrica disponible.")

		return template
