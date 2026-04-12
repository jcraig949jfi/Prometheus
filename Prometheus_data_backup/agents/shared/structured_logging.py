"""Shared structured logging for all Prometheus agents.

Provides dual-output logging: existing text format (backward compatible)
+ JSON structured log stream (for aggregation by the Auditor agent).

Usage in any agent:
    from shared.structured_logging import get_logger
    log = get_logger("hephaestus")
    log.info("forge_complete", status="forged", accuracy=0.6, concepts=["A", "B", "C"])

This produces:
  1. Text line to stdout/file (existing format, unchanged):
     2026-03-27 08:00:00 [INFO] forge_complete
  2. JSON line appended to agents/{agent}/events.jsonl:
     {"timestamp": "2026-03-27T08:00:00", "agent": "hephaestus", "event": "forge_complete",
      "status": "forged", "accuracy": 0.6, "concepts": ["A", "B", "C"]}

The Auditor agent reads events.jsonl files from all agents.
"""

import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import structlog
    HAS_STRUCTLOG = True
except ImportError:
    HAS_STRUCTLOG = False

PROMETHEUS_ROOT = Path(__file__).resolve().parent.parent


def _json_serializer(obj):
    """Handle non-serializable types."""
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, set):
        return list(obj)
    return str(obj)


class JSONLWriter:
    """Append structured events to a JSONL file."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, event_dict: dict):
        """Append one JSON line."""
        try:
            line = json.dumps(event_dict, default=_json_serializer, ensure_ascii=False)
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass  # Never crash the agent over logging


class DualLogger:
    """Logger that writes to both the existing text logger AND a JSONL file.

    Maintains full backward compatibility with existing log scraping
    while adding structured events for the Auditor.
    """

    def __init__(self, agent_name: str, text_logger: logging.Logger, jsonl_writer: JSONLWriter):
        self.agent_name = agent_name
        self.text_logger = text_logger
        self.jsonl = jsonl_writer

    def _emit(self, level: str, event: str, **kwargs):
        """Emit to both text and structured streams."""
        # Text log (existing format — backward compatible)
        msg = event
        if kwargs:
            details = " ".join(f"{k}={v}" for k, v in kwargs.items()
                               if k not in ("_timestamp", "_agent"))
            if details:
                msg = f"{event} | {details}"
        getattr(self.text_logger, level)(msg)

        # Structured JSON event
        event_dict = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": self.agent_name,
            "level": level.upper(),
            "event": event,
        }
        event_dict.update(kwargs)
        self.jsonl.write(event_dict)

    def info(self, event: str, **kwargs):
        self._emit("info", event, **kwargs)

    def warning(self, event: str, **kwargs):
        self._emit("warning", event, **kwargs)

    def error(self, event: str, **kwargs):
        self._emit("error", event, **kwargs)

    def debug(self, event: str, **kwargs):
        self._emit("debug", event, **kwargs)

    # Proxy standard logging methods for backward compatibility
    def __getattr__(self, name):
        return getattr(self.text_logger, name)


def get_logger(agent_name: str, log_dir: Path | None = None) -> DualLogger:
    """Get a dual logger for an agent.

    Args:
        agent_name: e.g., "hephaestus", "nous", "nemesis", "coeus"
        log_dir: directory for events.jsonl. Defaults to agents/{agent_name}/

    Returns:
        DualLogger that writes text + JSONL
    """
    if log_dir is None:
        log_dir = PROMETHEUS_ROOT / "agents" / agent_name

    # Get or create the existing text logger
    text_logger = logging.getLogger(agent_name)

    # Create JSONL writer
    jsonl_path = log_dir / "events.jsonl"
    jsonl_writer = JSONLWriter(jsonl_path)

    return DualLogger(agent_name, text_logger, jsonl_writer)


def read_events(agent_name: str, since: datetime | None = None,
                event_filter: str | None = None,
                max_events: int = 1000) -> list[dict]:
    """Read structured events from an agent's events.jsonl.

    Used by the Auditor agent to aggregate across all agents.

    Args:
        agent_name: agent to read from
        since: only return events after this timestamp
        event_filter: only return events matching this event name
        max_events: maximum events to return (most recent first)

    Returns:
        list of event dicts, most recent first
    """
    jsonl_path = PROMETHEUS_ROOT / "agents" / agent_name / "events.jsonl"
    if not jsonl_path.exists():
        return []

    events = []
    try:
        with open(jsonl_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    if since:
                        ts = event.get("timestamp", "")
                        if ts < since.isoformat():
                            continue
                    if event_filter and event.get("event") != event_filter:
                        continue
                    events.append(event)
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass

    # Return most recent first, capped
    return events[-max_events:][::-1]


def read_all_events(since: datetime | None = None,
                    max_per_agent: int = 500) -> dict[str, list[dict]]:
    """Read structured events from ALL agents.

    Returns:
        dict: agent_name -> list of event dicts
    """
    agents_dir = PROMETHEUS_ROOT / "agents"
    result = {}

    for agent_dir in sorted(agents_dir.iterdir()):
        if not agent_dir.is_dir():
            continue
        events_file = agent_dir / "events.jsonl"
        if events_file.exists():
            events = read_events(agent_dir.name, since=since, max_events=max_per_agent)
            if events:
                result[agent_dir.name] = events

    return result
