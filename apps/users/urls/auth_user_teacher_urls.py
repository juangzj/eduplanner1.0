from django.urls import path
from ..views.auth_user_teacher_views import login_view, dashboard_view, logout_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard' )
]