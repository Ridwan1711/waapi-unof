from __future__ import annotations

from celery import shared_task
from django.utils import timezone

from .models import WebhookDelivery
from .services import attempt_delivery


@shared_task(bind=True, ignore_result=True)
def dispatch_webhook_delivery(self, delivery_id: str) -> None:
    delivery = WebhookDelivery.objects.filter(id=delivery_id).first()
    if delivery is None:
        return
    should_retry = attempt_delivery(delivery)
    if should_retry and delivery.next_retry_at:
        countdown = max(1, int((delivery.next_retry_at - timezone.now()).total_seconds()))
        dispatch_webhook_delivery.apply_async((str(delivery.id),), countdown=countdown)


@shared_task(ignore_result=True)
def retry_pending_webhook_deliveries() -> None:
    """Beat safety net: re-dispatch deliveries whose retry time has passed."""
    due = WebhookDelivery.objects.filter(
        status=WebhookDelivery.Status.RETRYING,
        next_retry_at__lte=timezone.now(),
    ).values_list("id", flat=True)
    for delivery_id in due:
        dispatch_webhook_delivery.delay(str(delivery_id))
