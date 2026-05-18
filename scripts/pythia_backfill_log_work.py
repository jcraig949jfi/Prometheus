"""One-shot: backfill log_work events for Pythia rows already dispatched/completed.

Run once after stage-name conformance lands so the dashboard's DR panel
+ email DR section pick up reports that completed before the rename.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import psycopg2.extras
import agora_persist
import session_telemetry


def first_body_excerpt(report_path: str, max_chars: int = 280) -> str | None:
    """Pull the first non-header paragraph from a saved Pythia report file."""
    try:
        f = Path(report_path)
        if not f.exists():
            return None
        text = f.read_text(encoding="utf-8", errors="replace")
        lines = []
        in_header = True
        for line in text.splitlines():
            stripped = line.strip()
            if in_header and (line.startswith("#") or line.startswith("**")
                              or line.startswith("---") or not stripped):
                continue
            in_header = False
            if not stripped:
                if lines:
                    break
                continue
            lines.append(stripped)
            if sum(len(x) for x in lines) > max_chars:
                break
        body = " ".join(lines)[:max_chars]
        return (body + "...") if body and len(body) >= max_chars else (body or None)
    except Exception:
        return None


def repo_relative(p: str) -> str:
    """Normalize an absolute path to a repo-relative POSIX path."""
    if not p:
        return ""
    norm = p.replace("\\", "/")
    # Strip "F:/Prometheus/" prefix or any local absolute prefix
    repo_str = str(REPO_ROOT).replace("\\", "/") + "/"
    if norm.startswith(repo_str):
        norm = norm[len(repo_str):]
    return norm.lstrip("/")


def main():
    with agora_persist._connect() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT id, queue_ref, title, tier, status, report_path,
                       report_github_url, completed_at, dispatched_at
                FROM agora.research_queue
                WHERE dispatched_at IS NOT NULL
                ORDER BY dispatched_at ASC
            """)
            rows = cur.fetchall()

    print(f"Found {len(rows)} dispatched Pythia rows (any status).")
    dispatched_logged = 0
    received_logged = 0
    for r in rows:
        ref = r.get("queue_ref") or f"row{r['id']}"
        tier = r.get("tier") or "?"
        title = (r.get("title") or "")[:160]

        # Dispatched event
        ok = session_telemetry.log_work(
            stage="deep_research_dispatched",
            agent="Pythia",
            summary=f"{ref} [T{tier}]: {title}",
            output_path=None,
        )
        if ok:
            dispatched_logged += 1

        # Received event — only if complete + report path exists
        if r["status"] == "complete" and r.get("report_path"):
            rel = repo_relative(r["report_path"])
            excerpt = first_body_excerpt(r["report_path"]) or f"{ref}: {title}"
            ok = session_telemetry.log_work(
                stage="deep_research_received",
                agent="Pythia",
                summary=excerpt,
                output_path=rel or None,
            )
            if ok:
                received_logged += 1

    print(f"Backfilled: {dispatched_logged} dispatched events, {received_logged} received events.")


if __name__ == "__main__":
    main()
