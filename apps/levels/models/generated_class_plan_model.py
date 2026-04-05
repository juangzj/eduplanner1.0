from django.db import models
import uuid


class GeneratedClassPlan(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Relación con la planeación
    class_planning = models.ForeignKey(
        'ClassPlanning',
        on_delete=models.CASCADE,
        related_name="generated_classes",
        verbose_name="Planeación de Clase"
    )

    # Contenido generado por IA
    generated_content = models.TextField(
        verbose_name="Contenido Generado"
    )

    # Información del modelo de IA (opcional pero útil)
    ai_model = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Modelo de IA"
    )

    # Auditoría (clave en este diseño)
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )

    class Meta:
        db_table = "generated_class_plans"
        verbose_name = "Clase Generada"
        verbose_name_plural = "Clases Generadas"
        ordering = ['-created_at']  # 👈 siempre trae la más reciente primero

    def __str__(self):
        return f"Clase - {self.class_planning.topic} ({self.created_at})"