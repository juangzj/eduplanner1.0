"""
Vista del dashboard administrativo con estadísticas centralizadas.
Solo accesible para administradores autenticados.
"""

from django.contrib import admin, messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from apps.levels.forms import AdminExcelUploadForm
from apps.levels.services import ExcelUploadError, ExcelUploadService
from apps.levels.stats import get_all_levels_stats
from apps.prompt_lab.stats import get_all_prompt_stats
from apps.users.stats import get_all_user_stats
from apps.interactions.stats import get_all_interaction_stats


@require_http_methods(["GET"])
@staff_member_required
def admin_dashboard(request):
    """Vista del dashboard de administración con estadísticas"""
    
    context = {
        'title': 'Panel de Estadísticas',
        'levels': get_all_levels_stats(),
        'prompts': get_all_prompt_stats(),
        'users': get_all_user_stats(),
        'interactions': get_all_interaction_stats(),
    }
    
    return render(request, 'admin/dashboard.html', context)


@require_http_methods(["GET", "POST"])
@never_cache
@staff_member_required
def admin_excel_upload(request):
    """Vista para que el administrador cargue un Excel a nombre de un docente"""

    form = AdminExcelUploadForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':

        if form.is_valid():
            teacher = form.cleaned_data['teacher']
            try:
                ExcelUploadService.create_performance_level_from_excel_service(
                    excel_file=form.cleaned_data['excel_file'],
                    user=teacher,
                )

                messages.success(request, f"Plantilla creada correctamente para {teacher}.")
                return redirect('admin_excel_upload')

            except ExcelUploadError as e:
                form.add_error('excel_file', str(e))

        messages.error(request, "No se pudo procesar el archivo. Revise los errores e intente de nuevo.")

    context = {
        **admin.site.each_context(request),
        'title': 'Cargar Excel a docente',
        'form': form,
    }

    return render(request, 'admin/excel_upload.html', context)
