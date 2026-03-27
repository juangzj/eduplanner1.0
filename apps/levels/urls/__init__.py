from .performance_level_template_urls import urlpatterns as performance_level_templates_patterns
from .generated_levels_urls import urlpatterns as generated_levels_patterns

app_name = 'levels'

urlpatterns = performance_level_templates_patterns + generated_levels_patterns
