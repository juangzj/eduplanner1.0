from django.db import models
from django.conf import settings
import uuid


class GeneratedClassComment(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    generated_class = models.ForeignKey(
        "GeneratedClassPlan",
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Clase generada"
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="generated_class_comments",
        verbose_name="Autor"
    )

    content = models.TextField(
        verbose_name="Contenido del comentario"
    )

    # Threads (respuestas)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies",
        verbose_name="Comentario padre"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )

    class Meta:
        db_table = "generated_class_comments"
        ordering = ["created_at"]
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"

    def __str__(self):
        return f"{self.author} -> {self.generated_class}"