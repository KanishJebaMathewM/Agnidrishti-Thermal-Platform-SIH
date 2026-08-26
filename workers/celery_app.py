from celery import Celery

from app.config import settings

celery_app = Celery(
    "agnidrishti",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "workers.ingestion.firms_worker",
        "workers.preprocessing.preprocess_worker",
        "workers.events.event_worker",
        "workers.notifications.notification_worker",
    ],
)
celery_app.conf.task_routes = {
    "workers.ingestion.*": {"queue": "ingestion"},
    "workers.preprocessing.*": {"queue": "processing"},
    "workers.events.*": {"queue": "events"},
    "workers.notifications.*": {"queue": "notifications"},
}
