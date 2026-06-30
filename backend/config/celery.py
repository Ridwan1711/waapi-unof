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


@app.task(bind=True, ignore_result=True)
def debug_task(self) -> None:
    """Trivial task useful for verifying the worker is processing jobs."""
    print(f"Request: {self.request!r}")
