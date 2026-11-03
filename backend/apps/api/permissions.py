"""Permissions DRF de base pour Pixeo.

Les règles d'isolation multi-tenant seront ajoutées dans les lots métier. Ce
module fournit seulement la distinction entre les deux rôles authentifiés de la
plateforme. Les visiteurs publics utilisent ``AllowAny`` explicitement sur les
vues concernées.
"""

from __future__ import annotations

from rest_framework.permissions import BasePermission

from apps.accounts.models import UserRole


class IsPhotographer(BasePermission):
    """Autorise uniquement un compte photographe authentifié."""

    message = "Un compte photographe authentifié est requis."

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) == UserRole.PHOTOGRAPHER
        )


class IsPlatformAdmin(BasePermission):
    """Autorise uniquement un administrateur de la plateforme."""

    message = "Un compte administrateur plateforme est requis."

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) == UserRole.PLATFORM_ADMIN
        )
