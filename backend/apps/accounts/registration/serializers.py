"""Serializers d'inscription Pixeo.

L'inscription est publique, mais elle ne crée aucune session : elle ne retourne
ni access token ni cookie de refresh. Le rôle, les permissions et les statuts
d'administration sont toujours imposés par le service serveur et ne peuvent
jamais être fournis par le client.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from rest_framework import serializers

from apps.accounts.models import User
from apps.accounts.validators import (
    BRANDING_USERNAME_MAX_LENGTH,
    normalize_branding_username,
    validate_branding_username,
)
from apps.api.serializers import PixeoSerializer, snakeize_keys, to_camel_case


class RegisterSerializer(PixeoSerializer):
    """Données publiques de création d'un compte photographe."""

    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        max_length=128,
    )
    password_confirmation = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        max_length=128,
    )
    branding_username = serializers.CharField(
        max_length=BRANDING_USERNAME_MAX_LENGTH,
        trim_whitespace=True,
    )

    def to_internal_value(self, data: Any) -> Any:
        """Refuse explicitement tout champ non déclaré.

        DRF ignore par défaut les champs inconnus. Pour un endpoint public qui
        crée un compte, une clé comme ``role``, ``isStaff`` ou ``isSuperuser``
        doit être rejetée plutôt qu'ignorée silencieusement.
        """

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
        return super().to_internal_value(data)

    def validate_email(self, value: str) -> str:
        return value.strip().lower()

    def validate_branding_username(self, value: str) -> str:
        normalized = normalize_branding_username(value)
        try:
            validate_branding_username(normalized)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc
        return normalized

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        password = attrs.get("password")
        confirmation = attrs.get("password_confirmation")

        if password != confirmation:
            raise serializers.ValidationError(
                {
                    "password_confirmation": [
                        "Les deux mots de passe ne correspondent pas."
                    ]
                }
            )

        candidate = User(
            email=attrs.get("email", ""),
            branding_username=attrs.get("branding_username", ""),
        )
        try:
            validate_password(password, user=candidate)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                {"password": list(exc.messages)}
            ) from exc

        # Un conflit d'e-mail ou de nom public reste volontairement non-field
        # et générique. Une erreur sur ``email`` révélerait directement qu'une
        # adresse existe ; le même message pour les deux conflits évite aussi
        # de distinguer les deux causes dans la réponse.
        email = attrs.get("email", "")
        branding_username = attrs.get("branding_username", "")
        if User.objects.filter(
            Q(email=email) | Q(branding_username=branding_username)
        ).exists():
            raise serializers.ValidationError(
                "Un compte avec ces informations existe déjà."
            )

        return attrs


class RegisterRequestSchema(serializers.Serializer):
    """Schéma OpenAPI du corps d'inscription, en camelCase public."""

    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        max_length=128,
    )
    passwordConfirmation = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        max_length=128,
    )
    brandingUsername = serializers.CharField(max_length=63)


class RegisteredUserSchema(serializers.Serializer):
    """Schéma OpenAPI du profil public retourné après inscription."""

    id = serializers.UUIDField()
    email = serializers.EmailField()
    firstName = serializers.CharField(allow_blank=True)
    lastName = serializers.CharField(allow_blank=True)
    role = serializers.CharField()
    brandingUsername = serializers.CharField()
    isActive = serializers.BooleanField()
    isSuspended = serializers.BooleanField()
    dateJoined = serializers.DateTimeField()


class RegisterDataSchema(serializers.Serializer):
    user = RegisteredUserSchema()


class RegisterResponseSchema(serializers.Serializer):
    ok = serializers.BooleanField()
    data = RegisterDataSchema()
