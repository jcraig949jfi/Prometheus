"""
Pythia — Oracle of Delphi (Aporia's tool for Gemini Deep Research dispatch)

Pythia is the mortal oracle who received petitioners' questions and channeled
answers from Apollo. Here she sits between Aporia (operator) + James (mortal
petitioner) and the external oracle Gemini deep-research-pro-preview-12-2025.

Wires into orchestration:
- registers as kind="tool" with operator="Aporia"
- writes heartbeat status_json with queue counts + budget remaining
- log_work per dispatch + per completion
- agora.research_queue is the source of truth; brief reads
  read_recent_completed_research for the 4-hour email

Concurrency: up to 3 in-flight Gemini interactions (paid-tier cap). Each
tick (default 60s): poll all in-flight; if any complete, save report +
mark_complete + auto git add+commit+push so the GitHub URL is clickable;
if any failed, mark_failed. If in-flight < 3 and today's budget < 20,
pop next pending and create a new interaction.

Quota / 4xx detection: only happens on client.interactions.create(). If
the error message contains a quota / RESOURCE_EXHAUSTED / 429 keyword,
mark the day as rate-limited in the heartbeat status_json (so the empirical
reset-hour discovery works) and skip further create attempts until the
next tick.

Usage:
    python scripts/pythia_daemon.py --loop --interval 60
    python scripts/pythia_daemon.py --once             # single tick
    python scripts/pythia_daemon.py status             # show queue state
    python scripts/pythia_daemon.py enqueue "TITLE" "PROMPT" --priority 1
    python scripts/pythia_daemon.py seed-from-default 21
"""
import argparse
import json
import logging
import os
import re
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
APORIA_SCRIPTS = REPO_ROOT / "aporia" / "scripts"
REPORTS_DIR_BASE = REPO_ROOT / "aporia" / "docs" / "deep_research_reports"

# GitHub URL prefix — derived from recent commit author noreply email
# (jcraig949jfi@users.noreply.github.com). Hardcoded for v0.1; parameterize later.
GITHUB_URL_PREFIX = "https://github.com/jcraig949jfi/Prometheus/blob/main"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(APORIA_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(APORIA_SCRIPTS))

try:
    import agora_persist
    HAS_PG = True
except Exception:
    HAS_PG = False

try:
    import session_telemetry
    HAS_TELEMETRY = True
except Exception:
    HAS_TELEMETRY = False

try:
    from keys import get_key  # noqa
    from google import genai  # noqa
    HAS_GENAI = True
except Exception:
    HAS_GENAI = False

# Reuse the dispatcher's text-extraction helper
try:
    from gemini_deep_research_dispatch import extract_text_from_interaction
    HAS_DISPATCH_HELPER = True
except Exception:
    HAS_DISPATCH_HELPER = False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [PYTHIA] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("pythia")


AGENT_MODEL = "deep-research-pro-preview-12-2025"
DAILY_BUDGET = 20
MAX_CONCURRENT = 3
QUOTA_KEYWORDS = ("RESOURCE_EXHAUSTED", "quota", "429", "rate limit",
                  "rate_limit", "exceeded")


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------

def slugify(s: str) -> str:
    """Filesystem-safe slug from a title."""
    s = re.sub(r"[^a-zA-Z0-9]+", "_", s.lower()).strip("_")
    return s[:60] or "untitled"


def is_quota_error(err_msg: str) -> bool:
    if not err_msg:
        return False
    lower = err_msg.lower()
    return any(k.lower() in lower for k in QUOTA_KEYWORDS)


def github_url_for(repo_relative_path: str) -> str:
    """Compose the GitHub blob URL for a repo-relative path. Forward slashes only."""
    norm = repo_relative_path.replace("\\", "/").lstrip("/")
    return f"{GITHUB_URL_PREFIX}/{norm}"


def report_path_for(row: dict) -> Path:
    """Where Pythia saves a completed DR report on disk (repo-relative)."""
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    n = row["id"]
    slug = slugify(row["title"])
    return REPORTS_DIR_BASE / date_str / f"{n:05d}_{slug}.md"


def repo_relative(p: Path) -> str:
    """Return p as a POSIX-style path relative to REPO_ROOT."""
    return str(p.resolve().relative_to(REPO_ROOT)).replace("\\", "/")


# ---------------------------------------------------------------------------
# Gemini client (cached)
# ---------------------------------------------------------------------------

_genai_client = None


def get_genai_client():
    global _genai_client
    if _genai_client is not None:
        return _genai_client
    if not HAS_GENAI:
        raise RuntimeError("google.genai / keys.get_key unavailable")
    api_key = get_key("gemini")
    _genai_client = genai.Client(api_key=api_key)
    return _genai_client


# ---------------------------------------------------------------------------
# Dispatch + poll
# ---------------------------------------------------------------------------

def dispatch_one(row: dict) -> dict:
    """Create a Gemini interaction for one pending row. Returns dict:
        {ok: bool, interaction_id: str|None, error: str|None, quota: bool}
    """
    try:
        client = get_genai_client()
        interaction = client.interactions.create(
            input=row["prompt_text"],
            agent=AGENT_MODEL,
            background=True,
            store=True,
        )
        iid = getattr(interaction, "id", None) or getattr(interaction, "interaction_id", None)
        if not iid:
            return {"ok": False, "interaction_id": None,
                    "error": "no interaction id returned", "quota": False}
        return {"ok": True, "interaction_id": iid, "error": None, "quota": False}
    except Exception as e:
        err = f"{type(e).__name__}: {e}"
        return {"ok": False, "interaction_id": None,
                "error": err, "quota": is_quota_error(err)}


def poll_one(interaction_id: str) -> dict:
    """Poll one interaction. Returns dict:
        {status: str, text: str|None, error: str|None, raw: object}
    where status is one of: 'running' | 'complete' | 'failed' | 'unknown'
    """
    try:
        client = get_genai_client()
        interaction = client.interactions.get(interaction_id)
        raw_status = getattr(interaction, "status", None)
        if raw_status in ("completed", "succeeded", "success"):
            text = extract_text_from_interaction(interaction) if HAS_DISPATCH_HELPER else str(interaction)
            return {"status": "complete", "text": text,
                    "error": None, "raw": raw_status}
        if raw_status in ("failed", "cancelled", "error"):
            err = getattr(interaction, "error", None)
            return {"status": "failed", "text": None,
                    "error": str(err or raw_status), "raw": raw_status}
        return {"status": "running", "text": None, "error": None, "raw": raw_status}
    except Exception as e:
        return {"status": "unknown", "text": None,
                "error": f"{type(e).__name__}: {e}", "raw": None}


# ---------------------------------------------------------------------------
# Report save + git push
# ---------------------------------------------------------------------------

def save_report(row: dict, text: str, elapsed_sec: float) -> tuple[Path, str]:
    """Write the DR report to disk under aporia/docs/deep_research_reports/<date>/.
    Returns (absolute path, repo-relative POSIX path).
    """
    target = report_path_for(row)
    target.parent.mkdir(parents=True, exist_ok=True)
    title = row.get("title", "")
    iid = row.get("interaction_id") or "?"
    header = (
        f"# {title}\n\n"
        f"**Pythia queue id:** {row['id']}\n"
        f"**Tier:** {row.get('tier','?')}\n"
        f"**Priority:** {row.get('priority','?')}\n"
        f"**Requested by:** {row.get('requested_by','?')}\n"
        f"**Agent:** {AGENT_MODEL}\n"
        f"**Interaction ID:** {iid}\n"
        f"**Elapsed:** {int(elapsed_sec)}s\n"
        f"**Completed at:** {datetime.now(timezone.utc).isoformat()}\n\n"
        "---\n\n"
    )
    target.write_text(header + text + "\n", encoding="utf-8")
    return target, repo_relative(target)


def git_commit_and_push_report(repo_rel_path: str, title: str) -> bool:
    """Best-effort git add + commit + push of a single report file.
    Bounded to ~60s; silent on failure. Reports without push still get the
    GitHub URL persisted — clickability gates on next manual / cron push.
    """
    short = title[:60].replace("\n", " ")
    msg = f"Pythia DR report: {short}"
    try:
        subprocess.run(["git", "add", repo_rel_path],
                       cwd=REPO_ROOT, check=True, timeout=20,
                       capture_output=True)
        # If nothing staged (file unchanged), skip
        diff = subprocess.run(["git", "diff", "--cached", "--quiet"],
                              cwd=REPO_ROOT, timeout=10)
        if diff.returncode == 0:
            return True  # nothing to commit
        subprocess.run(["git", "commit", "-m", msg],
                       cwd=REPO_ROOT, check=True, timeout=30,
                       capture_output=True)
        subprocess.run(["git", "push"],
                       cwd=REPO_ROOT, check=True, timeout=60,
                       capture_output=True)
        return True
    except Exception as e:
        log.warning(f"git push for {repo_rel_path} failed (non-fatal): {e}")
        return False


# ---------------------------------------------------------------------------
# Heartbeat + log
# ---------------------------------------------------------------------------

def emit_pythia_heartbeat(rate_limited_at: Optional[str] = None) -> None:
    """Compose Pythia's status_json with budget + queue counts."""
    if not HAS_TELEMETRY:
        return
    counts = agora_persist.count_research_today() if HAS_PG else {}
    today_complete = counts.get("complete", 0)
    today_failed = counts.get("failed", 0)
    today_rate_limited = counts.get("rate_limited", 0)
    in_flight = len(agora_persist.get_in_flight_research()) if HAS_PG else 0
    pending = 0
    if HAS_PG:
        try:
            with agora_persist._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) FROM agora.research_queue WHERE status='pending'")
                    pending = cur.fetchone()[0]
        except Exception:
            pass
    budget_remaining = max(0, DAILY_BUDGET - (today_complete + in_flight))
    status_json = {
        "queue_pending": pending,
        "in_flight": in_flight,
        "completed_today": today_complete,
        "failed_today": today_failed,
        "rate_limited_today": today_rate_limited,
        "daily_budget": DAILY_BUDGET,
        "budget_remaining": budget_remaining,
        "max_concurrent": MAX_CONCURRENT,
        "model": AGENT_MODEL,
    }
    if rate_limited_at:
        status_json["last_rate_limited_at"] = rate_limited_at
    session_telemetry.register_session(
        agent_name="Pythia", machine="M1",
        role="Gemini Deep Research dispatcher (Oracle of Delphi)",
        kind="tool",
        status_json={**status_json, "operator": "Aporia"},
    )


# ---------------------------------------------------------------------------
# Tick — one pass of the daemon loop
# ---------------------------------------------------------------------------

def run_tick(dry_run: bool = False) -> dict:
    """One pass: poll in-flight, mark complete/failed, then dispatch new ones."""
    stats = {"polled": 0, "completed": 0, "failed": 0,
             "dispatched": 0, "rate_limited": False}
    rate_limited_at = None

    if not HAS_PG:
        log.error("agora_persist unavailable; cannot run")
        return stats

    # 1. Poll all in-flight
    in_flight = agora_persist.get_in_flight_research()
    for row in in_flight:
        iid = row.get("interaction_id")
        if not iid:
            continue
        result = poll_one(iid)
        stats["polled"] += 1
        if result["status"] == "complete":
            dispatched_at = row.get("dispatched_at")
            try:
                dt = datetime.fromisoformat(dispatched_at.replace("Z", "+00:00")) if dispatched_at else None
                elapsed = (datetime.now(timezone.utc) - dt).total_seconds() if dt else 0.0
            except Exception:
                elapsed = 0.0
            if dry_run:
                log.info(f"[dry-run] would mark complete: row={row['id']}")
                continue
            full_row = _fetch_row(row["id"]) or row
            abs_path, rel_path = save_report(full_row, result["text"] or "", elapsed)
            url = github_url_for(rel_path)
            git_commit_and_push_report(rel_path, full_row.get("title", ""))
            agora_persist.mark_research_complete(
                row_id=row["id"], report_path=str(abs_path),
                report_github_url=url,
                report_summary=(result["text"] or "")[:300],
                elapsed_sec=elapsed,
            )
            stats["completed"] += 1
            log.info(f"complete row={row['id']} -> {url}")
            if HAS_TELEMETRY:
                session_telemetry.log_work(
                    stage="dr_report_completed", agent="Pythia",
                    summary=f"Report ready: {full_row.get('title','')[:120]}. URL: {url}",
                    output_path=str(abs_path),
                )
        elif result["status"] == "failed":
            agora_persist.mark_research_failed(row["id"], result["error"] or "unknown")
            stats["failed"] += 1
            log.warning(f"failed row={row['id']}: {result['error']}")
        # else 'running' / 'unknown' — leave for next tick

    # 2. Dispatch up to MAX_CONCURRENT - currently in-flight, respecting daily budget
    current_in_flight = len(agora_persist.get_in_flight_research())
    counts = agora_persist.count_research_today()
    completed_today = counts.get("complete", 0)
    budget_used = completed_today + current_in_flight
    slots = min(MAX_CONCURRENT - current_in_flight, DAILY_BUDGET - budget_used)
    if slots <= 0:
        if budget_used >= DAILY_BUDGET:
            log.info(f"daily budget reached ({budget_used}/{DAILY_BUDGET}); idle dispatch")
        emit_pythia_heartbeat(rate_limited_at)
        return stats
    pending = agora_persist.next_pending_research(limit=slots)
    for row in pending:
        if dry_run:
            log.info(f"[dry-run] would dispatch row={row['id']}: {row.get('title','')[:60]}")
            continue
        res = dispatch_one(row)
        if res["ok"]:
            agora_persist.mark_research_dispatched(row["id"], res["interaction_id"])
            stats["dispatched"] += 1
            log.info(f"dispatched row={row['id']} iid={res['interaction_id']} ({row.get('title','')[:60]})")
            if HAS_TELEMETRY:
                session_telemetry.log_work(
                    stage="dr_dispatched", agent="Pythia",
                    summary=f"Dispatched: {row.get('title','')[:120]} (iid={res['interaction_id']})",
                )
        else:
            if res["quota"]:
                stats["rate_limited"] = True
                rate_limited_at = datetime.now(timezone.utc).isoformat()
                log.warning(f"QUOTA hit on row={row['id']}: {res['error']}")
                if HAS_TELEMETRY:
                    session_telemetry.log_work(
                        stage="dr_quota_hit", agent="Pythia",
                        summary=f"Quota detected at {rate_limited_at}: {res['error'][:200]}",
                        success=False, error=res["error"],
                    )
                break  # stop dispatching this tick
            else:
                # Non-quota failure: bump attempt count via mark_failed-then-reset-to-pending
                # is overkill; for now mark failed with the error message and operator can
                # re-enqueue. Simpler model; retries are explicit.
                agora_persist.mark_research_failed(row["id"], res["error"], status="failed")
                stats["failed"] += 1
                log.warning(f"dispatch failed row={row['id']}: {res['error']}")
                if HAS_TELEMETRY:
                    session_telemetry.log_work(
                        stage="dr_dispatch_failed", agent="Pythia",
                        summary=f"Dispatch failed for row {row['id']}: {res['error'][:200]}",
                        success=False, error=res["error"],
                    )

    emit_pythia_heartbeat(rate_limited_at)
    return stats


def _fetch_row(row_id: int) -> Optional[dict]:
    """Refetch a single row by id (in case the cached row is stale)."""
    if not HAS_PG:
        return None
    try:
        with agora_persist._connect() as conn:
            with conn.cursor() as cur:
                import psycopg2.extras
                cur2 = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                cur2.execute("""
                    SELECT * FROM agora.research_queue WHERE id = %s
                """, (row_id,))
                r = cur2.fetchone()
                if r is None:
                    return None
                d = dict(r)
                for k in ("requested_at", "dispatched_at", "completed_at", "last_attempt_at"):
                    if d.get(k):
                        d[k] = d[k].isoformat()
                return d
    except Exception as e:
        log.warning(f"_fetch_row({row_id}) failed: {e}")
        return None


# ---------------------------------------------------------------------------
# Seed from default queue
# ---------------------------------------------------------------------------

def seed_from_default_queue(n: int = 21) -> int:
    """Pull top-n unfired entries from aporia/docs/gemini_research_queue/queue.jsonl,
    insert into agora.research_queue. Returns number inserted.

    Reads fired_log.jsonl to dedup. Excludes entries already in
    agora.research_queue by queue_ref.
    """
    queue_path = REPO_ROOT / "aporia" / "docs" / "gemini_research_queue" / "queue.jsonl"
    fired_path = REPO_ROOT / "aporia" / "docs" / "gemini_research_queue" / "fired_log.jsonl"

    fired_ids: set = set()
    if fired_path.exists():
        for line in fired_path.read_text(encoding="utf-8").splitlines():
            try:
                fired_ids.add(json.loads(line).get("id"))
            except Exception:
                pass

    # Also dedup against already-in-queue
    in_queue: set = set()
    try:
        with agora_persist._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT queue_ref FROM agora.research_queue WHERE queue_ref IS NOT NULL")
                in_queue = {r[0] for r in cur.fetchall()}
    except Exception:
        pass

    entries: list = []
    if not queue_path.exists():
        log.error(f"queue file not found at {queue_path}")
        return 0
    for line in queue_path.read_text(encoding="utf-8").splitlines():
        try:
            e = json.loads(line)
            qid = e.get("id")
            if qid in fired_ids or qid in in_queue:
                continue
            entries.append(e)
        except Exception:
            pass
    entries.sort(key=lambda e: (e.get("tier", "T9"), str(e.get("id", ""))))
    inserted = 0
    for e in entries[:n]:
        prompt_body = e.get("prompt") or e.get("body") or e.get("title", "")
        if not prompt_body:
            continue
        rid = agora_persist.enqueue_research(
            title=e.get("title") or e.get("id", "untitled"),
            prompt_text=prompt_body,
            requested_by="Aporia",
            priority=1 if e.get("tier") == "T1" else 5,
            tier=e.get("tier"),
            queue_ref=e.get("id"),
            target_substrate_type=e.get("substrate_type"),
            tags={"source": "gemini_research_queue", "raw_tier": e.get("tier")},
        )
        if rid:
            inserted += 1
            log.info(f"seeded row={rid} {e.get('id')}: {e.get('title','')[:60]}")
    return inserted


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Pythia — Gemini Deep Research dispatch daemon")
    sub = ap.add_subparsers(dest="cmd")

    sub.add_parser("status", help="show queue state")

    p_seed = sub.add_parser("seed-from-default", help="seed N prompts from default queue")
    p_seed.add_argument("n", type=int, default=21, nargs="?")

    p_enq = sub.add_parser("enqueue", help="enqueue one research request")
    p_enq.add_argument("title")
    p_enq.add_argument("prompt")
    p_enq.add_argument("--priority", type=int, default=1)
    p_enq.add_argument("--tier", default=None)

    ap.add_argument("--once", action="store_true", help="single tick then exit")
    ap.add_argument("--loop", action="store_true", help="loop with --interval delay")
    ap.add_argument("--interval", type=int, default=60, help="loop interval seconds")
    ap.add_argument("--dry-run", action="store_true", help="don't actually dispatch")

    args = ap.parse_args()

    if not HAS_PG:
        log.error("agora_persist unavailable")
        return 1

    if args.cmd == "status":
        counts = agora_persist.count_research_today()
        in_flight = agora_persist.get_in_flight_research()
        pending = agora_persist.next_pending_research(limit=200)
        completed_recent = agora_persist.read_recent_completed_research(hours=24, limit=20)
        print("=== Pythia Queue Status ===")
        print(f"Today's status counts: {dict(counts)}")
        print(f"In-flight: {len(in_flight)}")
        for r in in_flight:
            print(f"  row={r['id']}  iid={r.get('interaction_id')}  {r.get('title','')[:60]}")
        print(f"Pending: {len(pending)}")
        for r in pending[:10]:
            print(f"  row={r['id']}  prio={r.get('priority')}  T={r.get('tier')}  {r.get('title','')[:60]}")
        print(f"Recently completed: {len(completed_recent)}")
        for r in completed_recent[:10]:
            print(f"  row={r['id']}  {r['completed_at']}  url={r.get('report_github_url')}")
        return 0

    if args.cmd == "seed-from-default":
        n = seed_from_default_queue(args.n)
        print(f"Seeded {n} prompts from gemini_research_queue/queue.jsonl")
        return 0

    if args.cmd == "enqueue":
        rid = agora_persist.enqueue_research(
            title=args.title, prompt_text=args.prompt,
            requested_by="James", priority=args.priority, tier=args.tier,
        )
        print(f"Enqueued row={rid}")
        return 0

    print("=" * 60)
    print(f"  PYTHIA — Oracle of Delphi (Gemini DR dispatcher) v0.1")
    print(f"  Postgres: {'on' if HAS_PG else 'OFF'}")
    print(f"  Gemini:   {'on' if HAS_GENAI else 'OFF (google.genai unavailable)'}")
    print(f"  Mode:     {'loop @ ' + str(args.interval) + 's' if args.loop else 'single tick'}")
    print(f"  Budget:   {DAILY_BUDGET}/day, max {MAX_CONCURRENT} concurrent")
    print("=" * 60)

    if args.once:
        stats = run_tick(dry_run=args.dry_run)
        print(json.dumps(stats, indent=2))
        return 0

    if args.loop:
        while True:
            try:
                stats = run_tick(dry_run=args.dry_run)
                log.info(f"tick: {stats}")
            except Exception as e:
                log.exception(f"tick failed: {e}")
            time.sleep(args.interval)

    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
