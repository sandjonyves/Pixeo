"""Configuration de l'application API Pixeo."""

from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Regroupe les conventions transverses de l'API REST."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.api"
    verbose_name = "API Pixeo"
