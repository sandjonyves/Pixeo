"""Tests de la migration initiale de l'application accounts."""

from __future__ import annotations

import importlib

import pytest
from django.core.management import call_command
from django.db import migrations, models

pytestmark = pytest.mark.django_db


def _initial_migration():
    return importlib.import_module("apps.accounts.migrations.0001_initial")


def test_initial_migration_creates_custom_user():
    migration = _initial_migration()

    assert migration.Migration.initial is True
    assert ("auth", "0012_alter_user_first_name_max_length") in (
        migration.Migration.dependencies
    )

    create_user = [
        operation
        for operation in migration.Migration.operations
        if isinstance(operation, migrations.CreateModel)
        and operation.name == "User"
    ]
    assert len(create_user) == 1

    fields = dict(create_user[0].fields)
    assert isinstance(fields["id"], models.UUIDField)
    assert fields["id"].primary_key is True
    assert fields["email"].unique is True
    assert fields["branding_username"].unique is True
    assert fields["branding_username"].max_length == 63
    assert create_user[0].managers[0][0] == "objects"


def test_no_pending_model_changes():
    call_command(
        "makemigrations",
        "--check",
        "--dry-run",
        verbosity=0,
    )
