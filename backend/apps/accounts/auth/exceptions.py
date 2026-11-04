"""Exceptions d'authentification de l'API Pixeo.

Chaque exception porte un attribut ``pixeo_code``. Le gestionnaire central de
``apps.api.exceptions`` s'appuie sur ce code pour produire une enveloppe stable
sans exposer le détail interne de l'exception.
"""

from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import APIException, PermissionDenied


class PixeoAuthException(APIException):
    """Base des erreurs d'authentification au format Pixeo."""

    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Authentification requise."
    default_code = "authentication_failed"
    pixeo_code = "authentication_failed"
    auth_header = 'Bearer realm="api"'


class InvalidCredentials(PixeoAuthException):
    """Identifiants absents, inconnus ou incorrects."""

    default_detail = "Adresse e-mail ou mot de passe incorrect."
    default_code = "invalid_credentials"
    pixeo_code = "invalid_credentials"


class TokenExpired(PixeoAuthException):
    """Jeton JWT expiré."""

    default_detail = "La session a expiré."
    default_code = "token_expired"
    pixeo_code = "token_expired"


class TokenInvalid(PixeoAuthException):
    """Jeton JWT absent, mal formé ou inutilisable."""

    default_detail = "Le jeton est invalide."
    default_code = "token_invalid"
    pixeo_code = "token_invalid"


class TokenRevoked(PixeoAuthException):
    """Refresh token déjà blacklisté ou révoqué."""

    default_detail = "La session a été révoquée."
    default_code = "token_revoked"
    pixeo_code = "token_revoked"


class AccountDisabled(APIException):
    """Compte désactivé côté Django."""

    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Ce compte est désactivé."
    default_code = "account_disabled"
    pixeo_code = "account_disabled"


class AccountSuspended(APIException):
    """Compte suspendu côté métier Pixeo."""

    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Ce compte est suspendu."
    default_code = "account_suspended"
    pixeo_code = "account_suspended"


class CSRFCheckFailed(PermissionDenied):
    """Échec de la vérification CSRF sur une opération à cookie."""

    default_detail = "La vérification CSRF a échoué."
    default_code = "csrf_failed"
    pixeo_code = "csrf_failed"
