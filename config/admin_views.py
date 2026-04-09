"""
Vista del dashboard administrativo con estadísticas centralizadas.
Solo accesible para administradores autenticados.
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

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
