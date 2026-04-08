from django.urls import path

from ..views.prompt_views import prompt_create_view, prompt_detail_view, prompt_list_view

urlpatterns = [
    path("prompt/create/", prompt_create_view, name="prompt-create"),
    path("prompt/list/", prompt_list_view, name="prompt-list"),
    path("prompt/<int:prompt_id>/", prompt_detail_view, name="prompt-detail"),
]
