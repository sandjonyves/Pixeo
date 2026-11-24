"""Tests API des galeries Pixeo."""

from __future__ import annotations

from datetime import timedelta
from unittest import mock
from uuid import uuid4

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.accounts.models import User, UserRole
from apps.galleries.models import Gallery, GalleryStatus
from apps.galleries.views import _is_slug_unique_conflict

pytestmark = pytest.mark.django_db

LIST_URL = "/api/v1/galleries/"
CSRF_URL = "/api/v1/auth/csrf/"


def _detail_url(gallery_id) -> str:
    return f"/api/v1/galleries/{gallery_id}/"


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


def _payload(**overrides):
    data = {
        "title": "Mariage de Camille",
        "slug": "mariage-camille",
    }
    data.update(overrides)
    return data


def _gallery(photographer: User, **overrides) -> Gallery:
    values = {
        "title": "Mariage de Camille",
        "slug": "mariage-camille",
    }
    values.update(overrides)
    return Gallery.objects.create(photographer=photographer, **values)


@pytest.fixture
def photographer() -> User:
    return User.objects.create_user(
        email="photographer@example.com",
        password="StrongPassword123!",
        branding_username="photographer",
        first_name="Jean",
        last_name="Dupont",
    )


@pytest.fixture
def other_photographer() -> User:
    return User.objects.create_user(
        email="other@example.com",
        password="StrongPassword123!",
        branding_username="other-photographer",
        first_name="Alice",
        last_name="Martin",
    )


@pytest.fixture
def platform_admin() -> User:
    return User.objects.create_user(
        email="admin@example.com",
        password="StrongPassword123!",
        branding_username="pixeo-admin",
        role=UserRole.PLATFORM_ADMIN,
        is_staff=True,
    )


@pytest.fixture
def suspended_photographer(photographer: User) -> User:
    photographer.is_suspended = True
    photographer.save(update_fields=["is_suspended"])
    return photographer


@pytest.fixture
def inactive_photographer(photographer: User) -> User:
    photographer.is_active = False
    photographer.save(update_fields=["is_active"])
    return photographer


# ─── Authentification et autorisation ────────────────────────────────────────


def test_anonymous_cannot_list_galleries():
    response = APIClient().get(LIST_URL, HTTP_HOST="localhost")

    assert response.status_code == 401
    assert response.json()["code"] == "AUTHENTICATION_REQUIRED"


def test_photographer_can_list_galleries(photographer: User):
    response = _client_for(photographer).get(
        LIST_URL,
        HTTP_HOST="localhost",
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["data"]["items"] == []
    assert payload["data"]["total"] == 0


def test_platform_admin_cannot_access_galleries(platform_admin: User):
    response = _client_for(platform_admin).get(
        LIST_URL,
        HTTP_HOST="localhost",
    )

    assert response.status_code == 403
    assert response.json()["code"] == "PERMISSION_DENIED"


def test_platform_admin_cannot_create_gallery(platform_admin: User):
    response = _client_for(platform_admin).post(
        LIST_URL,
        _payload(),
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 403
    assert Gallery.objects.count() == 0


def test_suspended_photographer_cannot_access_galleries(
    suspended_photographer: User,
):
    response = _client_for(suspended_photographer).get(
        LIST_URL,
        HTTP_HOST="localhost",
    )

    assert response.status_code == 403
    assert response.json()["code"] == "ACCOUNT_SUSPENDED"


def test_inactive_photographer_cannot_access_galleries(
    inactive_photographer: User,
):
    response = _client_for(inactive_photographer).get(
        LIST_URL,
        HTTP_HOST="localhost",
    )

    assert response.status_code == 403
    assert response.json()["code"] == "ACCOUNT_DISABLED"


# ─── Création ────────────────────────────────────────────────────────────────


def test_create_gallery(photographer: User):
    response = _client_for(photographer).post(
        LIST_URL,
        {
            "title": "Mariage de Camille",
            "slug": "mariage-camille",
            "description": "Sélection des meilleurs moments.",
        },
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["ok"] is True
    data = payload["data"]
    assert set(data) == {
        "id",
        "title",
        "slug",
        "description",
        "status",
        "publishedAt",
        "createdAt",
        "updatedAt",
    }
    assert data["title"] == "Mariage de Camille"
    assert data["slug"] == "mariage-camille"
    assert data["description"] == "Sélection des meilleurs moments."
    assert data["status"] == GalleryStatus.DRAFT
    assert data["publishedAt"] is None
    assert data["createdAt"]
    assert data["updatedAt"]
    assert "photographer" not in data
    assert "password" not in data

    gallery = Gallery.objects.get(pk=data["id"])
    assert gallery.photographer == photographer
    assert gallery.title == data["title"]
    assert gallery.status == GalleryStatus.DRAFT
    assert gallery.published_at is None


@pytest.mark.parametrize("status_value", GalleryStatus.values)
def test_create_rejects_status(
    photographer: User,
    status_value: str,
):
    response = _client_for(photographer).post(
        LIST_URL,
        _payload(status=status_value),
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["code"] == "VALIDATION_ERROR"
    assert "status" in payload["details"]
    assert Gallery.objects.count() == 0


def test_create_rejects_published_at(photographer: User):
    response = _client_for(photographer).post(
        LIST_URL,
        _payload(publishedAt="2026-01-01T00:00:00Z"),
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["code"] == "VALIDATION_ERROR"
    assert "publishedAt" in payload["details"]
    assert Gallery.objects.count() == 0


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("id", str(uuid4())),
        ("createdAt", "2026-01-01T00:00:00Z"),
        ("updatedAt", "2026-01-01T00:00:00Z"),
    ],
)
def test_create_rejects_read_only_fields(
    photographer: User,
    field: str,
    value: str,
):
    response = _client_for(photographer).post(
        LIST_URL,
        _payload(**{field: value}),
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["code"] == "VALIDATION_ERROR"
    assert field in payload["details"]
    assert Gallery.objects.count() == 0


def test_create_assigns_owner_from_request_user(photographer: User):
    response = _client_for(photographer).post(
        LIST_URL,
        _payload(),
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 201
    gallery = Gallery.objects.get(pk=response.json()["data"]["id"])
    assert gallery.photographer == photographer


@pytest.mark.parametrize("field", ["photographer", "photographerId"])
def test_create_rejects_owner_injection(
    photographer: User,
    other_photographer: User,
    field: str,
):
    response = _client_for(photographer).post(
        LIST_URL,
        _payload(**{field: str(other_photographer.id)}),
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["code"] == "VALIDATION_ERROR"
    assert field in payload["details"]
    assert Gallery.objects.count() == 0


def test_create_requires_title(photographer: User):
    response = _client_for(photographer).post(
        LIST_URL,
        {"slug": "mariage-camille"},
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    assert "title" in response.json()["details"]


def test_create_requires_slug(photographer: User):
    response = _client_for(photographer).post(
        LIST_URL,
        {"title": "Mariage de Camille"},
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    assert "slug" in response.json()["details"]


def test_create_rejects_empty_title_and_slug(photographer: User):
    response = _client_for(photographer).post(
        LIST_URL,
        {"title": "", "slug": ""},
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    details = response.json()["details"]
    assert "title" in details
    assert "slug" in details


def test_create_rejects_duplicate_slug_for_same_photographer(
    photographer: User,
):
    _gallery(photographer, slug="mariage-camille")

    response = _client_for(photographer).post(
        LIST_URL,
        _payload(),
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    assert "slug" in response.json()["details"]
    assert Gallery.objects.filter(photographer=photographer).count() == 1


def test_same_slug_allowed_for_different_photographers(
    photographer: User,
    other_photographer: User,
):
    first = _client_for(photographer).post(
        LIST_URL,
        _payload(),
        format="json",
        HTTP_HOST="localhost",
    )
    second = _client_for(other_photographer).post(
        LIST_URL,
        _payload(),
        format="json",
        HTTP_HOST="localhost",
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert Gallery.objects.filter(slug="mariage-camille").count() == 2


def test_create_rejects_invalid_status(photographer: User):
    response = _client_for(photographer).post(
        LIST_URL,
        _payload(status="archived"),
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    assert "status" in response.json()["details"]


def test_create_defaults_to_draft(photographer: User):
    response = _client_for(photographer).post(
        LIST_URL,
        _payload(),
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 201
    assert response.json()["data"]["status"] == GalleryStatus.DRAFT
    gallery = Gallery.objects.get(pk=response.json()["data"]["id"])
    assert gallery.status == GalleryStatus.DRAFT


def test_create_optional_description_defaults_empty(photographer: User):
    response = _client_for(photographer).post(
        LIST_URL,
        _payload(),
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 201
    assert response.json()["data"]["description"] == ""


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("title", "x" * 151),
        ("slug", "a" * 101),
    ],
)
def test_create_enforces_max_lengths(
    photographer: User,
    field: str,
    value: str,
):
    response = _client_for(photographer).post(
        LIST_URL,
        _payload(**{field: value}),
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    assert field in response.json()["details"]


def test_create_handles_slug_integrity_error(photographer: User):
    with mock.patch(
        "apps.galleries.serializers.GallerySerializer.save",
        side_effect=IntegrityError(
            "duplicate key value violates unique constraint "
            '"unique_gallery_slug_per_photographer"'
        ),
    ):
        response = _client_for(photographer).post(
            LIST_URL,
            _payload(),
            format="json",
            HTTP_HOST="localhost",
        )

    assert response.status_code == 400
    payload = response.json()
    assert payload["code"] == "VALIDATION_ERROR"
    assert "nonFieldErrors" in payload["details"]
    assert Gallery.objects.count() == 0


def test_patch_handles_slug_integrity_error(photographer: User):
    gallery = _gallery(photographer)

    with mock.patch(
        "apps.galleries.serializers.GallerySerializer.save",
        side_effect=IntegrityError(
            "duplicate key value violates unique constraint "
            '"unique_gallery_slug_per_photographer"'
        ),
    ):
        response = _client_for(photographer).patch(
            _detail_url(gallery.id),
            {"title": "Titre modifié"},
            format="json",
            HTTP_HOST="localhost",
        )

    assert response.status_code == 400
    payload = response.json()
    assert payload["code"] == "VALIDATION_ERROR"
    assert "nonFieldErrors" in payload["details"]
    gallery.refresh_from_db()
    assert gallery.title == "Mariage de Camille"


def test_create_does_not_mask_unexpected_integrity_error(
    photographer: User,
    caplog,
):
    with mock.patch(
        "apps.galleries.serializers.GallerySerializer.save",
        side_effect=IntegrityError(
            "violates foreign key constraint on another table"
        ),
    ):
        response = _client_for(photographer).post(
            LIST_URL,
            _payload(),
            format="json",
            HTTP_HOST="localhost",
        )

    assert response.status_code == 500
    payload = response.json()
    assert payload["code"] == "INTERNAL_ERROR"
    assert "foreign key" not in response.content.decode().lower()
    assert "Unexpected gallery integrity error" in caplog.text
    assert Gallery.objects.count() == 0


def test_slug_unique_conflict_is_detected_from_database(photographer: User):
    _gallery(photographer, slug="duplicate-slug")

    with pytest.raises(IntegrityError) as exc_info:
        with transaction.atomic():
            Gallery.objects.bulk_create(
                [
                    Gallery(
                        photographer=photographer,
                        title="Doublon",
                        slug="duplicate-slug",
                    )
                ]
            )

    assert _is_slug_unique_conflict(exc_info.value)


# ─── Liste ───────────────────────────────────────────────────────────────────


def test_list_only_returns_own_galleries(
    photographer: User,
    other_photographer: User,
):
    own_first = _gallery(photographer, slug="own-first")
    own_second = _gallery(photographer, slug="own-second")
    _gallery(other_photographer, slug="other-gallery")

    response = _client_for(photographer).get(
        LIST_URL,
        HTTP_HOST="localhost",
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    data = payload["data"]
    assert data["total"] == 2
    assert data["page"] == 1
    assert data["pageSize"] == 20
    assert {item["id"] for item in data["items"]} == {
        str(own_first.id),
        str(own_second.id),
    }


def test_list_pagination(photographer: User):
    for index in range(21):
        _gallery(photographer, slug=f"gallery-{index}")

    response = _client_for(photographer).get(
        LIST_URL,
        {"page": 3, "page_size": 10},
        HTTP_HOST="localhost",
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] == 21
    assert data["page"] == 3
    assert data["pageSize"] == 10
    assert len(data["items"]) == 1


def test_list_filters_by_status(
    photographer: User,
    other_photographer: User,
):
    _gallery(
        photographer,
        slug="draft-gallery",
        status=GalleryStatus.DRAFT,
    )
    published = _gallery(
        photographer,
        slug="published-gallery",
        status=GalleryStatus.PUBLISHED,
        published_at=timezone.now(),
    )
    _gallery(
        other_photographer,
        slug="other-published",
        status=GalleryStatus.PUBLISHED,
        published_at=timezone.now(),
    )

    response = _client_for(photographer).get(
        LIST_URL,
        {"status": GalleryStatus.PUBLISHED},
        HTTP_HOST="localhost",
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] == 1
    assert data["items"][0]["id"] == str(published.id)


def test_list_uses_model_ordering(photographer: User):
    older = _gallery(photographer, slug="older-gallery")
    newer = _gallery(photographer, slug="newer-gallery")
    Gallery.objects.filter(pk=older.pk).update(
        created_at=timezone.now() - timedelta(days=1)
    )

    response = _client_for(photographer).get(
        LIST_URL,
        HTTP_HOST="localhost",
    )

    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert items[0]["id"] == str(newer.id)


# ─── Détail et isolation multi-tenant ────────────────────────────────────────


def test_retrieve_own_gallery(photographer: User):
    gallery = _gallery(photographer)

    response = _client_for(photographer).get(
        _detail_url(gallery.id),
        HTTP_HOST="localhost",
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["data"]["id"] == str(gallery.id)


def test_retrieve_other_photographer_gallery_returns_404(
    photographer: User,
    other_photographer: User,
):
    gallery = _gallery(other_photographer)

    response = _client_for(photographer).get(
        _detail_url(gallery.id),
        HTTP_HOST="localhost",
    )

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


def test_retrieve_invalid_uuid_returns_404(photographer: User):
    response = _client_for(photographer).get(
        "/api/v1/galleries/not-a-uuid/",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


def test_patch_own_gallery(photographer: User):
    gallery = _gallery(photographer)

    response = _client_for(photographer).patch(
        _detail_url(gallery.id),
        {
            "title": "Nouveau titre",
            "description": "Nouvelle description",
        },
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["data"]["title"] == "Nouveau titre"
    assert payload["data"]["description"] == "Nouvelle description"
    assert payload["data"]["status"] == GalleryStatus.DRAFT
    assert payload["data"]["publishedAt"] is None

    gallery.refresh_from_db()
    assert gallery.title == "Nouveau titre"
    assert gallery.description == "Nouvelle description"
    assert gallery.status == GalleryStatus.DRAFT
    assert gallery.published_at is None
    assert gallery.photographer == photographer


@pytest.mark.parametrize("status_value", GalleryStatus.values)
def test_patch_rejects_status(
    photographer: User,
    status_value: str,
):
    gallery = _gallery(photographer)

    response = _client_for(photographer).patch(
        _detail_url(gallery.id),
        {"status": status_value},
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["code"] == "VALIDATION_ERROR"
    assert "status" in payload["details"]
    gallery.refresh_from_db()
    assert gallery.status == GalleryStatus.DRAFT


def test_patch_rejects_hidden_to_published(photographer: User):
    gallery = _gallery(
        photographer,
        status=GalleryStatus.HIDDEN,
    )

    response = _client_for(photographer).patch(
        _detail_url(gallery.id),
        {"status": GalleryStatus.PUBLISHED},
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    assert "status" in response.json()["details"]
    gallery.refresh_from_db()
    assert gallery.status == GalleryStatus.HIDDEN


@pytest.mark.parametrize("target_status", GalleryStatus.values)
def test_patch_rejects_transition_from_published(
    photographer: User,
    target_status: str,
):
    published_at = timezone.now()
    gallery = _gallery(
        photographer,
        status=GalleryStatus.PUBLISHED,
        published_at=published_at,
    )

    response = _client_for(photographer).patch(
        _detail_url(gallery.id),
        {"status": target_status},
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    assert "status" in response.json()["details"]
    gallery.refresh_from_db()
    assert gallery.status == GalleryStatus.PUBLISHED
    assert gallery.published_at == published_at


def test_patch_metadata_preserves_publication_fields(photographer: User):
    published_at = timezone.now()
    gallery = _gallery(
        photographer,
        status=GalleryStatus.PUBLISHED,
        published_at=published_at,
    )

    response = _client_for(photographer).patch(
        _detail_url(gallery.id),
        {"title": "Titre modifié"},
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == GalleryStatus.PUBLISHED
    assert data["publishedAt"] is not None
    gallery.refresh_from_db()
    assert gallery.title == "Titre modifié"
    assert gallery.status == GalleryStatus.PUBLISHED
    assert gallery.published_at == published_at


def test_patch_rejects_published_at(photographer: User):
    gallery = _gallery(photographer)

    response = _client_for(photographer).patch(
        _detail_url(gallery.id),
        {"publishedAt": "2026-01-01T00:00:00Z"},
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["code"] == "VALIDATION_ERROR"
    assert "publishedAt" in payload["details"]
    gallery.refresh_from_db()
    assert gallery.published_at is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("id", str(uuid4())),
        ("createdAt", "2026-01-01T00:00:00Z"),
        ("updatedAt", "2026-01-01T00:00:00Z"),
    ],
)
def test_patch_rejects_read_only_fields(
    photographer: User,
    field: str,
    value: str,
):
    gallery = _gallery(photographer)
    original_id = gallery.id

    response = _client_for(photographer).patch(
        _detail_url(gallery.id),
        {field: value},
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["code"] == "VALIDATION_ERROR"
    assert field in payload["details"]
    gallery.refresh_from_db()
    assert gallery.id == original_id


def test_patch_other_photographer_gallery_returns_404(
    photographer: User,
    other_photographer: User,
):
    gallery = _gallery(other_photographer, title="Titre original")

    response = _client_for(photographer).patch(
        _detail_url(gallery.id),
        {"title": "Titre modifié"},
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 404
    gallery.refresh_from_db()
    assert gallery.title == "Titre original"


def test_patch_rejects_duplicate_slug(photographer: User):
    _gallery(photographer, slug="premier-slug")
    second = _gallery(photographer, slug="second-slug")

    response = _client_for(photographer).patch(
        _detail_url(second.id),
        {"slug": "premier-slug"},
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    assert "slug" in response.json()["details"]
    second.refresh_from_db()
    assert second.slug == "second-slug"


def test_patch_rejects_invalid_status(photographer: User):
    gallery = _gallery(photographer)

    response = _client_for(photographer).patch(
        _detail_url(gallery.id),
        {"status": "archived"},
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    assert "status" in response.json()["details"]


@pytest.mark.parametrize("field", ["photographer", "photographerId"])
def test_patch_rejects_owner_injection(
    photographer: User,
    other_photographer: User,
    field: str,
):
    gallery = _gallery(photographer)

    response = _client_for(photographer).patch(
        _detail_url(gallery.id),
        {field: str(other_photographer.id)},
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    assert field in response.json()["details"]
    gallery.refresh_from_db()
    assert gallery.photographer == photographer


def test_patch_description_is_optional(photographer: User):
    gallery = _gallery(photographer, description="Description initiale")

    response = _client_for(photographer).patch(
        _detail_url(gallery.id),
        {"description": ""},
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 200
    assert response.json()["data"]["description"] == ""
    gallery.refresh_from_db()
    assert gallery.description == ""


def test_delete_own_gallery(photographer: User):
    gallery = _gallery(photographer)

    response = _client_for(photographer).delete(
        _detail_url(gallery.id),
        HTTP_HOST="localhost",
    )

    assert response.status_code == 204
    assert response.content == b""
    assert not Gallery.objects.filter(pk=gallery.pk).exists()


def test_delete_other_photographer_gallery_returns_404(
    photographer: User,
    other_photographer: User,
):
    gallery = _gallery(other_photographer)

    response = _client_for(photographer).delete(
        _detail_url(gallery.id),
        HTTP_HOST="localhost",
    )

    assert response.status_code == 404
    assert Gallery.objects.filter(pk=gallery.pk).exists()


def test_put_is_not_allowed(photographer: User):
    gallery = _gallery(photographer)

    response = _client_for(photographer).put(
        _detail_url(gallery.id),
        _payload(title="Titre remplacé"),
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 405
    assert response.json()["code"] == "METHOD_NOT_ALLOWED"


def test_validation_error_uses_standard_envelope(photographer: User):
    response = _client_for(photographer).post(
        LIST_URL,
        {"slug": "mariage-camille"},
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["ok"] is False
    assert payload["code"] == "VALIDATION_ERROR"
    assert payload["error"]
    assert "title" in payload["details"]


# ─── CSRF et authentification par session ─────────────────────────────────────


def test_session_post_without_csrf_is_refused(photographer: User):
    client = _session_client(photographer)

    response = client.post(
        LIST_URL,
        _payload(),
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 403
    assert response.json()["code"] == "CSRF_FAILED"
    assert Gallery.objects.count() == 0


def test_session_patch_without_csrf_is_refused(photographer: User):
    gallery = _gallery(photographer)
    client = _session_client(photographer)

    response = client.patch(
        _detail_url(gallery.id),
        {"title": "Titre modifié"},
        format="json",
        HTTP_HOST="localhost",
    )

    assert response.status_code == 403
    assert response.json()["code"] == "CSRF_FAILED"
    gallery.refresh_from_db()
    assert gallery.title == "Mariage de Camille"


def test_session_delete_without_csrf_is_refused(photographer: User):
    gallery = _gallery(photographer)
    client = _session_client(photographer)

    response = client.delete(
        _detail_url(gallery.id),
        HTTP_HOST="localhost",
    )

    assert response.status_code == 403
    assert response.json()["code"] == "CSRF_FAILED"
    assert Gallery.objects.filter(pk=gallery.pk).exists()


def test_session_post_with_valid_csrf_succeeds(photographer: User):
    client = _session_client(photographer)
    csrf_token = _csrf_token(client)

    response = client.post(
        LIST_URL,
        _payload(),
        format="json",
        HTTP_HOST="localhost",
        HTTP_X_CSRFTOKEN=csrf_token,
    )

    assert response.status_code == 201
    assert response.json()["data"]["status"] == GalleryStatus.DRAFT


def test_session_patch_with_valid_csrf_succeeds(photographer: User):
    gallery = _gallery(photographer)
    client = _session_client(photographer)
    csrf_token = _csrf_token(client)

    response = client.patch(
        _detail_url(gallery.id),
        {"title": "Titre modifié"},
        format="json",
        HTTP_HOST="localhost",
        HTTP_X_CSRFTOKEN=csrf_token,
    )

    assert response.status_code == 200
    assert response.json()["data"]["title"] == "Titre modifié"


def test_session_delete_with_valid_csrf_succeeds(photographer: User):
    gallery = _gallery(photographer)
    client = _session_client(photographer)
    csrf_token = _csrf_token(client)

    response = client.delete(
        _detail_url(gallery.id),
        HTTP_HOST="localhost",
        HTTP_X_CSRFTOKEN=csrf_token,
    )

    assert response.status_code == 204
    assert not Gallery.objects.filter(pk=gallery.pk).exists()
