from django.shortcuts import render, redirect
from django.contrib import messages
from ..forms import  TeacherLoginForm
from ..services import  login_teacher_service

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = TeacherLoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = login_teacher_service(
                request, 
                gmail=form.cleaned_data['gmail'], 
                password=form.cleaned_data['password']
            )
            if user:
                return redirect('home')
            else:
                messages.error(request, "Correo o contraseña no válidos.")
                
    return render(request, 'auth/login.html', {'form': form})