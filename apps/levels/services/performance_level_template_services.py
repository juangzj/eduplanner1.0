from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from ..models import PerformanceLevelTemplate


def create_performance_level_service(form, user):
    """
    Encapsula la creación de un nuevo nivel de desempeño.
    """

    performance_level = form.save(commit=False)

    # Asignar el usuario antes de guardar
    performance_level.user = user

    performance_level.save()

    return performance_level


@transaction.atomic
def soft_delete_performance_level_service(*, performance_id, user) -> bool:
    """
    Soft delete a performance template owned by the current user.
    Also soft deletes related generated levels when present.
    """
    performance = (
        PerformanceLevelTemplate.objects.select_related("generated_levels")
        .filter(
            id=performance_id,
            user=user,
            deleted_at__isnull=True,
        )
        .first()
    )

    if performance is None:
        return False

    now = timezone.now()
    performance.deleted_at = now
    performance.generated_level_id = None
    performance.save(update_fields=["deleted_at", "generated_level_id", "updated_at"])

    generated_levels = getattr(performance, "generated_levels", None)
    if generated_levels is not None and generated_levels.deleted_at is None:
        generated_levels.deleted_at = now
        generated_levels.save(update_fields=["deleted_at", "updated_at"])

    return True