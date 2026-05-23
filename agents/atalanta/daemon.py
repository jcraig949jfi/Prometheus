"""Atalanta — E-track primitive hunter daemon.

See agents/atalanta/CHARTER.md for the full contract. Summary:
  - Scans Apollo's runs/ directory for new organism logs since last tick
  - Aggregates primitive-usage frequencies + unnamed composite chains
  - Fires Type-E DR query for the top candidate (rotating high-reuse vs unnamed-composite)
  - Anti-silence: NULL_TICK or UPSTREAM_NOT_FOUND sentinel every tick if no work
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import socket
import sys
import time
from collections import Counter
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
    import agora_persist
    HAS_PG = True
except Exception:
    agora_persist = None  # type: ignore
    HAS_PG = False

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
PID_FILE = AGENT_DIR / "atalanta.pid"
STATE_FILE = STATE_DIR / "state.json"
TEXT_LOG = LOG_DIR / "atalanta.log"

# External roots (in order; first existing root is the active source)
APOLLO_RUN_ROOTS = [
    REPO_ROOT / "apollo" / "runs",
    REPO_ROOT / "apollo" / "runs_v2",
    REPO_ROOT / "apollo" / "organism_runs",
]

# Defaults
DEFAULT_INTERVAL_SEC = 1800
ANTI_SILENCE_ALARM_THRESHOLD = 50
MIN_REUSE_FOR_CANDIDATE = 3        # primitive must appear in >= 3 organisms
MIN_COMPOSITE_FOR_CANDIDATE = 3    # composite chain must appear >= 3 times
CANDIDATE_RECENT_FIRE_WINDOW_DAYS = 14
CHARTER_VERSION = "v1"
AGENT_NAME = "Atalanta"
OPERATOR = "Aporia"

TYPE_E_PROMPT_TEMPLATE = """Identify candidate atomic reasoning primitives that recur across the following Apollo organisms.

CONTEXT:
Apollo evolves primitive routing DAGs. The Prometheus substrate uses these to build reusable reasoning tools. We are looking for primitives that should be NAMED and REGISTERED in the substrate's primitive catalog, either because they are repeatedly re-derived from composites, or because they appear in many successful organisms but lack a canonical name.

OBSERVATION (from Atalanta's scan of recent Apollo runs):
{observation_summary}

THE CANDIDATE:
{candidate_description}

OUTPUT (strict JSONL block per primitive proposal):
{{"primitive_name": "<CamelCase>", "signature": "<input_types> -> <output_type>", "when_applied": "<conditions of applicability>", "composition_rules": "<how it composes with existing primitives>", "evidence_organisms": [<organism ids>], "related_existing_primitives": [<existing primitive names if any>]}}

Cite at least 2 of the 5 mandated calibration patterns where applicable: PATTERN_PRIME_GRAVITATIONAL_OVERFIT, PATTERN_CONDUCTOR_CONFOUND, PATTERN_BASE_RATE_NEGLECT, PATTERN_VRAM_TRUNCATION_ARTIFACT, PATTERN_RANK_PARITY_LEAK.

After the JSONL, give a one-paragraph rationale: why this primitive is likely to be load-bearing, and what current substrate gap it fills.
"""


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def _setup_text_logger() -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log = logging.getLogger("atalanta")
    if log.handlers:
        return log
    log.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s [ATALANTA] %(message)s")
    sh = logging.StreamHandler(sys.stdout); sh.setFormatter(fmt); log.addHandler(sh)
    fh = logging.FileHandler(TEXT_LOG, encoding="utf-8"); fh.setFormatter(fmt); log.addHandler(fh)
    return log


_text_log = _setup_text_logger()
_evt_log = get_structured_logger("atalanta", log_dir=AGENT_DIR) if HAS_STRUCTLOG else None


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
# Single-instance lock (identical shape to Hypatia)
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
                _text_log.error(f"another atalanta instance is alive (pid={existing_pid}); aborting")
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
        "last_scanned_run_id": None,
        "last_pick_at": None,
        "anti_silence_counter": 0,
        "total_dispatched_lifetime": 0,
        "total_null_ticks_lifetime": 0,
        "recently_fired_candidate_hashes": {},  # hash -> ts
        "last_bucket_picked": None,  # 'high_reuse' | 'unnamed_composite' (rotates)
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
# Apollo runs ingestion
# ---------------------------------------------------------------------------

def find_active_apollo_root() -> Optional[Path]:
    for root in APOLLO_RUN_ROOTS:
        if root.exists() and root.is_dir():
            return root
    return None


def scan_new_apollo_runs(root: Path, since_id: Optional[str]) -> list[dict]:
    """Walk the Apollo root for completed runs newer than since_id.

    Tolerant of multiple plausible schemas. Each returned record is a dict
    with at least {run_id, organisms: [{organism_id, primitive_sequence}, ...]}.
    Parse failures emit APOLLO_FORMAT_DRIFT events but don't abort the tick.
    """
    if not root or not root.exists():
        return []
    runs = []
    for p in sorted(root.rglob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            _emit_event("apollo_format_drift", level="warning",
                        path=str(p.relative_to(REPO_ROOT)), error=str(e))
            continue
        run_id = data.get("run_id") or data.get("id") or p.stem
        if since_id and str(run_id) <= str(since_id):
            continue
        organisms = data.get("organisms") or data.get("population") or []
        if not isinstance(organisms, list):
            _emit_event("apollo_format_drift", level="warning",
                        path=str(p.relative_to(REPO_ROOT)), reason="organisms_not_list")
            continue
        normalized = []
        for o in organisms:
            if not isinstance(o, dict):
                continue
            seq = o.get("primitive_sequence") or o.get("sequence") or o.get("genome") or []
            if not isinstance(seq, list):
                continue
            normalized.append({
                "organism_id": o.get("organism_id") or o.get("id") or "unknown",
                "primitive_sequence": [str(x) for x in seq],
            })
        runs.append({"run_id": str(run_id), "organisms": normalized,
                     "path": str(p.relative_to(REPO_ROOT))})
    return runs


def aggregate_primitive_signals(runs: list[dict]) -> dict:
    """From a list of normalized runs, compute high-reuse + unnamed-composite buckets."""
    primitive_counts: Counter = Counter()
    composite_counts: Counter = Counter()  # tuple-of-2 or tuple-of-3 chains
    organism_index = {}  # primitive -> [organism_ids]
    for r in runs:
        for o in r.get("organisms", []):
            seq = o["primitive_sequence"]
            oid = o["organism_id"]
            for p in seq:
                primitive_counts[p] += 1
                organism_index.setdefault(p, []).append(oid)
            for i in range(len(seq) - 1):
                composite_counts[(seq[i], seq[i + 1])] += 1
            for i in range(len(seq) - 2):
                composite_counts[(seq[i], seq[i + 1], seq[i + 2])] += 1
    high_reuse = [
        {"primitive": p, "count": c, "organisms": organism_index[p][:10]}
        for p, c in primitive_counts.most_common() if c >= MIN_REUSE_FOR_CANDIDATE
    ]
    unnamed_composites = [
        {"composite": list(comp), "count": c}
        for comp, c in composite_counts.most_common() if c >= MIN_COMPOSITE_FOR_CANDIDATE
    ]
    return {
        "high_reuse": high_reuse,
        "unnamed_composites": unnamed_composites,
        "total_organisms": sum(len(r["organisms"]) for r in runs),
        "total_runs": len(runs),
    }


def pick_candidate(signals: dict, state: dict) -> Optional[dict]:
    """Rotate between high_reuse and unnamed_composite buckets; skip recently fired."""
    last_bucket = state.get("last_bucket_picked")
    next_bucket = "unnamed_composite" if last_bucket == "high_reuse" else "high_reuse"
    recently = set(state.get("recently_fired_candidate_hashes", {}).keys())

    def _candidate_hash(kind: str, payload) -> str:
        return hashlib.sha1(f"{kind}:{json.dumps(payload, sort_keys=True)}".encode()).hexdigest()[:16]

    for bucket in (next_bucket, last_bucket or "high_reuse"):
        items = signals.get(bucket if bucket == "high_reuse" else "unnamed_composites", [])
        for item in items:
            payload = item.get("primitive") if bucket == "high_reuse" else item.get("composite")
            h = _candidate_hash(bucket, payload)
            if h in recently:
                continue
            return {"kind": bucket, "payload": payload, "evidence": item, "hash": h}
    return None


# ---------------------------------------------------------------------------
# DR dispatch
# ---------------------------------------------------------------------------

def build_observation_summary(signals: dict) -> str:
    return (
        f"Scanned {signals.get('total_runs', 0)} Apollo runs across "
        f"{signals.get('total_organisms', 0)} organisms.\n"
        f"High-reuse primitives (>= {MIN_REUSE_FOR_CANDIDATE} organisms): "
        f"{len(signals.get('high_reuse', []))}.\n"
        f"Unnamed composite chains (>= {MIN_COMPOSITE_FOR_CANDIDATE} appearances): "
        f"{len(signals.get('unnamed_composites', []))}."
    )


def build_candidate_description(candidate: dict) -> str:
    if candidate["kind"] == "high_reuse":
        ev = candidate["evidence"]
        return (
            f"HIGH-REUSE PRIMITIVE: `{ev['primitive']}` appears in {ev['count']} organisms.\n"
            f"Sample organism ids: {ev['organisms']}.\n"
            f"This primitive is heavily used; nearby variants likely have high leverage."
        )
    else:
        ev = candidate["evidence"]
        return (
            f"UNNAMED COMPOSITE CHAIN: `{' -> '.join(ev['composite'])}` "
            f"appears {ev['count']} times across organisms.\n"
            f"This composite is being repeatedly re-derived; a named primitive that captures it "
            f"would compress organism length and free Apollo to explore further."
        )


def dispatch_candidate(candidate: dict, signals: dict, state: dict) -> Optional[dict]:
    if not HAS_PG:
        _emit_event("pg_unavailable_cannot_dispatch", level="error")
        return None
    now = datetime.now(timezone.utc)
    queue_ref = f"ATA-{now.strftime('%Y-%m-%d')}-{state.get('total_dispatched_lifetime', 0) + 1:03d}"
    obs = build_observation_summary(signals)
    desc = build_candidate_description(candidate)
    prompt = TYPE_E_PROMPT_TEMPLATE.format(observation_summary=obs, candidate_description=desc)
    payload_summary = str(candidate["payload"])[:50]
    title = f"Atalanta E-track [{queue_ref}]: primitive candidate {candidate['kind']} ({payload_summary})"
    tags = {
        "source": "atalanta_e_track",
        "candidate_kind": candidate["kind"],
        "candidate_payload": candidate["payload"],
        "candidate_hash": candidate["hash"],
        "charter_version": CHARTER_VERSION,
        "verdict_back_to": "techne/registry/primitive_candidates/",
    }
    try:
        rid = agora_persist.enqueue_research(
            title=title[:300], prompt_text=prompt,
            requested_by="Atalanta", priority=4, tier="T2",
            queue_ref=queue_ref, target_substrate_type="E",
            tags=tags,
        )
    except Exception as e:
        _emit_event("dispatch_failed", level="error", error=str(e))
        return None
    if not rid:
        _emit_event("dispatch_returned_no_rid", level="error", queue_ref=queue_ref)
        return None

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    artifact_path = ARTIFACT_DIR / f"dispatch_{queue_ref}.md"
    artifact_path.write_text(
        f"# Atalanta dispatch — {queue_ref}\n\n"
        f"- **Candidate kind:** {candidate['kind']}\n"
        f"- **Candidate payload:** `{candidate['payload']}`\n"
        f"- **Candidate hash:** {candidate['hash']}\n"
        f"- **Pythia row id:** {rid}\n"
        f"- **Substrate type:** E (primitive proposal candidate)\n"
        f"- **Dispatched at:** {now.isoformat()}\n\n"
        f"## Observation\n\n{obs}\n\n## Candidate\n\n{desc}\n\n## Title\n\n{title}\n\n"
        f"## Full prompt\n\n```\n{prompt}\n```\n",
        encoding="utf-8",
    )
    return {
        "queue_ref": queue_ref, "row_id": rid, "dispatched_at": now.isoformat(),
        "artifact": str(artifact_path.relative_to(REPO_ROOT)),
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
        "last_scanned_run_id": state.get("last_scanned_run_id"),
        "last_pick_at": state.get("last_pick_at"),
        "last_action": last_action,
        "charter_version": CHARTER_VERSION,
    }
    try:
        session_telemetry.register_session(
            name=AGENT_NAME, machine=socket.gethostname(),
            role="E-track primitive hunter: scans Apollo organisms",
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
             "dispatched": 0, "null_tick": False, "errors": 0}
    state = load_state()

    apollo_root = find_active_apollo_root()
    _emit_event("tick_start",
                apollo_root=str(apollo_root) if apollo_root else None,
                last_scanned_run_id=state.get("last_scanned_run_id"),
                anti_silence_counter=state.get("anti_silence_counter", 0))

    if not apollo_root:
        # Upstream not configured — emit loud sentinel
        stats["action"] = "upstream_not_found"
        stats["null_tick"] = True
        ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
        artifact_path = ARTIFACT_DIR / f"upstream_not_found_{tick_started.strftime('%Y%m%dT%H%M%S')}.json"
        artifact_path.write_text(json.dumps({
            "tick_at": tick_started.isoformat(),
            "searched": [str(r) for r in APOLLO_RUN_ROOTS],
            "ask": "Atalanta requires Apollo's organism-run output. Configure APOLLO_RUN_ROOTS in agents/atalanta/daemon.py to point at the real path.",
        }, indent=2), encoding="utf-8")
        emit_log_work("atalanta_upstream_not_found",
                      summary="Apollo runs root not found; checked: " + ", ".join(str(r) for r in APOLLO_RUN_ROOTS),
                      output_path=str(artifact_path.relative_to(REPO_ROOT)),
                      success=False, error="apollo_root_not_configured")
        state["anti_silence_counter"] = state.get("anti_silence_counter", 0) + 1
        state["total_null_ticks_lifetime"] = state.get("total_null_ticks_lifetime", 0) + 1
    else:
        new_runs = scan_new_apollo_runs(apollo_root, state.get("last_scanned_run_id"))
        _emit_event("apollo_scan_complete",
                    apollo_root=str(apollo_root),
                    new_run_count=len(new_runs))
        if not new_runs:
            stats["action"] = "null_tick_no_new_apollo_runs"
            stats["null_tick"] = True
            ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
            artifact_path = ARTIFACT_DIR / f"null_{tick_started.strftime('%Y%m%dT%H%M%S')}.json"
            artifact_path.write_text(json.dumps({
                "tick_at": tick_started.isoformat(),
                "reason": "no_new_apollo_runs",
                "apollo_root": str(apollo_root.relative_to(REPO_ROOT)),
                "last_scanned_run_id": state.get("last_scanned_run_id"),
            }, indent=2), encoding="utf-8")
            state["anti_silence_counter"] = state.get("anti_silence_counter", 0) + 1
            state["total_null_ticks_lifetime"] = state.get("total_null_ticks_lifetime", 0) + 1
            emit_log_work("atalanta_null_tick",
                          summary=f"No new Apollo runs since {state.get('last_scanned_run_id')}",
                          output_path=str(artifact_path.relative_to(REPO_ROOT)))
        else:
            signals = aggregate_primitive_signals(new_runs)
            candidate = pick_candidate(signals, state)
            if not candidate:
                stats["action"] = "null_tick_no_candidate"
                stats["null_tick"] = True
                ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
                artifact_path = ARTIFACT_DIR / f"null_{tick_started.strftime('%Y%m%dT%H%M%S')}.json"
                artifact_path.write_text(json.dumps({
                    "tick_at": tick_started.isoformat(),
                    "reason": "no_candidate_passes_thresholds",
                    "signals_summary": {
                        "high_reuse_count": len(signals["high_reuse"]),
                        "unnamed_composites_count": len(signals["unnamed_composites"]),
                    },
                }, indent=2), encoding="utf-8")
                state["anti_silence_counter"] = state.get("anti_silence_counter", 0) + 1
                state["total_null_ticks_lifetime"] = state.get("total_null_ticks_lifetime", 0) + 1
                emit_log_work("atalanta_null_tick",
                              summary="New Apollo runs scanned but no candidate passed reuse/composite thresholds",
                              output_path=str(artifact_path.relative_to(REPO_ROOT)))
            else:
                if dry_run:
                    stats["action"] = "would_dispatch"
                    _emit_event("dry_run_would_dispatch",
                                kind=candidate["kind"], hash=candidate["hash"])
                else:
                    result = dispatch_candidate(candidate, signals, state)
                    if result:
                        stats["action"] = "dispatched"
                        stats["dispatched"] = 1
                        state["last_pick_at"] = result["dispatched_at"]
                        state["last_bucket_picked"] = candidate["kind"]
                        state["recently_fired_candidate_hashes"][candidate["hash"]] = result["dispatched_at"]
                        state["total_dispatched_lifetime"] = state.get("total_dispatched_lifetime", 0) + 1
                        state["anti_silence_counter"] = 0
                        emit_log_work("atalanta_dispatch",
                                      summary=f"Dispatched Type-E DR for {candidate['kind']} candidate as {result['queue_ref']} (row {result['row_id']})",
                                      output_path=result["artifact"])
                    else:
                        stats["action"] = "dispatch_failed"
                        stats["errors"] = 1
            # Update last_scanned_run_id to the max we saw
            max_id = max((r["run_id"] for r in new_runs), default=state.get("last_scanned_run_id"))
            state["last_scanned_run_id"] = max_id

    if state.get("anti_silence_counter", 0) >= ANTI_SILENCE_ALARM_THRESHOLD:
        _emit_event("self_audit_null_alarm", level="error",
                    consecutive_null=state["anti_silence_counter"])
        emit_log_work("atalanta_self_audit_null",
                      summary=f"ALARM: {state['anti_silence_counter']} consecutive null ticks. Apollo upstream likely dead or thresholds too high.",
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
    apollo_root = find_active_apollo_root()
    print(f"=== Atalanta status ===")
    print(f"  charter_version: {state.get('charter_version')}")
    print(f"  apollo_root:     {apollo_root}")
    print(f"  total_dispatched_lifetime: {state.get('total_dispatched_lifetime', 0)}")
    print(f"  total_null_ticks_lifetime: {state.get('total_null_ticks_lifetime', 0)}")
    print(f"  anti_silence_counter:      {state.get('anti_silence_counter', 0)}")
    print(f"  last_scanned_run_id:       {state.get('last_scanned_run_id')}")
    print(f"  last_pick_at:              {state.get('last_pick_at')}")
    print(f"  last_bucket_picked:        {state.get('last_bucket_picked')}")
    print(f"  lock file exists:          {PID_FILE.exists()}")


def main():
    ap = argparse.ArgumentParser(description="Atalanta — E-track primitive hunter daemon")
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
            f"  Atalanta v0.1 — E-track primitive hunter (operator={OPERATOR})",
            f"  Postgres:    {'on' if HAS_PG else 'OFF'}",
            f"  Telemetry:   {'on' if HAS_TELEMETRY else 'OFF'}",
            f"  Structlog:   {'on' if HAS_STRUCTLOG else 'OFF'}",
            f"  Mode:        {'loop @ ' + str(args.interval) + 's' if args.loop else 'once'}",
            bar,
        ])
        for line in banner.splitlines():
            _text_log.info(line)
        _emit_event("startup", pg=HAS_PG, telemetry=HAS_TELEMETRY,
                    structlog=HAS_STRUCTLOG, mode=("loop" if args.loop else "once"))
        emit_log_work("atalanta_startup",
                      summary=f"Atalanta daemon up; mode={'loop' if args.loop else 'once'} interval={args.interval}s")
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
        emit_log_work("atalanta_shutdown", summary="Atalanta daemon shutting down")
        _emit_event("shutdown")
        release_lock()


if __name__ == "__main__":
    sys.exit(main() or 0)
