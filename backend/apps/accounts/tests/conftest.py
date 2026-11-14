"""Fixtures partagées des tests d'authentification Pixeo."""

from __future__ import annotations

import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.accounts.models import User, UserRole
from apps.accounts.registration.services import FREE_PLAN_CODE
from apps.billing.models import Plan

FREE_PLAN_DEFAULTS = {
    "name": "Free",
    "price_monthly_fcfa": 0,
    "storage_limit_bytes": 5 * 1024 * 1024 * 1024,
    "features": [
        "5 Go storage",
        "Unlimited galleries",
        "Private client link",
        "Password protection",
        "Pixeo watermark",
    ],
    "is_active": True,
    "sort_order": 0,
}


@pytest.fixture(autouse=True)
def clear_throttle_cache():
    """Évite qu'un test consomme le quota de throttling d'un autre."""

    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def free_plan(db) -> Plan:
    """Plan Free disponible même sans exécution des migrations de données."""

    plan, _created = Plan.objects.get_or_create(
        code=FREE_PLAN_CODE,
        defaults=FREE_PLAN_DEFAULTS,
    )
    return plan


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
