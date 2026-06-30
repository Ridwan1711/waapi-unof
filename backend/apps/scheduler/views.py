from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.devices.models import Device
from apps.workspaces.selectors import get_active_workspace

from .models import ScheduledMessage
from .serializers import ScheduledMessageCreateSerializer, ScheduledMessageSerializer
from .services import cancel_scheduled_message, create_scheduled_message


class ScheduledMessageListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        workspace = get_active_workspace(request)
        scheduled = ScheduledMessage.objects.filter(workspace=workspace)
        return Response(ScheduledMessageSerializer(scheduled, many=True).data)

    def post(self, request):
        workspace = get_active_workspace(request)
        serializer = ScheduledMessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        device = Device.objects.filter(id=data["device"], workspace=workspace).first()
        if device is None:
            return Response(
                {"error": {"code": "not_found", "message": "Device not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        payload = {
            "to": data["to"],
            "type": data["type"],
            "text": data.get("text", ""),
            "media": data.get("media"),
        }
        scheduled = create_scheduled_message(
            workspace=workspace, device=device, run_at=data["run_at"], payload=payload
        )
        return Response(ScheduledMessageSerializer(scheduled).data, status=status.HTTP_201_CREATED)


class ScheduledMessageDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        workspace = get_active_workspace(request)
        scheduled = ScheduledMessage.objects.filter(pk=pk, workspace=workspace).first()
        if scheduled is None:
            return _not_found()
        return Response(ScheduledMessageSerializer(scheduled).data)


class ScheduledMessageCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        workspace = get_active_workspace(request)
        scheduled = ScheduledMessage.objects.filter(pk=pk, workspace=workspace).first()
        if scheduled is None:
            return _not_found()
        cancel_scheduled_message(scheduled)
        return Response(ScheduledMessageSerializer(scheduled).data)


def _not_found() -> Response:
    return Response(
        {"error": {"code": "not_found", "message": "Scheduled message not found."}},
        status=status.HTTP_404_NOT_FOUND,
    )
