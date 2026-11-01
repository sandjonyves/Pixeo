"""Formulaires Django Admin du modèle utilisateur Pixeo.

Le champ `branding_username` est déclaré explicitement sans les validateurs du
modèle : la normalisation (minuscules, espaces de bord) doit être appliquée par
`User.clean_fields()` avant la validation. Le mot de passe reste géré par les
formulaires Django natifs et n'est jamais exposé en clair.
"""

from __future__ import annotations

from django import forms
from django.contrib.auth.forms import BaseUserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _

from .models import User
from .validators import BRANDING_USERNAME_MAX_LENGTH

BRANDING_USERNAME_HELP_TEXT = _(
    "Nom public unique utilisé comme sous-domaine Pixeo. "
    "Lettres minuscules, chiffres et tirets uniquement."
)


class PixeoUserCreationForm(BaseUserCreationForm):
    """Création d'un utilisateur depuis Django Admin, avec mot de passe hashé."""

    branding_username = forms.CharField(
        label=_("branding username"),
        max_length=BRANDING_USERNAME_MAX_LENGTH,
        help_text=BRANDING_USERNAME_HELP_TEXT,
    )

    class Meta(BaseUserCreationForm.Meta):
        model = User
        fields = (
            "email",
            "branding_username",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "is_suspended",
        )


class PixeoUserChangeForm(UserChangeForm):
    """Modification d'un utilisateur sans rendre le hash du mot de passe éditable."""

    branding_username = forms.CharField(
        label=_("branding username"),
        max_length=BRANDING_USERNAME_MAX_LENGTH,
        help_text=BRANDING_USERNAME_HELP_TEXT,
    )

    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"
