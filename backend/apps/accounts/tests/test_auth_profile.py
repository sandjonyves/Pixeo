"""Tests du profil du compte connecté Pixeo."""

from __future__ import annotations

from datetime import timedelta

from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from apps.accounts.tests.auth_helpers import ME_URL, login, me

import pytest

pytestmark = pytest.mark.django_db


def _access_for_login(api_client, user) -> str:
    response = login(api_client, user.email)
    assert response.status_code == 200
    return response.json()["data"]["accessToken"]


def test_me_with_valid_access_token_returns_non_sensitive_profile(
    api_client, photographer
):
    access = _access_for_login(api_client, photographer)

    response = me(api_client, access)

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    data = payload["data"]
    assert set(data) == {
        "id",
        "email",
        "firstName",
        "lastName",
        "role",
        "brandingUsername",
        "isActive",
        "isSuspended",
        "dateJoined",
    }
    assert data["id"] == str(photographer.id)
    assert data["email"] == "photographer@example.com"
    assert data["firstName"] == "Jean"
    assert data["lastName"] == "Dupont"
    assert data["role"] == "photographer"
    assert data["brandingUsername"] == "jean-dupont"
    assert data["isActive"] is True
    assert data["isSuspended"] is False

    body = response.content.decode()
    assert photographer.password not in body
    assert "password" not in body
    assert "refresh" not in body.lower()


def test_me_without_token_is_refused(api_client):
    response = api_client.get(ME_URL)

    assert response.status_code == 401
    assert response.json()["code"] == "AUTHENTICATION_REQUIRED"
    assert "WWW-Authenticate" in response


def test_me_with_invalid_token_returns_token_invalid(api_client):
    response = me(api_client, "invalid-token")

    assert response.status_code == 401
    assert response.json()["code"] == "TOKEN_INVALID"


def test_me_with_expired_token_returns_token_expired(
    api_client, photographer
):
    token = AccessToken.for_user(photographer)
    token.set_exp(
        from_time=timezone.now() - token.lifetime - timedelta(minutes=1)
    )

    response = me(api_client, str(token))

    assert response.status_code == 401
    assert response.json()["code"] == "TOKEN_EXPIRED"


def test_me_rejects_refresh_token_as_access_token(api_client, photographer):
    refresh_token = RefreshToken.for_user(photographer)

    response = me(api_client, str(refresh_token))

    assert response.status_code == 401
    assert response.json()["code"] == "TOKEN_INVALID"


def test_me_is_refused_after_suspension(api_client, photographer):
    access = _access_for_login(api_client, photographer)

    photographer.is_suspended = True
    photographer.save(update_fields=["is_suspended"])

    response = me(api_client, access)

    assert response.status_code == 403
    assert response.json()["code"] == "ACCOUNT_SUSPENDED"


def test_me_is_refused_after_deactivation(api_client, photographer):
    access = _access_for_login(api_client, photographer)

    photographer.is_active = False
    photographer.save(update_fields=["is_active"])

    response = me(api_client, access)

    assert response.status_code == 403
    assert response.json()["code"] == "ACCOUNT_DISABLED"


def test_me_works_for_platform_admin(api_client, platform_admin):
    access = _access_for_login(api_client, platform_admin)

    response = me(api_client, access)

    assert response.status_code == 200
    assert response.json()["data"]["role"] == "platform_admin"
