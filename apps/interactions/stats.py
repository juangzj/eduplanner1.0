"""
Módulo de estadísticas para la app de interactions.
Proporciona funciones para obtener datos agregados sobre likes y comentarios.
"""

from django.db.models import Count

from .models.generated_class_like import GeneratedClassLike
from .models.generated_class_comment import GeneratedClassComment


def get_generated_class_like_stats():
    """Retorna estadísticas sobre likes en clases generadas"""
    try:
        total = GeneratedClassLike.objects.count()
        
        top_classes = (
            GeneratedClassLike.objects
            .values(
                'generated_class__id',
                'generated_class__class_planning__topic'
            )
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        
        return {
            'total': total,
            'top_liked_classes': list(top_classes),
        }
    except Exception:
        return {
            'total': 0,
            'top_liked_classes': [],
        }


def get_generated_class_comment_stats():
    """Retorna estadísticas sobre comentarios en clases generadas"""
    try:
        total = GeneratedClassComment.objects.count()
        active = GeneratedClassComment.objects.filter(is_active=True).count()
        
        top_commented_classes = (
            GeneratedClassComment.objects
            .values(
                'generated_class__id',
                'generated_class__class_planning__topic'
            )
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        
        return {
            'total': total,
            'active': active,
            'top_commented_classes': list(top_commented_classes),
        }
    except Exception:
        return {
            'total': 0,
            'active': 0,
            'top_commented_classes': [],
        }


def get_all_interaction_stats():
    """Retorna todas las estadísticas de la app interactions"""
    return {
        'likes': get_generated_class_like_stats(),
        'comments': get_generated_class_comment_stats(),
    }
