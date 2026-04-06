from django.urls import path

from ..views.generated_class_plan_views import (
    GeneratedClassPlanDeleteView,
    GeneratedClassPlanUpdateView,
)


urlpatterns = [
    path(
        "generated-class-plans/<uuid:pk>/edit/",
        GeneratedClassPlanUpdateView.as_view(),
        name="generated-class-plan-edit",
    ),
    path(
        "generated-class-plans/<uuid:pk>/delete/",
        GeneratedClassPlanDeleteView.as_view(),
        name="generated-class-plan-delete",
    ),
]