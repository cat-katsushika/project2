from django.contrib import admin
from teams.models import Task, Team


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass
