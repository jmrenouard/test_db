"""Structured JSON line logging utilities for the Sirene ETL pipeline."""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any

_STANDARD_RECORD_ATTRS = frozenset(
    logging.LogRecord("", 0, "", 0, "", (), None).__dict__.keys()
) | {"message", "asctime"}
_CORE_KEYS = frozenset({"timestamp", "level", "logger", "message"})


class JsonLineFormatter(logging.Formatter):
    """Format log records as compact single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        """Serialize a logging.LogRecord and any extra attributes as JSON."""
        timestamp = datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(
            timespec="milliseconds"
        )
        if timestamp.endswith("+00:00"):
            timestamp = timestamp[:-6] + "Z"

        payload: dict[str, Any] = {
            "timestamp": timestamp,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for key, value in record.__dict__.items():
            if (
                key not in _STANDARD_RECORD_ATTRS
                and key not in _CORE_KEYS
                and not key.startswith("_")
            ):
                payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            payload["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(
            payload,
            separators=(",", ":"),
            default=str,
            ensure_ascii=False,
        )


class _DynamicStdoutHandler(logging.StreamHandler):
    """StreamHandler that always emits to the active sys.stdout."""

    def __init__(self) -> None:
        super().__init__(sys.stdout)

    def emit(self, record: logging.LogRecord) -> None:
        # Refresh stream reference on emit so test stdout captures always work.
        self.stream = sys.stdout
        super().emit(record)


def _resolve_level(level: str | int | None) -> int:
    if isinstance(level, int):
        return level
    raw = level if level is not None else os.getenv("LOG_LEVEL", "INFO")
    normalized = str(raw).strip().upper()
    resolved = logging.getLevelName(normalized)
    if isinstance(resolved, int):
        return resolved
    return logging.INFO


def get_logger(name: str, level: str | int | None = None) -> logging.Logger:
    """Return a structured JSON logger writing compact JSON lines to stdout."""
    logger = logging.getLogger(name)
    logger.setLevel(_resolve_level(level))
    logger.propagate = False

    has_json_handler = any(
        isinstance(handler, _DynamicStdoutHandler) for handler in logger.handlers
    )
    if not has_json_handler:
        handler = _DynamicStdoutHandler()
        handler.setFormatter(JsonLineFormatter())
        logger.addHandler(handler)

    return logger
