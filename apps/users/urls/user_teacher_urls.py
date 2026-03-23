from django.urls import path
from ..views.user_teacher_views import register_teacher_view

urlpatterns = [
    path('register-teacher/', register_teacher_view, name='register_teacher'),
]