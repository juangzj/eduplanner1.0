import os

from .base import *


django_env = os.getenv('DJANGO_ENV', 'development').lower()
is_render = bool(os.getenv('RENDER_EXTERNAL_HOSTNAME') or os.getenv('RENDER'))

if django_env in {'production', 'prod'} or is_render:
    from .prod import *
else:
    from .dev import *