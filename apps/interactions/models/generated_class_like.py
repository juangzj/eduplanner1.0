from django.db import models
from django.conf import settings
import uuid


class GeneratedClassLike(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    generated_class = models.ForeignKey(
        "levels.GeneratedClassPlan",
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="Clase generada"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="generated_class_likes",
        verbose_name="Usuario"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )

    class Meta:
        db_table = "generated_class_likes"
        verbose_name = "Me gusta"
        verbose_name_plural = "Me gusta"
        constraints = [
            models.UniqueConstraint(
                fields=["generated_class", "user"],
                name="unique_like_per_user_per_class"
            )
        ]

    def __str__(self):
        return f"{self.user} likes {self.generated_class}"