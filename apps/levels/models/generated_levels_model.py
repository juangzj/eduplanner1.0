from django.db import models
import uuid

class GeneratedLevels(models.Model):
    """
    Representa los niveles de desempeño específicos (Bajo, Básico, Alto, Superior)
    generados para una propuesta didáctica o plantilla de desempeño.
    """
    
    # 1. ID generado automáticamente (UUID)
    # Atributo: id (Inglés) | Mensaje: ID Niveles Generados (Español)
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID Niveles Generados"
    )

    # 2. Relación: Un PerformanceLevelTemplate tiene solo un GeneratedLevel
    # Atributo: performance_template (Inglés) | Mensaje: Plantilla de Desempeño (Español)
    performance_template = models.OneToOneField(
        'PerformanceLevelTemplate',
        on_delete=models.CASCADE,
        related_name="generated_levels",
        verbose_name="Plantilla de Desempeño"
    )

    # 3. Campos de niveles
    low_level = models.TextField(verbose_name="Nivel Bajo")
    basic_level = models.TextField(verbose_name="Nivel Básico")
    high_level = models.TextField(verbose_name="Nivel Alto")
    superior_level = models.TextField(verbose_name="Nivel Superior")

    # 4. Auditoría
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="Fecha de Actualización"
    )
    deleted_at = models.DateTimeField(
        blank=True, 
        null=True, 
        verbose_name="Fecha de Eliminación"
    )

    class Meta:
        db_table = "generated_levels" # Nombre de tabla en inglés
        verbose_name = "Nivel Generado"
        verbose_name_plural = "Niveles Generados"

    def __str__(self):
        return f"Niveles para: {self.performance_template.level_title}"