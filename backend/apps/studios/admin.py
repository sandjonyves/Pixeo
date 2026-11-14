"""Administration des paramètres de studio Pixeo."""

from __future__ import annotations

from django.contrib import admin

from .models import BrandingSettings, HomepageSettings


@admin.register(BrandingSettings)
class BrandingSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "custom_domain",
        "watermark_enabled",
        "updated_at",
    )
    search_fields = ("user__email", "user__branding_username", "custom_domain")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("user",)


@admin.register(HomepageSettings)
class HomepageSettingsAdmin(admin.ModelAdmin):
    list_display = ("user", "enabled", "brand_name", "updated_at")
    list_filter = ("enabled",)
    search_fields = ("user__email", "user__branding_username", "brand_name")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("user",)
