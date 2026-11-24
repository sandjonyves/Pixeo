"""Serializers API des galeries Pixeo."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from rest_framework import serializers

from apps.api.serializers import (
    PixeoModelSerializer,
    snakeize_keys,
    to_camel_case,
)

from .models import Gallery, GalleryStatus


class GallerySerializer(PixeoModelSerializer):
    """Représentation d'une galerie et validation des écritures.

    Le propriétaire n'est jamais un champ du serializer : il est imposé par la
    vue à partir de ``request.user``.
    """

    class Meta:
        model = Gallery
        fields = (
            "id",
            "title",
            "slug",
            "description",
            "status",
            "published_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "status",
            "published_at",
            "created_at",
            "updated_at",
        )

    # Champs présents dans la représentation mais interdits en écriture.
    # Les déclarer ``read_only`` ne suffit pas : DRF les ignorerait sans bruit.
    FORBIDDEN_WRITE_FIELDS = {
        "id": "Ce champ est en lecture seule.",
        "status": (
            "Le statut est géré par le processus de publication et ne peut "
            "pas être modifié via le CRUD."
        ),
        "published_at": (
            "La date de première publication est gérée par le processus de "
            "publication et ne peut pas être modifiée via le CRUD."
        ),
        "created_at": "Ce champ est en lecture seule.",
        "updated_at": "Ce champ est en lecture seule.",
    }

    def to_internal_value(self, data: Any) -> Any:
        """Refuse les champs inconnus et les champs interdits en écriture."""

        if isinstance(data, Mapping):
            normalized = snakeize_keys(data)
            unknown = set(normalized) - set(self.fields)
            forbidden = set(normalized) & set(self.FORBIDDEN_WRITE_FIELDS)

            errors: dict[str, list[str]] = {}
            for field in sorted(unknown):
                errors[to_camel_case(str(field))] = [
                    "Ce champ n'est pas autorisé."
                ]
            for field in sorted(forbidden):
                errors[to_camel_case(str(field))] = [
                    self.FORBIDDEN_WRITE_FIELDS[field]
                ]
            if errors:
                raise serializers.ValidationError(errors)

            return super().to_internal_value(normalized)

        return super().to_internal_value(data)

    def validate_slug(self, value: str) -> str:
        """Vérifie l'unicité du slug dans l'espace du photographe courant."""

        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return value

        queryset = Gallery.objects.filter(
            photographer=request.user,
            slug=value,
        )
        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "Une galerie avec ce slug existe déjà."
            )
        return value


class GalleryRequestSchema(serializers.Serializer):
    """Schéma OpenAPI du corps d'écriture, en camelCase public."""

    title = serializers.CharField(max_length=150)
    slug = serializers.SlugField(max_length=100)
    description = serializers.CharField(required=False, allow_blank=True)


class GallerySchema(serializers.Serializer):
    """Schéma OpenAPI de la représentation publique d'une galerie."""

    id = serializers.UUIDField()
    title = serializers.CharField(max_length=150)
    slug = serializers.SlugField(max_length=100)
    description = serializers.CharField(allow_blank=True)
    status = serializers.ChoiceField(choices=GalleryStatus.choices)
    publishedAt = serializers.DateTimeField(allow_null=True)
    createdAt = serializers.DateTimeField()
    updatedAt = serializers.DateTimeField()


class GalleryResponseSchema(serializers.Serializer):
    """Schéma OpenAPI de l'enveloppe de succès d'une galerie."""

    ok = serializers.BooleanField()
    data = GallerySchema()
