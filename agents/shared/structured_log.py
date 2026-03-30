"""Structured JSON logging for Prometheus pipelines.

Provides consistent, machine-parseable log output alongside human-readable console logs.
Both pipelines (intelligence + forge) use this for unified monitoring.

Usage:
    from agents.shared.structured_log import get_logger
    log = get_logger("hermes", log_dir=Path("agents/hermes/logs"))
    log.info("Email sent", recipient="james@example.com", sections=3)
    log.event("cycle_complete", duration_s=45.2, items_processed=12)
"""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path


class StructuredFormatter(logging.Formatter):
    """Outputs JSON-structured log lines alongside human-readable format."""

    def __init__(self, agent_name: str):
        super().__init__()
        self.agent_name = agent_name

    def format(self, record):
        entry = {
            "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "agent": self.agent_name,
            "level": record.levelname,
            "msg": record.getMessage(),
        }
        # Include any extra fields passed via log.info("msg", extra={...})
        if hasattr(record, "structured_data"):
            entry.update(record.structured_data)
        return json.dumps(entry, default=str)


class HumanFormatter(logging.Formatter):
    """Human-readable console format with agent name prefix."""

    def __init__(self, agent_name: str):
        super().__init__(
            fmt=f"%(asctime)s [{agent_name.upper()}] %(message)s",
            datefmt="%H:%M:%S",
        )


class StructuredLogger:
    """Logger that writes both human-readable (console) and structured (file) output."""

    def __init__(self, name: str, log_dir: Path = None):
        self.name = name
        self._logger = logging.getLogger(f"prometheus.{name}")
        self._logger.setLevel(logging.DEBUG)

        # Don't duplicate if already configured
        if self._logger.handlers:
            return

        # Console handler (human-readable)
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(logging.INFO)
        console.setFormatter(HumanFormatter(name))
        self._logger.addHandler(console)

        # File handler (structured JSON)
        if log_dir:
            log_dir.mkdir(parents=True, exist_ok=True)
            today = datetime.now().strftime("%Y-%m-%d")
            fh = logging.FileHandler(
                log_dir / f"{name}_{today}.jsonl",
                encoding="utf-8",
            )
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(StructuredFormatter(name))
            self._logger.addHandler(fh)

    def _log(self, level, msg, **kwargs):
        """Log with optional structured data."""
        extra = {"structured_data": kwargs} if kwargs else {}
        self._logger.log(level, msg, extra=extra)

    def debug(self, msg, **kwargs):
        self._log(logging.DEBUG, msg, **kwargs)

    def info(self, msg, **kwargs):
        self._log(logging.INFO, msg, **kwargs)

    def warning(self, msg, **kwargs):
        self._log(logging.WARNING, msg, **kwargs)

    def error(self, msg, **kwargs):
        self._log(logging.ERROR, msg, **kwargs)

    def event(self, event_type: str, **kwargs):
        """Log a structured event (always INFO level)."""
        self._log(logging.INFO, f"EVENT: {event_type}", event=event_type, **kwargs)


def get_logger(agent_name: str, log_dir: Path = None) -> StructuredLogger:
    """Get or create a structured logger for an agent.

    Args:
        agent_name: Short name (e.g., "hermes", "eos", "metis", "hephaestus")
        log_dir: Directory for JSON log files. If None, console only.

    Returns:
        StructuredLogger instance with .info(), .warning(), .error(), .event() methods.
    """
    return StructuredLogger(agent_name, log_dir)
