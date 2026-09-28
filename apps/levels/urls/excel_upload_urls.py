from django.urls import path

from ..views.excel_upload_views import class_planning_excel_upload_view, excel_upload_view


urlpatterns = [
    path("excel-upload/", excel_upload_view, name="excel-upload"),
    path("class-plans/create/excel/", class_planning_excel_upload_view, name="class-planning-excel-upload"),
]
