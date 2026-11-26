"""Services métier d'import et d'ordre des photos Pixeo.

Les vues restent minces. Ce module centralise la validation des fichiers, la
lecture des métadonnées, l'écriture dans le backend de stockage Django et la
cohérence des positions dans une galerie.

Le stockage utilisé est celui de ``default_storage`` via le champ
``Photo.file``. Le passage de ``STORAGE_BACKEND=local`` à S3/R2 ne change donc
pas la logique métier.
"""

from __future__ import annotations

import hashlib
import logging
import warnings
import uuid
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any, Iterable

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import F, Max
from PIL import Image, UnidentifiedImageError

from .models import (
    PHOTO_ALLOWED_FORMATS,
    PHOTO_FORMAT_EXTENSIONS,
    PHOTO_FORMAT_MIME_TYPES,
    Gallery,
    Photo,
)

logger = logging.getLogger("pixeo.galleries")


class PhotoValidationError(Exception):
    """Erreur de validation d'un fichier ou d'un ordre de photos."""

    def __init__(self, details: dict[str, list[str]]):
        super().__init__("Photo validation failed")
        self.details = details


@dataclass(frozen=True)
class ValidatedPhoto:
    """Contenu et métadonnées d'un fichier validé avant écriture."""

    data: bytes
    original_filename: str
    format: str
    mime_type: str
    extension: str
    size_bytes: int
    width: int
    height: int
    checksum_sha256: str


def _max_upload_size() -> int:
    return max(1, int(getattr(settings, "PIXEO_PHOTO_MAX_UPLOAD_SIZE", 0)))


def _max_batch_size() -> int:
    return max(1, int(getattr(settings, "PIXEO_PHOTO_MAX_BATCH_SIZE", 1)))


def _max_pixels() -> int:
    return max(1, int(getattr(settings, "PIXEO_PHOTO_MAX_PIXELS", 1)))


def _safe_original_filename(uploaded_file: Any) -> str:
    """Retourne un nom d'origine informatif, jamais utilisé comme chemin."""

    raw_name = str(getattr(uploaded_file, "name", "") or "photo")
    basename = raw_name.replace("\\", "/").rsplit("/", 1)[-1]
    basename = basename.replace("\x00", "").strip()
    return (basename or "photo")[:255]


def _read_upload(uploaded_file: Any, display_name: str) -> bytes:
    """Lit le fichier en mémoire après vérification de sa taille annoncée."""

    announced_size = getattr(uploaded_file, "size", None)
    if isinstance(announced_size, int) and announced_size > _max_upload_size():
        raise PhotoValidationError(
            {
                "files": [
                    (
                        f"Le fichier « {display_name} » dépasse la taille "
                        f"maximale de {_max_upload_size()} octets."
                    )
                ]
            }
        )

    try:
        uploaded_file.seek(0)
    except (AttributeError, OSError):
        pass

    try:
        data = uploaded_file.read()
    except (AttributeError, OSError) as exc:
        raise PhotoValidationError(
            {
                "files": [
                    f"Le fichier « {display_name} » n'a pas pu être lu."
                ]
            }
        ) from exc

    if not isinstance(data, bytes):
        data = bytes(data)

    if not data:
        raise PhotoValidationError(
            {"files": [f"Le fichier « {display_name} » est vide."]}
        )

    if len(data) > _max_upload_size():
        raise PhotoValidationError(
            {
                "files": [
                    (
                        f"Le fichier « {display_name} » dépasse la taille "
                        f"maximale de {_max_upload_size()} octets."
                    )
                ]
            }
        )

    return data


def validate_photo(uploaded_file: Any) -> ValidatedPhoto:
    """Valide un fichier et extrait ses métadonnées.

    Le format est détecté depuis le contenu. L'extension et le Content-Type
    annoncés par le client ne sont pas utilisés pour décider du format.
    """

    original_filename = _safe_original_filename(uploaded_file)
    data = _read_upload(uploaded_file, original_filename)

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(data)) as image:
                detected_format = (image.format or "").upper()
                width, height = image.size

                if detected_format not in PHOTO_ALLOWED_FORMATS:
                    raise PhotoValidationError(
                        {
                            "files": [
                                (
                                    f"Le format de « {original_filename} » "
                                    "n'est pas autorisé. Formats acceptés : "
                                    "JPEG, PNG et WEBP."
                                )
                            ]
                        }
                    )

                if width <= 0 or height <= 0:
                    raise PhotoValidationError(
                        {
                            "files": [
                                (
                                    f"Les dimensions de « {original_filename} » "
                                    "sont invalides."
                                )
                            ]
                        }
                    )

                if width * height > _max_pixels():
                    raise PhotoValidationError(
                        {
                            "files": [
                                (
                                    f"L'image « {original_filename} » dépasse "
                                    "le nombre maximal de pixels autorisé."
                                )
                            ]
                        }
                    )

                # ``verify()`` contrôle l'intégrité structurelle ; ``load()``
                # force le décodage des données pour détecter les fichiers
                # tronqués ou corrompus.
                image.verify()

            with Image.open(BytesIO(data)) as image:
                image.load()
    except PhotoValidationError:
        raise
    except (
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
        UnidentifiedImageError,
        OSError,
        ValueError,
    ) as exc:
        raise PhotoValidationError(
            {
                "files": [
                    (
                        f"Le fichier « {original_filename} » n'est pas une "
                        "image valide."
                    )
                ]
            }
        ) from exc

    extension = PHOTO_FORMAT_EXTENSIONS[detected_format]
    mime_type = PHOTO_FORMAT_MIME_TYPES[detected_format]

    return ValidatedPhoto(
        data=data,
        original_filename=original_filename,
        format=detected_format,
        mime_type=mime_type,
        extension=extension,
        size_bytes=len(data),
        width=width,
        height=height,
        checksum_sha256=hashlib.sha256(data).hexdigest(),
    )


def validate_uploaded_files(files: Iterable[Any]) -> list[ValidatedPhoto]:
    """Valide un lot complet avant toute écriture.

    Le lot est atomique : si un fichier est invalide, aucun fichier n'est
    enregistré en stockage ni en base.
    """

    uploaded_files = list(files)
    if not uploaded_files:
        raise PhotoValidationError(
            {"files": ["Au moins un fichier est requis."]}
        )

    if len(uploaded_files) > _max_batch_size():
        raise PhotoValidationError(
            {
                "files": [
                    (
                        "Le nombre maximal de fichiers par requête est de "
                        f"{_max_batch_size()}."
                    )
                ]
            }
        )

    validated: list[ValidatedPhoto] = []
    errors: list[str] = []

    for uploaded_file in uploaded_files:
        try:
            validated.append(validate_photo(uploaded_file))
        except PhotoValidationError as exc:
            errors.extend(exc.details.get("files", ["Fichier invalide."]))

    if errors:
        raise PhotoValidationError({"files": errors})

    return validated


def _next_position(gallery: Gallery) -> int:
    current_max = gallery.photos.aggregate(max_position=Max("position"))[
        "max_position"
    ]
    return 0 if current_max is None else current_max + 1


def _delete_storage_file(storage: Any, name: str) -> None:
    """Supprime un fichier sans faire échouer une opération déjà commitée."""

    if not name:
        return

    try:
        storage.delete(name)
    except Exception:  # noqa: BLE001 - le stockage ne doit pas masquer le succès DB
        logger.exception("Failed to delete photo file %s", name)


def _cleanup_stored_files(stored_files: list[tuple[Any, str]]) -> None:
    for storage, name in stored_files:
        _delete_storage_file(storage, name)


def import_photos(gallery: Gallery, files: Iterable[Any]) -> list[Photo]:
    """Valide puis importe un lot de photos dans une galerie.

    Les fichiers sont validés avant la transaction. La galerie est verrouillée
    pendant l'attribution des positions. Les fichiers déjà écrits sont nettoyés
    si l'écriture en base échoue.
    """

    validated_photos = validate_uploaded_files(files)
    stored_files: list[tuple[Any, str]] = []

    try:
        with transaction.atomic():
            locked_gallery = Gallery.objects.select_for_update().get(
                pk=gallery.pk
            )
            start_position = _next_position(locked_gallery)
            created_photos: list[Photo] = []

            for offset, validated in enumerate(validated_photos):
                photo = Photo(
                    gallery=locked_gallery,
                    original_filename=validated.original_filename,
                    format=validated.format,
                    mime_type=validated.mime_type,
                    size_bytes=validated.size_bytes,
                    width=validated.width,
                    height=validated.height,
                    checksum_sha256=validated.checksum_sha256,
                    position=start_position + offset,
                )
                photo._storage_extension = validated.extension
                storage_name = f"{uuid.uuid4().hex}{validated.extension}"
                photo.file.save(
                    storage_name,
                    ContentFile(validated.data),
                    save=False,
                )
                stored_files.append((photo.file.storage, photo.file.name))
                photo.save()
                created_photos.append(photo)

            return created_photos
    except Exception:
        _cleanup_stored_files(stored_files)
        raise


def _compact_positions(gallery: Gallery) -> None:
    """Rend les positions contiguës après une suppression.

    Les mises à jour sont effectuées dans l'ordre croissant. La cible est
    toujours inférieure ou égale à la position courante, donc la contrainte
    d'unicité ``(gallery, position)`` n'est jamais violée pendant la boucle.
    """

    photos = list(
        Photo.objects.select_for_update()
        .filter(gallery=gallery)
        .order_by("position", "created_at")
    )
    for index, photo in enumerate(photos):
        if photo.position != index:
            photo.position = index
            photo.save(update_fields=["position", "updated_at"])


def delete_photo(photo: Photo) -> None:
    """Supprime une photo en base puis son fichier après commit.

    La suppression du fichier est différée après le commit de la transaction :
    un rollback ne doit jamais laisser une ligne sans fichier.
    """

    storage = photo.file.storage
    storage_name = photo.file.name
    gallery_id = photo.gallery_id

    with transaction.atomic():
        locked_gallery = Gallery.objects.select_for_update().get(pk=gallery_id)
        photo.delete()
        _compact_positions(locked_gallery)
        transaction.on_commit(
            lambda: _delete_storage_file(storage, storage_name)
        )


def reorder_photos(gallery: Gallery, photo_ids: Iterable[uuid.UUID]) -> list[Photo]:
    """Réordonne toutes les photos d'une galerie.

    La liste fournie doit contenir exactement une fois chaque photo de la
    galerie. Une liste partielle serait ambiguë et est refusée.
    """

    requested_ids = list(photo_ids)
    if len(requested_ids) != len(set(requested_ids)):
        raise PhotoValidationError(
            {
                "photo_ids": [
                    "La liste de réorganisation contient des doublons."
                ]
            }
        )

    with transaction.atomic():
        locked_gallery = Gallery.objects.select_for_update().get(pk=gallery.pk)
        photos = list(
            Photo.objects.select_for_update()
            .filter(gallery=locked_gallery)
            .order_by("position", "created_at")
        )
        current_ids = {photo.id for photo in photos}
        requested_set = set(requested_ids)

        if requested_set != current_ids or len(requested_ids) != len(current_ids):
            raise PhotoValidationError(
                {
                    "photo_ids": [
                        (
                            "La liste doit contenir exactement toutes les "
                            "photos de la galerie, sans doublon."
                        )
                    ]
                }
            )

        if not photos:
            return []

        # Décalage temporaire pour éviter toute collision avec la contrainte
        # d'unicité pendant l'attribution des nouvelles positions.
        current_max = max(photo.position for photo in photos)
        offset = current_max + len(photos) + 1
        Photo.objects.filter(gallery=locked_gallery).update(
            position=F("position") + offset
        )

        by_id = {photo.id: photo for photo in photos}
        for index, photo_id in enumerate(requested_ids):
            photo = by_id[photo_id]
            photo.position = index
            photo.save(update_fields=["position", "updated_at"])

        return list(
            Photo.objects.filter(gallery=locked_gallery).order_by(
                "position", "created_at"
            )
        )
