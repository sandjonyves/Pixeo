"""Vérifications réelles du schéma de la table utilisateur.

Ces tests s'exécutent sur la base configurée (PostgreSQL en développement,
SQLite en mémoire pour les tests unitaires isolés).
"""

from __future__ import annotations

import pytest
from django.db import connection

pytestmark = pytest.mark.django_db


def test_accounts_user_table_exists():
    assert "accounts_user" in connection.introspection.table_names()


def test_accounts_user_constraints_are_present():
    with connection.cursor() as cursor:
        constraints = connection.introspection.get_constraints(
            cursor, "accounts_user"
        )

    unique_columns = {
        tuple(constraint["columns"])
        for constraint in constraints.values()
        if constraint.get("unique")
    }
    primary_key_columns = {
        tuple(constraint["columns"])
        for constraint in constraints.values()
        if constraint.get("primary_key")
    }

    assert ("email",) in unique_columns
    assert ("branding_username",) in unique_columns
    assert ("id",) in primary_key_columns
