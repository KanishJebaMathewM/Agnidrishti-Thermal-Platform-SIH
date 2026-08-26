# AGNIDRISHTI System Overview

AGNIDRISHTI processes India-focused thermal observations into explainable events and human-controlled operational actions.

## Operational loop

```text
Observation -> preprocessing/enrichment -> classification and anomaly
           -> event formation and severity -> jurisdiction -> authority route
           -> operator preview -> human action -> feedback and audit
```

Contributor 5 owns the final operational segment. Routing does not change the ML result and never searches for contacts dynamically.

## Routing

The backend sends an event centroid to PostGIS. `ST_Contains` resolves the configured administrative boundary. The state and district then select active authority records and routing profiles. Classification determines the ordered authority types; severity remains part of the returned decision context.

No matching polygon returns `Unknown / Offshore`. No matching authority returns an empty route rather than an invented contact.

## Notification lifecycle

`READY` means a notification may be presented. `PRESENTED` means the operator has seen the contact and alert. `ACTION_TAKEN` means the operator explicitly logged an email, phone, or portal action. Preview never dispatches externally.

One event, authority, and channel is protected by a configurable cooldown. Manual resend is explicit and auditable.

## Data provenance

Events retain links to observations. Routing results identify the jurisdiction and configured authority records. Notification records retain event, authority, channel, operator, and timestamps. Feedback records retain the model prediction, human label, reviewer, and comment.

A dedicated `audit_logs` table is a future database enhancement; the current MVP uses notification and operator-feedback records as operational audit records.
