"""Hypatia — D-track curator daemon.

See agents/hypatia/CHARTER.md for the full contract. Summary:
  - Picks 1 problem per 24h from aporia/mathematics/questions.jsonl
  - Builds a Type-D DR prompt (proof decomposition with R1-R5 ladder)
  - Enqueues to agora.research_queue with target_substrate_type='D'
  - Emits artifacts + heartbeat + log_work every tick (anti-silence)
  - Single-instance lock, persisted state, structured event JSONL
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import socket
import sys
import time
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

# Soft imports — daemon degrades gracefully if Postgres / telemetry / shared
# logging is unavailable.
try:
    import agora_persist
    HAS_PG = True
except Exception as e:
    agora_persist = None  # type: ignore
    HAS_PG = False
    _PG_ERR = str(e)

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
PID_FILE = AGENT_DIR / "hypatia.pid"
STATE_FILE = STATE_DIR / "state.json"
TEXT_LOG = LOG_DIR / "hypatia.log"

# External paths
QUESTIONS_JSONL = REPO_ROOT / "aporia" / "mathematics" / "questions.jsonl"
PHEME_DEMAND_LATEST = REPO_ROOT / "agents" / "pheme" / "artifacts" / "demand_latest.json"

# Defaults
DEFAULT_INTERVAL_SEC = 3600
DEFAULT_PICK_COOLDOWN_HOURS = 24
RECENTLY_PICKED_WINDOW_DAYS = 30
ANTI_SILENCE_ALARM_THRESHOLD = 50
CHARTER_VERSION = "v1"
AGENT_NAME = "Hypatia"
OPERATOR = "Aporia"

# Per-step reasoning-ladder definitions used in the Type-D prompt
LADDER_LEGEND = (
    "R1: Direct lookup (definition/axiom/named-theorem invocation).\n"
    "R2: 1-step transform (apply one known equation, substitution, rewrite).\n"
    "R3: 2-3 step chain (combine 2-3 R1/R2 steps).\n"
    "R4: Structural insight (symmetry, duality, decomposition).\n"
    "R5: Novel framework (construction not in standard toolkit)."
)

TYPE_D_PROMPT_TEMPLATE = """Decompose the proof of the following result into atomic reasoning steps, each tagged with its reasoning-ladder level.

PROBLEM (id={problem_id}):
{problem_text}

CITATION (if known):
{problem_citation}

CONTEXT:
This query is from Hypatia (Prometheus D-track curator). Output will be ingested into the Learner's worked-solutions training corpus. Step-level ladder annotation is the load-bearing element — without it the output is unusable.

REASONING LADDER (use exactly these tags):
{ladder_legend}

OUTPUT FORMAT (strict JSONL, one step per line, in proof order):
{{"step": 1, "claim": "<one-sentence claim being proved at this step>", "justification": "<the move that gets us there>", "ladder": "R1|R2|R3|R4|R5", "depends_on": [<prior step numbers>]}}

After the JSONL block, give a one-paragraph commentary on the proof's overall structure and which step is the load-bearing R4 or R5 (if any).

Cite at least 2 of the 5 mandated calibration patterns where applicable: PATTERN_PRIME_GRAVITATIONAL_OVERFIT, PATTERN_CONDUCTOR_CONFOUND, PATTERN_BASE_RATE_NEGLECT, PATTERN_VRAM_TRUNCATION_ARTIFACT, PATTERN_RANK_PARITY_LEAK.
"""


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def _setup_text_logger() -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log = logging.getLogger("hypatia")
    if log.handlers:
        return log
    log.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s [HYPATIA] %(message)s")
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    log.addHandler(sh)
    fh = logging.FileHandler(TEXT_LOG, encoding="utf-8")
    fh.setFormatter(fmt)
    log.addHandler(fh)
    return log


_text_log = _setup_text_logger()
_evt_log = get_structured_logger("hypatia", log_dir=AGENT_DIR) if HAS_STRUCTLOG else None


def _emit_event(event: str, level: str = "info", **kwargs) -> None:
    """Dual-emit to events.jsonl + text log. Never crashes the daemon."""
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
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            h = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
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
    """Return True if we got the lock; False if another instance is alive."""
    AGENT_DIR.mkdir(parents=True, exist_ok=True)
    if PID_FILE.exists():
        try:
            data = json.loads(PID_FILE.read_text(encoding="utf-8"))
            existing_pid = int(data.get("pid", 0))
            if existing_pid and existing_pid != os.getpid() and _is_pid_alive(existing_pid):
                _text_log.error(
                    f"another hypatia instance is alive (pid={existing_pid} started={data.get('started_at')}); aborting"
                )
                return False
        except Exception:
            pass  # stale or malformed; we'll overwrite
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
        "last_pick_at": None,
        "last_problem_id": None,
        "anti_silence_counter": 0,
        "total_dispatched_lifetime": 0,
        "total_null_ticks_lifetime": 0,
        "recently_picked": {},  # problem_id -> ISO timestamp
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
# Problem catalog + selection
# ---------------------------------------------------------------------------

def load_questions_catalog() -> list[dict]:
    if not QUESTIONS_JSONL.exists():
        _emit_event("catalog_not_found", level="error", path=str(QUESTIONS_JSONL))
        return []
    out = []
    for line in QUESTIONS_JSONL.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def load_pheme_demand_profile() -> Optional[dict]:
    """Pheme writes a substrate-demand profile naming the worst-performing
    reasoning patterns. Hypatia biases problem selection toward those.
    Returns None if Pheme hasn't run yet."""
    if not PHEME_DEMAND_LATEST.exists():
        return None
    try:
        return json.loads(PHEME_DEMAND_LATEST.read_text(encoding="utf-8"))
    except Exception:
        return None


def select_next_problem(catalog: list[dict], state: dict,
                        demand_profile: Optional[dict]) -> Optional[dict]:
    """Round-robin over the catalog, excluding recently-picked, biased by Pheme."""
    if not catalog:
        return None
    cutoff = datetime.now(timezone.utc) - timedelta(days=RECENTLY_PICKED_WINDOW_DAYS)
    recently = state.get("recently_picked", {})
    candidates = []
    for entry in catalog:
        pid = entry.get("id") or entry.get("problem_id")
        if not pid:
            continue
        last = recently.get(pid)
        if last:
            try:
                last_dt = datetime.fromisoformat(last.replace("Z", "+00:00"))
                if last_dt > cutoff:
                    continue
            except Exception:
                pass
        candidates.append(entry)
    if not candidates:
        _emit_event("catalog_saturated", level="warning",
                    catalog_size=len(catalog), recently_picked_count=len(recently))
        return None
    # Bias: if Pheme's demand profile names target patterns, prefer matching ones
    if demand_profile:
        target_patterns = set(demand_profile.get("target_reasoning_patterns") or [])
        if target_patterns:
            biased = [c for c in candidates if str(c.get("pattern_kind", "")) in target_patterns]
            if biased:
                candidates = biased
                _emit_event("pheme_demand_bias_applied", level="info",
                            target_patterns=list(target_patterns),
                            biased_subset_size=len(biased))
    # Within candidates: prefer ones never picked before; else oldest-picked
    candidates.sort(key=lambda c: recently.get(c.get("id") or "", ""))
    return candidates[0]


# ---------------------------------------------------------------------------
# DR dispatch
# ---------------------------------------------------------------------------

def build_type_d_prompt(problem: dict) -> str:
    return TYPE_D_PROMPT_TEMPLATE.format(
        problem_id=problem.get("id") or problem.get("problem_id") or "unknown",
        problem_text=problem.get("question") or problem.get("statement") or problem.get("text") or "",
        problem_citation=problem.get("citation") or problem.get("source") or "(none recorded in catalog)",
        ladder_legend=LADDER_LEGEND,
    )


def dispatch_problem(problem: dict, state: dict, demand_profile: Optional[dict]) -> Optional[dict]:
    """Enqueue the problem as a Type-D Pythia DR query. Returns dispatch record."""
    if not HAS_PG:
        _emit_event("pg_unavailable_cannot_dispatch", level="error")
        return None
    pid = problem.get("id") or problem.get("problem_id") or "unknown"
    now = datetime.now(timezone.utc)
    queue_ref = f"HYP-{now.strftime('%Y-%m-%d')}-{state.get('total_dispatched_lifetime', 0) + 1:03d}"
    prompt = build_type_d_prompt(problem)
    title = f"Hypatia D-track [{queue_ref}]: proof decomposition for {pid}"
    tags = {
        "source": "hypatia_d_track",
        "problem_id": pid,
        "charter_version": CHARTER_VERSION,
        "ergon_demand_target": (demand_profile or {}).get("target_reasoning_patterns"),
        "pheme_demand_profile_at": (demand_profile or {}).get("computed_at"),
        "verdict_back_to": "ergon/learner/corpus/v1_0_tier_pending/worked_solutions/",
    }
    try:
        rid = agora_persist.enqueue_research(
            title=title[:300], prompt_text=prompt,
            requested_by="Hypatia", priority=4, tier="T2",
            queue_ref=queue_ref, target_substrate_type="D",
            tags=tags,
        )
    except Exception as e:
        _emit_event("dispatch_failed", level="error",
                    problem_id=pid, queue_ref=queue_ref, error=str(e))
        return None
    if not rid:
        _emit_event("dispatch_returned_no_rid", level="error",
                    problem_id=pid, queue_ref=queue_ref)
        return None

    # Persist artifact
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    artifact_path = ARTIFACT_DIR / f"dispatch_{queue_ref}.md"
    artifact_path.write_text(
        f"# Hypatia dispatch — {queue_ref}\n\n"
        f"- **Problem id:** {pid}\n"
        f"- **Pythia row id:** {rid}\n"
        f"- **Substrate type:** D (worked solution with R1-R5 ladder)\n"
        f"- **Dispatched at:** {now.isoformat()}\n"
        f"- **Charter version:** {CHARTER_VERSION}\n"
        f"- **Pheme demand bias:** {tags['ergon_demand_target']}\n\n"
        f"## Title\n\n{title}\n\n## Prompt\n\n```\n{prompt}\n```\n",
        encoding="utf-8",
    )
    return {
        "queue_ref": queue_ref, "row_id": rid, "problem_id": pid,
        "dispatched_at": now.isoformat(), "artifact": str(artifact_path.relative_to(REPO_ROOT)),
    }


# ---------------------------------------------------------------------------
# Heartbeat + log_work
# ---------------------------------------------------------------------------

def emit_heartbeat(state: dict, last_action: str) -> None:
    if not HAS_TELEMETRY:
        return
    status = {
        "anti_silence_counter": state.get("anti_silence_counter", 0),
        "total_dispatched_lifetime": state.get("total_dispatched_lifetime", 0),
        "total_null_ticks_lifetime": state.get("total_null_ticks_lifetime", 0),
        "last_pick_at": state.get("last_pick_at"),
        "last_problem_id": state.get("last_problem_id"),
        "last_action": last_action,
        "catalog_size": state.get("_catalog_size_cached", 0),
        "charter_version": CHARTER_VERSION,
    }
    try:
        session_telemetry.register_session(
            name=AGENT_NAME, machine=socket.gethostname(),
            role="D-track curator: worked solutions with R1-R5 ladder",
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
    stats = {
        "tick_started_at": tick_started.isoformat(),
        "action": None,
        "dispatched": 0,
        "null_tick": False,
        "errors": 0,
    }

    state = load_state()
    catalog = load_questions_catalog()
    state["_catalog_size_cached"] = len(catalog)
    demand_profile = load_pheme_demand_profile()

    _emit_event("tick_start",
                catalog_size=len(catalog),
                pheme_demand_available=demand_profile is not None,
                anti_silence_counter=state.get("anti_silence_counter", 0))

    # Check the 24h cooldown
    last_pick = state.get("last_pick_at")
    cooldown_elapsed = True
    next_pick_at = None
    if last_pick:
        try:
            last_dt = datetime.fromisoformat(last_pick.replace("Z", "+00:00"))
            next_pick_at = last_dt + timedelta(hours=DEFAULT_PICK_COOLDOWN_HOURS)
            cooldown_elapsed = tick_started >= next_pick_at
        except Exception:
            cooldown_elapsed = True

    if cooldown_elapsed:
        problem = select_next_problem(catalog, state, demand_profile)
        if not problem:
            # Catalog saturated — emit loud sentinel
            stats["action"] = "catalog_saturated"
            stats["null_tick"] = True
            ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
            artifact_path = ARTIFACT_DIR / f"catalog_saturated_{tick_started.strftime('%Y%m%dT%H%M%S')}.json"
            artifact_path.write_text(json.dumps({
                "tick_at": tick_started.isoformat(),
                "catalog_size": len(catalog),
                "recently_picked_count": len(state.get("recently_picked", {})),
                "ask": "Aporia: expand aporia/mathematics/questions.jsonl; the 30-day recently-picked window has consumed the available catalog.",
            }, indent=2), encoding="utf-8")
            emit_log_work("hypatia_catalog_saturated",
                          summary=f"Catalog saturated: {len(catalog)} problems all in 30-day window. Need Aporia expansion.",
                          output_path=str(artifact_path.relative_to(REPO_ROOT)),
                          success=False, error="catalog_saturated")
            state["anti_silence_counter"] = state.get("anti_silence_counter", 0) + 1
            state["total_null_ticks_lifetime"] = state.get("total_null_ticks_lifetime", 0) + 1
        else:
            if dry_run:
                stats["action"] = "would_dispatch"
                _emit_event("dry_run_would_dispatch", problem_id=problem.get("id"))
            else:
                result = dispatch_problem(problem, state, demand_profile)
                if result:
                    stats["action"] = "dispatched"
                    stats["dispatched"] = 1
                    pid = result["problem_id"]
                    state["last_pick_at"] = result["dispatched_at"]
                    state["last_problem_id"] = pid
                    state["recently_picked"][pid] = result["dispatched_at"]
                    state["total_dispatched_lifetime"] = state.get("total_dispatched_lifetime", 0) + 1
                    state["anti_silence_counter"] = 0
                    emit_log_work("hypatia_dispatch",
                                  summary=f"Dispatched Type-D DR for problem {pid} as {result['queue_ref']} (row {result['row_id']})",
                                  output_path=result["artifact"])
                    _emit_event("dispatch_complete",
                                problem_id=pid, queue_ref=result["queue_ref"], row_id=result["row_id"])
                else:
                    stats["action"] = "dispatch_failed"
                    stats["errors"] = 1
    else:
        # Within 24h cooldown — emit NULL_TICK sentinel
        stats["action"] = "null_tick_within_cooldown"
        stats["null_tick"] = True
        ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
        artifact_path = ARTIFACT_DIR / f"null_{tick_started.strftime('%Y%m%dT%H%M%S')}.json"
        artifact_path.write_text(json.dumps({
            "tick_at": tick_started.isoformat(),
            "reason": "within_24h_cooldown",
            "last_pick_at": last_pick,
            "next_pick_at": next_pick_at.isoformat() if next_pick_at else None,
            "anti_silence_counter": state.get("anti_silence_counter", 0) + 1,
        }, indent=2), encoding="utf-8")
        state["anti_silence_counter"] = state.get("anti_silence_counter", 0) + 1
        state["total_null_ticks_lifetime"] = state.get("total_null_ticks_lifetime", 0) + 1
        emit_log_work("hypatia_null_tick",
                      summary=f"Within 24h cooldown; next pick at {next_pick_at.isoformat() if next_pick_at else 'unknown'}",
                      output_path=str(artifact_path.relative_to(REPO_ROOT)))

    # Anti-silence alarm
    if state.get("anti_silence_counter", 0) >= ANTI_SILENCE_ALARM_THRESHOLD:
        _emit_event("self_audit_null_alarm", level="error",
                    consecutive_null=state["anti_silence_counter"])
        emit_log_work("hypatia_self_audit_null",
                      summary=f"ALARM: {state['anti_silence_counter']} consecutive null ticks (>= {ANTI_SILENCE_ALARM_THRESHOLD}). Likely state corruption or stuck cooldown.",
                      success=False, error="anti_silence_threshold_exceeded")

    save_state(state)
    emit_heartbeat(state, last_action=stats["action"] or "unknown")
    _emit_event("tick_end", **{k: v for k, v in stats.items() if not k.startswith("_")})
    return stats


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def print_status() -> None:
    state = load_state()
    print(f"=== Hypatia status ===")
    print(f"  charter_version: {state.get('charter_version')}")
    print(f"  total_dispatched_lifetime: {state.get('total_dispatched_lifetime', 0)}")
    print(f"  total_null_ticks_lifetime: {state.get('total_null_ticks_lifetime', 0)}")
    print(f"  anti_silence_counter:      {state.get('anti_silence_counter', 0)}")
    print(f"  last_pick_at:              {state.get('last_pick_at')}")
    print(f"  last_problem_id:           {state.get('last_problem_id')}")
    print(f"  recently_picked count:     {len(state.get('recently_picked', {}))}")
    print(f"  lock file exists:          {PID_FILE.exists()}")


def main():
    ap = argparse.ArgumentParser(description="Hypatia — D-track curator daemon")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("status", help="print current state and exit")
    ap.add_argument("--once", action="store_true", help="single tick then exit")
    ap.add_argument("--loop", action="store_true", help="loop with --interval delay")
    ap.add_argument("--interval", type=int, default=DEFAULT_INTERVAL_SEC,
                    help=f"loop interval seconds (default {DEFAULT_INTERVAL_SEC})")
    ap.add_argument("--dry-run", action="store_true", help="do not actually dispatch")
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
            f"  Hypatia v0.1 — D-track curator (operator={OPERATOR})",
            f"  Postgres:    {'on' if HAS_PG else 'OFF (degraded)'}",
            f"  Telemetry:   {'on' if HAS_TELEMETRY else 'OFF (degraded)'}",
            f"  Structlog:   {'on' if HAS_STRUCTLOG else 'OFF (text-only)'}",
            f"  Mode:        {'loop @ ' + str(args.interval) + 's' if args.loop else 'once'}",
            bar,
        ])
        for line in banner.splitlines():
            _text_log.info(line)
        _emit_event("startup",
                    pg=HAS_PG, telemetry=HAS_TELEMETRY, structlog=HAS_STRUCTLOG,
                    mode=("loop" if args.loop else "once"), interval=args.interval)
        emit_log_work("hypatia_startup",
                      summary=f"Hypatia daemon up; mode={'loop' if args.loop else 'once'} interval={args.interval}s",
                      output_path=None)
        if args.once or not args.loop:
            stats = run_tick(dry_run=args.dry_run)
            _text_log.info(f"tick: {stats}")
            return 0
        # Loop
        while True:
            try:
                stats = run_tick(dry_run=args.dry_run)
                _text_log.info(f"tick: {stats}")
            except Exception as e:
                _emit_event("tick_uncaught_exception", level="error", error=str(e))
                _text_log.exception("uncaught exception in tick")
            time.sleep(max(1, args.interval))
    finally:
        emit_log_work("hypatia_shutdown", summary="Hypatia daemon shutting down")
        _emit_event("shutdown")
        release_lock()


if __name__ == "__main__":
    sys.exit(main() or 0)
