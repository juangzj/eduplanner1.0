from __future__ import annotations

from typing import Any

from django.db import transaction

from ..ai.factory import get_ai_client
from ..models import GeneratedLevels, PerformanceLevelTemplate


class GeneratedLevelsCreateService:

    @staticmethod
    @transaction.atomic
    def create_generated_levels_service(form, user=None) -> GeneratedLevels:
        """
        Generates performance levels with AI and persists them.
        """
        template: PerformanceLevelTemplate = form.cleaned_data["performance_template"]
        prompt_data = GeneratedLevelsCreateService._build_prompt_data(template)

        ai_client = get_ai_client()
        ai_response = ai_client.generate_level_content(prompt_data)

        generated_levels = GeneratedLevels.objects.create(
            performance_template=template,
            low_level=ai_response["low_level"],
            basic_level=ai_response["basic_level"],
            high_level=ai_response["high_level"],
            superior_level=ai_response["superior_level"],
        )

        template.generated_level_id = str(generated_levels.id)
        template.save(update_fields=["generated_level_id"])

        return generated_levels

    @staticmethod
    def _build_prompt_data(template: PerformanceLevelTemplate) -> dict[str, Any]:
        return {
            "area": template.area,
            "subject": template.subject,
            "grade": template.get_grade_display(),
            "academic_period": template.academic_period,
            "competency": template.competency,
            "statement": template.statement,
            "learning_evidence": template.learning_evidence,
            "level_title": template.level_title,
            "level_description": template.level_description,
        }