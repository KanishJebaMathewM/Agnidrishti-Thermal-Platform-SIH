"""Human-controlled notification action logging with cooldown protection."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import text

try:
    from celery import shared_task
except ImportError:  # pragma: no cover - permits pure unit testing without Celery
    def shared_task(*args: Any, **kwargs: Any):
        def decorator(function: Any) -> Any:
            return function
        return decorator

VALID_CHANNELS = frozenset({"EMAIL", "PHONE", "PORTAL"})
READY = "READY"
PRESENTED = "PRESENTED"
ACTION_TAKEN = "ACTION_TAKEN"


async def _already_logged(db: Any, event_id: str, authority_id: str, channel: str, cutoff: datetime) -> bool:
    result = await db.execute(
        text(
            """
            SELECT 1 FROM notifications
            WHERE event_id = :event_id AND authority_id = :authority_id
              AND channel = :channel AND created_at >= :cutoff
            LIMIT 1
            """
        ),
        {"event_id": event_id, "authority_id": authority_id, "channel": channel, "cutoff": cutoff},
    )
    return result.fetchone() is not None


async def log_notification_action(
    db: Any,
    event_id: str,
    authority_id: str,
    channel: str,
    operator_id: str,
    cooldown_minutes: int = 60,
    now: datetime | None = None,
    allow_manual_resend: bool = False,
) -> dict[str, Any]:
    channel = channel.upper().strip()
    if channel not in VALID_CHANNELS:
        raise ValueError(f"channel must be one of {sorted(VALID_CHANNELS)}")
    if not operator_id.strip():
        raise ValueError("operator_id is required")
    if cooldown_minutes < 0:
        raise ValueError("cooldown_minutes cannot be negative")
    current_time = now or datetime.now(timezone.utc)
    if not allow_manual_resend and await _already_logged(db, event_id, authority_id, channel, current_time - timedelta(minutes=cooldown_minutes)):
        return {"status": "DUPLICATE_SUPPRESSED", "event_id": event_id, "authority_id": authority_id, "channel": channel}
    await db.execute(
        text(
            """
            INSERT INTO notifications
              (id, event_id, authority_id, channel, status, alert_content,
               presented_at, action_taken_at, operator_id, created_at)
            VALUES
              (gen_random_uuid(), :event_id, :authority_id, :channel, :status,
               CAST(:alert_content AS jsonb), :presented_at, :action_taken_at,
               :operator_id, :created_at)
            """
        ),
        {
            "event_id": event_id,
            "authority_id": authority_id,
            "channel": channel,
            "status": ACTION_TAKEN,
            "alert_content": "{}",
            "presented_at": current_time,
            "action_taken_at": current_time,
            "operator_id": operator_id.strip(),
            "created_at": current_time,
        },
    )
    return {"status": "DISPATCHED", "event_id": event_id, "authority_id": authority_id, "channel": channel, "operator_id": operator_id.strip()}


@shared_task(name="workers.notifications.send_notification")
def send_notification(event_id: str, authority_id: str, channel: str, operator_id: str) -> dict[str, Any]:
    """Task boundary; API code should call log_notification_action with a DB session."""
    return {"status": "REQUIRES_OPERATOR_DB_ACTION", "event_id": event_id, "authority_id": authority_id, "channel": channel, "operator_id": operator_id}
