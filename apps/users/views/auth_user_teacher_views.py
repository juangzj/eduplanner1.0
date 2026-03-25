from django.shortcuts import render, redirect
from ..forms import TeacherLoginForm
from ..services.auth_user_teacher_services import login_teacher_service
from django.contrib.auth.decorators import login_required


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


def logout(request):
    return render(request, 'landing/index.html')


@login_required()
def dashboard_view(request):
    return render (request, 'pages/dashboard.html')



