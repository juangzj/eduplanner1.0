"""
Módulo de estadísticas para la app de prompt_lab.
Proporciona funciones para obtener datos agregados sobre prompts.
"""

from django.db.models import Count, Avg, Max, Q
from django.utils import timezone
from datetime import timedelta

from .models.prompt_model import Prompt


def get_prompt_stats():
    """Retorna estadísticas sobre prompts"""
    total = Prompt.objects.filter(deleted_at__isnull=True).count()
    
    ai_generated = Prompt.objects.filter(
        is_ai_generated=True,
        deleted_at__isnull=True
    ).count()
    
    user_created = Prompt.objects.filter(
        is_ai_generated=False,
        deleted_at__isnull=True
    ).count()
    
    with_score = Prompt.objects.filter(
        score__isnull=False,
        deleted_at__isnull=True
    ).count()
    
    avg_score = (
        Prompt.objects
        .filter(score__isnull=False, deleted_at__isnull=True)
        .aggregate(Avg('score'))['score__avg']
    )
    
    by_teacher = (
        Prompt.objects
        .filter(deleted_at__isnull=True)
        .values('teacher__gmail', 'teacher__first_name', 'teacher__last_name')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    
    by_refinement = (
        Prompt.objects
        .filter(deleted_at__isnull=True)
        .values('refinement_number')
        .annotate(count=Count('id'))
        .order_by('refinement_number')
    )
    
    latest_7_days = Prompt.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7),
        deleted_at__isnull=True
    ).count()
    
    return {
        'total': total,
        'ai_generated': ai_generated,
        'user_created': user_created,
        'with_score': with_score,
        'avg_score': round(avg_score, 2) if avg_score else 0,
        'latest_7_days': latest_7_days,
        'top_teachers': list(by_teacher),
        'by_refinement': list(by_refinement),
    }


def get_all_prompt_stats():
    """Retorna todas las estadísticas de la app prompt_lab"""
    try:
        return {
            'prompts': get_prompt_stats(),
        }
    except Exception:
        return {
            'prompts': {
                'total': 0,
                'ai_generated': 0,
                'user_created': 0,
                'with_score': 0,
                'avg_score': 0,
                'latest_7_days': 0,
                'top_teachers': [],
                'by_refinement': [],
            },
        }
