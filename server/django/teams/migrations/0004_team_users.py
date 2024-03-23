# Generated by Django 4.2.3 on 2024-03-23 00:54

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("teams", "0003_alter_team_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="team",
            name="users",
            field=models.ManyToManyField(related_name="teams", to=settings.AUTH_USER_MODEL),
        ),
    ]