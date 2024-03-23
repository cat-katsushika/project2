import uuid

from django.conf import settings
from django.db import models


class Team(models.Model):
    id = models.UUIDField(
        verbose_name="チームID",
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="teams", blank=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Task(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "進行中"
        COMPLETED = "completed", "完了"

    id = models.UUIDField(
        verbose_name="タスクID",
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasks")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="tasks")

    status = models.CharField(max_length=15, choices=Status.choices, default=Status.IN_PROGRESS)
