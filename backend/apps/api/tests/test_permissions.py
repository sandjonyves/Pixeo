"""Tests des permissions DRF de base."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.accounts.models import User, UserRole

pytestmark = [
    pytest.mark.urls("apps.api.tests.test_urls"),
    pytest.mark.django_db,
]


def _user(role: str, *, email: str, branding_username: str) -> User:
    return User.objects.create_user(
        email=email,
        password="StrongPassword123!",
        branding_username=branding_username,
        role=role,
    )


def _client_for(user: User) -> APIClient:
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(user)}")
    return client


def test_photographer_permission_allows_photographer():
    user = _user(
        UserRole.PHOTOGRAPHER,
        email="photo@example.com",
        branding_username="photo",
    )

    response = _client_for(user).get(
        "/api/v1/photographer-only/",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 200
    assert response.json() == {
        "ok": True,
        "data": {"scope": "photographer"},
    }


def test_photographer_permission_denies_platform_admin():
    user = _user(
        UserRole.PLATFORM_ADMIN,
        email="admin@example.com",
        branding_username="admin-user",
    )

    response = _client_for(user).get(
        "/api/v1/photographer-only/",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 403
    assert response.json()["code"] == "PERMISSION_DENIED"


def test_platform_admin_permission_allows_admin():
    user = _user(
        UserRole.PLATFORM_ADMIN,
        email="admin@example.com",
        branding_username="admin-user",
    )

    response = _client_for(user).get(
        "/api/v1/admin-only/",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 200
    assert response.json() == {
        "ok": True,
        "data": {"scope": "admin"},
    }


def test_platform_admin_permission_denies_photographer():
    user = _user(
        UserRole.PHOTOGRAPHER,
        email="photo@example.com",
        branding_username="photo",
    )

    response = _client_for(user).get(
        "/api/v1/admin-only/",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 403
    assert response.json()["code"] == "PERMISSION_DENIED"


def test_public_view_allows_anonymous_visitor():
    response = APIClient().get(
        "/api/v1/items/",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_photographer_permission_denies_suspended_account():
    user = _user(
        UserRole.PHOTOGRAPHER,
        email="photo@example.com",
        branding_username="photo",
    )
    user.is_suspended = True
    user.save(update_fields=["is_suspended"])

    response = _client_for(user).get(
        "/api/v1/photographer-only/",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 403
    assert response.json()["code"] == "ACCOUNT_SUSPENDED"


def test_photographer_permission_denies_inactive_account():
    user = _user(
        UserRole.PHOTOGRAPHER,
        email="photo@example.com",
        branding_username="photo",
    )
    user.is_active = False
    user.save(update_fields=["is_active"])

    response = _client_for(user).get(
        "/api/v1/photographer-only/",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 403
    assert response.json()["code"] == "ACCOUNT_DISABLED"


def test_platform_admin_permission_denies_suspended_account():
    user = _user(
        UserRole.PLATFORM_ADMIN,
        email="admin@example.com",
        branding_username="admin-user",
    )
    user.is_suspended = True
    user.save(update_fields=["is_suspended"])

    response = _client_for(user).get(
        "/api/v1/admin-only/",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 403
    assert response.json()["code"] == "ACCOUNT_SUSPENDED"


def test_session_authentication_denies_suspended_account(client):
    user = _user(
        UserRole.PHOTOGRAPHER,
        email="photo@example.com",
        branding_username="photo",
    )
    client.force_login(user)
    user.is_suspended = True
    user.save(update_fields=["is_suspended"])

    response = client.get("/api/v1/photographer-only/")

    assert response.status_code == 403
    assert response.json()["code"] == "ACCOUNT_SUSPENDED"
