import logging
import json
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    """
    Structured JSON formatter.
    Every log line includes: timestamp, level, service, event_type, and trace_id (if available).
    """
    def format(self, record):
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "service": "agnidrishti-backend",
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Inject extra attributes like event_type and trace_id if they exist
        log_record["event_type"] = getattr(record, "event_type", "system_event")
        
        trace_id = getattr(record, "trace_id", None)
        if trace_id:
            log_record["trace_id"] = trace_id

        # If exception information is present, include it
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record)

def setup_logging():
    """Overrides default root logger configuration with JSON output."""
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Remove existing handlers to avoid duplicate formats
    for h in root.handlers[:]:
        root.removeHandler(h)

    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    root.addHandler(handler)
