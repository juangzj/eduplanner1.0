from .performance_level_template_urls import urlpatterns as performance_level_templates_patterns
from .generated_levels_urls import urlpatterns as generated_levels_patterns
from .assessment_rubric_urls import urlpatterns as assessment_rubric_patterns
from .class_planning_urls import urlpatterns as class_planning_patterns

app_name = 'levels'

urlpatterns = (
	performance_level_templates_patterns
	+ generated_levels_patterns
	+ assessment_rubric_patterns
	+ class_planning_patterns
)
