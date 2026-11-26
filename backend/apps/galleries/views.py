"""Vues API de gestion des galeries Pixeo."""

from __future__ import annotations

import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)
from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from apps.api.pagination import PixeoPageNumberPagination
from apps.api.permissions import IsPhotographer

from .models import Gallery, GalleryStatus, Photo
from .serializers import (
    GalleryRequestSchema,
    GalleryResponseSchema,
    GallerySchema,
    GallerySerializer,
    PhotoBatchResponseSchema,
    PhotoEnvelopeSchema,
    PhotoReorderRequestSchema,
    PhotoReorderSerializer,
    PhotoSchema,
    PhotoSerializer,
    PhotoUploadRequestSchema,
    PhotoUploadSerializer,
)
from .services import (
    PhotoValidationError,
    delete_photo,
    import_photos,
    reorder_photos,
)

logger = logging.getLogger("pixeo.galleries")

SLUG_UNIQUE_CONSTRAINT = "unique_gallery_slug_per_photographer"


def _is_slug_unique_conflict(exc: IntegrityError) -> bool:
    """Identifie le conflit d'unicité du slug sur PostgreSQL et SQLite."""

    parts = [str(exc)]
    cause = exc.__cause__
    if cause is not None:
        parts.append(str(cause))

        diag = getattr(cause, "diag", None)
        constraint_name = getattr(diag, "constraint_name", None)
        if constraint_name:
            parts.append(str(constraint_name))

        constraint_name = getattr(cause, "constraint_name", None)
        if constraint_name:
            parts.append(str(constraint_name))

    text = " ".join(parts).lower()
    if SLUG_UNIQUE_CONSTRAINT.lower() in text:
        return True

    # SQLite ne nomme pas la contrainte dans le message.
    return (
        "unique constraint failed" in text
        and "photographer_id" in text
        and "slug" in text
    )

STATUS_FILTER_PARAMETER = OpenApiParameter(
    name="status",
    type=str,
    location=OpenApiParameter.QUERY,
    required=False,
    enum=list(GalleryStatus.values),
    description="Filtre les galeries du photographe par statut.",
)


@extend_schema_view(
    list=extend_schema(
        tags=["Galeries"],
        parameters=[STATUS_FILTER_PARAMETER],
        responses=GallerySchema(many=True),
        description=(
            "Liste paginée des galeries appartenant exclusivement au "
            "photographe authentifié."
        ),
    ),
    create=extend_schema(
        tags=["Galeries"],
        request=GalleryRequestSchema,
        responses={201: GalleryResponseSchema},
        description=(
            "Crée une galerie appartenant au photographe authentifié. Le "
            "propriétaire est toujours déduit de request.user et ne peut pas "
            "être fourni par le client. La galerie est toujours créée en "
            "brouillon : status et publishedAt sont refusés en écriture."
        ),
    ),
    retrieve=extend_schema(
        tags=["Galeries"],
        responses=GalleryResponseSchema,
        description=(
            "Retourne une galerie du photographe authentifié. Une galerie "
            "appartenant à un autre photographe renvoie 404."
        ),
    ),
    partial_update=extend_schema(
        tags=["Galeries"],
        request=GalleryRequestSchema,
        responses=GalleryResponseSchema,
        description=(
            "Modifie partiellement une galerie du photographe authentifié. "
            "Seuls title, slug et description sont modifiables. status et "
            "publishedAt sont gérés par le futur processus de publication et "
            "refusés dans le CRUD."
        ),
    ),
    destroy=extend_schema(
        tags=["Galeries"],
        responses={204: None},
        description=(
            "Supprime une galerie du photographe authentifié. Une galerie "
            "appartenant à un autre photographe renvoie 404."
        ),
    ),
)
class GalleryViewSet(viewsets.ModelViewSet):
    """CRUD des galeries du photographe courant.

    Le queryset est toujours filtré par ``request.user`` : une galerie d'un
    autre photographe est traitée comme inexistante. La permission
    ``IsPhotographer`` vérifie le rôle et le statut courant du compte.
    """

    # Le queryset de classe ne doit jamais exposer les galeries d'autrui.
    # La sécurité réelle est assurée par get_queryset().
    queryset = Gallery.objects.none()
    serializer_class = GallerySerializer
    permission_classes = [IsPhotographer]
    pagination_class = PixeoPageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status"]
    http_method_names = [
        "get",
        "post",
        "patch",
        "delete",
        "head",
        "options",
    ]

    def get_queryset(self):
        return Gallery.objects.filter(photographer=self.request.user)

    def get_object(self):
        """Transforme un identifiant invalide en 404 API standard."""

        try:
            return super().get_object()
        except (DjangoValidationError, ValueError) as exc:
            raise NotFound() from exc

    def perform_create(self, serializer):
        self._save_with_conflict_handling(
            serializer,
            photographer=self.request.user,
            status=GalleryStatus.DRAFT,
            published_at=None,
        )

    def perform_update(self, serializer):
        self._save_with_conflict_handling(serializer)

    def _save_with_conflict_handling(self, serializer, **kwargs):
        """Enregistre en convertissant les erreurs de base en erreurs API."""

        try:
            with transaction.atomic():
                return serializer.save(**kwargs)
        except IntegrityError as exc:
            if not _is_slug_unique_conflict(exc):
                logger.exception(
                    "Unexpected gallery integrity error"
                )
                raise

            raise ValidationError(
                {
                    "non_field_errors": [
                        "Une galerie avec ce slug existe déjà."
                    ]
                }
            ) from exc
        except DjangoValidationError as exc:
            details = getattr(exc, "message_dict", None) or {
                "non_field_errors": exc.messages
            }
            raise ValidationError(details) from exc

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"ok": True, "data": serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"ok": True, "data": serializer.data})

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"ok": True, "data": serializer.data})


@extend_schema_view(
    list=extend_schema(
        tags=["Photos"],
        responses=PhotoSchema(many=True),
        description=(
            "Liste paginée des photos d'une galerie du photographe "
            "authentifié, triées par position."
        ),
    ),
    create=extend_schema(
        tags=["Photos"],
        request=PhotoUploadRequestSchema,
        responses={201: PhotoBatchResponseSchema},
        description=(
            "Importe une ou plusieurs photos dans une galerie du photographe. "
            "Le corps est multipart avec le champ répétable `files` ou le "
            "champ unique `file`. Les fichiers sont validés avant toute "
            "écriture ; un lot invalide ne crée aucune photo."
        ),
    ),
    retrieve=extend_schema(
        tags=["Photos"],
        responses=PhotoEnvelopeSchema,
        description=(
            "Retourne les métadonnées d'une photo d'une galerie du "
            "photographe authentifié. Une photo d'un autre photographe ou "
            "d'une autre galerie renvoie 404."
        ),
    ),
    destroy=extend_schema(
        tags=["Photos"],
        responses={204: None},
        description=(
            "Supprime une photo de la galerie et son fichier stocké. Les "
            "positions restantes sont compactées."
        ),
    ),
)
class GalleryPhotoViewSet(viewsets.GenericViewSet):
    """Import, lecture, suppression et ordre des photos d'une galerie.

    Le queryset est toujours filtré par ``gallery__photographer=request.user``
    et par l'identifiant de galerie du chemin. Une galerie ou une photo d'un
    autre photographe est traitée comme inexistante.
    """

    queryset = Photo.objects.none()
    serializer_class = PhotoSerializer
    permission_classes = [IsPhotographer]
    pagination_class = PixeoPageNumberPagination
    lookup_field = "id"
    lookup_url_kwarg = "photo_id"
    filter_backends: list = []
    http_method_names = [
        "get",
        "post",
        "patch",
        "delete",
        "head",
        "options",
    ]

    def get_gallery(self) -> Gallery:
        """Retourne la galerie du photographe ou lève un 404 standard."""

        try:
            return Gallery.objects.get(
                pk=self.kwargs.get("gallery_id"),
                photographer=self.request.user,
            )
        except (
            Gallery.DoesNotExist,
            DjangoValidationError,
            ValueError,
        ) as exc:
            raise NotFound() from exc

    def get_queryset(self):
        return Photo.objects.filter(
            gallery__photographer=self.request.user,
            gallery_id=self.kwargs.get("gallery_id"),
        ).select_related("gallery")

    def list(self, request, *args, **kwargs):
        self.get_gallery()
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "ok": True,
                "data": {
                    "items": serializer.data,
                    "total": queryset.count(),
                },
            }
        )

    def create(self, request, *args, **kwargs):
        gallery = self.get_gallery()
        upload_serializer = PhotoUploadSerializer(data=request.data)
        upload_serializer.is_valid(raise_exception=True)

        try:
            photos = import_photos(
                gallery,
                upload_serializer.validated_data["files"],
            )
        except PhotoValidationError as exc:
            raise ValidationError(exc.details) from exc
        except Gallery.DoesNotExist as exc:
            raise NotFound() from exc

        serializer = self.get_serializer(photos, many=True)
        return Response(
            {
                "ok": True,
                "data": {
                    "items": serializer.data,
                    "total": len(photos),
                },
            },
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, *args, **kwargs):
        photo = self.get_object()
        serializer = self.get_serializer(photo)
        return Response({"ok": True, "data": serializer.data})

    def destroy(self, request, *args, **kwargs):
        photo = self.get_object()
        try:
            delete_photo(photo)
        except Gallery.DoesNotExist as exc:
            raise NotFound() from exc

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        tags=["Photos"],
        request=PhotoReorderRequestSchema,
        responses={200: PhotoBatchResponseSchema},
        description=(
            "Réordonne toutes les photos d'une galerie. Le corps contient "
            "`photoIds`, la liste complète des identifiants dans le nouvel "
            "ordre. Une liste partielle, un doublon ou une photo étrangère "
            "renvoie 400."
        ),
    )
    def reorder(self, request, *args, **kwargs):
        gallery = self.get_gallery()
        serializer = PhotoReorderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            photos = reorder_photos(
                gallery,
                serializer.validated_data["photo_ids"],
            )
        except PhotoValidationError as exc:
            raise ValidationError(exc.details) from exc
        except Gallery.DoesNotExist as exc:
            raise NotFound() from exc

        output = self.get_serializer(photos, many=True)
        return Response(
            {
                "ok": True,
                "data": {
                    "items": output.data,
                    "total": len(photos),
                },
            }
        )
