"""Classes d'authentification DRF de Pixeo.

Le JWT reste le mécanisme principal de l'API. La session Django est conservée
pour l'administration et les interfaces qui en dépendent. Les deux classes
rechargent le compte depuis la base à chaque requête afin qu'une suspension ou
une désactivation prenne effet immédiatement, sans attendre l'expiration du
token.
"""

from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import (
    AuthenticationFailed as SimpleJWTAuthenticationFailed,
)
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.settings import api_settings

from apps.accounts.models import User

from .auth.exceptions import (
    AccountDisabled,
    AccountSuspended,
    TokenExpired,
    TokenInvalid,
    TokenRevoked,
)
from .auth.services import ensure_account_allowed


def _translate_invalid_token(exc: InvalidToken) -> Exception:
    """Transforme une erreur SimpleJWT en code Pixeo stable."""

    messages: list[Any] = []
    if isinstance(exc.detail, dict):
        raw_messages = exc.detail.get("messages", [])
        if isinstance(raw_messages, list):
            messages = raw_messages

    text = " ".join(
        str(message.get("message", ""))
        for message in messages
        if isinstance(message, dict)
    ).lower()

    if "blacklist" in text:
        return TokenRevoked()
    if "expired" in text:
        return TokenExpired()
    return TokenInvalid()


class PixeoJWTAuthentication(JWTAuthentication):
    """JWT avec vérification du statut courant du compte."""

    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except (TokenExpired, TokenInvalid, TokenRevoked, AccountDisabled, AccountSuspended):
            raise
        except InvalidToken as exc:
            raise _translate_invalid_token(exc) from exc
        except SimpleJWTAuthenticationFailed as exc:
            raise TokenInvalid() from exc

    def get_validated_token(self, raw_token):
        try:
            return super().get_validated_token(raw_token)
        except InvalidToken as exc:
            raise _translate_invalid_token(exc) from exc

    def get_user(self, validated_token):
        user_id = validated_token.get(api_settings.USER_ID_CLAIM)
        if not user_id:
            raise TokenInvalid()

        try:
            user = User.objects.get(**{api_settings.USER_ID_FIELD: user_id})
        except (User.DoesNotExist, ValidationError, ValueError, TypeError):
            raise TokenInvalid() from None

        return ensure_account_allowed(user)


class PixeoSessionAuthentication(SessionAuthentication):
    """Session Django avec vérification du statut courant du compte."""

    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None

        user, _auth = result
        ensure_account_allowed(user)
        return result
