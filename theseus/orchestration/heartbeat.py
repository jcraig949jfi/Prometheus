"""Per-batch heartbeat logging for the Theseus daemon loop.

Fire #70 incident: a batch ran for 60+ minutes consuming 50% CPU and
15+ GB RAM while writing only 4 records (all in the first second).
The daemon's per-batch loop had ZERO observability into:
  - What gen was currently running
  - Whether next() calls were slow
  - Whether all gens were returning None
  - How memory grew over time

This module fixes that. The HeartbeatLogger:
  1. Records every N seconds (default 30s) to a per-batch JSONL
  2. Emits per-gen tick counts, consecutive-Nones, last-emit time
  3. Tees a short summary line to stdout for live visibility
  4. Captures process RSS so we see RAM growth fire-to-fire
  5. Records slow-next() warnings (per-gen p99 next() duration > threshold)

Reads cleanly:
    heartbeat_<batch_id>.jsonl

Each line is one snapshot with elapsed_s, tick_count, records, RAM,
per-gen status. Easy to grep for stalls post-hoc.

Designed to be hot-path cheap: snapshot operations are O(n_gens),
no I/O between snapshots; one append per tick interval.
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterator, List, Optional


def _process_rss_mb() -> float:
    """Return current process RSS in MB. Falls back to 0.0 if psutil
    is not available (the project doesn't require psutil)."""
    try:
        import psutil  # type: ignore
        return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
    except Exception:
        # Windows-friendly fallback via WMI: also optional. Return 0 if
        # both fail — heartbeat still works, just without RAM data.
        try:
            import resource  # type: ignore
            return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
        except Exception:
            return 0.0


@dataclass
class GenStats:
    """Per-generator tick-level stats during the batch."""
    tick_count: int = 0
    none_count: int = 0
    consecutive_nones: int = 0
    record_count: int = 0
    error_count: int = 0
    last_emit_at: Optional[float] = None  # monotonic seconds
    last_call_at: Optional[float] = None
    total_next_seconds: float = 0.0
    max_next_seconds: float = 0.0
    slow_next_count: int = 0  # next() calls > slow_threshold


class HeartbeatLogger:
    """Periodic heartbeat for the daemon batch loop.

    Usage:

        hb = HeartbeatLogger(
            batch_id=batch_id,
            journal_dir=JOURNAL_DIR,
            interval_seconds=30,
            slow_next_threshold_seconds=5.0,
        )
        hb.start(generator_ids)
        ...
        for g in instances:
            with hb.tick(g.generator_id):
                rec = g.next()
            hb.record_result(g.generator_id, rec)
            hb.maybe_snapshot(tick_count, records_written)
        ...
        hb.final_snapshot(tick_count, records_written)
        hb.close()
    """

    def __init__(
        self,
        batch_id: str,
        journal_dir: Path,
        interval_seconds: float = 30.0,
        slow_next_threshold_seconds: float = 5.0,
        tee_stdout: bool = True,
        watchdog_stall_threshold_seconds: float = 60.0,
        watchdog_poll_seconds: float = 10.0,
    ) -> None:
        self.batch_id = batch_id
        self.path = journal_dir / f"heartbeat_{batch_id}.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.interval = interval_seconds
        self.slow_threshold = slow_next_threshold_seconds
        self.tee_stdout = tee_stdout
        self.watchdog_stall_threshold = watchdog_stall_threshold_seconds
        self.watchdog_poll_seconds = watchdog_poll_seconds
        self._gen_stats: Dict[str, GenStats] = defaultdict(GenStats)
        self._start_mono: float = 0.0
        self._last_snapshot_mono: float = 0.0
        self._snapshot_count: int = 0
        self._fh = None  # opened in start()
        # Watchdog: independent thread that detects main-loop stalls (e.g.
        # hung-in-next() bugs like Fires #100/#112/#116). The inline
        # heartbeat snapshots are scheduled by maybe_snapshot() at the end
        # of each tick — if a single .next() call hangs, no snapshot fires.
        # The watchdog runs in its own thread and writes a stall event
        # when no tick activity for watchdog_stall_threshold seconds.
        self._write_lock = threading.Lock()
        self._last_tick_at: float = 0.0
        self._last_stall_warning_at: float = 0.0
        self._watchdog_thread: Optional[threading.Thread] = None
        self._watchdog_stop = threading.Event()

    def start(self, generator_ids: List[str]) -> None:
        self._start_mono = time.monotonic()
        self._last_snapshot_mono = self._start_mono
        self._last_tick_at = self._start_mono
        for gid in generator_ids:
            self._gen_stats[gid]  # touch to create default entry
        self._fh = self.path.open("w", encoding="utf-8")
        self._write({
            "event": "batch_start",
            "elapsed_s": 0.0,
            "batch_id": self.batch_id,
            "generator_ids": list(generator_ids),
            "process_rss_mb": _process_rss_mb(),
        })
        # Spawn watchdog thread AFTER batch_start is written
        self._watchdog_stop.clear()
        self._watchdog_thread = threading.Thread(
            target=self._watchdog_loop,
            name=f"hb-watchdog-{self.batch_id}",
            daemon=True,
        )
        self._watchdog_thread.start()

    def _watchdog_loop(self) -> None:
        """Background thread: detect main-loop stalls.

        Polls every watchdog_poll_seconds. If the main thread hasn't
        called tick() in > watchdog_stall_threshold seconds, write a
        stall event to the JSONL. Re-warns every threshold-interval
        thereafter so single warnings don't get lost in long stalls.
        """
        while not self._watchdog_stop.is_set():
            self._watchdog_stop.wait(self.watchdog_poll_seconds)
            if self._watchdog_stop.is_set():
                return
            now = time.monotonic()
            since_tick = now - self._last_tick_at
            if since_tick < self.watchdog_stall_threshold:
                continue
            # Rate-limit warnings: at most once per stall_threshold seconds
            if now - self._last_stall_warning_at < self.watchdog_stall_threshold:
                continue
            self._last_stall_warning_at = now
            # Find which gen was last ticked (best-effort attribution)
            last_gen = None
            last_call_at = 0.0
            for gid, gs in self._gen_stats.items():
                if gs.last_call_at and gs.last_call_at > last_call_at:
                    last_call_at = gs.last_call_at
                    last_gen = gid
            self._write({
                "event": "watchdog_stall",
                "elapsed_s": round(now - self._start_mono, 2),
                "seconds_since_last_tick": round(since_tick, 1),
                "last_ticked_gen": last_gen,
                "process_rss_mb": round(_process_rss_mb(), 1),
            })
            if self.tee_stdout:
                print(
                    f"[watchdog] STALL: no tick for {since_tick:.0f}s "
                    f"(last gen: {last_gen}, rss={_process_rss_mb():.0f}MB)",
                    flush=True,
                )

    @contextmanager
    def tick(self, generator_id: str) -> Iterator[None]:
        """Wrap a single gen.next() call. Records duration + slow warnings."""
        t0 = time.monotonic()
        self._last_tick_at = t0  # watchdog: I'm alive
        gs = self._gen_stats[generator_id]
        gs.tick_count += 1
        gs.last_call_at = t0
        try:
            yield
        finally:
            dt = time.monotonic() - t0
            gs.total_next_seconds += dt
            if dt > gs.max_next_seconds:
                gs.max_next_seconds = dt
            if dt >= self.slow_threshold:
                gs.slow_next_count += 1
                self._write({
                    "event": "slow_next",
                    "elapsed_s": round(time.monotonic() - self._start_mono, 2),
                    "generator_id": generator_id,
                    "next_seconds": round(dt, 3),
                    "max_seconds_for_gen": round(gs.max_next_seconds, 3),
                })

    def record_result(self, generator_id: str, record: Optional[object]) -> None:
        gs = self._gen_stats[generator_id]
        if record is None:
            gs.none_count += 1
            gs.consecutive_nones += 1
        else:
            gs.record_count += 1
            gs.consecutive_nones = 0
            gs.last_emit_at = time.monotonic()

    def record_error(self, generator_id: str) -> None:
        self._gen_stats[generator_id].error_count += 1

    def mark_exhausted(self, generator_id: str) -> None:
        elapsed = time.monotonic() - self._start_mono
        self._write({
            "event": "exhausted",
            "elapsed_s": round(elapsed, 2),
            "generator_id": generator_id,
            "tick_count": self._gen_stats[generator_id].tick_count,
            "record_count": self._gen_stats[generator_id].record_count,
            "consecutive_nones_at_exhaust": self._gen_stats[generator_id].consecutive_nones,
        })

    def maybe_snapshot(self, tick_count: int, records_written: int) -> None:
        now = time.monotonic()
        if now - self._last_snapshot_mono < self.interval:
            return
        self._snapshot(tick_count, records_written, kind="periodic")
        self._last_snapshot_mono = now

    def final_snapshot(self, tick_count: int, records_written: int) -> None:
        self._snapshot(tick_count, records_written, kind="final")

    def batch_end(
        self,
        tick_count: int,
        records_written: int,
        kills: int = 0,
        confirmations: int = 0,
        exit_reason: str = "normal",
    ) -> None:
        """Emit a batch_end event marking clean batch completion.

        Absence of this event in the JSONL = the process exited
        unexpectedly (silent crash like Fires #112 / #116 pre-fix).
        Presence + correct counts = clean shutdown.
        """
        elapsed = time.monotonic() - self._start_mono
        self._write({
            "event": "batch_end",
            "elapsed_s": round(elapsed, 2),
            "tick_count": tick_count,
            "records_written": records_written,
            "kills": kills,
            "confirmations": confirmations,
            "exit_reason": exit_reason,
            "process_rss_mb": round(_process_rss_mb(), 1),
        })

    def _snapshot(self, tick_count: int, records_written: int, kind: str) -> None:
        self._snapshot_count += 1
        elapsed = time.monotonic() - self._start_mono
        now = time.monotonic()
        per_gen = {}
        for gid, gs in self._gen_stats.items():
            time_since_emit = (
                round(now - gs.last_emit_at, 1) if gs.last_emit_at else None
            )
            avg_next_ms = (
                round((gs.total_next_seconds / gs.tick_count) * 1000, 2)
                if gs.tick_count > 0 else 0.0
            )
            per_gen[gid] = {
                "ticks": gs.tick_count,
                "records": gs.record_count,
                "consec_nones": gs.consecutive_nones,
                "errors": gs.error_count,
                "time_since_last_emit_s": time_since_emit,
                "avg_next_ms": avg_next_ms,
                "max_next_s": round(gs.max_next_seconds, 3),
                "slow_calls": gs.slow_next_count,
            }
        snapshot = {
            "event": "snapshot",
            "kind": kind,
            "snapshot_n": self._snapshot_count,
            "elapsed_s": round(elapsed, 2),
            "tick_count": tick_count,
            "tick_rate_per_s": (
                round(tick_count / elapsed, 1) if elapsed > 0 else 0.0
            ),
            "records_written": records_written,
            "process_rss_mb": round(_process_rss_mb(), 1),
            "per_gen": per_gen,
        }
        self._write(snapshot)
        if self.tee_stdout:
            line = self._stdout_line(snapshot)
            print(line, flush=True)

    def _stdout_line(self, snapshot: dict) -> str:
        elapsed_min = snapshot["elapsed_s"] / 60.0
        parts = [
            f"[heartbeat] t={elapsed_min:.1f}min",
            f"records={snapshot['records_written']:,}",
            f"ticks={snapshot['tick_count']:,}",
            f"rate={snapshot['tick_rate_per_s']:.1f}/s",
            f"rss={snapshot['process_rss_mb']:.0f}MB",
        ]
        # Per-gen short status: gid:ticks:records (or :STALLED if no emit in 60s)
        for gid, g in snapshot["per_gen"].items():
            since = g["time_since_last_emit_s"]
            status = ""
            if g["records"] == 0:
                status = "noemit"
            elif since is not None and since > 60:
                status = f"stalled{since:.0f}s"
            tag = f":{status}" if status else ""
            parts.append(f"{gid}={g['records']:,}/{g['ticks']:,}{tag}")
        return " ".join(parts)

    def _write(self, payload: dict) -> None:
        if self._fh is None:
            return
        with self._write_lock:
            if self._fh is None:
                return
            self._fh.write(json.dumps(payload, sort_keys=True) + "\n")
            self._fh.flush()

    def close(self) -> None:
        # Stop watchdog first to avoid writes after fh close
        self._watchdog_stop.set()
        if self._watchdog_thread is not None:
            self._watchdog_thread.join(timeout=2.0)
            self._watchdog_thread = None
        if self._fh is not None:
            with self._write_lock:
                self._fh.close()
                self._fh = None
