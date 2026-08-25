"""Human verification and training-label persistence."""

from __future__ import annotations

from typing import Any

from sqlalchemy import text


async def _event_prediction(db: Any, event_id: str) -> dict[str, Any]:
    result = await db.execute(
        text("SELECT classification, classification_confidence FROM events WHERE id = :event_id"),
        {"event_id": event_id},
    )
    row = result.fetchone()
    if row is None:
        raise LookupError(f"event {event_id} was not found")
    return dict(row._mapping)


async def _record_feedback(db: Any, event_id: str, reviewer: str, comment: str, human_label: str) -> dict[str, Any]:
    if not reviewer.strip():
        raise ValueError("reviewer is required")
    prediction = await _event_prediction(db, event_id)
    await db.execute(
        text(
            """
            INSERT INTO operator_feedback
              (id, event_id, model_prediction, model_confidence, human_label, reviewer, comment, verified_at)
            VALUES
              (gen_random_uuid(), :event_id, :model_prediction, :model_confidence,
               :human_label, :reviewer, :comment, CURRENT_TIMESTAMP)
            """
        ),
        {
            "event_id": event_id,
            "model_prediction": prediction["classification"],
            "model_confidence": prediction["classification_confidence"],
            "human_label": human_label,
            "reviewer": reviewer.strip(),
            "comment": comment,
        },
    )
    await db.execute(
        text(
            """
            INSERT INTO training_labels
              (id, observation_id, label, label_source, label_confidence, verification_status, labeled_at)
            SELECT gen_random_uuid(), eo.observation_id, :label, 'operator_feedback', 1.0, 'VERIFIED', CURRENT_TIMESTAMP
            FROM event_observations eo
            WHERE eo.event_id = :event_id
            """
        ),
        {"event_id": event_id, "label": human_label},
    )
    return {"event_id": event_id, "model_prediction": prediction["classification"], "human_label": human_label}


async def record_human_confirmation(db: Any, event_id: str, reviewer: str, comment: str) -> dict[str, Any]:
    result = await _record_feedback(db, event_id, reviewer, comment, "CONFIRMED")
    await db.execute(text("UPDATE events SET status = 'CONFIRMED', updated_at = CURRENT_TIMESTAMP WHERE id = :event_id"), {"event_id": event_id})
    return {"status": "CONFIRMED", **result}


async def record_false_alarm(db: Any, event_id: str, reviewer: str, comment: str) -> dict[str, Any]:
    result = await _record_feedback(db, event_id, reviewer, comment, "FALSE_ALARM")
    await db.execute(text("UPDATE events SET status = 'FALSE_ALARM', updated_at = CURRENT_TIMESTAMP WHERE id = :event_id"), {"event_id": event_id})
    return {"status": "FALSE_ALARM", **result}


async def record_reclassification(db: Any, event_id: str, new_class: str, reviewer: str, comment: str) -> dict[str, Any]:
    if not new_class.strip():
        raise ValueError("new classification is required")
    result = await _record_feedback(db, event_id, reviewer, comment, new_class.strip())
    await db.execute(
        text("UPDATE events SET classification = :classification, status = 'RECLASSIFIED', updated_at = CURRENT_TIMESTAMP WHERE id = :event_id"),
        {"event_id": event_id, "classification": new_class.strip()},
    )
    return {"status": "RECLASSIFIED", "new_classification": new_class.strip(), **result}
