from django.conf import settings
from django.db import models


class Prompt(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="prompts",
    )
    parent_prompt = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="refinement_attempts",
        null=True,
        blank=True,
    )
    root_prompt = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="thread_prompts",
        null=True,
        blank=True,
    )
    refinement_number = models.PositiveIntegerField(default=0)
    is_ai_generated = models.BooleanField(default=False)
    purpose = models.TextField()
    role = models.TextField()
    context = models.TextField()
    task = models.TextField()
    process = models.TextField(blank=True, null=True)
    format = models.TextField()
    constraints = models.TextField(blank=True, null=True)
    full_prompt = models.TextField()
    score = models.FloatField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Prompt {self.id} - {self.teacher}"
