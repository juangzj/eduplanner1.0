from django.urls import path
from ..views.auth_user_teacher_views import login_view

urlpatterns = [
    path('login/', login_view, name='login'),
]