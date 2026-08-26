from datetime import datetime, timezone

import pytest

from workers.notifications.alert_composer import compose_event_alert_payload
from workers.notifications.notification_worker import log_notification_action


class Result:
    def __init__(self, row=None):
        self.row = row

    def fetchone(self):
        return self.row


class Session:
    def __init__(self, duplicate=False):
        self.duplicate = duplicate
        self.inserts = []

    async def execute(self, query, params):
        if "SELECT 1" in str(query):
            return Result(object() if self.duplicate else None)
        self.inserts.append(params)
        return Result()


def test_alert_payload_contains_actionable_evidence():
    payload = compose_event_alert_payload(
        {"id": "evt-1", "centroid_lat": 10, "centroid_lon": 76, "severity": "HIGH", "classification": "Forest Fire", "classification_confidence": 0.91, "anomaly_score": 0.94, "observation_count": 7},
        {"jurisdiction": {"state_name": "Kerala", "district_name": "Ernakulam"}, "primary_authority": {"department": "Forest"}, "secondary_authorities": []},
        "https://example.test/events",
    )
    assert payload["event_id"] == "evt-1"
    assert "91.0%" in payload["body_text"]
    assert payload["map_url"].startswith("https://example.test/events?")


@pytest.mark.asyncio
async def test_duplicate_action_is_suppressed():
    result = await log_notification_action(Session(duplicate=True), "evt", "auth", "email", "operator", now=datetime.now(timezone.utc))
    assert result["status"] == "DUPLICATE_SUPPRESSED"


@pytest.mark.asyncio
async def test_valid_action_is_logged():
    db = Session()
    result = await log_notification_action(db, "evt", "auth", "phone", "operator", now=datetime.now(timezone.utc))
    assert result["status"] == "DISPATCHED"
    assert db.inserts[0]["channel"] == "PHONE"


@pytest.mark.asyncio
async def test_invalid_channel_is_rejected():
    with pytest.raises(ValueError):
        await log_notification_action(Session(), "evt", "auth", "sms", "operator")
