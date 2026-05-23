"""
Shared logging + orchestration-event helpers for the M4 reporting tier.

Two things in one module:
  1. `get_logger(name)` — returns a configured Python logger with file
     handler at logs/<name>.log + stdout handler. Idempotent.
  2. `emit_event(stage, summary, ...)` — convenience wrapper around
     session_telemetry.log_work that pulls cycle_id from the
     PROMETHEUS_CYCLE_ID environment variable. This is how the
     intelligence_loop daemon threads a single cycle_id through every
     child script in one hourly tick so the dashboard groups them.

Convention: orchestration scripts should call `emit_event(stage, summary,
output_path)` at every meaningful boundary — script start, major
substeps, success/failure exit. The dashboard's "intelligence pipeline"
section reads from agora.intelligence_outputs filtered by stage.

Stage taxonomy (orchestration tier):
  pronoia_cycle_started       — hourly tick begins
  pronoia_portfolio_refresh   — portfolio_monitor.py finished
  pronoia_brief_generated     — metis_portfolio.py finished
  pronoia_dashboard_pushed    — git push of docs/* completed
  pronoia_email_dispatched    — send_brief_email.py finished
  pronoia_weekly_recap        — weekly_recap.py finished
  pronoia_cycle_complete      — hourly tick ends with summary
  metis_brief_generated       — Metis script self-reports success
  portfolio_monitor_run       — portfolio_monitor self-reports
  email_dispatched            — send_brief_email self-reports
  weekly_recap_generated      — weekly_recap self-reports
  calliope_daily_narrative    — (existing) calliope self-reports

These names match patterns the Metis prompt already understands.
"""
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = REPO_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# session_telemetry import is fail-soft — emit_event becomes a no-op
# rather than raising if Postgres / agora_persist are unreachable.
sys.path.insert(0, str(REPO_ROOT / "scripts"))
try:
    import session_telemetry
    HAS_TELEMETRY = True
except Exception as e:
    print(f"[orchestration_logging] session_telemetry unavailable ({e})",
          file=sys.stderr)
    HAS_TELEMETRY = False
    session_telemetry = None


_LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s %(message)s"
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Return a configured logger writing to logs/<name>.log + stdout.

    Idempotent: re-importing or calling get_logger(name) twice doesn't
    duplicate handlers. Loggers do not propagate to the root logger so
    they don't collide with logging.basicConfig calls elsewhere.
    """
    logger = logging.getLogger(name)
    if getattr(logger, "_orchestration_configured", False):
        return logger
    logger.setLevel(level)
    logger.propagate = False
    fmt = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    try:
        fh = logging.FileHandler(str(LOG_DIR / f"{name}.log"), encoding="utf-8")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    except Exception as e:
        print(f"[orchestration_logging] file handler for {name} failed: {e}",
              file=sys.stderr)
    logger._orchestration_configured = True  # type: ignore[attr-defined]
    return logger


def _get_cycle_id() -> Optional[str]:
    """Return the current Pronoia cycle UUID, if set in the env."""
    return os.environ.get("PROMETHEUS_CYCLE_ID") or None


def emit_event(
    stage: str,
    summary: str = "",
    success: bool = True,
    output_path: Optional[str] = None,
    error: Optional[str] = None,
    agent: Optional[str] = None,
    cycle_id: Optional[str] = None,
    duration_sec: Optional[float] = None,
    started_at: Optional[datetime] = None,
) -> bool:
    """Emit one orchestration-tier event to agora.intelligence_outputs.

    Pulls cycle_id from PROMETHEUS_CYCLE_ID env var if not passed explicitly.
    Fail-soft: returns False on any underlying failure rather than raising.
    """
    if not HAS_TELEMETRY:
        return False
    cid = cycle_id or _get_cycle_id()
    if duration_sec is not None and started_at is None:
        # Fabricate a started_at so log_intelligence_stage records the duration
        from datetime import timedelta
        started_at = datetime.now(timezone.utc) - timedelta(seconds=duration_sec)
    try:
        return session_telemetry.log_work(
            stage=stage,
            summary=summary,
            success=success,
            output_path=output_path,
            error=error,
            cycle_id=cid,
            agent=agent,
            started_at=started_at,
        )
    except Exception as e:
        print(f"[orchestration_logging] emit_event({stage}) failed: {e}",
              file=sys.stderr)
        return False


def new_cycle_id() -> str:
    """Generate a fresh cycle_id (UUID4 hex). Used by intelligence_loop.py
    at the top of each hourly tick to mint a new grouping key."""
    import uuid
    return uuid.uuid4().hex
