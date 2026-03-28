from django.urls import path

from ..views.performance_level_template_views import (
     levels_view,
     performance_level_create_view,
     performance_level_soft_delete_view,
)

urlpatterns = [
     path('create-performance-level-template/', performance_level_create_view, name='create_performance_level'),
     path('delete-performance-level-template/<uuid:performance_id>/', performance_level_soft_delete_view, name='delete_performance_level'),
     path('', levels_view, name='levels'),
]