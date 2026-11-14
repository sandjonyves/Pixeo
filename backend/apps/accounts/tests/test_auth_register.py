"""Tests de l'inscription publique des photographes Pixeo."""

from __future__ import annotations

import logging

import pytest
from django.conf import settings
from django.db import IntegrityError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

from apps.accounts.auth.exceptions import RegistrationConflict
from apps.accounts.auth.throttles import AuthRegisterThrottle
from apps.accounts.models import User, UserRole
from apps.accounts.registration.services import register_photographer
from apps.accounts.tests.auth_helpers import (
    PASSWORD,
    REGISTER_URL,
    login,
    refresh_cookie,
)
from apps.billing.models import Plan, Subscription, SubscriptionStatus
from apps.studios.models import BrandingSettings, HomepageSettings

pytestmark = pytest.mark.django_db


def registration_payload(**overrides):
    payload = {
        "email": "photographe@example.com",
        "password": "MotDePasseSolide123!",
        "passwordConfirmation": "MotDePasseSolide123!",
        "brandingUsername": "studio-photo",
    }
    payload.update(overrides)
    return payload


def register(client, payload=None, **extra):
    if payload is None:
        payload = registration_payload()
    return client.post(
        REGISTER_URL,
        payload,
        format="json",
        **extra,
    )


def test_registration_creates_photographer_and_initializes_studio(
    api_client, free_plan
):
    response = register(
        api_client,
        registration_payload(
            email="  Photographe@Example.COM  ",
            brandingUsername="  Studio-Photo  ",
        ),
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["ok"] is True

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
    assert user_data["email"] == "photographe@example.com"
    assert user_data["role"] == "photographer"
    assert user_data["brandingUsername"] == "studio-photo"
    assert user_data["isActive"] is True
    assert user_data["isSuspended"] is False

    user = User.objects.get(email="photographe@example.com")
    assert user.role == UserRole.PHOTOGRAPHER
    assert user.branding_username == "studio-photo"
    assert user.is_staff is False
    assert user.is_superuser is False
    assert user.is_active is True
    assert user.is_suspended is False
    assert user.check_password("MotDePasseSolide123!") is True
    assert user.password != "MotDePasseSolide123!"

    subscription = Subscription.objects.get(user=user)
    assert subscription.plan_id == free_plan.id
    assert subscription.status == SubscriptionStatus.ACTIVE
    assert subscription.current_period_start is not None
    assert subscription.current_period_end is None
    assert subscription.cancel_at_period_end is False

    branding = BrandingSettings.objects.get(user=user)
    assert branding.custom_domain == ""
    assert branding.logo_url == ""
    assert branding.favicon_url == ""
    assert branding.watermark_enabled is True
    assert branding.watermark_text == "Pixeo"

    homepage = HomepageSettings.objects.get(user=user)
    assert homepage.enabled is True
    assert homepage.biography == ""
    assert homepage.brand_name == "studio-photo"

    # Aucune session n'est créée par l'inscription.
    assert settings.AUTH_REFRESH_COOKIE_NAME not in response.cookies
    assert "sessionid" not in response.cookies
    assert "accessToken" not in payload["data"]
    assert "refresh" not in response.content.decode().lower()
    assert not OutstandingToken.objects.filter(user=user).exists()

    # Le compte peut se connecter via l'endpoint A5 existant.
    login_response = login(
        api_client,
        "photographe@example.com",
        "MotDePasseSolide123!",
    )
    assert login_response.status_code == 200
    assert login_response.json()["data"]["user"]["role"] == "photographer"
    assert refresh_cookie(login_response) is not None


@pytest.mark.parametrize(
    "payload",
    [
        registration_payload(email="not-an-email"),
        registration_payload(
            password="short",
            passwordConfirmation="short",
        ),
        registration_payload(
            password="12345678",
            passwordConfirmation="12345678",
        ),
        registration_payload(passwordConfirmation="DifferentPassword123!"),
        registration_payload(brandingUsername="bad_name"),
        registration_payload(brandingUsername="-bad"),
        registration_payload(brandingUsername="bad-"),
        registration_payload(brandingUsername="a" * 64),
        registration_payload(brandingUsername="admin"),
        {},
    ],
)
def test_invalid_registration_payload_is_rejected(api_client, payload):
    response = register(api_client, payload)

    assert response.status_code == 400
    assert response.json()["ok"] is False
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert User.objects.count() == 0


def test_duplicate_email_is_case_insensitive_and_rejected(api_client):
    User.objects.create_user(
        email="existing@example.com",
        password=PASSWORD,
        branding_username="existing-user",
    )

    response = register(
        api_client,
        registration_payload(
            email="EXISTING@EXAMPLE.COM",
            brandingUsername="new-user",
        ),
    )

    assert response.status_code == 400
    details = response.json()["details"]
    assert details == {
        "nonFieldErrors": ["Un compte avec ces informations existe déjà."]
    }
    assert "email" not in details
    assert User.objects.filter(email="existing@example.com").count() == 1


def test_duplicate_branding_username_is_case_insensitive(api_client):
    User.objects.create_user(
        email="existing@example.com",
        password=PASSWORD,
        branding_username="studio-photo",
    )

    response = register(
        api_client,
        registration_payload(
            email="new@example.com",
            brandingUsername="Studio-Photo",
        ),
    )

    assert response.status_code == 400
    details = response.json()["details"]
    assert details == {
        "nonFieldErrors": ["Un compte avec ces informations existe déjà."]
    }
    assert "brandingUsername" not in details
    assert User.objects.count() == 1


def test_duplicate_email_and_branding_return_the_same_generic_error(api_client):
    User.objects.create_user(
        email="existing@example.com",
        password=PASSWORD,
        branding_username="studio-photo",
    )

    email_conflict = register(
        api_client,
        registration_payload(
            email="existing@example.com",
            brandingUsername="new-user",
        ),
    )
    branding_conflict = register(
        api_client,
        registration_payload(
            email="new@example.com",
            brandingUsername="studio-photo",
        ),
    )

    assert email_conflict.status_code == 400
    assert branding_conflict.status_code == 400
    assert email_conflict.json()["details"] == branding_conflict.json()["details"]


def test_invalid_email_format_keeps_a_field_specific_error(api_client):
    response = register(
        api_client,
        registration_payload(email="not-an-email"),
    )

    assert response.status_code == 400
    details = response.json()["details"]
    assert "email" in details
    assert "nonFieldErrors" not in details


def test_invalid_branding_format_keeps_a_field_specific_error(api_client):
    response = register(
        api_client,
        registration_payload(brandingUsername="bad_name"),
    )

    assert response.status_code == 400
    details = response.json()["details"]
    assert "brandingUsername" in details
    assert "nonFieldErrors" not in details


@pytest.mark.parametrize(
    "extra_fields",
    [
        {"role": "platform_admin"},
        {"isStaff": True},
        {"is_staff": True},
        {"isSuperuser": True},
        {"is_superuser": True},
        {"planId": "studio"},
    ],
)
def test_privileged_or_unknown_fields_are_rejected(api_client, extra_fields):
    response = register(api_client, registration_payload(**extra_fields))

    assert response.status_code == 400
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert User.objects.count() == 0


def test_registration_does_not_expose_password_or_hash(api_client, free_plan):
    raw_password = "MotDePasseSolide123!"
    response = register(
        api_client,
        registration_payload(password=raw_password),
    )

    assert response.status_code == 201
    user = User.objects.get(email="photographe@example.com")
    body = response.content.decode()
    assert raw_password not in body
    assert user.password not in body
    assert "password" not in body.lower()
    assert "hash" not in body.lower()


def test_registration_does_not_log_password_or_hash(
    api_client, free_plan
):
    records: list[str] = []

    class CaptureHandler(logging.Handler):
        def emit(self, record):
            records.append(record.getMessage())

    handler = CaptureHandler()
    loggers = [
        logging.getLogger("django.db.backends"),
        logging.getLogger("django.request"),
        logging.getLogger("pixeo"),
        logging.getLogger("pixeo.api"),
    ]
    for logger in loggers:
        logger.addHandler(handler)

    raw_password = "MotDePasseSolide123!"
    try:
        response = register(
            api_client,
            registration_payload(password=raw_password),
        )
    finally:
        for logger in loggers:
            logger.removeHandler(handler)

    assert response.status_code == 201
    user = User.objects.get(email="photographe@example.com")
    logs = "\n".join(records)
    assert raw_password not in logs
    assert user.password not in logs


@pytest.mark.parametrize(
    "content_type",
    [
        "application/x-www-form-urlencoded",
        "text/plain",
        "multipart/form-data",
    ],
)
def test_registration_rejects_non_json_content_types(
    api_client, content_type
):
    response = api_client.post(
        REGISTER_URL,
        registration_payload(),
        content_type=content_type,
    )

    assert response.status_code == 415
    assert response.json()["code"] == "UNSUPPORTED_MEDIA_TYPE"
    assert User.objects.count() == 0


def test_registration_preflight_allows_trusted_origin(api_client):
    response = api_client.options(
        REGISTER_URL,
        HTTP_ORIGIN="http://app.lvh.me:3000",
        HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        HTTP_ACCESS_CONTROL_REQUEST_HEADERS="content-type",
    )

    assert response["Access-Control-Allow-Origin"] == "http://app.lvh.me:3000"
    assert response["Access-Control-Allow-Credentials"] == "true"
    assert "POST" in response["Access-Control-Allow-Methods"]


def test_registration_preflight_rejects_untrusted_origin(api_client):
    response = api_client.options(
        REGISTER_URL,
        HTTP_ORIGIN="https://evil.example",
        HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        HTTP_ACCESS_CONTROL_REQUEST_HEADERS="content-type",
    )

    assert "Access-Control-Allow-Origin" not in response


def test_registration_is_rate_limited(api_client, monkeypatch):
    monkeypatch.setattr(
        AuthRegisterThrottle,
        "rate",
        "2/min",
        raising=False,
    )

    first = register(api_client, {})
    second = register(api_client, {})
    third = register(api_client, {})

    assert first.status_code == 400
    assert second.status_code == 400
    assert third.status_code == 429
    assert third.json()["code"] == "RATE_LIMITED"
    assert "Retry-After" in third


@pytest.mark.parametrize(
    "model",
    [Subscription, BrandingSettings, HomepageSettings],
)
def test_registration_rolls_back_if_a_studio_step_fails(
    monkeypatch, free_plan, model
):
    def fail_create(*args, **kwargs):
        raise RuntimeError("simulated creation failure")

    monkeypatch.setattr(model.objects, "create", fail_create)

    with pytest.raises(RuntimeError):
        register_photographer(
            email="rollback@example.com",
            password="MotDePasseSolide123!",
            branding_username="rollback-user",
        )

    assert not User.objects.filter(email="rollback@example.com").exists()
    assert not Subscription.objects.filter(
        user__email="rollback@example.com"
    ).exists()
    assert not BrandingSettings.objects.filter(
        user__email="rollback@example.com"
    ).exists()
    assert not HomepageSettings.objects.filter(
        user__email="rollback@example.com"
    ).exists()


def test_registration_service_maps_insert_race_to_conflict(
    monkeypatch, free_plan
):
    def fail_create(*args, **kwargs):
        raise IntegrityError("duplicate key value violates unique constraint")

    monkeypatch.setattr(User.objects, "create_user", fail_create)

    with pytest.raises(RegistrationConflict):
        register_photographer(
            email="race@example.com",
            password="MotDePasseSolide123!",
            branding_username="race-user",
        )

    assert not User.objects.filter(email="race@example.com").exists()


def test_registration_service_maps_existing_account_to_conflict(free_plan):
    User.objects.create_user(
        email="existing@example.com",
        password=PASSWORD,
        branding_username="existing-user",
    )

    with pytest.raises(RegistrationConflict):
        register_photographer(
            email="existing@example.com",
            password="MotDePasseSolide123!",
            branding_username="new-user",
        )

    assert User.objects.count() == 1


def test_registration_endpoint_maps_conflict_to_409(api_client, monkeypatch):
    def raise_conflict(**kwargs):
        raise RegistrationConflict()

    monkeypatch.setattr(
        "apps.accounts.registration.views.register_photographer",
        raise_conflict,
    )

    response = register(api_client)

    assert response.status_code == 409
    assert response.json()["code"] == "CONFLICT"
    assert User.objects.count() == 0


def test_registration_returns_503_without_free_plan(api_client, free_plan):
    Plan.objects.filter(code="free").delete()

    response = register(api_client)

    assert response.status_code == 503
    assert response.json()["code"] == "NOT_CONFIGURED"
    assert User.objects.count() == 0
    assert Subscription.objects.count() == 0


def test_registration_returns_503_with_inactive_free_plan(
    api_client, free_plan
):
    free_plan.is_active = False
    free_plan.save(update_fields=["is_active"])

    response = register(api_client)

    assert response.status_code == 503
    assert response.json()["code"] == "NOT_CONFIGURED"
    assert User.objects.count() == 0
    assert Subscription.objects.count() == 0
    free_plan.refresh_from_db()
    assert free_plan.is_active is False


def test_registration_reads_free_plan_inside_the_transaction(
    monkeypatch, free_plan
):
    from django.db import connection

    from apps.accounts.registration import services

    original_get_free_plan = services.get_free_plan
    observed = {}

    def wrapped_get_free_plan():
        observed["in_atomic"] = connection.in_atomic_block
        return original_get_free_plan()

    monkeypatch.setattr(services, "get_free_plan", wrapped_get_free_plan)

    register_photographer(
        email="atomic-plan@example.com",
        password="MotDePasseSolide123!",
        branding_username="atomic-plan",
    )

    assert observed == {"in_atomic": True}


def test_registration_endpoint_returns_generic_error_on_failure(
    api_client, free_plan, monkeypatch
):
    def fail_create(*args, **kwargs):
        raise RuntimeError("simulated creation failure")

    monkeypatch.setattr(BrandingSettings.objects, "create", fail_create)

    response = register(api_client)

    assert response.status_code == 500
    assert response.json() == {
        "ok": False,
        "error": "Une erreur interne est survenue.",
        "code": "INTERNAL_ERROR",
        "details": {},
    }
    assert not User.objects.filter(email="photographe@example.com").exists()


def test_free_plan_is_the_only_initial_subscription(api_client, free_plan):
    Plan.objects.get_or_create(
        code="starter",
        defaults={
            "name": "Starter",
            "price_monthly_fcfa": 2000,
            "storage_limit_bytes": 50 * 1024 * 1024 * 1024,
        },
    )

    response = register(api_client)

    assert response.status_code == 201
    user = User.objects.get(email="photographe@example.com")
    assert Subscription.objects.filter(user=user).count() == 1
    assert Subscription.objects.get(user=user).plan.code == "free"
