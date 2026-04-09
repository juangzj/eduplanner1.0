from django.contrib import admin

from .models.generated_class_comment import GeneratedClassComment
from .models.generated_class_like import GeneratedClassLike


@admin.register(GeneratedClassLike)
class GeneratedClassLikeAdmin(admin.ModelAdmin):
	list_display = ("id", "generated_class", "user", "created_at")
	search_fields = ("generated_class__class_planning__topic", "user__gmail")
	list_filter = ("created_at",)


@admin.register(GeneratedClassComment)
class GeneratedClassCommentAdmin(admin.ModelAdmin):
	list_display = ("id", "generated_class", "author", "parent", "is_active", "created_at")
	search_fields = ("generated_class__class_planning__topic", "author__gmail", "content")
	list_filter = ("is_active", "created_at")
