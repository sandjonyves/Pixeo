"""Endpoints d'authentification et de session Pixeo."""

from __future__ import annotations

from django.conf import settings
from django.middleware.csrf import get_token
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .cookies import clear_refresh_cookie, set_refresh_cookie
from .csrf import enforce_csrf
from .exceptions import TokenInvalid
from .serializers import (
    CSRFResponseSerializer,
    LoginResponseSerializer,
    LoginSerializer,
    LogoutResponseSerializer,
    MeResponseSerializer,
    RefreshResponseSerializer,
    UserProfileSerializer,
)
from .services import (
    authenticate_credentials,
    issue_refresh_token,
    revoke_refresh_token,
    rotate_session,
)
from .throttles import AuthLoginThrottle, AuthRefreshThrottle

CSRF_HEADER = OpenApiParameter(
    name="X-CSRFToken",
    type=str,
    location=OpenApiParameter.HEADER,
    required=True,
    description="Jeton CSRF obtenu via GET /api/v1/auth/csrf/.",
)


def _success(data, status_code: int = 200) -> Response:
    return Response({"ok": True, "data": data}, status=status_code)


class LoginView(APIView):
    """Connexion par e-mail et mot de passe."""

    authentication_classes = []
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]
    throttle_classes = [AuthLoginThrottle]

    @extend_schema(
        tags=["Authentification"],
        request=LoginSerializer,
        parameters=[CSRF_HEADER],
        responses={200: LoginResponseSerializer},
        description=(
            "Vérifie les identifiants, retourne un access token et place le "
            "refresh token dans un cookie HttpOnly. Le login exige un jeton "
            "CSRF et accepte uniquement du JSON. Le refresh token n'est jamais "
            "présent dans le corps JSON."
        ),
    )
    def post(self, request, *args, **kwargs):
        # Le login crée un état d'authentification : il est donc protégé contre
        # le Login CSRF, même s'il ne consomme pas encore le cookie de refresh.
        enforce_csrf(request)

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate_credentials(
            serializer.validated_data["email"],
            serializer.validated_data["password"],
        )
        refresh = issue_refresh_token(user)
        response = _success(
            {
                "accessToken": str(refresh.access_token),
                "user": UserProfileSerializer(user).data,
            }
        )
        return set_refresh_cookie(response, str(refresh))


class RefreshView(APIView):
    """Rotation du refresh token contenu dans le cookie HttpOnly."""

    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [AuthRefreshThrottle]

    @extend_schema(
        tags=["Authentification"],
        request=None,
        parameters=[CSRF_HEADER],
        responses={200: RefreshResponseSerializer},
        description=(
            "Lit le refresh token dans le cookie, vérifie le compte, "
            "blackliste l'ancien jeton, effectue la rotation et retourne "
            "uniquement le nouvel access token."
        ),
    )
    def post(self, request, *args, **kwargs):
        # Le cookie est sensible : la vérification CSRF est obligatoire.
        enforce_csrf(request)

        raw_token = request.COOKIES.get(settings.AUTH_REFRESH_COOKIE_NAME)
        try:
            if not raw_token:
                raise TokenInvalid()
            _user, refresh = rotate_session(raw_token)
        except Exception as exc:  # noqa: BLE001 - le handler central décide
            response = self.handle_exception(exc)
            return clear_refresh_cookie(response)

        response = _success({"accessToken": str(refresh.access_token)})
        return set_refresh_cookie(response, str(refresh))


class LogoutView(APIView):
    """Révocation de la session courante."""

    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Authentification"],
        request=None,
        parameters=[CSRF_HEADER],
        responses={200: LogoutResponseSerializer},
        description=(
            "Blackliste le refresh token s'il est encore valide, puis "
            "supprime le cookie. L'access token déjà émis reste valide "
            "jusqu'à son expiration."
        ),
    )
    def post(self, request, *args, **kwargs):
        enforce_csrf(request)

        raw_token = request.COOKIES.get(settings.AUTH_REFRESH_COOKIE_NAME)
        revoke_refresh_token(raw_token)
        response = _success({"loggedOut": True})
        return clear_refresh_cookie(response)


class MeView(APIView):
    """Profil non sensible du compte authentifié."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Authentification"],
        responses={200: MeResponseSerializer},
        description="Retourne le profil courant sans mot de passe ni jeton.",
    )
    def get(self, request, *args, **kwargs):
        return _success(UserProfileSerializer(request.user).data)


class CSRFView(APIView):
    """Fournit un jeton CSRF au frontend."""

    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Authentification"],
        responses={200: CSRFResponseSerializer},
        description=(
            "Génère un jeton CSRF, pose le cookie CSRF et retourne le jeton "
            "à envoyer dans l'en-tête X-CSRFToken. Aucun refresh token "
            "n'est exposé."
        ),
    )
    def get(self, request, *args, **kwargs):
        # get_token() marque le cookie pour le middleware CSRF en réponse.
        token = get_token(request._request)
        return _success({"csrfToken": token})
