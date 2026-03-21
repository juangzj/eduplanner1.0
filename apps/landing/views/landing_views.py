from django.shortcuts import render
from ..services.landing_services import get_landing_data

def landing(request):
    data = get_landing_data()

    return render(request, 'landing/index.html', data)