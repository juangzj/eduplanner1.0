from django.shortcuts import render, redirect
from ..forms import TeacherLoginForm
from ..services.auth_user_teacher_services import login_teacher_service, process_logout
from ..services.dashboard_services import get_dashboard_data
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache


def login_view(request):
    form = TeacherLoginForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            gmail = form.cleaned_data.get('gmail')
            password = form.cleaned_data.get('password')

            user = login_teacher_service(request, gmail, password)

            if user is not None:
                return redirect('users:dashboard')
            else:
                form.add_error(None, "Correo o contraseña incorrectos")

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        process_logout(request)
        return redirect('landing:landing') 
    return redirect('landing:landing')

@never_cache
@login_required()
def dashboard_view(request):
    dashboard_data = get_dashboard_data(request.user)
    return render(request, 'pages/dashboard.html', dashboard_data)



