"""Celery task placeholder for observation preprocessing."""

from workers.celery_app import celery_app


@celery_app.task(name="workers.preprocessing.preprocess_observation")
def preprocess_observation(*args, **kwargs):
    raise NotImplementedError("Observation preprocessing belongs to the data pipeline contributor")
