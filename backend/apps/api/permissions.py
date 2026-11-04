"""Permissions DRF de base pour Pixeo.

Les règles d'isolation multi-tenant seront ajoutées dans les lots métier. Ce
module fournit la distinction entre les deux rôles authentifiés de la
plateforme. Les visiteurs publics utilisent ``AllowAny`` explicitement sur les
vues concernées.

Les classes d'authentification rechargent le compte depuis la base à chaque
requête. Les permissions vérifient malgré tout les statuts courants afin
qu'aucune vue ne puisse accorder un accès sur la seule foi d'un rôle ancien.
"""

from __future__ import annotations

from rest_framework.permissions import BasePermission

from apps.accounts.models import UserRole


def _has_current_role(user, role: str) -> bool:
    """Vérifie le rôle et le statut courant du compte."""

    return bool(
        user
        and user.is_authenticated
        and getattr(user, "is_active", False)
        and not getattr(user, "is_suspended", False)
        and getattr(user, "role", None) == role
    )


class IsPhotographer(BasePermission):
    """Autorise uniquement un compte photographe actif et non suspendu."""

    message = "Un compte photographe authentifié est requis."

    def has_permission(self, request, view) -> bool:
        return _has_current_role(request.user, UserRole.PHOTOGRAPHER)


class IsPlatformAdmin(BasePermission):
    """Autorise uniquement un administrateur plateforme actif et non suspendu."""

    message = "Un compte administrateur plateforme est requis."

    def has_permission(self, request, view) -> bool:
        return _has_current_role(request.user, UserRole.PLATFORM_ADMIN)
