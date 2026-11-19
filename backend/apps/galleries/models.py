"""Modèle de galerie photo Pixeo.

Une galerie appartient à un seul photographe. Le slug est unique dans l'espace
de ce photographe, ce qui permet à deux photographes différents d'utiliser le
même slug sans collision.
"""

from __future__ import annotations

import uuid

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import UserRole


class GalleryStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    PUBLISHED = "published", _("Published")
    HIDDEN = "hidden", _("Hidden")
    PRE_RELEASE = "pre_release", _("Pre-release")


class Gallery(models.Model):
    """Galerie photo appartenant à un photographe."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    photographer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="galleries",
        verbose_name=_("photographer"),
    )
    title = models.CharField(_("title"), max_length=150)
    slug = models.SlugField(_("slug"), max_length=100)
    description = models.TextField(_("description"), blank=True, default="")
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=GalleryStatus.choices,
        default=GalleryStatus.DRAFT,
    )
    published_at = models.DateTimeField(
        _("published at"), null=True, blank=True
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("gallery")
        verbose_name_plural = _("galleries")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["photographer", "slug"],
                name="unique_gallery_slug_per_photographer",
            ),
            models.CheckConstraint(
                condition=~models.Q(title=""),
                name="gallery_title_not_empty",
            ),
            models.CheckConstraint(
                condition=~models.Q(slug=""),
                name="gallery_slug_not_empty",
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=GalleryStatus.values),
                name="gallery_status_valid",
            ),
        ]

    def clean(self):
        """Valide les règles inter-tables du modèle."""
        super().clean()
        self._validate_photographer_role()

    def save(self, *args, **kwargs):
        """Applique la règle de rôle aux écritures ORM directes."""
        self._validate_photographer_role()
        super().save(*args, **kwargs)

    def _validate_photographer_role(self):
        """Refuse un propriétaire qui n'est pas un photographe.

        Une contrainte SQL ne peut pas vérifier une colonne d'une table liée.
        La règle est donc vérifiée par ``full_clean()`` et par ``save()``. Les
        opérations de masse doivent passer par un service qui appelle
        ``full_clean()``.
        """
        if not self.photographer_id:
            return

        try:
            role = self.photographer.role
        except ObjectDoesNotExist:
            # La contrainte de clé étrangère signalera l'utilisateur absent.
            return

        if role != UserRole.PHOTOGRAPHER:
            raise ValidationError(
                {
                    "photographer": _(
                        "Une galerie doit appartenir à un photographe."
                    )
                }
            )

    def __str__(self) -> str:
        return self.title
