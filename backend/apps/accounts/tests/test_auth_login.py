"""Tests de l'endpoint de connexion Pixeo."""

from __future__ import annotations

from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

from apps.accounts.models import User
from apps.accounts.tests.auth_helpers import (
    LOGIN_URL,
    PASSWORD,
    get_csrf,
    login,
    refresh_cookie,
    refresh_cookie_value,
)

import pytest

pytestmark = pytest.mark.django_db


def test_photographer_login_returns_access_token_and_http_only_cookie(
    api_client, photographer
):
    response = login(api_client, photographer.email)

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["data"]["accessToken"]

    user_data = payload["data"]["user"]
    assert set(user_data) == {
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
    assert user_data["id"] == str(photographer.id)
    assert user_data["email"] == "photographer@example.com"
    assert user_data["firstName"] == "Jean"
    assert user_data["lastName"] == "Dupont"
    assert user_data["role"] == "photographer"
    assert user_data["brandingUsername"] == "jean-dupont"
    assert user_data["isActive"] is True
    assert user_data["isSuspended"] is False
    assert user_data["dateJoined"]

    # Le refresh token n'est jamais dans le JSON.
    assert "refresh" not in payload["data"]
    assert "refreshToken" not in payload["data"]
    assert "password" not in payload["data"]["user"]
    assert "access" not in payload["data"]["user"]

    cookie = refresh_cookie(response)
    assert cookie is not None
    assert cookie.value == refresh_cookie_value(response)
    assert cookie["httponly"] is True or cookie["httponly"] == "True"
    assert cookie["path"] == "/api/v1/auth/"
    assert int(cookie["max-age"]) == int(
        settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()
    )
    assert (cookie["samesite"] or "").lower() == "lax"
    assert not cookie["secure"]
    assert not cookie["domain"]

    access = AccessToken(payload["data"]["accessToken"])
    assert access["user_id"] == str(photographer.id)
    assert access["token_type"] == "access"

    assert OutstandingToken.objects.filter(user=photographer).count() == 1


def test_platform_admin_login_succeeds(api_client, platform_admin):
    response = login(api_client, platform_admin.email)

    assert response.status_code == 200
    assert response.json()["data"]["user"]["role"] == "platform_admin"
    assert refresh_cookie(response) is not None


def test_email_is_normalized_and_case_insensitive(api_client, photographer):
    response = login(api_client, "  PHOTOGRAPHER@EXAMPLE.COM  ")

    assert response.status_code == 200
    assert response.json()["data"]["user"]["email"] == "photographer@example.com"


def test_invalid_password_and_unknown_email_return_the_same_generic_error(
    api_client, photographer
):
    wrong_password = login(api_client, photographer.email, "WrongPassword!")
    unknown_email = login(api_client, "unknown@example.com", PASSWORD)

    assert wrong_password.status_code == 401
    assert unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()
    assert wrong_password.json()["code"] == "INVALID_CREDENTIALS"
    assert wrong_password.json()["error"] == (
        "Adresse e-mail ou mot de passe incorrect."
    )
    assert refresh_cookie(wrong_password) is None
    assert refresh_cookie(unknown_email) is None


def test_disabled_account_is_refused(api_client, photographer):
    photographer.is_active = False
    photographer.save(update_fields=["is_active"])

    response = login(api_client, photographer.email)

    assert response.status_code == 403
    assert response.json()["code"] == "ACCOUNT_DISABLED"
    assert response.json()["error"] == "Ce compte est désactivé."
    assert refresh_cookie(response) is None


def test_suspended_account_is_refused(api_client, photographer):
    photographer.is_suspended = True
    photographer.save(update_fields=["is_suspended"])

    response = login(api_client, photographer.email)

    assert response.status_code == 403
    assert response.json()["code"] == "ACCOUNT_SUSPENDED"
    assert response.json()["error"] == "Ce compte est suspendu."
    assert refresh_cookie(response) is None


def test_missing_credentials_return_validation_error(api_client):
    csrf_token = get_csrf(api_client)
    response = api_client.post(
        LOGIN_URL,
        {},
        format="json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )

    assert response.status_code == 400
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert set(response.json()["details"]) == {"email", "password"}


def test_login_updates_last_login(api_client, photographer):
    assert photographer.last_login is None

    response = login(api_client, photographer.email)

    assert response.status_code == 200
    photographer.refresh_from_db()
    assert photographer.last_login is not None


def test_login_does_not_create_refresh_token_for_bad_password(
    api_client, photographer
):
    response = login(api_client, photographer.email, "WrongPassword!")

    assert response.status_code == 401
    assert not OutstandingToken.objects.filter(user=photographer).exists()


def test_login_does_not_leak_refresh_token_in_response_body(
    api_client, photographer
):
    response = login(api_client, photographer.email)

    assert response.status_code == 200
    raw_refresh = refresh_cookie_value(response)
    assert raw_refresh not in response.content.decode()
    assert "pixeo_refresh" not in response.content.decode()


def test_user_can_login_again_with_different_case_after_creation(api_client):
    User.objects.create_user(
        email="Mixed.Case@Example.com",
        password=PASSWORD,
        branding_username="mixed-case",
    )

    response = login(api_client, "mixed.case@example.com")

    assert response.status_code == 200
    assert response.json()["data"]["user"]["email"] == "mixed.case@example.com"
