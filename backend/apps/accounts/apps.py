"""Configuration de l'application accounts."""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    verbose_name = "Accounts"

    def ready(self):
        # Enregistre les extensions OpenAPI des classes d'authentification.
        from . import schema  # noqa: F401
