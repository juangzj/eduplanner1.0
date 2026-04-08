from django.contrib import admin

from .models import Prompt


@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = ("id", "teacher", "score", "created_at")
    search_fields = ("teacher__gmail", "purpose", "task")
    list_filter = ("created_at",)
