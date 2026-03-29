from django.urls import path
from ..views.generated_levels_views import GeneratedLevelsCreateView, GeneratedLevelsUpdateView

urlpatterns = [
    path(
        "generated-levels/create/",
        GeneratedLevelsCreateView.as_view(),
        name="generated-levels-create"
    ),
    path(
        "generated-levels/<uuid:pk>/edit/",
        GeneratedLevelsUpdateView.as_view(),
        name="generated-levels-edit",
    ),
]