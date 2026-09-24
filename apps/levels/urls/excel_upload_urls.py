from django.urls import path

from ..views.excel_upload_views import excel_upload_view


urlpatterns = [
    path("excel-upload/", excel_upload_view, name="excel-upload"),
]
