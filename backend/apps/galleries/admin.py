"""Administration des galeries photo Pixeo."""

from __future__ import annotations

from django.contrib import admin

from .models import Gallery, Photo


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ("title", "photographer", "slug", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("title", "slug")
    ordering = ("-created_at",)
    readonly_fields = (
        "status",
        "published_at",
        "created_at",
        "updated_at",
    )
    autocomplete_fields = ("photographer",)


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    """Consultation et suppression des photos importées.

    L'ajout et la modification des métadonnées passent par l'API : l'admin ne
    doit pas contourner la validation du fichier ni le service de stockage.
    """

    list_display = (
        "original_filename",
        "gallery",
        "position",
        "width",
        "height",
        "size_bytes",
        "created_at",
    )
    list_filter = ("format", "created_at")
    search_fields = (
        "original_filename",
        "gallery__title",
        "gallery__slug",
        "gallery__photographer__email",
    )
    ordering = ("gallery", "position", "created_at")
    list_select_related = ("gallery",)
    readonly_fields = (
        "id",
        "gallery",
        "file",
        "original_filename",
        "format",
        "mime_type",
        "size_bytes",
        "width",
        "height",
        "checksum_sha256",
        "position",
        "created_at",
        "updated_at",
    )
    autocomplete_fields = ("gallery",)

    def has_add_permission(self, request) -> bool:
        return False
