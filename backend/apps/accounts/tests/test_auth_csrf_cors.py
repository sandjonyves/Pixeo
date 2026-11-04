"""Tests CSRF, CORS et limitation de débit des endpoints d'authentification."""

from __future__ import annotations

from django.conf import settings
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

from apps.accounts.auth.throttles import AuthLoginThrottle, AuthRefreshThrottle
from apps.accounts.tests.auth_helpers import (
    CSRF_URL,
    LOGIN_URL,
    PASSWORD,
    get_csrf,
    login,
    refresh,
    refresh_cookie,
)

import pytest

pytestmark = pytest.mark.django_db


def test_csrf_endpoint_returns_token_and_sets_cookie(api_client):
    response = api_client.get(CSRF_URL)

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["data"]["csrfToken"]
    assert "refresh" not in payload["data"]

    cookie = response.cookies.get(settings.CSRF_COOKIE_NAME)
    assert cookie is not None
    assert cookie.value
    assert not cookie["httponly"] or cookie["httponly"] == "False"
    assert cookie["path"] == "/"
    assert (cookie["samesite"] or "").lower() == "lax"
    assert not cookie["secure"]


def test_csrf_endpoint_does_not_create_refresh_cookie(api_client):
    response = api_client.get(CSRF_URL)

    assert settings.AUTH_REFRESH_COOKIE_NAME not in response.cookies


def test_login_without_csrf_is_refused(api_client, photographer):
    response = api_client.post(
        LOGIN_URL,
        {"email": photographer.email, "password": PASSWORD},
        format="json",
    )

    assert response.status_code == 403
    assert response.json()["code"] == "CSRF_FAILED"
    assert refresh_cookie(response) is None
    assert not OutstandingToken.objects.filter(user=photographer).exists()


def test_login_with_valid_csrf_succeeds(api_client, photographer):
    csrf_token = get_csrf(api_client)

    response = api_client.post(
        LOGIN_URL,
        {"email": photographer.email, "password": PASSWORD},
        format="json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )

    assert response.status_code == 200
    assert response.json()["data"]["accessToken"]
    assert refresh_cookie(response) is not None


def test_login_rejects_untrusted_origin(api_client, photographer):
    csrf_token = get_csrf(api_client)

    response = api_client.post(
        LOGIN_URL,
        {"email": photographer.email, "password": PASSWORD},
        format="json",
        HTTP_X_CSRFTOKEN=csrf_token,
        HTTP_ORIGIN="https://evil.example",
    )

    assert response.status_code == 403
    assert response.json()["code"] == "CSRF_FAILED"
    assert refresh_cookie(response) is None
    assert not OutstandingToken.objects.filter(user=photographer).exists()


def test_login_accepts_trusted_origin(api_client, photographer):
    csrf_token = get_csrf(api_client)

    response = api_client.post(
        LOGIN_URL,
        {"email": photographer.email, "password": PASSWORD},
        format="json",
        HTTP_X_CSRFTOKEN=csrf_token,
        HTTP_ORIGIN="http://app.lvh.me:3000",
    )

    assert response.status_code == 200
    assert refresh_cookie(response) is not None


@pytest.mark.parametrize(
    "content_type",
    [
        "application/x-www-form-urlencoded",
        "text/plain",
    ],
)
def test_login_rejects_non_json_content_types(
    api_client,
    photographer,
    content_type,
):
    csrf_token = get_csrf(api_client)

    response = api_client.post(
        LOGIN_URL,
        {"email": photographer.email, "password": PASSWORD},
        content_type=content_type,
        HTTP_X_CSRFTOKEN=csrf_token,
    )

    assert response.status_code == 415
    assert response.json()["code"] == "UNSUPPORTED_MEDIA_TYPE"
    assert refresh_cookie(response) is None
    assert not OutstandingToken.objects.filter(user=photographer).exists()


def test_login_rejects_multipart_form_data(api_client, photographer):
    csrf_token = get_csrf(api_client)

    response = api_client.post(
        LOGIN_URL,
        {"email": photographer.email, "password": PASSWORD},
        format="multipart",
        HTTP_X_CSRFTOKEN=csrf_token,
    )

    # Le contrôle CSRF consomme le corps multipart avant le parser JSON.
    # Le refus peut donc être un 400 de validation plutôt qu'un 415 ; dans
    # tous les cas, aucune authentification ni aucun cookie n'est créé.
    assert response.status_code in {400, 415}
    assert response.json()["code"] in {
        "VALIDATION_ERROR",
        "UNSUPPORTED_MEDIA_TYPE",
    }
    assert refresh_cookie(response) is None
    assert not OutstandingToken.objects.filter(user=photographer).exists()


def test_login_malformed_multipart_is_rejected_without_500(
    api_client, photographer
):
    csrf_token = get_csrf(api_client)

    response = api_client.post(
        LOGIN_URL,
        data="not-a-valid-multipart-body",
        content_type="multipart/form-data",
        HTTP_X_CSRFTOKEN=csrf_token,
    )

    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_REQUEST"
    assert refresh_cookie(response) is None
    assert not OutstandingToken.objects.filter(user=photographer).exists()


def test_login_html_form_without_csrf_is_refused(api_client, photographer):
    response = api_client.post(
        LOGIN_URL,
        {"email": photographer.email, "password": PASSWORD},
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 403
    assert response.json()["code"] == "CSRF_FAILED"
    assert refresh_cookie(response) is None
    assert not OutstandingToken.objects.filter(user=photographer).exists()


def test_login_preflight_rejects_untrusted_origin(api_client):
    response = api_client.options(
        LOGIN_URL,
        HTTP_ORIGIN="https://evil.example",
        HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        HTTP_ACCESS_CONTROL_REQUEST_HEADERS="content-type,x-csrftoken",
    )

    assert "Access-Control-Allow-Origin" not in response


def test_login_preflight_allows_trusted_origin(api_client):
    response = api_client.options(
        LOGIN_URL,
        HTTP_ORIGIN="http://app.lvh.me:3000",
        HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        HTTP_ACCESS_CONTROL_REQUEST_HEADERS="content-type,x-csrftoken",
    )

    assert response["Access-Control-Allow-Origin"] == "http://app.lvh.me:3000"
    assert response["Access-Control-Allow-Credentials"] == "true"
    assert "POST" in response["Access-Control-Allow-Methods"]
    assert "x-csrftoken" in response["Access-Control-Allow-Headers"].lower()


def test_refresh_rejects_untrusted_origin(api_client, photographer):
    login(api_client, photographer.email)
    csrf_token = get_csrf(api_client)

    response = refresh(
        api_client,
        csrf_token,
        HTTP_ORIGIN="https://evil.example",
    )

    assert response.status_code == 403
    assert response.json()["code"] == "CSRF_FAILED"
    assert response.json()["details"] == {}
    error = response.json()["error"].lower()
    assert "cookie" not in error
    assert "origin" not in error


def test_refresh_accepts_trusted_origin(api_client, photographer):
    login(api_client, photographer.email)
    csrf_token = get_csrf(api_client)

    response = refresh(
        api_client,
        csrf_token,
        HTTP_ORIGIN="http://app.lvh.me:3000",
    )

    assert response.status_code == 200


def test_cors_allows_explicit_development_origin_with_credentials(api_client):
    response = api_client.get(
        CSRF_URL,
        HTTP_ORIGIN="http://app.lvh.me:3000",
    )

    assert response.status_code == 200
    assert response["Access-Control-Allow-Origin"] == "http://app.lvh.me:3000"
    assert response["Access-Control-Allow-Credentials"] == "true"


def test_cors_rejects_untrusted_origin(api_client):
    response = api_client.get(
        CSRF_URL,
        HTTP_ORIGIN="https://evil.example",
    )

    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" not in response


def test_login_is_rate_limited(api_client, photographer, monkeypatch):
    monkeypatch.setattr(
        AuthLoginThrottle,
        "rate",
        "2/min",
        raising=False,
    )

    first = login(api_client, photographer.email, "WrongPassword!")
    second = login(api_client, photographer.email, "WrongPassword!")
    third = login(api_client, photographer.email, "WrongPassword!")

    assert first.status_code == 401
    assert second.status_code == 401
    assert third.status_code == 429
    assert third.json()["code"] == "RATE_LIMITED"
    assert "Retry-After" in third


def test_refresh_is_rate_limited(api_client, photographer, monkeypatch):
    monkeypatch.setattr(
        AuthRefreshThrottle,
        "rate",
        "1/min",
        raising=False,
    )
    login(api_client, photographer.email, PASSWORD)
    csrf_token = get_csrf(api_client)

    first = refresh(api_client, csrf_token)
    second = refresh(api_client, csrf_token)

    assert first.status_code == 200
    assert second.status_code == 429
    assert second.json()["code"] == "RATE_LIMITED"
