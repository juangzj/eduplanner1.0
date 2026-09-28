from django.urls import path

from ..views.prompt_views import (
    prompt_create_view,
    prompt_delete_view,
    prompt_detail_view,
    prompt_excel_upload_view,
    prompt_list_view,
)

urlpatterns = [
    path("prompt/create/", prompt_create_view, name="prompt-create"),
    path("prompt/create/excel/", prompt_excel_upload_view, name="prompt-excel-upload"),
    path("prompt/list/", prompt_list_view, name="prompt-list"),
    path("prompt/<int:prompt_id>/delete/", prompt_delete_view, name="prompt-delete"),
    path("prompt/<int:prompt_id>/", prompt_detail_view, name="prompt-detail"),
]
