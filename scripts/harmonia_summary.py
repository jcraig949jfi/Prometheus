"""
harmonia_summary.py -one-page daily rollup of the Harmonia swarm.

Reads:
- harmonia/agents/_logs/ticks.jsonl (lifetime tick records)
- harmonia/agents/_rotation_state.json (recent rolling window)
- harmonia/agents/_swarm.pid (daemon liveness)
- harmonia/agents/<name>/artifacts/ (per-agent artifact counts)
- harmonia/agents/<name>/state/*.json (per-agent state)
- agora.research_queue via agora_persist (Pythia queue snapshot -optional)

Prints a markdown brief. Designed for daily check-in or piping to a file.

Usage:
    python scripts/harmonia_summary.py                  # full report
    python scripts/harmonia_summary.py --window 24h     # tick stats only for last 24h
    python scripts/harmonia_summary.py --no-pythia      # skip Postgres query
    python scripts/harmonia_summary.py --json           # machine-readable output
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

_SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = _SCRIPT_DIR.parent
AGENTS_DIR = REPO_ROOT / "harmonia" / "agents"
TICKS_JSONL = AGENTS_DIR / "_logs" / "ticks.jsonl"
ROTATION_STATE = AGENTS_DIR / "_rotation_state.json"
PID_FILE = AGENTS_DIR / "_swarm.pid"
AGENT_NAMES = ("phylax", "sophia", "iris", "argos", "telos")


def _parse_window(window: Optional[str]) -> Optional[timedelta]:
    if not window:
        return None
    m = re.fullmatch(r"(\d+)([hmd])", window.lower().strip())
    if not m:
        raise SystemExit(f"bad --window value '{window}'; expected like '24h', '7d', '90m'")
    n = int(m.group(1))
    unit = m.group(2)
    return {"h": timedelta(hours=n), "m": timedelta(minutes=n), "d": timedelta(days=n)}[unit]


def _read_jsonl_ticks(window: Optional[timedelta]) -> list[dict]:
    if not TICKS_JSONL.exists():
        return []
    rows: list[dict] = []
    cutoff: Optional[datetime] = None
    if window is not None:
        cutoff = datetime.now(timezone.utc) - window
    try:
        with open(TICKS_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                if cutoff is not None:
                    try:
                        started = datetime.fromisoformat(r["started_at"])
                        if started < cutoff:
                            continue
                    except Exception:
                        pass
                rows.append(r)
    except Exception as e:
        print(f"WARNING: failed to read ticks.jsonl: {e}", file=sys.stderr)
    return rows


def _daemon_status() -> dict:
    """Liveness check via PID file + OS process query (cross-platform)."""
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
        # Best-effort age via wmic (tasklist doesn't give creation time)
        try:
            import datetime as _dt
            proc = subprocess.run(
                ["wmic", "process", "where", f"ProcessId={pid}",
                 "get", "CreationDate", "/value"],
                capture_output=True, text=True, timeout=10, check=False,
            )
            for line in proc.stdout.splitlines():
                if line.startswith("CreationDate="):
                    ts = line.split("=", 1)[1].strip()
                    if ts and len(ts) >= 14:
                        # Format: yyyymmddHHMMSS.ffffff±zzz
                        dt = _dt.datetime.strptime(ts[:14], "%Y%m%d%H%M%S")
                        out["age_minutes"] = int(
                            (_dt.datetime.now() - dt).total_seconds() / 60
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


def _agent_artifact_count(name: str) -> int:
    d = AGENTS_DIR / name / "artifacts"
    if not d.exists():
        return 0
    try:
        return sum(1 for p in d.iterdir() if p.is_file())
    except Exception:
        return 0


def _load_state(name: str, key: str) -> Any:
    p = AGENTS_DIR / name / "state" / f"{key}.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _pythia_snapshot() -> dict:
    """Try to query Postgres for Pythia queue state. Returns {ok, details}."""
    out: dict = {"ok": False, "error": None}
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    try:
        import agora_persist  # type: ignore
    except Exception as e:
        out["error"] = f"agora_persist import failed: {e}"
        return out
    try:
        import psycopg2.extras  # type: ignore
        with agora_persist._connect(timeout=5) as conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(
                "SELECT status, COUNT(*) AS n FROM agora.research_queue "
                "GROUP BY status ORDER BY n DESC"
            )
            out["by_status"] = {r["status"]: int(r["n"]) for r in cur.fetchall()}
            cur.execute(
                "SELECT id, completed_at FROM agora.research_queue "
                "WHERE status='complete' ORDER BY completed_at DESC LIMIT 1"
            )
            r = cur.fetchone()
            out["newest_completion"] = {
                "id": r["id"],
                "completed_at": r["completed_at"].isoformat() if r else None,
            } if r else None
            # In-flight rows
            cur.execute(
                "SELECT id, dispatched_at, title FROM agora.research_queue "
                "WHERE status IN ('dispatched','in_progress') ORDER BY dispatched_at"
            )
            out["in_flight"] = [
                {
                    "id": r["id"],
                    "dispatched_at": r["dispatched_at"].isoformat()
                    if r["dispatched_at"] else None,
                    "title": (r["title"] or "")[:60],
                }
                for r in cur.fetchall()
            ]
            # Today's enqueues by requester
            cur.execute(
                "SELECT requested_by, COUNT(*) AS n FROM agora.research_queue "
                "WHERE requested_at >= date_trunc('day', NOW() AT TIME ZONE 'UTC') "
                "GROUP BY requested_by ORDER BY n DESC"
            )
            out["today_by_requester"] = {
                r["requested_by"]: int(r["n"]) for r in cur.fetchall()
            }
            out["ok"] = True
            return out
    except Exception as e:
        out["error"] = f"{type(e).__name__}: {str(e)[:120]}"
        return out


def build_report(window: Optional[timedelta], skip_pythia: bool) -> dict:
    rep: dict = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "window": str(window) if window else "lifetime",
    }
    # Daemon
    rep["daemon"] = _daemon_status()

    # Ticks
    ticks = _read_jsonl_ticks(window)
    lifetime_total = sum(1 for _ in open(TICKS_JSONL, "r", encoding="utf-8")) \
        if TICKS_JSONL.exists() else 0
    rep["ticks"] = {
        "in_window": len(ticks),
        "lifetime_total": lifetime_total,
        "per_agent": dict(Counter(t["agent"] for t in ticks)),
        "errors_in_window": sum(
            1 for t in ticks
            if t.get("error") or t.get("stats", {}).get("errors")
        ),
    }
    if ticks:
        rep["ticks"]["first"] = ticks[0]["started_at"]
        rep["ticks"]["last"] = ticks[-1]["started_at"]

    # Per-agent last tick + interesting stats
    by_agent: dict = defaultdict(list)
    for t in ticks:
        by_agent[t["agent"]].append(t)
    rotation_state = {}
    if ROTATION_STATE.exists():
        try:
            rotation_state = json.loads(
                ROTATION_STATE.read_text(encoding="utf-8")
            )
        except Exception:
            pass

    agents_block: dict = {}
    for name in AGENT_NAMES:
        block: dict = {"artifacts": _agent_artifact_count(name)}
        if by_agent[name]:
            last = by_agent[name][-1]
            block["last_tick_at"] = last["started_at"]
            block["last_stats"] = {
                k: v for k, v in last.get("stats", {}).items()
                if k not in ("tick_id", "elapsed_sec")
            }
            block["ticks_in_window"] = len(by_agent[name])
        # Specific per-agent extras
        if name == "argos":
            seeded = _load_state("argos", "dr_seeded") or []
            today = datetime.now(timezone.utc).date().isoformat()
            block["dr_seeded_today"] = sum(
                1 for e in seeded
                if str(e.get("ts", ""))[:10] == today
            )
            block["dr_seeded_lifetime"] = len(seeded)
        elif name == "telos":
            ph = _load_state("telos", "proposed_history") or {}
            block["proposed_history_summary"] = {
                fid: len(lst) for fid, lst in ph.items()
            }
            exh = [
                t for t in by_agent["telos"]
                if t.get("stats", {}).get("proposal_pool_exhausted")
            ]
            block["pool_exhausts_in_window"] = len(exh)
        elif name == "iris":
            block["dismissed_candidates"] = _load_state(
                "iris", "dismissed_candidates"
            ) or []
        elif name == "phylax":
            seeded = _load_state("phylax", "dr_seeded") or []
            today = datetime.now(timezone.utc).date().isoformat()
            block["dr_seeded_today"] = sum(
                1 for e in seeded
                if str(e.get("ts", ""))[:10] == today
            )
            block["dr_seeded_lifetime"] = len(seeded)
        elif name == "sophia":
            tried = _load_state("sophia", "tried_pairs") or []
            block["tried_pairs_lifetime"] = len(tried)
        agents_block[name] = block
    rep["agents"] = agents_block

    # Pythia
    if not skip_pythia:
        rep["pythia"] = _pythia_snapshot()
    else:
        rep["pythia"] = {"skipped": True}
    return rep


def _fmt_md(rep: dict) -> str:
    lines: list[str] = []
    lines.append(f"# Harmonia swarm -daily brief")
    lines.append(f"")
    lines.append(f"**Generated:** `{rep['generated_at']}`")
    lines.append(f"**Window:** {rep['window']}")
    lines.append(f"")

    # Daemon
    d = rep["daemon"]
    if d["alive"]:
        age = f"{d['age_minutes']} min" if d.get("age_minutes") is not None else "?"
        lines.append(f"## Daemon -ALIVE (pid={d['pid']}, age={age})")
    else:
        lines.append(f"## Daemon -DEAD (pid={d.get('pid')})")
        lines.append(f"")
        lines.append(f"Restart with:")
        lines.append(f"```powershell")
        lines.append(f"Start-Process -FilePath \"scripts\\harmonia_loop_launch.bat\" -WindowStyle Hidden")
        lines.append(f"```")
    lines.append(f"")

    # Ticks
    t = rep["ticks"]
    lines.append(f"## Ticks")
    lines.append(f"")
    lines.append(f"- **In window**: {t['in_window']}")
    lines.append(f"- **Lifetime total**: {t['lifetime_total']}")
    lines.append(f"- **Errors in window**: {t['errors_in_window']}")
    if t.get("first") and t.get("last"):
        lines.append(f"- **First in window**: {t['first']}")
        lines.append(f"- **Last in window**: {t['last']}")
    if t.get("per_agent"):
        per = t["per_agent"]
        lines.append(f"- **Per-agent ticks in window**: " + ", ".join(
            f"{a}={per.get(a, 0)}" for a in AGENT_NAMES
        ))
    lines.append(f"")

    # Agents
    lines.append(f"## Agents")
    lines.append(f"")
    lines.append(f"| Agent | Artifacts | Last tick | Notable |")
    lines.append(f"|---|---|---|---|")
    for name in AGENT_NAMES:
        a = rep["agents"][name]
        last_t = a.get("last_tick_at", "—")
        if last_t != "—":
            last_t = last_t[11:19]
        notable: list[str] = []
        s = a.get("last_stats", {})
        if name == "phylax":
            notable.append(f"items={s.get('items_processed', '?')}")
            v = s.get("verdicts") or {}
            notable.append(f"verdicts={v}")
            if a.get("dr_seeded_today") is not None:
                notable.append(f"dr_today={a['dr_seeded_today']}/lifetime={a['dr_seeded_lifetime']}")
        elif name == "sophia":
            notable.append(f"pair={s.get('pair_proposed')}")
            notable.append(f"blr={s.get('backlog_remaining')}")
            notable.append(f"tried_lifetime={a.get('tried_pairs_lifetime', '?')}")
        elif name == "iris":
            notable.append(f"clusters={s.get('total_clusters_tracked', '?')}")
            notable.append(f"corpus={s.get('corpus_size', '?')}")
            d = a.get("dismissed_candidates") or []
            if d:
                notable.append(f"dismissed={len(d)}")
        elif name == "argos":
            notable.append(f"prob={s.get('problem_id_processed', '?')}")
            notable.append(f"dr_today={a.get('dr_seeded_today', 0)}")
            notable.append(f"dr_lifetime={a.get('dr_seeded_lifetime', 0)}")
        elif name == "telos":
            notable.append(f"fid={s.get('fid_picked', '?')}")
            notable.append(f"exhausts_in_window={a.get('pool_exhausts_in_window', 0)}")
            ph = a.get("proposed_history_summary") or {}
            if ph:
                notable.append(
                    "history=" + ",".join(f"{k}:{v}" for k, v in ph.items())
                )
        lines.append(f"| {name} | {a['artifacts']} | {last_t} | {'; '.join(notable)} |")
    lines.append(f"")

    # Pythia
    p = rep["pythia"]
    if p.get("skipped"):
        lines.append(f"## Pythia -_skipped_")
    elif not p.get("ok"):
        lines.append(f"## Pythia -UNREACHABLE")
        if p.get("error"):
            lines.append(f"")
            lines.append(f"`{p['error']}`")
    else:
        lines.append(f"## Pythia DR queue")
        lines.append(f"")
        by_status = p.get("by_status") or {}
        if by_status:
            lines.append(f"- **By status**: " + ", ".join(
                f"{k}={v}" for k, v in by_status.items()
            ))
        nc = p.get("newest_completion") or {}
        if nc:
            lines.append(f"- **Newest completion**: id={nc.get('id')} at `{nc.get('completed_at')}`")
        inflight = p.get("in_flight") or []
        if inflight:
            lines.append(f"- **In-flight ({len(inflight)})**:")
            for r in inflight[:5]:
                lines.append(f"  - id={r['id']} dispatched_at=`{r.get('dispatched_at')}` -{r.get('title')}")
        tbr = p.get("today_by_requester") or {}
        if tbr:
            lines.append(f"- **Today's enqueues**: " + ", ".join(
                f"{k}={v}" for k, v in tbr.items()
            ))
    lines.append(f"")

    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Harmonia swarm daily-rollup brief"
    )
    ap.add_argument("--window", default="24h",
                    help="time window for tick stats (e.g. 24h, 7d, 90m). 'lifetime' to read all.")
    ap.add_argument("--no-pythia", action="store_true",
                    help="skip Postgres query")
    ap.add_argument("--json", action="store_true",
                    help="emit machine-readable JSON instead of markdown")
    args = ap.parse_args()

    window: Optional[timedelta] = None
    if args.window.lower() != "lifetime":
        window = _parse_window(args.window)

    rep = build_report(window=window, skip_pythia=args.no_pythia)
    if args.json:
        print(json.dumps(rep, indent=2, default=str))
    else:
        print(_fmt_md(rep))
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
