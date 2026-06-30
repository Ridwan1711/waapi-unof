from __future__ import annotations

from django.http import HttpRequest, HttpResponse, StreamingHttpResponse
from django.views import View
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

from apps.accounts.models import User
from apps.workspaces.selectors import get_active_workspace

from .models import Device
from .serializers import DeviceCreateSerializer, DeviceSerializer
from .services import connect_device, create_device, delete_device, logout_device
from .sse import iter_device_events


class DeviceListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        workspace = get_active_workspace(request)
        devices = Device.objects.filter(workspace=workspace)
        return Response(DeviceSerializer(devices, many=True).data)

    def post(self, request):
        workspace = get_active_workspace(request)
        serializer = DeviceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        device = create_device(workspace=workspace, **serializer.validated_data)
        return Response(DeviceSerializer(device).data, status=status.HTTP_201_CREATED)


class DeviceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_device(self, request, pk) -> Device | None:
        return Device.objects.filter(pk=pk, workspace=get_active_workspace(request)).first()

    def get(self, request, pk):
        device = self._get_device(request, pk)
        if device is None:
            return _not_found()
        return Response(DeviceSerializer(device).data)

    def delete(self, request, pk):
        device = self._get_device(request, pk)
        if device is None:
            return _not_found()
        delete_device(device)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DeviceConnectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        device = Device.objects.filter(pk=pk, workspace=get_active_workspace(request)).first()
        if device is None:
            return _not_found()
        connect_device(device)
        return Response(DeviceSerializer(device).data)


class DeviceLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        device = Device.objects.filter(pk=pk, workspace=get_active_workspace(request)).first()
        if device is None:
            return _not_found()
        logout_device(device)
        return Response(DeviceSerializer(device).data)


def _not_found() -> Response:
    return Response(
        {"error": {"code": "not_found", "message": "Device not found."}},
        status=status.HTTP_404_NOT_FOUND,
    )


def _user_from_token(token: str | None) -> User | None:
    if not token:
        return None
    try:
        access = AccessToken(token)
    except TokenError:
        return None
    return User.objects.filter(id=access.get("user_id")).first()


class DeviceEventsView(View):
    """SSE stream of QR + status for a device.

    EventSource cannot send an Authorization header, so the access token is
    passed as a `token` query parameter and validated here.
    """

    def get(self, request: HttpRequest, pk) -> HttpResponse:
        user = _user_from_token(request.GET.get("token"))
        if user is None:
            return HttpResponse(status=401)

        device = Device.objects.filter(pk=pk, workspace__memberships__user=user).first()
        if device is None:
            return HttpResponse(status=404)

        response = StreamingHttpResponse(
            iter_device_events(device), content_type="text/event-stream"
        )
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response
