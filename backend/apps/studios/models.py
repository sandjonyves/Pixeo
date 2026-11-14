"""Paramètres de présentation du studio photographe.

``BrandingSettings`` et ``HomepageSettings`` sont des extensions 1:1 de
``accounts.User``. Le nom public reste unique dans ``User.branding_username`` :
il n'est jamais dupliqué ici.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class BrandingSettings(models.Model):
    """Identité visuelle et filigrane du studio."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="branding_settings",
        verbose_name=_("photographer"),
    )
    custom_domain = models.CharField(
        _("custom domain"), max_length=255, blank=True, default=""
    )
    logo_url = models.URLField(_("logo URL"), max_length=500, blank=True, default="")
    favicon_url = models.URLField(
        _("favicon URL"), max_length=500, blank=True, default=""
    )
    watermark_enabled = models.BooleanField(_("watermark enabled"), default=False)
    watermark_text = models.CharField(
        _("watermark text"), max_length=100, blank=True, default="Pixeo"
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("branding settings")
        verbose_name_plural = _("branding settings")

    def __str__(self) -> str:
        return f"Branding de {self.user_id}"


class HomepageSettings(models.Model):
    """Paramètres de la page d'accueil publique du studio."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="homepage_settings",
        verbose_name=_("photographer"),
    )
    enabled = models.BooleanField(_("enabled"), default=True)
    biography = models.TextField(_("biography"), blank=True, default="")
    brand_name = models.CharField(
        _("brand name"), max_length=100, blank=True, default=""
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("homepage settings")
        verbose_name_plural = _("homepage settings")

    def __str__(self) -> str:
        return f"Homepage de {self.user_id}"
