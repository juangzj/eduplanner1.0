from __future__ import annotations

from typing import Any

from django.db import transaction

from ..ai.factory import get_ai_client
from ..models import ClassPlanning, GeneratedClassPlan, PerformanceLevelTemplate


class ClassPlanningCreateService:

	@staticmethod
	@transaction.atomic
	def create_class_planning_service(*, form, user=None) -> ClassPlanning:
		template: PerformanceLevelTemplate = form.cleaned_data["performance_template"]

		if user is None or template.user_id != user.id:
			raise PermissionError("User does not own this performance template record.")

		prompt_data = ClassPlanningCreateService._build_prompt_data(form.cleaned_data)
		ai_client = get_ai_client()
		ai_response = ai_client.generate_class_planning_content(prompt_data)

		class_planning = ClassPlanning.objects.create(
			user=user,
			performance_template=template,
			generated_levels=template.generated_levels,
			assessment_rubric=template.generated_levels.assessment_rubric,
			topic=str(form.cleaned_data["topic"]).strip(),
			subtopic=str(form.cleaned_data.get("subtopic") or "").strip() or None,
			class_objective=str(form.cleaned_data["class_objective"]).strip(),
			duration_minutes=form.cleaned_data["duration_minutes"],
			prompt=str(form.cleaned_data["prompt"]).strip(),
			methodology=str(form.cleaned_data.get("methodology") or "").strip() or None,
			resources=str(form.cleaned_data.get("resources") or "").strip() or None,
		)

		GeneratedClassPlan.objects.create(
			class_planning=class_planning,
			generated_content=str(ai_response["generated_content"]).strip(),
			ai_model=getattr(ai_client, "model", None),
		)

		return class_planning

	@staticmethod
	def _build_prompt_data(cleaned_data: dict[str, Any]) -> dict[str, Any]:
		template: PerformanceLevelTemplate = cleaned_data["performance_template"]
		generated_levels = template.generated_levels
		assessment_rubric = generated_levels.assessment_rubric

		return {
			"area": template.area,
			"grade": template.get_grade_display(),
			"academic_period": template.academic_period,
			"competency": template.competency,
			"statement": template.statement,
			"learning_evidence": template.learning_evidence,
			"level_title": template.level_title,
			"level_description": template.level_description,
			"low_level": generated_levels.low_level,
			"basic_level": generated_levels.basic_level,
			"high_level": generated_levels.high_level,
			"superior_level": generated_levels.superior_level,
			"rubric_title": assessment_rubric.title,
			"rubric_description": assessment_rubric.rubric_description,
			"rubric_content": assessment_rubric.rubric_content,
			"topic": cleaned_data.get("topic"),
			"subtopic": cleaned_data.get("subtopic"),
			"class_objective": cleaned_data.get("class_objective"),
			"duration_minutes": cleaned_data.get("duration_minutes"),
			"methodology": cleaned_data.get("methodology"),
			"resources": cleaned_data.get("resources"),
			"prompt": cleaned_data.get("prompt"),
		}
