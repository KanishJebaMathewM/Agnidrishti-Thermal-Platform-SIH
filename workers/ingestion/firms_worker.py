"""Celery task placeholder for NASA FIRMS snapshot ingestion."""

from workers.celery_app import celery_app


@celery_app.task(name="workers.ingestion.ingest_firms_snapshot")
def ingest_firms_snapshot(*args, **kwargs):
    raise NotImplementedError("FIRMS ingestion belongs to the data pipeline contributor")
