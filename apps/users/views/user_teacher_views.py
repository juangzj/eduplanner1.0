from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..forms import TeacherProfileForm, TeacherRegisterForm
from ..services import register_teacher_service, update_teacher_profile_service

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


@login_required(login_url='/users/login/')
def profile_settings_view(request):
    if request.method == 'POST':
        form = TeacherProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            try:
                update_teacher_profile_service(user=request.user, form=form)
                messages.success(request, 'Tu perfil fue actualizado correctamente.')
                return redirect('users:profile-settings')

            except ValueError as e:
                messages.error(request, str(e))
            except Exception:
                messages.error(request, 'Ocurrió un error inesperado al actualizar tu perfil.')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')

    else:
        form = TeacherProfileForm(instance=request.user)

    return render(request, 'users/profile_settings.html', {'form': form})