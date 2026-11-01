"""Configuration Django Admin du modèle utilisateur Pixeo."""

from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .forms import PixeoUserChangeForm, PixeoUserCreationForm
from .models import User


class UserStatusFilter(admin.SimpleListFilter):
    """Filtre synthétique actif / inactif / suspendu."""

    title = _("status")
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return (
            ("active", _("Active")),
            ("inactive", _("Inactive")),
            ("suspended", _("Suspended")),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == "active":
            return queryset.filter(is_active=True, is_suspended=False)
        if value == "inactive":
            return queryset.filter(is_active=False, is_suspended=False)
        if value == "suspended":
            return queryset.filter(is_suspended=True)
        return queryset


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Administration des photographes et administrateurs plateforme."""

    form = PixeoUserChangeForm
    add_form = PixeoUserCreationForm

    list_display = (
        "email",
        "branding_username",
        "role",
        "is_active",
        "is_suspended",
        "created_at",
    )
    list_filter = ("role", UserStatusFilter)
    search_fields = (
        "email",
        "branding_username",
        "first_name",
        "last_name",
    )
    ordering = ("-created_at",)
    readonly_fields = (
        "last_login",
        "date_joined",
        "created_at",
        "updated_at",
        "suspended_at",
    )

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Identité"),
            {"fields": ("first_name", "last_name", "branding_username")},
        ),
        (
            _("Rôle et statut"),
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_suspended",
                    "suspended_at",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            _("Dates"),
            {
                "fields": (
                    "last_login",
                    "date_joined",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "branding_username",
                    "first_name",
                    "last_name",
                    "role",
                    "is_active",
                    "is_suspended",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    filter_horizontal = ("groups", "user_permissions")

    def save_model(self, request, obj, form, change):
        """Maintient `suspended_at` cohérent avec `is_suspended`."""
        if obj.is_suspended and obj.suspended_at is None:
            obj.suspended_at = timezone.now()
        elif not obj.is_suspended:
            obj.suspended_at = None
        super().save_model(request, obj, form, change)
