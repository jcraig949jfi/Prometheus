"""
harmonia_audit.py -- daily 4-criterion swarm-health audit for the
Harmonia auto-promotion swarm (Phase 1.5 patch 5).

Different shape from the weekly-maturation roll-up
(`D:\\Prometheus\\scripts\\harmonia_weekly_report.py`, which is metrics-
trends over 7 days). This script is health-focused: per agent it asks

  1. Orchestration compliance -- is the agent's pipeline/daemon importable,
     does it subclass HarmoniaAgent, is it quiesced, is it emitting events
     at all?
  2. Structured logging -- 24h event / yield / tick counts per agent.
  3. Backlog or activity -- agent-specific backlog signal + count of
     artifacts modified in the last 24h.
  4. Self-generation capacity -- always-available fallback source per
     agent, with a note when the fallback pool is exhausted or stale.

It also emits a diminishing-returns flag per agent (artifacts that are
functionally duplicates within the window) and rolls up a recommended-
cadence-changes section the conductor can act on.

Reads (all read-only -- this audit never mutates state):
- `D:\\Prometheus\\harmonia\\agents\\_logs\\events.jsonl`
- `D:\\Prometheus\\harmonia\\agents\\_logs\\yields.jsonl`
- `D:\\Prometheus\\harmonia\\agents\\_logs\\ticks.jsonl`
- `D:\\Prometheus\\harmonia\\agents\\_swarm.pid`
- `D:\\Prometheus\\harmonia\\agents\\<name>\\daemon.py` (importability check)
- `D:\\Prometheus\\harmonia\\agents\\<name>\\_pipeline.py` (optional)
- `D:\\Prometheus\\harmonia\\agents\\<name>\\state\\*.json` (backlog signals)
- `D:\\Prometheus\\harmonia\\agents\\<name>\\artifacts\\*` (activity signals)
- `D:\\Prometheus\\harmonia\\memory\\symbols\\*.md` (Phylax backlog)
- `D:\\Prometheus\\harmonia\\memory\\frontier_specimen_state.md` (Telos)

Writes:
- `D:\\Prometheus\\harmonia\\agents\\_logs\\swarm_audit_<UTC>.md`
- one `weekly_report_emitted` event with event_data tagging this as an
  audit (no new event class introduced, per spec).

Usage:
    python scripts/harmonia_audit.py                # default 24h, write + stdout
    python scripts/harmonia_audit.py --window 48h   # custom window
    python scripts/harmonia_audit.py --json         # machine-readable
    python scripts/harmonia_audit.py --stdout       # do not write file
    python scripts/harmonia_audit.py --agent iris   # restrict to one agent
"""
from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

_SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = _SCRIPT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from harmonia.agents._scorer import (  # noqa: E402
    emit_event,
    read_yields,
    consolidate_yields,
    EVENT_WEEKLY_REPORT_EMITTED,
    YIELDS_JSONL,
    EVENTS_JSONL,
    LOGS_DIR,
    AGENTS_DIR,
)

AGENT_NAMES = ("phylax", "sophia", "iris", "argos", "telos")
TICKS_JSONL = LOGS_DIR / "ticks.jsonl"
PID_FILE = AGENTS_DIR / "_swarm.pid"
SYMBOLS_DIR = REPO_ROOT / "harmonia" / "memory" / "symbols"
FRONTIER_STATE = REPO_ROOT / "harmonia" / "memory" / "frontier_specimen_state.md"

# Sophia's universe of (operator, specimen) pairs is bounded; the 140
# figure is the design ceiling for the v1 toolkit (see Sophia CHARTER).
SOPHIA_PAIR_CEILING = 140

# Diminishing-returns thresholds (per agent).
DR_RATIO_WARN = 0.50          # >= 50% duplicates -> flag
TELOS_FID_FLOOR = 2           # <= 2 distinct F-IDs in window -> flag
TELOS_STALLED_THRESHOLD = 5   # F-IDs with >=5 entries in proposed_history -> stalled

# Cadence recommendations (stride = 1-in-N rotation slots) when DR fires.
CADENCE_STRIDE_DR = {"sophia": 6, "telos": 4, "iris": 3}


# ---------------------------------------------------------------------------
# CLI parsing
# ---------------------------------------------------------------------------

def _parse_window(window: str) -> timedelta:
    m = re.fullmatch(r"(\d+)\s*([hdwm])", window.lower().strip())
    if not m:
        raise SystemExit(
            f"bad --window value '{window}'; expected like '24h', '48h', '7d'"
        )
    n = int(m.group(1))
    unit = m.group(2)
    return {
        "h": timedelta(hours=n),
        "d": timedelta(days=n),
        "w": timedelta(weeks=n),
        "m": timedelta(days=30 * n),
    }[unit]


def _build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Daily 4-criterion swarm-health audit for the Harmonia swarm. "
            "Writes a swarm_audit_<utc>.md under "
            "D:\\Prometheus\\harmonia\\agents\\_logs\\ and emits one "
            "weekly_report_emitted event tagged with kind=swarm_audit."
        )
    )
    p.add_argument("--window", default="24h",
                   help="lookback window (default: 24h)")
    p.add_argument("--json", action="store_true",
                   help="emit machine-readable JSON instead of markdown")
    p.add_argument("--stdout", action="store_true",
                   help="print to stdout only; do not write a swarm_audit_*.md")
    p.add_argument("--agent", default=None, choices=list(AGENT_NAMES),
                   help="restrict scorecards to a single agent")
    p.add_argument("--no-emit-event", action="store_true",
                   help="skip emitting the audit event (use when previewing)")
    return p


# ---------------------------------------------------------------------------
# Log readers (all graceful on missing files)
# ---------------------------------------------------------------------------

def _read_jsonl(path: Path, cutoff: Optional[datetime],
                ts_field: str = "ts") -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                if cutoff is not None:
                    ts_raw = r.get(ts_field) or r.get("started_at")
                    if not ts_raw:
                        continue
                    try:
                        ts = datetime.fromisoformat(ts_raw)
                        if ts < cutoff:
                            continue
                    except Exception:
                        continue
                rows.append(r)
    except Exception as e:
        print(f"[harmonia_audit] read {path.name} failed: {e}", file=sys.stderr)
    return rows


def _read_events(cutoff: Optional[datetime]) -> list[dict]:
    return _read_jsonl(EVENTS_JSONL, cutoff, ts_field="ts")


def _read_ticks(cutoff: Optional[datetime]) -> list[dict]:
    return _read_jsonl(TICKS_JSONL, cutoff, ts_field="started_at")


def _lifetime_tick_count() -> int:
    if not TICKS_JSONL.exists():
        return 0
    try:
        with open(TICKS_JSONL, "r", encoding="utf-8") as f:
            return sum(1 for line in f if line.strip())
    except Exception:
        return 0


# ---------------------------------------------------------------------------
# Daemon liveness (cross-platform; mirrors harmonia_summary.py)
# ---------------------------------------------------------------------------

def _daemon_status() -> dict:
    out: dict = {"alive": False, "pid": None, "age_minutes": None}
    if not PID_FILE.exists():
        return out
    try:
        pid = int(PID_FILE.read_text(encoding="utf-8").strip())
    except Exception:
        return out
    out["pid"] = pid
    if os.name == "nt":
        try:
            import ctypes
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            h = ctypes.windll.kernel32.OpenProcess(
                PROCESS_QUERY_LIMITED_INFORMATION, False, pid
            )
            if not h:
                return out
            exit_code = ctypes.c_ulong()
            ok = ctypes.windll.kernel32.GetExitCodeProcess(h, ctypes.byref(exit_code))
            ctypes.windll.kernel32.CloseHandle(h)
            out["alive"] = bool(ok) and exit_code.value == 259
        except Exception:
            return out
        try:
            proc = subprocess.run(
                ["wmic", "process", "where", f"ProcessId={pid}",
                 "get", "CreationDate", "/value"],
                capture_output=True, text=True, timeout=10, check=False,
            )
            for line in proc.stdout.splitlines():
                if line.startswith("CreationDate="):
                    ts = line.split("=", 1)[1].strip()
                    if ts and len(ts) >= 14:
                        dt = datetime.strptime(ts[:14], "%Y%m%d%H%M%S")
                        out["age_minutes"] = int(
                            (datetime.now() - dt).total_seconds() / 60
                        )
        except Exception:
            pass
    else:
        try:
            os.kill(pid, 0)
            out["alive"] = True
        except OSError:
            pass
    return out


# ---------------------------------------------------------------------------
# Criterion 1 -- orchestration compliance
# ---------------------------------------------------------------------------

def _check_orchestration(name: str, events_24h: list[dict]) -> dict:
    """Returns {importable, subclasses_base, emits_events, quiesced, ok, notes}.

    Checks both `_pipeline.py` (if present) and `daemon.py`. Either one
    subclassing HarmoniaAgent satisfies the base-class gate.
    """
    out: dict = {
        "importable": False,
        "has_pipeline_module": False,
        "subclasses_base": False,
        "emits_events": False,
        "quiesced": False,
        "ok": False,
        "notes": [],
    }
    agent_dir = AGENTS_DIR / name
    daemon_py = agent_dir / "daemon.py"
    pipeline_py = agent_dir / "_pipeline.py"

    out["has_pipeline_module"] = pipeline_py.exists()

    # Quiesced flag (state/quiesced.json)
    quiesce_flag = agent_dir / "state" / "quiesced.json"
    out["quiesced"] = quiesce_flag.exists()

    # Try to import daemon module to verify HarmoniaAgent subclassing.
    if daemon_py.exists():
        try:
            mod = importlib.import_module(f"harmonia.agents.{name}.daemon")
            out["importable"] = True
            try:
                from harmonia.agents._base import HarmoniaAgent
                for attr in dir(mod):
                    obj = getattr(mod, attr, None)
                    if (
                        isinstance(obj, type)
                        and obj is not HarmoniaAgent
                        and issubclass(obj, HarmoniaAgent)
                    ):
                        out["subclasses_base"] = True
                        break
            except Exception as e:
                out["notes"].append(f"base-class probe failed: {type(e).__name__}")
        except Exception as e:
            out["notes"].append(f"daemon import failed: {type(e).__name__}: {str(e)[:80]}")
    else:
        out["notes"].append("no daemon.py found")

    # Independently try _pipeline.py if it exists (Iris currently).
    if pipeline_py.exists():
        try:
            importlib.import_module(f"harmonia.agents.{name}._pipeline")
        except Exception as e:
            out["notes"].append(f"_pipeline import failed: {type(e).__name__}")

    out["emits_events"] = any(
        ev.get("agent") == name for ev in events_24h
    )

    # Aggregate verdict: importable AND subclasses_base AND not quiesced.
    out["ok"] = bool(
        out["importable"] and out["subclasses_base"] and not out["quiesced"]
    )
    return out


# ---------------------------------------------------------------------------
# Criterion 2 -- structured logging
# ---------------------------------------------------------------------------

def _logging_stats(name: str, events_24h: list[dict],
                   yields_24h: list[dict],
                   ticks_24h: list[dict]) -> dict:
    ev_by_class: Counter = Counter()
    n_events = 0
    for ev in events_24h:
        if ev.get("agent") != name:
            continue
        n_events += 1
        ev_by_class[ev.get("event_class") or "unknown"] += 1

    n_yields = sum(1 for y in yields_24h if y.get("agent") == name)
    n_ticks = sum(1 for t in ticks_24h if t.get("agent") == name)
    return {
        "events": n_events,
        "events_by_class": dict(ev_by_class),
        "yields": n_yields,
        "ticks": n_ticks,
    }


# ---------------------------------------------------------------------------
# Criterion 3 -- backlog / activity
# ---------------------------------------------------------------------------

def _load_state(name: str, key: str) -> Any:
    p = AGENTS_DIR / name / "state" / f"{key}.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _count_symbols_promoted() -> int:
    if not SYMBOLS_DIR.exists():
        return 0
    try:
        return sum(1 for p in SYMBOLS_DIR.iterdir()
                   if p.is_file() and p.suffix.lower() == ".md")
    except Exception:
        return 0


def _count_recent_artifacts(name: str, cutoff: Optional[datetime]) -> int:
    d = AGENTS_DIR / name / "artifacts"
    if not d.exists():
        return 0
    if cutoff is None:
        try:
            return sum(1 for p in d.iterdir() if p.is_file())
        except Exception:
            return 0
    cutoff_ts = cutoff.timestamp()
    n = 0
    try:
        for p in d.iterdir():
            if not p.is_file():
                continue
            try:
                if p.stat().st_mtime >= cutoff_ts:
                    n += 1
            except Exception:
                continue
    except Exception:
        pass
    return n


def _telos_stalled_fids(threshold: int = TELOS_STALLED_THRESHOLD) -> int:
    ph = _load_state("telos", "proposed_history") or {}
    if not isinstance(ph, dict):
        return 0
    return sum(1 for fid, lst in ph.items()
               if isinstance(lst, list) and len(lst) >= threshold)


def _backlog_signal(name: str) -> dict:
    """Per-agent backlog / progress signal. Returns
    {label, value, denom (optional), unaudited (optional)}."""
    if name == "phylax":
        promoted = _count_symbols_promoted()
        last_audit = _load_state("phylax", "symbol_last_audit") or {}
        if not isinstance(last_audit, dict):
            last_audit = {}
        unaudited = max(0, promoted - len(last_audit))
        return {
            "label": "unaudited symbols",
            "value": unaudited,
            "denom": promoted,
        }
    if name == "sophia":
        tried = _load_state("sophia", "tried_pairs") or []
        try:
            tried_n = len(tried)
        except Exception:
            tried_n = 0
        return {
            "label": "untried pairs",
            "value": max(0, SOPHIA_PAIR_CEILING - tried_n),
            "denom": SOPHIA_PAIR_CEILING,
        }
    if name == "iris":
        clusters = _load_state("iris", "clusters") or {}
        if not isinstance(clusters, dict):
            clusters = {}
        n_total = len(clusters)
        n_ripe = 0
        for v in clusters.values():
            files: Any = None
            if isinstance(v, dict):
                files = v.get("distinct_files") or v.get("files")
            try:
                if files is not None and len(files) >= 3:
                    n_ripe += 1
            except Exception:
                continue
        return {
            "label": "clusters tracked",
            "value": n_total,
            "ripe_clusters": n_ripe,
        }
    if name == "argos":
        lens_history = _load_state("argos", "lens_history") or {}
        try:
            lens_n = len(lens_history) if isinstance(lens_history, (dict, list)) else 0
        except Exception:
            lens_n = 0
        return {
            "label": "problems with applied lenses",
            "value": lens_n,
        }
    if name == "telos":
        stalled = _telos_stalled_fids()
        return {
            "label": f"stalled F-IDs (>={TELOS_STALLED_THRESHOLD} proposals)",
            "value": stalled,
        }
    return {"label": "n/a", "value": 0}


# ---------------------------------------------------------------------------
# Criterion 4 -- self-generation capacity
# ---------------------------------------------------------------------------

def _self_gen_capacity(name: str, ticks_24h: list[dict]) -> dict:
    """Per-agent always-available fallback source. Reports OK with a note
    if the pool is degraded."""
    if name == "phylax":
        return {"ok": True, "fallback": "re-audit crawl", "note": ""}
    if name == "sophia":
        # Sophia falls back to meta_expand_toolkit when tried_pairs grows.
        tried = _load_state("sophia", "tried_pairs") or []
        try:
            n = len(tried)
        except Exception:
            n = 0
        if n >= SOPHIA_PAIR_CEILING:
            return {
                "ok": True,
                "fallback": "meta_expand_toolkit",
                "note": (
                    f"pair grid saturated ({n}/{SOPHIA_PAIR_CEILING}); "
                    "fallback meta-tasks may be diminishing"
                ),
            }
        return {"ok": True, "fallback": "meta_expand_toolkit", "note": ""}
    if name == "iris":
        return {"ok": True, "fallback": "corpus rotation", "note": ""}
    if name == "argos":
        dr_seeded = _load_state("argos", "dr_seeded") or []
        seeded_n = len(dr_seeded) if isinstance(dr_seeded, list) else 0
        # Argos's pending_problem_seeds queue size is reported by tick stats.
        backlog_remaining: Optional[int] = None
        for t in reversed(ticks_24h):
            if t.get("agent") != "argos":
                continue
            s = t.get("stats") or {}
            br = s.get("backlog_remaining")
            if isinstance(br, int):
                backlog_remaining = br
                break
        note = ""
        if backlog_remaining is not None and backlog_remaining < 50:
            note = f"pending_problem_seeds running low: {backlog_remaining} remaining"
        return {
            "ok": True,
            "fallback": "pending_problem_seeds + DR enqueue",
            "note": note or f"DR seeded lifetime={seeded_n}",
        }
    if name == "telos":
        ph = _load_state("telos", "proposed_history") or {}
        if not isinstance(ph, dict):
            ph = {}
        n_fids = len(ph)
        note = ""
        if n_fids == 0:
            note = "no FIDs in proposed_history; killed-revisit + NEGATIVE_SPACE_MAPPED pools empty"
        elif n_fids <= TELOS_FID_FLOOR:
            note = (
                f"only {n_fids} FID(s) cycled: "
                + ", ".join(sorted(ph.keys()))
                + "; weighted round-robin patch needed"
            )
        return {
            "ok": True,
            "fallback": "killed-revisit + NEGATIVE_SPACE_MAPPED",
            "note": note,
        }
    return {"ok": True, "fallback": "n/a", "note": ""}


# ---------------------------------------------------------------------------
# Diminishing-returns detector
# ---------------------------------------------------------------------------

def _diminishing_returns(name: str, cutoff: Optional[datetime]) -> dict:
    """Per-agent DR flag. Returns {flag, ratio, label, detail}."""
    d = AGENTS_DIR / name / "artifacts"
    if not d.exists():
        return {"flag": False, "ratio": None, "label": "n/a", "detail": "no artifacts dir"}
    cutoff_ts = cutoff.timestamp() if cutoff is not None else 0.0
    in_window: list[str] = []
    try:
        for p in d.iterdir():
            if not p.is_file():
                continue
            try:
                if p.stat().st_mtime >= cutoff_ts:
                    in_window.append(p.name)
            except Exception:
                continue
    except Exception:
        pass
    total = len(in_window)
    if total == 0:
        return {"flag": False, "ratio": None, "label": "no artifacts in window",
                "detail": ""}

    if name == "sophia":
        n_dup = sum(1 for fn in in_window if fn.startswith("meta_expand_toolkit_"))
        ratio = n_dup / total
        return {
            "flag": ratio >= DR_RATIO_WARN,
            "ratio": ratio,
            "label": "meta_expand_toolkit duplicate-rate",
            "detail": f"{n_dup}/{total} artifacts in window are meta_expand_toolkit_*.md",
        }
    if name == "iris":
        n_dup = sum(1 for fn in in_window if fn.startswith("scan_tick_"))
        ratio = n_dup / total
        return {
            "flag": ratio >= DR_RATIO_WARN,
            "ratio": ratio,
            "label": "scan_tick duplicate-rate",
            "detail": f"{n_dup}/{total} artifacts in window are scan_tick_*.md",
        }
    if name == "telos":
        fid_re = re.compile(r"^revive_(F\d+[a-z]?)_")
        fids: set[str] = set()
        for fn in in_window:
            m = fid_re.match(fn)
            if m:
                fids.add(m.group(1))
        flag = len(fids) > 0 and len(fids) <= TELOS_FID_FLOOR
        return {
            "flag": flag,
            "ratio": None,
            "label": "distinct F-ID coverage",
            "detail": (
                f"{len(fids)} distinct F-ID(s) in window: "
                + (", ".join(sorted(fids)) if fids else "none")
                + (f" -- <= {TELOS_FID_FLOOR}, narrow coverage" if flag else "")
            ),
        }
    return {
        "flag": False,
        "ratio": None,
        "label": "no DR detector",
        "detail": "each artifact treated as distinct work",
    }


# ---------------------------------------------------------------------------
# Per-agent assembly
# ---------------------------------------------------------------------------

def _agent_last_tick(name: str, ticks_24h: list[dict]) -> Optional[dict]:
    for t in reversed(ticks_24h):
        if t.get("agent") == name:
            return t
    return None


def assemble_agent_card(name: str, window_hours: float,
                        events_24h: list[dict], yields_24h: list[dict],
                        ticks_24h: list[dict],
                        cutoff: Optional[datetime]) -> dict:
    orch = _check_orchestration(name, events_24h)
    logs = _logging_stats(name, events_24h, yields_24h, ticks_24h)
    backlog = _backlog_signal(name)
    recent_artifacts = _count_recent_artifacts(name, cutoff)
    selfgen = _self_gen_capacity(name, ticks_24h)
    dr = _diminishing_returns(name, cutoff)
    last_tick = _agent_last_tick(name, ticks_24h)
    return {
        "name": name,
        "window_hours": window_hours,
        "orch": orch,
        "logs": logs,
        "backlog": backlog,
        "recent_artifacts": recent_artifacts,
        "selfgen": selfgen,
        "dr": dr,
        "last_tick": last_tick,
    }


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

def _fmt_pct(x: Optional[float]) -> str:
    if x is None:
        return "-"
    return f"{x * 100:.0f}%"


def _backlog_brief(card: dict) -> str:
    b = card["backlog"]
    label = b.get("label", "n/a")
    val = b.get("value", 0)
    parts = [f"{val} {label}"]
    if "denom" in b and b["denom"]:
        parts[-1] = f"{val} {label} (of {b['denom']})"
    if "ripe_clusters" in b:
        parts.append(f"{b['ripe_clusters']} ripe (>=3 distinct files)")
    parts.append(f"{card['recent_artifacts']} recent artifacts")
    return " / ".join(parts)


def _orch_brief(card: dict) -> str:
    o = card["orch"]
    if o.get("quiesced"):
        return "QUIESCED"
    bits = []
    if not o.get("importable"):
        bits.append("import-fail")
    if not o.get("subclasses_base"):
        bits.append("not-subclassed")
    if not o.get("emits_events"):
        bits.append("no-events")
    if not bits:
        return "OK"
    return "WARN: " + ",".join(bits)


def _logs_brief(card: dict) -> str:
    lg = card["logs"]
    return f"{lg['events']} events / {lg['yields']} yields / {lg['ticks']} ticks"


def _selfgen_brief(card: dict) -> str:
    sg = card["selfgen"]
    base = f"OK ({sg['fallback']})"
    if sg.get("note"):
        base += f" -- {sg['note']}"
    return base


def _dr_brief(card: dict) -> str:
    dr = card["dr"]
    if dr["flag"]:
        if dr["ratio"] is not None:
            return f"YES ({_fmt_pct(dr['ratio'])} {dr['label']})"
        return f"YES ({dr['detail']})"
    if dr.get("ratio") is not None:
        return f"No ({_fmt_pct(dr['ratio'])})"
    return "No"


def _header_section(now: datetime, daemon: dict, lifetime_ticks: int,
                    swarm_events_24h: int, swarm_yields_24h: int,
                    window_hours: float) -> list[str]:
    lines = [
        f"# Harmonia swarm audit -- {now.strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
        f"**Window:** last {window_hours:g}h  "
        f"**Generated:** `{now.isoformat()}`",
        "",
    ]
    if daemon["alive"]:
        age = (f"{daemon['age_minutes']} min"
               if daemon.get("age_minutes") is not None else "?")
        lines.append(
            f"**Daemon:** PID {daemon['pid']} ALIVE ({age})"
        )
    else:
        pid_disp = daemon.get("pid") if daemon.get("pid") else "(no pid file)"
        lines.append(f"**Daemon:** {pid_disp} DEAD -- restart with:")
        lines.append("")
        lines.append("```powershell")
        lines.append(
            "Start-Process -FilePath \"D:\\Prometheus\\scripts\\"
            "harmonia_loop_launch.bat\" -WindowStyle Hidden"
        )
        lines.append("```")
    lines.append(
        f"**Lifetime ticks:** {lifetime_ticks}  "
        f"**Events {window_hours:g}h:** {swarm_events_24h}  "
        f"**Yields {window_hours:g}h:** {swarm_yields_24h}"
    )
    lines.append("")
    return lines


def _scorecard_table(cards: list[dict]) -> list[str]:
    lines = [
        "## Per-agent scorecard (4 criteria)",
        "",
        "| Agent | Orch | Logs | Backlog / Activity | Self-gen | Diminishing returns |",
        "|---|---|---|---|---|---|",
    ]
    for c in cards:
        lines.append(
            f"| {c['name']} | {_orch_brief(c)} | {_logs_brief(c)} "
            f"| {_backlog_brief(c)} | {_selfgen_brief(c)} | {_dr_brief(c)} |"
        )
    lines.append("")
    return lines


def _agent_detail(card: dict) -> list[str]:
    name = card["name"]
    o = card["orch"]
    lt = card["last_tick"]
    lines = [f"### {name.capitalize()}", ""]
    if lt is not None:
        try:
            started = datetime.fromisoformat(lt["started_at"])
            last_str = started.strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception:
            last_str = lt.get("started_at", "?")
        elapsed = lt.get("elapsed_sec", "?")
        stats = lt.get("stats") or {}
        errors = stats.get("errors", 0)
        lines.append(
            f"- Last tick: {last_str}, elapsed {elapsed}s, errors={errors}"
        )
        keys = [k for k in stats.keys()
                if k not in ("tick_id", "elapsed_sec")][:8]
        if keys:
            lines.append("- Recent stats keys: " + ", ".join(keys))
    else:
        lines.append("- Last tick: no ticks in window")
    lines.append(f"- Importable: {o['importable']}  "
                 f"Subclasses HarmoniaAgent: {o['subclasses_base']}  "
                 f"Has _pipeline.py: {o['has_pipeline_module']}  "
                 f"Quiesced: {'Yes' if o['quiesced'] else 'No'}")
    if o.get("notes"):
        for n in o["notes"]:
            lines.append(f"  - note: {n}")
    lines.append(f"- Logging: {_logs_brief(card)}")
    if card["logs"]["events_by_class"]:
        bits = ", ".join(
            f"{k}={v}" for k, v in
            sorted(card["logs"]["events_by_class"].items(),
                   key=lambda kv: -kv[1])
        )
        lines.append(f"  - event_class breakdown: {bits}")
    lines.append(f"- Backlog: {_backlog_brief(card)}")
    lines.append(f"- Self-gen: {_selfgen_brief(card)}")
    dr = card["dr"]
    if dr["flag"]:
        lines.append(f"- **DIMINISHING RETURNS FLAG:** {dr['detail']}")
    else:
        lines.append(f"- Diminishing returns: No -- {dr['detail']}")
    lines.append("")
    return lines


def _dr_summary(cards: list[dict]) -> list[str]:
    lines = ["## Diminishing-returns summary", ""]
    any_flag = False
    for c in cards:
        dr = c["dr"]
        if not dr["flag"]:
            continue
        any_flag = True
        if dr["ratio"] is not None:
            lines.append(
                f"- {c['name']}: {_fmt_pct(dr['ratio'])} {dr['label']} -- "
                f"{dr['detail']}"
            )
        else:
            lines.append(f"- {c['name']}: {dr['detail']}")
    if not any_flag:
        lines.append("- (no agent currently exceeds the duplicate-rate threshold)")
    lines.append("")
    return lines


def _cadence_recommendations(cards: list[dict]) -> list[str]:
    lines = ["## Recommended cadence changes", ""]
    any_rec = False
    for c in cards:
        if not c["dr"]["flag"]:
            continue
        stride = CADENCE_STRIDE_DR.get(c["name"])
        if not stride:
            continue
        any_rec = True
        lines.append(
            f"- {c['name']}: stride {stride} (1-in-{stride} rotation slot) "
            "until DR signal clears"
        )
    if not any_rec:
        lines.append("- (no cadence changes recommended)")
    lines.append("")
    return lines


def _health_alerts(cards: list[dict], daemon: dict) -> list[str]:
    lines = ["## Health alerts", ""]
    alerts: list[str] = []
    if not daemon["alive"]:
        alerts.append("Swarm daemon is DEAD; ticks have stopped")
    for c in cards:
        o = c["orch"]
        if o.get("quiesced"):
            alerts.append(f"{c['name']} is QUIESCED")
        if not o["importable"]:
            alerts.append(f"{c['name']}: daemon module is not importable")
        elif not o["subclasses_base"]:
            alerts.append(f"{c['name']}: no HarmoniaAgent subclass detected")
        if c["logs"]["events"] == 0 and c["logs"]["ticks"] == 0:
            alerts.append(
                f"{c['name']}: no events AND no ticks in window -- "
                "agent may have stopped running"
            )
        sg_note = c["selfgen"].get("note") or ""
        if "empty" in sg_note or "running low" in sg_note:
            alerts.append(f"{c['name']}: self-gen note -- {sg_note}")
    if not alerts:
        lines.append("- (nothing -- all agents nominal)")
    else:
        for a in alerts:
            lines.append(f"- {a}")
    lines.append("")
    return lines


def _source_data() -> list[str]:
    return [
        "## Source data",
        "",
        f"- `{EVENTS_JSONL}`",
        f"- `{YIELDS_JSONL}`",
        f"- `{TICKS_JSONL}`",
        f"- `{PID_FILE}`",
        f"- `{AGENTS_DIR}\\<agent>\\state\\*.json`",
        f"- `{AGENTS_DIR}\\<agent>\\artifacts\\*`",
        f"- `{SYMBOLS_DIR}\\*.md`",
        f"- `{FRONTIER_STATE}`",
        "",
        "_Audit generated by "
        "`D:\\Prometheus\\scripts\\harmonia_audit.py` (Phase 1.5 patch 5)._",
        "",
    ]


# ---------------------------------------------------------------------------
# Top-level orchestration
# ---------------------------------------------------------------------------

def build_report(window: timedelta, now: datetime,
                 only_agent: Optional[str]) -> tuple[str, list[dict], dict]:
    cutoff = now - window
    events_24h = _read_events(cutoff)
    yields_24h = read_yields(since_iso=cutoff.isoformat())
    ticks_24h = _read_ticks(cutoff)
    lifetime_ticks = _lifetime_tick_count()
    daemon = _daemon_status()

    window_hours = window.total_seconds() / 3600.0
    selected = [n for n in AGENT_NAMES if (only_agent is None or n == only_agent)]
    cards = [
        assemble_agent_card(n, window_hours, events_24h, yields_24h,
                            ticks_24h, cutoff)
        for n in selected
    ]

    swarm_events = sum(c["logs"]["events"] for c in cards)
    swarm_yields = sum(c["logs"]["yields"] for c in cards)

    md_lines: list[str] = []
    md_lines += _header_section(now, daemon, lifetime_ticks,
                                swarm_events, swarm_yields, window_hours)
    md_lines += _scorecard_table(cards)
    md_lines.append("## Detailed per-agent cards")
    md_lines.append("")
    for c in cards:
        md_lines += _agent_detail(c)
    md_lines += _dr_summary(cards)
    md_lines += _cadence_recommendations(cards)
    md_lines += _health_alerts(cards, daemon)
    md_lines += _source_data()

    md = "\n".join(md_lines)

    swarm_meta = {
        "lifetime_ticks": lifetime_ticks,
        "events_in_window": swarm_events,
        "yields_in_window": swarm_yields,
        "daemon": daemon,
        "window_hours": window_hours,
    }
    return md, cards, swarm_meta


def _cards_to_json(cards: list[dict]) -> list[dict]:
    out: list[dict] = []
    for c in cards:
        cc = dict(c)
        # Truncate last_tick stats blob for portability.
        lt = cc.get("last_tick")
        if isinstance(lt, dict):
            cc["last_tick"] = {
                "started_at": lt.get("started_at"),
                "elapsed_sec": lt.get("elapsed_sec"),
                "error": lt.get("error"),
                "stats_keys": list((lt.get("stats") or {}).keys()),
            }
        out.append(cc)
    return out


def main(argv: Optional[list[str]] = None) -> int:
    args = _build_argparser().parse_args(argv)
    window = _parse_window(args.window)
    now = datetime.now(timezone.utc)

    md, cards, swarm_meta = build_report(window, now, args.agent)

    if args.json:
        payload = {
            "generated_at": now.isoformat(),
            "window_hours": swarm_meta["window_hours"],
            "swarm": swarm_meta,
            "cards": _cards_to_json(cards),
        }
        out_text = json.dumps(payload, indent=2, default=str)
    else:
        out_text = md

    out_path: Optional[Path] = None
    if not args.stdout:
        out_path = LOGS_DIR / f"swarm_audit_{now.strftime('%Y%m%d_%H%M%S')}.md"
        try:
            LOGS_DIR.mkdir(parents=True, exist_ok=True)
            out_path.write_text(md, encoding="utf-8")
        except Exception as e:
            print(f"[harmonia_audit] write failed: {e}", file=sys.stderr)
            out_path = None

    print(out_text)
    if out_path is not None:
        print(f"\n[harmonia_audit] wrote {out_path}")

    if not args.no_emit_event:
        emit_event(
            EVENT_WEEKLY_REPORT_EMITTED,
            {
                "kind": "swarm_audit",
                "audit_path": str(out_path) if out_path else None,
                "window_hours": swarm_meta["window_hours"],
                "agents_audited": [c["name"] for c in cards],
                "dr_flagged": [c["name"] for c in cards if c["dr"]["flag"]],
                "daemon_alive": bool(swarm_meta["daemon"]["alive"]),
                "lifetime_ticks": swarm_meta["lifetime_ticks"],
                "events_in_window": swarm_meta["events_in_window"],
                "yields_in_window": swarm_meta["yields_in_window"],
            },
            agent="harmonia_audit",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
