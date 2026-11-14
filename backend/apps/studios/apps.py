"""Configuration de l'application studios."""

from django.apps import AppConfig


class StudiosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.studios"
    verbose_name = "Studios"
