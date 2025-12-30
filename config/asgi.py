import os
from django.core.asgi import get_asgi_application

# default to the existing settings module to avoid breaking the current project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dineops-backend.settings')

application = get_asgi_application()

