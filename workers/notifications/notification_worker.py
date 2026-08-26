"""Celery task placeholder for notification delivery."""

from workers.celery_app import celery_app


@celery_app.task(name="workers.notifications.send_notification")
def send_notification(*args, **kwargs):
    raise NotImplementedError("Notification delivery belongs to the routing contributor")
