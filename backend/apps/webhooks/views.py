from __future__ import annotations

import secrets

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.pagination import DefaultPagination
from apps.workspaces.selectors import get_active_workspace

from .models import Webhook, WebhookDelivery
from .serializers import WebhookDeliverySerializer, WebhookSerializer


class WebhookListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        workspace = get_active_workspace(request)
        webhooks = Webhook.objects.filter(workspace=workspace)
        return Response(WebhookSerializer(webhooks, many=True).data)

    def post(self, request):
        workspace = get_active_workspace(request)
        serializer = WebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(workspace=workspace, secret=secrets.token_hex(24))
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WebhookDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get(self, request, pk) -> Webhook | None:
        return Webhook.objects.filter(pk=pk, workspace=get_active_workspace(request)).first()

    def get(self, request, pk):
        webhook = self._get(request, pk)
        if webhook is None:
            return _not_found()
        return Response(WebhookSerializer(webhook).data)

    def patch(self, request, pk):
        webhook = self._get(request, pk)
        if webhook is None:
            return _not_found()
        serializer = WebhookSerializer(webhook, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        webhook = self._get(request, pk)
        if webhook is None:
            return _not_found()
        webhook.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WebhookDeliveryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        workspace = get_active_workspace(request)
        webhook = Webhook.objects.filter(pk=pk, workspace=workspace).first()
        if webhook is None:
            return _not_found()
        deliveries = WebhookDelivery.objects.filter(webhook=webhook)
        paginator = DefaultPagination()
        page = paginator.paginate_queryset(deliveries, request, view=self)
        return paginator.get_paginated_response(WebhookDeliverySerializer(page, many=True).data)


def _not_found() -> Response:
    return Response(
        {"error": {"code": "not_found", "message": "Webhook not found."}},
        status=status.HTTP_404_NOT_FOUND,
    )
