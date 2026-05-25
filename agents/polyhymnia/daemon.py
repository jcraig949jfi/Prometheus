"""Polyhymnia — the one-tensor agent daemon.

See agents/polyhymnia/CHARTER.md for the full contract. Summary:
  - Picks the next scour in round-robin rotation each tick.
  - Runs the scour, integrates candidates into the tensor, appends lineage edges.
  - Emits artifact + heartbeat + log_work every tick (anti-silence per Telos doctrine).
  - Single-instance lock, persisted state, structured event JSONL.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import socket
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_THIS = Path(__file__).resolve()
REPO_ROOT = _THIS.parents[2]
AGENT_DIR = _THIS.parent

for p in (REPO_ROOT, REPO_ROOT / "scripts", REPO_ROOT / "aporia" / "scripts", REPO_ROOT / "agents"):
    sp = str(p)
    if sp not in sys.path:
        sys.path.insert(0, sp)

try:
    import session_telemetry
    HAS_TELEMETRY = True
except Exception:
    session_telemetry = None  # type: ignore
    HAS_TELEMETRY = False

try:
    from shared.structured_logging import get_logger as get_structured_logger
    HAS_STRUCTLOG = True
except Exception:
    get_structured_logger = None  # type: ignore
    HAS_STRUCTLOG = False

from agents.polyhymnia.tensor import PolyhymniaTensor
from agents.polyhymnia.scours import REGISTRY as SCOUR_REGISTRY
from agents._shared.self_improving import (
    SelfImprovingDaemon, Adaptation, HealthSample,
)

# Local paths
STATE_DIR = AGENT_DIR / "state"
ARTIFACT_DIR = AGENT_DIR / "artifacts"
LOG_DIR = AGENT_DIR / "logs"
TENSOR_DIR = AGENT_DIR / "tensor"
PID_FILE = AGENT_DIR / "polyhymnia.pid"
STATE_FILE = STATE_DIR / "state.json"
SI_STATE_FILE = STATE_DIR / "self_improvement.json"
TEXT_LOG = LOG_DIR / "polyhymnia.log"
APORIA_INBOX = REPO_ROOT / "aporia" / "meta" / "queue" / "aporia_inbox.jsonl"

# Defaults
DEFAULT_INTERVAL_SEC = 1800
ANTI_SILENCE_ALARM_THRESHOLD = 50
CHARTER_VERSION = "v1"
AGENT_NAME = "Polyhymnia"
OPERATOR = "Aporia"


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def _setup_text_logger() -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log = logging.getLogger("polyhymnia")
    if log.handlers:
        return log
    log.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s [POLYHYMNIA] %(message)s")
    sh = logging.StreamHandler(sys.stdout); sh.setFormatter(fmt); log.addHandler(sh)
    fh = logging.FileHandler(TEXT_LOG, encoding="utf-8"); fh.setFormatter(fmt); log.addHandler(fh)
    return log


_text_log = _setup_text_logger()
_evt_log = get_structured_logger("polyhymnia", log_dir=AGENT_DIR) if HAS_STRUCTLOG else None


def _emit_event(event: str, level: str = "info", **kwargs) -> None:
    try:
        if _evt_log:
            getattr(_evt_log, level)(event, **kwargs)
        else:
            details = " ".join(f"{k}={v}" for k, v in kwargs.items())
            getattr(_text_log, level)(f"{event} | {details}")
    except Exception as e:
        _text_log.warning(f"event emission failed: {e}")


# ---------------------------------------------------------------------------
# Single-instance lock (mirrors Hypatia/Atalanta/Pheme/Talos)
# ---------------------------------------------------------------------------

def _is_pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        if os.name == "nt":
            import ctypes
            h = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
            if not h:
                return False
            ctypes.windll.kernel32.CloseHandle(h)
            return True
        else:
            os.kill(pid, 0)
            return True
    except Exception:
        return False


def acquire_lock() -> bool:
    AGENT_DIR.mkdir(parents=True, exist_ok=True)
    if PID_FILE.exists():
        try:
            data = json.loads(PID_FILE.read_text(encoding="utf-8"))
            existing_pid = int(data.get("pid", 0))
            if existing_pid and existing_pid != os.getpid() and _is_pid_alive(existing_pid):
                _text_log.error(f"another polyhymnia instance is alive (pid={existing_pid}); aborting")
                return False
        except Exception:
            pass
    PID_FILE.write_text(json.dumps({
        "pid": os.getpid(),
        "hostname": socket.gethostname(),
        "started_at": datetime.now(timezone.utc).isoformat(),
    }), encoding="utf-8")
    return True


def release_lock() -> None:
    try:
        if PID_FILE.exists():
            data = json.loads(PID_FILE.read_text(encoding="utf-8"))
            if int(data.get("pid", 0)) == os.getpid():
                PID_FILE.unlink()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# State persistence
# ---------------------------------------------------------------------------

def _default_state() -> dict:
    return {
        "schema_version": 1,
        "charter_version": CHARTER_VERSION,
        "first_run_at": datetime.now(timezone.utc).isoformat(),
        "scour_rotation_cursor": 0,
        "scour_state": {},          # per-scour persistent state
        "scour_last_run_at": {},    # per-scour last-run timestamps
        "per_scour_tesserae_contributed": {},
        "total_tesserae_lifetime": 0,
        "total_lineage_lifetime": 0,
        "anti_silence_counter": 0,
        "total_ticks_lifetime": 0,
        "total_null_ticks_lifetime": 0,
        # Sliding window of recent tick outcomes — fuel for SelfImprover.measure_health.
        "recent_tick_outcomes": [],   # list of {at, new_tesserae, null_tick}
    }


def load_state() -> dict:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if not STATE_FILE.exists():
        return _default_state()
    try:
        s = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        # Defensive defaults for newly-added keys
        for k, v in _default_state().items():
            s.setdefault(k, v)
        return s
    except Exception as e:
        _emit_event("state_load_failed_using_default", level="warning", error=str(e))
        return _default_state()


def save_state(state: dict) -> None:
    state["last_save_at"] = datetime.now(timezone.utc).isoformat()
    tmp = STATE_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, indent=2), encoding="utf-8")
    tmp.replace(STATE_FILE)


# ---------------------------------------------------------------------------
# Self-improvement layer (SelfImprovingDaemon adoption)
# ---------------------------------------------------------------------------

def _adapt_drop_mtime_cache(agent, agent_state):
    """Adaptation: clear prometheus_self's path-mtime cache so the next tick
    forces a full rescan. Snapshot the cleared values for revert."""
    scour_state = agent_state.get("scour_state", {}).get("prometheus_self", {})
    snapshot = dict(scour_state.get("path_mtimes", {}))
    scour_state["path_mtimes"] = {}
    return snapshot


def _revert_drop_mtime_cache(agent, agent_state, snapshot):
    if snapshot:
        agent_state.setdefault("scour_state", {}).setdefault(
            "prometheus_self", {})["path_mtimes"] = snapshot


def _adapt_stub_log_only(name):
    """Build a no-op adaptation that just logs. Used for placeholders that
    document the menu growth path without doing fake work."""
    def _apply(agent, agent_state):
        _emit_event("self_improvement_stub_applied", level="info", stub=name)
        return None
    def _revert(agent, agent_state, snapshot):
        pass
    return _apply, _revert


class PolyhymniaSelfImprover(SelfImprovingDaemon):
    """Self-improvement layer for Polyhymnia. Composition-style: instantiated
    once at module level; called from inside run_tick."""

    AGENT_NAME_FOR_TICKETS = "Polyhymnia"
    SELF_SUMMON_INBOX_PATH = APORIA_INBOX
    HEALTH_WINDOW_TICKS = 10
    STAGNATION_THRESHOLD = 0.35
    EXPERIMENT_OBSERVATION_TICKS = 2     # short — Polyhymnia ticks slowly
    MAX_MUTATIONS_PER_DAY = 3            # conservative for v1

    # The Polyhymnia menu (v1). Two real adaptations; rest stubbed to document
    # the menu-growth path. As v2 ships, stubs become real apply()s.
    _stub1_apply, _stub1_revert = _adapt_stub_log_only("EXPAND_KW_RE_v1_placeholder")
    _stub2_apply, _stub2_revert = _adapt_stub_log_only("EXPAND_PATHS_v1_placeholder")
    _stub3_apply, _stub3_revert = _adapt_stub_log_only("EXPAND_FILE_TYPES_v1_placeholder")
    _stub4_apply, _stub4_revert = _adapt_stub_log_only("SPAWN_SIBLING_SCOUR_v1_placeholder")
    _stub5_apply, _stub5_revert = _adapt_stub_log_only("MODE_PIVOT_GAME_GEN_v1_placeholder")

    ADAPTATION_MENU = [
        Adaptation(
            name="DROP_MTIME_CACHE",
            description="Clear prometheus_self path-mtime cache → next tick does full rescan",
            cost="one_tick",
            reversibility="manual_via_revert",
            apply=_adapt_drop_mtime_cache,
            revert=_revert_drop_mtime_cache,
        ),
        Adaptation(
            name="EXPAND_KW_RE",
            description="Auto-mine top-5 free_tags from existing tesserae, add to KW_RE",
            cost="trivial", reversibility="manual_via_revert",
            apply=_stub1_apply, revert=_stub1_revert,
        ),
        Adaptation(
            name="EXPAND_PATHS",
            description="Add prometheus_data/, vault/, archive/, journal/, docs/ to WALK_ROOTS",
            cost="one_tick", reversibility="manual_via_revert",
            apply=_stub2_apply, revert=_stub2_revert,
        ),
        Adaptation(
            name="EXPAND_FILE_TYPES",
            description="Also walk *.md, *.yaml, *.json (currently only *.py)",
            cost="medium", reversibility="manual_via_revert",
            apply=_stub3_apply, revert=_stub3_revert,
        ),
        Adaptation(
            name="SPAWN_SIBLING_SCOUR",
            description="Auto-generate scours/<new_name>.py from template for a new source",
            cost="high", reversibility="manual_via_revert",
            apply=_stub4_apply, revert=_stub4_revert,
            requires_human_approval=True,    # spawning code is the dangerous one
        ),
        Adaptation(
            name="MODE_PIVOT_GAME_GEN",
            description="Stop extracting; for N ticks, query existing tesserae and emit games",
            cost="medium", reversibility="manual_via_revert",
            apply=_stub5_apply, revert=_stub5_revert,
        ),
    ]

    def measure_health(self, tick_stats: dict, agent_state: dict) -> HealthSample:
        recent = agent_state.get("recent_tick_outcomes", [])[-self.HEALTH_WINDOW_TICKS:]
        if not recent:
            # No history yet — call it healthy until we have data
            return HealthSample(null_rate=0.0, diversity=0.5,
                                downstream_consumption=0.0, novelty=0.5)
        n = len(recent)
        nulls = sum(1 for o in recent if o.get("null_tick"))
        new_total = sum(o.get("new_tesserae", 0) for o in recent)
        null_rate = nulls / n
        # Diversity proxy: did we add new tesserae across multiple ticks
        # (not all concentrated in one productive tick)?
        productive_ticks = sum(1 for o in recent if o.get("new_tesserae", 0) > 0)
        diversity = productive_ticks / n
        # Downstream consumption: not wired yet. 0 for now.
        downstream = 0.0
        # Novelty proxy: ratio of new vs total contributed
        novelty = min(1.0, new_total / max(1, n * 100))   # 100 new per tick = saturated novelty
        return HealthSample(
            null_rate=null_rate, diversity=diversity,
            downstream_consumption=downstream, novelty=novelty,
            extras={"recent_ticks": n, "recent_nulls": nulls,
                    "recent_new_tesserae": new_total},
        )


# Singleton — instantiated once
_SI = PolyhymniaSelfImprover()


# ---------------------------------------------------------------------------
# Tick
# ---------------------------------------------------------------------------

def run_tick(dry_run: bool = False, only_scour: Optional[str] = None) -> dict:
    tick_started = datetime.now(timezone.utc)
    stats = {
        "tick_started_at": tick_started.isoformat(),
        "action": None, "errors": 0,
        "scour_run": None, "candidates": 0, "new_tesserae": 0,
        "merged_tesserae": 0, "lineage_edges_added": 0,
        "null_tick": False,
    }
    state = load_state()
    state["total_ticks_lifetime"] += 1
    tensor = PolyhymniaTensor(TENSOR_DIR)

    if not SCOUR_REGISTRY:
        stats["action"] = "upstream_not_found"
        stats["null_tick"] = True
        ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
        (ARTIFACT_DIR / f"upstream_not_found_{tick_started.strftime('%Y%m%dT%H%M%S')}.json").write_text(
            json.dumps({"tick_at": tick_started.isoformat(),
                        "ask": "Register scours in agents/polyhymnia/scours/__init__.REGISTRY"},
                       indent=2), encoding="utf-8")
        state["anti_silence_counter"] += 1
        state["total_null_ticks_lifetime"] += 1
        if not dry_run:
            save_state(state)
        _emit_event("tick_end", **{k: v for k, v in stats.items() if not k.startswith("_")})
        return stats

    # Pick scour
    if only_scour:
        chosen = next((s() for s in SCOUR_REGISTRY if s.name == only_scour), None)
        if chosen is None:
            stats["action"] = "scour_not_found"
            stats["errors"] = 1
            _emit_event("scour_not_found", level="error", requested=only_scour)
            return stats
    else:
        idx = state["scour_rotation_cursor"] % len(SCOUR_REGISTRY)
        chosen = SCOUR_REGISTRY[idx]()
        state["scour_rotation_cursor"] = (idx + 1) % len(SCOUR_REGISTRY)

    stats["scour_run"] = chosen.name
    _emit_event("tick_start", scour=chosen.name,
                anti_silence_counter=state["anti_silence_counter"],
                tick_number=state["total_ticks_lifetime"])

    # Run scour
    scour_state = state["scour_state"].setdefault(chosen.name, {})
    try:
        candidates = chosen.discover(scour_state)
    except Exception as e:
        _emit_event("scour_exception", level="error",
                    scour=chosen.name, error=f"{type(e).__name__}: {e}")
        stats["errors"] = 1
        stats["action"] = f"scour_{chosen.name}_exception"
        save_state(state)
        return stats

    stats["candidates"] = len(candidates)

    if not candidates:
        stats["action"] = f"scour_{chosen.name}_null"
        stats["null_tick"] = True
        ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
        (ARTIFACT_DIR / f"null_{tick_started.strftime('%Y%m%dT%H%M%S')}.json").write_text(
            json.dumps({"tick_at": tick_started.isoformat(),
                        "scour": chosen.name,
                        "reason": "scour returned 0 candidates",
                        "scour_state": scour_state}, indent=2), encoding="utf-8")
        state["anti_silence_counter"] += 1
        state["total_null_ticks_lifetime"] += 1
        emit_log_work(f"polyhymnia_scour_{chosen.name}_run",
                      summary=f"Scour {chosen.name}: 0 candidates this tick.")
    else:
        if dry_run:
            stats["action"] = f"scour_{chosen.name}_would_integrate"
            _emit_event("dry_run_would_integrate",
                        scour=chosen.name, candidate_count=len(candidates))
        else:
            delta = tensor.integrate(candidates)
            stats["new_tesserae"] = delta["new"]
            stats["merged_tesserae"] = delta["merged"]
            stats["action"] = f"scour_{chosen.name}_integrated"
            edges = chosen.lineage(candidates)
            stats["lineage_edges_added"] = tensor.append_lineage(edges)
            # State bookkeeping
            per_scour = state["per_scour_tesserae_contributed"].setdefault(chosen.name, 0)
            state["per_scour_tesserae_contributed"][chosen.name] = per_scour + delta["new"]
            state["total_tesserae_lifetime"] += delta["new"]
            state["total_lineage_lifetime"] += stats["lineage_edges_added"]
            state["anti_silence_counter"] = 0
            ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
            tick_artifact = ARTIFACT_DIR / f"tick_{tick_started.strftime('%Y%m%dT%H%M%S')}.json"
            tick_artifact.write_text(json.dumps({**stats, "delta": delta,
                                                 "scour_state_size": len(json.dumps(scour_state))},
                                                indent=2), encoding="utf-8")
            emit_log_work(f"polyhymnia_scour_{chosen.name}_run",
                          summary=(f"Scour {chosen.name}: {len(candidates)} candidates → "
                                   f"{delta['new']} new + {delta['merged']} merged + "
                                   f"{stats['lineage_edges_added']} lineage edges. "
                                   f"Total tensor: {state['total_tesserae_lifetime']} cells lifetime."),
                          output_path=str(tick_artifact.relative_to(REPO_ROOT)))

    state["scour_last_run_at"][chosen.name] = tick_started.isoformat()

    # Anti-silence alarm
    if state["anti_silence_counter"] >= ANTI_SILENCE_ALARM_THRESHOLD:
        _emit_event("self_audit_null_alarm", level="error",
                    consecutive_null=state["anti_silence_counter"])
        emit_log_work("polyhymnia_self_audit_null",
                      summary=f"ALARM: {state['anti_silence_counter']} consecutive null ticks.",
                      success=False, error="anti_silence_threshold_exceeded")

    # Track this tick in the sliding window for SelfImprover's measure_health.
    state["recent_tick_outcomes"].append({
        "at": tick_started.isoformat(),
        "new_tesserae": stats.get("new_tesserae", 0),
        "null_tick": stats.get("null_tick", False),
    })
    # Trim to last HEALTH_WINDOW_TICKS
    state["recent_tick_outcomes"] = state["recent_tick_outcomes"][-_SI.HEALTH_WINDOW_TICKS:]

    # Self-improvement cycle. The mixin handles its own state file, so even
    # if this tick is a dry-run we still measure (cheap) but don't apply.
    if not dry_run:
        try:
            si_result = _SI.run_self_improvement_cycle(
                tick_stats=stats,
                agent_state=state,
                shared_state_path=SI_STATE_FILE,
            )
            stats["self_improvement"] = si_result
            _emit_event("self_improvement_cycle", **si_result)
            if si_result.get("action") not in ("skipped", "observing"):
                emit_log_work(
                    "polyhymnia_self_improvement",
                    summary=f"SI: {si_result.get('action')} adaptation={si_result.get('adaptation')} "
                            f"reason={si_result.get('reason') or ''}",
                )
        except Exception as e:
            _emit_event("self_improvement_exception", level="error", error=str(e))

    if not dry_run:
        save_state(state)
    emit_heartbeat(state, tensor, last_action=stats["action"] or "unknown")
    _emit_event("tick_end", **{k: v for k, v in stats.items() if not k.startswith("_") and not isinstance(v, dict)})
    return stats


# ---------------------------------------------------------------------------
# Heartbeat + log_work
# ---------------------------------------------------------------------------

def emit_heartbeat(state: dict, tensor: PolyhymniaTensor, last_action: str) -> None:
    if not HAS_TELEMETRY:
        return
    try:
        tstats = tensor.stats()
    except Exception:
        tstats = {}
    status = {
        "anti_silence_counter": state.get("anti_silence_counter", 0),
        "total_ticks_lifetime": state.get("total_ticks_lifetime", 0),
        "total_tesserae_lifetime": state.get("total_tesserae_lifetime", 0),
        "total_lineage_lifetime": state.get("total_lineage_lifetime", 0),
        "per_scour_tesserae_contributed": state.get("per_scour_tesserae_contributed", {}),
        "tensor_stats": tstats,
        "last_action": last_action,
        "charter_version": CHARTER_VERSION,
    }
    try:
        session_telemetry.register_session(
            name=AGENT_NAME, machine=socket.gethostname(),
            role="One-tensor agent: ingest, integrate, lens, play",
            kind="tool", operator=OPERATOR, status_json=status,
        )
    except Exception as e:
        _emit_event("heartbeat_failed", level="warning", error=str(e))


def emit_log_work(stage: str, summary: str, output_path: Optional[str] = None,
                  success: bool = True, error: Optional[str] = None) -> None:
    if not HAS_TELEMETRY:
        return
    try:
        session_telemetry.log_work(
            stage=stage, agent=AGENT_NAME, summary=summary[:1000],
            output_path=output_path, success=success, error=error,
        )
    except Exception as e:
        _emit_event("log_work_failed", level="warning", stage=stage, error=str(e))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def print_status() -> None:
    state = load_state()
    tensor = PolyhymniaTensor(TENSOR_DIR)
    tstats = tensor.stats()
    print("=== Polyhymnia status ===")
    print(f"  charter_version: {state.get('charter_version')}")
    print(f"  total_ticks_lifetime:    {state.get('total_ticks_lifetime', 0)}")
    print(f"  total_tesserae_lifetime:    {state.get('total_tesserae_lifetime', 0)}")
    print(f"  total_lineage_lifetime:  {state.get('total_lineage_lifetime', 0)}")
    print(f"  anti_silence_counter:    {state.get('anti_silence_counter', 0)}")
    print()
    print(f"  Omnitensor on disk: {tstats['total_tesserae']} tesserae, "
          f"{tstats['total_lineage_edges']} lineage edges")
    print(f"  Per-axis cardinality (coord):")
    for a, n in tstats['coord_axis_cardinality'].items():
        registered = tstats['registered_coord_sizes'].get(a, 0)
        print(f"    {a:20s} populated={n:4d}  registered={registered:4d}")
    print(f"  Per-axis cardinality (tag):")
    for a, n in tstats['tag_axis_cardinality'].items():
        print(f"    {a:20s} unique_values={n}")
    if tstats['dense_capacity_if_fully_populated']:
        spar = tstats['sparsity_fraction_populated']
        print(f"  Sparsity: {spar:.2e} populated / dense-capacity")
    print()
    print(f"  Per-scour tesserae contributed:")
    for s, n in state.get('per_scour_tesserae_contributed', {}).items():
        print(f"    {s:24s} {n}")


def print_awaken() -> None:
    """Sacred ritual — print the Omnitensor's mass and motto. Cheerful
    extradimensional librarian voice (ChatGPT 2026-05-24 contribution)."""
    tensor = PolyhymniaTensor(TENSOR_DIR)
    tstats = tensor.stats()
    n = tstats['total_tesserae']
    print()
    print("            T H E   O M N I T E N S O R")
    print("                    awakens.")
    print()
    print("  Sacred rule:")
    print("    There is only one tensor.")
    print()
    print("  Current mass:")
    print(f"    {n:>7} tesserae")
    print(f"    {tstats['total_lineage_edges']:>7} lineage edges")
    print(f"    {sum(tstats['registered_coord_sizes'].values()):>7} registered axis values "
          f"across {len(tstats['registered_coord_sizes'])} coord axes")
    print(f"    {sum(tstats['tag_axis_cardinality'].values()):>7} unique tag values "
          f"across {len(tstats['tag_axis_cardinality'])} tag axes")
    print()
    print("  Hunger:")
    print("    papers, formulas, code, datasets, problems, myths,")
    print("    notations, fringe, every loosely-tensor-shaped thing.")
    print()
    print("  Polyhymnia speaks:")
    if n == 0:
        print("    I am empty. Feed me.")
    elif n < 1000:
        print("    I have begun. Bring more.")
    elif n < 10000:
        print("    I grow. Keep the scours running.")
    else:
        print("    I am hungry still. There is no limit.")
    print()


def main():
    ap = argparse.ArgumentParser(description="Polyhymnia — one-tensor agent daemon")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("status", help="print state + tensor stats")
    sub.add_parser("awaken", help="ritual: print the Omnitensor's mass + motto")
    p_scour = sub.add_parser("scour", help="run a specific scour now")
    p_scour.add_argument("scour_name")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--interval", type=int, default=DEFAULT_INTERVAL_SEC)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.cmd == "status":
        print_status()
        return 0
    if args.cmd == "awaken":
        print_awaken()
        return 0
    if args.cmd == "scour":
        if not acquire_lock():
            return 2
        try:
            stats = run_tick(dry_run=args.dry_run, only_scour=args.scour_name)
            print(json.dumps(stats, indent=2))
            return 0
        finally:
            release_lock()

    if not acquire_lock():
        return 2
    try:
        bar = "=" * 60
        banner = "\n".join([
            bar,
            f"  Polyhymnia v0.2 — keeper of the Omnitensor (operator={OPERATOR})",
            f"  Sacred rule: there is only one tensor.",
            f"  Scours registered: {len(SCOUR_REGISTRY)} "
            f"({', '.join(s.name for s in SCOUR_REGISTRY)})",
            f"  Telemetry:   {'on' if HAS_TELEMETRY else 'OFF'}",
            f"  Structlog:   {'on' if HAS_STRUCTLOG else 'OFF'}",
            f"  Mode:        {'loop @ ' + str(args.interval) + 's' if args.loop else 'once'}",
            bar,
        ])
        for line in banner.splitlines():
            _text_log.info(line)
        _emit_event("startup", telemetry=HAS_TELEMETRY, structlog=HAS_STRUCTLOG,
                    mode=("loop" if args.loop else "once"),
                    scours_registered=len(SCOUR_REGISTRY))
        emit_log_work("polyhymnia_startup",
                      summary=f"Polyhymnia daemon up; mode={'loop' if args.loop else 'once'} "
                              f"interval={args.interval}s scours={len(SCOUR_REGISTRY)}")
        if args.once or not args.loop:
            stats = run_tick(dry_run=args.dry_run)
            _text_log.info(f"tick: action={stats['action']} new={stats['new_tesserae']} "
                           f"merged={stats['merged_tesserae']} edges={stats['lineage_edges_added']}")
            return 0
        while True:
            try:
                stats = run_tick(dry_run=args.dry_run)
                _text_log.info(f"tick: action={stats['action']} new={stats['new_tesserae']} "
                               f"merged={stats['merged_tesserae']} edges={stats['lineage_edges_added']}")
            except Exception:
                _emit_event("tick_uncaught_exception", level="error")
                _text_log.exception("uncaught exception in tick")
            time.sleep(max(1, args.interval))
    finally:
        emit_log_work("polyhymnia_shutdown", summary="Polyhymnia daemon shutting down")
        _emit_event("shutdown")
        release_lock()


if __name__ == "__main__":
    sys.exit(main() or 0)
