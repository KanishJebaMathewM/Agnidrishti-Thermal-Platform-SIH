# Operational API Contract

These service contracts are consumed by the FastAPI routes and frontend integration.

## Resolve routing

`GET /routing/resolve?lat={lat}&lon={lon}&classification={classification}&severity={severity}`

Returns `jurisdiction`, `classification`, `severity`, `primary_authority`, `secondary_authorities`, `routing_rule_matched`, and `authority_types_considered`.

## Notification preview

`POST /events/{event_id}/notification-preview`

Returns `event_id`, `subject`, `body_text`, `map_url`, `primary_recipient`, `secondary_recipients`, and compact evidence. It does not dispatch or create an action-taken record.

## Notification action log

`POST /events/{event_id}/notification-log`

Body:

```json
{"authority_id":"...","channel":"EMAIL","operator_id":"..."}
```

Allowed channels are `EMAIL`, `PHONE`, and `PORTAL`. A duplicate within the configured cooldown returns `DUPLICATE_SUPPRESSED`; a valid explicit action returns `DISPATCHED`.

## Human feedback

- `POST /events/{event_id}/confirm` with `reviewer` and `comment`.
- `POST /events/{event_id}/false-alarm` with `reviewer` and `comment`.
- `POST /events/{event_id}/reclassify` with `new_classification`, `reviewer`, and `comment`.

Each operation updates event workflow state and records the model prediction, human outcome, reviewer, and comment.

## Status vocabulary

The database-compatible names are `READY`, `PRESENTED`, and `ACTION_TAKEN`. They correspond to the master plan names `READY_TO_NOTIFY`, `CONTACT_PRESENTED`, and `ACTION_TAKEN`.
