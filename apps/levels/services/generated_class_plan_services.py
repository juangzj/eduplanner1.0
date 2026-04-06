from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from ..models import GeneratedClassPlan


class GeneratedClassPlanUpdateService:

    @staticmethod
    @transaction.atomic
    def update_generated_class_plan_service(*, form, generated_class_plan: GeneratedClassPlan, user) -> GeneratedClassPlan:
        if generated_class_plan.class_planning.user_id != user.id:
            raise PermissionError("User does not own this generated class plan record.")

        if generated_class_plan.deleted_at is not None:
            raise ValueError("Generated class plan is not available.")

        if generated_class_plan.class_planning.deleted_at is not None:
            raise ValueError("Related class planning is not available.")

        updated_plan = form.save(commit=False)
        updated_plan.save()
        return updated_plan


class GeneratedClassPlanDeleteService:

    @staticmethod
    @transaction.atomic
    def soft_delete_generated_class_plan_service(*, generated_class_plan: GeneratedClassPlan, user) -> bool:
        if generated_class_plan.class_planning.user_id != user.id:
            raise PermissionError("User does not own this generated class plan record.")

        if generated_class_plan.deleted_at is not None:
            return False

        if generated_class_plan.class_planning.deleted_at is not None:
            raise ValueError("Related class planning is not available.")

        generated_class_plan.deleted_at = timezone.now()
        generated_class_plan.save(update_fields=["deleted_at", "updated_at"])
        return True