"""Services d'authentification et de session Pixeo.

Les vues restent minces : la vérification des identifiants, le contrôle du
statut du compte, la rotation et la révocation des refresh tokens sont
centralisés ici. Aucun mot de passe ni jeton n'est journalisé.
"""

from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import update_last_login
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import ExpiredTokenError, TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from .exceptions import (
    AccountDisabled,
    AccountSuspended,
    InvalidCredentials,
    TokenExpired,
    TokenInvalid,
    TokenRevoked,
)

User = get_user_model()

# Ce hash factice permet de conserver un coût de vérification comparable quand
# l'adresse e-mail n'existe pas. Il ne protège aucun compte réel.
_DUMMY_PASSWORD_HASH = make_password("pixeo-dummy-password-not-a-secret")


def ensure_account_allowed(user: Any) -> Any:
    """Refuse un compte désactivé ou suspendu.

    Le contrôle est effectué à chaque authentification de requête, à la
    connexion et au renouvellement de session.
    """

    if getattr(user, "is_suspended", False):
        raise AccountSuspended()
    if not getattr(user, "is_active", False):
        raise AccountDisabled()
    return user


def authenticate_credentials(email: str, password: str) -> Any:
    """Vérifie les identifiants et retourne l'utilisateur autorisé.

    L'e-mail est normalisé avant la recherche. Le message d'erreur reste
    identique pour un compte inexistant et un mot de passe incorrect.
    """

    normalized_email = (email or "").strip().lower()

    try:
        user = User.objects.get_by_natural_key(normalized_email)
    except User.DoesNotExist:
        # Coût de vérification comparable à celui d'un compte existant.
        check_password(password, _DUMMY_PASSWORD_HASH)
        raise InvalidCredentials() from None

    if not user.check_password(password):
        raise InvalidCredentials()

    ensure_account_allowed(user)
    update_last_login(None, user)
    return user


def issue_refresh_token(user: Any) -> RefreshToken:
    """Crée un refresh token pour un compte autorisé."""

    ensure_account_allowed(user)
    return RefreshToken.for_user(user)


def parse_refresh_token(raw_token: str) -> RefreshToken:
    """Décode un refresh token en distinguant expiration, révocation et invalidité."""

    try:
        return RefreshToken(raw_token)
    except ExpiredTokenError as exc:
        raise TokenExpired() from exc
    except TokenError as exc:
        if "blacklist" in str(exc).lower():
            raise TokenRevoked() from exc
        raise TokenInvalid() from exc


def user_from_refresh_token(refresh: RefreshToken) -> Any:
    """Retourne le compte associé au refresh token s'il est toujours autorisé."""

    user_id = refresh.payload.get(api_settings.USER_ID_CLAIM)
    if not user_id:
        raise TokenInvalid()

    try:
        user = User.objects.get(**{api_settings.USER_ID_FIELD: user_id})
    except (User.DoesNotExist, ValidationError, ValueError, TypeError):
        raise TokenInvalid() from None

    return ensure_account_allowed(user)


def rotate_refresh_token(refresh: RefreshToken) -> RefreshToken:
    """Blackliste l'ancien refresh token et prépare le nouveau.

    La séquence reprend celle de SimpleJWT : l'ancien jeton est blacklisté avant
    de changer son JTI, puis le nouveau jeton est inscrit dans les jetons
    émis. L'ancien refresh token devient donc inutilisable.
    """

    refresh.blacklist()
    refresh.set_jti()
    refresh.set_exp()
    refresh.set_iat()
    refresh.outstand()
    return refresh


def rotate_session(raw_token: str) -> tuple[Any, RefreshToken]:
    """Valide une session puis effectue la rotation du refresh token."""

    refresh = parse_refresh_token(raw_token)
    user = user_from_refresh_token(refresh)
    rotate_refresh_token(refresh)
    return user, refresh


def revoke_refresh_token(raw_token: str | None) -> None:
    """Blackliste un refresh token lors de la déconnexion.

    Une valeur absente, expirée, invalide ou déjà révoquée est ignorée : la
    déconnexion reste idempotente et ne divulgue rien sur le jeton.
    """

    if not raw_token:
        return

    try:
        refresh = RefreshToken(raw_token)
    except TokenError:
        return

    try:
        refresh.blacklist()
    except TokenError:
        # Le jeton peut avoir été blacklisté entre-temps.
        return
