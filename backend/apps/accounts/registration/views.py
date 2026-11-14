"""Endpoint public d'inscription Pixeo."""

from __future__ import annotations

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.auth.serializers import UserProfileSerializer
from apps.accounts.auth.throttles import AuthRegisterThrottle

from .serializers import (
    RegisterRequestSchema,
    RegisterResponseSchema,
    RegisterSerializer,
)
from .services import register_photographer


class RegisterView(APIView):
    """Crée un compte photographe et initialise son espace Pixeo.

    L'endpoint est public, sans session et sans cookie. Il n'applique donc pas
    la vérification CSRF des endpoints à cookie ; la protection repose sur le
    parser JSON strict, CORS et le throttling. Aucun login automatique n'est
    effectué : le client utilise ensuite ``POST /api/v1/auth/login/``.
    """

    authentication_classes = []
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]
    throttle_classes = [AuthRegisterThrottle]

    @extend_schema(
        tags=["Authentification"],
        request=RegisterRequestSchema,
        responses={201: RegisterResponseSchema},
        description=(
            "Crée un compte photographe, son abonnement Free, ses paramètres "
            "de branding et sa homepage. L'opération est transactionnelle. "
            "Le rôle est toujours `photographer` ; aucun token ni cookie de "
            "session n'est créé. Le client se connecte ensuite via "
            "`/api/v1/auth/login/`."
        ),
        examples=[
            OpenApiExample(
                "Inscription photographe",
                value={
                    "email": "photographe@example.com",
                    "password": "MotDePasseSolide123!",
                    "passwordConfirmation": "MotDePasseSolide123!",
                    "brandingUsername": "studio-photo",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Compte créé",
                value={
                    "ok": True,
                    "data": {
                        "user": {
                            "id": "00000000-0000-0000-0000-000000000000",
                            "email": "photographe@example.com",
                            "firstName": "",
                            "lastName": "",
                            "role": "photographer",
                            "brandingUsername": "studio-photo",
                            "isActive": True,
                            "isSuspended": False,
                            "dateJoined": "2026-11-04T00:00:00Z",
                        }
                    },
                },
                response_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = register_photographer(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            branding_username=serializer.validated_data["branding_username"],
        )

        return Response(
            {
                "ok": True,
                "data": {"user": UserProfileSerializer(user).data},
            },
            status=status.HTTP_201_CREATED,
        )
