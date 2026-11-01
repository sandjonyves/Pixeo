"""Tests de la configuration Django Admin du modèle utilisateur."""

from __future__ import annotations

import pytest
from django.contrib import admin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.test import Client
from django.urls import reverse

from apps.accounts.forms import PixeoUserChangeForm, PixeoUserCreationForm
from apps.accounts.models import User, UserRole

pytestmark = pytest.mark.django_db


@pytest.fixture
def superuser():
    return User.objects.create_superuser(
        email="admin@example.com",
        password="a-strong-password",
        branding_username="pixeo-admin",
    )


@pytest.fixture
def admin_client(superuser):
    client = Client()
    client.force_login(superuser)
    return client


def test_user_is_registered_in_admin():
    assert admin.site.is_registered(User)


def test_admin_index_requires_staff(client):
    response = client.get(reverse("admin:index"))
    assert response.status_code == 302


def test_admin_index_is_accessible(admin_client):
    response = admin_client.get(reverse("admin:index"))
    assert response.status_code == 200


def test_user_changelist_search_and_filters(admin_client):
    User.objects.create_user(
        email="alice@example.com",
        password="a-strong-password",
        branding_username="alice",
    )
    suspended = User.objects.create_user(
        email="bob@example.com",
        password="a-strong-password",
        branding_username="bob",
    )
    suspended.is_suspended = True
    suspended.save()

    changelist = reverse("admin:accounts_user_changelist")

    response = admin_client.get(changelist, {"q": "alice@example.com"})
    assert response.status_code == 200
    assert b"alice@example.com" in response.content
    assert b"bob@example.com" not in response.content

    response = admin_client.get(changelist, {"role": "photographer"})
    assert response.status_code == 200
    assert b"alice@example.com" in response.content
    assert b"bob@example.com" in response.content

    response = admin_client.get(changelist, {"status": "suspended"})
    assert response.status_code == 200
    assert b"bob@example.com" in response.content
    assert b"alice@example.com" not in response.content


def test_change_form_password_is_read_only():
    user = User.objects.create_user(
        email="readonly@example.com",
        password="a-strong-password",
        branding_username="readonly-user",
    )

    form = PixeoUserChangeForm(instance=user)

    assert isinstance(form.fields["password"], ReadOnlyPasswordHashField)
    assert form.fields["password"].disabled is True


def test_change_page_does_not_expose_password_hash(admin_client):
    user = User.objects.create_user(
        email="change-page@example.com",
        password="a-strong-password",
        branding_username="change-page-user",
    )

    response = admin_client.get(
        reverse("admin:accounts_user_change", args=[user.pk])
    )

    assert response.status_code == 200
    content = response.content.decode()
    assert user.password not in content
    assert "password/" in content


def test_admin_change_rejects_superuser_with_non_admin_role(admin_client):
    user = User.objects.create_user(
        email="role-check@example.com",
        password="a-strong-password",
        branding_username="role-check",
    )

    response = admin_client.post(
        reverse("admin:accounts_user_change", args=[user.pk]),
        {
            "email": user.email,
            "branding_username": user.branding_username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": UserRole.PHOTOGRAPHER,
            "is_active": "on",
            "is_superuser": "on",
            "_save": "Save",
        },
    )

    assert response.status_code == 200
    assert "role" in response.context["adminform"].form.errors

    user.refresh_from_db()
    assert user.is_superuser is False


def test_creation_form_hashes_password_and_normalizes_branding():
    form = PixeoUserCreationForm(
        data={
            "email": "New.User@Example.COM",
            "branding_username": "  New-User  ",
            "first_name": "New",
            "last_name": "User",
            "role": UserRole.PHOTOGRAPHER,
            "is_active": True,
            "is_suspended": False,
            "password1": "a-strong-password",
            "password2": "a-strong-password",
        }
    )

    assert form.is_valid(), form.errors
    user = form.save()

    assert user.email == "new.user@example.com"
    assert user.branding_username == "new-user"
    assert user.check_password("a-strong-password") is True
    assert user.password != "a-strong-password"


def test_admin_add_view_creates_hashed_user(admin_client):
    response = admin_client.post(
        reverse("admin:accounts_user_add"),
        {
            "email": "admin-created@example.com",
            "branding_username": "admin-created",
            "first_name": "Admin",
            "last_name": "Created",
            "role": UserRole.PHOTOGRAPHER,
            "is_active": "on",
            "password1": "a-strong-password",
            "password2": "a-strong-password",
            "_save": "Save",
        },
    )

    assert response.status_code == 302
    user = User.objects.get(email="admin-created@example.com")
    assert user.branding_username == "admin-created"
    assert user.check_password("a-strong-password") is True
    assert user.role == UserRole.PHOTOGRAPHER
