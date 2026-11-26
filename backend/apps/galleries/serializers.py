"""Serializers API des galeries Pixeo."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from django.conf import settings
from rest_framework import serializers

from apps.api.serializers import (
    PixeoModelSerializer,
    PixeoSerializer,
    snakeize_keys,
    to_camel_case,
)

from .models import Gallery, GalleryStatus, Photo


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


class StrictPixeoSerializer(PixeoSerializer):
    """Serializer Pixeo qui refuse explicitement les champs inconnus."""

    def to_internal_value(self, data: Any) -> Any:
        if isinstance(data, Mapping):
            normalized = snakeize_keys(data)
            unknown = set(normalized) - set(self.fields)
            if unknown:
                raise serializers.ValidationError(
                    {
                        to_camel_case(str(field)): [
                            "Ce champ n'est pas autorisé."
                        ]
                        for field in sorted(unknown)
                    }
                )
            return super().to_internal_value(normalized)

        return super().to_internal_value(data)


class PhotoSerializer(PixeoModelSerializer):
    """Représentation publique d'une photo et de ses métadonnées."""

    url = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = (
            "id",
            "gallery_id",
            "original_filename",
            "format",
            "mime_type",
            "size_bytes",
            "width",
            "height",
            "position",
            "url",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_url(self, obj: Photo) -> str | None:
        """Retourne l'URL du fichier sans exposer la clé de stockage brute."""

        if not obj.file:
            return None

        try:
            file_url = obj.file.url
        except (AttributeError, ValueError):
            return None

        request = self.context.get("request")
        if request is not None:
            return request.build_absolute_uri(file_url)
        return file_url


class PhotoUploadSerializer(StrictPixeoSerializer):
    """Corps multipart d'import d'une ou plusieurs photos."""

    files = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        allow_empty=False,
    )
    file = serializers.FileField(required=False)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        files = list(attrs.get("files") or [])
        single_file = attrs.get("file")
        if single_file is not None:
            files.insert(0, single_file)

        if not files:
            raise serializers.ValidationError(
                {"files": ["Au moins un fichier est requis."]}
            )

        max_batch_size = max(
            1,
            int(getattr(settings, "PIXEO_PHOTO_MAX_BATCH_SIZE", 1)),
        )
        if len(files) > max_batch_size:
            raise serializers.ValidationError(
                {
                    "files": [
                        (
                            "Le nombre maximal de fichiers par requête est "
                            f"de {max_batch_size}."
                        )
                    ]
                }
            )

        attrs["files"] = files
        attrs.pop("file", None)
        return attrs


class PhotoReorderSerializer(StrictPixeoSerializer):
    """Corps de réorganisation complète des photos d'une galerie."""

    photo_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=True,
    )


class PhotoSchema(serializers.Serializer):
    """Schéma OpenAPI de la représentation publique d'une photo."""

    id = serializers.UUIDField()
    galleryId = serializers.UUIDField()
    originalFilename = serializers.CharField()
    format = serializers.CharField()
    mimeType = serializers.CharField()
    sizeBytes = serializers.IntegerField()
    width = serializers.IntegerField()
    height = serializers.IntegerField()
    position = serializers.IntegerField()
    url = serializers.URLField(allow_null=True)
    createdAt = serializers.DateTimeField()
    updatedAt = serializers.DateTimeField()


class PhotoEnvelopeSchema(serializers.Serializer):
    """Schéma OpenAPI de l'enveloppe d'une photo."""

    ok = serializers.BooleanField()
    data = PhotoSchema()


class PhotoBatchDataSchema(serializers.Serializer):
    """Données d'un import ou d'une réorganisation de plusieurs photos."""

    items = PhotoSchema(many=True)
    total = serializers.IntegerField()


class PhotoBatchResponseSchema(serializers.Serializer):
    """Enveloppe de succès d'un import ou d'une réorganisation."""

    ok = serializers.BooleanField()
    data = PhotoBatchDataSchema()


class PhotoUploadRequestSchema(serializers.Serializer):
    """Schéma OpenAPI du corps multipart d'import."""

    files = serializers.ListField(
        child=serializers.FileField(),
        required=False,
    )
    file = serializers.FileField(required=False)


class PhotoReorderRequestSchema(serializers.Serializer):
    """Schéma OpenAPI du corps de réorganisation."""

    photoIds = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=True,
    )
