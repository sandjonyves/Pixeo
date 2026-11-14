"""Tests de l'identité réseau utilisée par les throttles d'authentification."""

from __future__ import annotations

import pytest
from django.test import RequestFactory, override_settings

from apps.accounts.auth.throttles import (
    AuthLoginThrottle,
    AuthRefreshThrottle,
    AuthRegisterThrottle,
    PixeoAuthThrottle,
    get_client_ident,
)
from apps.accounts.tests.auth_helpers import (
    PASSWORD,
    REGISTER_URL,
    get_csrf,
    login,
    refresh,
)

pytestmark = pytest.mark.django_db

REMOTE_ADDR = "203.0.113.10"


def _registration_request(client, forwarded_for):
    return client.post(
        REGISTER_URL,
        {},
        format="json",
        REMOTE_ADDR=REMOTE_ADDR,
        HTTP_X_FORWARDED_FOR=forwarded_for,
    )


@override_settings(AUTH_TRUSTED_PROXY_COUNT=0)
def test_different_forwarded_for_values_do_not_bypass_registration_throttle(
    api_client, monkeypatch
):
    monkeypatch.setattr(
        AuthRegisterThrottle,
        "rate",
        "2/min",
        raising=False,
    )

    responses = [
        _registration_request(api_client, f"198.51.100.{index}")
        for index in range(1, 5)
    ]

    assert [response.status_code for response in responses] == [
        400,
        400,
        429,
        429,
    ]


@override_settings(AUTH_TRUSTED_PROXY_COUNT=0)
def test_same_network_identity_triggers_registration_throttle(
    api_client, monkeypatch
):
    monkeypatch.setattr(
        AuthRegisterThrottle,
        "rate",
        "2/min",
        raising=False,
    )

    responses = [
        _registration_request(api_client, "198.51.100.1") for _ in range(4)
    ]

    assert [response.status_code for response in responses] == [
        400,
        400,
        429,
        429,
    ]


@override_settings(AUTH_TRUSTED_PROXY_COUNT=0)
def test_different_forwarded_for_values_do_not_bypass_login_throttle(
    api_client, photographer, monkeypatch
):
    monkeypatch.setattr(
        AuthLoginThrottle,
        "rate",
        "2/min",
        raising=False,
    )

    responses = [
        login(
            api_client,
            photographer.email,
            "WrongPassword!",
            HTTP_X_FORWARDED_FOR=f"198.51.100.{index}",
        )
        for index in range(1, 4)
    ]

    assert [response.status_code for response in responses] == [
        401,
        401,
        429,
    ]


@override_settings(AUTH_TRUSTED_PROXY_COUNT=0)
def test_different_forwarded_for_values_do_not_bypass_refresh_throttle(
    api_client, photographer, monkeypatch
):
    monkeypatch.setattr(
        AuthRefreshThrottle,
        "rate",
        "1/min",
        raising=False,
    )
    login_response = login(api_client, photographer.email, PASSWORD)
    assert login_response.status_code == 200
    csrf_token = get_csrf(api_client)

    first = refresh(
        api_client,
        csrf_token,
        HTTP_X_FORWARDED_FOR="198.51.100.1",
    )
    second = refresh(
        api_client,
        csrf_token,
        HTTP_X_FORWARDED_FOR="198.51.100.2",
    )

    assert first.status_code == 200
    assert second.status_code == 429


@override_settings(AUTH_TRUSTED_PROXY_COUNT=0)
def test_forwarded_for_is_ignored_without_a_trusted_proxy():
    request = RequestFactory().post(
        "/",
        REMOTE_ADDR=REMOTE_ADDR,
        HTTP_X_FORWARDED_FOR="198.51.100.1",
    )

    assert get_client_ident(request) == REMOTE_ADDR


@override_settings(AUTH_TRUSTED_PROXY_COUNT=1)
def test_one_trusted_proxy_uses_the_forwarded_client_address():
    request = RequestFactory().post(
        "/",
        REMOTE_ADDR="10.0.0.5",
        HTTP_X_FORWARDED_FOR="198.51.100.1",
    )

    assert get_client_ident(request) == "198.51.100.1"


@override_settings(AUTH_TRUSTED_PROXY_COUNT=2)
def test_two_trusted_proxies_select_the_client_address_from_the_right():
    request = RequestFactory().post(
        "/",
        REMOTE_ADDR="10.0.0.5",
        HTTP_X_FORWARDED_FOR="198.51.100.1, 10.0.0.4",
    )

    assert get_client_ident(request) == "198.51.100.1"


@override_settings(AUTH_TRUSTED_PROXY_COUNT=2)
def test_incomplete_forwarded_for_falls_back_to_remote_addr():
    request = RequestFactory().post(
        "/",
        REMOTE_ADDR=REMOTE_ADDR,
        HTTP_X_FORWARDED_FOR="198.51.100.1",
    )

    assert get_client_ident(request) == REMOTE_ADDR


@override_settings(AUTH_TRUSTED_PROXY_COUNT=2)
def test_forwarded_for_whitespace_is_normalized():
    request = RequestFactory().post(
        "/",
        REMOTE_ADDR="10.0.0.5",
        HTTP_X_FORWARDED_FOR=" 198.51.100.1 , 10.0.0.4 ",
    )

    assert get_client_ident(request) == "198.51.100.1"


@override_settings(AUTH_TRUSTED_PROXY_COUNT=1)
def test_all_auth_throttles_share_the_same_trusted_proxy_strategy():
    request = RequestFactory().post(
        "/",
        REMOTE_ADDR="10.0.0.5",
        HTTP_X_FORWARDED_FOR="198.51.100.1",
    )
    ident = get_client_ident(request)
    assert ident == "198.51.100.1"

    for throttle_class in (
        AuthLoginThrottle,
        AuthRefreshThrottle,
        AuthRegisterThrottle,
    ):
        throttle = throttle_class()
        assert isinstance(throttle, PixeoAuthThrottle)
        cache_key = throttle.get_cache_key(request, None)
        assert cache_key is not None
        assert cache_key.endswith(f"_{ident}")
