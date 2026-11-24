"""Tests du modèle de galerie Pixeo."""

from __future__ import annotations

import uuid

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.accounts.models import User, UserRole
from apps.galleries.models import Gallery, GalleryStatus

pytestmark = pytest.mark.django_db


@pytest.fixture
def photographer():
    return User.objects.create_user(
        email="gallery-owner@example.com",
        password="StrongPassword123!",
        branding_username="gallery-owner",
    )


@pytest.fixture
def other_photographer():
    return User.objects.create_user(
        email="other-gallery-owner@example.com",
        password="StrongPassword123!",
        branding_username="other-gallery-owner",
    )


@pytest.fixture
def platform_admin():
    return User.objects.create_user(
        email="platform-admin@example.com",
        password="StrongPassword123!",
        branding_username="platform-admin",
        role=UserRole.PLATFORM_ADMIN,
    )


@pytest.fixture
def gallery(photographer):
    return Gallery.objects.create(
        photographer=photographer,
        title="Mariage de Camille et Alex",
        slug="mariage-camille-alex",
    )


def test_gallery_creation(gallery, photographer):
    assert gallery.photographer == photographer
    assert gallery.title == "Mariage de Camille et Alex"
    assert gallery.slug == "mariage-camille-alex"
    assert gallery.description == ""
    assert gallery.status == GalleryStatus.DRAFT
    assert gallery.published_at is None


def test_gallery_id_is_uuid(gallery):
    assert isinstance(gallery.id, uuid.UUID)
    gallery.refresh_from_db()
    assert isinstance(gallery.id, uuid.UUID)


def test_gallery_default_status_is_draft(photographer):
    gallery = Gallery.objects.create(
        photographer=photographer,
        title="Galerie brouillon",
        slug="galerie-brouillon",
    )

    assert gallery.status == GalleryStatus.DRAFT


def test_gallery_requires_photographer():
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Gallery.objects.create(
                photographer=None,
                title="Sans photographe",
                slug="sans-photographe",
            )


def test_gallery_slug_is_unique_for_a_photographer(photographer):
    Gallery.objects.create(
        photographer=photographer,
        title="Première galerie",
        slug="mariage",
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Gallery.objects.create(
                photographer=photographer,
                title="Deuxième galerie",
                slug="mariage",
            )


def test_two_photographers_can_use_the_same_slug(
    photographer, other_photographer
):
    first = Gallery.objects.create(
        photographer=photographer,
        title="Mariage du photographe A",
        slug="mariage",
    )
    second = Gallery.objects.create(
        photographer=other_photographer,
        title="Mariage du photographe B",
        slug="mariage",
    )

    assert first.slug == second.slug == "mariage"
    assert first.photographer != second.photographer


def test_gallery_rejects_invalid_status(photographer):
    gallery = Gallery(
        photographer=photographer,
        title="Statut invalide",
        slug="statut-invalide",
        status="archived",
    )

    with pytest.raises(ValidationError) as exc_info:
        gallery.full_clean()

    assert "status" in exc_info.value.message_dict


def test_gallery_rejects_blank_title_and_slug(photographer):
    gallery = Gallery(photographer=photographer, title="", slug="")

    with pytest.raises(ValidationError) as exc_info:
        gallery.full_clean()

    assert "title" in exc_info.value.message_dict
    assert "slug" in exc_info.value.message_dict


def test_gallery_save_rejects_empty_title(gallery):
    gallery.title = ""

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            gallery.save()


def test_gallery_save_rejects_empty_slug(gallery):
    gallery.slug = ""

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            gallery.save()


def test_gallery_objects_create_rejects_empty_title(photographer):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Gallery.objects.create(
                photographer=photographer,
                title="",
                slug="titre-vide",
            )


def test_gallery_objects_create_rejects_empty_slug(photographer):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Gallery.objects.create(
                photographer=photographer,
                title="Slug vide",
                slug="",
            )


def test_gallery_save_rejects_invalid_status(gallery):
    gallery.status = "archived"

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            gallery.save()


def test_gallery_objects_create_rejects_invalid_status(photographer):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Gallery.objects.create(
                photographer=photographer,
                title="Statut invalide",
                slug="statut-invalide",
                status="archived",
            )


def test_gallery_bulk_create_rejects_empty_title(photographer):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Gallery.objects.bulk_create(
                [
                    Gallery(
                        photographer=photographer,
                        title="",
                        slug="bulk-titre-vide",
                    )
                ]
            )


def test_gallery_bulk_create_rejects_empty_slug(photographer):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Gallery.objects.bulk_create(
                [
                    Gallery(
                        photographer=photographer,
                        title="Bulk slug vide",
                        slug="",
                    )
                ]
            )


def test_gallery_bulk_create_rejects_invalid_status(photographer):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Gallery.objects.bulk_create(
                [
                    Gallery(
                        photographer=photographer,
                        title="Bulk statut invalide",
                        slug="bulk-statut-invalide",
                        status="archived",
                    )
                ]
            )


def test_gallery_full_clean_rejects_platform_admin(platform_admin):
    gallery = Gallery(
        photographer=platform_admin,
        title="Galerie administrateur",
        slug="galerie-administrateur",
    )

    with pytest.raises(ValidationError) as exc_info:
        gallery.full_clean()

    assert "photographer" in exc_info.value.message_dict


def test_gallery_save_rejects_platform_admin(platform_admin):
    gallery = Gallery(
        photographer=platform_admin,
        title="Galerie administrateur",
        slug="galerie-administrateur",
    )

    with pytest.raises(ValidationError) as exc_info:
        gallery.save()

    assert "photographer" in exc_info.value.message_dict


def test_gallery_objects_create_rejects_platform_admin(platform_admin):
    with pytest.raises(ValidationError) as exc_info:
        Gallery.objects.create(
            photographer=platform_admin,
            title="Galerie administrateur",
            slug="galerie-administrateur",
        )

    assert "photographer" in exc_info.value.message_dict


def test_gallery_is_deleted_with_its_photographer(gallery):
    gallery_id = gallery.pk

    gallery.photographer.delete()

    assert Gallery.objects.filter(pk=gallery_id).exists() is False


def test_gallery_date_fields(gallery):
    assert gallery.created_at is not None
    assert gallery.updated_at is not None
    assert gallery.published_at is None

    previous_updated_at = gallery.updated_at
    gallery.published_at = timezone.now()
    gallery.save()
    gallery.refresh_from_db()

    assert gallery.created_at is not None
    assert gallery.published_at is not None
    assert gallery.updated_at >= previous_updated_at


def test_gallery_rejects_published_without_published_at(photographer):
    gallery = Gallery(
        photographer=photographer,
        title="Galerie publiée",
        slug="galerie-publiee",
        status=GalleryStatus.PUBLISHED,
    )

    with pytest.raises(ValidationError) as exc_info:
        gallery.full_clean()

    assert "published_at" in exc_info.value.message_dict


def test_gallery_save_rejects_published_without_published_at(photographer):
    gallery = Gallery(
        photographer=photographer,
        title="Galerie publiée",
        slug="galerie-publiee",
        status=GalleryStatus.PUBLISHED,
    )

    with pytest.raises(ValidationError) as exc_info:
        gallery.save()

    assert "published_at" in exc_info.value.message_dict


def test_gallery_objects_create_rejects_published_without_published_at(
    photographer,
):
    with pytest.raises(ValidationError) as exc_info:
        Gallery.objects.create(
            photographer=photographer,
            title="Galerie publiée",
            slug="galerie-publiee",
            status=GalleryStatus.PUBLISHED,
        )

    assert "published_at" in exc_info.value.message_dict


def test_gallery_bulk_create_rejects_published_without_published_at(
    photographer,
):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Gallery.objects.bulk_create(
                [
                    Gallery(
                        photographer=photographer,
                        title="Galerie publiée",
                        slug="galerie-publiee",
                        status=GalleryStatus.PUBLISHED,
                    )
                ]
            )


def test_gallery_published_with_published_at_is_allowed(photographer):
    published_at = timezone.now()
    gallery = Gallery.objects.create(
        photographer=photographer,
        title="Galerie publiée",
        slug="galerie-publiee",
        status=GalleryStatus.PUBLISHED,
        published_at=published_at,
    )

    assert gallery.status == GalleryStatus.PUBLISHED
    assert gallery.published_at == published_at


@pytest.mark.parametrize(
    "gallery_status",
    [
        GalleryStatus.DRAFT,
        GalleryStatus.HIDDEN,
        GalleryStatus.PRE_RELEASE,
    ],
)
def test_non_published_gallery_can_keep_published_at(
    photographer,
    gallery_status,
):
    published_at = timezone.now()
    gallery = Gallery.objects.create(
        photographer=photographer,
        title="Galerie déjà publiée",
        slug=f"galerie-{gallery_status}",
        status=gallery_status,
        published_at=published_at,
    )

    assert gallery.status == gallery_status
    assert gallery.published_at == published_at


def test_gallery_has_publication_consistency_constraint():
    names = {constraint.name for constraint in Gallery._meta.constraints}

    assert "gallery_published_requires_published_at" in names


def test_gallery_field_lengths_and_status_choices():
    assert Gallery._meta.get_field("title").max_length == 150
    assert Gallery._meta.get_field("slug").max_length == 100
    assert GalleryStatus.values == [
        "draft",
        "published",
        "hidden",
        "pre_release",
    ]
