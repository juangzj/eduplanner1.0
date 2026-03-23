from django.shortcuts import render, redirect
from django.contrib import messages
from ..forms import TeacherRegisterForm
from ..services import register_teacher_service

def register_teacher_view(request):
    if request.method == 'POST':
        form = TeacherRegisterForm(request.POST)
        if form.is_valid():
            register_teacher_service(form.cleaned_data)
            messages.success(request, "¡Registro exitoso! Ya puedes iniciar sesión.")
            return redirect('login')
    else:
        form = TeacherRegisterForm()
    
    return render(request, 'users/register_user_teacher.html', {'form': form})