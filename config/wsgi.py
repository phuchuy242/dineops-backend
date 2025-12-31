import os
from django.core.wsgi import get_wsgi_application

# Use config.settings.prod as the default WSGI settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')

application = get_wsgi_application()
