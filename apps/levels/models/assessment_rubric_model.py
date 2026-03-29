from django.db import models
import uuid


class AssessmentRubric(models.Model):
    """
    Representa la rúbrica de evaluación asociada a los niveles generados.
    Un conjunto de niveles generados solo puede tener una rúbrica.
    """

    # 1. ID único (equivalente a id_rubricas_evaluacion)
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID de la rúbrica de evaluación"
    )

    # 2. Relación 1 a 1 con GeneratedLevels
    generated_levels = models.OneToOneField(
        'GeneratedLevels',
        on_delete=models.CASCADE,
        related_name="assessment_rubric",
        verbose_name="Niveles generados"
    )

    # 3. Campos principales
    title = models.CharField(
        max_length=255,
        verbose_name="Título de la rúbrica"
    )

    rubric_description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción de la rúbrica"
    )

    rubric_content = models.TextField(
        verbose_name="Contenido de la rúbrica"
    )

    # 4. Auditoría
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de actualización"
    )

    deleted_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Fecha de eliminación"
    )

    class Meta:
        db_table = "assessment_rubrics"
        verbose_name = "Rúbrica de evaluación"
        verbose_name_plural = "Rúbricas de evaluación"

    def __str__(self):
        return self.title