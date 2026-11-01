"""Tests de validation et de normalisation de `branding_username`."""

from __future__ import annotations

import pytest
from django.core.exceptions import ValidationError

from apps.accounts.models import User
from apps.accounts.validators import (
    RESERVED_BRANDING_USERNAMES,
    normalize_branding_username,
    validate_branding_username,
)


@pytest.mark.parametrize(
    "value",
    [
        "yves",
        "studio-42",
        "a",
        "a-b",
        "a" * 63,
    ],
)
def test_valid_branding_usernames(value):
    validate_branding_username(value)


@pytest.mark.parametrize(
    "value",
    [
        "",
        "Yves",
        "yves studio",
        "yves_studio",
        "yves.studio",
        "-yves",
        "yves-",
        "a" * 64,
        "é",
        "yves!",
        "yves@example",
    ],
)
def test_invalid_branding_usernames(value):
    with pytest.raises(ValidationError):
        validate_branding_username(value)


@pytest.mark.parametrize("value", sorted(RESERVED_BRANDING_USERNAMES))
def test_reserved_branding_usernames_are_rejected(value):
    with pytest.raises(ValidationError):
        validate_branding_username(value)


@pytest.mark.parametrize(
    "value",
    ["app", "admin", "api", "www", "cdn", "mail", "static", "media"],
)
def test_required_reserved_names_are_present(value):
    assert value in RESERVED_BRANDING_USERNAMES


def test_normalize_branding_username():
    assert normalize_branding_username("  YVES  ") == "yves"
    assert normalize_branding_username("Studio-42") == "studio-42"


def test_model_normalizes_branding_username_and_email():
    user = User(
        email="Test@Example.COM",
        branding_username="  YVES  ",
    )
    user.set_password("a-strong-password")

    user.clean_fields()

    assert user.branding_username == "yves"
    assert user.email == "test@example.com"


@pytest.mark.parametrize(
    "value",
    ["admin", "yves_studio", "yves studio", "-yves", "a" * 64],
)
def test_model_clean_fields_rejects_invalid_values(value):
    user = User(email="test@example.com", branding_username=value)
    user.set_password("a-strong-password")

    with pytest.raises(ValidationError):
        user.clean_fields()


def test_model_clean_fields_rejects_blank_branding_username():
    user = User(email="test@example.com", branding_username="")
    user.set_password("a-strong-password")

    with pytest.raises(ValidationError):
        user.clean_fields()
