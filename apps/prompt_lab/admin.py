from django.contrib import admin

from .models.prompt_model import Prompt


@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = ("id", "teacher", "refinement_number", "is_ai_generated", "score", "created_at")
    search_fields = ("teacher__gmail", "purpose", "role", "context", "task", "full_prompt")
    list_filter = ("is_ai_generated", "created_at")
