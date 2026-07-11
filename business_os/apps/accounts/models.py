from __future__ import annotations

import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_("email address"), blank=False, db_index=True)
    phone_number = models.CharField(max_length=40, blank=True)
    locale = models.CharField(max_length=16, default="en")
    timezone = models.CharField(max_length=80, default="Asia/Dubai")
    is_platform_staff = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["is_platform_staff"]),
        ]

    def __str__(self) -> str:
        return self.get_full_name() or self.username or self.email

