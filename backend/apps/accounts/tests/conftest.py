"""Fixtures partagées des tests d'authentification Pixeo."""

from __future__ import annotations

import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.accounts.models import User, UserRole


@pytest.fixture(autouse=True)
def clear_throttle_cache():
    """Évite qu'un test consomme le quota de throttling d'un autre."""

    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def api_client() -> APIClient:
    # Les tests d'authentification doivent simuler un navigateur qui applique
    # réellement les règles CSRF. Login, refresh et logout sont vérifiés
    # explicitement, car APIView est exempté par défaut.
    return APIClient(enforce_csrf_checks=True)


@pytest.fixture
def photographer(db) -> User:
    return User.objects.create_user(
        email="photographer@example.com",
        password="StrongPassword123!",
        branding_username="jean-dupont",
        first_name="Jean",
        last_name="Dupont",
    )


@pytest.fixture
def platform_admin(db) -> User:
    return User.objects.create_user(
        email="admin@example.com",
        password="StrongPassword123!",
        branding_username="pixeo-admin",
        first_name="Ada",
        last_name="Admin",
        role=UserRole.PLATFORM_ADMIN,
        is_staff=True,
    )
