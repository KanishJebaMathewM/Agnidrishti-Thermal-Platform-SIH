"""Pure alert payload composition; this module never dispatches messages."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlencode


def compose_event_alert_payload(event: dict[str, Any], route: dict[str, Any], dashboard_base_url: str = "https://agnidrishti.gov.in/events") -> dict[str, Any]:
    jurisdiction = route.get("jurisdiction") or {}
    event_id = str(event["id"])
    lat = event["centroid_lat"]
    lon = event["centroid_lon"]
    severity = str(event.get("severity", "NORMAL"))
    classification = str(event.get("classification", "Unknown"))
    confidence = float(event.get("classification_confidence") or 0.0)
    anomaly_score = event.get("anomaly_score")
    map_url = f"{dashboard_base_url}?{urlencode({'id': event_id, 'lat': lat, 'lon': lon})}"
    district = jurisdiction.get("district_name", event.get("district", "Unknown"))
    state = jurisdiction.get("state_name", event.get("state", "Unknown"))
    subject = f"[AGNIDRISHTI {severity} ALERT] {classification} in {district}, {state}"
    body = "\n".join(
        [
            "AGNIDRISHTI THERMAL ANOMALY INTELLIGENCE ALERT",
            f"Event ID: {event_id}",
            f"Severity: {severity}",
            f"Classification: {classification} (Confidence: {confidence * 100:.1f}%)",
            f"Location: {float(lat):.4f} N, {float(lon):.4f} E ({district}, {state})",
            f"First Seen: {event.get('first_seen', 'Unknown')}",
            f"Last Seen: {event.get('last_seen', 'Unknown')}",
            f"Observation Count: {event.get('observation_count', 0)}",
            f"Anomaly Score: {anomaly_score if anomaly_score is not None else 'Unknown'}",
            f"Dashboard: {map_url}",
            "Recommended action: verify the event and contact the configured primary authority.",
        ]
    )
    return {
        "event_id": event_id,
        "subject": subject,
        "body_text": body,
        "map_url": map_url,
        "primary_recipient": route.get("primary_authority"),
        "secondary_recipients": route.get("secondary_authorities", []),
        "evidence": {
            "confidence": confidence,
            "anomaly_score": anomaly_score,
            "observation_count": event.get("observation_count", 0),
        },
    }
