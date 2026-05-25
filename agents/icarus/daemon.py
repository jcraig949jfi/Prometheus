"""
Icarus daemon -- the main 5-step loop.

Per spec v0.2 sect 2. Each iteration:
  Step 0: clone last-stable cycle into cycles/cycle_<N>/
  Step 1: self-code-eval (Improve() with 3 backends)
  Step 2: external ingestion (DR + OSS + Forge) -- Phase 0 stubs
  Step 3: enriched structured logging
  Step 4: TDD red->green->refactor
  Step 5: frontier review emit + inbox scan
  Step 6 (implicit): freeze + stability decision

FIXED infrastructure -- Icarus does NOT modify this module.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ICARUS_DIR = Path(r"D:\Prometheus\agents\icarus")
STATE_DIR = ICARUS_DIR / "state"
PID_FILE = STATE_DIR / "_icarus.pid"
PAUSE_FLAG = STATE_DIR / "pause.flag"
RESUME_FLAG = STATE_DIR / "resume.flag"
KILL_FLAG = STATE_DIR / "kill.flag"

_REPO_ROOT = Path(r"D:\Prometheus")
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(ICARUS_DIR) not in sys.path:
    sys.path.insert(0, str(ICARUS_DIR))

os.environ.setdefault("PYTHONIOENCODING", "utf-8")

# Soft imports
try:
    from harmonia.agents._scorer import emit_event
    HAS_EMIT = True
except Exception:
    HAS_EMIT = False
    def emit_event(*args, **kwargs):  # type: ignore
        return False

from lineage import (
    cycle_path, current_iteration, increment_iteration,
    last_stable_cycle_id, last_stable_cycle_n,
    clone_from_stable, freeze_cycle, mark_stable, record_outcome,
)
import improve as improve_mod


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [ICARUS] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("icarus")


# ---------------------------------------------------------------------------
# Single-instance lock + control flags
# ---------------------------------------------------------------------------

def _pid_alive(pid: int) -> bool:
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


def _acquire_lock() -> None:
    if PID_FILE.exists():
        try:
            old_pid = int(PID_FILE.read_text(encoding="utf-8").strip())
        except Exception:
            old_pid = -1
        if old_pid > 0 and _pid_alive(old_pid):
            print(f"[icarus] another daemon already running (pid={old_pid})",
                  file=sys.stderr)
            sys.exit(2)
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(os.getpid()), encoding="utf-8")


def _release_lock() -> None:
    try:
        if PID_FILE.exists() and PID_FILE.read_text(encoding="utf-8").strip() == str(os.getpid()):
            PID_FILE.unlink()
    except Exception:
        pass


def _check_kill() -> bool:
    return KILL_FLAG.exists()


def _check_pause() -> bool:
    if not PAUSE_FLAG.exists():
        return False
    log.info("pause.flag present; waiting for resume.flag")
    while not RESUME_FLAG.exists() and not KILL_FLAG.exists():
        time.sleep(5)
    if KILL_FLAG.exists():
        return True  # treat kill as exit
    try:
        RESUME_FLAG.unlink()
        PAUSE_FLAG.unlink()
    except Exception:
        pass
    log.info("resumed")
    return False


# ---------------------------------------------------------------------------
# Per-cycle log helpers
# ---------------------------------------------------------------------------

def _append_cycle_log(cycle_n: int, phase: str, details: dict) -> None:
    path = cycle_path(cycle_n) / "log.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "cycle_id": f"icarus-cycle-{cycle_n:03d}",
        "iteration_n": cycle_n,
        "phase": phase,
        "ts": datetime.now(timezone.utc).isoformat(),
        "details": details,
    }
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, default=str) + "\n")
    except Exception as e:
        log.warning(f"cycle log append failed: {e}")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


# ---------------------------------------------------------------------------
# The 5-step cycle
# ---------------------------------------------------------------------------

def run_cycle(
    force_park: bool = False,
    force_stable: bool = False,
) -> dict:
    """Execute one Icarus cycle. Returns the cycle's outcome dict."""
    tick_id = f"icarus-tick-{uuid.uuid4().hex[:12]}"
    started_at = datetime.now(timezone.utc)

    emit_event(
        "tick_start",
        {"agent": "Icarus", "dry_run": False},
        agent="Icarus",
        tick_id=tick_id,
    )

    # Step 0: clone last-stable into new cycle dir
    n = increment_iteration()
    log.info(f"=== cycle {n} starting (cloned from stable {last_stable_cycle_id()}) ===")
    try:
        new_cycle_dir = clone_from_stable(n)
    except Exception as e:
        log.exception(f"clone_from_stable failed: {e}")
        record_outcome(n, decision="park", reason=f"clone_failed: {e}")
        return _emit_complete(tick_id, started_at, n, "park", {})

    tier_target = _read_json(STATE_DIR / "tier_target.json", {"tier": "R1"}).get("tier", "R1")
    failure_context = _build_failure_context()

    _append_cycle_log(n, "step_0_clone", {
        "parent_cycle": last_stable_cycle_id(),
        "tier_target": tier_target,
    })

    # Step 1: self-code-eval
    if force_park:
        improve_result = {"backend_used": "force_park", "diff": None, "rationale": "force_park flag set"}
    elif force_stable:
        improve_result = {"backend_used": "force_stable", "diff": "", "rationale": "force_stable flag set"}
    else:
        try:
            improve_result = improve_mod.propose_diff(
                cycle_n=n,
                source_dir=new_cycle_dir / "code",
                tier_challenge={
                    "tier": tier_target,
                    "falsification_test": _ladder_falsification_test(tier_target),
                },
                failure_context=failure_context,
                wisdom=_load_wisdom(),
                backend="auto",
            )
        except Exception as e:
            log.exception(f"improve.propose_diff failed: {e}")
            improve_result = {"backend_used": "error", "diff": None,
                              "rationale": f"propose_diff_failed: {e}"}

    _append_cycle_log(n, "step_1_improve", {
        "backend_used": improve_result.get("backend_used"),
        "diff_lines": len((improve_result.get("diff") or "").splitlines()),
        "rationale_excerpt": (improve_result.get("rationale") or "")[:300],
        "tokens_used": improve_result.get("tokens_used"),
        "cost_usd": improve_result.get("cost_estimate_usd"),
    })

    # Write the diff artifact
    diff_text = improve_result.get("diff") or ""
    rationale_text = improve_result.get("rationale") or ""
    if diff_text or improve_result.get("backend_used") == "chimera_pending":
        (new_cycle_dir / "diff.patch").write_text(diff_text, encoding="utf-8")
        (new_cycle_dir / "diff_rationale.md").write_text(
            f"# Cycle {n} Improve() rationale\n\n"
            f"**Backend:** {improve_result.get('backend_used')}\n"
            f"**Model:** {improve_result.get('model_used', 'n/a')}\n\n"
            f"{rationale_text}\n",
            encoding="utf-8",
        )

    # Step 2: external ingestion (Phase 0 stubs)
    _append_cycle_log(n, "step_2_external_ingestion", {
        "dr_enqueued": 0,
        "oss_pulled": 0,
        "forge_imported": 0,
        "note": "phase_0_stub_no_external_ingestion",
    })

    # Step 3: enriched logging (already happening per-phase; this is a checkpoint)
    _append_cycle_log(n, "step_3_log_checkpoint", {
        "phases_so_far": ["step_0_clone", "step_1_improve", "step_2_external_ingestion"],
    })

    # Step 4: TDD (stubbed Phase 0)
    tdd_result = _run_tdd_stub(n, new_cycle_dir, tier_target)
    _append_cycle_log(n, "step_4_tdd", tdd_result)

    # Step 5: frontier review emit + inbox scan (stubbed Phase 0)
    _append_cycle_log(n, "step_5_frontier", {
        "outbox_written": False,
        "inbox_consumed": 0,
        "note": "phase_0_stub",
    })

    # Step 6: freeze + stability decision
    decision, reason = _decide_outcome(
        improve_result, tdd_result, force_park=force_park, force_stable=force_stable,
    )
    record_outcome(n, decision=decision, reason=reason, details={
        "improve_backend": improve_result.get("backend_used"),
        "tdd_all_passed": tdd_result.get("all_passed"),
    })

    # Freeze the cycle directory
    freeze_cycle(n)

    # Advance pointer if stable
    if decision == "mark_stable":
        mark_stable(n)
        log.info(f"cycle {n} MARK_STABLE (pointer advanced)")
    elif decision == "park":
        log.info(f"cycle {n} PARK (pointer unchanged at {last_stable_cycle_id()}): {reason}")

    return _emit_complete(tick_id, started_at, n, decision, {
        "improve_backend": improve_result.get("backend_used"),
        "tdd_all_passed": tdd_result.get("all_passed"),
        "reason": reason,
    })


def _emit_complete(tick_id, started_at, n, decision, stats) -> dict:
    elapsed = (datetime.now(timezone.utc) - started_at).total_seconds()
    emit_event(
        "tick_complete",
        {
            "agent": "Icarus",
            "cycle_n": n,
            "decision": decision,
            "elapsed_sec": round(elapsed, 2),
            **stats,
        },
        agent="Icarus",
        tick_id=tick_id,
    )
    return {
        "cycle_n": n,
        "decision": decision,
        "elapsed_sec": elapsed,
        **stats,
    }


def _decide_outcome(improve_result, tdd_result, force_park, force_stable):
    if force_park:
        return "park", "force_park_flag"
    if force_stable:
        return "mark_stable", "force_stable_flag"
    backend = improve_result.get("backend_used")
    if backend in ("chimera_pending", "no_op", "error"):
        return "park", f"improve_no_diff_backend={backend}"
    if not improve_result.get("diff"):
        return "park", "empty_diff"
    if not tdd_result.get("all_passed"):
        return "park", "tdd_failed"
    return "mark_stable", "tdd_passed"


def _ladder_falsification_test(tier: str) -> str:
    """Look up the falsification-test description from ladder.py without
    crashing if ladder isn't importable yet."""
    try:
        sys.path.insert(0, str(ICARUS_DIR))
        from ladder import get_tier
        return get_tier(tier).falsification_test
    except Exception:
        return "(ladder.py not importable; using placeholder)"


def _build_failure_context() -> dict:
    """Read the last 5 cycles' outcomes for the next Improve() call."""
    from lineage import list_parked_cycles
    parked = list_parked_cycles(limit=5)
    return {
        "recent_parks": [{"cycle": p["cycle_n"], "reason": p["outcome"].get("reason")} for p in parked],
        "last_stable": last_stable_cycle_id(),
    }


def _load_wisdom() -> str:
    """Load wisdom/wisdom.md if present."""
    wisdom_path = ICARUS_DIR / "wisdom" / "wisdom.md"
    if wisdom_path.exists():
        try:
            return wisdom_path.read_text(encoding="utf-8")
        except Exception:
            return ""
    return ""


def _run_tdd_stub(n: int, cycle_dir: Path, tier_target: str) -> dict:
    """Phase 0 TDD stub. Returns all_passed=True if there's no actual code
    to test (Phase 0 reasoner is empty)."""
    code_dir = cycle_dir / "code"
    tests_dir = code_dir / "tests"
    if not tests_dir.exists() or not any(tests_dir.glob("test_*.py")):
        return {
            "all_passed": True,
            "per_source": {"tier_falsification": {"passed": 0, "failed": 0, "skipped": 0}},
            "note": "no_tests_in_cycle_dir_phase_0",
        }
    # In Phase 1 we'll wire pytest here. For now, just check the test files
    # have valid Python syntax.
    import ast
    failed = 0
    passed = 0
    for tp in tests_dir.glob("test_*.py"):
        try:
            ast.parse(tp.read_text(encoding="utf-8"))
            passed += 1
        except Exception:
            failed += 1
    return {
        "all_passed": failed == 0,
        "per_source": {
            "tier_falsification": {"passed": passed, "failed": failed, "skipped": 0},
        },
        "note": "phase_0_syntax_check_only",
    }


# ---------------------------------------------------------------------------
# Status + CLI
# ---------------------------------------------------------------------------

def cmd_status():
    n = current_iteration()
    stable = last_stable_cycle_id()
    tier_target = _read_json(STATE_DIR / "tier_target.json", {}).get("tier", "?")
    tier_passing = _read_json(STATE_DIR / "tier_currently_passing.json", {}).get("tier", "?")
    print(f"Icarus status:")
    print(f"  current iteration:        {n}")
    print(f"  last_stable_cycle:        {stable}")
    print(f"  tier_target:              {tier_target}")
    print(f"  tier_currently_passing:   {tier_passing}")
    print(f"  paused:                   {PAUSE_FLAG.exists()}")
    print(f"  kill flag:                {KILL_FLAG.exists()}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Icarus self-improving agent daemon")
    ap.add_argument("--once", action="store_true", help="single cycle then exit")
    ap.add_argument("--loop", action="store_true", help="continuous loop")
    ap.add_argument("--interval", type=int, default=90, help="seconds between cycles in --loop mode")
    ap.add_argument("--status", action="store_true", help="print status and exit")
    ap.add_argument("--force-park", action="store_true", help="force park decision (testing)")
    ap.add_argument("--force-stable", action="store_true", help="force stable decision (testing)")
    args = ap.parse_args()

    if args.status:
        cmd_status()
        return 0

    if args.loop:
        _acquire_lock()
        try:
            log.info(f"loop mode interval={args.interval}s pid={os.getpid()}")
            while not _check_kill():
                if _check_pause():
                    break  # kill arrived during pause
                try:
                    run_cycle(force_park=args.force_park, force_stable=args.force_stable)
                except KeyboardInterrupt:
                    log.info("interrupted")
                    return 0
                except Exception as e:
                    log.exception(f"cycle failed: {e}")
                time.sleep(args.interval)
        finally:
            _release_lock()
        return 0

    if args.once:
        result = run_cycle(force_park=args.force_park, force_stable=args.force_stable)
        print(json.dumps(result, indent=2, default=str))
        return 0

    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
