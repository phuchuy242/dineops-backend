import os
from django.core.asgi import get_asgi_application

# Use config.settings.prod as the default ASGI settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')

application = get_asgi_application()
