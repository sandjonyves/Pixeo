"""Administration des galeries photo Pixeo."""

from __future__ import annotations

from django.contrib import admin

from .models import Gallery


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
