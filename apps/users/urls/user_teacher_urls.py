from django.urls import path
from ..views.user_teacher_views import profile_settings_view, register_teacher_view

urlpatterns = [
    path('register-teacher/', register_teacher_view, name='register_teacher'),
    path('settings/', profile_settings_view, name='profile-settings'),
]