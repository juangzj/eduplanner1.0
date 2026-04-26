import os

from .base import *


django_env = os.getenv('DJANGO_ENV', 'development').lower()

if django_env in {'production', 'prod'}:
    from .prod import *
else:
    from .dev import *