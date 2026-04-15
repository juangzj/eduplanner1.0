from django.contrib import admin

from .models.assessment_rubric_model import AssessmentRubric
from .models.class_planning_model import ClassPlanning
from .models.generated_class_plan_model import GeneratedClassPlan
from .models.generated_levels_model import GeneratedLevels
from .models.performance_level_template_model import PerformanceLevelTemplate


@admin.register(PerformanceLevelTemplate)
class PerformanceLevelTemplateAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "area", "grade", "academic_period", "created_at")
	search_fields = ("user__gmail", "level_title", "learning", "didactic_resources", "learning_evidence")
	list_filter = ("area", "grade", "academic_period", "created_at")


@admin.register(GeneratedLevels)
class GeneratedLevelsAdmin(admin.ModelAdmin):
	list_display = ("id", "performance_template", "created_at", "updated_at")
	search_fields = ("performance_template__level_title", "low_level", "basic_level", "high_level", "superior_level")
	list_filter = ("created_at", "updated_at")


@admin.register(AssessmentRubric)
class AssessmentRubricAdmin(admin.ModelAdmin):
	list_display = ("id", "generated_levels", "title", "created_at", "updated_at")
	search_fields = ("title", "rubric_description", "rubric_content")
	list_filter = ("created_at", "updated_at")


@admin.register(ClassPlanning)
class ClassPlanningAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "topic", "performance_template", "generated_levels", "assessment_rubric", "created_at")
	search_fields = ("user__gmail", "topic", "subtopic", "class_objective", "prompt")
	list_filter = ("created_at", "updated_at")


@admin.register(GeneratedClassPlan)
class GeneratedClassPlanAdmin(admin.ModelAdmin):
	list_display = ("id", "class_planning", "ai_model", "created_at", "updated_at")
	search_fields = ("class_planning__topic", "generated_content", "ai_model")
	list_filter = ("created_at", "updated_at")
