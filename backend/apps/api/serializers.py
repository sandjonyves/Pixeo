"""Conventions de sérialisation de l'API Pixeo.

Les modèles et les serializers Django restent en ``snake_case``. Ce module
applique la conversion ``camelCase`` au niveau des serializers, à l'entrée comme
à la sortie, y compris pour les structures imbriquées et les erreurs de
validation.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from django.http import QueryDict
from rest_framework import serializers


def to_camel_case(value: str) -> str:
    """Convertit un identifiant ``snake_case`` en ``camelCase``.

    Une valeur déjà en camelCase est laissée inchangée, ce qui rend la
    conversion idempotente pour les structures imbriquées.
    """

    if not value:
        return value

    first, *rest = value.split("_")
    return first + "".join(
        part[:1].upper() + part[1:] for part in rest if part
    )


def to_snake_case(value: str) -> str:
    """Convertit un identifiant ``camelCase`` en ``snake_case``."""

    if not value:
        return value

    value = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", value)
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    return value.lower()


def camelize_keys(value: Any) -> Any:
    """Convertit récursivement les clés d'une structure en camelCase."""

    if isinstance(value, Mapping):
        return {
            to_camel_case(str(key)): camelize_keys(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [camelize_keys(item) for item in value]
    return value


def snakeize_keys(value: Any) -> Any:
    """Convertit récursivement les clés d'une structure en snake_case.

    ``QueryDict`` est traité séparément afin de préserver les valeurs
    multiples des formulaires et des uploads multipart.
    """

    if isinstance(value, QueryDict):
        converted = QueryDict(mutable=True)
        for key, values in value.lists():
            converted.setlist(to_snake_case(str(key)), values)
        return converted
    if isinstance(value, Mapping):
        return {
            to_snake_case(str(key)): snakeize_keys(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [snakeize_keys(item) for item in value]
    return value


class CamelCaseSerializerMixin:
    """Applique la convention JSON camelCase à un serializer DRF."""

    def to_representation(self, instance: Any) -> Any:
        representation = super().to_representation(instance)
        return camelize_keys(representation)

    def to_internal_value(self, data: Any) -> Any:
        return super().to_internal_value(snakeize_keys(data))


class PixeoSerializer(CamelCaseSerializerMixin, serializers.Serializer):
    """Serializer de base pour les payloads JSON Pixeo."""


class PixeoModelSerializer(CamelCaseSerializerMixin, serializers.ModelSerializer):
    """Serializer de base pour les modèles Django Pixeo."""


class PixeoRootSerializer(PixeoSerializer):
    """Schéma de la racine versionnée de l'API."""

    ok = serializers.BooleanField()
    data = serializers.DictField(child=serializers.URLField())
