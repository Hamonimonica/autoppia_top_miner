"""Structured JSON logging for the agent process."""

from __future__ import annotations

import json
import logging


class StructuredFormatter(logging.Formatter):
    """JSON-lines formatter for structured log output."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in ("task_id", "url", "step_index", "action_type"):
            val = getattr(record, key, None)
            if val is not None:
                log_data[key] = val
        if record.exc_info and record.exc_info[0] is not None:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)


def configure_agent_logging() -> logging.Logger:
    """Attach structured handler to the ``agent`` logger (idempotent-safe)."""
    logger = logging.getLogger("agent")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger
