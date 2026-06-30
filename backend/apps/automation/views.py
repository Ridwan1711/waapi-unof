from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.workspaces.selectors import get_active_workspace

from .models import AutoReplyRule
from .serializers import AutoReplyRuleSerializer


def _validate_device_scope(device, workspace) -> bool:
    return device is None or device.workspace_id == workspace.id


class AutoReplyRuleListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        workspace = get_active_workspace(request)
        rules = AutoReplyRule.objects.filter(workspace=workspace)
        return Response(AutoReplyRuleSerializer(rules, many=True).data)

    def post(self, request):
        workspace = get_active_workspace(request)
        serializer = AutoReplyRuleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not _validate_device_scope(serializer.validated_data.get("device"), workspace):
            return Response(
                {"error": {"code": "invalid", "message": "Device not in this workspace."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save(workspace=workspace)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AutoReplyRuleDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get(self, request, pk) -> AutoReplyRule | None:
        return AutoReplyRule.objects.filter(pk=pk, workspace=get_active_workspace(request)).first()

    def get(self, request, pk):
        rule = self._get(request, pk)
        if rule is None:
            return _not_found()
        return Response(AutoReplyRuleSerializer(rule).data)

    def patch(self, request, pk):
        rule = self._get(request, pk)
        if rule is None:
            return _not_found()
        serializer = AutoReplyRuleSerializer(rule, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        rule = self._get(request, pk)
        if rule is None:
            return _not_found()
        rule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def _not_found() -> Response:
    return Response(
        {"error": {"code": "not_found", "message": "Rule not found."}},
        status=status.HTTP_404_NOT_FOUND,
    )
