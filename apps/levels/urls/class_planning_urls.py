from django.urls import path

from ..views.class_planning_views import ClassPlanningCreateView, class_plans_list_view


urlpatterns = [
	path("class-plans/create/", ClassPlanningCreateView.as_view(), name="class-planning-create"),
	path("class-plans/", class_plans_list_view, name="class-plans"),
]
