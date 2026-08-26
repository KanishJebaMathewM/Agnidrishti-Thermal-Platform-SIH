"""Celery task placeholder for event processing."""

from workers.celery_app import celery_app


@celery_app.task(name="workers.events.process_event")
def process_event(*args, **kwargs):
    raise NotImplementedError("Event processing belongs to the data pipeline contributor")
