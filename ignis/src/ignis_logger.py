"""
Ignis — Structured Logging Framework

Provides context-aware logging with hierarchical markers:
  [MODEL:qwen2.5-0.5b] [GEN:042] [GENOME:007/020] [TRAP:decimal_magnitude] [STEP:score]

All log lines are prefixed with the current context so that logs can be
grep'd / filtered by any dimension.

Usage:
    from ignis_logger import slog, LogContext

    with LogContext(model="Qwen/Qwen2.5-0.5B", generation=5):
        slog.info("Starting evaluation")
        with LogContext(genome_idx=3, genome_total=20):
            slog.trace("Sampling vector from CMA-ES distribution")
"""

import logging
import sys
import threading
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── Custom TRACE level (below DEBUG) ─────────────────────────────────────────
TRACE = 5
logging.addLevelName(TRACE, "TRACE")


class _ContextStore(threading.local):
    """Thread-local storage for the current log context stack."""
    def __init__(self):
        super().__init__()
        self.stack: list[dict] = []

    @property
    def merged(self) -> dict:
        result = {}
        for frame in self.stack:
            result.update(frame)
        return result

    def push(self, ctx: dict):
        self.stack.append(ctx)

    def pop(self):
        if self.stack:
            self.stack.pop()


_ctx = _ContextStore()


class _ContextFormatter(logging.Formatter):
    """Formatter that prepends the current context markers to every log line."""

    _KEY_ORDER = ["cycle", "model", "gen", "genome", "trap", "step"]

    def format(self, record: logging.LogRecord) -> str:
        ctx = _ctx.merged
        parts = []
        for key in self._KEY_ORDER:
            if key in ctx:
                parts.append(f"[{key.upper()}:{ctx[key]}]")
        # Include any extra keys not in the standard order
        for key, val in ctx.items():
            if key not in self._KEY_ORDER:
                parts.append(f"[{key.upper()}:{val}]")

        prefix = " ".join(parts)
        ts = self.formatTime(record, self.datefmt)
        level = record.levelname
        msg = record.getMessage()
        base = f"{ts} {level:>5s} {prefix} {msg}" if prefix else f"{ts} {level:>5s} {msg}"

        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            base += "\n" + record.exc_text
        return base


class _IgnisLogger:
    """Thin wrapper around stdlib logger with .trace() and context awareness."""

    def __init__(self):
        self._logger = logging.getLogger("ignis")
        self._logger.setLevel(TRACE)
        self._logger.propagate = False  # prevent duplicate output via root logger
        self._configured = False

    def configure(self, log_dir: Optional[Path] = None, console_level: int = logging.INFO,
                  file_level: int = TRACE):
        """Call once at startup to set up handlers."""
        if self._configured:
            return
        self._configured = True

        fmt = _ContextFormatter(datefmt="%Y-%m-%d %H:%M:%S")

        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(console_level)
        ch.setFormatter(fmt)
        self._logger.addHandler(ch)

        # File handler (if log_dir provided)
        if log_dir:
            log_dir = Path(log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "ignis.log"

            # Rotate existing log to timestamped archive before starting fresh
            if log_file.exists() and log_file.stat().st_size > 0:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                archive_name = log_dir / f"ignis_{ts}.log"
                try:
                    log_file.rename(archive_name)
                except OSError:
                    # File may be locked on Windows; fall back to copy + truncate
                    import shutil
                    shutil.copy2(log_file, archive_name)

            fh = logging.FileHandler(log_file, mode="w", encoding="utf-8")
            fh.setLevel(file_level)
            fh.setFormatter(fmt)
            self._logger.addHandler(fh)

    # ── Standard levels ──────────────────────────────────────────────────
    def trace(self, msg, *args, **kw):
        self._logger.log(TRACE, msg, *args, **kw)

    def debug(self, msg, *args, **kw):
        self._logger.log(logging.DEBUG, msg, *args, **kw)

    def info(self, msg, *args, **kw):
        self._logger.log(logging.INFO, msg, *args, **kw)

    def warning(self, msg, *args, **kw):
        self._logger.log(logging.WARNING, msg, *args, **kw)

    def error(self, msg, *args, **kw):
        self._logger.log(logging.ERROR, msg, *args, **kw)

    def critical(self, msg, *args, **kw):
        self._logger.log(logging.CRITICAL, msg, *args, **kw)

    def exception(self, msg, *args, **kw):
        self._logger.log(logging.ERROR, msg, *args, exc_info=True, **kw)


# Module-level singleton
slog = _IgnisLogger()


@contextmanager
def LogContext(**kwargs):
    """Push a context frame for the duration of a with-block.

    Example:
        with LogContext(model="Qwen/Qwen2.5-0.5B", gen=5):
            slog.info("evaluating")   # [MODEL:Qwen/Qwen2.5-0.5B] [GEN:5] evaluating
    """
    _ctx.push(kwargs)
    try:
        yield
    finally:
        _ctx.pop()

