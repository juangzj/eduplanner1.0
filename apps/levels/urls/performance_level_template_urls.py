from django.urls import path
from ..views.performance_level_template_views import performance_level_create_view, levels_view

urlpatterns = [
     path('create-performance-level-template/',performance_level_create_view , name='create_performance_level'),
     path('', levels_view, name='levels'),
]