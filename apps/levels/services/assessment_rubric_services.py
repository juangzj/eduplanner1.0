from __future__ import annotations

from typing import Any

from django.db import transaction

from ..ai.factory import get_ai_client
from ..models import AssessmentRubric, GeneratedLevels


class AssessmentRubricCreateService:

    @staticmethod
    @transaction.atomic
    def create_assessment_rubric_service(*, form, user=None) -> AssessmentRubric:
        generated_levels: GeneratedLevels = form.cleaned_data["generated_levels"]

        if user is None or generated_levels.performance_template.user_id != user.id:
            raise PermissionError("User does not own this generated levels record.")

        prompt_data = AssessmentRubricCreateService._build_prompt_data(generated_levels)
        ai_client = get_ai_client()
        ai_response = ai_client.generate_assessment_content(prompt_data)

        return AssessmentRubric.objects.create(
            generated_levels=generated_levels,
            title=str(ai_response["title"]).strip(),
            rubric_description=str(ai_response["rubric_description"]).strip(),
            rubric_content=str(ai_response["rubric_content"]).strip(),
        )

    @staticmethod
    def _build_prompt_data(generated_levels: GeneratedLevels) -> dict[str, Any]:
        template = generated_levels.performance_template
        return {
            "area": template.area,
            "grade": template.get_grade_display(),
            "academic_period": template.academic_period,
            "learning": template.learning,
            "didactic_resources": template.didactic_resources,
            "learning_evidence": template.learning_evidence,
            "evaluation_criteria": template.evaluation_criteria,
            "assessment_instrument": template.assessment_instrument,
            "level_title": template.level_title,
            "level_description": template.level_description,
            "low_level": generated_levels.low_level,
            "basic_level": generated_levels.basic_level,
            "high_level": generated_levels.high_level,
            "superior_level": generated_levels.superior_level,
        }


class AssessmentRubricUpdateService:

    @staticmethod
    @transaction.atomic
    def update_assessment_rubric_service(*, form, assessment_rubric: AssessmentRubric, user) -> AssessmentRubric:
        if assessment_rubric.generated_levels.performance_template.user_id != user.id:
            raise PermissionError("User does not own this assessment rubric record.")

        if assessment_rubric.deleted_at is not None:
            raise ValueError("Assessment rubric is not available.")

        if assessment_rubric.generated_levels.deleted_at is not None:
            raise ValueError("Related generated levels are not available.")

        if assessment_rubric.generated_levels.performance_template.deleted_at is not None:
            raise ValueError("Related performance template is not available.")

        updated_assessment = form.save(commit=False)
        updated_assessment.save()
        return updated_assessment
