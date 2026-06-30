from __future__ import annotations

from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.apikeys.models import ApiKey
from apps.apikeys.throttling import ApiKeyRateThrottle
from apps.workspaces.selectors import get_active_workspace, get_user_workspaces
from apps.workspaces.serializers import WorkspaceSerializer

from .serializers import RegisterSerializer, UserSerializer
from .services import register_user


class RegisterView(APIView):
    authentication_classes: list = []
    permission_classes = [AllowAny]
    throttle_scope = "auth"

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = register_user(**serializer.validated_data)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    """JWT obtain (email + password). Throttled to slow credential stuffing."""

    throttle_scope = "auth"


class MeView(APIView):
    # Dashboard endpoint: JWT/session only.
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "user": UserSerializer(request.user).data,
                "workspaces": WorkspaceSerializer(
                    get_user_workspaces(request.user), many=True
                ).data,
            }
        )


class WhoAmIView(APIView):
    """Works with either JWT or an API key; reports the active workspace."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [ApiKeyRateThrottle]

    def get(self, request):
        workspace = get_active_workspace(request)
        return Response(
            {
                "auth_method": "api_key" if isinstance(request.auth, ApiKey) else "jwt",
                "workspace": WorkspaceSerializer(workspace).data if workspace else None,
            }
        )
