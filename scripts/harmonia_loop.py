"""
harmonia_loop.py — rotation orchestrator for the Harmonia agent swarm.

Cycles through Phylax / Sophia / Iris / Argos / Telos one tick per
invocation. Designed to be fired by Claude Code's `/loop` feature:

    /loop 4m python scripts/harmonia_loop.py

State (which agent goes next) lives at
`harmonia/agents/_rotation_state.json` so the rotation survives process
restarts. Round-robin by default; --agent <name> forces a single agent.

Heartbeat / log_work via session_telemetry. No /dev/null swallow on
failure — exceptions are logged with full stack and the rotation
advances anyway (a sticky agent should not freeze the swarm).
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent
for p in (str(_REPO_ROOT), str(_SCRIPT_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

os.environ.setdefault("AGORA_REDIS_HOST", "192.168.1.176")
os.environ.setdefault("AGORA_REDIS_PASSWORD", "prometheus")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from harmonia.agents import AGENT_NAMES
from harmonia.agents._base import get_agent

try:
    import session_telemetry  # type: ignore
    HAS_TELEMETRY = True
except Exception:
    session_telemetry = None  # type: ignore
    HAS_TELEMETRY = False

PID_FILE = _REPO_ROOT / "harmonia" / "agents" / "_swarm.pid"


def _pid_alive(pid: int) -> bool:
    """Cross-platform liveness check. Returns False on any uncertainty."""
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        h = ctypes.windll.kernel32.OpenProcess(
            PROCESS_QUERY_LIMITED_INFORMATION, False, pid
        )
        if not h:
            return False
        exit_code = ctypes.c_ulong()
        ok = ctypes.windll.kernel32.GetExitCodeProcess(
            h, ctypes.byref(exit_code)
        )
        ctypes.windll.kernel32.CloseHandle(h)
        return bool(ok) and exit_code.value == 259  # STILL_ACTIVE
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _acquire_single_instance_lock(loop_mode: bool) -> None:
    """Refuse to start a second --loop daemon. Single-tick invocations
    (no --loop, no --status) bypass the lock so /loop and one-off
    debugging stay friction-free."""
    if not loop_mode:
        return
    if PID_FILE.exists():
        try:
            old_pid = int(PID_FILE.read_text(encoding="utf-8").strip())
        except Exception:
            old_pid = -1
        if old_pid > 0 and _pid_alive(old_pid):
            print(
                f"[HARMONIA_LOOP] another --loop daemon already running "
                f"(pid={old_pid}, lock={PID_FILE}). Refusing to start.",
                file=sys.stderr,
            )
            sys.exit(2)
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(os.getpid()), encoding="utf-8")


def _release_single_instance_lock() -> None:
    try:
        if PID_FILE.exists() and PID_FILE.read_text(encoding="utf-8").strip() == str(os.getpid()):
            PID_FILE.unlink()
    except Exception:
        pass


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [HARMONIA_LOOP] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("harmonia_loop")

STATE_PATH = _REPO_ROOT / "harmonia" / "agents" / "_rotation_state.json"
JSONL_LOG = _REPO_ROOT / "harmonia" / "agents" / "_logs" / "ticks.jsonl"
# D:\Prometheus\harmonia\agents\_rotation_weights.json — per-agent stride
# config. stride=N means "this agent ticks once every N rotation cycles".
# Missing-from-config defaults to 1 (tick every cycle). Missing file =
# everyone strides at 1 (round-robin baseline preserved).
WEIGHTS_PATH = _REPO_ROOT / "harmonia" / "agents" / "_rotation_weights.json"
# Sentinel large initial value for ticks_since_last_pick so the first
# rotation walk always honors stride (any agent is "due").
_TICKS_INIT_HIGH = 100
_UNKNOWN_WEIGHTS_WARNED: set[str] = set()


def _load_rotation_weights() -> dict[str, int]:
    """Load per-agent stride config. Returns {agent: stride_int}.

    Gracefully defaults missing/corrupt file to all-1 (today's
    round-robin behavior). Unknown agents in the file are dropped with
    a one-shot warning.
    """
    weights: dict[str, int] = {a: 1 for a in AGENT_NAMES}
    if not WEIGHTS_PATH.exists():
        return weights
    try:
        raw = json.loads(WEIGHTS_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        log.warning(
            f"rotation weights load failed ({WEIGHTS_PATH}): {e} -- "
            f"falling back to all-stride-1"
        )
        return weights
    if not isinstance(raw, dict):
        log.warning(
            f"rotation weights file is not a dict ({WEIGHTS_PATH}) -- "
            f"falling back to all-stride-1"
        )
        return weights
    for k, v in raw.items():
        agent = str(k).lower()
        if agent not in AGENT_NAMES:
            if agent not in _UNKNOWN_WEIGHTS_WARNED:
                log.warning(f"unknown agent '{agent}' in rotation weights -- ignored")
                _UNKNOWN_WEIGHTS_WARNED.add(agent)
            continue
        try:
            stride = int(v)
        except (TypeError, ValueError):
            log.warning(f"non-integer stride for '{agent}' ({v!r}) -- using 1")
            stride = 1
        if stride < 1:
            stride = 1
        weights[agent] = stride
    return weights


def _append_jsonl_tick(record: dict) -> None:
    """Append a tick record to the lifetime JSONL log.

    The rotation_state.json history is capped at 200 entries (rolling
    window). This append-only JSONL preserves every tick for lifetime
    metrics (pool-exhaust counts, per-agent yield histograms, etc).
    """
    try:
        JSONL_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(JSONL_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")
    except Exception as e:
        log.warning(f"jsonl tick log append failed: {e}")


def _load_rotation_state() -> dict:
    if not STATE_PATH.exists():
        return {"next_index": 0, "history": []}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"next_index": 0, "history": []}


def _save_rotation_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        STATE_PATH.write_text(json.dumps(state, indent=2, default=str),
                              encoding="utf-8")
    except Exception as e:
        log.warning(f"could not persist rotation state: {e}")


def _pick_next_agent(force: str | None) -> tuple[str, dict]:
    state = _load_rotation_state()
    if force:
        name = force.lower()
        if name not in AGENT_NAMES:
            raise SystemExit(f"unknown agent '{force}' "
                             f"(valid: {AGENT_NAMES})")
        # Forced pick bypasses stride logic entirely; do not mutate the
        # ticks_since_last_pick counters so the natural rotation cadence
        # resumes cleanly on the next non-forced call.
        return name, state

    weights = _load_rotation_weights()

    # Per-agent "ticks since this agent was last picked" counter. First
    # run initializes every agent high so the first rotation walk works
    # normally regardless of stride.
    raw_ticks = state.get("ticks_since_last_pick")
    if not isinstance(raw_ticks, dict):
        raw_ticks = {}
    ticks: dict[str, int] = {}
    for a in AGENT_NAMES:
        try:
            ticks[a] = int(raw_ticks.get(a, _TICKS_INIT_HIGH))
        except (TypeError, ValueError):
            ticks[a] = _TICKS_INIT_HIGH

    # Every agent's wait counter advances by 1 each call.
    for a in AGENT_NAMES:
        ticks[a] += 1

    # Walk round-robin starting at next_index; pick the first candidate
    # whose stride has elapsed. Cap at 2 * len(AGENT_NAMES) iterations
    # to guarantee termination if config is broken.
    start_idx = int(state.get("next_index", 0)) % len(AGENT_NAMES)
    n = len(AGENT_NAMES)
    cap = 2 * n
    chosen_name: str | None = None
    chosen_idx: int = start_idx
    for step in range(cap):
        candidate_idx = (start_idx + step) % n
        candidate = AGENT_NAMES[candidate_idx]
        stride = weights.get(candidate, 1)
        if ticks[candidate] >= stride:
            chosen_name = candidate
            chosen_idx = candidate_idx
            break

    if chosen_name is None:
        # All strides too large vs counters; fall back to start_idx pick
        # so the swarm never freezes. Should be unreachable when at least
        # one stride <= _TICKS_INIT_HIGH, but guard anyway.
        chosen_name = AGENT_NAMES[start_idx]
        chosen_idx = start_idx
        log.warning(
            "rotation walk found no due agent within cap; falling back "
            f"to next_index={start_idx} ({chosen_name})"
        )

    # Picked agent's counter resets; advance next_index past it.
    ticks[chosen_name] = 0
    state["ticks_since_last_pick"] = ticks
    state["next_index"] = (chosen_idx + 1) % n
    return chosen_name, state


def _emit_loop_heartbeat(last_run: dict) -> None:
    if not HAS_TELEMETRY:
        return
    try:
        session_telemetry.register_session(
            name="Harmonia_Loop",
            machine="M2",
            role="rotation orchestrator (Phylax/Sophia/Iris/Argos/Telos)",
            kind="tool",
            operator="Harmonia",
            status_json={
                "last_run": last_run,
                "as_of": datetime.now(timezone.utc).isoformat(),
                "agents": AGENT_NAMES,
            },
        )
    except Exception as e:
        log.warning(f"loop heartbeat failed: {e}")


def run_once(force_agent: str | None = None, dry_run: bool = False) -> dict:
    name, state = _pick_next_agent(force_agent)
    log.info(f"dispatching agent: {name} (forced={bool(force_agent)})")
    started = datetime.now(timezone.utc).isoformat()
    t0 = time.time()
    stats: dict = {}
    err: str | None = None
    try:
        agent = get_agent(name)
        stats = agent.tick(dry_run=dry_run)
    except Exception as e:
        log.exception(f"agent {name} crashed: {e}")
        err = str(e)[:300]
        stats = {"errors": 1, "exception": err}
    elapsed = time.time() - t0
    record = {
        "agent": name,
        "started_at": started,
        "elapsed_sec": round(elapsed, 2),
        "stats": stats,
        "error": err,
        "dry_run": dry_run,
    }
    state.setdefault("history", []).append(record)
    state["history"] = state["history"][-200:]  # cap
    if not force_agent:
        _save_rotation_state(state)
    _append_jsonl_tick(record)
    _emit_loop_heartbeat(record)
    log.info(f"agent {name} done in {elapsed:.1f}s: {stats}")
    return record


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Harmonia agent-swarm rotation orchestrator"
    )
    ap.add_argument("--agent", default=None,
                    help="force a specific agent (phylax/sophia/iris/argos/telos)")
    ap.add_argument("--dry-run", action="store_true",
                    help="run agent in dry-run mode (no artifact writes)")
    ap.add_argument("--loop", action="store_true",
                    help="self-loop with --interval delay (otherwise single tick)")
    ap.add_argument("--interval", type=int, default=240,
                    help="loop interval seconds when --loop (default 240 = 4m)")
    ap.add_argument("--status", action="store_true",
                    help="print rotation state and exit")
    args = ap.parse_args()

    if args.status:
        state = _load_rotation_state()
        print(json.dumps(state, indent=2, default=str))
        return 0

    _acquire_single_instance_lock(loop_mode=args.loop)

    if args.loop:
        log.info(f"self-loop mode, interval={args.interval}s pid={os.getpid()} "
                 f"(use Claude Code /loop for the recommended path)")
        try:
            while True:
                try:
                    run_once(force_agent=args.agent, dry_run=args.dry_run)
                except KeyboardInterrupt:
                    log.info("interrupted")
                    return 0
                except Exception as e:
                    log.exception(f"tick failed: {e}")
                time.sleep(args.interval)
        finally:
            _release_single_instance_lock()

    record = run_once(force_agent=args.agent, dry_run=args.dry_run)
    print(json.dumps(record, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
