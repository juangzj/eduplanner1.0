from django.urls import path
from ..views.landing_views import landing

urlpatterns = [
    path('', landing, name='landing'),
]