from django.contrib import admin

from .models.user_teacher import TeacherUser


@admin.register(TeacherUser)
class TeacherUserAdmin(admin.ModelAdmin):
	list_display = ("id", "gmail", "first_name", "last_name", "is_staff", "is_active")
	search_fields = ("gmail", "first_name", "middle_name", "last_name", "second_last_name", "nickname")
	list_filter = ("is_staff", "is_active")
