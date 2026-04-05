from django.urls import path

from ..views.class_planning_views import class_plans_list_view


urlpatterns = [
	path("class-plans/", class_plans_list_view, name="class-plans"),
]
