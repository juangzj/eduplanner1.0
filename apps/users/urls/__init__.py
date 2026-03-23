from .user_teacher_urls import urlpatterns as teacher_patterns
from .auth_user_teacher_urls import urlpatterns as auth_patterns

app_name = 'users' 

urlpatterns = []
urlpatterns += teacher_patterns + auth_patterns