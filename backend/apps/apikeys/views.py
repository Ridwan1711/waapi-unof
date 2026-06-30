from __future__ import annotations

from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.workspaces.selectors import get_active_workspace

from .models import ApiKey
from .serializers import ApiKeyCreateSerializer, ApiKeySerializer
from .services import generate_api_key

# API keys are managed from the dashboard only — a key cannot manage keys.
_DASHBOARD_AUTH = [JWTAuthentication, SessionAuthentication]


class ApiKeyListCreateView(APIView):
    authentication_classes = _DASHBOARD_AUTH
    permission_classes = [IsAuthenticated]

    def get(self, request):
        workspace = get_active_workspace(request)
        keys = ApiKey.objects.filter(workspace=workspace)
        return Response(ApiKeySerializer(keys, many=True).data)

    def post(self, request):
        workspace = get_active_workspace(request)
        serializer = ApiKeyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        api_key, raw_key = generate_api_key(
            workspace=workspace,
            created_by=request.user,
            **serializer.validated_data,
        )
        data = ApiKeySerializer(api_key).data
        data["key"] = raw_key  # shown exactly once
        return Response(data, status=status.HTTP_201_CREATED)


class ApiKeyRevokeView(APIView):
    authentication_classes = _DASHBOARD_AUTH
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        workspace = get_active_workspace(request)
        try:
            key = ApiKey.objects.get(pk=pk, workspace=workspace)
        except ApiKey.DoesNotExist:
            return Response(
                {"error": {"code": "not_found", "message": "API key not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        key.revoke()
        return Response(ApiKeySerializer(key).data)
