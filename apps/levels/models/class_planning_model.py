from django.db import models
from django.conf import settings
import uuid


class ClassPlanning(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # -------------------------
    # RELACIONES
    # -------------------------

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="class_plannings",
        verbose_name="Usuario Docente"
    )

    performance_template = models.ForeignKey(
        'PerformanceLevelTemplate',
        on_delete=models.CASCADE,
        related_name="class_plannings",
        verbose_name="Plantilla de Desempeño"
    )

    generated_levels = models.ForeignKey(
        'GeneratedLevels',
        on_delete=models.CASCADE,
        related_name="class_plannings",
        verbose_name="Niveles Generados"
    )

    assessment_rubric = models.ForeignKey(
        'AssessmentRubric',
        on_delete=models.CASCADE,
        related_name="class_plannings",
        verbose_name="Rúbrica de Evaluación"
    )

    # -------------------------
    # CONTEXTO PEDAGÓGICO
    # -------------------------

    topic = models.CharField(
        max_length=255,
        verbose_name="Tema"
    )

    subtopic = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Subtema"
    )

    class_objective = models.TextField(
        verbose_name="Objetivo de la Clase"
    )

    duration_minutes = models.IntegerField(
        verbose_name="Duración (minutos)"
    )

    # -------------------------
    # INPUT IA
    # -------------------------

    prompt = models.TextField(
        verbose_name="Prompt del Docente"
    )

    # -------------------------
    # CONFIGURACIÓN DIDÁCTICA
    # -------------------------

    methodology = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Metodología"
    )

    resources = models.TextField(
        blank=True,
        null=True,
        verbose_name="Recursos"
    )

    # -------------------------
    # AUDITORÍA
    # -------------------------

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
        db_table = "class_plannings"
        verbose_name = "Planeación de Clase"
        verbose_name_plural = "Planeaciones de Clase"

    def __str__(self):
        return f"{self.topic} - {self.performance_template.area}"