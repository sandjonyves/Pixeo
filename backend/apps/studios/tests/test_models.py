"""Tests des paramètres de studio Pixeo."""

from __future__ import annotations

import pytest
from django.db import IntegrityError, transaction

from apps.accounts.models import User
from apps.studios.models import BrandingSettings, HomepageSettings

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user(
        email="studio@example.com",
        password="StrongPassword123!",
        branding_username="studio-user",
    )


def test_branding_settings_defaults(user):
    settings = BrandingSettings.objects.create(user=user)

    assert settings.custom_domain == ""
    assert settings.logo_url == ""
    assert settings.favicon_url == ""
    assert settings.watermark_enabled is False
    assert settings.watermark_text == "Pixeo"


def test_homepage_settings_defaults(user):
    settings = HomepageSettings.objects.create(user=user)

    assert settings.enabled is True
    assert settings.biography == ""
    assert settings.brand_name == ""


def test_branding_settings_are_one_to_one(user):
    BrandingSettings.objects.create(user=user)

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            BrandingSettings.objects.create(user=user)


def test_homepage_settings_are_one_to_one(user):
    HomepageSettings.objects.create(user=user)

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            HomepageSettings.objects.create(user=user)
