from django.urls import path

from ..views.assessment_rubric_views import (
    AssessmentRubricCreateView,
    AssessmentRubricUpdateView,
)

urlpatterns = [
    path(
        "assessment-rubrics/create/",
        AssessmentRubricCreateView.as_view(),
        name="assessment-rubric-create",
    ),
    path(
        "assessment-rubrics/<uuid:pk>/edit/",
        AssessmentRubricUpdateView.as_view(),
        name="assessment-rubric-edit",
    ),
]
