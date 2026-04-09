"""
Módulo de estadísticas para la app de users.
Proporciona funciones para obtener datos agregados sobre usuarios.
"""

from django.db.models import Count

from .models.user_teacher import TeacherUser


def get_teacher_stats():
    """Retorna estadísticas sobre usuarios docentes"""
    total = TeacherUser.objects.count()
    active = TeacherUser.objects.filter(is_active=True).count()
    inactive = TeacherUser.objects.filter(is_active=False).count()
    staff = TeacherUser.objects.filter(is_staff=True).count()
    
    return {
        'total': total,
        'active': active,
        'inactive': inactive,
        'staff': staff,
    }


def get_all_user_stats():
    """Retorna todas las estadísticas de la app users"""
    try:
        return {
            'teachers': get_teacher_stats(),
        }
    except Exception:
        return {
            'teachers': {
                'total': 0,
                'active': 0,
                'inactive': 0,
                'staff': 0,
            },
        }
