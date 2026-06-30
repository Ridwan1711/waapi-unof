from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.apikeys.throttling import ApiKeyRateThrottle
from apps.core.pagination import DefaultPagination
from apps.devices.models import Device
from apps.workspaces.selectors import get_active_workspace

from .models import Message
from .serializers import MessageSerializer, SendMessageSerializer
from .services import send_message


class MessageListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ApiKeyRateThrottle]

    def get(self, request):
        workspace = get_active_workspace(request)
        queryset = Message.objects.filter(workspace=workspace)
        device = request.query_params.get("device")
        direction = request.query_params.get("direction")
        status_param = request.query_params.get("status")
        if device:
            queryset = queryset.filter(device_id=device)
        if direction:
            queryset = queryset.filter(direction=direction)
        if status_param:
            queryset = queryset.filter(status=status_param)

        paginator = DefaultPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        return paginator.get_paginated_response(MessageSerializer(page, many=True).data)

    def post(self, request):
        workspace = get_active_workspace(request)
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        device = Device.objects.filter(id=data["device"], workspace=workspace).first()
        if device is None:
            return Response(
                {"error": {"code": "not_found", "message": "Device not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        message = send_message(
            device=device,
            to=data["to"],
            message_type=data["type"],
            text=data.get("text", ""),
            media=data.get("media"),
            idempotency_key=data.get("idempotency_key", ""),
        )
        return Response(MessageSerializer(message).data, status=status.HTTP_202_ACCEPTED)


class MessageDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        workspace = get_active_workspace(request)
        message = Message.objects.filter(pk=pk, workspace=workspace).first()
        if message is None:
            return Response(
                {"error": {"code": "not_found", "message": "Message not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(MessageSerializer(message).data)
