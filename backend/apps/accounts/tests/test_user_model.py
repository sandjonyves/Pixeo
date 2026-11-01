"""Tests du modèle utilisateur Pixeo et de son manager."""

from __future__ import annotations

import pytest
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.accounts.models import User, UserRole, UserStatus

pytestmark = pytest.mark.django_db


def test_auth_user_model_points_to_custom_user():
    assert settings.AUTH_USER_MODEL == "accounts.User"
    assert get_user_model() is User


def test_user_uses_email_as_username_field():
    assert User.USERNAME_FIELD == "email"
    assert User.REQUIRED_FIELDS == ["branding_username"]
    assert "username" not in {field.name for field in User._meta.get_fields()}


def test_user_has_uuid_primary_key():
    field = User._meta.get_field("id")
    assert field.primary_key is True
    assert field.get_internal_type() == "UUIDField"


def test_branding_username_is_unique_and_bounded():
    field = User._meta.get_field("branding_username")
    assert field.unique is True
    assert field.max_length == 63


def test_email_is_unique():
    field = User._meta.get_field("email")
    assert field.unique is True


def test_create_user_normalizes_identifiers_and_hashes_password():
    user = User.objects.create_user(
        email="Test.User@Example.COM",
        password="a-strong-password",
        branding_username="  YVES  ",
    )

    assert user.email == "test.user@example.com"
    assert user.branding_username == "yves"
    assert user.check_password("a-strong-password") is True
    assert user.password != "a-strong-password"
    assert user.status == UserStatus.ACTIVE
    assert str(user) == "test.user@example.com"


def test_status_property_reflects_suspension_and_inactivity():
    user = User.objects.create_user(
        email="status@example.com",
        password="a-strong-password",
        branding_username="status-user",
    )
    assert user.status == UserStatus.ACTIVE

    user.is_suspended = True
    # La suspension métier ne désactive pas `is_active` : le contrôle d'accès
    # C5 devra donc vérifier explicitement `is_suspended` à chaque requête.
    assert user.is_active is True
    assert user.status == UserStatus.SUSPENDED

    user.is_suspended = False
    user.is_active = False
    assert user.status == UserStatus.INACTIVE


def test_update_normalizes_identifiers():
    user = User.objects.create_user(
        email="original@example.com",
        password="a-strong-password",
        branding_username="original-name",
    )

    user.email = "  Updated@Example.COM "
    user.branding_username = "  NEW-NAME  "
    user.save()

    user.refresh_from_db()
    assert user.email == "updated@example.com"
    assert user.branding_username == "new-name"


def test_create_superuser_sets_admin_role_and_flags():
    admin = User.objects.create_superuser(
        email="admin@example.com",
        password="a-strong-password",
        branding_username="pixeo-admin",
    )

    assert admin.is_staff is True
    assert admin.is_superuser is True
    assert admin.role == UserRole.PLATFORM_ADMIN


def test_authenticate_by_email_is_case_insensitive():
    user = User.objects.create_user(
        email="Case.User@Example.COM",
        password="a-strong-password",
        branding_username="case-user",
    )

    assert (
        authenticate(username="CASE.USER@example.com", password="a-strong-password")
        == user
    )
    assert authenticate(username="case.user@example.com", password="wrong") is None


def test_superuser_has_platform_admin_permissions():
    admin = User.objects.create_superuser(
        email="permissions@example.com",
        password="a-strong-password",
        branding_username="permissions-admin",
    )

    assert admin.is_active is True
    assert admin.is_staff is True
    assert admin.is_superuser is True
    assert admin.role == UserRole.PLATFORM_ADMIN
    assert admin.has_perm("accounts.change_user") is True
    assert admin.has_module_perms("accounts") is True


def test_create_superuser_rejects_non_admin_role():
    with pytest.raises(ValueError):
        User.objects.create_superuser(
            email="admin@example.com",
            password="a-strong-password",
            branding_username="pixeo-admin",
            role=UserRole.PHOTOGRAPHER,
        )


def test_superuser_role_invariant_is_enforced_on_full_clean():
    user = User(
        email="invalid-admin@example.com",
        branding_username="invalid-admin",
        is_superuser=True,
        role=UserRole.PHOTOGRAPHER,
    )
    user.set_password("a-strong-password")

    with pytest.raises(ValidationError):
        user.full_clean()


def test_create_user_rejects_reserved_branding_username():
    with pytest.raises(ValidationError):
        User.objects.create_user(
            email="reserved@example.com",
            password="a-strong-password",
            branding_username="admin",
        )


def test_create_user_rejects_duplicate_branding_username():
    User.objects.create_user(
        email="first@example.com",
        password="a-strong-password",
        branding_username="studio",
    )

    with pytest.raises(ValidationError):
        User.objects.create_user(
            email="second@example.com",
            password="a-strong-password",
            branding_username="STUDIO",
        )


def test_branding_username_is_unique_at_database_level():
    User.objects.create_user(
        email="first@example.com",
        password="a-strong-password",
        branding_username="unique-name",
    )

    duplicate = User(
        email="second@example.com",
        branding_username="UNIQUE-NAME",
    )
    duplicate.set_password("a-strong-password")

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            duplicate.save()


def test_email_is_unique_at_database_level():
    User.objects.create_user(
        email="duplicate@example.com",
        password="a-strong-password",
        branding_username="first-name",
    )

    duplicate = User(
        email="DUPLICATE@example.com",
        branding_username="second-name",
    )
    duplicate.set_password("a-strong-password")

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            duplicate.save()
