from django.shortcuts import render, redirect
from django.contrib import messages
from ..forms import PerformanceLevelTemplateCreateForm
from ..services import create_performance_level_service


def performance_level_create_view(request):
    """
    Vista exclusiva para la creación de niveles de desempeño.
    """

    form = PerformanceLevelTemplateCreateForm(request.POST or None)

    if request.method == 'POST':

        if form.is_valid():
            try:
                # Se envía el formulario + el usuario autenticado
                create_performance_level_service(form, request.user)

                messages.success(request, "Nivel de desempeño creado exitosamente.")
                return redirect('users:dashboard')

            except Exception as e:
                form.add_error(None, f"Error al procesar la solicitud: {str(e)}")

        else:
            messages.error(request, "Error en los datos suministrados. Verifique el formulario.")

    return render(request, 'levels/create_performance_level.html', {
        'form': form,
        'title': 'Registrar Nuevo Nivel de Desempeño'
    })