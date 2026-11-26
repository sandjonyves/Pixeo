"""Tests API de gestion des photos d'une galerie Pixeo."""

from __future__ import annotations

import hashlib
from io import BytesIO
from pathlib import Path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import override_settings
from PIL import Image
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.accounts.models import User, UserRole
from apps.galleries.models import Gallery, Photo
from apps.galleries.services import delete_photo

pytestmark = pytest.mark.django_db

CSRF_URL = "/api/v1/auth/csrf/"


def _photos_url(gallery_id) -> str:
    return f"/api/v1/galleries/{gallery_id}/photos/"


def _photo_url(gallery_id, photo_id) -> str:
    return f"/api/v1/galleries/{gallery_id}/photos/{photo_id}/"


def _order_url(gallery_id) -> str:
    return f"/api/v1/galleries/{gallery_id}/photos/order/"


def _client_for(user: User) -> APIClient:
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(user)}")
    return client


def _session_client(user: User) -> APIClient:
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(user)
    return client


def _csrf_token(client: APIClient) -> str:
    response = client.get(CSRF_URL, HTTP_HOST="localhost")
    assert response.status_code == 200
    return response.json()["data"]["csrfToken"]


def _image_bytes(
    image_format: str = "JPEG",
    size: tuple[int, int] = (20, 10),
) -> bytes:
    buffer = BytesIO()
    Image.new("RGB", size, (200, 30, 30)).save(buffer, format=image_format)
    return buffer.getvalue()


def _mime_type(image_format: str) -> str:
    return {
        "JPEG": "image/jpeg",
        "PNG": "image/png",
        "WEBP": "image/webp",
        "GIF": "image/gif",
    }[image_format]


def _extension(image_format: str) -> str:
    return {
        "JPEG": ".jpg",
        "PNG": ".png",
        "WEBP": ".webp",
    }[image_format]


def _upload(
    name: str = "photo.jpg",
    image_format: str = "JPEG",
    size: tuple[int, int] = (20, 10),
) -> SimpleUploadedFile:
    return SimpleUploadedFile(
        name,
        _image_bytes(image_format, size),
        content_type=_mime_type(image_format),
    )


def _create_photo(
    gallery: Gallery,
    position: int = 0,
    image_format: str = "JPEG",
    width: int = 20,
    height: int = 10,
) -> Photo:
    data = _image_bytes(image_format, (width, height))
    filename = f"photo-{position}{_extension(image_format)}"
    uploaded = SimpleUploadedFile(
        filename,
        data,
        content_type=_mime_type(image_format),
    )
    return Photo.objects.create(
        gallery=gallery,
        file=uploaded,
        original_filename=filename,
        format=image_format,
        mime_type=_mime_type(image_format),
        size_bytes=len(data),
        width=width,
        height=height,
        checksum_sha256=hashlib.sha256(data).hexdigest(),
        position=position,
    )


def _stored_files(media_root: Path) -> list[Path]:
    if not media_root.exists():
        return []
    return [path for path in media_root.rglob("*") if path.is_file()]


@pytest.fixture(autouse=True)
def photo_media(tmp_path):
    media_root = tmp_path / "media"
    with override_settings(
        MEDIA_ROOT=str(media_root),
        MEDIA_URL="/media/",
        PIXEO_PHOTO_MAX_UPLOAD_SIZE=20 * 1024 * 1024,
        PIXEO_PHOTO_MAX_BATCH_SIZE=20,
        PIXEO_PHOTO_MAX_PIXELS=50_000_000,
    ):
        yield media_root


@pytest.fixture
def photographer() -> User:
    return User.objects.create_user(
        email="photo-photographer@example.com",
        password="StrongPassword123!",
        branding_username="photo-photographer",
    )


@pytest.fixture
def other_photographer() -> User:
    return User.objects.create_user(
        email="photo-other@example.com",
        password="StrongPassword123!",
        branding_username="photo-other",
    )


@pytest.fixture
def platform_admin() -> User:
    return User.objects.create_user(
        email="photo-admin@example.com",
        password="StrongPassword123!",
        branding_username="photo-admin",
        role=UserRole.PLATFORM_ADMIN,
        is_staff=True,
    )


@pytest.fixture
def gallery(photographer: User) -> Gallery:
    return Gallery.objects.create(
        photographer=photographer,
        title="Mariage photo",
        slug="mariage-photo",
    )


@pytest.fixture
def other_gallery(other_photographer: User) -> Gallery:
    return Gallery.objects.create(
        photographer=other_photographer,
        title="Autre mariage",
        slug="autre-mariage",
    )


# ─── Authentification et isolation ──────────────────────────────────────────


def test_anonymous_cannot_list_photos(gallery: Gallery):
    response = APIClient().get(_photos_url(gallery.id), HTTP_HOST="localhost")

    assert response.status_code == 401
    assert response.json()["code"] == "AUTHENTICATION_REQUIRED"


def test_platform_admin_cannot_access_photos(
    platform_admin: User,
    gallery: Gallery,
):
    response = _client_for(platform_admin).get(
        _photos_url(gallery.id),
        HTTP_HOST="localhost",
    )

    assert response.status_code == 403
    assert response.json()["code"] == "PERMISSION_DENIED"


def test_photographer_can_list_only_own_gallery_photos(
    photographer: User,
    gallery: Gallery,
    other_gallery: Gallery,
):
    first = _create_photo(gallery, position=0)
    second = _create_photo(gallery, position=1)
    _create_photo(other_gallery, position=0)

    response = _client_for(photographer).get(
        _photos_url(gallery.id),
        HTTP_HOST="localhost",
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    data = payload["data"]
    assert data["total"] == 2
    assert [item["id"] for item in data["items"]] == [
        str(first.id),
        str(second.id),
    ]


def test_list_other_photographer_gallery_returns_404(
    photographer: User,
    other_gallery: Gallery,
):
    response = _client_for(photographer).get(
        _photos_url(other_gallery.id),
        HTTP_HOST="localhost",
    )

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


def test_photo_list_is_paginated(photographer: User, gallery: Gallery):
    for position in range(3):
        _create_photo(gallery, position=position)

    response = _client_for(photographer).get(
        _photos_url(gallery.id),
        {"page": 2, "page_size": 2},
        HTTP_HOST="localhost",
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] == 3
    assert data["page"] == 2
    assert data["pageSize"] == 2
    assert len(data["items"]) == 1


# ─── Import ─────────────────────────────────────────────────────────────────


def test_import_single_photo(
    photographer: User,
    gallery: Gallery,
    photo_media: Path,
):
    uploaded = _upload("mariage.jpg")
    original_bytes = uploaded.read()
    uploaded.seek(0)

    response = _client_for(photographer).post(
        _photos_url(gallery.id),
        {"file": uploaded},
        format="multipart",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["ok"] is True
    assert payload["data"]["total"] == 1
    item = payload["data"]["items"][0]
    assert set(item) == {
        "id",
        "galleryId",
        "originalFilename",
        "format",
        "mimeType",
        "sizeBytes",
        "width",
        "height",
        "position",
        "url",
        "createdAt",
        "updatedAt",
    }
    assert item["galleryId"] == str(gallery.id)
    assert item["originalFilename"] == "mariage.jpg"
    assert item["format"] == "JPEG"
    assert item["mimeType"] == "image/jpeg"
    assert item["sizeBytes"] == len(original_bytes)
    assert item["width"] == 20
    assert item["height"] == 10
    assert item["position"] == 0
    assert item["url"].startswith("http://localhost/media/")

    photo = Photo.objects.get(pk=item["id"])
    assert photo.gallery == gallery
    assert photo.original_filename == "mariage.jpg"
    assert photo.checksum_sha256 == hashlib.sha256(original_bytes).hexdigest()
    assert photo.file.name.startswith(f"galleries/{gallery.id}/photos/")
    assert photo.file.storage.exists(photo.file.name)
    assert _stored_files(photo_media)


def test_import_multiple_photos_assigns_positions(
    photographer: User,
    gallery: Gallery,
):
    response = _client_for(photographer).post(
        _photos_url(gallery.id),
        {
            "files": [
                _upload("premier.jpg"),
                _upload("second.png", image_format="PNG"),
                _upload("troisieme.webp", image_format="WEBP"),
            ]
        },
        format="multipart",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 201
    items = response.json()["data"]["items"]
    assert [item["position"] for item in items] == [0, 1, 2]
    assert [item["format"] for item in items] == ["JPEG", "PNG", "WEBP"]
    assert Photo.objects.filter(gallery=gallery).count() == 3


def test_import_requires_at_least_one_file(
    photographer: User,
    gallery: Gallery,
):
    response = _client_for(photographer).post(
        _photos_url(gallery.id),
        {},
        format="multipart",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert Photo.objects.count() == 0


def test_import_rejects_invalid_image(
    photographer: User,
    gallery: Gallery,
    photo_media: Path,
):
    uploaded = SimpleUploadedFile(
        "faux.jpg",
        b"ceci n'est pas une image",
        content_type="image/jpeg",
    )

    response = _client_for(photographer).post(
        _photos_url(gallery.id),
        {"files": [uploaded]},
        format="multipart",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["code"] == "VALIDATION_ERROR"
    assert "files" in payload["details"]
    assert Photo.objects.count() == 0
    assert _stored_files(photo_media) == []


def test_import_rejects_unsupported_format(
    photographer: User,
    gallery: Gallery,
):
    uploaded = _upload("animation.gif", image_format="GIF")

    response = _client_for(photographer).post(
        _photos_url(gallery.id),
        {"files": [uploaded]},
        format="multipart",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert Photo.objects.count() == 0


def test_import_rejects_empty_file(
    photographer: User,
    gallery: Gallery,
):
    uploaded = SimpleUploadedFile(
        "vide.jpg",
        b"",
        content_type="image/jpeg",
    )

    response = _client_for(photographer).post(
        _photos_url(gallery.id),
        {"files": [uploaded]},
        format="multipart",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert Photo.objects.count() == 0


def test_import_rejects_oversized_file(
    photographer: User,
    gallery: Gallery,
):
    with override_settings(PIXEO_PHOTO_MAX_UPLOAD_SIZE=10):
        response = _client_for(photographer).post(
            _photos_url(gallery.id),
            {"files": [_upload()]},
            format="multipart",
            HTTP_HOST="localhost",
        )

    assert response.status_code == 400
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert Photo.objects.count() == 0


def test_import_rejects_too_many_pixels(
    photographer: User,
    gallery: Gallery,
):
    with override_settings(PIXEO_PHOTO_MAX_PIXELS=100):
        response = _client_for(photographer).post(
            _photos_url(gallery.id),
            {"files": [_upload()]},
            format="multipart",
            HTTP_HOST="localhost",
        )

    assert response.status_code == 400
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert Photo.objects.count() == 0


def test_import_rejects_too_many_files(
    photographer: User,
    gallery: Gallery,
):
    with override_settings(PIXEO_PHOTO_MAX_BATCH_SIZE=1):
        response = _client_for(photographer).post(
            _photos_url(gallery.id),
            {"files": [_upload("a.jpg"), _upload("b.jpg")]},
            format="multipart",
            HTTP_HOST="localhost",
        )

    assert response.status_code == 400
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert Photo.objects.count() == 0


def test_import_batch_is_atomic(
    photographer: User,
    gallery: Gallery,
    photo_media: Path,
):
    valid = _upload("valide.jpg")
    invalid = SimpleUploadedFile(
        "invalide.jpg",
        b"broken",
        content_type="image/jpeg",
    )

    response = _client_for(photographer).post(
        _photos_url(gallery.id),
        {"files": [valid, invalid]},
        format="multipart",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    assert Photo.objects.count() == 0
    assert _stored_files(photo_media) == []


@pytest.mark.parametrize(
    "field",
    ["galleryId", "photographerId", "owner", "position"],
)
def test_import_rejects_unknown_or_owner_fields(
    photographer: User,
    gallery: Gallery,
    field: str,
):
    response = _client_for(photographer).post(
        _photos_url(gallery.id),
        {
            "files": [_upload()],
            field: str(gallery.id),
        },
        format="multipart",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["code"] == "VALIDATION_ERROR"
    assert field in payload["details"]
    assert Photo.objects.count() == 0


def test_import_cleans_stored_files_when_database_write_fails(
    photographer: User,
    gallery: Gallery,
    photo_media: Path,
    monkeypatch,
):
    def fail_save(self, *args, **kwargs):
        raise IntegrityError("simulated photo insert failure")

    monkeypatch.setattr(Photo, "save", fail_save)

    response = _client_for(photographer).post(
        _photos_url(gallery.id),
        {"files": [_upload()]},
        format="multipart",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 500
    assert response.json()["code"] == "INTERNAL_ERROR"
    assert Photo.objects.count() == 0
    assert _stored_files(photo_media) == []


# ─── Détail ─────────────────────────────────────────────────────────────────


def test_retrieve_own_photo(photographer: User, gallery: Gallery):
    photo = _create_photo(gallery)

    response = _client_for(photographer).get(
        _photo_url(gallery.id, photo.id),
        HTTP_HOST="localhost",
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["data"]["id"] == str(photo.id)
    assert payload["data"]["galleryId"] == str(gallery.id)


def test_retrieve_photo_from_other_photographer_returns_404(
    photographer: User,
    other_gallery: Gallery,
):
    photo = _create_photo(other_gallery)

    response = _client_for(photographer).get(
        _photo_url(other_gallery.id, photo.id),
        HTTP_HOST="localhost",
    )

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


def test_retrieve_photo_from_another_own_gallery_returns_404(
    photographer: User,
    gallery: Gallery,
):
    second_gallery = Gallery.objects.create(
        photographer=photographer,
        title="Deuxième galerie",
        slug="deuxieme-galerie",
    )
    photo = _create_photo(second_gallery)

    response = _client_for(photographer).get(
        _photo_url(gallery.id, photo.id),
        HTTP_HOST="localhost",
    )

    assert response.status_code == 404


# ─── Suppression ────────────────────────────────────────────────────────────


def test_delete_photo_removes_file_and_compacts_positions(
    photographer: User,
    gallery: Gallery,
    django_capture_on_commit_callbacks,
):
    first = _create_photo(gallery, position=0)
    middle = _create_photo(gallery, position=1)
    last = _create_photo(gallery, position=2)
    middle_storage = middle.file.storage
    middle_name = middle.file.name

    with django_capture_on_commit_callbacks(execute=True):
        response = _client_for(photographer).delete(
            _photo_url(gallery.id, middle.id),
            HTTP_HOST="localhost",
        )

    assert response.status_code == 204
    assert response.content == b""
    assert not Photo.objects.filter(pk=middle.pk).exists()
    assert not middle_storage.exists(middle_name)

    first.refresh_from_db()
    last.refresh_from_db()
    assert first.position == 0
    assert last.position == 1


def test_delete_other_photographer_photo_returns_404(
    photographer: User,
    other_gallery: Gallery,
):
    photo = _create_photo(other_gallery)
    storage = photo.file.storage
    name = photo.file.name

    response = _client_for(photographer).delete(
        _photo_url(other_gallery.id, photo.id),
        HTTP_HOST="localhost",
    )

    assert response.status_code == 404
    assert Photo.objects.filter(pk=photo.pk).exists()
    assert storage.exists(name)


def test_delete_rollback_keeps_database_row_and_file(
    photographer: User,
    gallery: Gallery,
    monkeypatch,
):
    photo = _create_photo(gallery)
    photo_pk = photo.pk
    storage = photo.file.storage
    name = photo.file.name

    def fail_compaction(gallery):
        raise RuntimeError("simulated compaction failure")

    monkeypatch.setattr(
        "apps.galleries.services._compact_positions",
        fail_compaction,
    )

    with pytest.raises(RuntimeError):
        delete_photo(photo)

    # ``Model.delete()`` remet ``pk`` à None en mémoire même si la transaction
    # est annulée : on vérifie la ligne avec l'identifiant capturé avant.
    assert Photo.objects.filter(pk=photo_pk).exists()
    assert storage.exists(name)


# ─── Réorganisation ─────────────────────────────────────────────────────────


def test_reorder_photos(photographer: User, gallery: Gallery):
    first = _create_photo(gallery, position=0)
    second = _create_photo(gallery, position=1)
    third = _create_photo(gallery, position=2)

    response = _client_for(photographer).patch(
        _order_url(gallery.id),
        {
            "photoIds": [
                str(third.id),
                str(first.id),
                str(second.id),
            ]
        },
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 200
    payload = response.json()
    assert [item["id"] for item in payload["data"]["items"]] == [
        str(third.id),
        str(first.id),
        str(second.id),
    ]
    assert [item["position"] for item in payload["data"]["items"]] == [0, 1, 2]

    first.refresh_from_db()
    second.refresh_from_db()
    third.refresh_from_db()
    assert (first.position, second.position, third.position) == (1, 2, 0)


def test_reorder_empty_gallery(photographer: User, gallery: Gallery):
    response = _client_for(photographer).patch(
        _order_url(gallery.id),
        {"photoIds": []},
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 200
    assert response.json()["data"] == {"items": [], "total": 0}


def test_reorder_rejects_missing_photo(
    photographer: User,
    gallery: Gallery,
):
    first = _create_photo(gallery, position=0)
    _create_photo(gallery, position=1)

    response = _client_for(photographer).patch(
        _order_url(gallery.id),
        {"photoIds": [str(first.id)]},
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    assert "photoIds" in response.json()["details"]


def test_reorder_rejects_duplicate_photo(
    photographer: User,
    gallery: Gallery,
):
    first = _create_photo(gallery, position=0)
    second = _create_photo(gallery, position=1)

    response = _client_for(photographer).patch(
        _order_url(gallery.id),
        {"photoIds": [str(first.id), str(first.id)]},
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    assert "photoIds" in response.json()["details"]
    assert Photo.objects.get(pk=second.pk).position == 1


def test_reorder_rejects_foreign_photo(
    photographer: User,
    gallery: Gallery,
    other_gallery: Gallery,
):
    first = _create_photo(gallery, position=0)
    foreign = _create_photo(other_gallery, position=0)

    response = _client_for(photographer).patch(
        _order_url(gallery.id),
        {"photoIds": [str(first.id), str(foreign.id)]},
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    assert "photoIds" in response.json()["details"]
    assert Photo.objects.get(pk=foreign.pk).position == 0


def test_reorder_other_photographer_gallery_returns_404(
    photographer: User,
    other_gallery: Gallery,
):
    response = _client_for(photographer).patch(
        _order_url(other_gallery.id),
        {"photoIds": []},
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 404


def test_reorder_rejects_unknown_fields(
    photographer: User,
    gallery: Gallery,
):
    response = _client_for(photographer).patch(
        _order_url(gallery.id),
        {"photoIds": [], "galleryId": str(gallery.id)},
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    assert "galleryId" in response.json()["details"]


# ─── Méthodes et CSRF ───────────────────────────────────────────────────────


def test_put_is_not_allowed_on_photo(
    photographer: User,
    gallery: Gallery,
):
    photo = _create_photo(gallery)

    response = _client_for(photographer).put(
        _photo_url(gallery.id, photo.id),
        {},
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 405
    assert response.json()["code"] == "METHOD_NOT_ALLOWED"


def test_session_import_without_csrf_is_refused(
    photographer: User,
    gallery: Gallery,
):
    client = _session_client(photographer)

    response = client.post(
        _photos_url(gallery.id),
        {"files": [_upload()]},
        format="multipart",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 403
    assert response.json()["code"] == "CSRF_FAILED"
    assert Photo.objects.count() == 0


def test_session_import_with_valid_csrf_succeeds(
    photographer: User,
    gallery: Gallery,
):
    client = _session_client(photographer)
    token = _csrf_token(client)

    response = client.post(
        _photos_url(gallery.id),
        {"files": [_upload()]},
        format="multipart",
        HTTP_HOST="localhost",
        HTTP_X_CSRFTOKEN=token,
    )

    assert response.status_code == 201
    assert Photo.objects.filter(gallery=gallery).count() == 1


def test_session_delete_without_csrf_is_refused(
    photographer: User,
    gallery: Gallery,
):
    photo = _create_photo(gallery)
    client = _session_client(photographer)

    response = client.delete(
        _photo_url(gallery.id, photo.id),
        HTTP_HOST="localhost",
    )

    assert response.status_code == 403
    assert response.json()["code"] == "CSRF_FAILED"
    assert Photo.objects.filter(pk=photo.pk).exists()


def test_session_delete_with_valid_csrf_succeeds(
    photographer: User,
    gallery: Gallery,
    django_capture_on_commit_callbacks,
):
    photo = _create_photo(gallery)
    client = _session_client(photographer)
    token = _csrf_token(client)

    with django_capture_on_commit_callbacks(execute=True):
        response = client.delete(
            _photo_url(gallery.id, photo.id),
            HTTP_HOST="localhost",
            HTTP_X_CSRFTOKEN=token,
        )

    assert response.status_code == 204
    assert not Photo.objects.filter(pk=photo.pk).exists()


def test_session_reorder_without_csrf_is_refused(
    photographer: User,
    gallery: Gallery,
):
    first = _create_photo(gallery, position=0)
    second = _create_photo(gallery, position=1)
    client = _session_client(photographer)

    response = client.patch(
        _order_url(gallery.id),
        {"photoIds": [str(second.id), str(first.id)]},
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 403
    assert response.json()["code"] == "CSRF_FAILED"
    assert Photo.objects.get(pk=first.pk).position == 0


def test_session_reorder_with_valid_csrf_succeeds(
    photographer: User,
    gallery: Gallery,
):
    first = _create_photo(gallery, position=0)
    second = _create_photo(gallery, position=1)
    client = _session_client(photographer)
    token = _csrf_token(client)

    response = client.patch(
        _order_url(gallery.id),
        {"photoIds": [str(second.id), str(first.id)]},
        format="json",
        HTTP_HOST="localhost",
        HTTP_X_CSRFTOKEN=token,
    )

    assert response.status_code == 200
    assert [item["id"] for item in response.json()["data"]["items"]] == [
        str(second.id),
        str(first.id),
    ]
