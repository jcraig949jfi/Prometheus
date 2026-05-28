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
import patcher
import tdd_runner
import taxonomy
import debt_ledger
import ablation
from lenses._base import CycleContext
from lenses._panel import run_lens_panel


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
    """Execute one Icarus cycle via the lens panel (Phase 2 architecture).
    Returns the cycle's outcome dict."""
    tick_id = f"icarus-tick-{uuid.uuid4().hex[:12]}"
    started_at = datetime.now(timezone.utc)

    emit_event(
        "tick_start",
        {"agent": "Icarus", "dry_run": False},
        agent="Icarus", tick_id=tick_id,
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

    _append_cycle_log(n, "step_0_clone", {
        "parent_cycle": last_stable_cycle_id(),
        "tier_target": tier_target,
    })

    # Test-only fast paths
    if force_park or force_stable:
        decision = "park" if force_park else "mark_stable"
        reason = "force_park_flag" if force_park else "force_stable_flag"
        record_outcome(n, decision=decision, reason=reason,
                       details={"forced": True})
        freeze_cycle(n)
        if decision == "mark_stable":
            mark_stable(n)
        return _emit_complete(tick_id, started_at, n, decision,
                               {"reason": reason, "forced": True})

    # Build CycleContext
    failure_context = _build_failure_context()
    cycle_strategy = ("minimal", "structural", "exploratory")[n % 3]
    open_debts = debt_ledger.open_debts()
    ctx = CycleContext(
        cycle_n=n,
        source_dir=new_cycle_dir / "code",
        tier_target=tier_target,
        tier_challenge={
            "tier": tier_target,
            "falsification_test": _ladder_falsification_test(tier_target),
        },
        last_stable_id=last_stable_cycle_id(),
        recent_parks=failure_context.get("recent_parks", []),
        wisdom=_load_wisdom(),
        cycle_strategy=cycle_strategy,
        open_debts=open_debts,
    )
    log.info(f"  strategy={cycle_strategy} tier_target={tier_target} "
             f"open_debts={len(open_debts)}")

    # Run the lens panel (phase A through F)
    try:
        panel_result = run_lens_panel(
            ctx=ctx,
            cycle_dir=new_cycle_dir,
            apply_fn=patcher.apply_diff,
            tdd_fn=tdd_runner.run_all_tests,
            emit_event_fn=emit_event,
        )
    except Exception as e:
        log.exception(f"lens panel raised: {e}")
        # Even a panel crash must leave residue -- failure is the primary
        # product. Emit a minimal training object before exiting.
        try:
            crash_obj = taxonomy.build_training_object(
                cycle_n=n, tier_target=tier_target, strategy=cycle_strategy,
                decision="park",
                apply_result=ctx.apply_result or {},
                tdd_result=ctx.tdd_result or {},
                skeptic_report=None,
                contract_report=ctx.contract_report or {},
                integrator_report={},
                load_bearing_lens="panel_crash",
            )
            crash_obj.failure_class = "panel_error"
            crash_obj.failure_subclass = "unparseable_lens_output"
            crash_obj.improvement_rationale = f"panel_crashed: {e}"
            taxonomy.write_training_object(crash_obj, new_cycle_dir)
        except Exception as e2:
            log.warning(f"crash training-object emit failed: {e2}")
        record_outcome(n, decision="park", reason=f"panel_crashed: {e}",
                       details={"failure_class": "panel_error"})
        freeze_cycle(n)
        return _emit_complete(tick_id, started_at, n, "park",
                               {"reason": f"panel_crashed: {e}"})

    # Persist the proposed diff artifact (Generator's output)
    if ctx.proposed_diff:
        (new_cycle_dir / "diff.patch").write_text(ctx.proposed_diff, encoding="utf-8")

    # Log a checkpoint for each panel phase
    _append_cycle_log(n, "panel_complete", {
        "decision": panel_result["decision"],
        "load_bearing_lens": panel_result["load_bearing_lens"],
        "agreement_patterns": panel_result["agreement_patterns"],
        "axes_summary": panel_result["axes_summary"],
    })

    # Record multi-axis outcome
    decision = panel_result["decision"]
    rationale = panel_result["rationale"]
    load_bearing = panel_result["load_bearing_lens"]
    apply_result = panel_result.get("apply_result") or {}
    tdd_result = panel_result.get("tdd_result") or {}
    contract_report = ctx.contract_report or {}
    skeptic_dict = ctx.skeptic_report.to_dict() if ctx.skeptic_report else None
    integ_extra = ctx.integrator_report.extra if ctx.integrator_report else {}

    # Q12 ablation: oracle-verified capability check (candidate vs parent on
    # the blind holdout). This OVERRIDES the LLM Integrator's self-reported
    # improvement_kind with a non-gameable verdict.
    ablation_result = None
    if apply_result.get("applied"):
        try:
            ablation_result = ablation.check_decorative(
                candidate_dir=new_cycle_dir / "code",
                parent_dir=cycle_path(last_stable_cycle_n()) / "code",
                tier_target=tier_target,
            )
            _append_cycle_log(n, "ablation", ablation_result)
        except Exception as e:
            log.warning(f"ablation failed: {e}")

    # Build the typed training object (the reusable artifact every cycle emits)
    training_obj = taxonomy.build_training_object(
        cycle_n=n,
        tier_target=tier_target,
        strategy=cycle_strategy,
        decision=decision,
        apply_result=apply_result,
        tdd_result=tdd_result,
        skeptic_report=skeptic_dict,
        contract_report=contract_report,
        integrator_report=integ_extra,
        load_bearing_lens=load_bearing,
    )
    # Override improvement_kind with the oracle-verified ablation verdict
    if ablation_result is not None:
        training_obj.improvement_kind = ablation_result["improvement_kind"]
        training_obj.improvement_rationale = ablation_result["detail"]
    taxonomy.write_training_object(training_obj, new_cycle_dir)

    # Debt accounting: record new debts when promoting despite a concern;
    # attempt to close debts when tests were added.
    tests_before = _stable_tests_run()
    tests_after = training_obj.tests_run
    if decision == "mark_stable":
        # contract violation that survived into promotion -> debt
        if contract_report.get("contract_violation"):
            debt_ledger.record_debt(
                cycle=n,
                concern=(contract_report.get("violations") or [{}])[0].get("detail", "contract violation"),
                regression_test_to_write=training_obj.regression_test_to_write,
                source="contract",
                future_tier_risk=training_obj.future_tier_risk,
            )
        # skeptic minority that survived into promotion -> debt
        elif skeptic_dict and skeptic_dict.get("minority_position"):
            debt_ledger.record_debt(
                cycle=n,
                concern=skeptic_dict.get("minority_position"),
                regression_test_to_write=training_obj.regression_test_to_write,
                source="skeptic",
                future_tier_risk=training_obj.future_tier_risk,
            )
    closed = debt_ledger.attempt_auto_close(
        cycle=n, tests_run_before=tests_before, tests_run_after=tests_after,
    )

    record_outcome(n, decision=decision, reason=rationale[:300], details={
        "schema_version": "v3_typed_residue",
        "load_bearing_lens": load_bearing,
        "axes_summary": panel_result["axes_summary"],
        "agreement_patterns": panel_result["agreement_patterns"],
        "diff_applied": apply_result.get("applied"),
        "files_changed": apply_result.get("files_changed", []),
        "tdd_all_passed": tdd_result.get("all_passed"),
        "contract_violation": contract_report.get("contract_violation", False),
        "failure_class": training_obj.failure_class,
        "improvement_kind": training_obj.improvement_kind,
        "debts_closed": closed,
        "open_debts_after": len(debt_ledger.open_debts()),
    })

    freeze_cycle(n)
    if decision == "mark_stable":
        mark_stable(n)
        log.info(f"cycle {n} MARK_STABLE [lb={load_bearing}] "
                 f"class={training_obj.failure_class} kind={training_obj.improvement_kind} "
                 f"contract_viol={contract_report.get('contract_violation', False)} "
                 f"debts_closed={len(closed)}")
    else:
        log.info(f"cycle {n} PARK [lb={load_bearing}] "
                 f"class={training_obj.failure_class} (stable still {last_stable_cycle_id()})")

    return _emit_complete(tick_id, started_at, n, decision, {
        "load_bearing_lens": load_bearing,
        "failure_class": training_obj.failure_class,
        "improvement_kind": training_obj.improvement_kind,
        "contract_violation": contract_report.get("contract_violation", False),
    })


def _stable_tests_run() -> int:
    """Read the last-stable cycle's training object to get its tests_run,
    for debt auto-close delta. Defaults to 0 if unavailable."""
    try:
        stable_dir = cycle_path(last_stable_cycle_n())
        to = stable_dir / "training_object.json"
        if to.exists():
            return int(json.loads(to.read_text(encoding="utf-8")).get("tests_run", 0))
    except Exception:
        pass
    return 0


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


# _decide_outcome removed -- replaced by lens panel Integrator's load-bearing
# citation (per James's lenses-over-mono-solutions principle).


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
