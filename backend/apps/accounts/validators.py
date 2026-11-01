"""Validation du nom public de photographe (`branding_username`).

Le nom public sert de clé de tenant et de label de sous-domaine. Il doit donc
respecter les règles d'un label DNS tout en restant lisible et non réservé.
"""

from __future__ import annotations

import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

BRANDING_USERNAME_MAX_LENGTH = 63

# Label DNS : minuscules, chiffres et tirets, sans tiret en début ou fin.
BRANDING_USERNAME_REGEX = re.compile(
    r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$"
)

# Noms utilisés par la plateforme, les routes techniques ou les sous-domaines
# d'infrastructure. Ils ne peuvent pas devenir des noms de photographe.
RESERVED_BRANDING_USERNAMES = frozenset(
    {
        "account",
        "accounts",
        "admin",
        "api",
        "app",
        "assets",
        "auth",
        "billing",
        "blog",
        "cdn",
        "dashboard",
        "demo",
        "dev",
        "docs",
        "download",
        "downloads",
        "favicon",
        "files",
        "galleries",
        "gallery",
        "help",
        "images",
        "imap",
        "localhost",
        "login",
        "logout",
        "mail",
        "media",
        "ns1",
        "ns2",
        "p",
        "photos",
        "pixeo",
        "pop",
        "public",
        "register",
        "robots",
        "s",
        "settings",
        "signup",
        "sitemap",
        "smtp",
        "static",
        "status",
        "staging",
        "support",
        "test",
        "uploads",
        "well-known",
        "www",
        "www2",
    }
)


def normalize_branding_username(value: str) -> str:
    """Normalise un nom public avant validation et persistance."""
    return value.strip().lower()


def validate_branding_username(value: str) -> None:
    """Valide un `branding_username` déjà normalisé.

    La normalisation (minuscules, suppression des espaces de bord) est faite par
    le modèle avant l'appel aux validateurs. Un appel direct avec une valeur non
    normalisée est donc refusé.
    """
    if not isinstance(value, str) or not value:
        raise ValidationError(
            _("Le nom public est obligatoire."),
            code="invalid_branding_username",
        )

    if value != value.lower():
        raise ValidationError(
            _("Le nom public doit être en minuscules."),
            code="invalid_branding_username",
        )

    if len(value) > BRANDING_USERNAME_MAX_LENGTH:
        raise ValidationError(
            _(
                "Le nom public ne peut pas dépasser %(max)d caractères."
            ),
            code="invalid_branding_username",
            params={"max": BRANDING_USERNAME_MAX_LENGTH},
        )

    if not BRANDING_USERNAME_REGEX.fullmatch(value):
        raise ValidationError(
            _(
                "Le nom public ne peut contenir que des lettres minuscules, "
                "des chiffres et des tirets, sans tiret au début ni à la fin."
            ),
            code="invalid_branding_username",
        )

    if value in RESERVED_BRANDING_USERNAMES:
        raise ValidationError(
            _("Ce nom public est réservé par Pixeo."),
            code="reserved_branding_username",
        )
