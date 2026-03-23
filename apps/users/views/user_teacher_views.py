from django.shortcuts import render, redirect
from django.contrib import messages
from ..forms import TeacherRegisterForm
from ..services import register_teacher_service

def register_teacher_view(request):
    """Vista para el registro de nuevos docentes."""
    
    if request.method == 'POST':
        form = TeacherRegisterForm(request.POST)
        
        if form.is_valid():
            try:
                # El servicio procesa la lógica y guarda en la base de datos
                register_teacher_service(form.cleaned_data)
                
                messages.success(request, "¡Registro exitoso! Ya puedes iniciar sesión.")
                return redirect('users:login')
                
            except ValueError as e:
                # Maneja errores de lógica de negocio (ej: correo duplicado)
                messages.error(request, str(e))
            
            except Exception:
                # Maneja errores técnicos inesperados de forma silenciosa para el usuario
                messages.error(request, "Ocurrió un error inesperado al procesar su registro. Por favor, intente más tarde.")
        else:
            # Si el formulario no pasa la validación (campos vacíos, formato inválido, etc.)
            messages.error(request, "Por favor corrija los errores marcados en el formulario.")
            
    else:
        form = TeacherRegisterForm()
    
    return render(request, 'users/register_user_teacher.html', {'form': form})