"""Talos — reasoning-code specialist corpus-builder daemon (Phase 0).

See agents/talos/CHARTER.md for the full contract. Summary:
  - Scans 5 corpus streams: Hephaestus forged tools, Apollo organisms,
    Prometheus substrate code, external reasoning OSS, synthetic pairs.
  - Extracts Python-shaped reasoning code with provenance + weight tags.
  - Writes shards (gitignored) + a JSON manifest (auditable, atomically
    pointed at via corpus/manifest_latest.json).
  - Phase 0: corpus + manifest + eval scaffold ONLY. No GPU training.

Following the orchestration conventions established by Hypatia / Atalanta
/ Pheme: single-instance pid lock, session_telemetry heartbeat + log_work,
shared.structured_logging events JSONL, persisted state.json, atomic
state/manifest writes, anti-silence sentinel artifacts every tick.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import logging
import os
import re
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
CORPUS_DIR = AGENT_DIR / "corpus"
SHARDS_DIR = CORPUS_DIR / "shards"
EVAL_DIR = AGENT_DIR / "eval"
TRAINING_DIR = AGENT_DIR / "training"
PID_FILE = AGENT_DIR / "talos.pid"
STATE_FILE = STATE_DIR / "state.json"
TEXT_LOG = LOG_DIR / "talos.log"
MANIFEST_LATEST = CORPUS_DIR / "manifest_latest.json"

# External stream roots (in order tried; missing = upstream_not_found for
# that stream, daemon continues with others).
HEPHAESTUS_ROOTS = [REPO_ROOT / "agents" / "hephaestus"]
APOLLO_ROOTS = [
    REPO_ROOT / "apollo" / "runs",
    REPO_ROOT / "apollo" / "runs_v2",
    REPO_ROOT / "apollo" / "organism_runs",
]
PROMETHEUS_SUBSTRATE_ROOTS = [
    REPO_ROOT / "prometheus_math",
    REPO_ROOT / "charon" / "diagnostics",
    REPO_ROOT / "theseus" / "scripts",
]
EXTERNAL_OSS_ROOT = AGENT_DIR / "corpus" / "_staging" / "external"
SYNTHETIC_ROOT = AGENT_DIR / "corpus" / "_staging" / "synthetic"

# Stream weights (sum to 1.0; tuneable later via config.yaml)
STREAM_WEIGHTS = {
    "hephaestus_forge":      0.30,
    "apollo_organism":       0.25,
    "prometheus_substrate":  0.20,
    "external_reasoning_oss": 0.15,
    "synthetic":             0.10,
}

# Quality thresholds for extraction
MIN_FUNCTION_BODY_LINES = 3        # exclude trivial passthroughs
MAX_FUNCTION_BODY_LINES = 200      # exclude monolithic dumping-grounds
REQUIRE_DOCSTRING_FOR_OSS = True   # external sources need docs to be in
SYNTHETIC_WEIGHT_ALARM_THRESHOLD = 0.30  # see CHARTER §"Hard stops"

# Daemon settings
DEFAULT_INTERVAL_SEC = 3600
ANTI_SILENCE_ALARM_THRESHOLD = 50
CHARTER_VERSION = "v1"
AGENT_NAME = "Talos"
OPERATOR = "Ergon"


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def _setup_text_logger() -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log = logging.getLogger("talos")
    if log.handlers:
        return log
    log.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s [TALOS] %(message)s")
    sh = logging.StreamHandler(sys.stdout); sh.setFormatter(fmt); log.addHandler(sh)
    fh = logging.FileHandler(TEXT_LOG, encoding="utf-8"); fh.setFormatter(fmt); log.addHandler(fh)
    return log


_text_log = _setup_text_logger()
_evt_log = get_structured_logger("talos", log_dir=AGENT_DIR) if HAS_STRUCTLOG else None


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
                _text_log.error(f"another talos instance is alive (pid={existing_pid}); aborting")
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
        "stream_cursors": {},   # stream_name -> {last_sha, last_scanned_at}
        "corpus_size": {       # per-stream example counts
            s: 0 for s in STREAM_WEIGHTS
        },
        "total_examples_lifetime": 0,
        "anti_silence_counter": 0,
        "total_null_ticks_lifetime": 0,
        "total_ticks_lifetime": 0,
        "last_manifest_at": None,
    }


def load_state() -> dict:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if not STATE_FILE.exists():
        return _default_state()
    try:
        s = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        # Defensive: ensure all streams have cursor slots
        for stream in STREAM_WEIGHTS:
            s.setdefault("stream_cursors", {}).setdefault(stream, {})
            s.setdefault("corpus_size", {}).setdefault(stream, 0)
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
# Extraction primitives
# ---------------------------------------------------------------------------

def extract_python_functions(source_text: str, source_path: str) -> list[dict]:
    """Parse source_text as Python; return one record per function-level unit
    that passes quality filters (size band, optional docstring requirement)."""
    try:
        tree = ast.parse(source_text)
    except (SyntaxError, ValueError):
        return []
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        body_lines = (node.end_lineno or node.lineno) - node.lineno + 1
        if body_lines < MIN_FUNCTION_BODY_LINES or body_lines > MAX_FUNCTION_BODY_LINES:
            continue
        docstring = ast.get_docstring(node) or ""
        # Slice the original source for this function
        src_lines = source_text.splitlines()
        snippet = "\n".join(src_lines[node.lineno - 1: node.end_lineno or node.lineno])
        out.append({
            "function_name": node.name,
            "docstring": docstring,
            "snippet": snippet,
            "lineno": node.lineno,
            "body_lines": body_lines,
            "has_docstring": bool(docstring.strip()),
            "source_path": source_path,
        })
    return out


def _fingerprint(record: dict) -> str:
    """Stable content hash for dedup within + across streams."""
    h = hashlib.sha256()
    h.update(record["function_name"].encode())
    h.update(b"\x00")
    h.update(record["snippet"].encode("utf-8", errors="replace"))
    return h.hexdigest()[:16]


# ---------------------------------------------------------------------------
# Per-stream scanners
# ---------------------------------------------------------------------------

def _walk_python_files(roots: list[Path]) -> list[Path]:
    out = []
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob("*.py"):
            # Skip caches + obvious noise
            parts = set(p.parts)
            if "__pycache__" in parts or ".venv" in parts or "venv" in parts:
                continue
            # Skip pure orchestrators (best-effort filter)
            if p.name in ("__init__.py", "__main__.py", "setup.py", "conftest.py"):
                continue
            out.append(p)
    return out


def scan_stream(stream: str, roots: list[Path], state: dict,
                require_docstring: bool = False) -> tuple[list[dict], dict]:
    """Generic stream scanner. Returns (new_records, summary)."""
    existing_fps = set()
    cursor = state.get("stream_cursors", {}).get(stream, {})
    # Load existing fingerprints from latest shard to dedup
    shard_path = SHARDS_DIR / f"{stream}.jsonl"
    if shard_path.exists():
        try:
            for line in shard_path.read_text(encoding="utf-8").splitlines():
                try:
                    existing_fps.add(json.loads(line).get("fingerprint"))
                except Exception:
                    continue
        except Exception:
            pass

    new_records = []
    files_scanned = 0
    files_skipped_due_to_unchanged = 0
    last_seen_path_to_mtime = cursor.get("path_mtimes", {})
    new_path_to_mtime = {}
    for path in _walk_python_files(roots):
        files_scanned += 1
        rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
        try:
            mtime = path.stat().st_mtime
        except Exception:
            continue
        new_path_to_mtime[rel] = mtime
        if last_seen_path_to_mtime.get(rel) == mtime:
            files_skipped_due_to_unchanged += 1
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            _emit_event("file_read_failed", level="warning",
                        path=rel, error=str(e), stream=stream)
            continue
        funcs = extract_python_functions(text, rel)
        for fn in funcs:
            if require_docstring and not fn["has_docstring"]:
                continue
            fp = _fingerprint(fn)
            if fp in existing_fps:
                continue
            existing_fps.add(fp)
            new_records.append({
                "fingerprint": fp,
                "stream": stream,
                "weight": STREAM_WEIGHTS.get(stream, 0.0),
                "extracted_at": datetime.now(timezone.utc).isoformat(),
                **fn,
            })

    # Update cursor
    state.setdefault("stream_cursors", {})[stream] = {
        "last_scanned_at": datetime.now(timezone.utc).isoformat(),
        "path_mtimes": new_path_to_mtime,
    }
    summary = {
        "files_scanned": files_scanned,
        "files_skipped_unchanged": files_skipped_due_to_unchanged,
        "new_records": len(new_records),
        "shard_size_existing": len(existing_fps) - len(new_records),
    }
    return new_records, summary


def scan_apollo_organisms(state: dict) -> tuple[list[dict], dict]:
    """Apollo stream is special — it's not directly Python on disk.
    We compile organism primitive_sequences into pseudo-Python records.
    Phase 0: scaffold only — emit a placeholder until the proper compiler
    is built (Phase 0.5). If no Apollo runs exist, emit upstream_not_found
    via the caller."""
    apollo_root = next((r for r in APOLLO_ROOTS if r.exists()), None)
    if not apollo_root:
        return [], {"upstream_not_found": True, "searched": [str(r) for r in APOLLO_ROOTS]}
    # Phase 0: count organism files but defer compilation
    organism_files = list(apollo_root.rglob("*.json"))
    summary = {
        "apollo_root": str(apollo_root.relative_to(REPO_ROOT)),
        "organism_files_seen": len(organism_files),
        "new_records": 0,
        "phase_0_note": "compilation to Python deferred to Phase 0.5",
    }
    return [], summary


# ---------------------------------------------------------------------------
# Shard writer + manifest
# ---------------------------------------------------------------------------

def append_to_shard(stream: str, records: list[dict]) -> int:
    if not records:
        return 0
    SHARDS_DIR.mkdir(parents=True, exist_ok=True)
    shard = SHARDS_DIR / f"{stream}.jsonl"
    with shard.open("a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return len(records)


def write_manifest(state: dict, scan_summary: dict) -> Path:
    """Write manifest_<UTC-date>.json + atomically update manifest_latest.json."""
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    manifest = {
        "schema_version": 1,
        "charter_version": CHARTER_VERSION,
        "computed_at": now.isoformat(),
        "corpus_size": state.get("corpus_size", {}),
        "total_examples": sum(state.get("corpus_size", {}).values()),
        "stream_weights": STREAM_WEIGHTS,
        "stream_weights_alarm": (
            "synthetic_above_threshold"
            if STREAM_WEIGHTS.get("synthetic", 0) > SYNTHETIC_WEIGHT_ALARM_THRESHOLD
            else None
        ),
        "last_tick_summary": scan_summary,
        "shards": {
            stream: {
                "path": f"agents/talos/corpus/shards/{stream}.jsonl",
                "examples": state.get("corpus_size", {}).get(stream, 0),
                "weight": STREAM_WEIGHTS.get(stream, 0.0),
            }
            for stream in STREAM_WEIGHTS
        },
        "phase": "Phase 0 — corpus builder only; no training",
    }
    path = CORPUS_DIR / f"manifest_{now.strftime('%Y-%m-%d')}.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    tmp = MANIFEST_LATEST.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    tmp.replace(MANIFEST_LATEST)
    return path


# ---------------------------------------------------------------------------
# Heartbeat + log_work
# ---------------------------------------------------------------------------

def emit_heartbeat(state: dict, last_action: str) -> None:
    if not HAS_TELEMETRY:
        return
    status = {
        "anti_silence_counter": state.get("anti_silence_counter", 0),
        "total_ticks_lifetime": state.get("total_ticks_lifetime", 0),
        "total_null_ticks_lifetime": state.get("total_null_ticks_lifetime", 0),
        "total_examples_lifetime": state.get("total_examples_lifetime", 0),
        "corpus_size_by_stream": state.get("corpus_size", {}),
        "last_action": last_action,
        "charter_version": CHARTER_VERSION,
        "phase": "Phase 0 (corpus builder)",
    }
    try:
        session_telemetry.register_session(
            name=AGENT_NAME, machine=socket.gethostname(),
            role="Reasoning-code specialist corpus builder (Phase 0)",
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
             "examples_added": 0, "null_tick": False, "errors": 0,
             "by_stream": {}}
    state = load_state()
    state["total_ticks_lifetime"] = state.get("total_ticks_lifetime", 0) + 1

    _emit_event("tick_start",
                anti_silence_counter=state.get("anti_silence_counter", 0),
                tick_number=state["total_ticks_lifetime"])

    streams_with_new_content = 0
    upstreams_missing = []
    total_new = 0

    # Stream 1 — Hephaestus
    new_records, summary = scan_stream(
        "hephaestus_forge", HEPHAESTUS_ROOTS, state, require_docstring=False)
    stats["by_stream"]["hephaestus_forge"] = summary
    if not any(r.exists() for r in HEPHAESTUS_ROOTS):
        upstreams_missing.append("hephaestus")
    if new_records:
        added = 0 if dry_run else append_to_shard("hephaestus_forge", new_records)
        state["corpus_size"]["hephaestus_forge"] += added
        total_new += added
        streams_with_new_content += 1

    # Stream 2 — Apollo organisms (scaffold only in Phase 0)
    _, summary = scan_apollo_organisms(state)
    stats["by_stream"]["apollo_organism"] = summary
    if summary.get("upstream_not_found"):
        upstreams_missing.append("apollo")

    # Stream 3 — Prometheus substrate code
    new_records, summary = scan_stream(
        "prometheus_substrate", PROMETHEUS_SUBSTRATE_ROOTS, state,
        require_docstring=False)
    stats["by_stream"]["prometheus_substrate"] = summary
    if new_records:
        added = 0 if dry_run else append_to_shard("prometheus_substrate", new_records)
        state["corpus_size"]["prometheus_substrate"] += added
        total_new += added
        streams_with_new_content += 1

    # Stream 4 — External OSS (require docstring)
    if EXTERNAL_OSS_ROOT.exists():
        new_records, summary = scan_stream(
            "external_reasoning_oss", [EXTERNAL_OSS_ROOT], state,
            require_docstring=REQUIRE_DOCSTRING_FOR_OSS)
        stats["by_stream"]["external_reasoning_oss"] = summary
        if new_records:
            added = 0 if dry_run else append_to_shard("external_reasoning_oss", new_records)
            state["corpus_size"]["external_reasoning_oss"] += added
            total_new += added
            streams_with_new_content += 1
    else:
        stats["by_stream"]["external_reasoning_oss"] = {
            "upstream_not_found": True,
            "note": f"clone external libs into {EXTERNAL_OSS_ROOT.relative_to(REPO_ROOT)} to enable",
        }
        upstreams_missing.append("external_reasoning_oss")

    # Stream 5 — Synthetic
    if SYNTHETIC_ROOT.exists():
        new_records, summary = scan_stream(
            "synthetic", [SYNTHETIC_ROOT], state, require_docstring=False)
        stats["by_stream"]["synthetic"] = summary
        if new_records:
            added = 0 if dry_run else append_to_shard("synthetic", new_records)
            state["corpus_size"]["synthetic"] += added
            total_new += added
            streams_with_new_content += 1
    else:
        stats["by_stream"]["synthetic"] = {
            "upstream_not_found": True,
            "note": f"place synthetic pairs into {SYNTHETIC_ROOT.relative_to(REPO_ROOT)} to enable",
        }

    stats["examples_added"] = total_new
    state["total_examples_lifetime"] = state.get("total_examples_lifetime", 0) + total_new

    # Anti-silence + manifest publication
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    if total_new > 0:
        stats["action"] = "corpus_grew"
        state["anti_silence_counter"] = 0
        if not dry_run:
            manifest_path = write_manifest(state, stats)
            state["last_manifest_at"] = datetime.now(timezone.utc).isoformat()
            emit_log_work(
                "talos_corpus_growth",
                summary=(f"Corpus grew by {total_new} examples across "
                         f"{streams_with_new_content} stream(s). Total: "
                         f"{sum(state['corpus_size'].values())}. Streams: "
                         f"{state['corpus_size']}"),
                output_path=str(manifest_path.relative_to(REPO_ROOT)),
            )
        artifact_path = ARTIFACT_DIR / f"tick_{tick_started.strftime('%Y%m%dT%H%M%S')}.json"
        artifact_path.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    elif upstreams_missing and not state.get("corpus_size", {}).get("hephaestus_forge"):
        # Only fire upstream_not_found if we have NO corpus yet AND streams are
        # missing; otherwise it's a normal null-tick (no new content)
        stats["action"] = "upstream_not_found"
        stats["null_tick"] = True
        state["anti_silence_counter"] = state.get("anti_silence_counter", 0) + 1
        state["total_null_ticks_lifetime"] = state.get("total_null_ticks_lifetime", 0) + 1
        artifact_path = ARTIFACT_DIR / f"upstream_not_found_{tick_started.strftime('%Y%m%dT%H%M%S')}.json"
        artifact_path.write_text(json.dumps({
            "tick_at": tick_started.isoformat(),
            "upstreams_missing": upstreams_missing,
            "ask": "Configure stream roots in agents/talos/daemon.py or place "
                   "content under agents/talos/corpus/_staging/.",
        }, indent=2), encoding="utf-8")
        emit_log_work("talos_upstream_not_found",
                      summary=f"No corpus yet; upstreams missing: {upstreams_missing}",
                      output_path=str(artifact_path.relative_to(REPO_ROOT)),
                      success=False, error="upstreams_not_found")
    else:
        stats["action"] = "null_tick_no_new_content"
        stats["null_tick"] = True
        state["anti_silence_counter"] = state.get("anti_silence_counter", 0) + 1
        state["total_null_ticks_lifetime"] = state.get("total_null_ticks_lifetime", 0) + 1
        artifact_path = ARTIFACT_DIR / f"null_{tick_started.strftime('%Y%m%dT%H%M%S')}.json"
        artifact_path.write_text(json.dumps({
            "tick_at": tick_started.isoformat(),
            "reason": "no_new_content_in_any_stream",
            "corpus_size": state.get("corpus_size", {}),
            "by_stream": stats["by_stream"],
        }, indent=2), encoding="utf-8")
        emit_log_work("talos_null_tick",
                      summary=f"No new content in any stream. Corpus: {sum(state.get('corpus_size',{}).values())} examples.",
                      output_path=str(artifact_path.relative_to(REPO_ROOT)))

    if state.get("anti_silence_counter", 0) >= ANTI_SILENCE_ALARM_THRESHOLD:
        _emit_event("self_audit_null_alarm", level="error",
                    consecutive_null=state["anti_silence_counter"])
        emit_log_work("talos_self_audit_null",
                      summary=f"ALARM: {state['anti_silence_counter']} consecutive null ticks.",
                      success=False, error="anti_silence_threshold_exceeded")

    # Dry-run must not persist state mutations — otherwise a dry run stamps
    # path-mtime cursors and subsequent real runs see all files as "unchanged".
    if not dry_run:
        save_state(state)
    emit_heartbeat(state, last_action=stats["action"] or "unknown")
    _emit_event("tick_end",
                action=stats["action"], examples_added=stats["examples_added"],
                null_tick=stats["null_tick"], total_examples_lifetime=state["total_examples_lifetime"])
    return stats


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def print_status() -> None:
    state = load_state()
    print(f"=== Talos status ===")
    print(f"  charter_version: {state.get('charter_version')}")
    print(f"  phase:           Phase 0 (corpus builder)")
    print(f"  total_examples_lifetime: {state.get('total_examples_lifetime', 0)}")
    print(f"  total_ticks_lifetime:    {state.get('total_ticks_lifetime', 0)}")
    print(f"  total_null_ticks:        {state.get('total_null_ticks_lifetime', 0)}")
    print(f"  anti_silence_counter:    {state.get('anti_silence_counter', 0)}")
    print(f"  last_manifest_at:        {state.get('last_manifest_at')}")
    print(f"  corpus_size by stream:")
    for stream, n in state.get("corpus_size", {}).items():
        w = STREAM_WEIGHTS.get(stream, 0.0)
        print(f"    {stream:24s}  {n:6d}  (weight {w})")
    print(f"  manifest_latest exists:  {MANIFEST_LATEST.exists()}")


def print_manifest() -> None:
    if not MANIFEST_LATEST.exists():
        print("(no manifest yet — daemon hasn't completed a productive tick)")
        return
    print(MANIFEST_LATEST.read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser(description="Talos — reasoning-code specialist corpus builder (Phase 0)")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("status", help="print current state and exit")
    sub.add_parser("manifest", help="print latest corpus manifest")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--interval", type=int, default=DEFAULT_INTERVAL_SEC)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.cmd == "status":
        print_status()
        return 0
    if args.cmd == "manifest":
        print_manifest()
        return 0

    if not acquire_lock():
        return 2
    try:
        bar = "=" * 60
        banner = "\n".join([
            bar,
            f"  Talos v0.1 — reasoning-code specialist corpus builder (operator={OPERATOR})",
            f"  Phase:       0 (corpus only; no GPU training)",
            f"  Telemetry:   {'on' if HAS_TELEMETRY else 'OFF'}",
            f"  Structlog:   {'on' if HAS_STRUCTLOG else 'OFF'}",
            f"  Mode:        {'loop @ ' + str(args.interval) + 's' if args.loop else 'once'}",
            bar,
        ])
        for line in banner.splitlines():
            _text_log.info(line)
        _emit_event("startup", telemetry=HAS_TELEMETRY, structlog=HAS_STRUCTLOG,
                    mode=("loop" if args.loop else "once"))
        emit_log_work("talos_startup",
                      summary=f"Talos daemon up; mode={'loop' if args.loop else 'once'} interval={args.interval}s")
        if args.once or not args.loop:
            stats = run_tick(dry_run=args.dry_run)
            _text_log.info(f"tick: action={stats['action']} added={stats['examples_added']} null={stats['null_tick']}")
            return 0
        while True:
            try:
                stats = run_tick(dry_run=args.dry_run)
                _text_log.info(f"tick: action={stats['action']} added={stats['examples_added']} null={stats['null_tick']}")
            except Exception:
                _emit_event("tick_uncaught_exception", level="error")
                _text_log.exception("uncaught exception in tick")
            time.sleep(max(1, args.interval))
    finally:
        emit_log_work("talos_shutdown", summary="Talos daemon shutting down")
        _emit_event("shutdown")
        release_lock()


if __name__ == "__main__":
    sys.exit(main() or 0)
