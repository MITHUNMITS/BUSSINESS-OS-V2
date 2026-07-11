import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "business_os.config.settings.dev")

app = Celery("business_os")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

