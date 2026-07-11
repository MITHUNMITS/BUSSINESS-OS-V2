import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "business_os.config.settings.dev")

application = get_wsgi_application()

