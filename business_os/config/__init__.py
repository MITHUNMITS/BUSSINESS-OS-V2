"""Runtime configuration package."""

from business_os.config.celery import app as celery_app

__all__ = ("celery_app",)
