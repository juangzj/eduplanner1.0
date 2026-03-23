from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from ..forms import TeacherLoginForm

def login_view(request):
    form = TeacherLoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            gmail = form.cleaned_data.get('gmail')
            password = form.cleaned_data.get('password')
            user = authenticate(request, gmail=gmail, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('landing') 
            else:
                form.add_error(None, "Correo o contraseña incorrectos")

    return render(request, 'users/login.html', {'form': form})