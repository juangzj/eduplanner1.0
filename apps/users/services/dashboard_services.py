from django.db.models import Q

from apps.levels.models import AssessmentRubric, ClassPlanning, PerformanceLevelTemplate
from apps.prompt_lab.models import Prompt


def get_dashboard_data(user):
    prompt_count = Prompt.objects.filter(
        teacher=user,
        parent_prompt__isnull=True,
        deleted_at__isnull=True,
    ).count()

    class_planning_count = ClassPlanning.objects.filter(
        user=user,
        deleted_at__isnull=True,
    ).count()

    template_count = PerformanceLevelTemplate.objects.filter(
        user=user,
        deleted_at__isnull=True,
    ).count()

    rubric_count = AssessmentRubric.objects.filter(
        generated_levels__performance_template__user=user,
        generated_levels__performance_template__deleted_at__isnull=True,
        generated_levels__deleted_at__isnull=True,
        deleted_at__isnull=True,
    ).count()

    average_prompt_score = (
        Prompt.objects.filter(
            teacher=user,
            parent_prompt__isnull=True,
            deleted_at__isnull=True,
            score__isnull=False,
        )
        .order_by()
        .values_list("score", flat=True)
    )

    score_value = 0.0
    score_count = len(average_prompt_score)
    if score_count > 0:
        score_value = round(sum(average_prompt_score) / score_count, 1)

    recent_prompt_items = list(
        Prompt.objects.filter(
            teacher=user,
            deleted_at__isnull=True,
        )
        .order_by("-created_at")
        .values("id", "purpose", "created_at")[:4]
    )

    recent_planning_items = list(
        ClassPlanning.objects.filter(
            user=user,
            deleted_at__isnull=True,
        )
        .order_by("-created_at")
        .values("id", "topic", "created_at")[:4]
    )

    activities = []

    for item in recent_prompt_items:
        activities.append(
            {
                "title": "Prompt actualizado en Prompt Lab",
                "description": item["purpose"][:90],
                "created_at": item["created_at"],
                "icon": "bi-chat-square-text",
                "color": "primary",
                "url": f"/prompt/{item['id']}/",
            }
        )

    for item in recent_planning_items:
        activities.append(
            {
                "title": "Planeacion creada",
                "description": item["topic"][:90],
                "created_at": item["created_at"],
                "icon": "bi-journal-text",
                "color": "success",
                "url": "/levels/class-plans/",
            }
        )

    activities.sort(key=lambda record: record["created_at"], reverse=True)
    activities = activities[:6]

    return {
        "teacher_display_name": user.first_name or "Docente",
        "stats": {
            "prompt_count": prompt_count,
            "class_planning_count": class_planning_count,
            "template_count": template_count,
            "rubric_count": rubric_count,
            "average_prompt_score": score_value,
            "average_prompt_score_has_data": score_count > 0,
        },
        "activities": activities,
    }
