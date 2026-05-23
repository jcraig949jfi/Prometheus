"""Pheme — substrate demand voicer daemon.

See agents/pheme/CHARTER.md for the full contract. Summary:
  - Scans Ergon eval output for new runs
  - Aggregates per-pattern failure rates into a demand profile
  - Writes agents/pheme/artifacts/demand_<ts>.json + atomic demand_latest.json
  - Fires log_work(stage='ergon_substrate_demand', ...) every profile
  - Anti-silence sentinel every tick: NULL_TICK | UPSTREAM_NOT_FOUND | EVAL_DROUGHT
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import socket
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
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

# Local paths
STATE_DIR = AGENT_DIR / "state"
ARTIFACT_DIR = AGENT_DIR / "artifacts"
LOG_DIR = AGENT_DIR / "logs"
PID_FILE = AGENT_DIR / "pheme.pid"
STATE_FILE = STATE_DIR / "state.json"
TEXT_LOG = LOG_DIR / "pheme.log"
DEMAND_LATEST = ARTIFACT_DIR / "demand_latest.json"

# External roots
EVAL_ROOTS = [
    REPO_ROOT / "ergon" / "learner" / "evals",
    REPO_ROOT / "ergon" / "evals",
    REPO_ROOT / "ergon" / "diagnostic_c" / "eval_runs",
]

# Defaults
DEFAULT_INTERVAL_SEC = 1800
ANTI_SILENCE_ALARM_THRESHOLD = 50
EVAL_DROUGHT_DAYS = 7
TOP_K_DEMAND_PATTERNS = 10
DEFAULT_SUBSTRATE_QUOTA = {"A": 0.35, "D": 0.25, "B": 0.15, "C": 0.15, "E": 0.10}
CHARTER_VERSION = "v1"
AGENT_NAME = "Pheme"
OPERATOR = "Ergon"


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def _setup_text_logger() -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log = logging.getLogger("pheme")
    if log.handlers:
        return log
    log.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s [PHEME] %(message)s")
    sh = logging.StreamHandler(sys.stdout); sh.setFormatter(fmt); log.addHandler(sh)
    fh = logging.FileHandler(TEXT_LOG, encoding="utf-8"); fh.setFormatter(fmt); log.addHandler(fh)
    return log


_text_log = _setup_text_logger()
_evt_log = get_structured_logger("pheme", log_dir=AGENT_DIR) if HAS_STRUCTLOG else None


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
# Single-instance lock
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
                _text_log.error(f"another pheme instance is alive (pid={existing_pid}); aborting")
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
        "last_scanned_eval_id": None,
        "last_profile_at": None,
        "anti_silence_counter": 0,
        "total_profiles_lifetime": 0,
        "total_null_ticks_lifetime": 0,
        "prior_top_patterns": [],  # for trend computation
    }


def load_state() -> dict:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if not STATE_FILE.exists():
        return _default_state()
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        _emit_event("state_load_failed_using_default", level="warning", error=str(e))
        return _default_state()


def save_state(state: dict) -> None:
    state["last_save_at"] = datetime.now(timezone.utc).isoformat()
    tmp = STATE_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, indent=2), encoding="utf-8")
    tmp.replace(STATE_FILE)


# ---------------------------------------------------------------------------
# Eval ingestion + aggregation
# ---------------------------------------------------------------------------

def find_active_eval_root() -> Optional[Path]:
    for root in EVAL_ROOTS:
        if root.exists() and root.is_dir():
            return root
    return None


def scan_new_eval_runs(root: Path, since_id: Optional[str]) -> list[dict]:
    """Walk eval root for runs newer than since_id."""
    if not root or not root.exists():
        return []
    runs = []
    # Support both per-run JSON file and per-run directory with JSONL inside
    for p in sorted(root.rglob("*.json*")):
        if p.suffix not in (".json", ".jsonl"):
            continue
        try:
            if p.suffix == ".jsonl":
                records = []
                for line in p.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
                # Synthesize a run wrapper around the JSONL
                run_id = p.stem
                completed_at = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).isoformat()
                data = {"run_id": run_id, "completed_at": completed_at, "examples": records}
            else:
                data = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            _emit_event("eval_format_drift", level="warning",
                        path=str(p.relative_to(REPO_ROOT)), error=str(e))
            continue
        run_id = data.get("run_id") or data.get("id") or p.stem
        if since_id and str(run_id) <= str(since_id):
            continue
        examples = data.get("examples") or data.get("results") or []
        if not isinstance(examples, list):
            continue
        runs.append({
            "run_id": str(run_id),
            "completed_at": data.get("completed_at") or datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).isoformat(),
            "examples": examples,
            "path": str(p.relative_to(REPO_ROOT)),
        })
    return runs


def aggregate_demand_profile(runs: list[dict], state: dict) -> dict:
    """Build the demand profile from new runs.

    Per-pattern failure rate, top-K worst patterns, trend vs prior_top_patterns,
    substrate_type_bias adjustment.
    """
    by_pattern_total: Counter = Counter()
    by_pattern_fail: Counter = Counter()
    total_examples = 0

    for r in runs:
        for ex in r.get("examples", []):
            if not isinstance(ex, dict):
                continue
            total_examples += 1
            # Pattern key: ladder_level + pattern_kind (e.g., "R4_group_theoretic")
            ladder = ex.get("ladder_level") or "R?"
            kind = ex.get("pattern_kind") or ex.get("paradigm") or "uncategorized"
            key = f"{ladder}_{kind}"
            by_pattern_total[key] += 1
            correct = ex.get("correct")
            if correct is False or correct == 0:
                by_pattern_fail[key] += 1

    # Build per-pattern stats
    patterns = []
    for key, total in by_pattern_total.most_common():
        fail = by_pattern_fail[key]
        rate = (fail / total) if total > 0 else 0.0
        patterns.append({"pattern_kind": key, "failure_rate": round(rate, 3),
                         "n": total, "fail_n": fail})

    # Trend computation (vs prior_top_patterns)
    prior = {p["pattern_kind"]: p["failure_rate"] for p in (state.get("prior_top_patterns") or [])}
    for p in patterns:
        prev = prior.get(p["pattern_kind"])
        if prev is None:
            p["trend"] = "new"
        elif p["failure_rate"] > prev + 0.05:
            p["trend"] = "regressing"
        elif p["failure_rate"] < prev - 0.05:
            p["trend"] = "improving"
        else:
            p["trend"] = "stable"

    # Sort by failure_rate desc, threshold n>=5 for priority assignment
    actionable = [p for p in patterns if p["n"] >= 5]
    actionable.sort(key=lambda p: (-p["failure_rate"], -p["n"]))
    for p in actionable:
        if p["failure_rate"] >= 0.5:
            p["priority"] = "P0"
        elif p["failure_rate"] >= 0.3:
            p["priority"] = "P1"
        elif p["failure_rate"] >= 0.15:
            p["priority"] = "P2"
        else:
            p["priority"] = "P3"

    target = [p for p in actionable if p["priority"] in ("P0", "P1")][:TOP_K_DEMAND_PATTERNS]
    low_priority = [p for p in actionable if p["priority"] == "P3"][:5]

    # Substrate-type bias: bias D higher when R3/R4/R5 patterns dominate failures
    bias = dict(DEFAULT_SUBSTRATE_QUOTA)
    if target:
        r45_share = sum(1 for p in target if p["pattern_kind"].startswith(("R3_", "R4_", "R5_"))) / len(target)
        if r45_share >= 0.4:
            # Shift weight from B/C into D
            bias["D"] = round(bias["D"] + 0.10, 3)
            bias["B"] = round(max(0.05, bias["B"] - 0.05), 3)
            bias["C"] = round(max(0.05, bias["C"] - 0.05), 3)
        if any(p["trend"] == "regressing" for p in target):
            # Boost A (anti-anchors) when regressions appear — likely model is
            # hallucinating recently-trained refuted claims.
            bias["A"] = round(bias["A"] + 0.05, 3)
            bias["E"] = round(max(0.05, bias["E"] - 0.05), 3)

    return {
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "charter_version": CHARTER_VERSION,
        "last_eval_run_id": runs[-1]["run_id"] if runs else None,
        "eval_runs_aggregated": len(runs),
        "total_examples": total_examples,
        "target_reasoning_patterns": target,
        "low_priority_patterns": low_priority,
        "substrate_type_bias": bias,
        "all_patterns_count": len(patterns),
    }


def write_profile_atomic(profile: dict) -> Path:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    full_path = ARTIFACT_DIR / f"demand_{ts}.json"
    full_path.write_text(json.dumps(profile, indent=2), encoding="utf-8")
    # Atomic latest pointer
    tmp = DEMAND_LATEST.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(profile, indent=2), encoding="utf-8")
    tmp.replace(DEMAND_LATEST)
    return full_path


# ---------------------------------------------------------------------------
# Heartbeat + log_work
# ---------------------------------------------------------------------------

def emit_heartbeat(state: dict, last_action: str, current_top_patterns: list = None) -> None:
    if not HAS_TELEMETRY:
        return
    status = {
        "anti_silence_counter": state.get("anti_silence_counter", 0),
        "total_profiles_lifetime": state.get("total_profiles_lifetime", 0),
        "total_null_ticks_lifetime": state.get("total_null_ticks_lifetime", 0),
        "last_scanned_eval_id": state.get("last_scanned_eval_id"),
        "last_profile_at": state.get("last_profile_at"),
        "last_action": last_action,
        "charter_version": CHARTER_VERSION,
        "current_top_patterns": current_top_patterns[:5] if current_top_patterns else [],
    }
    try:
        session_telemetry.register_session(
            name=AGENT_NAME, machine=socket.gethostname(),
            role="Substrate demand voicer: Learner-deficit signal to producers",
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
# Tick
# ---------------------------------------------------------------------------

def run_tick(dry_run: bool = False) -> dict:
    tick_started = datetime.now(timezone.utc)
    stats = {"tick_started_at": tick_started.isoformat(), "action": None,
             "profile_published": 0, "null_tick": False, "errors": 0}
    state = load_state()
    current_top_for_heartbeat = state.get("prior_top_patterns", [])

    eval_root = find_active_eval_root()
    _emit_event("tick_start",
                eval_root=str(eval_root) if eval_root else None,
                last_scanned_eval_id=state.get("last_scanned_eval_id"),
                anti_silence_counter=state.get("anti_silence_counter", 0))

    if not eval_root:
        stats["action"] = "upstream_not_found"
        stats["null_tick"] = True
        ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
        artifact_path = ARTIFACT_DIR / f"upstream_not_found_{tick_started.strftime('%Y%m%dT%H%M%S')}.json"
        artifact_path.write_text(json.dumps({
            "tick_at": tick_started.isoformat(),
            "searched": [str(r) for r in EVAL_ROOTS],
            "ask": "Pheme requires Ergon's eval output. Configure EVAL_ROOTS in agents/pheme/daemon.py.",
        }, indent=2), encoding="utf-8")
        emit_log_work("pheme_upstream_not_found",
                      summary="Ergon eval root not found; checked: " + ", ".join(str(r) for r in EVAL_ROOTS),
                      output_path=str(artifact_path.relative_to(REPO_ROOT)),
                      success=False, error="eval_root_not_configured")
        state["anti_silence_counter"] = state.get("anti_silence_counter", 0) + 1
        state["total_null_ticks_lifetime"] = state.get("total_null_ticks_lifetime", 0) + 1
    else:
        new_runs = scan_new_eval_runs(eval_root, state.get("last_scanned_eval_id"))
        _emit_event("eval_scan_complete",
                    eval_root=str(eval_root),
                    new_run_count=len(new_runs))

        # Eval-drought check: even if no new runs, did the last run land recently enough?
        drought = False
        last_profile_iso = state.get("last_profile_at")
        if last_profile_iso:
            try:
                last_dt = datetime.fromisoformat(last_profile_iso.replace("Z", "+00:00"))
                if (tick_started - last_dt).days >= EVAL_DROUGHT_DAYS:
                    drought = True
            except Exception:
                pass

        if not new_runs:
            if drought:
                stats["action"] = "eval_drought"
                ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
                artifact_path = ARTIFACT_DIR / f"eval_drought_{tick_started.strftime('%Y%m%dT%H%M%S')}.json"
                artifact_path.write_text(json.dumps({
                    "tick_at": tick_started.isoformat(),
                    "last_profile_at": last_profile_iso,
                    "days_since": EVAL_DROUGHT_DAYS,
                    "ask": "Demand signal going stale; producers are flying blind. Trigger Ergon eval.",
                }, indent=2), encoding="utf-8")
                emit_log_work("pheme_eval_drought",
                              summary=f"No eval run in {EVAL_DROUGHT_DAYS}+ days; demand signal stale",
                              output_path=str(artifact_path.relative_to(REPO_ROOT)),
                              success=False, error="eval_drought")
            else:
                stats["action"] = "null_tick_no_new_evals"
                ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
                artifact_path = ARTIFACT_DIR / f"null_{tick_started.strftime('%Y%m%dT%H%M%S')}.json"
                artifact_path.write_text(json.dumps({
                    "tick_at": tick_started.isoformat(),
                    "reason": "no_new_eval_runs",
                    "last_scanned_eval_id": state.get("last_scanned_eval_id"),
                }, indent=2), encoding="utf-8")
                emit_log_work("pheme_null_tick",
                              summary=f"No new eval runs since {state.get('last_scanned_eval_id')}",
                              output_path=str(artifact_path.relative_to(REPO_ROOT)))
            stats["null_tick"] = True
            state["anti_silence_counter"] = state.get("anti_silence_counter", 0) + 1
            state["total_null_ticks_lifetime"] = state.get("total_null_ticks_lifetime", 0) + 1
        else:
            profile = aggregate_demand_profile(new_runs, state)
            if dry_run:
                stats["action"] = "would_publish_profile"
                _emit_event("dry_run_would_publish",
                            target_patterns=len(profile["target_reasoning_patterns"]))
            else:
                path = write_profile_atomic(profile)
                stats["action"] = "published_profile"
                stats["profile_published"] = 1
                state["last_profile_at"] = profile["computed_at"]
                state["last_scanned_eval_id"] = profile["last_eval_run_id"]
                state["prior_top_patterns"] = profile["target_reasoning_patterns"]
                state["total_profiles_lifetime"] = state.get("total_profiles_lifetime", 0) + 1
                state["anti_silence_counter"] = 0
                current_top_for_heartbeat = profile["target_reasoning_patterns"]
                emit_log_work("ergon_substrate_demand",
                              summary=(f"Published demand profile: {len(profile['target_reasoning_patterns'])} "
                                       f"target patterns from {profile['eval_runs_aggregated']} eval runs "
                                       f"({profile['total_examples']} examples). Top pattern: "
                                       f"{profile['target_reasoning_patterns'][0]['pattern_kind'] if profile['target_reasoning_patterns'] else 'none'}"),
                              output_path=str(path.relative_to(REPO_ROOT)))
                _emit_event("profile_published",
                            target_patterns=len(profile["target_reasoning_patterns"]),
                            substrate_bias=profile["substrate_type_bias"])

    if state.get("anti_silence_counter", 0) >= ANTI_SILENCE_ALARM_THRESHOLD:
        _emit_event("self_audit_null_alarm", level="error",
                    consecutive_null=state["anti_silence_counter"])
        emit_log_work("pheme_self_audit_null",
                      summary=f"ALARM: {state['anti_silence_counter']} consecutive null ticks. Eval upstream likely dead.",
                      success=False, error="anti_silence_threshold_exceeded")

    save_state(state)
    emit_heartbeat(state, last_action=stats["action"] or "unknown",
                   current_top_patterns=current_top_for_heartbeat)
    _emit_event("tick_end", **{k: v for k, v in stats.items() if not k.startswith("_")})
    return stats


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def print_status() -> None:
    state = load_state()
    eval_root = find_active_eval_root()
    print(f"=== Pheme status ===")
    print(f"  charter_version: {state.get('charter_version')}")
    print(f"  eval_root:       {eval_root}")
    print(f"  total_profiles_lifetime:   {state.get('total_profiles_lifetime', 0)}")
    print(f"  total_null_ticks_lifetime: {state.get('total_null_ticks_lifetime', 0)}")
    print(f"  anti_silence_counter:      {state.get('anti_silence_counter', 0)}")
    print(f"  last_scanned_eval_id:      {state.get('last_scanned_eval_id')}")
    print(f"  last_profile_at:           {state.get('last_profile_at')}")
    print(f"  demand_latest exists:      {DEMAND_LATEST.exists()}")
    print(f"  lock file exists:          {PID_FILE.exists()}")


def main():
    ap = argparse.ArgumentParser(description="Pheme — substrate demand voicer daemon")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("status", help="print current state and exit")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--interval", type=int, default=DEFAULT_INTERVAL_SEC)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.cmd == "status":
        print_status()
        return 0

    if not acquire_lock():
        return 2
    try:
        bar = "=" * 60
        banner = "\n".join([
            bar,
            f"  Pheme v0.1 — substrate demand voicer (operator={OPERATOR})",
            f"  Telemetry:   {'on' if HAS_TELEMETRY else 'OFF'}",
            f"  Structlog:   {'on' if HAS_STRUCTLOG else 'OFF'}",
            f"  Mode:        {'loop @ ' + str(args.interval) + 's' if args.loop else 'once'}",
            bar,
        ])
        for line in banner.splitlines():
            _text_log.info(line)
        _emit_event("startup", telemetry=HAS_TELEMETRY, structlog=HAS_STRUCTLOG,
                    mode=("loop" if args.loop else "once"))
        emit_log_work("pheme_startup",
                      summary=f"Pheme daemon up; mode={'loop' if args.loop else 'once'} interval={args.interval}s")
        if args.once or not args.loop:
            stats = run_tick(dry_run=args.dry_run)
            _text_log.info(f"tick: {stats}")
            return 0
        while True:
            try:
                stats = run_tick(dry_run=args.dry_run)
                _text_log.info(f"tick: {stats}")
            except Exception:
                _emit_event("tick_uncaught_exception", level="error")
                _text_log.exception("uncaught exception in tick")
            time.sleep(max(1, args.interval))
    finally:
        emit_log_work("pheme_shutdown", summary="Pheme daemon shutting down")
        _emit_event("shutdown")
        release_lock()


if __name__ == "__main__":
    sys.exit(main() or 0)
