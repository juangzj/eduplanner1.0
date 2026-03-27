from django.urls import path
from ..views.generated_levels_views import GeneratedLevelsCreateView 

urlpatterns = [
    path(
        "generated-levels/create/",
        GeneratedLevelsCreateView.as_view(),
        name="generated-levels-create"
    ),
]