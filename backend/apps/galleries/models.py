"""Modèle de galerie photo Pixeo.

Une galerie appartient à un seul photographe. Le slug est unique dans l'espace
de ce photographe, ce qui permet à deux photographes différents d'utiliser le
même slug sans collision.
"""

from __future__ import annotations

import uuid
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import UserRole

# Formats réellement décodés par Pillow et acceptés par l'import A9. Le format
# est détecté depuis le contenu, jamais depuis l'extension fournie par le client.
PHOTO_ALLOWED_FORMATS = ("JPEG", "PNG", "WEBP")
PHOTO_FORMAT_EXTENSIONS = {
    "JPEG": ".jpg",
    "PNG": ".png",
    "WEBP": ".webp",
}
PHOTO_FORMAT_MIME_TYPES = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp",
}


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
            models.CheckConstraint(
                condition=(
                    ~models.Q(status=GalleryStatus.PUBLISHED)
                    | models.Q(published_at__isnull=False)
                ),
                name="gallery_published_requires_published_at",
            ),
        ]

    def clean(self):
        """Valide les règles inter-tables du modèle."""
        super().clean()
        self._validate_photographer_role()
        self._validate_publication_consistency()

    def save(self, *args, **kwargs):
        """Applique les règles métier aux écritures ORM directes."""
        self._validate_photographer_role()
        self._validate_publication_consistency()
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

    def _validate_publication_consistency(self):
        """Garantit qu'une galerie publiée possède une date de publication.

        ``published_at`` représente la date de première publication. Elle peut
        donc rester renseignée après une dépublication ou un masquage.
        """

        if (
            self.status == GalleryStatus.PUBLISHED
            and self.published_at is None
        ):
            raise ValidationError(
                {
                    "published_at": _(
                        "Une galerie publiée doit avoir une date de première "
                        "publication."
                    )
                }
            )

    def __str__(self) -> str:
        return self.title


def photo_upload_path(instance: "Photo", filename: str) -> str:
    """Construit une clé de stockage stable et non devinable.

    L'extension est choisie par le service après validation du contenu. En cas
    d'écriture directe hors service, l'extension du nom fourni est conservée si
    elle fait partie des formats autorisés, sinon ``.img`` est utilisé. Le nom
    d'origine n'est jamais utilisé comme chemin.
    """

    detected_extension = getattr(instance, "_storage_extension", None)
    if detected_extension in PHOTO_FORMAT_EXTENSIONS.values():
        extension = detected_extension
    else:
        suffix = Path(filename).suffix.lower()
        extension = (
            suffix
            if suffix in PHOTO_FORMAT_EXTENSIONS.values()
            else ".img"
        )

    return f"galleries/{instance.gallery_id}/photos/{uuid.uuid4().hex}{extension}"


class Photo(models.Model):
    """Photo importée dans une galerie Pixeo.

    La photo appartient à la galerie, donc au photographe propriétaire de cette
    galerie. Aucun champ propriétaire dupliqué n'est exposé : l'isolation est
    appliquée via ``gallery__photographer``.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gallery = models.ForeignKey(
        Gallery,
        on_delete=models.CASCADE,
        related_name="photos",
        verbose_name=_("gallery"),
    )
    file = models.ImageField(
        _("file"),
        upload_to=photo_upload_path,
        max_length=500,
    )
    original_filename = models.CharField(
        _("original filename"),
        max_length=255,
    )
    format = models.CharField(_("format"), max_length=20)
    mime_type = models.CharField(_("MIME type"), max_length=100)
    size_bytes = models.PositiveBigIntegerField(_("size (bytes)"))
    width = models.PositiveIntegerField(_("width"))
    height = models.PositiveIntegerField(_("height"))
    checksum_sha256 = models.CharField(_("SHA-256 checksum"), max_length=64)
    position = models.PositiveIntegerField(_("position"), default=0)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("photo")
        verbose_name_plural = _("photos")
        ordering = ["position", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["gallery", "position"],
                name="unique_photo_position_per_gallery",
            ),
            models.CheckConstraint(
                condition=~models.Q(original_filename=""),
                name="photo_original_filename_not_empty",
            ),
            models.CheckConstraint(
                condition=models.Q(format__in=PHOTO_ALLOWED_FORMATS),
                name="photo_format_valid",
            ),
            models.CheckConstraint(
                condition=models.Q(width__gt=0) & models.Q(height__gt=0),
                name="photo_dimensions_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(size_bytes__gt=0),
                name="photo_size_positive",
            ),
        ]

    def __str__(self) -> str:
        return self.original_filename or str(self.pk)
