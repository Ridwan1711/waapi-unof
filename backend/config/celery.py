"""Celery application factory.

Tasks live in each app's ``tasks.py`` and are auto-discovered. Configuration is
read from Django settings using the ``CELERY_`` namespace.
"""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("waapi")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Periodic safety net: re-dispatch webhook deliveries that are due for retry
# (covers worker restarts that drop in-flight countdown tasks).
app.conf.beat_schedule = {
    "retry-pending-webhooks": {
        "task": "apps.webhooks.tasks.retry_pending_webhook_deliveries",
        "schedule": 60.0,
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self) -> None:
    """Trivial task useful for verifying the worker is processing jobs."""
    print(f"Request: {self.request!r}")
