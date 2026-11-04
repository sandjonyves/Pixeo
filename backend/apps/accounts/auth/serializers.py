"""Serializers d'authentification Pixeo."""

from __future__ import annotations

from rest_framework import serializers

from apps.accounts.models import User
from apps.api.serializers import PixeoModelSerializer, PixeoSerializer


class LoginSerializer(PixeoSerializer):
    """Identifiants de connexion, sans jamais exposer le mot de passe en sortie."""

    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        max_length=128,
    )

    def validate_email(self, value: str) -> str:
        return value.strip().lower()


class UserProfileSerializer(PixeoModelSerializer):
    """Informations de compte non sensibles exposées par l'API."""

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "branding_username",
            "is_active",
            "is_suspended",
            "date_joined",
        )
        read_only_fields = fields


class LoginDataSerializer(PixeoSerializer):
    access_token = serializers.CharField()
    user = UserProfileSerializer()


class LoginResponseSerializer(PixeoSerializer):
    ok = serializers.BooleanField()
    data = LoginDataSerializer()


class RefreshDataSerializer(PixeoSerializer):
    access_token = serializers.CharField()


class RefreshResponseSerializer(PixeoSerializer):
    ok = serializers.BooleanField()
    data = RefreshDataSerializer()


class LogoutDataSerializer(PixeoSerializer):
    logged_out = serializers.BooleanField()


class LogoutResponseSerializer(PixeoSerializer):
    ok = serializers.BooleanField()
    data = LogoutDataSerializer()


class CSRFDataSerializer(PixeoSerializer):
    csrf_token = serializers.CharField()


class CSRFResponseSerializer(PixeoSerializer):
    ok = serializers.BooleanField()
    data = CSRFDataSerializer()


class MeResponseSerializer(PixeoSerializer):
    ok = serializers.BooleanField()
    data = UserProfileSerializer()
