"""
Módulo de estadísticas para la app de levels.
Proporciona funciones para obtener datos agregados sobre:
- Plantillas de desempeño
- Planeaciones de clase
- Clases generadas
"""

from django.db.models import Count, Q, Max, Min
from django.utils import timezone
from datetime import timedelta

from .models import (
    PerformanceLevelTemplate,
    GeneratedLevels,
    AssessmentRubric,
    ClassPlanning,
    GeneratedClassPlan,
)


def get_performance_levels_stats():
    """Retorna estadísticas de niveles de desempeño"""
    total = PerformanceLevelTemplate.objects.filter(deleted_at__isnull=True).count()
    
    by_area = (
        PerformanceLevelTemplate.objects
        .filter(deleted_at__isnull=True)
        .values('area')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    
    by_grade = (
        PerformanceLevelTemplate.objects
        .filter(deleted_at__isnull=True)
        .values('grade')
        .annotate(count=Count('id'))
        .order_by('grade')
    )
    
    by_period = (
        PerformanceLevelTemplate.objects
        .filter(deleted_at__isnull=True)
        .values('academic_period')
        .annotate(count=Count('id'))
        .order_by('academic_period')
    )
    
    return {
        'total': total,
        'by_area': list(by_area),
        'by_grade': list(by_grade),
        'by_period': list(by_period),
    }


def get_class_planning_stats():
    """Retorna estadísticas de planeaciones de clase"""
    total = ClassPlanning.objects.filter(deleted_at__isnull=True).count()
    
    by_user = (
        ClassPlanning.objects
        .filter(deleted_at__isnull=True)
        .values('user__gmail', 'user__first_name', 'user__last_name')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    
    latest_7_days = ClassPlanning.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7),
        deleted_at__isnull=True
    ).count()
    
    return {
        'total': total,
        'latest_7_days': latest_7_days,
        'top_teachers': list(by_user),
    }


def get_generated_class_stats():
    """Retorna estadísticas de clases generadas"""
    total = GeneratedClassPlan.objects.filter(deleted_at__isnull=True).count()
    
    by_model = (
        GeneratedClassPlan.objects
        .filter(deleted_at__isnull=True)
        .values('ai_model')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    
    by_month = (
        GeneratedClassPlan.objects
        .filter(deleted_at__isnull=True)
        .extra(select={'month': 'DATE_TRUNC(\'month\', created_at)'})
        .values('month')
        .annotate(count=Count('id'))
        .order_by('-month')[:12]
    )
    
    latest_7_days = GeneratedClassPlan.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7),
        deleted_at__isnull=True
    ).count()
    
    return {
        'total': total,
        'latest_7_days': latest_7_days,
        'by_ai_model': list(by_model),
        'recent_months': list(by_month),
    }


def get_generated_levels_stats():
    """Retorna estadísticas de niveles generados"""
    total = GeneratedLevels.objects.filter(deleted_at__isnull=True).count()
    
    return {
        'total': total,
    }


def get_assessment_rubric_stats():
    """Retorna estadísticas de rúbricas de evaluación"""
    total = AssessmentRubric.objects.filter(deleted_at__isnull=True).count()
    
    return {
        'total': total,
    }


def get_all_levels_stats():
    """Retorna todas las estadísticas de la app levels"""
    try:
        return {
            'performance_levels': get_performance_levels_stats(),
            'class_planning': get_class_planning_stats(),
            'generated_classes': get_generated_class_stats(),
            'generated_levels': get_generated_levels_stats(),
            'assessment_rubrics': get_assessment_rubric_stats(),
        }
    except Exception:
        return {
            'performance_levels': {'total': 0, 'by_area': [], 'by_grade': [], 'by_period': []},
            'class_planning': {'total': 0, 'latest_7_days': 0, 'top_teachers': []},
            'generated_classes': {'total': 0, 'latest_7_days': 0, 'by_ai_model': [], 'recent_months': []},
            'generated_levels': {'total': 0},
            'assessment_rubrics': {'total': 0},
        }
