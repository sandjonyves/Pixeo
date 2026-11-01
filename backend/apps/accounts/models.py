"""Modèle utilisateur personnalisé de Pixeo.

Le photographe est le tenant. `branding_username` est sa clé publique et son
sous-domaine ; l'e-mail est l'identifiant de connexion. Aucun champ `plan`
n'existe ici : le plan actif viendra de `billing.Subscription`.
"""

from __future__ import annotations

import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

from .validators import (
    BRANDING_USERNAME_MAX_LENGTH,
    normalize_branding_username,
    validate_branding_username,
)


class UserRole(models.TextChoices):
    PHOTOGRAPHER = "photographer", _("Photographer")
    PLATFORM_ADMIN = "platform_admin", _("Platform admin")


class UserStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    INACTIVE = "inactive", _("Inactive")
    SUSPENDED = "suspended", _("Suspended")


class UserManager(BaseUserManager):
    """Manager basé sur l'e-mail, sans champ `username` séparé."""

    use_in_migrations = True

    def _create_user(self, email: str, password: str | None, **extra_fields):
        if not email:
            raise ValueError(_("L'adresse e-mail est obligatoire."))

        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        # Validation serveur explicite : le manager ne doit pas contourner les
        # règles de branding_username ni l'unicité applicative.
        user.full_clean()
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(
        self, email: str, password: str | None = None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", UserRole.PLATFORM_ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Un superutilisateur doit avoir is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                _("Un superutilisateur doit avoir is_superuser=True.")
            )
        if extra_fields.get("role") != UserRole.PLATFORM_ADMIN:
            raise ValueError(
                _(
                    "Un superutilisateur doit avoir "
                    "role=platform_admin."
                )
            )

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Utilisateur Pixeo : photographe ou administrateur plateforme."""

    # L'e-mail remplace le username Django comme identifiant de connexion.
    username = None

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_("email address"), unique=True)

    branding_username = models.CharField(
        _("branding username"),
        max_length=BRANDING_USERNAME_MAX_LENGTH,
        unique=True,
        validators=[validate_branding_username],
        help_text=_(
            "Nom public unique utilisé comme sous-domaine Pixeo. "
            "Lettres minuscules, chiffres et tirets uniquement."
        ),
    )

    role = models.CharField(
        _("role"),
        max_length=32,
        choices=UserRole.choices,
        default=UserRole.PHOTOGRAPHER,
    )
    is_suspended = models.BooleanField(_("suspended"), default=False)
    suspended_at = models.DateTimeField(
        _("suspended at"), null=True, blank=True
    )

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["branding_username"]

    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-created_at"]

    def clean_fields(self, exclude=None):
        """Normalise les identifiants avant d'exécuter les validateurs."""
        excluded = set(exclude or ())
        if "email" not in excluded and self.email:
            self.email = self.email.strip().lower()
        if "branding_username" not in excluded and self.branding_username:
            self.branding_username = normalize_branding_username(
                self.branding_username
            )
        super().clean_fields(exclude=excluded)

    def save(self, *args, **kwargs):
        """Garantit la normalisation même en cas d'écriture ORM directe."""
        if self.email:
            self.email = self.email.strip().lower()
        if self.branding_username:
            self.branding_username = normalize_branding_username(
                self.branding_username
            )
        super().save(*args, **kwargs)

    @property
    def status(self) -> str:
        """Statut lisible dérivé de `is_active` et `is_suspended`."""
        if self.is_suspended:
            return UserStatus.SUSPENDED
        if not self.is_active:
            return UserStatus.INACTIVE
        return UserStatus.ACTIVE

    def __str__(self) -> str:
        return self.email or self.branding_username or str(self.pk)
